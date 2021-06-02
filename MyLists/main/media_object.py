import secrets
import pykakasi
from MyLists import app
from flask import url_for
from datetime import datetime
from MyLists.API_data import ApiData
from MyLists.models import ListType, Status


def latin_alphabet(original_name):
    try:
        original_name.encode('iso-8859-1')
        return True
    except UnicodeEncodeError:
        try:
            kks = pykakasi.kakasi()
            kks.setMode("H", "a")
            kks.setMode("K", "a")
            kks.setMode("J", "a")
            kks.setMode("s", True)
            try:
                conv = kks.getConverter().do(original_name).split('.')
            except:
                conv = kks.getConverter().do(original_name).split()
            cap_parts = [p.capitalize() for p in conv]
            cap_message = " ".join(cap_parts)
            return cap_message
        except:
            return False


def change_air_format(date, media_sheet=False, games=False):
    if media_sheet and not games:
        try:
            return datetime.strptime(date, '%Y-%m-%d').strftime("%b %Y")
        except:
            return 'Unknown'
    elif not media_sheet and not games:
        try:
            return datetime.strptime(date, '%Y-%m-%d').strftime("%d %b %Y")
        except:
            return 'Unknown'
    elif games:
        try:
            return datetime.utcfromtimestamp(int(date)).strftime('%d %b %Y')
        except:
            return 'Unknown'


# Parsing the DB data to the <MediaSheet> route
class MediaDict:
    def __init__(self, media_data, list_type):
        self.data = media_data
        self.list_type = list_type
        self.media_info = {}

    def create_list_dict(self):
        if self.list_type != ListType.GAMES:
            self.media_dict()
        elif self.list_type == ListType.GAMES:
            self.games_dict()

        return self.media_info

    def games_dict(self):
        self.media_info = {"id": self.data.id,
                           "cover": 'games_covers/{}'.format(self.data.image_cover),
                           "display_name": self.data.name,
                           "IGDB_url": self.data.IGDB_url,
                           "vote_average": self.data.vote_average,
                           "vote_count": self.data.vote_count,
                           "synopsis": self.data.summary,
                           "lock_status": self.data.lock_status,
                           "collection_name": self.data.collection_name,
                           "game_engine": self.data.game_engine,
                           "game_modes": self.data.game_modes,
                           "player_perspective": self.data.player_perspective,
                           "storyline": self.data.storyline,
                           "genres": ', '.join([r.genre for r in self.data.genres]),
                           "platforms": ', '.join([r.name for r in self.data.platforms]),
                           "hltb_main": self.data.hltb_main_time,
                           "hltb_main_extra": self.data.hltb_main_and_extra_time,
                           "hltb_complete": self.data.hltb_total_complete_time,
                           "cover_path": 'games_covers',
                           "media_type": 'Games',
                           "publisher": [],
                           "developer": [],
                           "in_user_list": False,
                           "score": "---",
                           "favorite": False,
                           "status": Status.COMPLETED.value,
                           "comment": None,
                           "playtime": 0.,
                           "completion": False}

        for company in self.data.companies:
            if company.publisher is True:
                self.media_info['publisher'].append(company.name)
            if company.developer is True:
                self.media_info['developer'].append(company.name)

        self.media_info["release_date"] = change_air_format(self.data.release_date, games=True)

        self.add_genres()
        self.add_follow_list()

        in_user_list = self.data.in_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["comment"] = in_user_list.comment
            self.media_info["completion"] = in_user_list.completion
            self.media_info["playtime"] = int(in_user_list.playtime)

    def media_dict(self):
        self.media_info = {"id": self.data.id,
                           "homepage": self.data.homepage,
                           "vote_average": self.data.vote_average,
                           "vote_count": self.data.vote_count,
                           "synopsis": self.data.synopsis,
                           "popularity": self.data.popularity,
                           "lock_status": self.data.lock_status,
                           "actors": ', '.join([r.name for r in self.data.actors]),
                           "genres": ', '.join([r.genre for r in self.data.genres]),
                           "in_user_list": False,
                           "score": "---",
                           "favorite": False,
                           "rewatched": 0,
                           "comment": None}

        return_latin = latin_alphabet(self.data.original_name)
        if return_latin is True:
            self.media_info["display_name"] = self.data.original_name
            self.media_info["other_name"] = self.data.name
        elif return_latin is False:
            self.media_info["display_name"] = self.data.name
            self.media_info["other_name"] = self.data.original_name
        else:
            self.media_info["display_name"] = self.data.name
            self.media_info["other_name"] = return_latin

        if self.data.original_name == self.data.name:
            self.media_info["other_name"] = None

        self.add_genres()
        self.add_follow_list()

        if self.list_type != ListType.MOVIES:
            self.add_tv_dict()
        else:
            self.add_movies_dict()

    def add_tv_dict(self):
        self.media_info.update({"created_by": self.data.created_by,
                                "total_seasons": self.data.total_seasons,
                                "total_episodes": self.data.total_episodes,
                                "prod_status": self.data.status,
                                "duration": self.data.duration,
                                "in_production": self.data.in_production,
                                "origin_country": self.data.origin_country,
                                "eps_per_season": [r.episodes for r in self.data.eps_per_season],
                                "networks": ', '.join([r.network for r in self.data.networks]),
                                "first_air_date": change_air_format(self.data.first_air_date, media_sheet=True),
                                "last_air_date": change_air_format(self.data.last_air_date, media_sheet=True),
                                "time_to_complete": self.data.total_episodes * self.data.duration,
                                "status": Status.WATCHING.value,
                                "last_episode_watched": 1,
                                "current_season": 1})

        if self.list_type == ListType.SERIES:
            self.media_info.update({"media_type": "Series",
                                    "cover": f"series_covers/{self.data.image_cover}",
                                    "cover_path": "series_covers"})
        elif self.list_type == ListType.ANIME:
            self.media_info.update({"name": self.data.original_name,
                                    "original_name": self.data.name,
                                    "media_type": "Anime",
                                    "cover": f"anime_covers/{self.data.image_cover}",
                                    "cover_path": "anime_covers"})

        in_user_list = self.data.in_user_list()
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
        self.media_info["duration"] = self.data.duration
        self.media_info["budget"] = self.data.budget
        self.media_info["revenue"] = self.data.revenue
        self.media_info["tagline"] = self.data.tagline
        self.media_info["tmdb_id"] = self.data.api_id
        self.media_info['release_date'] = 'Unknown'
        self.media_info["status"] = Status.COMPLETED.value

        # Change <release_date> format
        self.media_info['release_date'] = change_air_format(self.data.release_date)

        in_user_list = self.data.in_user_list()
        if in_user_list:
            self.media_info["in_user_list"] = True
            self.media_info["score"] = in_user_list.score
            self.media_info["favorite"] = in_user_list.favorite
            self.media_info["status"] = in_user_list.status.value
            self.media_info["rewatched"] = in_user_list.rewatched
            self.media_info["comment"] = in_user_list.comment

    def add_genres(self):
        genres_list = [r.genre for r in self.data.genres]
        if len(genres_list) > 2:
            genres_list = genres_list[:2]

        self.media_info['same_genres'] = self.data.get_same_genres(genres_list)

    def add_follow_list(self):
        self.media_info['in_follows_lists'] = self.data.in_follows_lists()


# Parsing the DB data to the <MediaList> route
class MediaListObj:
    def __init__(self, media_data, common_media, list_type):
        if list_type == ListType.SERIES:
            cover_path = url_for('static', filename='covers/series_covers/')
            self.media = "Series"
        elif list_type == ListType.ANIME:
            cover_path = url_for('static', filename='covers/anime_covers/')
            self.media = "Anime"
        elif list_type == ListType.MOVIES:
            cover_path = url_for('static', filename='covers/movies_covers/')
            self.media = "Movies"
        elif list_type == ListType.GAMES:
            cover_path = url_for('static', filename='covers/games_covers/')
            self.media = "Games"

        if list_type != ListType.GAMES:
            self.tmdb_id = media_data[0].api_id
            self.rewatched = media_data[1].rewatched

        self.id = media_data[0].id
        self.cover = "{}{}".format(cover_path, media_data[0].image_cover)
        self.favorite = media_data[1].favorite
        self.comment = media_data[1].comment
        self.category = media_data[1].status.value

        self.score = media_data[1].score
        if not media_data[1].score or media_data[1].score == -1:
            self.score = '---'

        self.display_name = media_data[0].name
        if list_type != ListType.GAMES:
            return_latin = latin_alphabet(media_data[0].original_name)
            if return_latin is True:
                self.display_name = media_data[0].original_name
                self.other_name = media_data[0].name
            elif return_latin is False:
                self.display_name = media_data[0].name
                self.other_name = media_data[0].original_name
            else:
                self.display_name = media_data[0].name
                self.other_name = return_latin

        self.common = False
        if media_data[0].id in common_media:
            self.common = True

        if list_type != ListType.MOVIES and list_type != ListType.GAMES:
            self.last_episode_watched = media_data[1].last_episode_watched
            self.eps_per_season = [eps.episodes for eps in media_data[0].eps_per_season]
            self.current_season = media_data[1].current_season
        elif list_type == ListType.GAMES:
            self.playtime = media_data[1].playtime


# Parsing the <API_data> to dict to display the autocomplete
class Autocomplete:
    def __init__(self, result):
        self.tmdb_cover_link = "http://image.tmdb.org/t/p/w300"
        self.igdb_cover_link = "https://images.igdb.com/igdb/image/upload/t_1080p/"
        self.result = result
        self.info = {}

    def get_autocomplete_dict(self):
        self.info['tmdb_id'] = self.result.get('id')

        self.info['image_cover'] = url_for('static', filename="covers/series_covers/default.jpg")
        if self.result.get('poster_path'):
            self.info['image_cover'] = "{}{}".format(self.tmdb_cover_link, self.result.get('poster_path'))

        if self.result.get('media_type') == 'tv':
            self.get_tv_dict()
        elif self.result.get('media_type') == 'movie':
            self.get_movies_dict()

        return self.info

    def get_games_autocomplete_dict(self):
        self.info['igdb_id'] = self.result.get('id')
        self.info['display_name'] = self.result.get('name')
        self.info['category'] = 'Games'
        self.info['type'] = 'Game'

        self.info['image_cover'] = url_for('static', filename="covers/series_covers/default.jpg")
        if self.result.get('cover'):
            self.info['image_cover'] = "{}{}.jpg".format(self.igdb_cover_link, self.result['cover']['image_id'])

        self.info['date'] = change_air_format(self.result.get('first_release_date'), games=True)

        return self.info

    def get_user_dict(self):
        self.info = {'display_name': self.result.username,
                     'image_cover': '/static/profile_pics/' + self.result.image_file,
                     'date': datetime.strftime(self.result.registered_on, '%d %b %Y'),
                     'category': 'Users',
                     'type': 'User'}

        return self.info

    def get_tv_dict(self):
        self.info['category'] = 'Series/Anime'

        return_latin = latin_alphabet(self.result.get('original_name'))
        self.info['display_name'] = self.result.get('name')
        if return_latin is True:
            self.info['display_name'] = self.result.get('original_name')

        self.info['date'] = change_air_format(self.result.get('first_air_date'))
        self.info['type'] = 'Series'
        if self.result.get('origin_country') == 'JP' or self.result.get('original_language') == 'ja' \
                and 16 in self.result.get('genre_ids'):
            self.info['type'] = 'Anime'

    def get_movies_dict(self):
        self.info['category'] = 'Movies'

        return_latin = latin_alphabet(self.result.get('original_title'))
        self.info['display_name'] = self.result.get('title')
        if return_latin is True:
            self.info['display_name'] = self.result.get('original_title')

        self.info['date'] = change_air_format(self.result.get('release_date'))
        self.info['type'] = 'Movie'
