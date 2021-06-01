import json
import secrets
import requests
from PIL import Image
from flask import abort
from MyLists import app
from pathlib import Path
from urllib import request
from datetime import datetime
from howlongtobeatpy import HowLongToBeat
from ratelimit import sleep_and_retry, limits
from MyLists.models import ListType, MediaType
from urllib.request import urlretrieve, Request


# --- GENERAL ---------------------------------------------------------------------------------------------------


def status_code(status_code):
    if status_code != 200:
        abort(status_code)


class ApiData(object):
    @classmethod
    def get_API_model(cls, list_type):
        for model in cls.__subclasses__():
            if list_type in model._group:
                return model


class TMDBMixin(object):
    local_covers_path = None

    def __init__(self):
        self.api_key = app.config['THEMOVIEDB_API_KEY']
        self.poster_base_url = 'https://image.tmdb.org/t/p/w300'
        self.media_details = {}
        self.API_data = None

    def TMDb_search(self, media_name, page=1):
        response = requests.get("https://api.themoviedb.org/3/search/multi?api_key={0}&query={1}&page={2}"
                                .format(self.api_key, media_name, page), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def save_api_cover(self, media_cover_path, media_cover_name):
        urlretrieve(f"{self.poster_base_url}{media_cover_path}", f"{self.local_covers_path}/{media_cover_name}")
        img = Image.open(f"{self.local_covers_path}/{media_cover_name}")
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save(f"{self.local_covers_path}/{media_cover_name}", quality=90)

    def get_media_cover(self):
        media_cover_name = 'default.jpg'
        media_cover_path = self.API_data.get('poster_path') or None
        if media_cover_path:
            media_cover_name = '{}.jpg'.format(secrets.token_hex(8))
            try:
                self.save_api_cover(media_cover_path, media_cover_name)
            except Exception as e:
                app.logger.error('[ERROR] - Trying to recover the poster: {}'.format(e))
                media_cover_name = 'default.jpg'

        return media_cover_name

    def get_genres(self):
        genres = self.API_data.get('genres') or None
        genres_list = []
        if genres:
            for i in range(0, len(genres)):
                genres_list.append({'genre': genres[i]['name'], 'genre_id': int(genres[i]['id'])})
        else:
            genres_list.append({'genre': 'Unknown', 'genre_id': 0})

        return genres_list

    def get_actors(self):
        actors = self.API_data.get('credits', {'cast': None}).get('cast') or None
        actors_list = []
        if actors:
            for actor in actors[:5]:
                actors_list.append({'name': actor["name"]})
        else:
            actors_list.append({'name': 'Unknown'})

        return actors_list


class ApiTV(TMDBMixin):
    _duration = 0

    def get_details_and_credits_data(self, API_id):
        response = requests.get("https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=credits"
                                .format(API_id, self.api_key), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def get_changed_data(self):
        response = requests.get("https://api.themoviedb.org/3/tv/changes?api_key={0}"
                                .format(self.api_key), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def get_anime_genres(self):
        return []

    def from_API_to_dict(self, API_data):
        self.API_data = API_data
        self.media_details = {'name': API_data.get('name', 'Unknown') or 'Unknown',
                              'original_name': API_data.get('original_name', 'Unknown') or 'Unknown',
                              'first_air_date': API_data.get('first_air_date', 'Unknown') or 'Unknown',
                              'last_air_date': API_data.get('last_air_date', 'Unknown') or 'Unknown',
                              'homepage': API_data.get('homepage', 'Unknown') or 'Unknown',
                              'in_production': API_data.get('in_production', False) or False,
                              'total_seasons': API_data.get('number_of_seasons', 1) or 1,
                              'total_episodes': API_data.get('number_of_episodes', 1) or 1,
                              'status': API_data.get('status', 'Unknown') or 'Unknown',
                              'vote_average': API_data.get('vote_average', 0) or 0,
                              'vote_count': API_data.get('vote_count', 0) or 0,
                              'synopsis': API_data.get('overview', 'Not defined.') or 'Not defined.',
                              'popularity': API_data.get('popularity', 0) or 0,
                              'api_id': API_data.get('id'),
                              'next_episode_to_air': None,
                              'season_to_air': None,
                              'episode_to_air': None,
                              'last_update': datetime.utcnow(),
                              'image_cover': self.get_media_cover()}

        next_episode_to_air = API_data.get("next_episode_to_air") or None
        if next_episode_to_air:
            self.media_details['next_episode_to_air'] = next_episode_to_air['air_date']
            self.media_details['season_to_air'] = next_episode_to_air['season_number']
            self.media_details['episode_to_air'] = next_episode_to_air['episode_number']

        duration = API_data.get("episode_run_time") or None
        self.media_details['duration'] = self._duration
        if duration and float(duration) != 0:
            self.media_details['duration'] = duration[0]

        origin_country = API_data.get("origin_country") or None
        self.media_details['origin_country'] = 'Unknown'
        if origin_country:
            self.media_details['origin_country'] = origin_country[0]

        created_by = API_data.get("created_by") or None
        self.media_details['created_by'] = 'Unknown'
        if created_by:
            self.media_details['created_by'] = ", ".join(creator['name'] for creator in created_by)

        seasons, seasons_list = API_data.get('seasons') or None, []
        if seasons:
            for i in range(0, len(seasons)):
                if seasons[i]['season_number'] <= 0:
                    continue
                seasons_list.append({'season': seasons[i]['season_number'], 'episodes': seasons[i]['episode_count']})
        else:
            seasons_list.append({'season': 1, 'episodes': 1})

        networks, networks_list = API_data.get('networks') or None, []
        if networks:
            for network in networks[:4]:
                networks_list.append({'network': network["name"]})
        else:
            networks_list.append({'network': 'Unknown'})

        genres_list = self.get_genres()
        actors_list = self.get_actors()
        anime_genres_list = self.get_anime_genres()

        return {'media_data': self.media_details, 'seasons_data': seasons_list, 'genres_data': genres_list,
                'anime_genres_data': anime_genres_list, 'actors_data': actors_list, 'networks_data': networks_list}


# --- CALL CLASSES -----------------------------------------------------------------------------------------------


class ApiSeries(ApiData, ApiTV):
    _duration = 45
    _group = [ListType.SERIES, MediaType.SERIES]
    local_covers_path = Path(app.root_path, "static/covers/series_covers/")

    def get_trending(self):
        response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                .format(self.api_key), timeout=10)

        status_code(response.status_code)

        return json.loads(response.text)


class ApiAnime(ApiData, ApiTV):
    _duration = 24
    _group = [ListType.ANIME, MediaType.ANIME]
    local_covers_path = Path(app.root_path, "static/covers/anime_covers/")

    @staticmethod
    def get_trending():
        response = requests.get("https://api.jikan.moe/v3/top/anime/1/airing", timeout=10)
        status_code(response.status_code)

        return json.loads(response.text)

    @staticmethod
    @sleep_and_retry
    @limits(calls=1, period=4)
    def api_anime_search(anime_name):
        """ Recover the anime title from TMDb to the MyAnimeList API to gather more accurate genres with the
        <get_anime_genres> function """

        response = requests.get("https://api.jikan.moe/v3/search/anime?q={0}".format(anime_name))

        status_code(response.status_code)

        return json.loads(response.text)

    @staticmethod
    @sleep_and_retry
    @limits(calls=1, period=4)
    def get_api_anime_genres(mal_id):
        """ Recover the genres of MyAnimeList with the shape: "genres":
        [{"mal_id": 1, "type": "anime", "name": "Action", "url": ""},
        {"mal_id": 37, "type": "anime", "name": "Supernatural","url": ""},
        {"mal_id": 16, "type": "anime", "name": "Magic","url": ""},
        {"mal_id": 10, "type": "anime", "name": "Fantasy","url": ""}] """

        response = requests.get("https://api.jikan.moe/v3/anime/{}".format(mal_id))

        status_code(response.status_code)

        return json.loads(response.text)

    def get_anime_genres(self):
        anime_genres_list = []
        try:
            anime_search = self.api_anime_search(self.API_data.get("name"))
            anime_genres = self.get_api_anime_genres(anime_search["results"][0]["mal_id"])['genres']
        except Exception as e:
            app.logger.error('[ERROR] - Requesting the Jikan API: {}'.format(e), {'API': 'Jikan'})
            anime_genres = None

        if anime_genres:
            for i in range(0, len(anime_genres)):
                anime_genres_list.append({'genre': anime_genres[i]['name'], 'genre_id': int(anime_genres[i]['mal_id'])})

        return anime_genres_list


class ApiMovies(ApiData, TMDBMixin):
    _group = [ListType.MOVIES, MediaType.MOVIES]
    local_covers_path = Path(app.root_path, "static/covers/movies_covers")

    def get_details_and_credits_data(self, API_id):
        response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits"
                                .format(API_id, self.api_key), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def get_changed_data(self):
        response = requests.get("https://api.themoviedb.org/3/movie/changes?api_key={0}"
                                .format(self.api_key), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def get_trending(self):
        response = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key={}"
                                .format(self.api_key), timeout=10)

        status_code(response.status_code)

        return json.loads(response.text)

    def from_API_to_dict(self, API_data):
        self.API_data = API_data
        self.media_details = {'name': API_data.get('title', 'Unknown') or 'Unknown',
                              'original_name': API_data.get('original_title', 'Unknown') or 'Unknown',
                              'release_date': API_data.get('release_date', 'Unknown') or 'Unknown',
                              'homepage': API_data.get('homepage', 'Unknown') or 'Unknown',
                              'released': API_data.get('status', 'Unknown') or '"Unknown',
                              'vote_average': API_data.get('vote_average', 0) or 0,
                              'vote_count': API_data.get('vote_count', 0) or 0,
                              'synopsis': API_data.get('overview', 'Not defined.') or 'Not defined.',
                              'popularity': API_data.get('popularity', 0) or 0,
                              'budget': API_data.get('budget', 0) or 0,
                              'revenue': API_data.get('revenue', 0) or 0,
                              'tagline': API_data.get('tagline', '-') or '-',
                              'duration': API_data.get('runtime', 0) or 0,
                              'original_language': API_data.get('original_language', 'Unknown') or 'Unknown',
                              'themoviedb_id': API_data.get('id'),
                              'director_name': 'Unknown',
                              'image_cover': self.get_media_cover()}

        the_crew = API_data.get('credits', {'crew': None}).get('crew') or None
        if the_crew:
            for element in the_crew:
                if element['job'] == 'Director':
                    self.media_details['director_name'] = element['name']
                    break

        genres_list = self.get_genres()
        actors_list = self.get_actors()

        return {'media_data': self.media_details, 'seasons_data': [], 'genres_data': genres_list, 'networks_data': [],
                'anime_genres_data': [], 'actors_data': actors_list}


class ApiGames(ApiData):
    _group = [ListType.GAMES, MediaType.GAMES]
    local_covers_path = Path(app.root_path, "static/covers/games_covers/")

    def __init__(self):
        self.api_key = app.config['IGDB_API_KEY']
        self.client_igdb = app.config['CLIENT_IGDB']
        self.poster_base_url = 'https://images.igdb.com/igdb/image/upload/t_1080p/'
        self.media_details = {}
        self.API_data = None

    @staticmethod
    def HLTB_time(game_name):
        games_list = HowLongToBeat().search(game_name)
        if games_list and len(games_list) > 0:
            game = max(games_list, key=lambda x: x.similarity)
            return {'main': game.gameplay_main, 'extra': game.gameplay_main_extra,
                    'completionist': game.gameplay_completionist}
        else:
            return {'main': None, 'extra': None, 'completionist': None}

    def get_details_and_credits_data(self, API_id):
        headers = {'Client-ID': f"{self.client_igdb}",
                   'Authorization': 'Bearer ' + self.api_key}
        body = 'fields name, cover.image_id, collection.name, game_engines.name, game_modes.name, ' \
               'platforms.name, genres.name, player_perspectives.name, total_rating, total_rating_count, ' \
               'first_release_date, involved_companies.company.name, involved_companies.developer, ' \
               'involved_companies.publisher, storyline, summary, themes.name, url, external_games.uid, ' \
               'external_games.category; where id={};' \
            .format(API_id)
        response = requests.post('https://api.igdb.com/v4/games', data=body, headers=headers, timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    @sleep_and_retry
    @limits(calls=4, period=1)
    def IGDB_search(self, game_name):
        headers = {'Client-ID': f"{app.config['CLIENT_IGDB']}",
                   'Authorization': 'Bearer ' + self.api_key}
        body = 'fields id, name, cover.image_id, first_release_date, storyline; search "{}";'.format(game_name)
        response = requests.post('https://api.igdb.com/v4/games', data=body, headers=headers, timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def save_api_cover(self, media_cover_path, media_cover_name):
        url_address = f"{self.poster_base_url}{media_cover_path}.jpg"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) '
                                 'Chrome/23.0.1271.64 Safari/537.11',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                   'Accept-Encoding': 'none',
                   'Accept-Language': 'en-US,en;q=0.8',
                   'Connection': 'keep-alive'}
        request_ = Request(url_address, None, headers)
        response = request.urlopen(request_)
        f = open(f"{self.local_covers_path}/{media_cover_name}", 'wb')
        f.write(response.read())
        f.close()

        img = Image.open(f"{self.local_covers_path}/{media_cover_name}")
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save(f"{self.local_covers_path}/{media_cover_name}", quality=90)

    def get_media_cover(self):
        media_cover_name = 'default.jpg'
        media_cover_path = self.API_data.get('cover')['image_id'] or None
        if media_cover_path:
            media_cover_name = '{}.jpg'.format(secrets.token_hex(8))
            try:
                self.save_api_cover(media_cover_path, media_cover_name)
            except Exception as e:
                app.logger.error('[ERROR] - Trying to recover the poster: {}'.format(e))
                media_cover_name = 'default.jpg'

        return media_cover_name

    def from_API_to_dict(self, API_data):
        API_data = API_data[0]
        self.API_data = API_data
        self.media_details = {'name': API_data.get('name', 'Unknown') or 'Unknown',
                              'release_date': API_data.get('first_release_date', 'Unknown') or 'Unknown',
                              'IGDB_url': API_data.get('url', 'Unknown') or 'Unknown',
                              'vote_average': API_data.get('total_rating', 0) or 0,
                              'vote_count': API_data.get('total_rating_count', 0) or 0,
                              'summary': API_data.get('summary', 'No summary found.') or 'No summary found.',
                              'storyline': API_data.get('storyline', 'No storyline found.') or 'No storyline found.',
                              'collection_name': API_data.get('collection', {'name': 'Unknown'})['name'] or 'Unknown',
                              'game_engine': API_data.get('game_engines', [{'name': 'Unknown'}])[0]['name'] or 'Unknown',
                              'player_perspective': API_data.get('player_perspectives', [{'name': 'Unknown'}])[0]['name'] or 'Unknown',
                              'game_modes': ','.join([x['name'] for x in API_data.get('game_modes', [{'name': 'Unknown'}])]),
                              'igdb_id': API_data.get('id'),
                              'image_cover': self.get_media_cover()}

        hltb_time = self.HLTB_time(self.media_details['name'])

        self.media_details['hltb_main_time'] = hltb_time['main']
        self.media_details['hltb_main_and_extra_time'] = hltb_time['extra']
        self.media_details['hltb_total_complete_time'] = hltb_time['completionist']

        platforms, platforms_list = API_data.get('platforms') or None, []
        if platforms:
            for platform in platforms:
                platforms_list.append({'name': platform["name"]})
        else:
            platforms_list.append({'name': 'Unknown'})

        companies, companies_list = API_data.get('involved_companies') or None, []
        if companies:
            for company in companies:
                companies_list.append({'name': company["company"]["name"], 'publisher': company["publisher"],
                                       'developer': company["developer"]})
        else:
            companies_list.append({'name': 'Unknown', 'publisher': False, 'developer': False})

        genres, genres_list = API_data.get('genres') or None, []
        if genres:
            for i in range(0, len(genres)):
                genres_list.append({'genre': genres[i]['name']})

        themes, themes_list = API_data.get('themes') or None, []
        if themes:
            for i in range(0, len(themes)):
                themes_list.append({'genre': themes[i]['name']})

        fusion_list = genres_list + themes_list
        if len(fusion_list) == 0:
            fusion_list.append({'genre': 'Unknown', 'genre_id': 0})

        return {'games_data': self.media_details, 'companies_data': companies_list, 'genres_data': fusion_list,
                'platforms_data': platforms_list, 'hltb_time': hltb_time}
