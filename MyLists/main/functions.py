import os
import secrets

from PIL import Image
from MyLists import db, app
from datetime import datetime
from flask_login import current_user
from MyLists.main.media_object import MediaListDict
from MyLists.main.scheduled_tasks import scheduled_task
from MyLists.models import MediaType, ListType, Status, get_media_count, UserLastUpdate


def check_cat_type(list_type, status):
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        if status == 'Watching':
            return Status.WATCHING
        elif status == 'Completed':
            return Status.COMPLETED
        elif status == 'On Hold':
            return Status.ON_HOLD
        elif status == 'Random':
            return Status.RANDOM
        elif status == 'Dropped':
            return Status.DROPPED
        elif status == 'Plan to Watch':
            return Status.PLAN_TO_WATCH
        else:
            return None
    elif list_type == ListType.MOVIES:
        if status == 'Completed':
            return Status.COMPLETED
        elif status == 'Completed Animation':
            return Status.COMPLETED_ANIMATION
        elif status == 'Plan to Watch':
            return Status.PLAN_TO_WATCH
        else:
            return None
    elif list_type == ListType.GAMES:
        if status == 'Playing':
            return Status.PLAYING
        elif status == 'Completed':
            return Status.COMPLETED
        elif status == 'On Hold':
            return Status.ON_HOLD
        elif status == 'Endless':
            return Status.ENDLESS
        elif status == 'Multiplayer':
            return Status.MULTIPLAYER
        elif status == 'Owned':
            return Status.OWNED
        elif status == 'Dropped':
            return Status.DROPPED
        elif status == 'Plan to Play':
            return Status.PLAN_TO_PLAY
        else:
            return None


def get_medialist_data(list_type, all_media_data, user_id):
    common_media, total_media = get_media_count(user_id, list_type)

    media_data_list = []
    for media_data in all_media_data:
        add_data = MediaListDict(media_data, common_media, list_type).redirect_medialist()
        media_data_list.append(add_data)

    try:
        percentage = int((len(common_media)/total_media)*100)
    except ZeroDivisionError:
        percentage = 0

    return {"media_data": media_data_list,
            "common_elements": [len(common_media), total_media, percentage]}


def save_new_cover(cover_file, media_type):
    if media_type == MediaType.SERIES:
        cover_path = 'static/covers/series_covers/'
    elif media_type == MediaType.ANIME:
        cover_path = 'static/covers/anime_covers/'
    elif media_type == MediaType.MOVIES:
        cover_path = 'static/covers/movies_covers/'

    _, f_ext = os.path.splitext(cover_file.filename)
    picture_fn = secrets.token_hex(8) + f_ext
    picture_path = os.path.join(app.root_path, cover_path, picture_fn)

    try:
        i = Image.open(cover_file)
        i = i.resize((300, 450), Image.ANTIALIAS)
        i.save(picture_path, quality=90)
    except Exception as e:
        app.logger.error('[SYSTEM] Error occured updating media cover: {}'.format(e))
        return "default.jpg"

    return picture_fn


def set_last_update(media, media_type, old_status=None, new_status=None, old_season=None, new_season=None,
                    old_episode=None, new_episode=None):

    check = UserLastUpdate.query.filter_by(user_id=current_user.id, media_type=media_type, media_id=media.id) \
        .order_by(UserLastUpdate.date.desc()).first()

    diff = 10000
    if check:
        diff = (datetime.utcnow() - check.date).total_seconds()

    update = UserLastUpdate(user_id=current_user.id, media_name=media.name, media_id=media.id, media_type=media_type,
                            old_status=old_status, new_status=new_status, old_season=old_season, new_season=new_season,
                            old_episode=old_episode, new_episode=new_episode, date=datetime.utcnow())

    if diff > 600:
        db.session.add(update)
    else:
        db.session.delete(check)
        db.session.add(update)

    db.session.commit()


def compute_time_spent(media=None, list_type=None, old_watched=0, new_watched=0, movie_status=None, new_gametime=0,
                       movie_delete=False, movie_add=False, old_gametime=0, new_rewatch=0, old_rewatch=0,
                       movie_runtime=0):

    if list_type == ListType.SERIES:
        old_time = current_user.time_spent_series
        current_user.time_spent_series = old_time + ((new_watched-old_watched)*media.episode_duration) + (
                media.total_episodes*media.episode_duration*(new_rewatch-old_rewatch))
    elif list_type == ListType.ANIME:
        old_time = current_user.time_spent_anime
        current_user.time_spent_anime = old_time + ((new_watched-old_watched)*media.episode_duration) + (
                media.total_episodes*media.episode_duration*(new_rewatch-old_rewatch))
    elif list_type == ListType.MOVIES:
        old_time = current_user.time_spent_movies
        if movie_delete:
            if movie_status == Status.COMPLETED or movie_status == Status.COMPLETED_ANIMATION:
                current_user.time_spent_movies = old_time - media.runtime + media.runtime*(new_rewatch-old_rewatch)
        elif movie_add:
            if movie_status == Status.COMPLETED or movie_status == Status.COMPLETED_ANIMATION:
                current_user.time_spent_movies = old_time + media.runtime
        else:
            if movie_status == Status.COMPLETED or movie_status == Status.COMPLETED_ANIMATION:
                current_user.time_spent_movies = old_time + movie_runtime + media.runtime*(new_rewatch-old_rewatch)
            else:
                current_user.time_spent_movies = old_time - movie_runtime + media.runtime*(new_rewatch-old_rewatch)
    elif list_type == ListType.GAMES:
        old_time = current_user.time_spent_games
        current_user.time_spent_games = old_time + new_gametime - old_gametime
    db.session.commit()


# ------- Python Scheduler -----------------------------------------------------------------------------------------


app.apscheduler.add_job(func=scheduled_task, trigger='cron', id='refresh_all_data', hour=3, minute=00)
