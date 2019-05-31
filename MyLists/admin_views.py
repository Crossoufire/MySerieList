from flask_admin import expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from MyLists.models import User, Serie, List, Episodesperseason, Genre, Network, Friend, Episodetimestamp
from MyLists import db, app
from flask_login import current_user
from flask_admin import Admin


class UserAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('id', 'username', 'email', 'active', 'private')
    column_searchable_list = ('username', 'email')
    column_sortable_list = ('id', 'username', 'email', 'active', 'private')

    list_template = 'admin/user.html'


class SerieAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_display_pk = True
    column_exclude_list = ('homepage', 'synopsis', 'image_cover', 'themoviedb_id')
    column_searchable_list = ['name']
    column_sortable_list = ('id', 'name', 'original_name', 'in_production', 'created_by', 'origin_country', 'status', 'episode_duration', 'total_seasons', 'total_episodes', 'vote_average', 'vote_count', 'popularity', 'first_air_date', 'last_air_date')

    list_template = 'admin/serie.html'


class ListAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'serie_id', 'current_season', 'last_episode_watched', 'status')
    column_searchable_list = ('user_id', 'serie_id', 'status')
    column_sortable_list = ('id', 'user_id', 'serie_id', 'status')

    list_template = 'admin/list.html'


class EpisodesperseasonAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('serie_id', 'season', 'episodes')
    column_searchable_list = ['serie_id']
    column_sortable_list = ('id', 'serie_id')

    list_template = 'admin/episodesperseason.html'


class GenreAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('serie_id', 'genre')
    column_searchable_list = ['serie_id']
    column_sortable_list = ('serie_id', 'genre')

    list_template = 'admin/genre.html'


class NetworkAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('serie_id', 'network')
    column_searchable_list = ('serie_id', 'network')
    column_sortable_list = ('serie_id', 'network')

    list_template = 'admin/network.html'


class FriendAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'friend_id', 'status')
    column_searchable_list = ('user_id', 'friend_id', 'status')
    column_sortable_list = ('user_id', 'friend_id', 'status')

    list_template = 'admin/friend.html'


class EpisodetimestampAdminsView(ModelView):

    def is_accessible(self):
        return current_user.get_id() == '1'

    column_list = ('user_id', 'serie_id', 'season', 'episode', 'timestamp')
    column_searchable_list = ('user_id', 'serie_id', 'timestamp')
    column_sortable_list = ('user_id', 'serie_id', 'timestamp')

    list_template = 'admin/episodetimestamp.html'


# Override of the index flask-admin view:
class MyHomeAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    @staticmethod
    def is_accessible():
        return current_user.get_id() == '1'


# Create the /admin index view:
admin = Admin(app, name='MyLists', index_view=MyHomeAdminView())

admin.add_view(UserAdminsView(model=User, session=db.session, name="User", endpoint='user'))
admin.add_view(SerieAdminsView(model=Serie, session=db.session, name="Serie", endpoint='serie'))
admin.add_view(ListAdminsView(model=List, session=db.session, name="List", endpoint='list'))
admin.add_view(EpisodesperseasonAdminsView(model=Episodesperseason, session=db.session, name="Episodesperseason", endpoint='episodesperseason'))
admin.add_view(GenreAdminsView(model=Genre, session=db.session, name="Genre", endpoint='genre'))
admin.add_view(NetworkAdminsView(model=Network, session=db.session, name="Network", endpoint='network'))
admin.add_view(FriendAdminsView(model=Friend, session=db.session, name="Friend", endpoint='friend'))
admin.add_view(EpisodetimestampAdminsView(model=Episodetimestamp, session=db.session, name="Episodetimestamp", endpoint='episodetimestamp'))
