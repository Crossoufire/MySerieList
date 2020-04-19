import os
import secrets

from pathlib import Path
from sqlalchemy import func
from MyLists import db, app
from datetime import datetime
from flask import flash, abort
from flask_login import current_user
from MyLists.API_data import ApiData
from MyLists.models import ListType, Status, AnimeList, Anime, AnimeEpisodesPerSeason, SeriesEpisodesPerSeason, \
    SeriesList, Series, MoviesList, Movies, SeriesGenre, AnimeGenre, MoviesGenre, UserLastUpdate, SeriesActors, \
    SeriesNetwork, AnimeNetwork, MoviesActors, MoviesCollections, AnimeActors


def get_collection_movie(collection_id):
    collection_data = ApiData().get_collection_data(collection_id)

    # Check the API response
    if collection_data is None:
        return None

    # Get the collection media cover
    collection_cover_path = collection_data.get("poster_path") or None

    if collection_cover_path:
        collection_cover_name = "{}.jpg".format(secrets.token_hex(8))
        issuccess = ApiData().save_api_cover(collection_cover_path, collection_cover_name,
                                             ListType.MOVIES, collection=True)
        if issuccess is False:
            collection_cover_name = "default.jpg"
    else:
        collection_cover_name = "default.jpg"

    collection_info = {'collection_id': collection_id,
                       'parts': len(collection_data.get('parts')),
                       'name': collection_data.get('name', "Unknown") or "Unknown",
                       'poster': collection_cover_name,
                       'overview': collection_data.get('overview', 'No overview available.') \
                          or 'No overview available.'}

    return collection_info


def get_details(api_id, list_type):
    details_data = ApiData().get_details_and_credits_data(api_id, list_type)

    # Check the API response
    if details_data is None:
        return None

    # Get the media cover
    media_cover_path = details_data.get("poster_path") or None

    if media_cover_path:
        media_cover_name = "{}.jpg".format(secrets.token_hex(8))
        issuccess = ApiData().save_api_cover(media_cover_path, media_cover_name, list_type)
        if issuccess is False:
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
        special = 0
        if seasons:
            # Check if a special season exist, if so: Ignore it
            if seasons[0]["season_number"] == 0:
                special = 1
            for i in range(special, len(seasons)):
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
            anime_genres = ApiData().get_anime_genres(details_data.get("name"))
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
                if i == 4: break
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
                if i == 4: break
        else:
            networks_dict = {'network': 'No networks found'}
            networks_list.append(networks_dict)

        return tv_data, seasons_list, genres_list, a_genres_list, actors_list, networks_list
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
                      'image_cover': media_cover_name}

        # Collection ID: Number
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
                if i == 4: break
        else:
            actors_dict = {'name': 'No actors found'}
            actors_list.append(actors_dict)

        return movie_data, collection_id, genres_list, actors_list


# -------------------------------------------


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
        if status == 'Completed' or status == 'Completed Animation':
            return Status.COMPLETED
        elif status == 'Plan to Watch':
            return Status.PLAN_TO_WATCH
        else:
            return None


def compute_time_spent(cat_type=None, old_eps=None, new_eps=None, old_seas=None, new_seas=None,
                       all_seas_data=None, media=None, old_status=None, new_status=None, list_type=None):

    def eps_watched_seasons(old_season, old_episode, new_season, all_seasons):
        nb_eps_watched = 0
        if new_season - old_season > 0:
            for i in range(old_season, new_season):
                nb_eps_watched += all_seasons[i-1].episodes
            nb_eps_watched += (1-old_episode)
        else:
            for i in range(new_season, old_season):
                nb_eps_watched += all_seasons[i-1].episodes
            nb_eps_watched += (1-old_episode)
            nb_eps_watched = -nb_eps_watched
        return nb_eps_watched

    def eps_watched_status(season, episode, all_seasons):
        nb_eps_watched = 0
        for i in range(1, season):
            nb_eps_watched += all_seasons[i-1].episodes
        nb_eps_watched += episode
        return nb_eps_watched

    if cat_type == 'episode':
        if list_type == ListType.SERIES:
            old_time = current_user.time_spent_series
            current_user.time_spent_series = old_time + ((new_eps-old_eps)*media.episode_duration)
        elif list_type == ListType.ANIME:
            old_time = current_user.time_spent_anime
            current_user.time_spent_anime = old_time + ((new_eps-old_eps)*media.episode_duration)

    elif cat_type == 'season':
        eps_watched = eps_watched_seasons(old_seas, old_eps, new_seas, all_seas_data)

        if list_type == ListType.SERIES:
            old_time = current_user.time_spent_series
            current_user.time_spent_series = old_time + (eps_watched*media.episode_duration)
        elif list_type == ListType.ANIME:
            old_time = current_user.time_spent_anime
            current_user.time_spent_anime = old_time + (eps_watched*media.episode_duration)

    elif cat_type == 'delete':
        if list_type == ListType.SERIES:
            eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
            old_time = current_user.time_spent_series
            current_user.time_spent_series = old_time - (eps_watched*media.episode_duration)
        elif list_type == ListType.ANIME:
            eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
            old_time = current_user.time_spent_anime
            current_user.time_spent_anime = old_time - (eps_watched*media.episode_duration)
        elif list_type == ListType.MOVIES:
            old_time = current_user.time_spent_movies
            current_user.time_spent_movies = old_time - media.runtime

    elif cat_type == 'category':
        if new_status == Status.WATCHING or new_status == Status.ON_HOLD or new_status == Status.DROPPED:
            if list_type == ListType.SERIES:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_series = current_user.time_spent_series + media.episode_duration
            elif list_type == ListType.ANIME:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_anime = current_user.time_spent_anime + media.episode_duration
        elif new_status == Status.COMPLETED or new_status == Status.COMPLETED_ANIMATION:
            if list_type == ListType.SERIES:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_series = current_user.time_spent_series + \
                                                    (media.total_episodes*media.episode_duration)
                else:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_series = current_user.time_spent_series + \
                                                    ((media.total_episodes-eps_watched)*media.episode_duration)
            elif list_type == ListType.ANIME:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_anime = current_user.time_spent_anime + \
                                                    (media.total_episodes*media.episode_duration)
                else:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_anime = current_user.time_spent_anime + \
                                                    ((media.total_episodes-eps_watched)*media.episode_duration)
            elif list_type == ListType.MOVIES:
                current_user.time_spent_movies = current_user.time_spent_movies + media.runtime
        elif new_status == Status.RANDOM:
            if list_type == ListType.SERIES:
                if old_status != Status.PLAN_TO_WATCH and old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_series = current_user.time_spent_series - eps_watched*media.episode_duration
            elif list_type == ListType.ANIME:
                if old_status != Status.PLAN_TO_WATCH and old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_anime = current_user.time_spent_anime - eps_watched*media.episode_duration
        elif new_status == Status.PLAN_TO_WATCH:
            if list_type == ListType.SERIES:
                if old_status != Status.RANDOM and old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_series = current_user.time_spent_series-(eps_watched*media.episode_duration)
            elif list_type == ListType.ANIME:
                if old_status != Status.RANDOM and old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_anime = current_user.time_spent_anime - eps_watched*media.episode_duration
            elif list_type == ListType.MOVIES:
                if old_status is not None:
                    current_user.time_spent_movies = current_user.time_spent_movies - media.runtime

    db.session.commit()


def get_medialist_data(element_data, list_type, covers_path, user_id):
    current_list = []
    if user_id != current_user.id:
        if list_type == ListType.ANIME:
            current_media = db.session.query(AnimeList.anime_id).filter_by(user_id=current_user.id).all()
        elif list_type == ListType.SERIES:
            current_media = db.session.query(SeriesList.series_id).filter_by(user_id=current_user.id).all()
        elif list_type == ListType.MOVIES:
            current_media = db.session.query(MoviesList.movies_id).filter_by(user_id=current_user.id).all()
        current_list = [r[0] for r in current_media]

    if list_type != ListType.MOVIES:
        watching_list = []
        completed_list = []
        onhold_list = []
        random_list = []
        dropped_list = []
        plantowatch_list = []

        common_elements = 0
        for element in element_data:
            # Get episodes per season
            nb_season = len(element[4].split(","))
            eps_per_season = element[6].split(",")[:nb_season]
            eps_per_season = [int(i) for i in eps_per_season]

            # Change first air time format
            first_air_date = element[0].first_air_date
            if 'Unknown' not in first_air_date:
                first_air_date = datetime.strptime(first_air_date, '%Y-%m-%d').strftime("%d %b %Y")

            # Change last air time format
            last_air_date = element[0].last_air_date
            if 'Unknown' not in last_air_date:
                last_air_date = datetime.strptime(last_air_date, '%Y-%m-%d').strftime("%d %b %Y")

            actors = element[5].replace(',', ', ')
            genres = element[2].replace(',', ', ')
            networks = element[3].replace(',', ', ')

            element_info = {"id": element[0].id,
                            "tmdb_id": element[0].themoviedb_id,
                            "cover": "{}{}".format(covers_path, element[0].image_cover),
                            "name": element[0].name,
                            "original_name": element[0].original_name,
                            "first_air_date": first_air_date,
                            "last_air_date": last_air_date,
                            "created_by": element[0].created_by,
                            "episode_duration": element[0].episode_duration,
                            "homepage": element[0].homepage,
                            "in_production": element[0].in_production,
                            "origin_country": element[0].origin_country,
                            "total_seasons": element[0].total_seasons,
                            "total_episodes": element[0].total_episodes,
                            "status": element[0].status,
                            "vote_average": element[0].vote_average,
                            "vote_count": element[0].vote_count,
                            "synopsis": element[0].synopsis,
                            "popularity": element[0].popularity,
                            "last_episode_watched": element[1].last_episode_watched,
                            "eps_per_season": eps_per_season,
                            "current_season": element[1].current_season,
                            "score": element[1].score,
                            "favorite": element[1].favorite,
                            "actors": actors,
                            "genres": genres,
                            "networks": networks}

            if element[1].status == Status.WATCHING:
                if element[0].id in current_list:
                    watching_list.append([element_info, True])
                    common_elements += 1
                else:
                    watching_list.append([element_info, False])
            elif element[1].status == Status.COMPLETED:
                if element[0].id in current_list:
                    completed_list.append([element_info, True])
                    common_elements += 1
                else:
                    completed_list.append([element_info, False])
            elif element[1].status == Status.ON_HOLD:
                if element[0].id in current_list:
                    onhold_list.append([element_info, True])
                    common_elements += 1
                else:
                    onhold_list.append([element_info, False])
            elif element[1].status == Status.RANDOM:
                if element[0].id in current_list:
                    random_list.append([element_info, True])
                    common_elements += 1
                else:
                    random_list.append([element_info, False])
            elif element[1].status == Status.DROPPED:
                if element[0].id in current_list:
                    dropped_list.append([element_info, True])
                    common_elements += 1
                else:
                    dropped_list.append([element_info, False])
            elif element[1].status == Status.PLAN_TO_WATCH:
                if element[0].id in current_list:
                    plantowatch_list.append([element_info, True])
                    common_elements += 1
                else:
                    plantowatch_list.append([element_info, False])

        element_all_data = [[watching_list, "WATCHING"], [completed_list, "COMPLETED"], [onhold_list, "ON HOLD"],
                            [random_list, "RANDOM"], [dropped_list, "DROPPED"], [plantowatch_list, "PLAN TO WATCH"]]

        try:
            percentage = int((common_elements/len(element_data))*100)
        except ZeroDivisionError:
            percentage = 0
        all_data_media = {"all_data": element_all_data,
                          "common_elements": [common_elements, len(element_data), percentage]}

        return all_data_media
    elif list_type == ListType.MOVIES:
        completed_list = []
        completed_list_animation = []
        plantowatch_list = []

        common_elements = 0
        for element in element_data:
            # Change release date format
            release_date = element[0].release_date
            if 'Unknown' not in release_date:
                release_date = datetime.strptime(release_date, '%Y-%m-%d').strftime("%d %b %Y")

            actors = element[3].replace(',', ', ')
            genres = element[2].replace(',', ', ')

            element_info = {"id": element[0].id,
                            "tmdb_id": element[0].themoviedb_id,
                            "cover": "{}{}".format(covers_path, element[0].image_cover),
                            "name": element[0].name,
                            "original_name": element[0].original_name,
                            "release_date": release_date,
                            "homepage": element[0].homepage,
                            "runtime": element[0].runtime,
                            "original_language": element[0].original_language,
                            "synopsis": element[0].synopsis,
                            "vote_average": element[0].vote_average,
                            "vote_count": element[0].vote_count,
                            "popularity": element[0].popularity,
                            "budget": element[0].budget,
                            "revenue": element[0].revenue,
                            "tagline": element[0].tagline,
                            "score": element[1].score,
                            "favorite": element[1].favorite,
                            "actors": actors,
                            "genres": genres}

            if element[1].status == Status.COMPLETED:
                if element[0].id in current_list:
                    completed_list.append([element_info, True])
                    common_elements += 1
                else:
                    completed_list.append([element_info, False])
            elif element[1].status == Status.COMPLETED_ANIMATION:
                if element[0].id in current_list:
                    completed_list_animation.append([element_info, True])
                    common_elements += 1
                else:
                    completed_list_animation.append([element_info, False])
            elif element[1].status == Status.PLAN_TO_WATCH:
                if element[0].id in current_list:
                    plantowatch_list.append([element_info, True])
                    common_elements += 1
                else:
                    plantowatch_list.append([element_info, False])

        element_all_data = [[completed_list, "COMPLETED"], [completed_list_animation, "COMPLETED ANIMATION"],
                            [plantowatch_list, "PLAN TO WATCH"]]

        try:
            percentage = int((common_elements/len(element_data))*100)
        except ZeroDivisionError:
            percentage = 0
        all_data_media = {"all_data": element_all_data,
                          "common_elements": [common_elements, len(element_data), percentage]}

        return all_data_media


def set_last_update(media_name, media_type, old_status=None, new_status=None, old_season=None,
                    new_season=None, old_episode=None, new_episode=None):

    check = UserLastUpdate.query.filter_by(user_id=current_user.id, media_type=media_type, media_name=media_name)\
        .order_by(UserLastUpdate.date.desc()).first()

    diff = 10000
    if check:
        diff = (datetime.utcnow()-check.date).total_seconds()

    update = UserLastUpdate(user_id=current_user.id, media_name=media_name, media_type=media_type,
                            old_status=old_status, new_status=new_status, old_season=old_season,
                            new_season=new_season, old_episode=old_episode, new_episode=new_episode,
                            date=datetime.utcnow())

    if diff > 600:
        db.session.add(update)
    else:
        db.session.delete(check)
        db.session.add(update)

    db.session.commit()


def load_media_sheet(element_id, user_id, list_type):
    # Retrieve the media data
    if list_type == ListType.SERIES:
        element = db.session.query(Series, func.group_concat(SeriesGenre.genre.distinct()),
                                   func.group_concat(SeriesNetwork.network.distinct()),
                                   func.group_concat(SeriesEpisodesPerSeason.season.distinct()),
                                   func.group_concat(SeriesActors.name.distinct()),
                                   func.group_concat(SeriesEpisodesPerSeason.episodes))\
            .join(SeriesGenre, SeriesGenre.series_id == Series.id)\
            .join(SeriesNetwork, SeriesNetwork.series_id == Series.id)\
            .join(SeriesActors, SeriesActors.series_id == Series.id)\
            .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.series_id == Series.id)\
            .filter(Series.id == element_id).first()
        cover = 'series_covers'
        in_user_list = SeriesList.query.filter_by(user_id=user_id, series_id=element_id).first()
    elif list_type == ListType.ANIME:
        element = db.session.query(Anime, func.group_concat(AnimeGenre.genre.distinct()),
                                   func.group_concat(AnimeNetwork.network.distinct()),
                                   func.group_concat(AnimeEpisodesPerSeason.season.distinct()),
                                   func.group_concat(AnimeActors.name.distinct()),
                                   func.group_concat(AnimeEpisodesPerSeason.episodes))\
            .join(AnimeGenre, AnimeGenre.anime_id == Anime.id)\
            .join(AnimeNetwork, AnimeNetwork.anime_id == Anime.id)\
            .join(AnimeActors, AnimeActors.anime_id == Anime.id)\
            .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.anime_id == Anime.id)\
            .filter(AnimeList.user_id == user_id, Anime.id == element_id).first()
        cover = 'anime_covers'
        in_user_list = AnimeList.query.filter_by(user_id=user_id, anime_id=element_id).first()
    elif list_type == ListType.MOVIES:
        element = db.session.query(Movies, func.group_concat(MoviesGenre.genre.distinct()),
                                   func.group_concat(MoviesActors.name.distinct()))\
            .join(MoviesGenre, MoviesGenre.movies_id == Movies.id)\
            .join(MoviesActors, MoviesActors.movies_id == Movies.id)\
            .filter(MoviesList.user_id == user_id, Movies.id == element_id).first()
        cover = 'movies_covers'
        in_user_list = MoviesList.query.filter_by(user_id=user_id, movies_id=element_id).first()

    if list_type != ListType.MOVIES:
        # Get episodes per season
        nb_season = len(element[3].split(","))
        eps_per_season = element[5].split(",")[:nb_season]
        eps_per_season = [int(i) for i in eps_per_season]
        print(eps_per_season)

        # Change first air time format
        first_air_date = element[0].first_air_date
        if 'Unknown' not in first_air_date:
            first_air_date = datetime.strptime(first_air_date, '%Y-%m-%d').strftime("%d %b %Y")

        # Change last air time format
        last_air_date = element[0].last_air_date
        if 'Unknown' not in last_air_date:
            last_air_date = datetime.strptime(last_air_date, '%Y-%m-%d').strftime("%d %b %Y")

        actors = element[4].replace(',', ', ')
        genres = element[1].replace(',', ', ')
        networks = element[2].replace(',', ', ')

        element_info = {"id": element[0].id,
                        "cover": '{}/{}'.format(cover, element[0].image_cover),
                        "name": element[0].name,
                        "original_name": element[0].original_name,
                        "first_air_date": first_air_date,
                        "last_air_date": last_air_date,
                        "created_by": element[0].created_by,
                        "episode_duration": element[0].episode_duration,
                        "homepage": element[0].homepage,
                        "in_production": element[0].in_production,
                        "origin_country": element[0].origin_country,
                        "total_seasons": element[0].total_seasons,
                        "total_episodes": element[0].total_episodes,
                        "status": element[0].status,
                        "vote_average": element[0].vote_average,
                        "vote_count": element[0].vote_count,
                        "synopsis": element[0].synopsis,
                        "popularity": element[0].popularity,
                        "eps_per_season": eps_per_season,
                        "in_user_list": False,
                        "actors": actors,
                        "genres": genres,
                        "networks": networks}

        if in_user_list:
            element_info['in_user_list'] = True
            element_info['last_episode_watched'] = in_user_list.last_episode_watched
            element_info['current_season'] = in_user_list.current_season
            element_info['score'] = in_user_list.score
            element_info['favorite'] = in_user_list.favorite
            element_info['status'] = in_user_list.status.value
        else:
            element_info['last_episode_watched'] = 1
            element_info['current_season'] = 1
            element_info['score'] = 0
            element_info['favorite'] = False
            element_info['status'] = Status.WATCHING.value
    else:
        # Change release date format
        release_date = element[0].release_date
        if 'Unknown' not in release_date:
            release_date = datetime.strptime(release_date, '%Y-%m-%d').strftime("%d %b %Y")

        actors = element[2].replace(',', ', ')
        genres = element[1].replace(',', ', ')

        element_info = {"id": element[0].id,
                        "cover": '{}/{}'.format(cover, element[0].image_cover),
                        "name": element[0].name,
                        "original_name": element[0].original_name,
                        "release_date": release_date,
                        "homepage": element[0].homepage,
                        "runtime": element[0].runtime,
                        "original_language": element[0].original_language,
                        "synopsis": element[0].synopsis,
                        "vote_average": element[0].vote_average,
                        "vote_count": element[0].vote_count,
                        "popularity": element[0].popularity,
                        "budget": element[0].budget,
                        "revenue": element[0].revenue,
                        "tagline": element[0].tagline,
                        "actors": actors,
                        "genres": genres,
                        "in_list": in_user_list}

    return element_info


def add_element_to_user(element, user_id, list_type, category):
    if list_type == ListType.SERIES:
        # Set season/episode to max if the "completed" category is selected
        if category == Status.COMPLETED:
            seasons_eps = SeriesEpisodesPerSeason.query.filter_by(series_id=element.id).all()
            current_season = len(seasons_eps)
            last_episode_watched = seasons_eps[-1].episodes
        else:
            current_season = 1
            last_episode_watched = 1

        user_list = SeriesList(user_id=user_id,
                               series_id=element.id,
                               current_season=current_season,
                               last_episode_watched=last_episode_watched,
                               status=category)

        # Commit the changes
        db.session.add(user_list)
        db.session.commit()
        app.logger.info('[{}] Added a series with the ID {}'.format(user_id, element.id))

        # Set the last update
        set_last_update(media_name=element.name, media_type=list_type, new_status=category)
    elif list_type == ListType.ANIME:
        # Set season/episode to max if the "completed" category is selected
        if category == Status.COMPLETED:
            seasons_eps = AnimeEpisodesPerSeason.query.filter_by(anime_id=element.id).all()
            current_season = len(seasons_eps)
            last_episode_watched = seasons_eps[-1].episodes
        else:
            current_season = 1
            last_episode_watched = 1

        user_list = AnimeList(user_id=user_id,
                              anime_id=element.id,
                              current_season=current_season,
                              last_episode_watched=last_episode_watched,
                              status=category)

        # Commit the changes
        db.session.add(user_list)
        db.session.commit()
        app.logger.info('[{}] Added an anime with the ID {}'.format(user_id, element.id))

        # Set the last update
        set_last_update(media_name=element.name, media_type=list_type, new_status=category)
    elif list_type == ListType.MOVIES:
        if category == Status.COMPLETED:
            # If it contain the "Animation" genre add to "Completed Animation"
            isanimation = MoviesGenre.query.filter_by(movies_id=element.id, genre="Animation").first()
            if isanimation:
                category = Status.COMPLETED_ANIMATION

        user_list = MoviesList(user_id=user_id,
                               movies_id=element.id,
                               status=category)

        # Commit the changes
        db.session.add(user_list)
        db.session.commit()
        app.logger.info('[{}] Added movie with the ID {}'.format(user_id, element.id))

        # Set the last update
        set_last_update(media_name=element.name, media_type=list_type, new_status=category)

    # Compute the new time spent
    compute_time_spent(cat_type="category", media=element, new_status=category, list_type=list_type)


def add_element_in_db(api_id, list_type, element_cat):
    if list_type != ListType.MOVIES:
        # Add TV details to DB
        tv_data, seasons_list, genres_list, a_genres_list, actors_list, networks_list = get_details(api_id, list_type)
        if tv_data is None:
            app.logger.error('[SYSTEM] - Error while getting: <tv_data>')
            return flash("There was an error fetching the API data, please try again later", "danger")
        if list_type == ListType.SERIES:
            element = Series(**tv_data)
        elif list_type == ListType.ANIME:
            element = Anime(**tv_data)
        db.session.add(element)
        db.session.commit()

        # Add genres to DB
        if list_type == ListType.SERIES:
            for genre in genres_list:
                genre.update({'series_id': element.id})
                db.session.add(SeriesGenre(**genre))
        elif list_type == ListType.ANIME:
            if a_genres_list:
                for genre in a_genres_list:
                    genre.update({'anime_id': element.id})
                    db.session.add(AnimeGenre(**genre))
            else:
                for genre in genres_list:
                    genre.update({'anime_id': element.id})
                    db.session.add(AnimeGenre(**genre))

        # Add actors to DB
        for actor in actors_list:
            if list_type == ListType.SERIES:
                actor.update({'series_id': element.id})
                db.session.add(SeriesActors(**actor))
            elif list_type == ListType.ANIME:
                actor.update({'anime_id': element.id})
                db.session.add(AnimeActors(**actor))

        # Add networks to DB
        for network in networks_list:
            if list_type == ListType.SERIES:
                network.update({'series_id': element.id})
                db.session.add(SeriesNetwork(**network))
            elif list_type == ListType.ANIME:
                network.update({'anime_id': element.id})
                db.session.add(AnimeNetwork(**network))

        # Add seasons to DB
        for season in seasons_list:
            if list_type == ListType.SERIES:
                season.update({'series_id': element.id})
                db.session.add(SeriesEpisodesPerSeason(**season))
            elif list_type == ListType.ANIME:
                season.update({'anime_id': element.id})
                db.session.add(AnimeEpisodesPerSeason(**season))
    elif list_type == ListType.MOVIES:
        # Add movie details to DB
        movie_data, collection_id, genres_list, actors_list = get_details(api_id, list_type)
        if movie_data is None:
            app.logger.error('[SYSTEM] - Error while getting: <movie_data>')
            return flash("There was an error fetching the API data, please try again later", "danger")
        element = Movies(**movie_data)
        db.session.add(element)
        db.session.commit()

        # Add genres to DB
        for genre in genres_list:
            genre.update({'movies_id': element.id})
            db.session.add(MoviesGenre(**genre))

        # Add actors to DB
        for actor in actors_list:
            actor.update({'movies_id': element.id})
            db.session.add(MoviesActors(**actor))

        # Add collection movie to DB
        if collection_id:
            collection_info = get_collection_movie(collection_id)
            db.session.add(MoviesCollections(**collection_info))

    db.session.commit()
    add_element_to_user(element, current_user.id, list_type, element_cat)


def add_element_in_db_bis(api_id, list_type):
    if list_type != ListType.MOVIES:
        # Add TV details to DB
        try:
            tv_data, seasons_list, genres_list, a_genres_list, actors_list, networks_list = get_details(api_id, list_type)
        except:
            app.logger.error('[SYSTEM] - Error while getting: <tv_data>')
            abort(404)
        if list_type == ListType.SERIES:
            element = Series(**tv_data)
        elif list_type == ListType.ANIME:
            element = Anime(**tv_data)
        db.session.add(element)
        db.session.commit()

        # Add genres to DB
        if list_type == ListType.SERIES:
            for genre in genres_list:
                genre.update({'series_id': element.id})
                db.session.add(SeriesGenre(**genre))
        elif list_type == ListType.ANIME:
            if a_genres_list:
                for genre in a_genres_list:
                    genre.update({'anime_id': element.id})
                    db.session.add(AnimeGenre(**genre))
            else:
                for genre in genres_list:
                    genre.update({'anime_id': element.id})
                    db.session.add(AnimeGenre(**genre))

        # Add actors to DB
        for actor in actors_list:
            if list_type == ListType.SERIES:
                actor.update({'series_id': element.id})
                db.session.add(SeriesActors(**actor))
            elif list_type == ListType.ANIME:
                actor.update({'anime_id': element.id})
                db.session.add(AnimeActors(**actor))

        # Add networks to DB
        for network in networks_list:
            if list_type == ListType.SERIES:
                network.update({'series_id': element.id})
                db.session.add(SeriesNetwork(**network))
            elif list_type == ListType.ANIME:
                network.update({'anime_id': element.id})
                db.session.add(AnimeNetwork(**network))

        # Add seasons to DB
        for season in seasons_list:
            if list_type == ListType.SERIES:
                season.update({'series_id': element.id})
                db.session.add(SeriesEpisodesPerSeason(**season))
            elif list_type == ListType.ANIME:
                season.update({'anime_id': element.id})
                db.session.add(AnimeEpisodesPerSeason(**season))
    elif list_type == ListType.MOVIES:
        # Add movie details to DB
        try:
            movie_data, collection_id, genres_list, actors_list = get_details(api_id, list_type)
        except:
            app.logger.error('[SYSTEM] - Error while getting: <movie_data>')
            abort(404)
        element = Movies(**movie_data)
        db.session.add(element)
        db.session.commit()

        # Add genres to DB
        for genre in genres_list:
            genre.update({'movies_id': element.id})
            db.session.add(MoviesGenre(**genre))

        # Add actors to DB
        for actor in actors_list:
            actor.update({'movies_id': element.id})
            db.session.add(MoviesActors(**actor))

        # Add collection movie to DB
        if collection_id:
            collection_info = get_collection_movie(collection_id)
            db.session.add(MoviesCollections(**collection_info))

    db.session.commit()
    media_data = load_media_sheet(element.id, current_user.id, list_type)

    return media_data


# ------------------------------------------- TMDb API Update Scheduler ---------------------------------------------- #


def scheduled_task():
    def automatic_media_refresh():
        app.logger.info('[SYSTEM] - Starting automatic refresh')

        def refresh_element_data(api_id, list_type):
            if list_type != ListType.MOVIES:
                tv_data, seasons_list, genres_list, a_genres_list, actors_list, networks_list = get_details(api_id,
                                                                                                            list_type)
                if tv_data is None:
                    return None
            elif list_type == ListType.MOVIES:
                movie_data, collection_id, genres_list, actors_list = get_details(api_id, list_type)
                if movie_data is None:
                    return None

            # Update the main details data
            if list_type == ListType.SERIES:
                Series.query.filter_by(themoviedb_id=api_id).update(tv_data)
            elif list_type == ListType.ANIME:
                Anime.query.filter_by(themoviedb_id=api_id).update(tv_data)
            elif list_type == ListType.MOVIES:
                Movies.query.filter_by(themoviedb_id=api_id).update(movie_data)

            db.session.commit()

            # Update the seasons
            if list_type == ListType.SERIES:
                element = Series.query.filter_by(themoviedb_id=api_id).first()
                for seas in seasons_list:
                    SeriesEpisodesPerSeason.query.filter_by(series_id=element.id,season=seas['season']).update(seas)
            elif list_type == ListType.ANIME:
                element = Anime.query.filter_by(themoviedb_id=api_id).first()
                for season in seasons_list:
                    AnimeEpisodesPerSeason.query.filter_by(anime_id=element.id, season=season['season']).update(season)

            db.session.commit()

            return True

        # Recover all the data
        all_series_tmdb_id = [r.themoviedb_id for r in db.session.query(Series)]
        all_anime_tmdb_id = [r.themoviedb_id for r in db.session.query(Anime)]
        all_movies_tmdb_id = [r.themoviedb_id for r in db.session.query(Movies)]

        # Recover from API all the changed TV ID and Movies ID
        all_id_tv_changes = ApiData().get_changed_data(list_type=ListType.SERIES)
        all_id_movies_changes = ApiData().get_changed_data(list_type=ListType.MOVIES)

        # Function to refresh series
        for element in all_id_tv_changes["results"]:
            if element["id"] in all_series_tmdb_id:
                info = refresh_element_data(element["id"], ListType.SERIES)
                if info:
                    app.logger.info('Refresh Series with TMDb_ID: {}'.format(element["id"]))
                else:
                    app.logger.error('Error while refreshing: no <tv_data>')

        # Function to refresh anime
        for element in all_id_tv_changes["results"]:
            if element["id"] in all_anime_tmdb_id:
                info = refresh_element_data(element["id"], ListType.ANIME)
                if info:
                    app.logger.info('Refresh Anime with TMDb_ID: {}'.format(element["id"]))
                else:
                    app.logger.error('Error while refreshing: no <tv_data>')

        # Function to refresh movies
        for element in all_id_movies_changes["results"]:
            if element["id"] in all_movies_tmdb_id:
                info = refresh_element_data(element["id"], ListType.MOVIES)
                if info:
                    app.logger.info('Refresh Movie with TMDb_ID: {}'.format(element["id"]))
                else:
                    app.logger.error('Error while refreshing: no <movie_data>')

        app.logger.info('[SYSTEM] - Automatic refresh completed')

    def remove_non_list_media():
        app.logger.info('[SYSTEM] - Starting media remover')

        # SERIES DELETIONS
        series = db.session.query(Series, SeriesList).outerjoin(SeriesList, SeriesList.series_id == Series.id).all()
        to_delete = []
        count = 0
        for tv_series in series:
            if tv_series[1] is None:
                to_delete.append(tv_series[0].id)
        for deletion in to_delete:
            Series.query.filter_by(id=deletion).delete()
            SeriesActors.query.filter_by(series_id=deletion).delete()
            SeriesGenre.query.filter_by(series_id=deletion).delete()
            SeriesNetwork.query.filter_by(series_id=deletion).delete()
            SeriesEpisodesPerSeason.query.filter_by(series_id=deletion).delete()
            count += 1

            app.logger.info('Removed series with ID: {}'.format(deletion))
        app.logger.info('Total series removed: {}'.format(count))

        # ANIME DELETIONS
        anime = db.session.query(Anime, AnimeList).outerjoin(AnimeList, AnimeList.anime_id == Anime.id).all()
        to_delete = []
        count = 0
        for tv_anime in anime:
            if tv_anime[1] is None:
                to_delete.append(tv_anime[0].id)
        for deletion in to_delete:
            Anime.query.filter_by(id=deletion).delete()
            AnimeActors.query.filter_by(anime_id=deletion).delete()
            AnimeGenre.query.filter_by(anime_id=deletion).delete()
            AnimeNetwork.query.filter_by(anime_id=deletion).delete()
            AnimeEpisodesPerSeason.query.filter_by(anime_id=deletion).delete()
            count += 1

            app.logger.info('Removed anime with ID: {}'.format(deletion))
        app.logger.info('Total anime removed: {}'.format(count))

        # MOVIES DELETIONS
        movies = db.session.query(Movies, MoviesList).outerjoin(MoviesList, MoviesList.movies_id == Movies.id).all()
        to_delete = []
        count = 0
        for movie in movies:
            if movie[1] is None:
                to_delete.append([movie[0].id, movie[0].collection_id])
        for deletion in to_delete:
            Movies.query.filter_by(id=deletion[0]).delete()
            MoviesActors.query.filter_by(movies_id=deletion[0]).delete()
            MoviesGenre.query.filter_by(movies_id=deletion[0]).delete()
            MoviesCollections.query.filter_by(collection_id=deletion[1]).delete()
            count += 1

            app.logger.info('Removed movie with ID: {0}. Remove movie collection with ID: {1}.'
                            .format(deletion[0], deletion[1]))
        app.logger.info('Total movies/movies collection removed: {}'.format(count))

        db.session.commit()
        app.logger.info('[SYSTEM] - Automatic non user media remove finished')

    def remove_old_covers():
        app.logger.info('[SYSTEM] - Starting the old covers remover')

        # SERIES OLD COVERS
        series = Series.query.all()
        path_series_covers = Path(app.root_path, 'static/covers/series_covers/')

        images_in_db = []
        for tv_show in series:
            images_in_db.append(tv_show.image_cover)

        images_saved = []
        for file in os.listdir(path_series_covers):
            images_saved.append(file)

        count = 0
        for image in images_saved:
            if image not in images_in_db and image != 'default.jpg':
                os.remove('{0}/{1}'.format(path_series_covers, image))
                app.logger.info('Removed the old series image with name: {}'.format(image))
                count += 1
        app.logger.info('Finished, {} old series images deleted'.format(count))


        # ANIME OLD COVERS
        anime = Anime.query.all()
        path_anime_covers = Path(app.root_path, 'static/covers/anime_covers/')

        images_in_db = []
        for tv_show in anime:
            images_in_db.append(tv_show.image_cover)

        images_saved = []
        for file in os.listdir(path_anime_covers):
            images_saved.append(file)

        count = 0
        for image in images_saved:
            if image not in images_in_db and image != 'default.jpg':
                os.remove('{0}/{1}'.format(path_anime_covers, image))
                app.logger.info('Removed the old anime image with name: {}'.format(image))
                count += 1
        app.logger.info('Finished, {} old anime images deleted'.format(count))


        # MOVIES OLD COVERS
        movies = Movies.query.all()
        path_movies_covers = Path(app.root_path, 'static/covers/movies_covers/')

        images_in_db = []
        for movie in movies:
            images_in_db.append(movie.image_cover)

        images_saved = []
        for file in os.listdir(path_movies_covers):
            images_saved.append(file)

        count = 0
        for image in images_saved:
            if image not in images_in_db and image != 'default.jpg':
                os.remove('{0}/{1}'.format(path_movies_covers, image))
                app.logger.info('Removed the old movie image with name: {}'.format(image))
                count += 1
        app.logger.info('Finished, {} old movies images deleted'.format(count))


        # MOVIES COLLECTION OLD COVERS
        movies_collec = MoviesCollections.query.all()
        path_movies_collec_covers = Path(app.root_path, 'static/covers/movies_collection_covers/')

        images_in_db = []
        for movie in movies_collec:
            images_in_db.append(movie.poster)

        images_saved = []
        for file in os.listdir(path_movies_collec_covers):
            images_saved.append(file)

        count = 0
        for image in images_saved:
            if image not in images_in_db and image != 'default.jpg':
                os.remove('{0}/{1}'.format(path_movies_collec_covers, image))
                app.logger.info('Removed the old movie collection image with name: {}'.format(image))
                count += 1

        app.logger.info('Finished, {} old movies collection images deleted'.format(count))
        app.logger.info('[SYSTEM] - Automatic remover of old covers finished')

    remove_non_list_media()
    remove_old_covers()
    automatic_media_refresh()


app.apscheduler.add_job(func=scheduled_task, trigger='cron', id='scheduled_task', hour=3, minute=0)
