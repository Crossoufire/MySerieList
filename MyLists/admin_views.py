from MyLists import db, app
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin, expose, AdminIndexView
from MyLists.models import User, UserLastUpdate, Series, SeriesList, SeriesEpisodesPerSeason, SeriesGenre, \
    SeriesNetwork, SeriesActors, Anime, AnimeEpisodesPerSeason, AnimeGenre, AnimeList, AnimeNetwork, AnimeActors, \
    Movies, MoviesGenre, MoviesList, MoviesActors, RoleType, Games, GamesList, GamesGenre, GamesCompanies, \
    GamesPlatforms


# --- USER ----------------------------------------------------------------------------------------------------- #

class UserAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True
    form_excluded_columns = ('series_list', 'anime_list', 'movies_list', 'games_list', 'redis_tasks',
                             'UserLastUpdate')
    column_exclude_list = ('password', )


class LastUpdateAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


# --- SERIES --------------------------------------------------------------------------------------------------- #

class SeriesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_display_pk = True
    column_exclude_list = ('synopsis',)


class SeriesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class SeriesEpisodesPerSeasonAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class SeriesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class SeriesNetworkAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class SeriesActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


# --- ANIME ---------------------------------------------------------------------------------------------------- #

class AnimeAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True
    column_exclude_list = ('synopsis',)


class AnimeListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class AnimeEpisodesPerSeasonAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class AnimeGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class AnimeNetworkAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class AnimeActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


# --- MOVIES --------------------------------------------------------------------------------------------------- #

class MoviesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True
    column_exclude_list = ('synopsis',)


class MoviesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class MoviesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class MoviesActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


# --- GAMES --------------------------------------------------------------------------------------------------- #

class GamesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True
    column_exclude_list = ('storyline', 'summary')


class GamesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class GamesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class GamesCompaniesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


class GamesPlatformsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN
    column_display_pk = True


# -------------------------------------------------------------------------------------------------------------- #


class MyHomeAdminView(AdminIndexView):
    @expose()
    def index(self):
        return self.render('admin/index.html')

    @staticmethod
    def is_accessible(**kwargs):
        return current_user.role == RoleType.ADMIN


# Create the /admin index view:
admin = Admin(app, name='Admin panel', index_view=MyHomeAdminView(), template_mode='bootstrap3')

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

admin.add_view(GamesAdminView(Games, db.session))
admin.add_view(GamesListAdminView(GamesList, db.session))
admin.add_view(GamesGenreAdminView(GamesGenre, db.session))
admin.add_view(GamesCompaniesAdminView(GamesCompanies, db.session))
admin.add_view(GamesPlatformsAdminView(GamesPlatforms, db.session))

