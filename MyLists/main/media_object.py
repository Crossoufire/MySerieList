from datetime import datetime
from flask_login import current_user
from MyLists.models import ListType, Status


def latin_alphabet(original_name):
    try:
        original_name.encode('iso-8859-1')
        return True
    except UnicodeEncodeError:
        return False


def change_air_format(date):
    return datetime.strptime(date, '%Y-%m-%d').strftime("%d %b %Y")


class MediaDict:
    def __init__(self, media_data, list_type):
        self.data = media_data
        self.list_type = list_type
        self.media_info = {}

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
                           "other_name": self.data.original_name,
                           "in_user_list": False,
                           "score": "---",
                           "favorite": False,
                           "rewatched": 0,
                           "comment": None}

        if latin_alphabet(self.data.original_name):
            self.media_info["display_name"] = self.data.original_name
            self.media_info["other_name"] = self.data.name

        if self.data.original_name == self.data.name:
            self.media_info["other_name"] = None

        self.add_genres()
        self.add_follow_list()

        if self.list_type != ListType.MOVIES:
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
        self.media_info["status"] = Status.WATCHING.value
        self.media_info["last_episode_watched"] = 1
        self.media_info["current_season"] = 1

        # Change <first_air_time> format
        if self.data.first_air_date != 'Unknown':
            self.media_info['first_air_date'] = change_air_format(self.data.first_air_date)

        # Change <last_air_time> format
        if self.data.last_air_date != 'Unknown':
            self.media_info['last_air_date'] = change_air_format(self.data.last_air_date)

        if self.list_type == ListType.SERIES:
            self.media_info["media_type"] = 'Series'
            self.media_info["cover"] = 'series_covers/{}'.format(self.data.image_cover),
            self.media_info["cover_path"] = 'series_covers'
        elif self.list_type == ListType.ANIME:
            self.media_info['name'] = self.data.original_name
            self.media_info['original_name'] = self.data.name
            self.media_info["media_type"] = 'Anime'
            self.media_info["cover"] = 'anime_covers/{}'.format(self.data.image_cover)
            self.media_info["cover_path"] = 'anime_covers'

        in_user_list = self.add_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["last_episode_watched"] = in_user_list.last_episode_watched
            self.media_info["current_season"] = in_user_list.current_season
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["rewatched"] = in_user_list.rewatched
            self.media_info["comment"] = in_user_list.comment

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
        self.media_info["status"] = Status.COMPLETED.value

        # Change <release_date> format
        if self.data.release_date != 'Unknown':
            self.media_info['release_date'] = change_air_format(self.data.release_date)

        in_user_list = self.add_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["rewatched"] = in_user_list.rewatched
            self.media_info["comment"] = in_user_list.comment

    def add_genres(self):
        genres_list = [r.genre for r in self.data.genres]
        genre_str = ','.join([g for g in genres_list])
        if len(genres_list) > 2:
            genres_list = genres_list[:2]
            genre_str = ','.join([g for g in genres_list[:2]])

        self.media_info['same_genres'] = self.data.get_same_genres(genres_list, genre_str)

    def add_follow_list(self):
        self.media_info['in_follows_lists'] = self.data.in_follows_lists(current_user.id)

    def add_user_list(self):
        return self.data.in_user_list(current_user.id)


class MediaListDict:
    def __init__(self, media_data, cover_path, common_media, list_type):
        self.data = media_data
        self.cover_path = cover_path
        self.list_type = list_type
        self.common_media = common_media
        self.media_info = {}

    def create_medialist_dict(self):
        self.media_info = {"id": self.data[0].id,
                           "tmdb_id": self.data[0].themoviedb_id,
                           "cover": "{}{}".format(self.cover_path, self.data[0].image_cover),
                           "score": self.data[1].score,
                           "favorite": self.data[1].favorite,
                           "rewatched": self.data[1].rewatched,
                           "comment": self.data[1].comment,
                           "category": self.data[1].status.value,
                           "display_name": self.data[0].name,
                           "other_name": self.data[0].original_name,
                           "common": False,
                           "media": "Movies"}

        if not self.media_info['score'] or self.media_info['score'] == -1:
            self.media_info['score'] = '---'

        if latin_alphabet(self.data[0].original_name):
            self.media_info["display_name"] = self.data[0].original_name
            self.media_info["other_name"] = self.data[0].name

        if self.data[0].id in self.common_media:
            self.media_info['common'] = True

        if self.list_type != ListType.MOVIES:
            self.add_tv_dict()

        return self.media_info

    def add_tv_dict(self):
        self.media_info['media'] = 'Series'
        if self.list_type == ListType.ANIME:
            self.media_info['media'] = 'Anime'

        self.media_info["last_episode_watched"] = self.data[1].last_episode_watched
        self.media_info["eps_per_season"] = [eps.episodes for eps in self.data[0].eps_per_season]
        self.media_info["current_season"] = self.data[1].current_season
