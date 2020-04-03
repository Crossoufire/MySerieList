from MyLists import db, app
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, expose, AdminIndexView
from MyLists.models import User, UserLastUpdate, Series, SeriesList, SeriesEpisodesPerSeason, SeriesGenre, \
    SeriesNetwork, SeriesActors, Anime, AnimeEpisodesPerSeason, AnimeGenre, AnimeList, AnimeNetwork, AnimeActors, \
    Movies, MoviesGenre, MoviesList, MoviesActors


# ------------------------------------------------------- USER ------------------------------------------------------- #

class UserAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('id', 'username', 'email', 'active', 'private')
    column_searchable_list = ('username', 'email')
    column_sortable_list = ('id', 'username', 'email', 'active', 'private')


class LastUpdateAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'media_name', 'media_type', 'old_status', 'new_status', 'old_season', 'new_season',
                   'old_episode', 'new_episode', 'date')
    column_searchable_list = ('user_id', 'media_name')
    column_sortable_list = ('user_id', 'media_name', 'date')


# ------------------------------------------------------ SERIES ------------------------------------------------------ #

class SeriesAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_display_pk = True
    column_exclude_list = ('original_name', 'homepage', 'synopsis', 'image_cover', 'in_production')
    column_searchable_list = ['name']


class SeriesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'series_id', 'current_season', 'last_episode_watched', 'status', 'score')
    column_searchable_list = ('user_id', 'series_id', 'status')
    column_sortable_list = ('id', 'user_id', 'series_id', 'status')


class SeriesEpisodesPerSeasonAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('series_id', 'season', 'episodes')
    column_searchable_list = ['series_id']
    column_sortable_list = ('id', 'series_id')


class SeriesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('series_id', 'genre')
    column_searchable_list = ['series_id']
    column_sortable_list = ('series_id', 'genre')


class SeriesNetworkAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('series_id', 'network')
    column_searchable_list = ('series_id', 'network')
    column_sortable_list = ('series_id', 'network')


class SeriesActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('series_id', 'name')
    column_searchable_list = ('series_id', 'name')
    column_sortable_list = ('series_id', 'name')


# ------------------------------------------------------ ANIME ------------------------------------------------------- #

class AnimeAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_display_pk = True
    column_exclude_list = ('homepage', 'synopsis', 'image_cover', 'themoviedb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'original_name', 'in_production', 'created_by', 'origin_country', 'status',
                            'episode_duration', 'total_seasons', 'total_episodes', 'vote_average', 'vote_count',
                            'popularity', 'first_air_date', 'last_air_date', 'last_update')


class AnimeListAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'anime_id', 'current_season', 'last_episode_watched', 'status', 'score')
    column_searchable_list = ('user_id', 'anime_id', 'status')
    column_sortable_list = ('id', 'user_id', 'anime_id', 'status')


class AnimeEpisodesPerSeasonAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('anime_id', 'season', 'episodes')
    column_searchable_list = ['anime_id']
    column_sortable_list = ('id', 'anime_id')


class AnimeGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('anime_id', 'genre')
    column_searchable_list = ('anime_id', 'genre')
    column_sortable_list = ('anime_id', 'genre')


class AnimeNetworkAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('anime_id', 'network')
    column_searchable_list = ('anime_id', 'network')
    column_sortable_list = ('anime_id', 'network')


class AnimeActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('anime_id', 'name')
    column_searchable_list = ('anime_id', 'name')
    column_sortable_list = ('anime_id', 'name')


# ------------------------------------------------------ MOVIES ------------------------------------------------------ #

class MoviesAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_display_pk = True
    column_exclude_list = ('homepage', 'released', 'synopsis', 'tagline', 'image_cover', 'themoviedb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'original_name', 'release_date', 'runtime', 'original_language',
                            'vote_average', 'vote_count', 'popularity', 'budget', 'revenue')


class MoviesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('movies_id', 'genre')
    column_searchable_list = ['movies_id']
    column_sortable_list = ('movies_id', 'genre')


class MoviesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'movies_id', 'status', 'score')
    column_searchable_list = ('user_id', 'movies_id', 'status')
    column_sortable_list = ('id', 'user_id', 'movies_id', 'status')


class MoviesActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('movies_id', 'name')
    column_searchable_list = ('movies_id', 'name')
    column_sortable_list = ('id', 'movies_id', 'name')


# -------------------------------------------------------------------------------------------------------------------- #

# Override of the index flask-admin view:
class MyHomeAdminView(AdminIndexView):
    @expose()
    def index(self):
        return self.render('admin/index.html')

    @staticmethod
    def is_accessible(**kwargs):
        return current_user.get_id() == '1'


# Create the /admin index view:
admin = Admin(app, name='Admin Panel', index_view=MyHomeAdminView())

admin.add_view(UserAdminView(User, db.session))
admin.add_view(LastUpdateAdminView(UserLastUpdate, db.session))

admin.add_view(SeriesAdminView(Series, db.session))
admin.add_view(SeriesListAdminView(SeriesList, db.session))
admin.add_view(SeriesGenreAdminView(SeriesGenre, db.session))
admin.add_view(SeriesNetworkAdminView(SeriesNetwork, db.session))
admin.add_view(SeriesActorsAdminView(SeriesActors, db.session))
admin.add_view(SeriesEpisodesPerSeasonAdminView(SeriesEpisodesPerSeason, db.session))

admin.add_view(AnimeAdminView(Anime, db.session))
admin.add_view(AnimeListAdminView(AnimeList, db.session))
admin.add_view(AnimeGenreAdminView(AnimeGenre, db.session))
admin.add_view(AnimeNetworkAdminView(AnimeNetwork, db.session))
admin.add_view(AnimeActorsAdminView(AnimeActors, db.session))
admin.add_view(AnimeEpisodesPerSeasonAdminView(AnimeEpisodesPerSeason, db.session))

admin.add_view(MoviesAdminView(Movies, db.session))
admin.add_view(MoviesListAdminView(MoviesList, db.session))
admin.add_view(MoviesGenreAdminView(MoviesGenre, db.session))
admin.add_view(MoviesActorsAdminView(MoviesActors, db.session))
