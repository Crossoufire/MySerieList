import json
from flask import Blueprint
from datetime import datetime
from MyLists import db, bcrypt, app
from MyLists.API_data import ApiData
from flask_login import login_required, current_user
from MyLists.general.trending_data import TrendingData
from flask import render_template, flash, request, abort
from MyLists.models import User, RoleType, MyListsStats, compute_media_time_spent
from MyLists.general.functions import add_badges_to_db, add_ranks_to_db, add_frames_to_db, refresh_db_frames, \
    refresh_db_badges, refresh_db_ranks, correct_orphan_media

bp = Blueprint('general', __name__)


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
                      role=RoleType.ADMIN)
        manager1 = User(username='manager',
                        email='manager@manager.com',
                        password=bcrypt.generate_password_hash("password").decode('utf-8'),
                        active=True,
                        registered_on=datetime.utcnow(),
                        activated_on=datetime.utcnow(),
                        role=RoleType.MANAGER)
        user1 = User(username='user',
                     email='user@user.com',
                     password=bcrypt.generate_password_hash("password").decode('utf-8'),
                     active=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(admin1)
        db.session.add(manager1)
        db.session.add(user1)
        add_frames_to_db()
        add_badges_to_db()
        add_ranks_to_db()
    refresh_db_frames()
    refresh_db_badges()
    refresh_db_ranks()

    compute_media_time_spent()
    correct_orphan_media()
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
    all_stats = MyListsStats.query.order_by(MyListsStats.timestamp.desc()).first()

    nb_users = all_stats.nb_users
    nb_media = json.loads(all_stats.nb_media)
    total_time = json.loads(all_stats.total_time)
    top_media = json.loads(all_stats.top_media)
    top_genres = json.loads(all_stats.top_genres)
    top_actors = json.loads(all_stats.top_actors)
    top_directors = json.loads(all_stats.top_directors)
    top_dropped = json.loads(all_stats.top_dropped)
    total_episodes = json.loads(all_stats.total_episodes)
    total_seasons = json.loads(all_stats.total_seasons)
    total_movies = json.loads(all_stats.total_movies)

    return render_template("mylists_stats.html", title='MyLists stats', nb_users=nb_users, total_time=total_time,
                           nb_media=nb_media, top_media=top_media, top_genres=top_genres, top_actors=top_actors,
                           top_directors=top_directors, top_dropped=top_dropped, total_episodes=total_episodes,
                           total_movies=total_movies, total_seasons=total_seasons)


@bp.route("/current_trends", methods=['GET'])
@login_required
def current_trends():
    try:
        series_info = ApiData().get_trending_tv()
    except Exception as e:
        series_info = {'results': []}
        app.logger.error('[ERROR] - Getting the Series trending info: {}.'.format(e))
        flash('The current TV trends from TMDb are not available right now.', 'warning')

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
        flash('The current movies trends from TMDb are not available right now.', 'warning')

    series_results = TrendingData(series_info).get_trending_series()
    anime_results = TrendingData(anime_info).get_trending_anime()
    movies_results = TrendingData(movies_info).get_trending_movies()

    template = 'current_trends_pc.html'
    platform = str(request.user_agent.platform)
    if platform == "iphone" or platform == "android" or not platform or platform == 'None':
        template = 'current_trends_mobile.html'

    return render_template(template, title="Current trends", series_trends=series_results, anime_trends=anime_results,
                           movies_trends=movies_results)


@bp.route("/privacy_policy", methods=['GET'])
@login_required
def privacy_policy():
    return render_template('privacy_policy.html', title='Privacy policy')


@bp.route("/about", methods=['GET'])
@login_required
def about():
    return render_template('about.html', title='About')
