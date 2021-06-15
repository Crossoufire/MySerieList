import json
import secrets
import requests
from PIL import Image
from flask import abort
from pathlib import Path
from urllib import request
from MyLists import app, db
from datetime import datetime
# from howlongtobeatpy import HowLongToBeat
from ratelimit import sleep_and_retry, limits
from urllib.request import urlretrieve, Request
from MyLists.models import ListType, MediaType, Series, Anime, SeriesGenre, AnimeGenre, AnimeActors, SeriesActors, \
    Movies, SeriesNetwork, AnimeNetwork, SeriesEpisodesPerSeason, AnimeEpisodesPerSeason, MoviesGenre, MoviesActors, \
    GamesCompanies, GamesPlatforms, Games, GamesGenre


# --- GENERAL ---------------------------------------------------------------------------------------------------


def status_code(status_code):
    if status_code != 200:
        abort(status_code)


class ApiData(object):
    _duration = 0
    local_covers_path = None

    def __init__(self, API_id=None):
        self.api_key = None
        self.client_igdb = None
        self.poster_base_url = None
        self.media_details = {}
        self.API_data = None
        self.API_id = API_id
        self.all_data = {}
        self.media = None

    @classmethod
    def get_API_model(cls, list_type):
        def all_subclasses(cls):
            return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])
        all_ = all_subclasses(cls)
        for model in all_:
            if list_type in model.group:
                return model

    def save_media_to_db(self):
        self.get_details_and_credits_data()
        self.from_API_to_dict()
        self.add_data_to_db()

        return self.media

    def update_media_data(self):
        self.get_details_and_credits_data()
        self.from_API_to_dict(updating=True)

        return self.all_data


class TMDBMixin(ApiData):
    group = []

    def __init__(self, API_id=None):
        super().__init__(API_id)
        self.api_key = app.config['THEMOVIEDB_API_KEY']
        self.poster_base_url = 'https://image.tmdb.org/t/p/w300'
        self.API_id = API_id

    def search(self, media_name, page=1):
        response = requests.get("https://api.themoviedb.org/3/search/multi?api_key={0}&query={1}&page={2}"
                                .format(self.api_key, media_name, page), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

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

    def save_api_cover(self, media_cover_path, media_cover_name):
        urlretrieve(f"{self.poster_base_url}{media_cover_path}", f"{self.local_covers_path}/{media_cover_name}")
        img = Image.open(f"{self.local_covers_path}/{media_cover_name}")
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save(f"{self.local_covers_path}/{media_cover_name}", quality=90)


class ApiTV(TMDBMixin):
    group = []

    def get_details_and_credits_data(self):
        response = requests.get("https://api.themoviedb.org/3/tv/{}?api_key={}&append_to_response=credits"
                                .format(self.API_id, self.api_key), timeout=15)

        status_code(response.status_code)
        self.API_data = json.loads(response.text)

    def get_changed_data(self):
        response = requests.get("https://api.themoviedb.org/3/tv/changes?api_key={0}"
                                .format(self.api_key), timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def from_API_to_dict(self, updating=False):
        self.media_details = {'name': self.API_data.get('name', 'Unknown') or 'Unknown',
                              'original_name': self.API_data.get('original_name', 'Unknown') or 'Unknown',
                              'first_air_date': self.API_data.get('first_air_date', 'Unknown') or 'Unknown',
                              'last_air_date': self.API_data.get('last_air_date', 'Unknown') or 'Unknown',
                              'homepage': self.API_data.get('homepage', 'Unknown') or 'Unknown',
                              'in_production': self.API_data.get('in_production', False) or False,
                              'total_seasons': self.API_data.get('number_of_seasons', 1) or 1,
                              'total_episodes': self.API_data.get('number_of_episodes', 1) or 1,
                              'status': self.API_data.get('status', 'Unknown') or 'Unknown',
                              'vote_average': self.API_data.get('vote_average', 0) or 0,
                              'vote_count': self.API_data.get('vote_count', 0) or 0,
                              'synopsis': self.API_data.get('overview', 'Not defined.') or 'Not defined.',
                              'popularity': self.API_data.get('popularity', 0) or 0,
                              'api_id': self.API_data.get('id'),
                              'next_episode_to_air': None,
                              'season_to_air': None,
                              'episode_to_air': None,
                              'last_update': datetime.utcnow(),
                              'image_cover': self.get_media_cover()}

        next_episode_to_air = self.API_data.get("next_episode_to_air") or None
        if next_episode_to_air:
            self.media_details['next_episode_to_air'] = next_episode_to_air['air_date']
            self.media_details['season_to_air'] = next_episode_to_air['season_number']
            self.media_details['episode_to_air'] = next_episode_to_air['episode_number']

        duration = self.API_data.get("episode_run_time") or None
        self.media_details['duration'] = self._duration
        if duration and float(duration[0]) != 0:
            self.media_details['duration'] = duration[0]

        origin_country = self.API_data.get("origin_country") or None
        self.media_details['origin_country'] = 'Unknown'
        if origin_country:
            self.media_details['origin_country'] = origin_country[0]

        created_by = self.API_data.get("created_by") or None
        self.media_details['created_by'] = 'Unknown'
        if created_by:
            self.media_details['created_by'] = ", ".join(creator['name'] for creator in created_by)

        seasons, seasons_list = self.API_data.get('seasons') or None, []
        if seasons:
            for i in range(0, len(seasons)):
                if seasons[i]['season_number'] <= 0:
                    continue
                seasons_list.append({'season': seasons[i]['season_number'], 'episodes': seasons[i]['episode_count']})
        else:
            seasons_list.append({'season': 1, 'episodes': 1})

        networks, networks_list = self.API_data.get('networks') or None, []
        if networks:
            for network in networks[:4]:
                networks_list.append({'network': network["name"]})
        else:
            networks_list.append({'network': 'Unknown'})

        genres_list, actors_list, anime_genres_list = [], [], []
        if not updating:
            genres_list = self.get_genres()
            actors_list = self.get_actors()
            anime_genres_list = self.get_anime_genres()

        self.all_data = {'media_data': self.media_details, 'seasons_data': seasons_list, 'genres_data': genres_list,
                         'anime_genres_data': anime_genres_list, 'actors_data': actors_list,
                         'networks_data': networks_list}

    def get_anime_genres(self):
        return []


# --- CALL CLASSES -----------------------------------------------------------------------------------------------


class ApiSeries(ApiTV):
    _duration = 45
    group = [ListType.SERIES, MediaType.SERIES]
    local_covers_path = Path(app.root_path, "static/covers/series_covers/")

    def get_trending(self):
        response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                .format(self.api_key), timeout=10)

        status_code(response.status_code)

        return json.loads(response.text)

    def add_data_to_db(self):
        self.media = Series(**self.all_data['media_data'])
        db.session.add(self.media)
        db.session.commit()

        for genre in [{**item, 'media_id': self.media.id} for item in self.all_data['genres_data']]:
            db.session.add(SeriesGenre(**genre))

        for actor in [{**item, 'media_id': self.media.id} for item in self.all_data['actors_data']]:
            db.session.add(SeriesActors(**actor))

        for network in [{**item, 'media_id': self.media.id} for item in self.all_data['networks_data']]:
            db.session.add(SeriesNetwork(**network))

        for season in [{**item, 'media_id': self.media.id} for item in self.all_data['seasons_data']]:
            db.session.add(SeriesEpisodesPerSeason(**season))


class ApiAnime(ApiTV):
    _duration = 24
    group = [ListType.ANIME, MediaType.ANIME]
    local_covers_path = Path(app.root_path, "static/covers/anime_covers/")

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

    def get_trending(self):
        response = requests.get("https://api.jikan.moe/v3/top/anime/1/airing", timeout=10)
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

    def add_data_to_db(self):
        self.media = Anime(**self.all_data['media_data'])
        db.session.add(self.media)
        db.session.commit()

        if len(self.all_data['anime_genres_data']) > 0:
            for genre in [{**item, 'media_id': self.media.id} for item in self.all_data['anime_genres_data']]:
                db.session.add(AnimeGenre(**genre))
        else:
            for genre in [{**item, 'media_id': self.media.id} for item in self.all_data['genres_data']]:
                db.session.add(AnimeGenre(**genre))

        for actor in [{**item, 'media_id': self.media.id} for item in self.all_data['actors_data']]:
            db.session.add(AnimeActors(**actor))

        for network in [{**item, 'media_id': self.media.id} for item in self.all_data['networks_data']]:
            db.session.add(AnimeNetwork(**network))

        for season in [{**item, 'media_id': self.media.id} for item in self.all_data['seasons_data']]:
            db.session.add(AnimeEpisodesPerSeason(**season))


class ApiMovies(TMDBMixin):
    group = [ListType.MOVIES, MediaType.MOVIES]
    local_covers_path = Path(app.root_path, "static/covers/movies_covers")

    def get_details_and_credits_data(self):
        response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}&append_to_response=credits"
                                .format(self.API_id, self.api_key), timeout=15)

        status_code(response.status_code)
        self.API_data = json.loads(response.text)

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

    def from_API_to_dict(self, updating=False):
        self.media_details = {'name': self.API_data.get('title', 'Unknown') or 'Unknown',
                              'original_name': self.API_data.get('original_title', 'Unknown') or 'Unknown',
                              'release_date': self.API_data.get('release_date', 'Unknown') or 'Unknown',
                              'homepage': self.API_data.get('homepage', 'Unknown') or 'Unknown',
                              'released': self.API_data.get('status', 'Unknown') or '"Unknown',
                              'vote_average': self.API_data.get('vote_average', 0) or 0,
                              'vote_count': self.API_data.get('vote_count', 0) or 0,
                              'synopsis': self.API_data.get('overview', 'Not defined.') or 'Not defined.',
                              'popularity': self.API_data.get('popularity', 0) or 0,
                              'budget': self.API_data.get('budget', 0) or 0,
                              'revenue': self.API_data.get('revenue', 0) or 0,
                              'tagline': self.API_data.get('tagline', '-') or '-',
                              'duration': self.API_data.get('runtime', 0) or 0,
                              'original_language': self.API_data.get('original_language', 'Unknown') or 'Unknown',
                              'api_id': self.API_data.get('id'),
                              'director_name': 'Unknown',
                              'image_cover': self.get_media_cover()}

        the_crew = self.API_data.get('credits', {'crew': None}).get('crew') or None
        if the_crew:
            for element in the_crew:
                if element['job'] == 'Director':
                    self.media_details['director_name'] = element['name']
                    break

        genres_list, actors_list = [], []
        if not updating:
            genres_list = self.get_genres()
            actors_list = self.get_actors()

        self.all_data = {'media_data': self.media_details, 'genres_data': genres_list, 'actors_data': actors_list}

    def add_data_to_db(self):
        self.media = Movies(**self.all_data['media_data'])
        db.session.add(self.media)
        db.session.commit()

        for genre in [{**item, 'media_id': self.media.id} for item in self.all_data['genres_data']]:
            db.session.add(MoviesGenre(**genre))

        for actor in [{**item, 'media_id': self.media.id} for item in self.all_data['actors_data']]:
            db.session.add(MoviesActors(**actor))


class ApiGames(ApiData):
    group = [ListType.GAMES, MediaType.GAMES]
    local_covers_path = Path(app.root_path, "static/covers/games_covers/")

    def __init__(self, API_id=None):
        super().__init__(API_id)
        self.api_key = app.config['IGDB_API_KEY']
        self.client_igdb = app.config['CLIENT_IGDB']
        self.poster_base_url = 'https://images.igdb.com/igdb/image/upload/t_1080p/'
        self.API_id = API_id

    @staticmethod
    def HLTB_time(game_name):
        games_list = HowLongToBeat().search(game_name)
        if games_list and len(games_list) > 0:
            game = max(games_list, key=lambda x: x.similarity)
            return {'main': game.gameplay_main, 'extra': game.gameplay_main_extra,
                    'completionist': game.gameplay_completionist}
        else:
            return {'main': None, 'extra': None, 'completionist': None}

    @sleep_and_retry
    @limits(calls=4, period=1)
    def search(self, game_name):
        print(app.config['CLIENT_IGDB'])
        print(self.api_key)
        headers = {'Client-ID': f"{app.config['CLIENT_IGDB']}",
                   'Authorization': 'Bearer ' + self.api_key}
        body = 'fields id, name, cover.image_id, first_release_date, storyline; search "{}";'.format(game_name)
        response = requests.post('https://api.igdb.com/v4/games', data=body, headers=headers, timeout=15)

        status_code(response.status_code)

        return json.loads(response.text)

    def get_details_and_credits_data(self):
        headers = {'Client-ID': f"{self.client_igdb}",
                   'Authorization': 'Bearer ' + self.api_key}
        body = 'fields name, cover.image_id, collection.name, game_engines.name, game_modes.name, ' \
               'platforms.name, genres.name, player_perspectives.name, total_rating, total_rating_count, ' \
               'first_release_date, involved_companies.company.name, involved_companies.developer, ' \
               'involved_companies.publisher, storyline, summary, themes.name, url, external_games.uid, ' \
               'external_games.category; where id={};' \
            .format(self.API_id)
        response = requests.post('https://api.igdb.com/v4/games', data=body, headers=headers, timeout=15)

        status_code(response.status_code)
        self.API_data = json.loads(response.text)

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

    def from_API_to_dict(self):
        self.API_data = self.API_data[0]
        self.media_details = {'name': self.API_data.get('name', 'Unknown') or 'Unknown',
                              'release_date': self.API_data.get('first_release_date', 'Unknown') or 'Unknown',
                              'IGDB_url': self.API_data.get('url', 'Unknown') or 'Unknown',
                              'vote_average': self.API_data.get('total_rating', 0) or 0,
                              'vote_count': self.API_data.get('total_rating_count', 0) or 0,
                              'summary': self.API_data.get('summary', 'No summary found.') or 'No summary found.',
                              'storyline': self.API_data.get('storyline', 'No storyline found.') or 'No storyline found.',
                              'collection_name': self.API_data.get('collection', {'name': 'Unknown'})['name'] or 'Unknown',
                              'game_engine': self.API_data.get('game_engines', [{'name': 'Unknown'}])[0]['name'] or 'Unknown',
                              'player_perspective': self.API_data.get('player_perspectives', [{'name': 'Unknown'}])[0]['name'] or 'Unknown',
                              'game_modes': ','.join([x['name'] for x in self.API_data.get('game_modes', [{'name': 'Unknown'}])]),
                              'igdb_id': self.API_data.get('id'),
                              'image_cover': self.get_media_cover()}

        hltb_time = self.HLTB_time(self.media_details['name'])

        self.media_details['hltb_main_time'] = hltb_time['main']
        self.media_details['hltb_main_and_extra_time'] = hltb_time['extra']
        self.media_details['hltb_total_complete_time'] = hltb_time['completionist']

        platforms, platforms_list = self.API_data.get('platforms') or None, []
        if platforms:
            for platform in platforms:
                platforms_list.append({'name': platform["name"]})
        else:
            platforms_list.append({'name': 'Unknown'})

        companies, companies_list = self.API_data.get('involved_companies') or None, []
        if companies:
            for company in companies:
                companies_list.append({'name': company["company"]["name"], 'publisher': company["publisher"],
                                       'developer': company["developer"]})
        else:
            companies_list.append({'name': 'Unknown', 'publisher': False, 'developer': False})

        genres, genres_list = self.API_data.get('genres') or None, []
        if genres:
            for i in range(0, len(genres)):
                genres_list.append({'genre': genres[i]['name']})

        themes, themes_list = self.API_data.get('themes') or None, []
        if themes:
            for i in range(0, len(themes)):
                themes_list.append({'genre': themes[i]['name']})

        fusion_list = genres_list + themes_list
        if len(fusion_list) == 0:
            fusion_list.append({'genre': 'Unknown', 'genre_id': 0})

        self.all_data = {'media_data': self.media_details, 'companies_data': companies_list, 'genres_data': fusion_list,
                         'platforms_data': platforms_list, 'hltb_time': hltb_time}

    def add_data_to_db(self):
        self.media = Games(**self.all_data['media_data'])
        db.session.add(self.media)
        db.session.commit()

        for genre in self.all_data['genres_data']:
            if genre['genre'] == '4X (explore, expand, exploit, and exterminate)':
                genre['genre'] = '4X'
            elif genre['genre'] == "Hack and slash/Beat 'em up":
                genre['genre'] = 'Hack and Slash'
            elif genre['genre'] == "Card & Board Game":
                genre['genre'] = 'Card Game'
            elif genre['genre'] == "Quiz/Trivia":
                genre['genre'] = 'Quiz'
            genre.update({'media_id': self.media.id})
            db.session.add(GamesGenre(**genre))

        for company in [{**item, 'media_id': self.media.id} for item in self.all_data['companies_data']]:
            db.session.add(GamesCompanies(**company))

        for platform in [{**item, 'media_id': self.media.id} for item in self.all_data['platforms_data']]:
            db.session.add(GamesPlatforms(**platform))
