from flask import url_for
from datetime import datetime


class TrendingData:
    def __init__(self, trending_data):
        self.movie_tmdb_link = "https://www.themoviedb.org/movie"
        self.tmdb_cover_path = "http://image.tmdb.org/t/p/w300"
        self.tv_tmdb_link = "https://www.themoviedb.org/tv"
        self.trending_data = trending_data
        self.media_data = None
        self.result = None

    @staticmethod
    def latin_alphabet(original_name):
        try:
            original_name.encode('iso-8859-1')
            return True
        except UnicodeEncodeError:
            return False

    @staticmethod
    def change_air_format(date):
        return datetime.strptime(date, '%Y-%m-%d').strftime("%d %b %Y")

    def _get_media_cover(self, anime=False):
        media_cover = url_for('static', filename="covers/series_covers/default.jpg")
        if not anime:
            poster_path = self.result.get('poster_path') or None
            if poster_path:
                media_cover = "{}{}".format(self.tmdb_cover_path, poster_path)
        else:
            poster_path = self.result.get('image_url') or None
            if poster_path:
                media_cover = "{}".format(poster_path)

        return media_cover

    def get_trending_series(self):
        series_results = []
        for i, self.result in enumerate(self.trending_data['results']):
            self.media_data = {'overview': self.result.get('overview', 'Unknown') or 'Unknown',
                               'release_date': self.result.get('first_air_date', 'Unknown') or 'Unknown',
                               'display_name': self.result.get('name', 'Unknown') or 'Unknown',
                               'tmdb_id': self.result.get('id')}

            if self.latin_alphabet(self.result.get('original_name')):
                self.media_data["display_name"] = self.result.get('original_name')

            # Change the <first_air_date> format
            if self.media_data['release_date'] != 'Unknown':
                self.media_data['release_date'] = self.change_air_format(self.result.get('first_air_date'))

            self.media_data['poster_path'] = self._get_media_cover()
            self.media_data['tmdb_link'] = "{}/{}".format(self.tv_tmdb_link, self.result.get('id'))
            self.media_data['media_type'] = 'serieslist'

            series_results.append(self.media_data)

            if i == 11:
                break
        return series_results

    def get_trending_anime(self):
        anime_results = []
        for i, self.result in enumerate(self.trending_data['top']):
            self.media_data = {'display_name': self.result.get('title', 'Unknown') or 'Unknown',
                               'release_date': self.result.get('start_date', 'Unknown') or 'Unknown',
                               'poster_path': self._get_media_cover(anime=True), 'tmdb_link': self.result.get("url"),
                               "overview": "There is no synopsis from this API. You can check it on "
                                           "<b><i>MyAnimeList</i></b> by clicking on the title."}

            anime_results.append(self.media_data)

            if i == 11:
                break
        return anime_results

    def get_trending_movies(self):
        movies_results = []
        for i, self.result in enumerate(self.trending_data['results']):
            self.media_data = {'overview': self.result.get('overview', 'Unknown') or 'Unknown',
                               'display_name': self.result.get('title', 'Unknown') or 'Unknown',
                               'release_date': self.result.get('release_date', 'Unknown') or 'Unknown',
                               'tmdb_id': self.result.get('id')}

            if self.latin_alphabet(self.result.get('original_title')):
                self.media_data["display_name"] = self.result.get('original_title')

            # Change the <release_date> format
            if self.media_data["release_date"] != 'Unknown':
                self.media_data['release_date'] = self.change_air_format(self.result.get('release_date'))

            self.media_data['poster_path'] = self._get_media_cover()
            self.media_data['tmdb_link'] = "{}/{}".format(self.movie_tmdb_link, self.result.get('id'))
            self.media_data['media_type'] = 'movieslist'

            movies_results.append(self.media_data)

            if i == 11:
                break
        return movies_results
