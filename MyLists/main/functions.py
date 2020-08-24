import os
import secrets

from PIL import Image
from flask import url_for
from MyLists import db, app
from datetime import datetime
from flask_login import current_user
from MyLists.API_data import ApiData
from MyLists.main.media_object import MediaListDict
from MyLists.main.scheduled_tasks import scheduled_task
from MyLists.models import MediaType, ListType, Status, get_media_count


def get_collection_movie(collection_id):
    try:
        collection_data = ApiData().get_collection_data(collection_id)
    except Exception as e:
        app.logger.error('[SYSTEM] Error requesting the TMDB API for movies collection data: {}'.format(e))

    # Check the API response
    if collection_data is None:
        return None

    # Get the collection media cover
    collection_cover_path = collection_data.get("poster_path") or None

    if collection_cover_path:
        collection_cover_name = "{}.jpg".format(secrets.token_hex(8))
        try:
            ApiData().save_api_cover(collection_cover_path, collection_cover_name, ListType.MOVIES, collection=True)
        except Exception as e:
            app.logger.error('[SYSTEM] Error trying to recover the poster: {}'.format(e))
            collection_cover_name = "default.jpg"
    else:
        collection_cover_name = "default.jpg"

    collection_info = {'collection_id': collection_id,
                       'parts': len(collection_data.get('parts')),
                       'name': collection_data.get('name', "Unknown") or "Unknown",
                       'poster': collection_cover_name,
                       'overview': collection_data.get('overview')}

    return collection_info


def get_details(api_id, list_type):
    details_data = ApiData().get_details_and_credits_data(api_id, list_type)

    # Get the media cover
    media_cover_path = details_data.get("poster_path") or None

    if media_cover_path:
        media_cover_name = "{}.jpg".format(secrets.token_hex(8))
        try:
            ApiData().save_api_cover(media_cover_path, media_cover_name, list_type)
        except Exception as e:
            app.logger.error('[SYSTEM] Error trying to recover the poster: {}'.format(e))
            media_cover_name = "default.jpg"
    else:
        media_cover_name = "default.jpg"

    if list_type != ListType.MOVIES:
        tv_data = {'name': details_data.get("name", "Unknown") or "Unknown",
                   'original_name': details_data.get("original_name", "Unknown") or "Unknown",
                   'first_air_date': details_data.get("first_air_date", "Unknown") or "Unknown",
                   'last_air_date': details_data.get("last_air_date", "Unknown") or "Unknown",
                   'homepage': details_data.get("homepage", "Unknown") or "Unknown",
                   'in_production': details_data.get("in_production", False) or False,
                   'total_seasons': details_data.get("number_of_seasons", 1) or 1,
                   'total_episodes': details_data.get("number_of_episodes", 1) or 1,
                   'status': details_data.get("status", "Unknown") or "Unknown",
                   'vote_average': details_data.get("vote_average", 0) or 0,
                   'vote_count': details_data.get("vote_count", 0) or 0,
                   'synopsis': details_data.get("overview", "No overview avalaible.") or "No overview avalaible.",
                   'popularity': details_data.get("popularity", 0) or 0,
                   'themoviedb_id': details_data.get("id"),
                   'image_cover': media_cover_name,
                   'last_update': datetime.utcnow()}

        # Next episode to air (air_date, season, episode):
        next_episode_to_air = details_data.get("next_episode_to_air") or None
        if next_episode_to_air:
            tv_data['next_episode_to_air'] = next_episode_to_air['air_date']
            tv_data['season_to_air'] = next_episode_to_air['season_number']
            tv_data['episode_to_air'] = next_episode_to_air['episode_number']
        else:
            tv_data['next_episode_to_air'] = None
            tv_data['season_to_air'] = None
            tv_data['episode_to_air'] = None

        # Episode duration: List
        episode_duration = details_data.get("episode_run_time") or None
        if episode_duration:
            tv_data['episode_duration'] = episode_duration[0]
        else:
            if list_type == ListType.ANIME:
                tv_data['episode_duration'] = 24
            elif list_type == ListType.SERIES:
                tv_data['episode_duration'] = 45

        # Origin country: List
        origin_country = details_data.get("origin_country") or None
        if origin_country:
            tv_data['origin_country'] = origin_country[0]
        else:
            tv_data['origin_country'] = 'Unknown'

        # Created by: List
        created_by = details_data.get("created_by") or None
        if created_by:
            tv_data['created_by'] = ", ".join(creator['name'] for creator in created_by)
        else:
            tv_data['created_by'] = 'Unknown'

        # Seasons: List
        seasons = details_data.get('seasons') or None
        seasons_list = []
        if seasons:
            for i in range(0, len(seasons)):
                if seasons[i]['season_number'] <= 0:
                    continue
                season_dict = {'season': seasons[i]['season_number'],
                               'episodes': seasons[i]['episode_count']}
                seasons_list.append(season_dict)
        else:
            season_dict = {'season': 1,
                           'episodes': 1}
            seasons_list.append(season_dict)

        # Genres: List
        genres = details_data.get('genres') or None
        genres_list = []
        if genres:
            for i in range(0, len(genres)):
                genres_dict = {'genre': genres[i]["name"],
                               'genre_id': int(genres[i]["id"])}
                genres_list.append(genres_dict)
        else:
            genres_dict = {'genre': 'No genres found',
                           'genre_id': 0}
            genres_list.append(genres_dict)

        # Anime Genre from Jikan My AnimeList API
        a_genres_list = []
        if list_type == ListType.ANIME:
            try:
                anime_search = ApiData().anime_search(details_data.get("name"))
                mal_id = anime_search["results"][0]["mal_id"]
            except Exception as e:
                app.logger.error('[SYSTEM] Error requesting the Jikan search API: {}'.format(e))
                mal_id = None

            try:
                anime_genres = ApiData().get_anime_genres(mal_id)
                anime_genres = anime_genres["genres"]
            except Exception as e:
                app.logger.error('[SYSTEM] Error requesting the Jikan genre API: {}'.format(e))
                anime_genres = None

            if anime_genres:
                for i in range(0, len(anime_genres)):
                    genres_dict = {'genre': anime_genres[i]['name'],
                                   'genre_id': int(anime_genres[i]['mal_id'])}
                    a_genres_list.append(genres_dict)

        # Actors: List
        actors = details_data.get("credits").get("cast") or None
        actors_list = []
        if actors:
            for i in range(0, len(actors)):
                actors_dict = {'name': actors[i]["name"]}
                actors_list.append(actors_dict)
                if int(i) == 4:
                    break
        else:
            actors_dict = {'name': 'No actors found'}
            actors_list.append(actors_dict)

        # Network: List
        networks = details_data.get('networks') or None
        networks_list = []
        if networks:
            for i in range(0, len(networks)):
                networks_dict = {'network': networks[i]["name"]}
                networks_list.append(networks_dict)
                if i == 4:
                    break
        else:
            networks_dict = {'network': 'No networks found'}
            networks_list.append(networks_dict)

        data = {'tv_data': tv_data,
                'seasons_data': seasons_list,
                'genres_data': genres_list,
                'anime_genres_data': a_genres_list,
                'actors_data': actors_list,
                'networks_data': networks_list}
    elif list_type == ListType.MOVIES:
        movie_data = {'name': details_data.get("title", "Unknown") or 'Unknown',
                      'original_name': details_data.get("original_title", "Unknown") or 'Unknown',
                      'release_date': details_data.get("release_date", "Unknown") or 'Unknown',
                      'homepage': details_data.get("homepage", "Unknown") or 'Unknown',
                      'released': details_data.get("status", "Unknown") or "Unknown",
                      'vote_average': details_data.get("vote_average", 0) or 0,
                      'vote_count': details_data.get("vote_count", 0) or 0,
                      'synopsis': details_data.get("overview", "No overview avalaible.") or 'No overview avalaible.',
                      'popularity': details_data.get("popularity", 0) or 0,
                      'budget': details_data.get("budget", 0) or 0,
                      'revenue': details_data.get("revenue", 0) or 0,
                      'tagline': details_data.get("tagline", "-") or '-',
                      'runtime': details_data.get("runtime", 0) or 0,
                      'original_language': details_data.get("original_language", "Unknown") or 'Unknown',
                      'themoviedb_id': details_data.get("id"),
                      'image_cover': media_cover_name,
                      'director_name': "Unknown"}

        # Director Name: str
        the_crew = details_data.get("credits").get("crew") or None
        if the_crew:
            for element in the_crew:
                if element['job'] == "Director":
                    movie_data['director_name'] = element['name']
                    break

        # Collection ID: Int
        collection_id = details_data.get("belongs_to_collection")
        if collection_id:
            movie_data['collection_id'] = collection_id['id']
            collection_id = collection_id['id']
        else:
            movie_data['collection_id'] = None
            collection_id = None

        # Genres: List
        genres = details_data.get('genres') or None
        genres_list = []
        if genres:
            for i in range(0, len(genres)):
                genres_dict = {'genre': genres[i]["name"],
                               'genre_id': int(genres[i]["id"])}
                genres_list.append(genres_dict)
        else:
            genres_dict = {'genre': 'No genres found',
                           'genre_id': 0}
            genres_list.append(genres_dict)

        # Actors: List
        actors = details_data.get("credits").get("cast") or None
        actors_list = []
        if actors:
            for i in range(0, len(actors)):
                actors_dict = {'name': actors[i]["name"]}
                actors_list.append(actors_dict)
                if i == 4:
                    break
        else:
            actors_dict = {'name': 'No actors found'}
            actors_list.append(actors_dict)

        data = {'movies_data': movie_data,
                'collections_data': collection_id,
                'genres_data': genres_list,
                'actors_data': actors_list}

    return data


# ---------------------------------------------------------------------------------------------------


def check_cat_type(list_type, status):
    if list_type != ListType.MOVIES:
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


def get_medialist_data(list_type, all_media_data, user_id):
    common_media, total_media = get_media_count(user_id, list_type)

    media_data_list = []
    for media_data in all_media_data:
        add_data = MediaListDict(media_data, common_media, list_type).create_medialist_dict()
        media_data_list.append(add_data)

    try:
        percentage = int((len(common_media)/total_media)*100)
    except ZeroDivisionError:
        percentage = 0

    return {"media_data": media_data_list,
            "common_elements": [len(common_media), total_media, percentage]}


def save_new_cover(cover_file, media_type):
    if media_type == MediaType.SERIES:
        cover_path = url_for('static', filename='covers/series_covers/')
    elif media_type == MediaType.ANIME:
        cover_path = url_for('static', filename='covers/anime_covers/')
    elif media_type == MediaType.MOVIES:
        cover_path = url_for('static', filename='covers/movies_covers/')

    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(cover_file.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, cover_path, picture_fn)

    try:
        i = Image.open(cover_file)
    except Exception as e:
        app.logger.error('[SYSTEM] Error occured updating media cover: {}'.format(e))
        return "default.jpg"

    i = i.resize((300, 450), Image.ANTIALIAS)
    i.save(picture_path, quality=90)

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


def compute_time_spent(media=None, old_season=None, new_season=None, old_episode=None, new_episode=None, list_type=None,
                       movie_status=None, movie_delete=False, movie_add=False, new_rewatch=0, old_rewatch=0,
                       movie_runtime=0):

    def eps_watched(season, episode, all_seasons):
        nb_eps_watched = 0
        for i in range(1, season):
            nb_eps_watched += all_seasons[i-1].episodes
        nb_eps_watched += episode
        return nb_eps_watched

    if list_type == ListType.SERIES:
        old_time = current_user.time_spent_series
        old_total = eps_watched(old_season, old_episode, media.eps_per_season)
        new_total = eps_watched(new_season, new_episode, media.eps_per_season)
        current_user.time_spent_series = old_time + ((new_total-old_total)*media.episode_duration) + \
                                         (media.total_episodes*media.episode_duration*(new_rewatch-old_rewatch))
    elif list_type == ListType.ANIME:
        old_time = current_user.time_spent_anime
        old_total = eps_watched(old_season, old_episode, media.eps_per_season)
        new_total = eps_watched(new_season, new_episode, media.eps_per_season)
        current_user.time_spent_anime = old_time + ((new_total-old_total)*media.episode_duration) + \
                                        (media.total_episodes*media.episode_duration*(new_rewatch-old_rewatch))
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

    db.session.commit()


# ------- Python Scheduler -----------------------------------------------------------------------------------------


app.apscheduler.add_job(func=scheduled_task, trigger='cron', id='refresh_all_data', hour=3, minute=00)
