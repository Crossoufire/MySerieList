import pytz
import random
from MyLists import db
from flask import url_for
from sqlalchemy import func
from flask_login import current_user
from _collections import OrderedDict
from MyLists.models import ListType, UserLastUpdate, SeriesList, AnimeList, MoviesList, Status, Series, Anime, Movies, \
    Ranks, Frames, RoleType, GamesList, Games


def get_media_count_by_status(user_id, list_type):
    if list_type == ListType.SERIES:
        status = SeriesList.status
    elif list_type == ListType.ANIME:
        status = AnimeList.status
    elif list_type == ListType.MOVIES:
        status = MoviesList.status
    elif list_type == ListType.GAMES:
        status = GamesList.status

    media_count = db.session.query(status, func.count(status)).filter_by(user_id=user_id).group_by(status).all()

    total = sum(x[1] for x in media_count)
    data = {'total': total,
            'nodata': False}
    if total == 0:
        data['nodata'] = True

    for media in media_count:
        data[media[0].value] = {"count": media[1],
                                "percent": (media[1]/total)*100}
    for media in Status:
        if media.value not in data.keys():
            data[media.value] = {"count": 0,
                                 "percent": 0}

    return data


def get_media_count_by_score(user_id, list_type):
    if list_type == ListType.SERIES:
        score = SeriesList.score
    elif list_type == ListType.ANIME:
        score = AnimeList.score
    elif list_type == ListType.MOVIES:
        score = MoviesList.score
    elif list_type == ListType.GAMES:
        score = GamesList.score

    media_count = db.session.query(score, func.count(score)).filter_by(user_id=user_id)\
        .group_by(score).order_by(score.asc()).all()

    data = {}
    for media in media_count:
        data[media[0]] = media[1]

    scores = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0]
    for sc in scores:
        if sc not in data.keys():
            data[sc] = 0

    data.pop(None, None)
    data.pop(-1, None)
    data = OrderedDict(sorted(data.items()))

    data_list = []
    for key, value in data.items():
        data_list.append(value)

    return data_list


def get_media_total_eps(user_id, list_type):
    if list_type == ListType.SERIES:
        media_list = SeriesList
    elif list_type == ListType.ANIME:
        media_list = AnimeList
    elif list_type == ListType.MOVIES:
        media_list = MoviesList
    elif list_type == ListType.GAMES:
        media_list = GamesList

    if list_type != ListType.GAMES:
        query = db.session.query(func.sum(media_list.eps_watched)).filter(media_list.user_id == user_id).all()
        eps_watched = query[0][0]
    else:
        query = db.session.query(func.count(media_list.media_id)).filter(media_list.user_id == user_id).all()
        eps_watched = query[0][0]

    if eps_watched is None:
        eps_watched = 0

    return eps_watched


def get_media_score(user_id, list_type):
    if list_type == ListType.SERIES:
        media = SeriesList
        status = Status.PLAN_TO_WATCH
    elif list_type == ListType.ANIME:
        media = AnimeList
        status = Status.PLAN_TO_WATCH
    elif list_type == ListType.MOVIES:
        media = MoviesList
        status = Status.PLAN_TO_WATCH
    elif list_type == ListType.GAMES:
        media = GamesList
        status = Status.PLAYING

    media_score = db.session.query(func.count(media.score), func.count(media.media_id), func.sum(media.score)) \
        .filter(media.user_id == user_id, media.status != status).all()

    try:
        percentage = int(float(media_score[0][0])/float(media_score[0][1])*100)
    except (ZeroDivisionError, TypeError):
        percentage = '-'

    try:
        mean_score = round(float(media_score[0][2])/float(media_score[0][0]), 2)
    except (ZeroDivisionError, TypeError):
        mean_score = '-'

    return {'scored_media': media_score[0][0],
            'total_media': media_score[0][1],
            'percentage': percentage,
            'mean_score': mean_score}


def get_favorites(user_id):
    s_fav = SeriesList.query.filter_by(favorite=True, user_id=user_id).all()
    series_favorites = db.session.query(Series).filter(Series.id.in_([m.media_id for m in s_fav])).all()
    random.shuffle(series_favorites)

    a_fav = AnimeList.query.filter_by(favorite=True, user_id=user_id).all()
    anime_favorites = db.session.query(Anime).filter(Anime.id.in_([m.media_id for m in a_fav])).all()
    random.shuffle(anime_favorites)

    m_fav = MoviesList.query.filter_by(favorite=True, user_id=user_id).all()
    movies_favorites = db.session.query(Movies).filter(Movies.id.in_([m.media_id for m in m_fav])).all()
    random.shuffle(movies_favorites)

    m_fav = GamesList.query.filter_by(favorite=True, user_id=user_id).all()
    games_favorites = db.session.query(Games).filter(Games.id.in_([m.media_id for m in m_fav])).all()
    random.shuffle(games_favorites)

    favorites = [series_favorites, anime_favorites, movies_favorites, games_favorites]

    return favorites


def get_media_levels(user, list_type):
    if list_type == ListType.SERIES:
        total_time_min = user.time_spent_series
    elif list_type == ListType.ANIME:
        total_time_min = user.time_spent_anime
    elif list_type == ListType.MOVIES:
        total_time_min = user.time_spent_movies
    elif list_type == ListType.GAMES:
        total_time_min = user.time_spent_games

    # Compute the corresponding level and percentage from the media time
    element_level_tmp = "{:.2f}".format(round((((400+80*total_time_min)**(1/2))-20)/40, 2))
    element_level = int(element_level_tmp.split('.')[0])
    element_percentage = int(element_level_tmp.split('.')[1])

    query_rank = Ranks.query.filter_by(level=element_level, type='media_rank\n').first()
    if query_rank:
        grade_id = url_for('static', filename='img/levels_ranks/{}'.format(query_rank.image_id))
        grade_title = query_rank.name
    else:
        grade_id = url_for('static', filename='img/levels_ranks/ReachRank49')
        grade_title = "Inheritor"

    level_info = {"level": element_level,
                  "level_percent": element_percentage,
                  "grade_id": grade_id,
                  "grade_title": grade_title}

    return level_info


def get_knowledge_frame(user):
    # Compute the corresponding level and percentage from the media time
    knowledge_level = int((((400+80*user.time_spent_series)**(1/2))-20)/40) +\
                      int((((400+80*user.time_spent_anime)**(1/2))-20)/40) + \
                      int((((400+80*user.time_spent_movies)**(1/2))-20)/40)

    frame_level = round(knowledge_level/8, 0) + 1
    query_frame = Frames.query.filter_by(level=frame_level).first()

    if query_frame:
        frame_id = url_for('static', filename='img/icon_frames/new/{}'.format(query_frame.image_id))
    else:
        frame_id = url_for('static', filename='img/icon_frames/new/border_40')

    return {"level": knowledge_level,
            "frame_id": frame_id,
            "frame_level": frame_level}


def get_updates(last_update):
    update = []
    for element in last_update:
        element_data = {}
        # Season or episode update
        if not element.old_status and not element.new_status:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element.old_season, element.old_episode),
                                      "S{:02d}.E{:02d}".format(element.new_season, element.new_episode)]

        # Category update
        elif element.old_status and element.new_status:
            element_data["update"] = ["{}".format(element.old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element.new_status.value).replace("Animation", "Anime")]

        # Newly added media
        elif not element.old_status and element.new_status:
            element_data["update"] = ["{}".format(element.new_status.value)]

        # Update date and add media name
        element_data["date"] = element.date.replace(tzinfo=pytz.UTC).isoformat()
        element_data["media_name"] = element.media_name
        element_data["media_id"] = element.media_id

        if element.media_type == ListType.SERIES:
            element_data["category"] = "Series"
            element_data["icon-color"] = "fas fa-tv text-series"
            element_data["border"] = "#216e7d"
        elif element.media_type == ListType.ANIME:
            element_data["category"] = "Anime"
            element_data["icon-color"] = "fas fa-torii-gate text-anime"
            element_data["border"] = "#945141"
        elif element.media_type == ListType.MOVIES:
            element_data["category"] = "Movies"
            element_data["icon-color"] = "fas fa-film text-movies"
            element_data["border"] = "#8c7821"
        elif element.media_type == ListType.GAMES:
            element_data["category"] = "Games"
            element_data["icon-color"] = "fas fa-gamepad text-games"
            element_data["border"] = "#196219"

        update.append(element_data)

    return update


# ----------------------------------------------------------------------------------------------------------


def get_header_data(user):
    # Check if the current user follows the user's account
    isfollowing = False
    if user.id != current_user.id and current_user.is_following(user):
        isfollowing = True

    # Recover the number of person that follows the user
    followers = user.followers.count()

    # Recover the knowledge frame and level of the user
    knowledge_info = get_knowledge_frame(user)

    # Header info
    header_data = {"id": str(user.id),
                   "username": user.username,
                   "profile_picture": url_for('static', filename='profile_pics/{0}'.format(user.image_file)),
                   "back_picture": url_for('static', filename='background_pics/{0}'.format(user.background_image)),
                   "register": user.registered_on.strftime("%d %b %Y"),
                   "followers": followers,
                   "isfollowing": isfollowing,
                   "knowledge_info": knowledge_info}

    return header_data


def get_user_data(user):
    # Recover the view count of the account and the media lists
    profile_view_count = user.profile_views
    if current_user.role != RoleType.ADMIN and user.id != current_user.id:
        user.profile_views += 1
        profile_view_count = user.profile_views

    view_count = {"profile": profile_view_count,
                  "series": user.series_views,
                  "anime": user.anime_views,
                  "movies": user.movies_views,
                  "games": user.games_views}

    # Recover the user's last updates
    last_updates = UserLastUpdate.query.filter_by(user_id=user.id).order_by(UserLastUpdate.date.desc()).limit(7)
    media_update = get_updates(last_updates)

    user_data = {"media_update": media_update,
                 "view_count": view_count}

    return user_data


def get_media_data(user):
    all_lists = [['series', ListType.SERIES, user.time_spent_series],
                 ['anime', ListType.ANIME, user.time_spent_anime],
                 ['movies', ListType.MOVIES, user.time_spent_movies]]
    if user.add_games:
        all_lists.append(["games", ListType.GAMES, user.time_spent_games])

    # Create dict with media as key. Dict values are dict or list of dict
    media_dict, total_time, total_media, total_score, total_mean_score, total_media_and_eps = {}, 0, 0, 0, 0, 0
    qte_media_type = len(all_lists)
    for list_type in all_lists:
        media_count = get_media_count_by_status(user.id, list_type[1])
        media_count_score = get_media_count_by_score(user.id, list_type[1])
        media_levels = get_media_levels(user, list_type[1])
        media_score = get_media_score(user.id, list_type[1])
        media_time = list_type[2]

        media_total_eps = get_media_total_eps(user.id, list_type[1])

        # Each media_data dict contains all the data for one type of media
        media_data = {'time_spent_hour': round(media_time/60),
                      'time_spent_day': round(media_time/1440, 2),
                      'media_count': media_count,
                      'media_count_score': media_count_score,
                      'media_total_eps': media_total_eps,
                      'media_levels': media_levels,
                      'media_score': media_score}

        # Recover the total time for all media in hours
        total_time += media_data['time_spent_hour']

        # Recover total number of media
        total_media += media_data['media_count']['total']

        # Recover total number of media
        total_media_and_eps += media_data['media_total_eps']

        # Recover the total score of all media
        total_score += media_data['media_score']['scored_media']

        # Recover the total mean score of all media
        try:
            total_mean_score += media_data['media_score']['mean_score']
        except:
            qte_media_type -= 1

        # return a media_dict with 3 keys (anime, series, movies) with media_data as values
        media_dict[f'{list_type[0]}'] = media_data

    # Add global data on all media
    media_dict['total_spent_hour'] = total_time
    media_dict['total_media'] = total_media
    media_dict['total_media_and_eps'] = total_media_and_eps
    media_dict['total_score'] = total_score
    try:
        media_dict['total_mean_score'] = round(total_mean_score/qte_media_type, 2)
    except:
        media_dict['total_mean_score'] = '-'

    return media_dict


def get_follows_data(user):
    # If not <current_user>, check <follows> to show (remove the private ones if <current_user> doesn't follow them)
    if current_user.id != user.id:
        followed_by_user = user.followed.all()
        current_user_follows = current_user.followed.all()

        follows_list = []
        for follow in followed_by_user:
            if follow.private:
                if follow in current_user_follows or current_user.id == follow.id:
                    follows_list.append(follow)
            else:
                follows_list.append(follow)

        follows_to_update = []
        for follow in follows_list:
            follows_to_update.append(follow.id)

        follows_update = db.session.query(UserLastUpdate) \
            .filter(UserLastUpdate.user_id.in_([u.id for u in user.followed.all()])) \
            .order_by(UserLastUpdate.date.desc()).limit(11)
    else:
        follows_list = user.followed.all()
        follows_update = db.session.query(UserLastUpdate) \
            .filter(UserLastUpdate.user_id.in_([u.id for u in user.followed.all()])) \
            .order_by(UserLastUpdate.date.desc()).limit(11)

    follows_update_list = []
    for follow in follows_update:
        follows = {'username': follow.user.username}
        follows.update(get_updates([follow])[0])
        follows_update_list.append(follows)

    return follows_list, follows_update_list


def get_all_follows_data(user):
    # If not <current_user>, check <follows> to show (remove the private ones if <current_user> does not follow them)
    if current_user.id != user.id:
        followed_by_user = user.followed.all()
        current_user_follows = current_user.followed.all()

        follows_to_display = []
        for follow in followed_by_user:
            if follow.private:
                if follow in current_user_follows or current_user.id == follow.id:
                    follows_to_display.append(follow)
            else:
                follows_to_display.append(follow)
    else:
        follows_to_display = current_user.followed.all()

    return follows_to_display
