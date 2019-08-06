from flask_admin import expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from MyLists.models import User, Friend, Series, SeriesList, SeriesEpisodesPerSeason, SeriesGenre, SeriesNetwork, \
    SeriesEpisodeTimestamp, Anime, AnimeEpisodesPerSeason, AnimeEpisodeTimestamp, AnimeGenre, AnimeList, AnimeNetwork, Book, BookList
from MyLists import db, app
from flask_login import current_user
from flask_admin import Admin


class UserAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('id', 'username', 'email', 'active', 'private')
    column_searchable_list = ('username', 'email')
    column_sortable_list = ('id', 'username', 'email', 'active', 'private')
    list_template = 'admin/user.html'


class FriendAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'friend_id', 'status')
    column_searchable_list = ('user_id', 'friend_id', 'status')
    column_sortable_list = ('user_id', 'friend_id', 'status')
    list_template = 'admin/friend.html'


######################################################## SERIES ########################################################


class SeriesAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_display_pk = True
    column_exclude_list = ('homepage', 'synopsis', 'image_cover', 'themoviedb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'original_name', 'in_production', 'created_by', 'origin_country', 'status',
                            'episode_duration', 'total_seasons', 'total_episodes', 'vote_average', 'vote_count',
                            'popularity', 'first_air_date', 'last_air_date')
    list_template = 'admin/series.html'


class SeriesListAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'series_id', 'current_season', 'last_episode_watched', 'status', 'score')
    column_searchable_list = ('user_id', 'series_id', 'status')
    column_sortable_list = ('id', 'user_id', 'series_id', 'status')
    list_template = 'admin/series_list.html'


class SeriesEpisodesPerSeasonAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('series_id', 'season', 'episodes')
    column_searchable_list = ['series_id']
    column_sortable_list = ('id', 'series_id')
    list_template = 'admin/series_episodes_per_season.html'


class SeriesGenreAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('series_id', 'genre')
    column_searchable_list = ['series_id']
    column_sortable_list = ('series_id', 'genre')
    list_template = 'admin/series_genre.html'


class SeriesNetworkAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('series_id', 'network')
    column_searchable_list = ('series_id', 'network')
    column_sortable_list = ('series_id', 'network')
    list_template = 'admin/series_network.html'


class SeriesEpisodeTimestampAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'series_id', 'season', 'episode', 'timestamp')
    column_searchable_list = ('user_id', 'series_id', 'timestamp')
    column_sortable_list = ('user_id', 'series_id', 'timestamp')
    list_template = 'admin/series_episode_timestamp.html'


######################################################## ANIME ########################################################


class AnimeAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_display_pk = True
    column_exclude_list = ('homepage', 'synopsis', 'image_cover', 'themoviedb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'original_name', 'in_production', 'created_by', 'origin_country', 'status',
                            'episode_duration', 'total_seasons', 'total_episodes', 'vote_average', 'vote_count',
                            'popularity', 'first_air_date', 'last_air_date')
    list_template = 'admin/anime.html'


class AnimeListAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'anime_id', 'current_season', 'last_episode_watched', 'status', 'score')
    column_searchable_list = ('user_id', 'anime_id', 'status')
    column_sortable_list = ('id', 'user_id', 'anime_id', 'status')
    list_template = 'admin/anime_list.html'


class AnimeEpisodesPerSeasonAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('anime_id', 'season', 'episodes')
    column_searchable_list = ['anime_id']
    column_sortable_list = ('id', 'anime_id')
    list_template = 'admin/anime_episodes_per_season.html'


class AnimeGenreAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('anime_id', 'genre')
    column_searchable_list = ['anime_id']
    column_sortable_list = ('anime_id', 'genre')
    list_template = 'admin/anime_genre.html'


class AnimeNetworkAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('anime_id', 'network')
    column_searchable_list = ('anime_id', 'network')
    column_sortable_list = ('anime_id', 'network')
    list_template = 'admin/anime_network.html'


class AnimeEpisodeTimestampAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'anime_id', 'season', 'episode', 'timestamp')
    column_searchable_list = ('user_id', 'anime_id', 'timestamp')
    column_sortable_list = ('user_id', 'anime_id', 'timestamp')
    list_template = 'admin/anime_episode_timestamp.html'


######################################################### BOOK #########################################################

class BookAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_display_pk = True
    column_exclude_list = ('image_cover', 'description', 'google_id')
    column_searchable_list = ['title']
    column_sortable_list = ('id', 'title', 'authors', 'published_date', 'page_count', 'categories')
    list_template = 'admin/book.html'


class BookListAdminView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'book_id', 'commentary', 'read_year', 'status', 'score')
    column_searchable_list = ('user_id', 'book_id')
    column_sortable_list = ('user_id', 'book_id', 'status')
    list_template = 'admin/book_list.html'


# Override of the index flask-admin view:
class MyHomeAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    @staticmethod
    def is_accessible():
        return current_user.get_id() == '1'


# Create the /admin index view:
admin = Admin(app, name='MyLists',
              index_view=MyHomeAdminView())

admin.add_view(UserAdminView(model=User,
                             session=db.session,
                             name="User",
                             endpoint='user'))

admin.add_view(FriendAdminView(model=Friend,
                               session=db.session,
                               name="Friend",
                               endpoint='friend'))

admin.add_view(SeriesAdminView(model=Series,
                               session=db.session,
                               name="Series",
                               endpoint='series'))

admin.add_view(SeriesListAdminView(model=SeriesList,
                                   session=db.session,
                                   name="Series list",
                                   endpoint='series_list'))

admin.add_view(SeriesEpisodesPerSeasonAdminView(model=SeriesEpisodesPerSeason,
                                                session=db.session,
                                                name="Series episodes per season",
                                                endpoint='series_episodes_per_season'))

admin.add_view(SeriesGenreAdminView(model=SeriesGenre,
                                    session=db.session,
                                    name="Series genre",
                                    endpoint='series_genre'))

admin.add_view(SeriesNetworkAdminView(model=SeriesNetwork,
                                      session=db.session,
                                      name="Series network",
                                      endpoint='series_network'))

admin.add_view(SeriesEpisodeTimestampAdminView(model=SeriesEpisodeTimestamp,
                                               session=db.session,
                                               name="Series episode timestamp",
                                               endpoint='series_episode_timestamp'))
admin.add_view(AnimeAdminView(model=Anime,
                              session=db.session,
                              name="Anime",
                              endpoint='anime'))

admin.add_view(AnimeListAdminView(model=AnimeList,
                                  session=db.session,
                                  name="Anime list",
                                  endpoint='anime_list'))

admin.add_view(AnimeEpisodesPerSeasonAdminView(model=AnimeEpisodesPerSeason,
                                               session=db.session,
                                               name="Anime episodes per season",
                                               endpoint='anime_episodes_per_season'))

admin.add_view(AnimeGenreAdminView(model=AnimeGenre,
                                   session=db.session,
                                   name="Anime genre",
                                   endpoint='anime_genre'))

admin.add_view(AnimeNetworkAdminView(model=AnimeNetwork,
                                     session=db.session,
                                     name="Anime network",
                                     endpoint='anime_network'))

admin.add_view(AnimeEpisodeTimestampAdminView(model=AnimeEpisodeTimestamp,
                                              session=db.session,
                                              name="Anime episode timestamp",
                                              endpoint='anime_episode_timestamp'))

admin.add_view(BookAdminView(model=Book,
                             session=db.session,
                             name="Book",
                             endpoint='book'))

admin.add_view(BookListAdminView(model=BookList,
                                 session=db.session,
                                 name="Book list",
                                 endpoint='book_list'))
