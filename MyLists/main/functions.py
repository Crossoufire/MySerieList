import os
import secrets
from PIL import Image
from MyLists import db, app
from datetime import datetime
from flask_login import current_user
from MyLists.main.scheduled_tasks import scheduled_task
from MyLists.models import MediaType, ListType, Status, UserLastUpdate


def check_cat_type(list_type, status):
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        tv_status_dict = {'Watching': Status.WATCHING,
                          'Completed': Status.COMPLETED,
                          'On Hold': Status.ON_HOLD,
                          'Random': Status.RANDOM,
                          'Dropped': Status.DROPPED,
                          'Plan to Watch': Status.PLAN_TO_WATCH}
        try:
            return tv_status_dict[status]
        except KeyError:
            return None
    elif list_type == ListType.MOVIES:
        movie_status_dict = {'Completed': Status.COMPLETED,
                             'Plan to Watch': Status.PLAN_TO_WATCH}
        try:
            return movie_status_dict[status]
        except KeyError:
            return None


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


def compute_time_spent(media=None, list_type=None, old_watched=0, new_watched=0, movie_status=None, movie_delete=False,
                       movie_add=False, new_rewatch=0, old_rewatch=0, movie_runtime=0):

    if list_type == ListType.SERIES:
        old_time = current_user.time_spent_series
        current_user.time_spent_series = old_time + ((new_watched-old_watched) * media.episode_duration) + (
                media.total_episodes * media.episode_duration * (new_rewatch - old_rewatch))
    elif list_type == ListType.ANIME:
        old_time = current_user.time_spent_anime
        current_user.time_spent_anime = old_time + ((new_watched-old_watched)*media.episode_duration) + (
                media.total_episodes*media.episode_duration*(new_rewatch-old_rewatch))
    elif list_type == ListType.MOVIES:
        old_time = current_user.time_spent_movies
        if movie_delete:
            if movie_status == Status.COMPLETED:
                current_user.time_spent_movies = old_time - media.runtime + media.runtime*(new_rewatch-old_rewatch)
        elif movie_add:
            if movie_status == Status.COMPLETED:
                current_user.time_spent_movies = old_time + media.runtime
        else:
            if movie_status == Status.COMPLETED:
                current_user.time_spent_movies = old_time + movie_runtime + media.runtime*(new_rewatch-old_rewatch)
            else:
                current_user.time_spent_movies = old_time - movie_runtime + media.runtime*(new_rewatch-old_rewatch)

    db.session.commit()


# --- Python Scheduler -----------------------------------------------------------------------------------------

# app.apscheduler.add_job(func=scheduled_task, trigger='cron', id='refresh_all_data', hour=3, minute=00)
