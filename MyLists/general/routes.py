from flask import Blueprint
from datetime import datetime
from MyLists import db, bcrypt, app
from MyLists.API_data import ApiData
from flask_login import login_required, current_user
from flask import render_template, url_for, flash, request, abort
from MyLists.general.functions import compute_media_time_spent, add_badges_to_db, add_ranks_to_db, add_frames_to_db, \
    refresh_db_frames, refresh_db_badges, refresh_db_ranks
from MyLists.models import Status, ListType, User, GlobalStats, RoleType

bp = Blueprint('general', __name__)


@bp.before_app_first_request
def create_user():
    db.create_all()
    if User.query.filter_by(id='1').first() is None:
        # noinspection PyArgumentList
        admin1 = User(username='admin',
                         email='admin@admin.com',
                         password=bcrypt.generate_password_hash("password").decode('utf-8'),
                         image_file='default.jpg',
                         active=True,
                         private=True,
                         registered_on=datetime.utcnow(),
                         activated_on=datetime.utcnow(),
                         role=RoleType.ADMIN)
        manager1 = User(username='manager',
                        email='manager@manager.com',
                        password=bcrypt.generate_password_hash("password").decode('utf-8'),
                        image_file='default.jpg',
                        active=True,
                        private=False,
                        registered_on=datetime.utcnow(),
                        activated_on=datetime.utcnow(),
                        role=RoleType.MANAGER)
        user1 = User(username='user',
                     email='user@user.com',
                     password=bcrypt.generate_password_hash("password").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow(),
                     role=RoleType.USER)
        db.session.add(admin1)
        db.session.add(manager1)
        db.session.add(user1)
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
    if current_user.role != RoleType.ADMIN:
        abort(403)
    return render_template('admin/index.html')


@bp.route("/global_stats", methods=['GET'])
@login_required
def global_stats():
    stats = GlobalStats()

    times_spent = stats.get_total_time_spent()
    if times_spent[0][0]:
        total_time = {"total": int((times_spent[0][1] / 60) + (times_spent[0][2] / 60) + (times_spent[0][3] / 60)),
                      "series": int(times_spent[0][1] / 60),
                      "anime": int(times_spent[0][2] / 60),
                      "movies": int(times_spent[0][3] / 60)}
    else:
        total_time = {"total": 0, "series": 0, "anime": 0, "movies": 0}

    top_series, top_anime, top_movies = stats.get_top_media()
    top_all_series, top_all_anime, top_all_movies = [], [], []
    for i in range(0, 5):
        try:
            top_all_series.append({"name": top_series[i][0].name, "quantity": top_series[i][2]})
        except:
            top_all_series.append({"name": "-", "quantity": "-"})
        try:
            top_all_anime.append({"name": top_anime[i][0].name, "quantity": top_anime[i][2]})
        except:
            top_all_anime.append({"name": "-", "quantity": "-"})
        try:
            top_all_movies.append({"name": top_movies[i][0].name, "quantity": top_movies[i][2]})
        except:
            top_all_movies.append({"name": "-", "quantity": "-"})

    most_present_media = {"series": top_all_series, "anime": top_all_anime, "movies": top_all_movies}

    series_genres, anime_genres, movies_genres = stats.get_top_genres()
    all_series_genres, all_anime_genres, all_movies_genres = [], [], []
    for i in range(5):
        try:
            all_series_genres.append({"genre": series_genres[i][1].genre, "quantity": series_genres[i][2]})
        except:
            all_series_genres.append({"genre": "-", "quantity": "-"})
        try:
            all_anime_genres.append({"genre": anime_genres[i][1].genre, "quantity": anime_genres[i][2]})
        except:
            all_anime_genres.append({"genre": "-", "quantity": "-"})
        try:
            all_movies_genres.append({"genre": movies_genres[i][1].genre, "quantity": movies_genres[i][2]})
        except:
            all_movies_genres.append({"genre": "-", "quantity": "-"})

    most_genres_media = {"series": all_series_genres, "anime": all_anime_genres, "movies": all_movies_genres}

    series_actors, anime_actors, movies_actors = stats.get_top_actors()
    all_series_actors, all_anime_actors, all_movies_actors = [], [], []
    for i in range(5):
        try:
            all_series_actors.append({"name": series_actors[i][1].name, "quantity": series_actors[i][2]})
        except:
            all_series_actors.append({"name": "-", "quantity": "-"})
        try:
            all_anime_actors.append({"name": anime_actors[i][1].name, "quantity": anime_actors[i][2]})
        except:
            all_anime_actors.append({"name": "-", "quantity": "-"})
        try:
            all_movies_actors.append({"name": movies_actors[i][1].name, "quantity": movies_actors[i][2]})
        except:
            all_movies_actors.append({"name": "-", "quantity": "-"})

    most_actors_media = {"series": all_series_actors, "anime": all_anime_actors, "movies": all_movies_actors}

    series_dropped, anime_dropped = stats.get_top_dropped()
    top_series_dropped, top_anime_dropped = [], []
    for i in range(5):
        try:
            top_series_dropped.append({"name": series_dropped[i][0].name, "quantity": series_dropped[i][2]})
        except:
            top_series_dropped.append({"name": "-", "quantity": "-"})
        try:
            top_anime_dropped.append({"name": anime_dropped[i][0].name, "quantity": anime_dropped[i][2]})
        except:
            top_anime_dropped.append({"name": "-", "quantity": "-"})

    top_dropped_media = {"series": top_series_dropped, "anime": top_anime_dropped}

    total_series_eps_seasons, total_anime_eps_seasons = stats.get_total_eps_seasons()
    total_series_seas_watched, total_series_eps_watched = 0, 0
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

    total_anime_seas_watched, total_anime_eps_watched = 0, 0
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

    total_seasons_media = {"series": total_series_seas_watched, "anime": total_anime_seas_watched}
    total_episodes_media = {"series": total_series_eps_watched, "anime": total_anime_eps_watched}

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
    try:
        tmdb_data_page_1, tmdb_data_page_2 = ApiData().get_trending_media('TMDB')
        tmdb_data = tmdb_data_page_1['results'] + tmdb_data_page_2['results']
    except Exception as e:
        app.logger.error('Error getting trending data for the TV shows: {} .'.format(e))
        flash('The current trends from TMDB are not available right now.', 'warning')
        tmdb_data = []

    try:
        anime_data = ApiData().get_trending_media('Jikan')
    except Exception as e:
        app.logger.error('Error getting trending data for the anime: {} .'.format(e))
        flash('The current trends from Jikan (Anime) are not available right now.', 'warning')
        anime_data = {'top': []}

    # Recover 12 results without peoples for series and movies
    series_results, movies_results = [], []
    for i, result in enumerate(tmdb_data):
        if len(series_results) >= 12:
            if result["media_type"] == 'tv':
                continue

        if len(movies_results) >= 12:
            if result["media_type"] == 'movie':
                continue

        if result.get('known_for_department'):
            continue

        media_data = {'name': result.get('original_title') or result.get('original_name'),
                      'first_air_date': result.get('first_air_date') or result.get('release_date'),
                      'overview': result.get('overview'),
                      'tmdb_id': result['id']}

        # Modify the overview if no data
        if media_data["overview"] == '':
            media_data['overview'] = "There is no overview available for this media."

        # Modify the first_air_date / release_date format
        if media_data["first_air_date"] == '':
            media_data["first_air_date"] = 'Not available'
        else:
            media_data["first_air_date"] = datetime.strptime(media_data["first_air_date"], '%Y-%m-%d')\
                .strftime("%d %b %Y")

        # Recover the poster_path or take a default image
        if result["poster_path"]:
            media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300", result["poster_path"])
        else:
            media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")

        # Put data in different lists in function of <media_type>
        if result['media_type'] == 'tv':
            media_data['tmdb_link'] = f"https://www.themoviedb.org/tv/{result['id']}"
            media_data['media_type'] = ListType.SERIES.value
            series_results.append(media_data)
        elif result['media_type'] == 'movie':
            media_data['tmdb_link'] = f"https://www.themoviedb.org/movie/{result['id']}"
            media_data['media_type'] = ListType.MOVIES.value
            if result['original_language'] == 'ja' and 16 in result['genre_ids']:
                media_data['name'] = result['title']
            movies_results.append(media_data)

    # Recover 12 results without peoples for anime
    anime_results = []
    for i, data in enumerate(anime_data['top']):
        if i == 12:
            break

        anime = {"name": data.get("title", "Unknown") or "Unknown"}

        media_cover_path = data.get("image_url") or None
        if media_cover_path:
            anime["poster_path"] = media_cover_path
        else:
            anime["poster_path"] = url_for('static', filename='covers/default.jpg')

        anime["first_air_date"] = data.get("start_date", 'Unknown') or "Unknown"
        anime["overview"] = "There is no overview from this API. " \
                            "You can check it on MyAnimeList by clicking on the title."
        anime["tmdb_link"] = data.get("url")
        anime_results.append(anime)

    platform = str(request.user_agent.platform)
    if platform == "iphone" or platform == "android" or platform is None or platform == 'None':
        template = 'current_trends_mobile.html'
    else:
        template = 'current_trends_pc.html'

    return render_template(template,
                           title="Current trends",
                           series_trends=series_results,
                           anime_trends=anime_results,
                           movies_trends=movies_results)
