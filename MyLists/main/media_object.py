import secrets

from MyLists import app
from flask import url_for
from datetime import datetime
from flask_login import current_user
from MyLists.API_data import ApiData
from MyLists.models import ListType, Status


def latin_alphabet(original_name):
    try:
        original_name.encode('iso-8859-1')
        return True
    except UnicodeEncodeError:
        return False


def change_air_format(date):
    return datetime.strptime(date, '%Y-%m-%d').strftime("%d %b %Y")


class MediaDict:
    def __init__(self, media_data, list_type):
        self.data = media_data
        self.list_type = list_type
        self.media_info = {}

    def create_media_dict(self):
        self.media_info = {"id": self.data.id,
                           "homepage": self.data.homepage,
                           "vote_average": self.data.vote_average,
                           "vote_count": self.data.vote_count,
                           "synopsis": self.data.synopsis,
                           "popularity": self.data.popularity,
                           "lock_status": self.data.lock_status,
                           "actors": ', '.join([r.name for r in self.data.actors]),
                           "genres": ', '.join([r.genre for r in self.data.genres]),
                           "display_name": self.data.name,
                           "other_name": self.data.original_name,
                           "in_user_list": False,
                           "score": "---",
                           "favorite": False,
                           "rewatched": 0,
                           "comment": None}

        if latin_alphabet(self.data.original_name):
            self.media_info["display_name"] = self.data.original_name
            self.media_info["other_name"] = self.data.name

        if self.data.original_name == self.data.name:
            self.media_info["other_name"] = None

        self.add_genres()
        self.add_follow_list()

        if self.list_type != ListType.MOVIES:
            self.add_tv_dict()
        else:
            self.add_movies_dict()

        return self.media_info

    def add_tv_dict(self):
        self.media_info["created_by"] = self.data.created_by
        self.media_info["total_seasons"] = self.data.total_seasons
        self.media_info["total_episodes"] = self.data.total_episodes
        self.media_info["prod_status"] = self.data.status
        self.media_info["episode_duration"] = self.data.episode_duration
        self.media_info["in_production"] = self.data.in_production
        self.media_info["origin_country"] = self.data.origin_country
        self.media_info["eps_per_season"] = [r.episodes for r in self.data.eps_per_season]
        self.media_info["networks"] = ", ".join([r.network for r in self.data.networks])
        self.media_info["first_air_date"] = self.data.first_air_date
        self.media_info["last_air_date"] = self.data.last_air_date
        self.media_info["status"] = Status.WATCHING.value
        self.media_info["last_episode_watched"] = 1
        self.media_info["current_season"] = 1

        # Change <first_air_time> format
        if self.data.first_air_date != 'Unknown':
            self.media_info['first_air_date'] = change_air_format(self.data.first_air_date)

        # Change <last_air_time> format
        if self.data.last_air_date != 'Unknown':
            self.media_info['last_air_date'] = change_air_format(self.data.last_air_date)

        if self.list_type == ListType.SERIES:
            self.media_info["media_type"] = 'Series'
            self.media_info["cover"] = 'series_covers/{}'.format(self.data.image_cover),
            self.media_info["cover_path"] = 'series_covers'
        elif self.list_type == ListType.ANIME:
            self.media_info['name'] = self.data.original_name
            self.media_info['original_name'] = self.data.name
            self.media_info["media_type"] = 'Anime'
            self.media_info["cover"] = 'anime_covers/{}'.format(self.data.image_cover)
            self.media_info["cover_path"] = 'anime_covers'

        in_user_list = self.add_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["last_episode_watched"] = in_user_list.last_episode_watched
            self.media_info["current_season"] = in_user_list.current_season
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["rewatched"] = in_user_list.rewatched
            self.media_info["comment"] = in_user_list.comment

    def add_movies_dict(self):
        self.media_info["media_type"] = "Movies"
        self.media_info["cover_path"] = 'movies_covers'
        self.media_info["cover"] = 'movies_covers/{}'.format(self.data.image_cover)
        self.media_info["original_language"] = self.data.original_language
        self.media_info["director"] = self.data.director_name
        self.media_info["runtime"] = self.data.runtime
        self.media_info["budget"] = self.data.budget
        self.media_info["revenue"] = self.data.revenue
        self.media_info["tagline"] = self.data.tagline
        self.media_info["collection_data"] = self.data.collection_movies
        self.media_info['release_date'] = 'Unknown'
        self.media_info["status"] = Status.COMPLETED.value

        # Change <release_date> format
        if self.data.release_date != 'Unknown':
            self.media_info['release_date'] = change_air_format(self.data.release_date)

        in_user_list = self.add_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["rewatched"] = in_user_list.rewatched
            self.media_info["comment"] = in_user_list.comment

    def add_genres(self):
        genres_list = [r.genre for r in self.data.genres]
        genre_str = ','.join([g for g in genres_list])
        if len(genres_list) > 2:
            genres_list = genres_list[:2]
            genre_str = ','.join([g for g in genres_list[:2]])

        self.media_info['same_genres'] = self.data.get_same_genres(genres_list, genre_str)

    def add_follow_list(self):
        self.media_info['in_follows_lists'] = self.data.in_follows_lists(current_user.id)

    def add_user_list(self):
        return self.data.in_user_list(current_user.id)


class MediaListDict:
    def __init__(self, media_data, common_media, list_type):
        self.data = media_data
        self.list_type = list_type
        self.common_media = common_media
        self.media_info = {}

        if self.list_type == ListType.SERIES:
            self.cover_path = url_for('static', filename='covers/series_covers/')
        elif self.list_type == ListType.ANIME:
            self.cover_path = url_for('static', filename='covers/anime_covers/')
        elif self.list_type == ListType.MOVIES:
            self.cover_path = url_for('static', filename='covers/movies_covers/')

    def create_medialist_dict(self):
        self.media_info = {"id": self.data[0].id,
                           "tmdb_id": self.data[0].themoviedb_id,
                           "cover": "{}{}".format(self.cover_path, self.data[0].image_cover),
                           "score": self.data[1].score,
                           "favorite": self.data[1].favorite,
                           "rewatched": self.data[1].rewatched,
                           "comment": self.data[1].comment,
                           "category": self.data[1].status.value,
                           "display_name": self.data[0].name,
                           "other_name": self.data[0].original_name,
                           "common": False,
                           "media": "Movies"}

        if not self.media_info['score'] or self.media_info['score'] == -1:
            self.media_info['score'] = '---'

        if latin_alphabet(self.data[0].original_name):
            self.media_info["display_name"] = self.data[0].original_name
            self.media_info["other_name"] = self.data[0].name

        if self.data[0].id in self.common_media:
            self.media_info['common'] = True

        if self.list_type != ListType.MOVIES:
            self.add_tv_dict()

        return self.media_info

    def add_tv_dict(self):
        self.media_info['media'] = 'Series'
        if self.list_type == ListType.ANIME:
            self.media_info['media'] = 'Anime'

        self.media_info["last_episode_watched"] = self.data[1].last_episode_watched
        self.media_info["eps_per_season"] = [eps.episodes for eps in self.data[0].eps_per_season]
        self.media_info["current_season"] = self.data[1].current_season


class MediaDetail:
    def __init__(self, media_data, list_type):
        self.media_data = media_data
        self.list_type = list_type
        self.media_detail = {}

        if list_type != ListType.MOVIES:
            self.get_tv_details()
        elif list_type == ListType.MOVIES:
            self.get_movies_details()

    def get_media_cover(self):
        media_cover_path = self.media_data.get("poster_path") or None
        media_cover_name = "default.jpg"
        if media_cover_path:
            media_cover_name = "{}.jpg".format(secrets.token_hex(8))
            try:
                ApiData().save_api_cover(media_cover_path, media_cover_name, self.list_type)
            except Exception as e:
                app.logger.error('[ERROR] - Trying to recover the poster: {}'.format(e))
                media_cover_name = "default.jpg"

        return media_cover_name

    def get_tv_details(self):
        self.media_detail = {'name': self.media_data.get("name", "Unknown") or "Unknown",
                             'original_name': self.media_data.get("original_name", "Unknown") or "Unknown",
                             'first_air_date': self.media_data.get("first_air_date", "Unknown") or "Unknown",
                             'last_air_date': self.media_data.get("last_air_date", "Unknown") or "Unknown",
                             'homepage': self.media_data.get("homepage", "Unknown") or "Unknown",
                             'in_production': self.media_data.get("in_production", False) or False,
                             'total_seasons': self.media_data.get("number_of_seasons", 1) or 1,
                             'total_episodes': self.media_data.get("number_of_episodes", 1) or 1,
                             'status': self.media_data.get("status", "Unknown") or "Unknown",
                             'vote_average': self.media_data.get("vote_average", 0) or 0,
                             'vote_count': self.media_data.get("vote_count", 0) or 0,
                             'synopsis': self.media_data.get("overview", "No overview avalaible.") or
                                         "No overview available.",
                             'popularity': self.media_data.get("popularity", 0) or 0,
                             'themoviedb_id': self.media_data.get("id"),
                             'image_cover': self.get_media_cover(),
                             'last_update': datetime.utcnow()}

        # Next episode to air (air_date, season, episode):
        next_episode_to_air = self.media_data.get("next_episode_to_air") or None
        tv_data['next_episode_to_air'] = None
        tv_data['season_to_air'] = None
        tv_data['episode_to_air'] = None
        if next_episode_to_air:
            tv_data['next_episode_to_air'] = next_episode_to_air['air_date']
            tv_data['season_to_air'] = next_episode_to_air['season_number']
            tv_data['episode_to_air'] = next_episode_to_air['episode_number']

        # Episode duration: List
        episode_duration = self.media_data.get("episode_run_time") or None
        if episode_duration:
            tv_data['episode_duration'] = episode_duration[0]
        else:
            if list_type == ListType.ANIME:
                tv_data['episode_duration'] = 24
            elif list_type == ListType.SERIES:
                tv_data['episode_duration'] = 45

        # Origin country: List
        origin_country = self.media_data.get("origin_country") or None
        if origin_country:
            tv_data['origin_country'] = origin_country[0]
        else:
            tv_data['origin_country'] = 'Unknown'

        # Created by: List
        created_by = self.media_data.get("created_by") or None
        if created_by:
            tv_data['created_by'] = ", ".join(creator['name'] for creator in created_by)
        else:
            tv_data['created_by'] = 'Unknown'

        # Seasons: List
        seasons = self.media_data.get('seasons') or None
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
        genres = self.media_data.get('genres') or None
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
                anime_search = ApiData().anime_search(self.media_data.get("name"))
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
        actors = self.media_data.get("credits").get("cast") or None
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
        networks = self.media_data.get('networks') or None
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

    def get_movies_details(self):
        movie_data = {'name': self.media_data.get("title", "Unknown") or 'Unknown',
                      'original_name': self.media_data.get("original_title", "Unknown") or 'Unknown',
                      'release_date': self.media_data.get("release_date", "Unknown") or 'Unknown',
                      'homepage': self.media_data.get("homepage", "Unknown") or 'Unknown',
                      'released': self.media_data.get("status", "Unknown") or "Unknown",
                      'vote_average': self.media_data.get("vote_average", 0) or 0,
                      'vote_count': self.media_data.get("vote_count", 0) or 0,
                      'synopsis': self.media_data.get("overview",
                                                   "No overview avalaible.") or 'No overview avalaible.',
                      'popularity': self.media_data.get("popularity", 0) or 0,
                      'budget': self.media_data.get("budget", 0) or 0,
                      'revenue': self.media_data.get("revenue", 0) or 0,
                      'tagline': self.media_data.get("tagline", "-") or '-',
                      'runtime': self.media_data.get("runtime", 0) or 0,
                      'original_language': self.media_data.get("original_language", "Unknown") or 'Unknown',
                      'themoviedb_id': self.media_data.get("id"),
                      'image_cover': media_cover_name,
                      'director_name': "Unknown"}

        # Director Name: str
        the_crew = self.media_data.get("credits").get("crew") or None
        if the_crew:
            for element in the_crew:
                if element['job'] == "Director":
                    movie_data['director_name'] = element['name']
                    break

        # Collection ID: Int
        collection_id = self.media_data.get("belongs_to_collection")
        if collection_id:
            movie_data['collection_id'] = collection_id['id']
            collection_id = collection_id['id']
        else:
            movie_data['collection_id'] = None
            collection_id = None

        # Genres: List
        genres = self.media_data.get('genres') or None
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
        actors = self.media_data.get("credits").get("cast") or None
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
