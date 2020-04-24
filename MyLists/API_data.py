import json
import requests
import pykakasi
import urllib.request

from PIL import Image
from MyLists import app
from pathlib import Path
from flask import url_for
from jikanpy import Jikan
from MyLists.models import ListType


class ApiData:
    def __init__(self, ):
        self.tmdb_api_key = app.config['THEMOVIEDB_API_KEY']
        self.tmdb_poster_base_url = 'https://image.tmdb.org/t/p/w300'

    def autocomplete_search(self, element_name):
        try:
            response = requests.get("https://api.themoviedb.org/3/search/multi?api_key={0}&query={1}"
                                    .format(self.tmdb_api_key, element_name))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            return [{"nb_results": 0}]

        data = self.check_response_status(response)
        if data is False:
            return [{"nb_results": 0}]

        if data.get("total_results", 0) == 0:
            return [{"nb_results": 0}]

        # Recover 7 results without peoples
        tmdb_results, i = [], 0
        while i < data["total_results"] and i < 20 and len(tmdb_results) < 7:
            result = data["results"][i]

            if result.get('known_for_department'):
                i += 1
                continue

            media_data = {'name': result.get('original_title') or result.get('original_name'),
                          "first_air_date": result.get('first_air_date') or result.get('release_date'),
                          'tmdb_id': result["id"]}

            if media_data['first_air_date'] == '':
                media_data['first_air_date'] = 'Unknown'

            if result['media_type'] == 'tv':
                if result['origin_country'] == 'JP' or result['original_language'] == 'ja' and 16 \
                        in result['genre_ids']:
                    media_data['media_type'] = 'animelist'
                    media_data['name'] = result['name']
                else:
                    media_data['media_type'] = 'serieslist'
            elif result['media_type'] == 'movie':
                media_data['media_type'] = 'movieslist'
                if result['original_language'] == 'ja' and 16 in result['genre_ids']:
                    media_data['name'] = result['title']

            if result["poster_path"]:
                media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300", result["poster_path"])
            else:
                media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")
            tmdb_results.append(media_data)

            i += 1

        return tmdb_results

    def media_search(self, element_name):
        try:
            response_tv = requests.get("https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}"
                                       .format(self.tmdb_api_key, element_name))
            response_movies = requests.get("https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}"
                                           .format(self.tmdb_api_key, element_name))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            return None, None, None

        data_tv = self.check_response_status(response_tv)
        data_movies = self.check_response_status(response_movies)
        if data_tv is False and data_movies is False:
            return None, None, None

        if data_tv.get("total_results", 0) == 0 and data_movies.get("total_results", 0) == 0:
            return None, None, None

        # Recover movies results
        movies_results = []
        for result in data_movies['results']:
            media_data = {'name': result['original_title'],
                          'overview': result['overview'],
                          'tmdb_id': result["id"],
                          "first_air_date": result.get('release_date', 'Unknown') or 'Unknown',
                          'url': "https://www.themoviedb.org/movie/{}".format(result["id"])}

            if result["poster_path"]:
                media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300", result["poster_path"])
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
                          'url': "https://www.themoviedb.org/tv/{}".format(result["id"])}

            if result["poster_path"]:
                media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300", result["poster_path"])
            else:
                media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")

            if result['origin_country'] == 'JP' or result['original_language'] == 'ja' and 16 in result['genre_ids']:
                anime_results.append(media_data)
            else:
                series_results.append(media_data)

        return series_results, anime_results, movies_results

    def get_details_and_credits_data(self, api_id, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}&append_to_response=credits"
                                        .format(api_id, self.tmdb_api_key))
            elif list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/{0}?api_key={1}&append_to_response=credits"
                                        .format(api_id, self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            return None

        data = self.check_response_status(response)
        if data is False:
            return None

        return data

    def get_collection_data(self, collection_id):
        try:
            response = requests.get("https://api.themoviedb.org/3/collection/{0}?api_key={1}"
                                    .format(collection_id, self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            return None

        data = self.check_response_status(response)
        if data is False:
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
            urllib.request.urlretrieve("{0}{1}".format(self.tmdb_poster_base_url, media_cover_path),
                                       "{0}/{1}".format(local_covers_path, media_cover_name))
        except Exception as e:
            app.logger.error('[SYSTEM] Error trying to recover the poster: {}'.format(e))
            return False

        img = Image.open("{}/{}".format(local_covers_path, media_cover_name))
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save("{0}/{1}".format(local_covers_path, media_cover_name), quality=90)

        return True

    def get_trending_media(self):
        try:
            series_response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                           .format(self.tmdb_api_key))
            anime_response = Jikan().top(type='anime', page=1, subtype='airing')
            movies_response = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key={}"
                                           .format(self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting themoviedb API or the Jikan API: {}'.format(e))
            return None

        series_data = self.check_response_status(series_response)
        if not series_data:
            return None

        anime_data = anime_response

        movies_data = self.check_response_status(movies_response)
        if not movies_data:
            return None

        return [series_data, anime_data, movies_data]

    def get_changed_data(self, list_type):
        try:
            if list_type == ListType.SERIES:
                response = requests.get("https://api.themoviedb.org/3/tv/changes?api_key={0}"
                                        .format(self.tmdb_api_key))
            elif list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/changes?api_key={0}"
                                        .format(self.tmdb_api_key))
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
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

    @staticmethod
    def check_response_status(response):
        if response.status_code == 200:
            return json.loads(response.text)
        elif response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: invalid API key')
        elif response.status_code == 404:
            app.logger.error('[SYSTEM] Invalid id: The pre-requisite id is invalid or not found.')
        elif response.status_code == 500:
            app.logger.error('[SYSTEM] 	Internal error: Something went wrong, contact TMDb.')
        elif response.status_code == 503:
            app.logger.error('[SYSTEM] Service offline: This service is temporarily offline, try again later.')
        elif response.status_code == 504:
            app.logger.error('[SYSTEM] Your request to the backend server timed out. Try again.')

        return False
