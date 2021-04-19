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

    column_list = ('id', 'username', 'email', 'active', 'private')
    column_searchable_list = ('username', 'email')
    column_sortable_list = ('id', 'username', 'email', 'active', 'private')


class LastUpdateAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('user_id', 'media_name', 'media_type', 'old_status', 'new_status', 'old_season', 'new_season',
                   'old_episode', 'new_episode', 'date')
    column_searchable_list = ('user_id', 'media_name')
    column_sortable_list = ('user_id', 'media_name', 'date')


# --- SERIES --------------------------------------------------------------------------------------------------- #

class SeriesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_display_pk = True
    column_exclude_list = ('original_name', 'homepage', 'synopsis', 'image_cover', 'in_production')
    column_searchable_list = ['name']


class SeriesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('user_id', 'media_id', 'current_season', 'last_episode_watched', 'status', 'score')
    column_searchable_list = ('user_id', 'media_id', 'status')
    column_sortable_list = ('id', 'user_id', 'media_id', 'status')


class SeriesEpisodesPerSeasonAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'season', 'episodes')
    column_searchable_list = ['media_id']
    column_sortable_list = ('id', 'media_id')


class SeriesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'genre')
    column_searchable_list = ['media_id']
    column_sortable_list = ('media_id', 'genre')


class SeriesNetworkAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'network')
    column_searchable_list = ('media_id', 'network')
    column_sortable_list = ('media_id', 'network')


class SeriesActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'name')
    column_searchable_list = ('media_id', 'name')
    column_sortable_list = ('media_id', 'name')


# --- ANIME ---------------------------------------------------------------------------------------------------- #

class AnimeAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_display_pk = True
    column_exclude_list = ('homepage', 'synopsis', 'image_cover', 'themoviedb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'original_name', 'in_production', 'created_by', 'origin_country', 'status',
                            'duration', 'total_seasons', 'total_episodes', 'vote_average', 'vote_count',
                            'popularity', 'first_air_date', 'last_air_date', 'last_update')


class AnimeListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('user_id', 'media_id', 'current_season', 'last_episode_watched', 'status', 'score')
    column_searchable_list = ('user_id', 'media_id', 'status')
    column_sortable_list = ('id', 'user_id', 'media_id', 'status')


class AnimeEpisodesPerSeasonAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'season', 'episodes')
    column_searchable_list = ['media_id']
    column_sortable_list = ('id', 'media_id')


class AnimeGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'genre')
    column_searchable_list = ('media_id', 'genre')
    column_sortable_list = ('media_id', 'genre')


class AnimeNetworkAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'network')
    column_searchable_list = ('media_id', 'network')
    column_sortable_list = ('media_id', 'network')


class AnimeActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'name')
    column_searchable_list = ('media_id', 'name')
    column_sortable_list = ('media_id', 'name')


# --- MOVIES --------------------------------------------------------------------------------------------------- #

class MoviesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_display_pk = True
    column_exclude_list = ('homepage', 'released', 'synopsis', 'tagline', 'image_cover', 'themoviedb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'original_name', 'release_date', 'duration', 'original_language',
                            'vote_average', 'vote_count', 'popularity', 'budget', 'revenue')


class MoviesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'genre')
    column_searchable_list = ['media_id']
    column_sortable_list = ('media_id', 'genre')


class MoviesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('user_id', 'media_id', 'status', 'score')
    column_searchable_list = ('user_id', 'media_id', 'status')
    column_sortable_list = ('id', 'user_id', 'media_id', 'status')


class MoviesActorsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'name')
    column_searchable_list = ('media_id', 'name')
    column_sortable_list = ('id', 'media_id', 'name')


# --- GAMES --------------------------------------------------------------------------------------------------- #

class GamesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_display_pk = True
    column_exclude_list = ('storyline', 'summary', 'tagline', 'image_cover', 'themoviedb_id', 'IGDB_url', 'igdb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'release_date', 'hltb_main_time', 'hltb_main_and_extra_time',
                            'hltb_total_complete_time', 'vote_average', 'vote_count', 'game_modes', 'game_engine',
                            'lock_status')


class GamesGenreAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'genre')
    column_searchable_list = ['media_id']
    column_sortable_list = ('media_id', 'genre')


class GamesListAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('user_id', 'media_id', 'status', 'score')
    column_searchable_list = ('user_id', 'media_id', 'status')
    column_sortable_list = ('id', 'user_id', 'media_id', 'status')


class GamesCompaniesAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'name')
    column_searchable_list = ('media_id', 'name')
    column_sortable_list = ('id', 'media_id', 'name')


class GamesPlatformsAdminView(ModelView):
    def is_accessible(self):
        return current_user.role == RoleType.ADMIN

    column_list = ('media_id', 'name')
    column_searchable_list = ('media_id', 'name')
    column_sortable_list = ('id', 'media_id', 'name')


# -------------------------------------------------------------------------------------------------------------- #


class MyHomeAdminView(AdminIndexView):
    @expose()
    def index(self):
        return self.render('admin/index.html')

    @staticmethod
    def is_accessible(**kwargs):
        return current_user.role == RoleType.ADMIN


# Create the /admin index view:
admin = Admin(app, name='Admin panel', index_view=MyHomeAdminView())

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

