import pykakasi
from flask import url_for
from datetime import datetime
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
