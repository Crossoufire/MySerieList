import json
import requests
from PIL import Image
from flask import abort
from MyLists import app
from pathlib import Path
from urllib import request
from MyLists.models import ListType
from howlongtobeatpy import HowLongToBeat
from ratelimit import sleep_and_retry, limits
from urllib.request import urlretrieve, Request


# --- GENERAL ---------------------------------------------------------------------------------------------------


def status_code(status_code):
    if status_code != 200:
        abort(status_code)


# --- SERIES, ANIME, MOVIES -------------------------------------------------------------------------------------


class TMDBMixin(object):
    local_covers_path = None

    def __init__(self):
        self.api_key = app.config['THEMOVIEDB_API_KEY']
        self.poster_base_url = 'https://image.tmdb.org/t/p/w300'

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


class ApiTV(TMDBMixin):
    def get_details_and_credits_data(self, api_id):
        response = requests.get("https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=credits"
                                .format(api_id, self.api_key), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def get_changed_data(self):
        response = requests.get("https://api.themoviedb.org/3/tv/changes?api_key={0}"
                                .format(self.api_key), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)


class ApiSeries(ApiTV):
    _group = [ListType.SERIES]
    local_covers_path = Path(app.root_path, "static/covers/series_covers/")

    def get_trending(self):
        response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                .format(self.api_key), timeout=10)

        status_code(response.status_code)

        return json.loads(response.text)


class ApiAnime(ApiTV):
    _group = [ListType.ANIME]
    local_covers_path = Path(app.root_path, "static/covers/anime_covers/")

    @staticmethod
    def get_trending():
        response = requests.get("https://api.jikan.moe/v3/top/anime/1/airing", timeout=10)

        status_code(response.status_code)

        return json.loads(response.text)

    @staticmethod
    @sleep_and_retry
    @limits(calls=1, period=4)
    def anime_search(anime_name):
        """ Recover the anime title from TMDb to the MyAnimeList API to gather more accurate genres with the
        <get_anime_genres> function """

        response = requests.get("https://api.jikan.moe/v3/search/anime?q={0}".format(anime_name))

        status_code(response.status_code)

        return json.loads(response.text)

    @staticmethod
    @sleep_and_retry
    @limits(calls=1, period=4)
    def get_anime_genres(mal_id):
        """ Recover the genres of MyAnimeList with the shape: "genres":
        [{"mal_id": 1, "type": "anime", "name": "Action", "url": ""},
        {"mal_id": 37, "type": "anime", "name": "Supernatural","url": ""},
        {"mal_id": 16, "type": "anime", "name": "Magic","url": ""},
        {"mal_id": 10, "type": "anime", "name": "Fantasy","url": ""}] """

        response = requests.get("https://api.jikan.moe/v3/anime/{}".format(mal_id))

        status_code(response.status_code)

        return json.loads(response.text)


class ApiMovies(TMDBMixin):
    _group = [ListType.MOVIES]
    local_covers_path = Path(app.root_path, "static/covers/movies_covers")

    def get_details_and_credits_data(self, api_id):
        response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits"
                                .format(api_id, self.api_key), timeout=15)

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


# --- GAMES ---------------------------------------------------------------------------------------------------


class ApiGames(object):
    _group = [ListType.GAMES]
    local_covers_path = Path(app.root_path, "static/covers/games_covers/")

    def __init__(self):
        self.api_key = app.config['IGDB_API_KEY']
        self.client_igdb = app.config['CLIENT_IGDB']
        self.poster_base_url = 'https://images.igdb.com/igdb/image/upload/t_1080p/'

    @staticmethod
    def HLTB_time(game_name):
        games_list = HowLongToBeat().search(game_name)
        if games_list and len(games_list) > 0:
            game = max(games_list, key=lambda x: x.similarity)
            hltb_time = {'main': game.gameplay_main,
                         'extra': game.gameplay_main_extra,
                         'completionist': game.gameplay_completionist}
            return hltb_time
        else:
            return {'main': None, 'extra': None, 'completionist': None}

    def get_details_and_credits_data(self, api_id):
        headers = {'Client-ID': f"{self.client_igdb}",
                   'Authorization': 'Bearer ' + self.api_key}
        body = 'fields name, cover.image_id, collection.name, game_engines.name, game_modes.name, ' \
               'platforms.name, genres.name, player_perspectives.name, total_rating, total_rating_count, ' \
               'first_release_date, involved_companies.company.name, involved_companies.developer, ' \
               'involved_companies.publisher, storyline, summary, themes.name, url, external_games.uid, ' \
               'external_games.category; where id={};' \
            .format(api_id)
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
