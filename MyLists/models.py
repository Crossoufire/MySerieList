from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from MyLists import db, login_manager, app
from flask_login import UserMixin
import enum


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
    SERIES = "Series"
    ANIME = "Anime"
    MOVIES = 'Movies'


class HomePage(enum.Enum):
    ACCOUNT = "account"
    HALL_OF_FAME = "hall_of_fame"
    MYSERIESLIST = "myserieslist"
    MYANIMELIST = "myanimelist"
    MYMOVIESLIST = "mymovieslist"


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
    biography = db.Column(db.Text)
    transition_email = db.Column(db.String(120))
    activated_on = db.Column(db.DateTime)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_register_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).decode('utf-8')

    def get_email_update_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).decode('utf-8')

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
    old_status = db.Column(db.Enum(Status))
    new_status = db.Column(db.Enum(Status))
    old_season = db.Column(db.Integer)
    new_season = db.Column(db.Integer)
    old_episode = db.Column(db.Integer)
    new_episode = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False)


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    follow_id = db.Column(db.Integer, db.ForeignKey('user.id'))


######################################################## SERIES ########################################################


class Series(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
    first_air_date = db.Column(db.String(30))
    last_air_date = db.Column(db.String(30))
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


class SeriesList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    current_season = db.Column(db.Integer, nullable=False)
    last_episode_watched = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    score = db.Column(db.Float)


class SeriesEpisodesPerSeason(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    season = db.Column(db.Integer, nullable=False)
    episodes = db.Column(db.Integer, nullable=False)


class SeriesGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class SeriesNetwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    network = db.Column(db.String(150), nullable=False)


class SeriesActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    series_id = db.Column(db.Integer, db.ForeignKey('series.id'), nullable=False)
    name = db.Column(db.String(150))


######################################################## ANIME #########################################################


class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
    first_air_date = db.Column(db.String(30))
    last_air_date = db.Column(db.String(30))
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


class AnimeList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)
    current_season = db.Column(db.Integer, nullable=False)
    last_episode_watched = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    score = db.Column(db.Float)


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


######################################################## MOVIES ########################################################


class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    original_name = db.Column(db.String(50), nullable=False)
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


class MoviesList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    status = db.Column(db.Enum(Status), nullable=False)
    score = db.Column(db.Float)


class MoviesGenre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, nullable=False)


class MoviesProd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    production_company = db.Column(db.String(150), nullable=False)


class MoviesActors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movies_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    name = db.Column(db.String(150))


######################################################## ACHIEVEMENTS ##################################################


class Achievements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    media = db.Column(db.String(10), nullable=False)
    threshold = db.Column(db.Integer, nullable=False)
    image_id = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100))