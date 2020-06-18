import json
import requests
import urllib.request

from PIL import Image
from MyLists import app
from pathlib import Path
from flask import url_for, abort
from jikanpy import Jikan
from MyLists.models import ListType


class ApiData:
    def __init__(self, ):
        self.tmdb_api_key = app.config['THEMOVIEDB_API_KEY']
        self.tmdb_poster_base_url = 'https://image.tmdb.org/t/p/w300'

    def autocomplete_search(self, element_name):
        response = requests.get("https://api.themoviedb.org/3/search/multi?api_key={0}&query={1}"
                                .format(self.tmdb_api_key, element_name))

        if response.status_code != 200:
            abort(response.status_code)

        # Get the response in a json form
        data = json.loads(response.text)

        if data.get("total_results", 0) == 0:
            return [{'nb_results': 0}]

        # Recover 7 results without peoples
        tmdb_results = []
        for i, result in enumerate(data["results"]):
            if i >= data["total_results"] or i > 19 or len(tmdb_results) >= 7:
                break

            if result.get('known_for_department'):
                continue

            media_data = {'name': result.get('original_title') or result.get('original_name'),
                          "first_air_date": result.get('first_air_date') or result.get('release_date'),
                          'tmdb_id': result["id"]}

            if media_data['first_air_date'] == '':
                media_data['first_air_date'] = 'Unknown'

            if result['media_type'] == 'tv':
                if result['origin_country'] == 'JP' or result['original_language'] == 'ja' \
                        and 16 in result['genre_ids']:
                    media_data['media_type'] = ListType.ANIME.value
                    media_data['name'] = result['name']
                else:
                    media_data['media_type'] = ListType.SERIES.value
            elif result['media_type'] == 'movie':
                media_data['media_type'] = ListType.MOVIES.value
                if result['original_language'] == 'ja' and 16 in result['genre_ids']:
                    media_data['name'] = result['title']

            if result["poster_path"]:
                media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300", result["poster_path"])
            else:
                media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")
            tmdb_results.append(media_data)

        return tmdb_results

    def media_search(self, element_name):
        response_tv = requests.get("https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}"
                                   .format(self.tmdb_api_key, element_name))
        response_movies = requests.get("https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}"
                                       .format(self.tmdb_api_key, element_name))

        data_tv = self.check_response_status(response_tv)
        data_movies = self.check_response_status(response_movies)
        if not data_tv and not data_movies:
            return None

        if data_tv.get("total_results", 0) == 0 and data_movies.get("total_results", 0) == 0:
            return None

        # Recover movies results
        movies_results = []
        for result in data_movies['results']:
            media_data = {'name': result['original_title'],
                          'overview': result['overview'],
                          'tmdb_id': result["id"],
                          "first_air_date": result.get('release_date', 'Unknown') or 'Unknown',
                          'url': f"https://www.themoviedb.org/movie/{result['id']}"}

            if result["poster_path"]:
                media_data["poster_path"] = f"{self.tmdb_poster_base_url}{result['poster_path']}"
            else:
                media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")
            movies_results.append(media_data)

        # Recover anime and series results
        series_results, anime_results = [], []
        for result in data_tv['results']:
            media_data = {'name': result['original_name'],
                          'overview': result['overview'],
                          'tmdb_id': result["id"],
                          "first_air_date": result.get('first_air_date', 'Unknown') or 'Unknown',
                          'url': f"https://www.themoviedb.org/tv/{result['id']}"}

            if result["poster_path"]:
                media_data["poster_path"] = f"{self.tmdb_poster_base_url}{result['poster_path']}"
            else:
                media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")

            if result['origin_country'] == 'JP' or result['original_language'] == 'ja' and 16 in result['genre_ids']:
                anime_results.append(media_data)
            else:
                series_results.append(media_data)

        return [series_results, anime_results, movies_results]

    def get_details_and_credits_data(self, api_id, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}&append_to_response=credits"
                                        .format(api_id, self.tmdb_api_key))
            elif list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/{0}?api_key={1}&append_to_response=credits"
                                        .format(api_id, self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the TMDB API: {}'.format(e))
            return None

        data = self.check_response_status(response)
        if not data:
            return None

        return data

    def get_collection_data(self, collection_id):
        try:
            response = requests.get("https://api.themoviedb.org/3/collection/{0}?api_key={1}"
                                    .format(collection_id, self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the TMDB API for movies collection data: {}'.format(e))
            return None

        data = self.check_response_status(response)
        if not data:
            return None

        return data

    def save_api_cover(self, media_cover_path, media_cover_name, list_type, collection=False):
        if list_type == ListType.SERIES:
            local_covers_path = Path(app.root_path, "static/covers/series_covers/")
        elif list_type == ListType.ANIME:
            local_covers_path = Path(app.root_path, "static/covers/anime_covers/")
        elif list_type == ListType.MOVIES:
            if collection is True:
                local_covers_path = Path(app.root_path, "static/covers/movies_collection_covers")
            else:
                local_covers_path = Path(app.root_path, "static/covers/movies_covers")

        try:
            urllib.request.urlretrieve(f"{self.tmdb_poster_base_url}{media_cover_path}",
                                       f"{local_covers_path}/{media_cover_name}")
        except Exception as e:
            app.logger.error('[SYSTEM] Error trying to recover the poster: {}'.format(e))
            return False

        img = Image.open(f"{local_covers_path}/{media_cover_name}")
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save(f"{local_covers_path}/{media_cover_name}", quality=90)

        return True

    def get_trending_media(self):
        data = {'tmdb_error': None,
                'jikan_error': None}

        try:
            series_response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                           .format(self.tmdb_api_key))
            movies_response = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key={}"
                                           .format(self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            series_response = None
            movies_response = None
            data['tmdb_error'] = True

        try:
            anime_response = Jikan().top(type='anime', page=1, subtype='airing')
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the Jikan API: {}'.format(e))
            anime_response = None
            data['jikan_error'] = True

        series_data = self.check_response_status(series_response)
        if not series_data:
            data['tmdb_error'] = True

        anime_data = anime_response

        movies_data = self.check_response_status(movies_response)
        if not movies_data:
            data['tmdb_error'] = True

        data['series_data'] = series_data
        data['anime_data'] = anime_data
        data['movies_data'] = movies_data

        return data

    def get_changed_data(self, list_type):
        try:
            if list_type == ListType.SERIES:
                response = requests.get("https://api.themoviedb.org/3/tv/changes?api_key={0}"
                                        .format(self.tmdb_api_key))
            elif list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/changes?api_key={0}"
                                        .format(self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the TMDB API: {}'.format(e))
            return None

        changed_data = self.check_response_status(response)
        if not changed_data:
            return None

        return changed_data

    @staticmethod
    def get_anime_genres(anime_name):
        """
        "genres": [{"mal_id":1,"type":"anime","name":"Action","url":""},
        {"mal_id":37,"type":"anime","name":"Supernatural","url":""},
        {"mal_id":16,"type":"anime","name":"Magic","url":""},
        {"mal_id":10,"type":"anime","name":"Fantasy","url":""}]
        """
        try:
            response = requests.get("https://api.jikan.moe/v3/search/anime?q={0}".format(anime_name))
            data_mal = json.loads(response.text)
            mal_id = data_mal["results"][0]["mal_id"]

            response = requests.get("https://api.jikan.moe/v3/anime/{}".format(mal_id))
            data_mal = json.loads(response.text)

            return data_mal["genres"]
        except:
            return None
