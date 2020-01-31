import os
import platform

from flask import Blueprint
from datetime import datetime
from sqlalchemy import func, text
from MyLists import app, db, bcrypt
from MyLists.admin.admin_views import User
from MyLists.medialists.API_data import ApiData
from flask_login import current_user, login_required
from flask import render_template, url_for, flash, redirect, request, abort
from MyLists.main.functions import refresh_db_badges, add_collections_movies, add_badges_to_db, get_badges, \
    get_level_and_grade, get_knowledge_grade, get_trending_data, compute_media_time_spent
from MyLists.models import Series, SeriesList, SeriesEpisodesPerSeason, Status, ListType, SeriesGenre, Anime, \
    AnimeList, AnimeEpisodesPerSeason, AnimeGenre, Movies, MoviesGenre, MoviesList, MoviesActors, SeriesActors, \
    AnimeActors, MoviesCollections


bp = Blueprint('main', __name__)


@app.before_first_request
def create_user():
    db.create_all()
    if User.query.filter_by(id='1').first() is None:
        admin = User(username='admin',
                     email='admin@admin.com',
                     password=bcrypt.generate_password_hash("password").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(admin)
        add_badges_to_db()
    if User.query.filter_by(id='2').first() is None:
        admin = User(username='aaa',
                     email='aaa@aaa.com',
                     password=bcrypt.generate_password_hash("a").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(admin)
    refresh_db_badges()
    db.session.commit()
    add_collections_movies()
    compute_media_time_spent(ListType.SERIES)
    compute_media_time_spent(ListType.ANIME)
    compute_media_time_spent(ListType.MOVIES)


@app.route("/badges/<user_name>", methods=['GET', 'POST'])
@login_required
def badges(user_name):
    user = User.query.filter_by(username=user_name).first()

    # No account with this username and protection of the admin account
    if user is None or user.id == 1 and current_user.id != 1:
        abort(404)

    # Check if the account is private or in the follow list
    if current_user.id == user.id or current_user.id == 1:
        pass
    elif user.private and current_user.is_following(user) is False:
        abort(404)

    user_badges = get_badges(user.id)[0]
    return render_template('badges.html',
                           title="{}'s badges".format(user_name),
                           user_badges=user_badges)


@app.route("/level_grade_data", methods=['GET'])
@login_required
def level_grade_data():
    all_ranks_list = []
    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\\csv_data\\levels_ranks.csv")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/csv_data/levels_ranks.csv")
    with open(path, "r") as fp:
        for line in fp:
            all_ranks_list.append(line.split(";"))

    all_ranks_list.pop(0)

    i, low, incr = [0, 0, 0]
    data = []
    while True:
        rank = all_ranks_list[i][2]
        if rank == 'ReachRank49':
            data.append(["ReachRank49", "Inheritor", [147, "+"], [(20*low)*(1+low), "+"],
                         [int(((20*low)*(1+low))/60), "+"]])
            break
        for j in range(i, len(all_ranks_list)):
            if str(rank) == all_ranks_list[j][2]:
                incr += 1
            else:
                data.append([rank, all_ranks_list[j-1][3], [low, incr-1],
                             [(20*low)*(1+low), ((20*incr)*(1+incr))-1],
                             [int(((20*low)*(1+low))/60), int((((20*incr)*(1+incr))-1)/60)]])
                i = j
                low = incr
                break

    return render_template('level_grade_data.html',
                           title='Level grade data',
                           data=data)


@app.route("/knowledge_grade_data", methods=['GET'])
@login_required
def knowledge_grade_data():
    all_knowledge_ranks_list = []
    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\\csv_data\\knowledge_ranks.csv")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/csv_data/knowledge_ranks.csv")
    with open(path, "r") as fp:
        for line in fp:
            all_knowledge_ranks_list.append(line.split(";"))

    i, low, incr = [1, 1, 1]
    data = []
    while True:
        rank = all_knowledge_ranks_list[i][1]
        if i == 346:
            data.append(["Knowledge_Emperor_Grade_4", "Knowledge Emperor Grade 4", [345, "+"]])
            break
        for j in range(i, len(all_knowledge_ranks_list)):
            if str(rank) == all_knowledge_ranks_list[j][1]:
                incr += 1
            else:
                data.append([rank, all_knowledge_ranks_list[j - 1][2], [low-1, incr-2]])
                i = j
                low = incr
                break

    return render_template('knowledge_grade_data.html',
                           title='Knowledge grade data',
                           data=data)


@app.route("/hall_of_fame", methods=['GET'])
@login_required
def hall_of_fame():
    users = User.query.filter(User.id >= "2", User.active == True).order_by(User.username.asc()).all()

    # Get the follows of the current user
    follows_list = []
    for follows in current_user.followed.all():
        follows_list.append(follows.id)

    all_users_data = []
    for user in users:
        user_data = {"id": user.id,
                     "username": user.username,
                     "profile_picture": user.image_file}

        series_level = get_level_and_grade(user.time_spent_series)
        user_data["series_level"] = series_level["level"]
        user_data["series_percent"] = series_level["level_percent"]
        user_data["series_grade_id"] = series_level["grade_id"]
        user_data["series_grade_title"] = series_level["grade_title"]

        anime_level = get_level_and_grade(user.time_spent_anime)
        user_data["anime_level"] = anime_level["level"]
        user_data["anime_percent"] = anime_level["level_percent"]
        user_data["anime_grade_id"] = anime_level["grade_id"]
        user_data["anime_grade_title"] = anime_level["grade_title"]

        movies_level = get_level_and_grade(user.time_spent_movies)
        user_data["movies_level"] = movies_level["level"]
        user_data["movies_percent"] = movies_level["level_percent"]
        user_data["movies_grade_id"] = movies_level["grade_id"]
        user_data["movies_grade_title"] = movies_level["grade_title"]

        knowledge_level = int(series_level["level"] + anime_level["level"] + movies_level["level"])
        knowledge_grade = get_knowledge_grade(knowledge_level)
        user_data["knowledge_level"] = knowledge_level
        user_data["knowledge_grade_id"] = knowledge_grade["grade_id"]
        user_data["knowledge_grade_title"] = knowledge_grade["grade_title"]

        if user.id in follows_list:
            user_data["isfollowing"] = True
        else:
            user_data["isfollowing"] = False

        if user.id == current_user.id:
            user_data["isprivate"] = False
            user_data["iscurrentuser"] = True
        else:
            user_data["isprivate"] = user.private
            user_data["iscurrentuser"] = False

        all_users_data.append(user_data)

    return render_template("hall_of_fame.html",
                           title='Hall of Fame',
                           all_data=all_users_data)


@app.route("/global_stats", methods=['GET'])
@login_required
def global_stats():
    # Total time spent for each media
    times_spent = db.session.query(User, func.sum(User.time_spent_series), func.sum(User.time_spent_anime),
                                   func.sum(User.time_spent_movies)).filter(User.id >= '2', User.active == True).all()

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
    for i in range(5):
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


@app.route("/current_trends", methods=['GET'])
@login_required
def current_trends():
    # Recover the trending media data from the API
    trending_data = ApiData().get_trending_media()

    if trending_data is None:
        flash('The current trends are not available right now, please try again later', 'warning')
        return redirect(url_for('account', user_name=current_user.username))

    series_trends = get_trending_data(trending_data[0], ListType.SERIES)
    anime_trends = get_trending_data(trending_data[1], ListType.ANIME)
    movies_trends = get_trending_data(trending_data[2], ListType.MOVIES)

    if series_trends is None or anime_trends is None or movies_trends is None:
        flash('The current trends are not available right now, please try again later', 'warning')
        return redirect(url_for('account', user_name=current_user.username))

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


@app.route("/movies_collection", methods=['GET'])
@login_required
def movies_collection():
    collection_movie = db.session.query(Movies, MoviesList, MoviesCollections,
                                        func.count(MoviesCollections.collection_id)) \
        .join(MoviesList, MoviesList.movies_id == Movies.id) \
        .join(MoviesCollections, MoviesCollections.collection_id == Movies.collection_id) \
        .filter(Movies.collection_id is not None, MoviesList.user_id == current_user.id,
                MoviesList.status != Status.PLAN_TO_WATCH).group_by(Movies.collection_id).all()

    completed_collections = []
    ongoing_collections = []
    for movie in collection_movie:
        movie_data = {"name": movie[2].name,
                      "total": movie[2].parts,
                      "parts": movie[3],
                      "overview": movie[2].overview,
                      "poster": '/static/covers/movies_collection_covers/' + movie[2].poster}

        if movie_data["total"] == movie_data["parts"]:
            movie_data["completed"] = True
            completed_collections.append(movie_data)
        else:
            movie_data["completed"] = False
            ongoing_collections.append(movie_data)

    completed_collections.sort(key=lambda x: (x['parts']), reverse=True)
    ongoing_collections.sort(key=lambda x: (x['parts'], x['total']), reverse=True)

    return render_template('movies_collection.html',
                           title='Movies collection',
                           completed_collections=completed_collections,
                           ongoing_collections=ongoing_collections,
                           length_completed=len(completed_collections),
                           length_ongoing=len(ongoing_collections))


@app.route("/follow_status", methods=['POST'])
@login_required
def follow_status():
    try:
        json_data = request.get_json()
        follow_id = int(json_data['follow_id'])
        status = json_data['follow_status']
    except:
        abort(400)

    # Check if the follow ID exist in the User database and status is boolean
    user = User.query.filter_by(id=follow_id).first()
    if user is None or type(status) is not bool:
        abort(400)

    # Check the status
    if status is True:
        current_user.add_follow(user)
        db.session.commit()
        app.logger.info('[{}] Follow the user with ID {}'.format(current_user.id, follow_id))
    else:
        current_user.remove_follow(user)
        db.session.commit()
        app.logger.info('[{}] Follow with ID {} unfollowed'.format(current_user.id, follow_id))

    return '', 204
