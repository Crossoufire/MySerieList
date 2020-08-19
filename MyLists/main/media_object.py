from datetime import datetime
from MyLists.models import ListType


class MediaDict:
    def __init__(self, media_data, media_type):
        self.data = media_data
        self.media_type = media_type
        self.media_info = {}

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
                           "other_name": self.data.original_name}

        if self.latin_alphabet(self.data.original_name):
            self.media_info["display_name"] = self.data.original_name
            self.media_info["other_name"] = self.data.name

        if self.data.original_name == self.data.name:
            self.media_info["other_name"] = None

        if self.media_type != ListType.MOVIES:
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

        # Change <first_air_time> format
        if self.data.first_air_date != 'Unknown':
            self.media_info['first_air_date'] = self.change_air_format(self.data.first_air_date)

        # Change <last_air_time> format
        if self.data.last_air_date != 'Unknown':
            self.media_info['last_air_date'] = self.change_air_format(self.data.last_air_date)

        if self.media_type == ListType.SERIES:
            self.media_info["media_type"] = 'Series'
            self.media_info["cover"] = 'series_covers/{}'.format(self.data.image_cover),
            self.media_info["cover_path"] = 'series_covers'
        elif self.media_type == ListType.ANIME:
            self.media_info['name'] = self.data.original_name
            self.media_info['original_name'] = self.data.name
            self.media_info["media_type"] = 'Anime'
            self.media_info["cover"] = 'anime_covers/{}'.format(self.data.image_cover)
            self.media_info["cover_path"] = 'anime_covers'

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

        # Change <release_date> format
        if self.data.release_date != 'Unknown':
            self.media_info['release_date'] = self.change_air_format(self.data.release_date)
