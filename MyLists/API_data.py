import os
import json
import urllib
import platform
import requests

from PIL import Image
from MyLists import app
from flask import url_for
from jikanpy import Jikan
from MyLists.models import ListType


class API_data():
    def __init__(self, API_key=None):
        self.tmdb_api_key = API_key

    def autocomplete_search(self, element_name, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}"
                                        .format(self.tmdb_api_key, element_name))
            if list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/search/movie?api_key={0}&query={1}"
                                        .format(self.tmdb_api_key, element_name))
        except:
            return [{"nb_results": 0}]

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: invalid API key')
            return [{"nb_results": 0}]

        if response.status_code == 34:
            return [{"nb_results": 0}]

        data = json.loads(response.text)

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

                tmdb_results.append(movies_data)
                i += 1

        return tmdb_results

    def get_details_data(self, api_id, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}"
                                        .format(api_id, self.tmdb_api_key))
            if list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/{0}?api_key={1}"
                                        .format(api_id, self.tmdb_api_key))
        except:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: Could not reach the endpoint')
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: invalid API key')
            return None

        if response.status_code == 34:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: The ressource could not be found')
            return None

        details_data = json.loads(response.text)

        return details_data

    def get_actors_data(self, api_id, list_type):
        try:
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/tv/{0}/credits?api_key={1}"
                                        .format(api_id, self.tmdb_api_key))
            if list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/movie/{0}/credits?api_key={1}"
                                        .format(api_id, self.tmdb_api_key))
        except:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: Could not reach the endpoint')
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: invalid API key')
            return None

        if response.status_code == 34:
            details_data = {}
        else:
            actors_data = json.loads(response.text)

        return actors_data

    def get_collection_data(self, collection_id):
        try:
            response = requests.get("https://api.themoviedb.org/3/collection/{0}?api_key={1}"
                                    .format(collection_id, self.tmdb_api_key))
        except:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: Could not reach the endpoint')
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API: invalid API key')
            return None

        if response.status_code == 34:
            collection_data = {}
        else:
            collection_data = json.loads(response.text)

        return collection_data

    def save_api_cover(self, media_cover_path, media_cover_name, list_type, collection=False):
        if list_type == ListType.SERIES:
            if platform.system() == "Windows":
                local_covers_path = os.path.join(app.root_path, "static\\covers\\series_covers\\")
            else:  # Linux & macOS
                local_covers_path = os.path.join(app.root_path, "static/covers/series_covers/")
        elif list_type == ListType.ANIME:
            if platform.system() == "Windows":
                local_covers_path = os.path.join(app.root_path, "static\\covers\\anime_covers\\")
            else:  # Linux & macOS
                local_covers_path = os.path.join(app.root_path, "static/covers/anime_covers/")
        elif list_type == ListType.MOVIES:
            if collection is True:
                if platform.system() == "Windows":
                    local_covers_path = os.path.join(app.root_path, "static\\covers\\movies_collection_covers\\")
                else:  # Linux & macOS
                    local_covers_path = os.path.join(app.root_path, "static/covers/movies_collection_covers/")
            else:
                if platform.system() == "Windows":
                    local_covers_path = os.path.join(app.root_path, "static\\covers\\movies_covers\\")
                else:  # Linux & macOS
                    local_covers_path = os.path.join(app.root_path, "static/covers/movies_covers/")

        try:
            urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{}".format(media_cover_path),
                                       "{}{}".format(local_covers_path, media_cover_name))
        except:
            return False

        img = Image.open("{}{}".format(local_covers_path, media_cover_name))
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save("{0}{1}".format(local_covers_path, media_cover_name), quality=90)

        return True

    def get_trending_media(self):
        # Trending movies
        try:
            series_response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                           .format(self.tmdb_api_key))
            anime_response = Jikan().top(type='anime', page=1, subtype='airing')
            movies_response = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key={}"
                                           .format(self.tmdb_api_key))
        except:
            return None

        series_data = json.loads(series_response.text)
        anime_data = anime_response
        movies_data = json.loads(movies_response.text)

        return [series_data, anime_data, movies_data]
