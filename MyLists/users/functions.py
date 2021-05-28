import pytz
import random
from MyLists import db
from flask import url_for
from sqlalchemy import func
from flask_login import current_user
from _collections import OrderedDict
from MyLists.models import ListType, UserLastUpdate, SeriesList, AnimeList, MoviesList, Status, Series, Anime, Movies, \
    Ranks, RoleType, GamesList, Games, Frames, User


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


def get_media_data(user):
    all_lists = [['series', ListType.SERIES, user.time_spent_series],
                 ['anime', ListType.ANIME, user.time_spent_anime],
                 ['movies', ListType.MOVIES, user.time_spent_movies]]
    if user.add_games:
        all_lists.append(["games", ListType.GAMES, user.time_spent_games])

    # Create dict with media as key. Values are dict or list of dict
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

