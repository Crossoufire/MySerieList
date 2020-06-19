import enum

from datetime import datetime
from sqlalchemy import func, desc
from flask_login import UserMixin
from MyLists import app, db, login_manager
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


class HomePage(enum.Enum):
    ACCOUNT = "account"
    HALL_OF_FAME = "hall_of_fame"
    MYSERIESLIST = "serieslist"
    MYANIMELIST = "animelist"
    MYMOVIESLIST = "movieslist"


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    homepage = db.Column(db.Enum(HomePage), nullable=False, default=HomePage.MYSERIESLIST)
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

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        user = User.query.get(user_id)
        if user is None:
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


# --- SERIES -------------------------------------------------------------------------------------------------------


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
    first_air_date = db.Column(db.String(30))
    last_air_date = db.Column(db.String(30))
    next_episode_to_air = db.Column(db.String(30))
    season_to_air = db.Column(db.Integer, default=None)
    episode_to_air = db.Column(db.Integer, default=None)
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
    eps_per_season = db.relationship('SeriesEpisodesPerSeason', backref='series', lazy=True)
    list_info = db.relationship('SeriesList', backref='series', lazy='dynamic')
    networks = db.relationship('SeriesNetwork', backref='series', lazy=True)

    def get_info(self):
        # Change first air time format
        if 'Unknown' not in self.first_air_date:
            first_air_date = datetime.strptime(self.first_air_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            first_air_date = 'Unknown'

        # Change last air time format
        if 'Unknown' not in self.last_air_date:
            last_air_date = datetime.strptime(self.last_air_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            last_air_date = 'Unknown'

        # Check name and original name
        if self.original_name != self.name:
            original_name = self.original_name
            name = self.name
        else:
            original_name = self.original_name
            name = None

        element_info = {"id": self.id,
                        "cover": 'series_covers/{}'.format(self.image_cover),
                        "cover_path": 'series_covers',
                        "name": name,
                        "original_name": original_name,
                        "first_air_date": first_air_date,
                        "last_air_date": last_air_date,
                        "created_by": self.created_by,
                        "episode_duration": self.episode_duration,
                        "homepage": self.homepage,
                        "in_production": self.in_production,
                        "origin_country": self.origin_country,
                        "total_seasons": self.total_seasons,
                        "total_episodes": self.total_episodes,
                        "prod_status": self.status,
                        "vote_average": self.vote_average,
                        "vote_count": self.vote_count,
                        "synopsis": self.synopsis,
                        "popularity": self.popularity,
                        "media_type": 'Series',
                        "lock_status": self.lock_status,
                        "eps_per_season": [r.episodes for r in self.eps_per_season],
                        "actors": ', '.join([r.name for r in self.actors]),
                        "genres": ', '.join([r.genre for r in self.genres]),
                        "networks": ', '.join([r.network for r in self.networks])}

        return element_info

    def get_same_genres(self):
        if len([r.genre for r in self.genres]) > 2:
            genres_list = [r.genre for r in self.genres][:2]
            genre_str = ','.join([g for g in genres_list])
        else:
            genres_list = [r.genre for r in self.genres]
            genre_str = ','.join([g for g in genres_list])

        same_genres = db.session.query(Series, SeriesGenre) \
            .join(Series, Series.id == SeriesGenre.series_id) \
            .filter(SeriesGenre.genre.in_(genres_list), SeriesGenre.series_id != self.id) \
            .group_by(SeriesGenre.series_id) \
            .having(func.group_concat(SeriesGenre.genre.distinct()) == genre_str).limit(8).all()

        return same_genres

    def in_follows_lists(self, user_id):
        in_follows_lists = db.session.query(User, SeriesList, followers) \
            .join(User, User.id == followers.c.followed_id) \
            .join(SeriesList, SeriesList.user_id == followers.c.followed_id) \
            .filter(followers.c.follower_id == user_id, SeriesList.series_id == self.id).all()

        return in_follows_lists

    def in_user_list(self, user_id):
        in_user_list = self.list_info.filter_by(user_id=user_id).first()

        if in_user_list:
            element_info = {'in_user_list': True,
                            'last_episode_watched': in_user_list.last_episode_watched,
                            'current_season': in_user_list.current_season,
                            'score': in_user_list.score,
                            'favorite': in_user_list.favorite,
                            'status': in_user_list.status.value}
        else:
            element_info = {'last_episode_watched': 1,
                            'current_season': 1,
                            'score': 0,
                            'favorite': False,
                            'status': Status.WATCHING.value}

        return element_info


class SeriesList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    current_season = db.Column(db.Integer, nullable=False)
    last_episode_watched = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    favorite = db.Column(db.Boolean)
    score = db.Column(db.Float)

    @staticmethod
    def get_series_info(user_id):
        element_data = db.session.query(Series, SeriesList, func.group_concat(SeriesGenre.genre.distinct()),
                                        func.group_concat(SeriesNetwork.network.distinct()),
                                        func.group_concat(SeriesEpisodesPerSeason.season.distinct()),
                                        func.group_concat(SeriesActors.name.distinct()),
                                        func.group_concat(SeriesEpisodesPerSeason.episodes)) \
            .join(SeriesList, SeriesList.series_id == Series.id) \
            .join(SeriesGenre, SeriesGenre.series_id == Series.id) \
            .join(SeriesNetwork, SeriesNetwork.series_id == Series.id) \
            .join(SeriesActors, SeriesActors.series_id == Series.id) \
            .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.series_id == Series.id) \
            .filter(SeriesList.user_id == user_id).group_by(Series.id).order_by(Series.name.asc()).all()

        return element_data


class SeriesGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class SeriesEpisodesPerSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    episodes = db.Column(db.Integer, nullable=False)


class SeriesNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    network = db.Column(db.String(150), nullable=False)


class SeriesActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    name = db.Column(db.String(150))


# --- ANIME -------------------------------------------------------------------------------------------------------


class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
    first_air_date = db.Column(db.String(30))
    last_air_date = db.Column(db.String(30))
    next_episode_to_air = db.Column(db.String(30))
    season_to_air = db.Column(db.Integer, default=None)
    episode_to_air = db.Column(db.Integer, default=None)
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
    eps_per_season = db.relationship('AnimeEpisodesPerSeason', backref='anime', lazy=True)
    list_info = db.relationship('AnimeList', backref='anime', lazy='dynamic')
    networks = db.relationship('AnimeNetwork', backref='anime', lazy=True)

    def get_info(self):
        # Change first air time format
        if 'Unknown' not in self.first_air_date:
            first_air_date = datetime.strptime(self.first_air_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            first_air_date = 'Unknown'

        # Change last air time format
        if 'Unknown' not in self.last_air_date:
            last_air_date = datetime.strptime(self.last_air_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            last_air_date = 'Unknown'

        element_info = {"id": self.id,
                        "cover": 'anime_covers/{}'.format(self.image_cover),
                        "cover_path": 'anime_covers',
                        "name": self.original_name,
                        "original_name": self.name,
                        "first_air_date": first_air_date,
                        "last_air_date": last_air_date,
                        "created_by": self.created_by,
                        "episode_duration": self.episode_duration,
                        "homepage": self.homepage,
                        "in_production": self.in_production,
                        "origin_country": self.origin_country,
                        "total_seasons": self.total_seasons,
                        "total_episodes": self.total_episodes,
                        "prod_status": self.status,
                        "vote_average": self.vote_average,
                        "vote_count": self.vote_count,
                        "synopsis": self.synopsis,
                        "popularity": self.popularity,
                        "media_type": 'Anime',
                        "lock_status": self.lock_status,
                        "eps_per_season": [r.episodes for r in self.eps_per_season],
                        "actors": ', '.join([r.name for r in self.actors]),
                        "genres": ', '.join([r.genre for r in self.genres]),
                        "networks": ', '.join([r.network for r in self.networks])}

        return element_info

    def get_same_genres(self):
        if len([r.genre for r in self.genres]) > 2:
            genres_list = [r.genre for r in self.genres][:2]
            genre_str = ','.join([g for g in genres_list])
        else:
            genres_list = [r.genre for r in self.genres]
            genre_str = ','.join([g for g in genres_list])

        same_genres = db.session.query(Anime, AnimeGenre) \
            .join(Anime, Anime.id == AnimeGenre.anime_id) \
            .filter(AnimeGenre.genre.in_(genres_list), AnimeGenre.anime_id != self.id) \
            .group_by(AnimeGenre.anime_id) \
            .having(func.group_concat(AnimeGenre.genre.distinct()) == genre_str).limit(8).all()

        return same_genres

    def in_follows_lists(self, user_id):
        in_follows_lists = db.session.query(User, AnimeList, followers) \
            .join(User, User.id == followers.c.followed_id) \
            .join(AnimeList, AnimeList.user_id == followers.c.followed_id) \
            .filter(followers.c.follower_id == user_id, AnimeList.anime_id == self.id).all()

        return in_follows_lists

    def in_user_list(self, user_id):
        in_user_list = self.list_info.filter_by(user_id=user_id).first()

        if in_user_list:
            element_info = {'in_user_list': True,
                            'last_episode_watched': in_user_list.last_episode_watched,
                            'current_season': in_user_list.current_season,
                            'score': in_user_list.score,
                            'favorite': in_user_list.favorite,
                            'status': in_user_list.status.value}
        else:
            element_info = {'last_episode_watched': 1,
                            'current_season': 1,
                            'score': 0,
                            'favorite': False,
                            'status': Status.WATCHING.value}

        return element_info


class AnimeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    current_season = db.Column(db.Integer, nullable=False)
    last_episode_watched = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    favorite = db.Column(db.Boolean)
    score = db.Column(db.Float)

    @staticmethod
    def get_anime_info(user_id):
        element_data = db.session.query(Anime, AnimeList, func.group_concat(AnimeGenre.genre.distinct()),
                                        func.group_concat(AnimeNetwork.network.distinct()),
                                        func.group_concat(AnimeEpisodesPerSeason.season.distinct()),
                                        func.group_concat(AnimeActors.name.distinct()),
                                        func.group_concat(AnimeEpisodesPerSeason.episodes)) \
            .join(AnimeList, AnimeList.anime_id == Anime.id) \
            .join(AnimeGenre, AnimeGenre.anime_id == Anime.id) \
            .join(AnimeNetwork, AnimeNetwork.anime_id == Anime.id) \
            .join(AnimeActors, AnimeActors.anime_id == Anime.id) \
            .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.anime_id == Anime.id) \
            .filter(AnimeList.user_id == user_id).group_by(Anime.id).order_by(Anime.name.asc()).all()

        return element_data


class AnimeEpisodesPerSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    episodes = db.Column(db.Integer, nullable=False)


class AnimeGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class AnimeNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    network = db.Column(db.String(150), nullable=False)


class AnimeActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    name = db.Column(db.String(150))


# --- MOVIES -------------------------------------------------------------------------------------------------------


class MoviesCollections(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('movies.collection_id'), nullable=False)
    parts = db.Column(db.Integer)
    name = db.Column(db.String(100))
    movies_names = db.Column(db.String(500))
    releases_dates = db.Column(db.String(500))
    poster = db.Column(db.String(100))
    overview = db.Column(db.String(100))

    @staticmethod
    def get_collection_movies(user_id):
        collection_movie = db.session.query(Movies, MoviesList, MoviesCollections,
                                            func.count(MoviesCollections.collection_id)) \
            .join(MoviesList, MoviesList.movies_id == Movies.id) \
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

    def get_info(self):
        # Change release date format
        release_date = self.release_date
        if 'Unknown' not in release_date:
            release_date = datetime.strptime(release_date, '%Y-%m-%d').strftime("%d %b %Y")
        else:
            release_date = 'Unknown'

        if self.original_language == 'ja':
            name = self.original_name
            original_name = self.name
        elif self.original_name != self.name:
            name = self.name
            original_name = self.original_name
        else:
            name = None
            original_name = self.original_name

        element_info = {"id": self.id,
                        "cover": 'movies_covers/{}'.format(self.image_cover),
                        "cover_path": 'movies_covers',
                        "name": name,
                        "original_name": original_name,
                        "director": self.director_name,
                        "release_date": release_date,
                        "homepage": self.homepage,
                        "runtime": self.runtime,
                        "budget": self.budget,
                        "revenue": self.revenue,
                        "tagline": self.tagline,
                        "original_language": self.original_language,
                        "vote_average": self.vote_average,
                        "vote_count": self.vote_count,
                        "synopsis": self.synopsis,
                        "popularity": self.popularity,
                        "media_type": 'Movies',
                        "lock_status": self.lock_status,
                        "actors": ', '.join([r.name for r in self.actors]),
                        "genres": ', '.join([r.genre for r in self.genres]),
                        "collection_data": self.collection_movies}

        return element_info

    def get_same_genres(self):
        if len([r.genre for r in self.genres]) > 2:
            genres_list = [r.genre for r in self.genres][:2]
            genre_str = ','.join([g for g in genres_list])
        else:
            genres_list = [r.genre for r in self.genres]
            genre_str = ','.join([g for g in genres_list])

        same_genres = db.session.query(Movies, MoviesGenre) \
            .join(Movies, Movies.id == MoviesGenre.movies_id) \
            .filter(MoviesGenre.genre.in_(genres_list), MoviesGenre.movies_id != self.id) \
            .group_by(MoviesGenre.movies_id) \
            .having(func.group_concat(MoviesGenre.genre.distinct()) == genre_str).limit(8).all()

        return same_genres

    def in_follows_lists(self, user_id):
        in_follows_lists = db.session.query(User, MoviesList, followers) \
            .join(User, User.id == followers.c.followed_id) \
            .join(AnimeList, MoviesList.user_id == followers.c.followed_id) \
            .filter(followers.c.follower_id == user_id, MoviesList.movies_id == self.id).all()

        return in_follows_lists

    def in_user_list(self, user_id):
        in_user_list = self.list_info.filter_by(user_id=user_id).first()

        if in_user_list:
            element_info = {'in_user_list': True,
                            'score': in_user_list.score,
                            'favorite': in_user_list.favorite,
                            'status': in_user_list.status.value}
        else:
            element_info = {'score': 0,
                            'favorite': False,
                            'status': Status.WATCHING.value}

        return element_info


class MoviesList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    favorite = db.Column(db.Boolean)
    score = db.Column(db.Float)

    @staticmethod
    def get_movies_info(user_id):
        element_data = db.session.query(Movies, MoviesList, func.group_concat(MoviesGenre.genre.distinct()),
                                        func.group_concat(MoviesActors.name.distinct())) \
            .join(MoviesList, MoviesList.movies_id == Movies.id) \
            .join(MoviesGenre, MoviesGenre.movies_id == Movies.id) \
            .join(MoviesActors, MoviesActors.movies_id == Movies.id) \
            .filter(MoviesList.user_id == user_id).group_by(Movies.id).order_by(Movies.name.asc()).all()
        return element_data


class MoviesGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class MoviesActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
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


class Notifications(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    media_type = db.Column(db.String(50))
    media_id = db.Column(db.Integer)
    media_name = db.Column(db.String(100))
    release_date = db.Column(db.String(30))
    season = db.Column(db.Integer)
    episode = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
