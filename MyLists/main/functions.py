import os
import json
import secrets
from collections import OrderedDict

from PIL import Image
from flask import abort
from pathlib import Path
from sqlalchemy import and_
from MyLists import db, app
from datetime import datetime
from flask_login import current_user
from MyLists.API_data import ApiData
from MyLists.general.functions import compute_media_time_spent
from MyLists.models import ListType, Status, AnimeList, Anime, AnimeEpisodesPerSeason, SeriesEpisodesPerSeason, \
    SeriesList, Series, MoviesList, Movies, SeriesGenre, AnimeGenre, MoviesGenre, UserLastUpdate, SeriesActors, \
    SeriesNetwork, AnimeNetwork, MoviesActors, MoviesCollections, AnimeActors, Notifications


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


def add_element_in_db(api_id, list_type):
    if list_type != ListType.MOVIES:
        # Add TV details to DB
        data = get_details(api_id, list_type)

        if list_type == ListType.SERIES:
            element = Series(**data['tv_data'])
        elif list_type == ListType.ANIME:
            element = Anime(**data['tv_data'])

        db.session.add(element)
        db.session.commit()

        # Add genres to DB
        if list_type == ListType.SERIES:
            for genre in data['genres_data']:
                genre.update({'series_id': element.id})
                db.session.add(SeriesGenre(**genre))
        elif list_type == ListType.ANIME:
            if data['anime_genres_data']:
                for genre in data['anime_genres_data']:
                    genre.update({'anime_id': element.id})
                    db.session.add(AnimeGenre(**genre))
            else:
                for genre in data['genres_data']:
                    genre.update({'anime_id': element.id})
                    db.session.add(AnimeGenre(**genre))

        # Add actors to DB
        for actor in data['actors_data']:
            if list_type == ListType.SERIES:
                actor.update({'series_id': element.id})
                db.session.add(SeriesActors(**actor))
            elif list_type == ListType.ANIME:
                actor.update({'anime_id': element.id})
                db.session.add(AnimeActors(**actor))

        # Add networks to DB
        for network in data['networks_data']:
            if list_type == ListType.SERIES:
                network.update({'series_id': element.id})
                db.session.add(SeriesNetwork(**network))
            elif list_type == ListType.ANIME:
                network.update({'anime_id': element.id})
                db.session.add(AnimeNetwork(**network))

        # Add seasons to DB
        for season in data['seasons_data']:
            if list_type == ListType.SERIES:
                season.update({'series_id': element.id})
                db.session.add(SeriesEpisodesPerSeason(**season))
            elif list_type == ListType.ANIME:
                season.update({'anime_id': element.id})
                db.session.add(AnimeEpisodesPerSeason(**season))
    elif list_type == ListType.MOVIES:
        # Add movie details to DB
        try:
            data = get_details(api_id, list_type)
        except:
            app.logger.error('[SYSTEM] - Error while getting: <movie_data>')
            abort(404)

        element = Movies(**data['movies_data'])
        db.session.add(element)
        db.session.commit()

        # Add genres to DB
        for genre in data['genres_data']:
            genre.update({'movies_id': element.id})
            db.session.add(MoviesGenre(**genre))

        # Add actors to DB
        for actor in data['actors_data']:
            actor.update({'movies_id': element.id})
            db.session.add(MoviesActors(**actor))

        # Add collection movie to DB
        if data['collections_data']:
            data = get_collection_movie(data['collections_data'])
            if data:
                update = MoviesCollections.query.filter_by(collection_id=data['collection_id']).first()
                if update:
                    MoviesCollections.query.filter_by(collection_id=data['collection_id']).update(**data)
                else:
                    db.session.add(MoviesCollections(**data))
            else:
                app.logger.error('Error adding/refreshing collection info of element ID: {}'.format(element.id))

    db.session.commit()

    return element


def get_medialist_data(element_data, list_type, covers_path, user_id):
    # Get the common media when looking at other lists
    current_list = []
    if user_id != current_user.id:
        if list_type == ListType.ANIME:
            current_media = db.session.query(AnimeList.anime_id).filter_by(user_id=current_user.id).all()
        elif list_type == ListType.SERIES:
            current_media = db.session.query(SeriesList.series_id).filter_by(user_id=current_user.id).all()
        elif list_type == ListType.MOVIES:
            current_media = db.session.query(MoviesList.movies_id).filter_by(user_id=current_user.id).all()
        current_list = [r[0] for r in current_media]

    group = 'categories'

    alphabet_group = {}
    genres_group = {}
    releases_group = {}
    tmdb_score_group = {}
    tmdb_scores_intervals = [[0, 2], [2, 4], [4, 6], [6, 8], [8, 11]]
    common_elements = 0
    if list_type != ListType.MOVIES:
        category = OrderedDict({'WATCHING': '',
                                'COMPLETED': '',
                                'ON HOLD': '',
                                'RANDOM': '',
                                'DROPPED': '',
                                'PLAN TO WATCH': ''})
        for element in element_data:
            # Get episodes per season
            nb_season = len(element[4].split(","))
            eps_per_season = element[6].split(",")[:nb_season]
            eps_per_season = [int(i) for i in eps_per_season]

            element_info = {"id": element[0].id,
                            "tmdb_id": element[0].themoviedb_id,
                            "cover": "{}{}".format(covers_path, element[0].image_cover),
                            "name": element[0].name,
                            "original_name": element[0].original_name,
                            "last_episode_watched": element[1].last_episode_watched,
                            "eps_per_season": eps_per_season,
                            "current_season": element[1].current_season,
                            "score": element[1].score,
                            "favorite": element[1].favorite,
                            "actors": element[5],
                            "genres": element[2],
                            "common": False,
                            "category": element[1].status}

            if element[0].id in current_list:
                element_info['common'] = True
                common_elements += 1

            if group == 'categories':
                if category[element[1].status.value.upper()] == '':
                    category[element[1].status.value.upper()] = [element_info]
                else:
                    category[element[1].status.value.upper()].append(element_info)
            elif group == 'alphabet':
                try:
                    if 0 <= int(element[0].name[0]) <= 9:
                        if '0-9' in alphabet_group:
                            alphabet_group['0-9'].append(element_info)
                        else:
                            alphabet_group['0-9'] = [element_info]
                except:
                    if element[0].name[0].upper() in alphabet_group:
                        alphabet_group[element[0].name[0].upper()].append(element_info)
                    else:
                        alphabet_group[element[0].name[0].upper()] = [element_info]
            elif group == 'genres':
                for genre in element[2].split(','):
                    if genre in genres_group:
                        genres_group[genre].append(element_info)
                    else:
                        genres_group[genre] = [element_info]
            elif group == 'releases':
                try:
                    if element[0].first_air_date.split('-')[0] in releases_group:
                        releases_group[element[0].first_air_date.split('-')[0]].append(element_info)
                    else:
                        releases_group[element[0].first_air_date.split('-')[0]] = [element_info]
                except:
                    if "No Airing Date" in releases_group:
                        releases_group["No Airing Date"].append(element_info)
                    else:
                        releases_group["No Airing Date"] = [element_info]
            elif group == 'TDMB_score':
                for interval in tmdb_scores_intervals:
                    if interval[0] <= element[0].vote_average < interval[1]:
                        if f'{interval[0]}-{interval[1]}' in tmdb_score_group:
                            tmdb_score_group[f'{interval[0]}-{interval[1]}'].append(element_info)
                            break
                        else:
                            tmdb_score_group[f'{interval[0]}-{interval[1]}'] = [element_info]
                            break
    elif list_type == ListType.MOVIES:
        category = OrderedDict({'COMPLETED': '',
                                'COMPLETED ANIMATION': '',
                                'PLAN TO WATCH': ''})
        for element in element_data:
            element_info = {"id": element[0].id,
                            "tmdb_id": element[0].themoviedb_id,
                            "cover": "{}{}".format(covers_path, element[0].image_cover),
                            "name": element[0].name,
                            "original_name": element[0].original_name,
                            "original_language": element[0].original_language,
                            "director": element[0].director_name,
                            "score": element[1].score,
                            "favorite": element[1].favorite,
                            "actors": element[3],
                            "genres": element[2],
                            "common": False}

            if element[0].id in current_list:
                element_info['common'] = True
                common_elements += 1

            if group == 'categories':
                if category[element[1].status.value.upper()] == '':
                    category[element[1].status.value.upper()] = [element_info]
                else:
                    category[element[1].status.value.upper()].append(element_info)
            elif group == 'alphabet':
                try:
                    if 0 <= int(element[0].name[0]) <= 9:
                        if '0-9' in alphabet_group:
                            alphabet_group['0-9'].append(element_info)
                        else:
                            alphabet_group['0-9'] = [element_info]
                except:
                    if element[0].name[0].upper() in alphabet_group:
                        alphabet_group[element[0].name[0].upper()].append(element_info)
                    else:
                        alphabet_group[element[0].name[0].upper()] = [element_info]

    try:
        percentage = int((common_elements/len(element_data))*100)
    except ZeroDivisionError:
        percentage = 0

    data = {"grouping": category,
            "common_elements": [common_elements, len(element_data), percentage]}

    return data


def load_media_sheet(media, user_id, list_type):
    # Basic element information
    element_info = {"id": media.id,
                    "homepage": media.homepage,
                    "vote_average": media.vote_average,
                    "vote_count": media.vote_count,
                    "synopsis": media.synopsis,
                    "popularity": media.popularity,
                    "lock_status": media.lock_status,
                    "actors": ', '.join([r.name for r in media.actors]),
                    "genres": ', '.join([r.genre for r in media.genres])}

    # Check <original_name> and change name accordingly for all media
    if media.original_name != media.name:
        element_info['name'] = media.name
        element_info['original_name'] = media.original_name
    else:
        element_info['name'] = None
        element_info['original_name'] = media.original_name

    # Depending on the media add/modify supplementary information
    if list_type != ListType.MOVIES:
        supp_info = {"created_by": media.created_by,
                     "total_seasons": media.total_seasons,
                     "total_episodes": media.total_episodes,
                     "prod_status": media.status,
                     "episode_duration": media.episode_duration,
                     "in_production": media.in_production,
                     "origin_country": media.origin_country,
                     "eps_per_season": [r.episodes for r in media.eps_per_season],
                     "networks": ', '.join([r.network for r in media.networks])}

        # Change <first_air_time> format
        if media.first_air_date != 'Unknown':
            supp_info['first_air_date'] = datetime.strptime(media.first_air_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            supp_info['first_air_date'] = 'Unknown'

        # Change <last_air_time> format
        if media.last_air_date != 'Unknown':
            supp_info['last_air_date'] = datetime.strptime(media.last_air_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            supp_info['last_air_date'] = 'Unknown'

        if list_type == ListType.SERIES:
            supp_info["media_type"] = 'Series'
            supp_info["cover"] = 'series_covers/{}'.format(media.image_cover)
            supp_info["cover_path"] = 'series_covers'
        elif list_type == ListType.ANIME:
            element_info['name'] = media.original_name
            element_info['original_name'] = media.name
            supp_info["media_type"] = 'Anime'
            supp_info["cover"] = 'anime_covers/{}'.format(media.image_cover)
            supp_info["cover_path"] = 'anime_covers'
    elif list_type == ListType.MOVIES:
        supp_info = {"media_type": 'Movies',
                     "cover_path": 'movies_covers',
                     "cover": 'movies_covers/{}'.format(media.image_cover),
                     "original_language": media.original_language,
                     "director": media.director_name,
                     "runtime": media.runtime,
                     "budget": media.budget,
                     "revenue": media.revenue,
                     "tagline": media.tagline,
                     "collection_data": media.collection_movies}

        # Change release date format
        if 'Unknown' not in media.release_date:
            supp_info['release_date'] = datetime.strptime(media.release_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            supp_info['release_date'] = 'Unknown'

    # Merge all the media info into one dict
    element_info.update(supp_info)

    # Recover the same media genres
    if len([r.genre for r in media.genres]) > 2:
        genres_list = [r.genre for r in media.genres][:2]
        genre_str = ','.join([g for g in genres_list])
    else:
        genres_list = [r.genre for r in media.genres]
        genre_str = ','.join([g for g in genres_list])
    same_genres = media.get_same_genres(genres_list, genre_str)

    # Recover the followers that have this media
    in_follows_list = media.in_follows_lists(user_id)

    # Recover the user information for this media
    in_user_list = media.in_user_list(user_id)
    if list_type != ListType.MOVIES:
        if in_user_list:
            user_info = {'in_user_list': True,
                         'last_episode_watched': in_user_list.last_episode_watched,
                         'current_season': in_user_list.current_season,
                         'score': in_user_list.score,
                         'favorite': in_user_list.favorite,
                         'status': in_user_list.status.value}
        else:
            user_info = {'last_episode_watched': 1,
                         'current_season': 1,
                         'score': 0,
                         'favorite': False,
                         'status': Status.WATCHING.value}
    elif list_type == ListType.MOVIES:
        if in_user_list:
            user_info = {'in_user_list': True,
                         'score': in_user_list.score,
                         'favorite': in_user_list.favorite,
                         'status': in_user_list.status.value}
        else:
            user_info = {'score': 0,
                         'favorite': False,
                         'status': Status.WATCHING.value}

    # Merge all data into one dict
    element_info['same_genres'] = same_genres
    element_info['in_follows_lists'] = in_follows_list
    element_info.update(user_info)

    return element_info


def save_new_cover(cover_file, media_type):
    if media_type == 'Series':
        cover_path = 'static/covers/series_covers/'
    elif media_type == 'Anime':
        cover_path = 'static/covers/anime_covers/'
    elif media_type == 'Movies':
        cover_path = 'static/covers/movies_covers/'

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


def compute_time_spent(media=None, old_season=None, new_season=None, old_episode=None, new_episode=None,
                       list_type=None, movie_status=None, movie_delete=False, movie_add=False):

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
        current_user.time_spent_series = old_time + ((new_total - old_total) * media.episode_duration)
    elif list_type == ListType.ANIME:
        old_time = current_user.time_spent_anime
        old_total = eps_watched(old_season, old_episode, media.eps_per_season)
        new_total = eps_watched(new_season, new_episode, media.eps_per_season)
        current_user.time_spent_series = old_time + ((new_total - old_total) * media.episode_duration)
    elif list_type == ListType.MOVIES:
        if movie_delete:
            if movie_status == Status.COMPLETED or movie_status == Status.COMPLETED_ANIMATION:
                current_user.time_spent_movies = current_user.time_spent_movies - media.runtime
        elif movie_add:
            if movie_status == Status.COMPLETED or movie_status == Status.COMPLETED_ANIMATION:
                current_user.time_spent_movies = current_user.time_spent_movies + media.runtime
        else:
            if movie_status == Status.COMPLETED or movie_status == Status.COMPLETED_ANIMATION:
                current_user.time_spent_movies = current_user.time_spent_movies + media.runtime
            else:
                current_user.time_spent_movies = current_user.time_spent_movies - media.runtime

    db.session.commit()


# ------- Python Scheduler -----------------------------------------------------------------------------------------


class ScheduledTask:
    def __init__(self):
        self.remove_non_list_media()
        self.remove_old_covers()
        self.automatic_media_refresh()
        self.new_releasing_movies()
        self.new_releasing_series()
        self.new_releasing_anime()

        compute_media_time_spent(ListType.SERIES)
        compute_media_time_spent(ListType.ANIME)
        compute_media_time_spent(ListType.MOVIES)

    @staticmethod
    def remove_non_list_media():
        app.logger.info('[SYSTEM] - Starting media remover')

        # SERIES DELETIONS
        series = db.session.query(Series, SeriesList).outerjoin(SeriesList, SeriesList.series_id == Series.id).all()
        count = 0
        to_delete = []
        for tv_series in series:
            if tv_series[1] is None:
                to_delete.append(tv_series[0].id)
        for deletion in to_delete:
            Series.query.filter_by(id=deletion).delete()
            SeriesActors.query.filter_by(series_id=deletion).delete()
            SeriesGenre.query.filter_by(series_id=deletion).delete()
            SeriesNetwork.query.filter_by(series_id=deletion).delete()
            SeriesEpisodesPerSeason.query.filter_by(series_id=deletion).delete()
            UserLastUpdate.query.filter_by(media_type=ListType.SERIES, media_id=deletion).delete()
            Notifications.query.filter_by(media_type='serieslist', media_id=deletion).delete()
            count += 1

            app.logger.info('Removed series with ID: {}'.format(deletion))
        app.logger.info('Total series removed: {}'.format(count))

        # ANIME DELETIONS
        anime = db.session.query(Anime, AnimeList).outerjoin(AnimeList, AnimeList.anime_id == Anime.id).all()
        count = 0
        to_delete = []
        for tv_anime in anime:
            if tv_anime[1] is None:
                to_delete.append(tv_anime[0].id)
        for deletion in to_delete:
            Anime.query.filter_by(id=deletion).delete()
            AnimeActors.query.filter_by(anime_id=deletion).delete()
            AnimeGenre.query.filter_by(anime_id=deletion).delete()
            AnimeNetwork.query.filter_by(anime_id=deletion).delete()
            AnimeEpisodesPerSeason.query.filter_by(anime_id=deletion).delete()
            UserLastUpdate.query.filter_by(media_type=ListType.ANIME, media_id=deletion).delete()
            Notifications.query.filter_by(media_type='animelist', media_id=deletion).delete()
            count += 1

            app.logger.info('Removed anime with ID: {}'.format(deletion))
        app.logger.info('Total anime removed: {}'.format(count))

        # MOVIES DELETIONS
        movies = db.session.query(Movies, MoviesList).outerjoin(MoviesList, MoviesList.movies_id == Movies.id).all()
        count = 0
        to_delete = []
        for movie in movies:
            if movie[1] is None:
                to_delete.append(movie[0].id)
        for deletion in to_delete:
            Movies.query.filter_by(id=deletion).delete()
            MoviesActors.query.filter_by(movies_id=deletion).delete()
            MoviesGenre.query.filter_by(movies_id=deletion).delete()
            UserLastUpdate.query.filter_by(media_type=ListType.MOVIES, media_id=deletion).delete()
            Notifications.query.filter_by(media_type='movieslist', media_id=deletion).delete()
            count += 1
            app.logger.info('Removed movie with ID: {0}'.format(deletion))
        app.logger.info('Total movies removed: {}'.format(count))

        db.session.commit()
        app.logger.info('[SYSTEM] - Automatic non user media remover finished')

    @staticmethod
    def remove_old_covers():
        app.logger.info('[SYSTEM] - Starting old covers remover')

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
                app.logger.info('Removed old series cover with name: {}'.format(image))
                count += 1
        app.logger.info('Finished, Total old series covers deleted: {}'.format(count))

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
                app.logger.info('Removed old anime cover with name: {}'.format(image))
                count += 1
        app.logger.info('Finished, Total old anime covers deleted: {}'.format(count))

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
                app.logger.info('Removed old movie cover with name: {}'.format(image))
                count += 1
        app.logger.info('Finished, Total old movies covers deleted: {}'.format(count))

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
                app.logger.info('Removed old movie collection cover with name: {}'.format(image))
                count += 1

        app.logger.info('Finished, Total old movies collections covers deleted: {}'.format(count))
        app.logger.info('[SYSTEM] - Automatic old covers remover finished')

    @staticmethod
    def refresh_element_data(api_id, list_type):
        if list_type != ListType.MOVIES:
            data = get_details(api_id, list_type)
            if data['tv_data'] is None:
                return None
        elif list_type == ListType.MOVIES:
            data = get_details(api_id, list_type)
            if data['movies_data'] is None:
                return None

        # Update the main details data
        if list_type == ListType.SERIES:
            Series.query.filter_by(themoviedb_id=api_id).update(data['tv_data'])
        elif list_type == ListType.ANIME:
            Anime.query.filter_by(themoviedb_id=api_id).update(data['tv_data'])
        elif list_type == ListType.MOVIES:
            Movies.query.filter_by(themoviedb_id=api_id).update(data['movies_data'])

        db.session.commit()

        # Refresh Seasons and Episodes
        def get_total_eps(user, eps_per_season):
            if user.status == Status.PLAN_TO_WATCH or user.status == Status.RANDOM:
                nb_eps_watched = 1
            else:
                nb_eps_watched = 0
                for i in range(1, user.current_season):
                    nb_eps_watched += eps_per_season[i - 1]
                nb_eps_watched += user.last_episode_watched

            return nb_eps_watched

        if list_type != ListType.MOVIES:
            if list_type == ListType.SERIES:
                element = Series.query.filter_by(themoviedb_id=api_id).first()
                old_seas_eps = \
                    [n.episodes for n in SeriesEpisodesPerSeason.query.filter_by(series_id=element.id).all()]
            elif list_type == ListType.ANIME:
                element = Anime.query.filter_by(themoviedb_id=api_id).first()
                old_seas_eps = \
                    [n.episodes for n in AnimeEpisodesPerSeason.query.filter_by(anime_id=element.id).all()]

            new_seas_eps = [d['episodes'] for d in data['seasons_data']]

            if new_seas_eps != old_seas_eps:
                if list_type == ListType.SERIES:
                    users_list = SeriesList.query.filter_by(series_id=element.id).all()

                    for user in users_list:
                        episodes_watched = get_total_eps(user, old_seas_eps)

                        count = 0
                        for i in range(0, len(data['seasons_data'])):
                            count += data['seasons_data'][i]['episodes']
                            if count == episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes']
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count > episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes'] - \
                                                            (count - episodes_watched)
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count < episodes_watched:
                                try:
                                    data['seasons_data'][i + 1]['season']
                                except IndexError:
                                    user.last_episode_watched = data['seasons_data'][i]['episodes']
                                    user.current_season = data['seasons_data'][i]['season']
                                    break
                        db.session.commit()

                    SeriesEpisodesPerSeason.query.filter_by(series_id=element.id).delete()
                    db.session.commit()

                    for seas in data['seasons_data']:
                        season = SeriesEpisodesPerSeason(series_id=element.id,
                                                         season=seas['season'],
                                                         episodes=seas['episodes'])
                        db.session.add(season)
                    db.session.commit()
                elif list_type == ListType.ANIME:
                    users_list = AnimeList.query.filter_by(anime_id=element.id).all()

                    for user in users_list:
                        episodes_watched = get_total_eps(user, old_seas_eps)

                        count = 0
                        for i in range(0, len(data['seasons_data'])):
                            count += data['seasons_data'][i]['episodes']
                            if count == episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes']
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count > episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes'] - (
                                        count - episodes_watched)
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count < episodes_watched:
                                try:
                                    data['seasons_data'][i + 1]['season']
                                except IndexError:
                                    user.last_episode_watched = data['seasons_data'][i]['episodes']
                                    user.current_season = data['seasons_data'][i]['season']
                                    break
                        db.session.commit()

                    AnimeEpisodesPerSeason.query.filter_by(anime_id=element.id).delete()
                    db.session.commit()

                    for seas in data['seasons_data']:
                        season = AnimeEpisodesPerSeason(anime_id=element.id,
                                                        season=seas['season'],
                                                        episodes=seas['episodes'])
                        db.session.add(season)
                    db.session.commit()

        return True

    def automatic_media_refresh(self):
        app.logger.info('[SYSTEM] - Starting automatic refresh')

        # Recover all the data
        all_series_tmdb_id = [m.themoviedb_id for m in Series.query.filter(Series.lock_status != True)]
        all_anime_tmdb_id = [m.themoviedb_id for m in db.session.query(Anime).filter(Anime.lock_status != True)]
        all_movies_tmdb_id = [m.themoviedb_id for m in db.session.query(Movies).filter(Movies.lock_status != True)]

        # Recover from API all the changed <TV_show> ID
        try:
            all_id_tv_changes = ApiData().get_changed_data(list_type=ListType.SERIES)
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the changed data from TMDB API: {}'.format(e))
            return

        # Recover from API all the changed <Movies> ID
        try:
            all_id_movies_changes = ApiData().get_changed_data(list_type=ListType.MOVIES)
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the changed data from TMDB API: {}'.format(e))
            return

        # Series
        for element in all_id_tv_changes["results"]:
            if element["id"] in all_series_tmdb_id:
                try:
                    self.refresh_element_data(element["id"], ListType.SERIES)
                    app.logger.info('Refreshed Series with TMDb_ID: {}'.format(element["id"]))
                except Exception as e:
                    app.logger.error('Error while refreshing: {}'.format(e))

        # Anime
        for element in all_id_tv_changes["results"]:
            if element["id"] in all_anime_tmdb_id:
                try:
                    self.refresh_element_data(element["id"], ListType.ANIME)
                    app.logger.info('Refreshed Anime with TMDb_ID: {}'.format(element["id"]))
                except Exception as e:
                    app.logger.error('Error while refreshing: {}'.format(e))

        # Refresh movies
        for element in all_id_movies_changes["results"]:
            if element["id"] in all_movies_tmdb_id:
                try:
                    self.refresh_element_data(element["id"], ListType.MOVIES)
                    app.logger.info('Refresh Movie with TMDb_ID: {}'.format(element["id"]))
                except Exception as e:
                    app.logger.error('Error while refreshing: {}'.format(e))

        app.logger.info('[SYSTEM] - Automatic refresh completed')

    @staticmethod
    def new_releasing_movies():
        all_movies = Movies.query.all()

        movies_id = []
        for movie in all_movies:
            try:
                diff = (datetime.utcnow() - datetime.strptime(movie.release_date, '%Y-%m-%d')).total_seconds()
                # Check if he movie released in one week or less (7 days)
                if diff < 0 and abs(diff/(3600*24)) <= 7:
                    movies_id.append(movie.id)
            except:
                pass

        movies_in_ptw = db.session.query(Movies, MoviesList) \
            .join(MoviesList, MoviesList.movies_id == Movies.id) \
            .filter(MoviesList.movies_id.in_(movies_id), MoviesList.status == Status.PLAN_TO_WATCH).all()

        for info in movies_in_ptw:
            if not bool(Notifications.query.filter_by(user_id=info[1].user_id,
                                                      media_type='movieslist',
                                                      media_id=info[0].id).first()):

                release_date = datetime.strptime(info[0].release_date, '%Y-%m-%d').strftime("%b %d")
                payload = {'name': info[0].name,
                           'release_date': release_date}

                data = Notifications(user_id=info[1].user_id,
                                     media_type='movieslist',
                                     media_id=info[0].id,
                                     payload_json=json.dumps(payload))
                db.session.add(data)

        db.session.commit()

    @staticmethod
    def new_releasing_series():
        all_series = Series.query.filter(Series.next_episode_to_air != None).all()

        series_id = []
        for series in all_series:
            try:
                diff = (datetime.utcnow() - datetime.strptime(series.next_episode_to_air, '%Y-%m-%d')).total_seconds()
                # Check if the next episode of the series is releasing in one week or less (7 days)
                if diff < 0 and abs(diff/(3600*24)) <= 7:
                    series_id.append(series.id)
            except:
                pass

        series_in_ptw = db.session.query(Series, SeriesList) \
            .join(SeriesList, SeriesList.series_id == Series.id) \
            .filter(SeriesList.series_id.in_(series_id), and_(SeriesList.status != Status.RANDOM,
                                                              SeriesList.status != Status.DROPPED)).all()

        for info in series_in_ptw:
            if not bool(Notifications.query.filter_by(user_id=info[1].user_id,
                                                      media_type='serieslist',
                                                      media_id=info[0].id).first()):

                release_date = datetime.strptime(info[0].next_episode_to_air, '%Y-%m-%d').strftime("%b %d")
                payload = {'name': info[0].name,
                           'release_date': release_date,
                           'season': info[0].season_to_air,
                           'episode': info[0].episode_to_air}

                data = Notifications(user_id=info[1].user_id,
                                     media_type='serieslist',
                                     media_id=info[0].id,
                                     payload_json=json.dumps(payload))
                db.session.add(data)

        db.session.commit()

    @staticmethod
    def new_releasing_anime():
        all_anime = Series.query.filter(Anime.next_episode_to_air != None).all()

        anime_id = []
        for anime in all_anime:
            try:
                diff = (datetime.utcnow() - datetime.strptime(anime.next_episode_to_air, '%Y-%m-%d')).total_seconds()
                # Check if the next episode of the series is releasing in one week or less (7 days)
                if diff < 0 and abs(diff/(3600*24)) <= 7:
                    anime_id.append(anime.id)
            except:
                pass

        anime_in_ptw = db.session.query(Anime, AnimeList) \
            .join(AnimeList, AnimeList.anime_id == Anime.id) \
            .filter(AnimeList.anime_id.in_(anime_id), and_(AnimeList.status != Status.RANDOM,
                                                           AnimeList.status != Status.DROPPED)).all()

        for info in anime_in_ptw:
            if not bool(Notifications.query.filter_by(user_id=info[1].user_id,
                                                      media_type='animelist',
                                                      media_id=info[0].id).first()):

                release_date = datetime.strptime(info[0].next_episode_to_air, '%Y-%m-%d').strftime("%b %d")
                payload = {'name': info[0].name,
                           'release_date': release_date,
                           'season': info[0].season_to_air,
                           'episode': info[0].episode_to_air}

                data = Notifications(user_id=info[1].user_id,
                                     media_type='animelist',
                                     media_id=info[0].id,
                                     payload_json=json.dumps(payload))
                db.session.add(data)

        db.session.commit()


app.apscheduler.add_job(func=ScheduledTask, trigger='cron', id='scheduled_task', hour=3, minute=00)
