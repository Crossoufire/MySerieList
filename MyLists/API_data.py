import json
import requests
import urllib.request

from PIL import Image
from flask import abort
from MyLists import app
from pathlib import Path
from jikanpy import Jikan
from MyLists.models import ListType


class ApiData:
    def __init__(self, ):
        self.tmdb_api_key = app.config['THEMOVIEDB_API_KEY']
        self.tmdb_poster_base_url = 'https://image.tmdb.org/t/p/w300'

    def TMDb_search(self, element_name):
        response = requests.get("https://api.themoviedb.org/3/search/multi?api_key={0}&query={1}"
                                .format(self.tmdb_api_key, element_name))

        self.status_code(response.status_code)

        return json.loads(response.text)

    def get_details_and_credits_data(self, api_id, list_type):
        if list_type != ListType.MOVIES:
            response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}&append_to_response=credits"
                                    .format(api_id, self.tmdb_api_key))
        elif list_type == ListType.MOVIES:
            response = requests.get("https://api.themoviedb.org/3/movie/{0}?api_key={1}&append_to_response=credits"
                                    .format(api_id, self.tmdb_api_key))

        self.status_code(response.status_code)

        return json.loads(response.text)

    def get_changed_data(self, list_type):
        if list_type == ListType.SERIES:
            response = requests.get("https://api.themoviedb.org/3/tv/changes?api_key={0}"
                                    .format(self.tmdb_api_key))
        elif list_type == ListType.MOVIES:
            response = requests.get("https://api.themoviedb.org/3/movie/changes?api_key={0}"
                                    .format(self.tmdb_api_key))

        self.status_code(response.status_code)

        return json.loads(response.text)

    def get_trending_media(self, list_type, api_name):
        if api_name == 'TMDB':
            if list_type != ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/trending/tv/week?api_key={}"
                                        .format(self.tmdb_api_key))
            elif list_type == ListType.MOVIES:
                response = requests.get("https://api.themoviedb.org/3/trending/movie/week?api_key={}"
                                        .format(self.tmdb_api_key))
        elif api_name == 'Jikan':
            response = Jikan().top(type='anime', page=1, subtype='airing')

        self.status_code(response.status_code)

        return json.loads(response.text)

    def get_collection_data(self, collection_id):
        response = requests.get("https://api.themoviedb.org/3/collection/{0}?api_key={1}"
                                .format(collection_id, self.tmdb_api_key))

        self.status_code(response.status_code)

        return json.loads(response.text)

    def anime_search(self, anime_name):
        """ Get the name of the anime from TMDB to MyAnimeList to obtain better genres with <anime_genres> function"""

        response = requests.get("https://api.jikan.moe/v3/search/anime?q={0}".format(anime_name))

        self.status_code(response.status_code)

        return json.loads(response.text)

    def get_anime_genres(self, mal_id):
        """
            "genres": [{"mal_id":1,"type":"anime","name":"Action","url":""},
            {"mal_id":37,"type":"anime","name":"Supernatural","url":""},
            {"mal_id":16,"type":"anime","name":"Magic","url":""},
            {"mal_id":10,"type":"anime","name":"Fantasy","url":""}]
        """

        response = requests.get("https://api.jikan.moe/v3/anime/{}".format(mal_id))

        self.status_code(response.status_code)

        return json.loads(response.text)

    def save_api_cover(self, media_cover_path, media_cover_name, list_type, collection=False):
        if list_type == ListType.SERIES:
            local_covers_path = Path(app.root_path, "static/covers/series_covers/")
        elif list_type == ListType.ANIME:
            local_covers_path = Path(app.root_path, "static/covers/anime_covers/")
        elif list_type == ListType.MOVIES:
            if collection:
                local_covers_path = Path(app.root_path, "static/covers/movies_collection_covers")
            else:
                local_covers_path = Path(app.root_path, "static/covers/movies_covers")

        urllib.request.urlretrieve(f"{self.tmdb_poster_base_url}{media_cover_path}",
                                   f"{local_covers_path}/{media_cover_name}")

        img = Image.open(f"{local_covers_path}/{media_cover_name}")
        img = img.resize((300, 450), Image.ANTIALIAS)
        img.save(f"{local_covers_path}/{media_cover_name}", quality=90)

    @staticmethod
    def status_code(status_code):
        if status_code != 200:
            abort(status_code)
