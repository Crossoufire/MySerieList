import os
import json
import platform
import requests
import urllib.request

from PIL import Image
from pathlib import Path
from flask import url_for
from jikanpy import Jikan
from MyLists import current_app
from MyLists.models import ListType


class ApiData:
    def __init__(self, ):
        self.tmdb_api_key = current_app.config['THEMOVIEDB_API_KEY']
        self.tmdb_poster_base_url = 'https://image.tmdb.org/t/p/w300'

    def autocomplete_search(self, element_name, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}"
                                        .format(self.tmdb_api_key, element_name))
            if list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}"
                                        .format(self.tmdb_api_key, element_name))
        except Exception as e:
            current_app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            return [{"nb_results": 0}]

        data = self.check_response_status(response)
        if data is False:
            return [{"nb_results": 0}]

        if data.get("total_results", 0) == 0:
            return [{"nb_results": 0}]

        if list_type != ListType.MOVIES:
            # Only the first 6 results. There are 20 results per page.
            tmdb_results, i = [], 0
            while i < data["total_results"] and i < 20 and len(tmdb_results) < 6:
                # genre_ids: list
                if "genre_ids" in data["results"][i]:
                    genre_ids = data["results"][i]["genre_ids"]
                else:
                    genre_ids = ["Unknown"]

                # origin_country: list
                if "origin_country" in data["results"][i]:
                    origin_country = data["results"][i]["origin_country"]
                else:
                    origin_country = ["Unknown"]

                # original_language: string
                if "original_language" in data["results"][i]:
                    original_language = data["results"][i]["original_language"]
                else:
                    original_language = "Unknown"

                if list_type == ListType.ANIME:
                    if (16 in genre_ids and "JP" in origin_country) or (16 in genre_ids and original_language == "ja"):
                        pass
                    else:
                        i += 1
                        continue
                elif list_type == ListType.SERIES:
                    if (16 in genre_ids and "JP" in origin_country) or (16 in genre_ids and original_language == "ja"):
                        i += 1
                        continue
                    else:
                        pass

                media_data = {"tmdb_id": data["results"][i]["id"],
                              "name": data["results"][i]["name"]}

                if data["results"][i]["poster_path"]:
                    media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300",
                                                              data["results"][i]["poster_path"])
                else:
                    media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")

                first_air_date = data["results"][i].get("first_air_date")
                if first_air_date:
                    if data["results"][i]["first_air_date"].split('-') != ['']:
                        media_data["first_air_date"] = data["results"][i]["first_air_date"].split('-')[0]
                    else:
                        media_data["first_air_date"] = "Unknown"
                else:
                    media_data["first_air_date"] = "Unknown"

                tmdb_results.append(media_data)
                i += 1
        elif list_type == ListType.MOVIES:
            # Take only the first 6 results. There are 20 results per page.
            tmdb_results, i = [], 0
            while i < data["total_results"] and i < 20 and len(tmdb_results) < 6:
                movies_data = {"tmdb_id": data["results"][i]["id"],
                               "name": data["results"][i]["title"]}

                if data["results"][i]["poster_path"]:
                    movies_data["poster_path"] = "{0}{1}".format("http://image.tmdb.org/t/p/w300",
                                                                 data["results"][i]["poster_path"])
                else:
                    movies_data["poster_path"] = url_for('static', filename="covers/movies_covers/default.jpg")

                release_date = data["results"][i].get("release_date")

                if release_date:
                    if data["results"][i]["release_date"] != ['']:
                        movies_data["first_air_date"] = data["results"][i]["release_date"].split('-')[0]
                    else:
                        movies_data["first_air_date"] = "Unknown"
                else:
                    movies_data["first_air_date"] = "Unknown"

                tmdb_results.append(movies_data)
                i += 1

        return tmdb_results

    def get_details_and_credits_data(self, api_id, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}&append_to_response=credits"
                                        .format(api_id, self.tmdb_api_key))
            if list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/{0}?api_key={1}&append_to_response=credits"
                                        .format(api_id, self.tmdb_api_key))
        except Exception as e:
            current_app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
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
            current_app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            return None

        data = self.check_response_status(response)
        if data is False:
            return None

        return data

    def save_api_cover(self, media_cover_path, media_cover_name, list_type, collection=False):
        if list_type == ListType.SERIES:
            local_covers_path = Path(current_app.root_path, "static/covers/series_covers/")
        elif list_type == ListType.ANIME:
            local_covers_path = Path(current_app.root_path, "static/covers/anime_covers/")
        elif list_type == ListType.MOVIES:
            if collection is True:
                local_covers_path = Path(current_app.root_path, "static/covers/movies_collection_covers/")
            else:
                local_covers_path = Path(current_app.root_path, "static/covers/movies_covers/")

        try:
            urllib.request.urlretrieve("{0}{1}".format(self.tmdb_poster_base_url, media_cover_path),
                                       "{0}{1}".format(local_covers_path, media_cover_name))
        except Exception as e:
            current_app.logger.error('[SYSTEM] Error trying to recover the poster: {}'.format(e))
            return False

        img = Image.open("{}{}".format(local_covers_path, media_cover_name))
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save("{0}{1}".format(local_covers_path, media_cover_name), quality=90)

        return True

    def get_trending_media(self):
        try:
            series_response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                           .format(self.tmdb_api_key))
            anime_response = Jikan().top(type='anime', page=1, subtype='airing')
            movies_response = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key={}"
                                           .format(self.tmdb_api_key))
        except Exception as e:
            current_app.logger.error('[SYSTEM] Error requesting themoviedb API or the Jikan API: {}'.format(e))
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
            current_app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
            return None

        changed_data = self.check_response_status(response)
        if not changed_data:
            return None

        return changed_data

    @staticmethod
    def get_anime_genres(anime_name):
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
            current_app.logger.error('[SYSTEM] Error requesting themoviedb API: invalid API key')
        elif response.status_code == 404:
            current_app.logger.error('[SYSTEM] Invalid id: The pre-requisite id is invalid or not found.')
        elif response.status_code == 500:
            current_app.logger.error('[SYSTEM] 	Internal error: Something went wrong, contact TMDb.')
        elif response.status_code == 503:
            current_app.logger.error('[SYSTEM] Service offline: This service is temporarily offline, try again later.')
        elif response.status_code == 504:
            current_app.logger.error('[SYSTEM] Your request to the backend server timed out. Try again.')

        return False
