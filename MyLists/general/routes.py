from flask import Blueprint
from datetime import datetime
from MyLists import db, bcrypt, app
from sqlalchemy import func, text
from MyLists.API_data import ApiData
from flask_login import current_user, login_required
from flask import render_template, url_for, flash, redirect, request
from MyLists.general.functions import compute_media_time_spent, add_badges_to_db, get_trending_data, add_ranks_to_db, \
    add_frames_to_db, refresh_db_frames, refresh_db_badges, refresh_db_ranks
from MyLists.models import Series, SeriesList, SeriesEpisodesPerSeason, Status, ListType, SeriesGenre, Anime, User, \
    AnimeList, AnimeEpisodesPerSeason, AnimeGenre, MoviesGenre, MoviesList, MoviesActors, SeriesActors, Movies, \
    AnimeActors


bp = Blueprint('general', __name__)


@bp.before_app_first_request
def create_user():
    db.create_all()
    if User.query.filter_by(id='1').first() is None:
        # noinspection PyArgumentList
        new_admin = User(username='admin',
                         email='admin@admin.com',
                         password=bcrypt.generate_password_hash("password").decode('utf-8'),
                         image_file='default.jpg',
                         active=True,
                         private=True,
                         registered_on=datetime.utcnow(),
                         activated_on=datetime.utcnow())
        db.session.add(new_admin)
        add_frames_to_db()
        add_badges_to_db()
        add_ranks_to_db()
    refresh_db_frames()
    refresh_db_badges()
    refresh_db_ranks()
    db.session.commit()
    compute_media_time_spent(ListType.SERIES)
    compute_media_time_spent(ListType.ANIME)
    compute_media_time_spent(ListType.MOVIES)


@bp.route("/admin", methods=['GET'])
@login_required
def admin():
    return render_template('admin/index.html')


@bp.route("/global_stats", methods=['GET'])
@login_required
def global_stats():
    # Total time spent for each media
    times_spent = db.session.query(User, func.sum(User.time_spent_series), func.sum(User.time_spent_anime),
                                   func.sum(User.time_spent_movies))\
        .filter(User.id >= '2', User.active == True).all()

    if times_spent[0][0]:
        total_time = {"total": int((times_spent[0][1] / 60) + (times_spent[0][2] / 60) + (times_spent[0][3] / 60)),
                      "series": int(times_spent[0][1] / 60),
                      "anime": int(times_spent[0][2] / 60),
                      "movies": int(times_spent[0][3] / 60)}
    else:
        total_time = {"total": 0, "series": 0, "anime": 0, "movies": 0}

    # Top media in users' lists
    top_series = db.session.query(Series, SeriesList, func.count(SeriesList.series_id == Series.id).label("count"))\
        .join(SeriesList, SeriesList.series_id == Series.id).group_by(SeriesList.series_id)\
        .filter(SeriesList.user_id >= '2').order_by(text("count desc")).limit(5).all()
    top_anime = db.session.query(Anime, AnimeList, func.count(AnimeList.anime_id == Anime.id).label("count"))\
        .join(AnimeList, AnimeList.anime_id == Anime.id).group_by(AnimeList.anime_id)\
        .filter(AnimeList.user_id >= '2').order_by(text("count desc")).limit(5).all()
    top_movies = db.session.query(Movies, MoviesList, func.count(MoviesList.movies_id == Movies.id).label("count"))\
        .join(MoviesList, MoviesList.movies_id == Movies.id).group_by(MoviesList.movies_id)\
        .filter(MoviesList.user_id >= '2').order_by(text("count desc")).limit(5).all()

    top_all_series, top_all_anime, top_all_movies = [], [], []
    for i in range(0, 5):
        try:
            tmp_series = {"name": top_series[i][0].name, "quantity": top_series[i][2]}
        except:
            tmp_series = {"name": "-", "quantity": "-"}
        try:
            tmp_anime = {"name": top_anime[i][0].name, "quantity": top_anime[i][2]}
        except:
            tmp_anime = {"name": "-", "quantity": "-"}
        try:
            tmp_movies = {"name": top_movies[i][0].name, "quantity": top_movies[i][2]}
        except:
            tmp_movies = {"name": "-", "quantity": "-"}

        top_all_series.append(tmp_series)
        top_all_anime.append(tmp_anime)
        top_all_movies.append(tmp_movies)

    most_present_media = {"series": top_all_series,
                          "anime": top_all_anime,
                          "movies": top_all_movies}

    # Top genre in users' lists
    series_genres = db.session.query(SeriesList, SeriesGenre, func.count(SeriesGenre.genre).label('count'))\
        .join(SeriesGenre, SeriesGenre.series_id == SeriesList.series_id)\
        .group_by(SeriesGenre.genre).filter(SeriesList.user_id >= '2').order_by(text('count desc')).limit(5).all()
    anime_genres = db.session.query(AnimeList, AnimeGenre, func.count(AnimeGenre.genre).label('count'))\
        .join(AnimeGenre, AnimeGenre.anime_id == AnimeList.anime_id)\
        .group_by(AnimeGenre.genre).filter(AnimeList.user_id >= '2').order_by(text('count desc')).limit(5).all()
    movies_genres = db.session.query(MoviesList, MoviesGenre, func.count(MoviesGenre.genre).label('count'))\
        .join(MoviesGenre, MoviesGenre.movies_id == MoviesList.movies_id)\
        .group_by(MoviesGenre.genre).filter(MoviesList.user_id >= '2').order_by(text('count desc')).limit(5).all()

    all_series_genres, all_anime_genres, all_movies_genres = [], [], []
    for i in range(5):
        try:
            tmp_series = {"genre": series_genres[i][1].genre, "quantity": series_genres[i][2]}
        except:
            tmp_series = {"genre": "-", "quantity": "-"}
        try:
            tmp_anime = {"genre": anime_genres[i][1].genre, "quantity": anime_genres[i][2]}
        except:
            tmp_anime = {"genre": "-", "quantity": "-"}
        try:
            tmp_movies = {"genre": movies_genres[i][1].genre, "quantity": movies_genres[i][2]}
        except:
            tmp_movies = {"genre": "-", "quantity": "-"}

        all_series_genres.append(tmp_series)
        all_anime_genres.append(tmp_anime)
        all_movies_genres.append(tmp_movies)

    most_genres_media = {"series": all_series_genres,
                         "anime": all_anime_genres,
                         "movies": all_movies_genres}

    # Top actors in the users' lists
    series_actors = db.session.query(SeriesList, SeriesActors, func.count(SeriesActors.name).label('count'))\
        .join(SeriesActors, SeriesActors.series_id == SeriesList.series_id)\
        .filter(SeriesActors.name != "Unknown").group_by(SeriesActors.name).filter(SeriesList.user_id >= '2')\
        .order_by(text('count desc')).limit(5).all()
    anime_actors = db.session.query(AnimeList, AnimeActors, func.count(AnimeActors.name).label('count'))\
        .join(AnimeActors, AnimeActors.anime_id == AnimeList.anime_id)\
        .filter(AnimeActors.name != "Unknown").group_by(AnimeActors.name).filter(AnimeList.user_id >= '2')\
        .order_by(text('count desc')).limit(5).all()
    movies_actors = db.session.query(MoviesList, MoviesActors, func.count(MoviesActors.name).label('count'))\
        .join(MoviesActors, MoviesActors.movies_id == MoviesList.movies_id)\
        .filter(MoviesActors.name != "Unknown").group_by(MoviesActors.name).filter(MoviesList.user_id >= '2')\
        .order_by(text('count desc')).limit(5).all()

    all_series_actors, all_anime_actors, all_movies_actors = [], [], []
    for i in range(5):
        try:
            tmp_series = {"name": series_actors[i][1].name, "quantity": series_actors[i][2]}
        except:
            tmp_series = {"name": "-", "quantity": "-"}
        try:
            tmp_anime = {"name": anime_actors[i][1].name, "quantity": anime_actors[i][2]}
        except:
            tmp_anime = {"name": "-", "quantity": "-"}
        try:
            tmp_movies = {"name": movies_actors[i][1].name, "quantity": movies_actors[i][2]}
        except:
            tmp_movies = {"name": "-", "quantity": "-"}

        all_series_actors.append(tmp_series)
        all_anime_actors.append(tmp_anime)
        all_movies_actors.append(tmp_movies)

    most_actors_media = {"series": all_series_actors,
                         "anime": all_anime_actors,
                         "movies": all_movies_actors}

    # Top dropped media in the users' lists
    series_dropped = db.session.query(Series, SeriesList, func.count(SeriesList.series_id == Series.id).label('count'))\
        .join(SeriesList, SeriesList.series_id == Series.id).filter_by(status=Status.DROPPED)\
        .group_by(SeriesList.series_id).filter(SeriesList.user_id >= '2').order_by(text('count desc')).limit(5).all()
    anime_dropped = db.session.query(Anime, AnimeList, func.count(AnimeList.anime_id == Anime.id).label('count'))\
        .join(AnimeList, AnimeList.anime_id == Anime.id).filter_by(status=Status.DROPPED).group_by(AnimeList.anime_id)\
        .filter(AnimeList.user_id >= '2').order_by(text('count desc')).limit(5).all()

    top_series_dropped, top_anime_dropped = [], []
    for i in range(5):
        try:
            tmp_series = {"name": series_dropped[i][0].name, "quantity": series_dropped[i][2]}
        except:
            tmp_series = {"name": "-", "quantity": "-"}
        try:
            tmp_anime = {"name": anime_dropped[i][0].name, "quantity": anime_dropped[i][2]}
        except:
            tmp_anime = {"name": "-", "quantity": "-"}

        top_series_dropped.append(tmp_series)
        top_anime_dropped.append(tmp_anime)

    top_dropped_media = {"series": top_series_dropped,
                         "anime": top_anime_dropped}

    # Total number of seasons/episodes watched for the series and anime
    total_series_eps_seasons = db.session.query(SeriesList, SeriesEpisodesPerSeason,
                                                func.group_concat(SeriesEpisodesPerSeason.episodes))\
        .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.series_id == SeriesList.series_id)\
        .group_by(SeriesList.id).filter(SeriesList.user_id >= '2').all()
    total_anime_eps_seasons = db.session.query(AnimeList, AnimeEpisodesPerSeason,
                                               func.group_concat(AnimeEpisodesPerSeason.episodes))\
        .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.anime_id == AnimeList.anime_id)\
        .group_by(AnimeList.id).filter(AnimeList.user_id >= '2').all()

    total_series_seas_watched = 0
    total_series_eps_watched = 0
    for element in total_series_eps_seasons:
        if element[0].status != Status.PLAN_TO_WATCH:
            episodes = element[2].split(",")
            episodes = [int(x) for x in episodes]
            if episodes[int(element[0].current_season) - 1] == int(element[0].last_episode_watched):
                total_series_seas_watched += int(element[0].current_season)
            else:
                total_series_seas_watched += int(element[0].current_season) - 1
            for i in range(1, element[0].current_season):
                total_series_eps_watched += episodes[i - 1]
            total_series_eps_watched += element[0].last_episode_watched

    total_anime_seas_watched = 0
    total_anime_eps_watched = 0
    for element in total_anime_eps_seasons:
        if element[0].status != Status.PLAN_TO_WATCH:
            episodes = element[2].split(",")
            episodes = [int(x) for x in episodes]
            if episodes[int(element[0].current_season) - 1] == int(element[0].last_episode_watched):
                total_anime_seas_watched += int(element[0].current_season)
            else:
                total_anime_seas_watched += int(element[0].current_season) - 1
            for i in range(1, element[0].current_season):
                total_anime_eps_watched += episodes[i - 1]
            total_anime_eps_watched += element[0].last_episode_watched

    total_seasons_media = {"series": total_series_seas_watched,
                           "anime": total_anime_seas_watched}
    total_episodes_media = {"series": total_series_eps_watched,
                            "anime": total_anime_eps_watched}

    return render_template("global_stats.html",
                           title='Global Stats',
                           total_time=total_time,
                           most_present_media=most_present_media,
                           most_actors_media=most_actors_media,
                           top_dropped_media=top_dropped_media,
                           total_seasons_media=total_seasons_media,
                           total_episodes_media=total_episodes_media,
                           most_genres_media=most_genres_media)


@bp.route("/current_trends", methods=['GET'])
@login_required
def current_trends():
    series_trends, anime_trends, movies_trends = [], [], []

    try:
        series_data = ApiData().get_trending_media(ListType.SERIES, 'TMDB')
        series_trends = get_trending_data(series_data, ListType.SERIES)
    except Exception as e:
        app.logger.error('Error getting trending data for the TV shows: {} .'.format(e))
        flash('The current trends from TMDB TV shows are not available right now.', 'warning')

    try:
        anime_data = ApiData().get_trending_media(ListType.ANIME, 'Jikan')
        anime_trends = get_trending_data(anime_data, ListType.ANIME)
    except Exception as e:
        app.logger.error('Error getting trending data for the anime: {} .'.format(e))
        flash('The current trends from Jikan (Anime) are not available right now.', 'warning')

    try:
        movies_data = ApiData().get_trending_media(ListType.MOVIES, 'TMDB')
        movies_trends = get_trending_data(movies_data, ListType.MOVIES)
    except Exception as e:
        app.logger.error('Error getting trending data for the movies: {} .'.format(e))
        flash('The current trends from TMDB Movies are not available right now.', 'warning')

    platform = str(request.user_agent.platform)
    if platform == "iphone" or platform == "android" or platform is None or platform == 'None':
        template = 'current_trends_mobile.html'
    else:
        template = 'current_trends_pc.html'

    return render_template(template,
                           title="Current trends",
                           series_trends=series_trends,
                           anime_trends=anime_trends,
                           movies_trends=movies_trends)
