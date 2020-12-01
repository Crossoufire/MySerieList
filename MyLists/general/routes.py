from flask import Blueprint
from datetime import datetime
from MyLists import db, bcrypt, app
from MyLists.API_data import ApiData
from flask_login import login_required, current_user
from MyLists.general.trending_data import TrendingData
from flask import render_template, flash, request, abort
from MyLists.models import ListType, User, GlobalStats, RoleType
from MyLists.general.functions import compute_media_time_spent, add_badges_to_db, add_ranks_to_db, add_frames_to_db, \
    refresh_db_frames, refresh_db_badges, refresh_db_ranks, add_collections_movies, add_collections_id_to_movieslist

bp = Blueprint('general', __name__)


# noinspection PyArgumentList
@bp.before_app_first_request
def create_first_data():
    db.create_all()
    if User.query.filter_by(id='1').first() is None:
        admin1 = User(username='admin',
                      email='admin@admin.com',
                      password=bcrypt.generate_password_hash("password").decode('utf-8'),
                      active=True,
                      private=True,
                      registered_on=datetime.utcnow(),
                      activated_on=datetime.utcnow(),
                      role=RoleType.ADMIN,
                      oauth_id="a")
        manager1 = User(username='manager',
                        email='manager@manager.com',
                        password=bcrypt.generate_password_hash("password").decode('utf-8'),
                        active=True,
                        registered_on=datetime.utcnow(),
                        activated_on=datetime.utcnow(),
                        role=RoleType.MANAGER,
                        oauth_id="b")
        user1 = User(username='user',
                     email='user@user.com',
                     password=bcrypt.generate_password_hash("password").decode('utf-8'),
                     active=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow(),
                     oauth_id="c")
        db.session.add(admin1)
        db.session.add(manager1)
        db.session.add(user1)
        add_frames_to_db()
        add_badges_to_db()
        add_ranks_to_db()
    refresh_db_frames()
    refresh_db_badges()
    refresh_db_ranks()
    compute_media_time_spent(ListType.SERIES)
    compute_media_time_spent(ListType.ANIME)
    compute_media_time_spent(ListType.MOVIES)
    compute_media_time_spent(ListType.GAMES)
    # add_collections_movies()
    # add_hltb_time()
    # add_manual_games()
    db.session.commit()


@bp.route("/admin", methods=['GET'])
@login_required
def admin():
    if current_user.role != RoleType.ADMIN:
        abort(403)
    return render_template('admin/index.html')


@bp.route("/mylists_stats", methods=['GET'])
@login_required
def mylists_stats():
    stats = GlobalStats()

    times_spent = stats.get_total_time_spent()

    if times_spent[0]:
        total_time = {"total": sum(times_spent[0]), "series": int(times_spent[0][0]/60),
                      "anime": int(times_spent[0][1]/60), "movies": int(times_spent[0][2]/60),
                      "games": int(times_spent[0][3]/60)}
    else:
        total_time = {"total": 0, "series": 0, "anime": 0, "movies": 0, "games": 0}

    def create_dict(data):
        series_list, anime_list, movies_list, games_list = [], [], [], []
        for i in range(5):
            try:
                series_list.append({"info": data[0][i][0], "quantity": data[0][i][2]})
            except:
                series_list.append({"info": "-", "quantity": "-"})
            try:
                anime_list.append({"info": data[1][i][0], "quantity": data[1][i][2]})
            except:
                anime_list.append({"info": "-", "quantity": "-"})
            try:
                movies_list.append({"info": data[2][i][0], "quantity": data[2][i][2]})
            except:
                movies_list.append({"info": "-", "quantity": "-"})
            try:
                games_list.append({"info": data[i][0], "quantity": data[i][2]})
            except:
                games_list.append({"info": "-", "quantity": "-"})

        return {'series': series_list, 'anime': anime_list, 'movies': movies_list, 'games': games_list}

    top_media = stats.get_top_media()
    most_present_media = create_dict(top_media)

    media_genres = stats.get_top_genres()
    most_genres_media = create_dict(media_genres)

    media_actors = stats.get_top_actors()
    most_actors_media = create_dict(media_actors)

    media_dropped = stats.get_top_dropped()
    top_dropped_media = create_dict(media_dropped)

    games_companies = stats.get_top_companies()
    top_companies_games = create_dict(games_companies)

    total_media_eps_seas = stats.get_total_eps_seasons()
    total_seasons_media = {"series": total_media_eps_seas[0][0][1], "anime": total_media_eps_seas[1][0][1]}
    total_episodes_media = {"series": total_media_eps_seas[0][0][0], "anime": total_media_eps_seas[1][0][0]}

    return render_template("mylists_stats.html",
                           title='MyLists Stats',
                           total_time=total_time,
                           most_present_media=most_present_media,
                           most_actors_media=most_actors_media,
                           top_dropped_media=top_dropped_media,
                           total_seasons_media=total_seasons_media,
                           total_episodes_media=total_episodes_media,
                           most_genres_media=most_genres_media,
                           top_companies_games=top_companies_games)


@bp.route("/current_trends", methods=['GET'])
@login_required
def current_trends():
    try:
        series_info = ApiData().get_trending_tv()
    except Exception as e:
        series_info = {'results': []}
        app.logger.error('[ERROR] - Getting the Series trending info: {}.'.format(e))
        flash('The current TV trends from TMDB are not available right now.', 'warning')

    try:
        anime_info = ApiData().get_trending_anime()
    except Exception as e:
        anime_info = {'top': []}
        app.logger.error('[ERROR] - Getting the anime trending info: {}.'.format(e))
        flash('The current anime trends from Jikan are not available right now.', 'warning')

    try:
        movies_info = ApiData().get_trending_movies()
    except Exception as e:
        movies_info = {'results': []}
        app.logger.error('[ERROR] - Getting the movies trending info: {}.'.format(e))
        flash('The current movies trends from TMDB are not available right now.', 'warning')

    series_results = TrendingData(series_info).get_trending_series()
    anime_results = TrendingData(anime_info).get_trending_anime()
    movies_results = TrendingData(movies_info).get_trending_movies()

    template = 'current_trends_pc.html'
    platform = str(request.user_agent.platform)
    if platform == "iphone" or platform == "android" or not platform or platform == 'None':
        template = 'current_trends_mobile.html'

    return render_template(template,
                           title="Current trends",
                           series_trends=series_results,
                           anime_trends=anime_results,
                           movies_trends=movies_results)


@bp.route("/privacy_policy", methods=['GET'])
@login_required
def privacy_policy():
    return render_template('privacy_policy.html', title='Privacy Policy of MyLists')


@bp.route("/about", methods=['GET'])
@login_required
def about():
    return render_template('about.html', title='About MyLists')


@bp.route('/service-worker.js')
def service_worker():
    return app.send_static_file('service-worker.js')
