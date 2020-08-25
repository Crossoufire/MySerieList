import enum

from flask import abort
from datetime import datetime
from sqlalchemy.orm import aliased
from MyLists import app, db, login_manager
from flask_login import UserMixin, current_user
from sqlalchemy import func, desc, text, and_, or_
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Status(enum.Enum):
    WATCHING = "Watching"
    COMPLETED = "Completed"
    COMPLETED_ANIMATION = "Completed Animation"
    ON_HOLD = "On Hold"
    RANDOM = "Random"
    DROPPED = "Dropped"
    PLAN_TO_WATCH = "Plan to Watch"


class ListType(enum.Enum):
    SERIES = "serieslist"
    ANIME = "animelist"
    MOVIES = 'movieslist'


class MediaType(enum.Enum):
    SERIES = "Series"
    ANIME = "Anime"
    MOVIES = 'Movies'


class HomePage(enum.Enum):
    ACCOUNT = "account"
    HALL_OF_FAME = "hall_of_fame"
    MYSERIESLIST = "serieslist"
    MYANIMELIST = "animelist"
    MYMOVIESLIST = "movieslist"


class RoleType(enum.Enum):
    ADMIN = "admin"         # Can access to the admin dashboard (/admin)
    MANAGER = "manager"     # Can lock and edit media (/lock_media & /media_sheet_form)
    USER = "user"           # Standard user


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    oauth_id = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    homepage = db.Column(db.Enum(HomePage), nullable=False, default=HomePage.ACCOUNT)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    time_spent_series = db.Column(db.Integer, nullable=False, default=0)
    time_spent_movies = db.Column(db.Integer, nullable=False, default=0)
    time_spent_anime = db.Column(db.Integer, nullable=False, default=0)
    private = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    profile_views = db.Column(db.Integer, nullable=False, default=0)
    series_views = db.Column(db.Integer, nullable=False, default=0)
    anime_views = db.Column(db.Integer, nullable=False, default=0)
    movies_views = db.Column(db.Integer, nullable=False, default=0)
    biography = db.Column(db.Text)
    transition_email = db.Column(db.String(120))
    activated_on = db.Column(db.DateTime)
    last_notif_read_time = db.Column(db.DateTime)
    role = db.Column(db.Enum(RoleType), nullable=False, default=RoleType.USER)

    series_list = db.relationship('SeriesList', backref='user', lazy=True)
    anime_list = db.relationship('AnimeList', backref='user', lazy=True)
    movies_list = db.relationship('MoviesList', backref='user', lazy=True)
    followed = db.relationship('User',
                               secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def add_follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def remove_follow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_register_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_email_update_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def count_notifications(self):
        last_notif_time = self.last_notif_read_time or datetime(1900, 1, 1)
        return Notifications.query.filter_by(user_id=self.id)\
            .filter(Notifications.timestamp > last_notif_time).count()

    def get_notifications(self):
        return Notifications.query.filter_by(user_id=self.id).order_by(desc(Notifications.timestamp)).limit(8).all()

    def check_autorization(self, user_name):
        # retrieve the user
        user = User.query.filter_by(username=user_name).first()

        # No account with this username
        if not user:
            abort(404)

        # Protection of the admin account
        if self.role != RoleType.ADMIN and user.role == RoleType.ADMIN:
            abort(404)

        # Check if the current account can see the target account's movies collection
        if self.id == user.id or self.role == RoleType.ADMIN:
            pass
        elif user.private and not self.is_following(user):
            abort(404)

        return user

    def add_view_count(self, user, list_type):
        if self.role != RoleType.ADMIN and user.id != self.id:
            if list_type == ListType.SERIES:
                user.series_views += 1
            elif list_type == ListType.ANIME:
                user.anime_views += 1
            elif list_type == ListType.MOVIES:
                user.movies_views += 1
            db.session.commit()

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        user = User.query.get(user_id)
        if not user:
            return None
        else:
            return user


class UserLastUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_name = db.Column(db.String(50), nullable=False)
    media_type = db.Column(db.Enum(ListType), nullable=False)
    media_id = db.Column(db.Integer)
    old_status = db.Column(db.Enum(Status))
    new_status = db.Column(db.Enum(Status))
    old_season = db.Column(db.Integer)
    new_season = db.Column(db.Integer)
    old_episode = db.Column(db.Integer)
    new_episode = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False)


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    media_type = db.Column(db.String(50))
    media_id = db.Column(db.Integer)
    payload_json = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)


# --- SERIES -------------------------------------------------------------------------------------------------------


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
    first_air_date = db.Column(db.String(30))
    last_air_date = db.Column(db.String(30))
    next_episode_to_air = db.Column(db.String(30))
    season_to_air = db.Column(db.Integer)
    episode_to_air = db.Column(db.Integer)
    homepage = db.Column(db.String(200))
    in_production = db.Column(db.Boolean)
    created_by = db.Column(db.String(100))
    episode_duration = db.Column(db.Integer)
    total_seasons = db.Column(db.Integer, nullable=False)
    total_episodes = db.Column(db.Integer)
    origin_country = db.Column(db.String(20))
    status = db.Column(db.String(50))
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Float)
    synopsis = db.Column(db.Text)
    popularity = db.Column(db.Float)
    image_cover = db.Column(db.String(100), nullable=False)
    themoviedb_id = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    lock_status = db.Column(db.Boolean, default=0)

    genres = db.relationship('SeriesGenre', backref='series', lazy=True)
    actors = db.relationship('SeriesActors', backref='series', lazy=True)
    eps_per_season = db.relationship('SeriesEpisodesPerSeason', backref='series', lazy=False)
    networks = db.relationship('SeriesNetwork', backref='series', lazy=True)
    list_info = db.relationship('SeriesList', backref='series', lazy="dynamic")

    def get_same_genres(self, genres_list, genre_str):
        same_genres = db.session.query(Series, SeriesGenre) \
            .join(Series, Series.id == SeriesGenre.media_id) \
            .filter(SeriesGenre.genre.in_(genres_list), SeriesGenre.media_id != self.id) \
            .group_by(SeriesGenre.media_id) \
            .having(func.group_concat(SeriesGenre.genre.distinct()) == genre_str).limit(8).all()
        return same_genres

    def in_follows_lists(self, user_id):
        in_follows_lists = db.session.query(User, SeriesList, followers) \
            .join(User, User.id == followers.c.followed_id) \
            .join(SeriesList, SeriesList.user_id == followers.c.followed_id) \
            .filter(followers.c.follower_id == user_id, SeriesList.media_id == self.id).all()
        return in_follows_lists

    def in_user_list(self, user_id):
        in_user_list = self.list_info.filter_by(user_id=user_id).first()
        return in_user_list


class SeriesList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    current_season = db.Column(db.Integer, nullable=False)
    last_episode_watched = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    rewatched = db.Column(db.Integer, nullable=False, default=0)
    favorite = db.Column(db.Boolean)
    score = db.Column(db.Float)
    comment = db.Column(db.Text)


class SeriesGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class SeriesEpisodesPerSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    episodes = db.Column(db.Integer, nullable=False)


class SeriesNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    network = db.Column(db.String(150), nullable=False)


class SeriesActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    name = db.Column(db.String(150))


# --- ANIME -------------------------------------------------------------------------------------------------------


class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
    first_air_date = db.Column(db.String(30))
    last_air_date = db.Column(db.String(30))
    next_episode_to_air = db.Column(db.String(30))
    season_to_air = db.Column(db.Integer)
    episode_to_air = db.Column(db.Integer)
    homepage = db.Column(db.String(200))
    in_production = db.Column(db.Boolean)
    created_by = db.Column(db.String(100))
    episode_duration = db.Column(db.Integer)
    total_seasons = db.Column(db.Integer, nullable=False)
    total_episodes = db.Column(db.Integer)
    origin_country = db.Column(db.String(20))
    status = db.Column(db.String(50))
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Float)
    synopsis = db.Column(db.Text)
    popularity = db.Column(db.Float)
    image_cover = db.Column(db.String(100), nullable=False)
    themoviedb_id = db.Column(db.Integer, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)
    lock_status = db.Column(db.Boolean, default=0)

    genres = db.relationship('AnimeGenre', backref='anime', lazy=True)
    actors = db.relationship('AnimeActors', backref='anime', lazy=True)
    eps_per_season = db.relationship('AnimeEpisodesPerSeason', backref='anime', lazy=False)
    list_info = db.relationship('AnimeList', backref='anime', lazy='dynamic')
    networks = db.relationship('AnimeNetwork', backref='anime', lazy=True)

    def get_same_genres(self, genres_list, genre_str):
        same_genres = db.session.query(Anime, AnimeGenre) \
            .join(Anime, Anime.id == AnimeGenre.media_id) \
            .filter(AnimeGenre.genre.in_(genres_list), AnimeGenre.media_id != self.id) \
            .group_by(AnimeGenre.media_id) \
            .having(func.group_concat(AnimeGenre.genre.distinct()) == genre_str).limit(8).all()
        return same_genres

    def in_follows_lists(self, user_id):
        in_follows_lists = db.session.query(User, AnimeList, followers) \
            .join(User, User.id == followers.c.followed_id) \
            .join(AnimeList, AnimeList.user_id == followers.c.followed_id) \
            .filter(followers.c.follower_id == user_id, AnimeList.media_id == self.id).all()
        return in_follows_lists

    def in_user_list(self, user_id):
        in_user_list = self.list_info.filter_by(user_id=user_id).first()
        return in_user_list


class AnimeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    current_season = db.Column(db.Integer, nullable=False)
    last_episode_watched = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    rewatched = db.Column(db.Integer, nullable=False, default=0)
    favorite = db.Column(db.Boolean)
    score = db.Column(db.Float)
    comment = db.Column(db.Text)


class AnimeEpisodesPerSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    episodes = db.Column(db.Integer, nullable=False)


class AnimeGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class AnimeNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    network = db.Column(db.String(150), nullable=False)


class AnimeActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    name = db.Column(db.String(150))


# --- MOVIES -------------------------------------------------------------------------------------------------------


class MoviesCollections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('movies.collection_id'), nullable=False)
    parts = db.Column(db.Integer)
    name = db.Column(db.String(100))
    poster = db.Column(db.String(100))
    overview = db.Column(db.String(100))

    @staticmethod
    def get_collection_movies(user_id):
        collection_movie = db.session.query(Movies, MoviesList, MoviesCollections,
                                            func.count(MoviesCollections.collection_id)) \
            .join(MoviesList, MoviesList.media_id == Movies.id) \
            .join(MoviesCollections, MoviesCollections.collection_id == Movies.collection_id) \
            .filter(Movies.collection_id != None, MoviesList.user_id == user_id,
                    MoviesList.status != Status.PLAN_TO_WATCH).group_by(Movies.collection_id).all()
        return collection_movie


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
    director_name = db.Column(db.String(100))
    release_date = db.Column(db.String(30))
    homepage = db.Column(db.String(200))
    released = db.Column(db.String(30))
    runtime = db.Column(db.Integer)
    original_language = db.Column(db.String(20))
    synopsis = db.Column(db.Text)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Float)
    popularity = db.Column(db.Float)
    budget = db.Column(db.Float)
    revenue = db.Column(db.Float)
    tagline = db.Column(db.String(30))
    image_cover = db.Column(db.String(100), nullable=False)
    themoviedb_id = db.Column(db.Integer, nullable=False)
    collection_id = db.Column(db.Integer)
    lock_status = db.Column(db.Boolean, default=0)

    collection_movies = db.relationship('MoviesCollections',
                                        primaryjoin=(MoviesCollections.collection_id == collection_id),
                                        backref='movies',
                                        lazy='dynamic')
    genres = db.relationship('MoviesGenre', backref='movies', lazy=True)
    actors = db.relationship('MoviesActors', backref='movies', lazy=True)
    list_info = db.relationship('MoviesList', backref='movies', lazy='dynamic')

    def get_same_genres(self, genres_list, genre_str):
        same_genres = db.session.query(Movies, MoviesGenre) \
            .join(Movies, Movies.id == MoviesGenre.media_id) \
            .filter(MoviesGenre.genre.in_(genres_list), MoviesGenre.media_id != self.id) \
            .group_by(MoviesGenre.media_id) \
            .having(func.group_concat(MoviesGenre.genre.distinct()) == genre_str).limit(8).all()
        return same_genres

    def in_follows_lists(self, user_id):
        in_follows_lists = db.session.query(User, MoviesList, followers) \
            .join(User, User.id == followers.c.followed_id) \
            .join(AnimeList, MoviesList.user_id == followers.c.followed_id) \
            .filter(followers.c.follower_id == user_id, MoviesList.media_id == self.id).all()
        return in_follows_lists

    def in_user_list(self, user_id):
        in_user_list = self.list_info.filter_by(user_id=user_id).first()
        return in_user_list


class MoviesList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    media_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    rewatched = db.Column(db.Integer, nullable=False, default=0)
    favorite = db.Column(db.Boolean)
    score = db.Column(db.Float)
    comment = db.Column(db.Text)


class MoviesGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class MoviesActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    name = db.Column(db.String(150))


# --- BADGES & RANKS -----------------------------------------------------------------------------------------------


class Badges(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    threshold = db.Column(db.Integer, nullable=False)
    image_id = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    genres_id = db.Column(db.String(100))


class Ranks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    image_id = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)


class Frames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, nullable=False)
    image_id = db.Column(db.String(50), nullable=False)


# --- OTHERS ------------------------------------------------------------------------------------------------------


class GlobalStats:
    def __init__(self):
        self.all_list_type = [ListType.SERIES, ListType.ANIME, ListType.MOVIES]
        self.truncated_list_type = [ListType.SERIES, ListType.ANIME]
        self.media = None
        self.media_genre = None
        self.media_actors = None
        self.media_eps = None
        self.media_list = None

    def get_type(self, list_type):
        if list_type == ListType.SERIES:
            self.media = Series
            self.media_genre = SeriesGenre
            self.media_actors = SeriesActors
            self.media_eps = SeriesEpisodesPerSeason
            self.media_list = SeriesList
        elif list_type == ListType.ANIME:
            self.media = Anime
            self.media_genre = AnimeGenre
            self.media_actors = AnimeActors
            self.media_eps = AnimeEpisodesPerSeason
            self.media_list = AnimeList
        elif list_type == ListType.MOVIES:
            self.media = Movies
            self.media_genre = MoviesGenre
            self.media_actors = MoviesActors
            self.media_list = MoviesList

    @staticmethod
    def get_total_time_spent():
        times_spent = db.session.query(func.sum(User.time_spent_series), func.sum(User.time_spent_anime),
                                       func.sum(User.time_spent_movies)) \
            .filter(User.role != RoleType.ADMIN, User.active == True).all()
        return times_spent

    def get_top_media(self):
        queries = []
        for list_type in self.all_list_type:
            self.get_type(list_type)
            queries.append(db.session.query(self.media, self.media_list,
                                            func.count(self.media_list.media_id == self.media.id).label("count"))
                           .join(self.media_list, self.media_list.media_id == self.media.id)
                           .group_by(self.media_list.media_id).order_by(text("count desc")).limit(5).all())
        return queries

    def get_top_genres(self):
        queries = []
        for list_type in self.all_list_type:
            self.get_type(list_type)
            queries.append(db.session.query(self.media_genre, self.media_list,
                                            func.count(self.media_genre.genre).label('count'))
                           .join(self.media_genre, self.media_genre.media_id == self.media_list.media_id)
                           .group_by(self.media_genre.genre).order_by(text('count desc')).limit(5).all())
        return queries

    def get_top_actors(self):
        queries = []
        for list_type in self.all_list_type:
            self.get_type(list_type)
            queries.append(db.session.query(self.media_actors, self.media_list,
                                            func.count(self.media_actors.name).label('count'))
                           .join(self.media_actors, self.media_actors.media_id == self.media_list.media_id)
                           .group_by(self.media_actors.name).filter(self.media_actors.name != 'Unknown')
                           .order_by(text('count desc')).limit(5).all())
        return queries

    def get_top_dropped(self):
        queries = []
        for list_type in self.truncated_list_type:
            self.get_type(list_type)
            queries.append(db.session.query(self.media, self.media_list,
                                            func.count(self.media_list.media_id == self.media.id).label('count'))
                           .join(self.media_list, self.media_list.media_id == self.media.id)
                           .filter(self.media_list.status == Status.DROPPED).group_by(self.media_list.media_id)
                           .order_by(text('count desc')).limit(5).all())
        return queries

    def get_total_eps_seasons(self):
        queries = []
        for list_type in self.truncated_list_type:
            self.get_type(list_type)
            queries.append(db.session.query(self.media_list, self.media_eps,
                                            func.group_concat(self.media_eps.episodes))
                           .join(self.media_eps, self.media_eps.media_id == self.media_list.media_id)
                           .group_by(self.media_list.id).all())
        return queries


def get_media_query(user_id, page, list_type, category, option=None, search=None, favorite=None, common=None):
    if list_type == ListType.SERIES:
        media = Series
        media_list = SeriesList
        actors_list = SeriesActors
        genre_list = SeriesGenre
    elif list_type == ListType.ANIME:
        media = Anime
        media_list = AnimeList
        actors_list = AnimeActors
        genre_list = AnimeGenre
    elif list_type == ListType.MOVIES:
        media = Movies
        media_list = MoviesList
        actors_list = MoviesActors
        genre_list = MoviesGenre

    if not search and not common and not favorite:
        query = db.session.query(media, media_list) \
            .join(media_list, media_list.media_id == media.id) \
            .filter(media_list.user_id == user_id, media_list.status == category).group_by(media.id) \
            .order_by(media.name.asc()).paginate(page, 50, error_out=True)
        category = category.value
    elif search:
        if option == 'Titles':
            query = db.session.query(media, media_list) \
                .join(media, media.id == media_list.media_id) \
                .filter(or_(media.name.like('%' + search + '%'), media.original_name.like('%' + search + '%')),
                        media_list.user_id == user_id) \
                .order_by(media_list.status).paginate(page, 30, error_out=True)
        elif option == 'Actors':
            query = db.session.query(media, media_list, actors_list) \
                .join(media, media.id == media_list.media_id)\
                .join(actors_list, actors_list.media_id == media_list.media_id) \
                .filter(actors_list.name.like('%' + search + '%'), media_list.user_id == user_id) \
                .order_by(media_list.status).paginate(page, 30, error_out=True)
        elif option == 'Genres':
            query = db.session.query(media, media_list, genre_list) \
                .join(media, media.id == media_list.media_id)\
                .join(genre_list, genre_list.media_id == media_list.media_id) \
                .filter(genre_list.genre.like('%' + search + '%'), media_list.user_id == user_id) \
                .order_by(media_list.status).paginate(page, 50, error_out=True)
        elif option == 'Director':
            query = db.session.query(media, media_list) \
                .join(media, media.id == media_list.media_id) \
                .filter(media.director_name.like('%' + search + '%'), media_list.user_id == user_id) \
                .order_by(media_list.status).paginate(page, 30, error_out=True)
        else:
            abort(404)
        category = "{} Search results for '{}'".format(option, search)
    elif favorite:
        query = db.session.query(media, media_list) \
            .join(media, media.id == media_list.media_id) \
            .filter(media_list.favorite, media_list.user_id == user_id) \
            .order_by(media_list.status).paginate(page, 30, error_out=True)
        category = "All Favorites"
    elif common:
        v1, v2 = aliased(media_list), aliased(media_list)
        get_common = db.session.query(v1, v2) \
            .join(v2, and_(v2.user_id == user_id, v2.media_id == v1.media_id)) \
            .filter(v1.user_id == current_user.id).all()
        common_ids = [r[0].media_id for r in get_common]
        query = db.session.query(media, media_list) \
            .join(media, media.id == media_list.media_id) \
            .filter(media_list.user_id == user_id, media_list.media_id.notin_(common_ids),
                    media_list.status == category).paginate(page, 50, error_out=True)
        category = category.value
    else:
        abort(404)

    return query, category


def get_media_count(user_id, list_type):
    if list_type == ListType.SERIES:
        media_list = SeriesList
    elif list_type == ListType.ANIME:
        media_list = AnimeList
    elif list_type == ListType.MOVIES:
        media_list = MoviesList

    v1, v2 = aliased(media_list), aliased(media_list)
    count_total = media_list.query.filter_by(user_id=user_id).count()
    count_versus = db.session.query(v1, v2) \
        .join(v2, and_(v2.user_id == user_id, v2.media_id == v1.media_id)) \
        .filter(v1.user_id == current_user.id).all()
    common_ids = [r[0].media_id for r in count_versus]

    return common_ids, int(count_total)


def get_next_airing(list_type):
    if list_type == ListType.SERIES:
        media = Series
        media_data = Series.next_episode_to_air
        media_list = SeriesList
    elif list_type == ListType.ANIME:
        media = Anime
        media_data = Anime.next_episode_to_air
        media_list = AnimeList
    elif list_type == ListType.MOVIES:
        media = Movies
        media_data = Movies.release_date
        media_list = MoviesList

    query = db.session.query(media, media_list) \
        .join(media, media.id == media_list.media_id) \
        .filter(media_data > datetime.utcnow(), media_list.user_id == current_user.id,
                and_(media_list.status != Status.RANDOM, media_list.status != Status.DROPPED)).all()

    return query


def get_total_time(user_id, list_type):
    if list_type == ListType.SERIES:
        media = Series
        media_list = SeriesList
    elif list_type == ListType.ANIME:
        media = Anime
        media_list = AnimeList
    elif list_type == ListType.MOVIES:
        media = Movies
        media_list = MoviesList

    query = db.session.query(media, media_list) \
        .join(media, media.id == media_list.media_id) \
        .filter(media_list.user_id == user_id)

    return query


def check_media(media_id, list_type, add=False):
    if list_type == ListType.SERIES:
        media = Series
        media_list = SeriesList
    elif list_type == ListType.ANIME:
        media = Anime
        media_list = AnimeList
    elif list_type == ListType.MOVIES:
        media = Movies
        media_list = MoviesList

    query = db.session.query(media, media_list) \
        .join(media, media.id == media_list.media_id) \
        .filter(media.id == media_id, media_list.user_id == current_user.id).first()

    if add:
        query = db.session.query(media).filter(media.id == media_id).first()

    return query
