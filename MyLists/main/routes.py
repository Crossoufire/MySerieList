from MyLists import db, app
from MyLists.API_data import ApiData
from MyLists.main.forms import EditMediaData
from flask_login import login_required, current_user
from flask import Blueprint, url_for, request, abort, render_template, flash, jsonify, redirect
from MyLists.main.functions import get_medialist_data, set_last_update, compute_time_spent, check_cat_type, \
    add_element_to_user, add_element_in_db, load_media_sheet, save_new_cover
from MyLists.models import User, Movies, MoviesActors, MoviesGenre, Series, SeriesGenre, SeriesList, \
    SeriesEpisodesPerSeason, SeriesNetwork, Anime, AnimeActors, AnimeEpisodesPerSeason, AnimeGenre, AnimeNetwork, \
    AnimeList, ListType, SeriesActors, MoviesList, Status, MoviesCollections


bp = Blueprint('main', __name__)


@bp.route("/<media_list>/<user_name>", methods=['GET'])
@login_required
def mymedialist(media_list, user_name):
    user = User.query.filter_by(username=user_name).first()

    # Check if <media_list> is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        abort(404)

    # No account with this username and protection of the admin account
    if user is None or (user.id == 1 and current_user.id != 1):
        abort(404)

    # Check if the current account can see the target account's list
    if current_user.id == user.id or current_user.id == 1:
        pass
    elif user.private and not current_user.is_following(user):
        abort(404)

    # Retrieve the media data
    if list_type == ListType.SERIES:
        element_data = SeriesList.get_series_info(user.id)
        covers_path = url_for('static', filename='covers/series_covers/')
        media_all_data = get_medialist_data(element_data, ListType.SERIES, covers_path, user.id)
    elif list_type == ListType.ANIME:
        element_data = AnimeList.get_anime_info(user.id)
        covers_path = url_for('static', filename='covers/anime_covers/')
        media_all_data = get_medialist_data(element_data, ListType.ANIME, covers_path, user.id)
    elif list_type == ListType.MOVIES:
        element_data = MoviesList.get_movies_info(user.id)
        covers_path = url_for('static', filename='covers/movies_covers/')
        media_all_data = get_medialist_data(element_data, ListType.MOVIES, covers_path, user.id)

    # View count of the media lists
    if current_user.id != 1 and user.id != current_user.id:
        if media_list == ListType.SERIES:
            user.series_views += 1
        elif media_list == ListType.ANIME:
            user.anime_views += 1
        elif media_list == ListType.MOVIES:
            user.movies_views += 1
        db.session.commit()

    if list_type != ListType.MOVIES:
        return render_template('medialist_tv.html',
                               title="{}'s {}".format(user_name, media_list),
                               all_data=media_all_data["all_data"],
                               common_elements=media_all_data["common_elements"],
                               media_list=media_list,
                               target_user_name=user_name,
                               target_user_id=str(user.id))
    elif list_type == ListType.MOVIES:
        return render_template('medialist_movies.html',
                               title="{}'s {}".format(user_name, media_list),
                               all_data=media_all_data["all_data"],
                               common_elements=media_all_data["common_elements"],
                               media_list=media_list,
                               target_user_name=user_name,
                               target_user_id=str(user.id))


@bp.route("/movies_collection/<user_name>", methods=['GET'])
@login_required
def movies_collection(user_name):
    user = User.query.filter_by(username=user_name).first()

    # No account with this username and protection of the admin account
    if user is None or user.id == 1 and current_user.id != 1:
        abort(404)

    # Check if the current account can see the target account's movies collection
    if current_user.id == user.id or current_user.id == 1:
        pass
    elif user.private and current_user.is_following(user) is False:
        abort(404)

    collection_movie = MoviesCollections.get_collection_movies(user.id)

    completed_collections = []
    ongoing_collections = []
    for movie in collection_movie:
        movie_data = {"name": movie[2].name,
                      "total": movie[2].parts,
                      "parts": movie[3],
                      "overview": movie[2].overview,
                      "poster": '/static/covers/movies_collection_covers/' + movie[2].poster}

        if movie_data['total'] == 1:
            pass
        elif movie_data["total"] == movie_data["parts"]:
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


@bp.route('/update_element_season', methods=['POST'])
@login_required
def update_element_season():
    try:
        json_data = request.get_json()
        new_season = int(json_data['season']) + 1
        element_id = int(json_data['element_id'])
        element_type = json_data['element_type']
    except:
        abort(400)

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        abort(400)

    if list_type == ListType.ANIME:
        # Check if the element is in the database (also used for watched time and last update)
        anime = Anime.query.filter_by(id=element_id).first()
        if anime is None:
            abort(400)

        # Check if the element is in the current account's list
        anime_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
        if anime_list is None:
            abort(400)

        # Check if the season number is between 1 and <last_season>
        all_seasons = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id)\
            .order_by(AnimeEpisodesPerSeason.season).all()
        if 1 > new_season > all_seasons[-1].season:
            abort(400)

        # Set the new data
        old_season = anime_list.current_season
        old_episode = anime_list.last_episode_watched
        anime_list.current_season = new_season
        anime_list.last_episode_watched = 1
        app.logger.info("[{}] Anime season with ID {} updated: {}"
                                .format(current_user.id, element_id, new_season))

        # Commit the changes
        db.session.commit()

        # Set the last update
        set_last_update(media_name=anime.name, media_type=list_type, old_season=old_season,
                        new_season=new_season, old_episode=old_episode, new_episode=1)

        # Compute the new time spent
        compute_time_spent(cat_type="season", old_eps=old_episode, old_seas=old_season, new_seas=new_season,
                           all_seas_data=all_seasons, media=anime, list_type=list_type)
    elif list_type == ListType.SERIES:
        # Check if the element is in the database (also used for watched time and last update)
        series = Series.query.filter_by(id=element_id).first()
        if series is None:
            abort(400)

        # Check if the element is in the current account's list
        series_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
        if series_list is None:
            abort(400)

        # Check if the season number is between 1 and <last_season>
        all_seasons = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id)\
            .order_by(SeriesEpisodesPerSeason.season).all()
        if 1 > new_season > all_seasons[-1].season:
            abort(400)

        # Set the new data
        old_season = series_list.current_season
        old_episode = series_list.last_episode_watched
        series_list.current_season = new_season
        series_list.last_episode_watched = 1
        app.logger.info('[{}] Series season with ID {} updated: {}'
                                .format(current_user.id, element_id, new_season))

        # Commit the changes
        db.session.commit()

        # Set the last updates
        set_last_update(media_name=series.name, media_type=list_type, old_season=old_season,
                        new_season=new_season, old_episode=old_episode, new_episode=1)

        # Compute the new time spent
        compute_time_spent(cat_type="season", old_eps=old_episode, old_seas=old_season, new_seas=new_season,
                           all_seas_data=all_seasons, media=series, list_type=list_type)

    return '', 204


@bp.route('/update_element_episode', methods=['POST'])
@login_required
def update_element_episode():
    try:
        json_data = request.get_json()
        new_episode = int(json_data['episode'])+1
        element_id = int(json_data['element_id'])
        element_type = json_data['element_type']
    except:
        abort(400)

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        abort(400)

    if list_type == ListType.ANIME:
        # Check if the element is in the database (also used for watched time and last update)
        anime = Anime.query.filter_by(id=element_id).first()
        if anime is None:
            abort(400)

        # Check if the element is in the current user's list
        anime_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
        if anime_list is None:
            abort(400)

        # Check if the episode number is between 1 and <last_episode>
        last_episode = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id, season=anime_list.current_season) \
            .first().episodes
        if 1 > new_episode > last_episode:
            abort(400)

        # Set the new data
        old_season = anime_list.current_season
        old_episode = anime_list.last_episode_watched
        anime_list.last_episode_watched = new_episode
        app.logger.info('[{}] Anime episode with ID {} updated: {}'
                                .format(current_user.id, element_id, new_episode))

        # Commit the changes
        db.session.commit()

        # Set the last update
        set_last_update(media_name=anime.name, media_type=list_type, old_season=old_season, new_season=old_season,
                        old_episode=old_episode, new_episode=new_episode)

        # Compute the new time spent
        compute_time_spent(cat_type='episode', new_eps=new_episode, old_eps=old_episode, media=anime,
                           list_type=list_type)
    elif list_type == ListType.SERIES:
        # Check if the element is in the database (also used for watched time and last update)
        series = Series.query.filter_by(id=element_id).first()
        if series is None:
            abort(400)

        # Check if the element is in the current user's list
        series_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
        if series_list is None:
            abort(400)

        # Check if the episode number is between 1 and <last_episode>
        last_episode = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id, season=series_list.current_season)\
            .first().episodes
        if 1 > new_episode > last_episode:
            abort(400)

        # Set the new data
        old_season = series_list.current_season
        old_episode = series_list.last_episode_watched
        series_list.last_episode_watched = new_episode
        app.logger.info('[{}] Series episode with ID {} updated: {}'
                                .format(current_user.id, element_id, new_episode))

        # Commit the changes
        db.session.commit()

        # Set the last update
        set_last_update(media_name=series.name, media_type=list_type, old_season=old_season, new_season=old_season,
                        old_episode=old_episode, new_episode=new_episode)

        # Compute the new time spent
        compute_time_spent(cat_type='episode', new_eps=new_episode, old_eps=old_episode, media=series,
                           list_type=list_type)

    return '', 204


@bp.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    try:
        json_data = request.get_json()
        element_id = int(json_data['element_id'])
        element_type = json_data['element_type']
        favorite = bool(json_data['favorite'])
    except:
        abort(400)

    # Check if the medialist exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        abort(400)

    # Check if favorite is boolean
    if type(favorite) is not bool:
        abort(400)

    # Check if the element is in the current user's list
    if list_type == ListType.ANIME:
        element_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
    elif list_type == ListType.SERIES:
        element_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
    else:
        element_list = MoviesList.query.filter_by(user_id=current_user.id, movies_id=element_id).first()

    if element_list is None:
        abort(400)

    element_list.favorite = favorite

    # Commit the changes
    db.session.commit()

    return '', 204


@bp.route('/delete_element', methods=['POST'])
@login_required
def delete_element():
    try:
        json_data = request.get_json()
        element_id = int(json_data['delete'])
        element_type = json_data['element_type']
    except:
        abort(400)

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        abort(400)

    if list_type == ListType.SERIES:
        # Check if series exists in the database (also used for watched time and last update)
        series = Series.query.filter_by(id=element_id).first()
        if series is None:
            abort(400)

        # Check if series exists in the current user's list
        series_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
        if series_list is None:
            abort(400)

        # Compute new time spent
        old_episode = series_list.last_episode_watched
        old_season = series_list.current_season
        all_seasons = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id) \
            .order_by(SeriesEpisodesPerSeason.season).all()
        compute_time_spent(cat_type="delete", old_eps=old_episode, old_seas=old_season, all_seas_data=all_seasons,
                           media=series, list_type=list_type)

        # Delete the media from the user's list
        SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).delete()
        db.session.commit()
        app.logger.info('[{}] Series with ID {} deleted'.format(current_user.id, element_id))
    elif list_type == ListType.ANIME:
        # Check if anime exists in the database (also used for watched time and last update)
        anime = Anime.query.filter_by(id=element_id).first()
        if anime is None:
            abort(400)

        # Check if anime exists in list of the current account
        anime_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
        if anime_list is None:
            abort(400)

        # Compute new time spent
        old_episode = anime_list.last_episode_watched
        old_season = anime_list.current_season
        all_seasons = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id) \
            .order_by(AnimeEpisodesPerSeason.season).all()
        compute_time_spent(cat_type="delete", old_eps=old_episode, old_seas=old_season, all_seas_data=all_seasons,
                           media=anime, list_type=list_type)

        # Delete the media from the user's list
        AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).delete()
        db.session.commit()
        app.logger.info('[{}] Anime with ID {} deleted'.format(current_user.id, element_id))
    elif list_type == ListType.MOVIES:
        # Check if movie exists in the database (also used for watched time and last update)
        movies = Movies.query.filter_by(id=element_id).first()
        if movies is None:
            abort(400)

        # Check if movie exists in the account's list
        movies_list = MoviesList.query.filter_by(user_id=current_user.id, movies_id=element_id).first()
        if movies_list is None:
            abort(400)

        # Compute the new time spent
        compute_time_spent(cat_type="delete", media=movies, list_type=list_type)

        # Delete the media from the user's list
        MoviesList.query.filter_by(user_id=current_user.id, movies_id=element_id).delete()
        db.session.commit()
        app.logger.info('[{}] Movie with ID {} deleted'.format(current_user.id, element_id))

    return '', 204


@bp.route('/change_element_category', methods=['POST'])
@login_required
def change_element_category():
    try:
        json_data = request.get_json()
        element_new_category = json_data['status']
        element_id = int(json_data['element_id'])
        element_type = json_data['element_type']
    except:
        abort(400)

    # Check if the <media_list> exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        abort(400)

    # Check if the status is valid compared to the list type
    new_status = check_cat_type(list_type, element_new_category)
    if new_status is None:
        abort(400)

    # Check if the element is in the user's list
    if list_type == ListType.SERIES:
        element = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
        season_data = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id).all()
    elif list_type == ListType.ANIME:
        element = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
        season_data = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id).all()
    elif list_type == ListType.MOVIES:
        element = MoviesList.query.filter_by(user_id=current_user.id, movies_id=element_id).first()
    if element is None:
        abort(400)

    old_status = element.status
    element.status = new_status

    if list_type != ListType.MOVIES:
        current_season = element.current_season
        last_episode_watched = element.last_episode_watched
    if new_status == Status.COMPLETED:
        # Set to the last seasons and episodes
        if list_type == ListType.SERIES:
            seasons_and_eps = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id) \
                .order_by(SeriesEpisodesPerSeason.season).all()
            element.current_season = len(seasons_and_eps)
            element.last_episode_watched = seasons_and_eps[-1].episodes
        elif list_type == ListType.ANIME:
            seasons_and_eps = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id) \
                .order_by(AnimeEpisodesPerSeason.season).all()
            element.current_season = len(seasons_and_eps)
            element.last_episode_watched = seasons_and_eps[-1].episodes
    elif new_status == Status.RANDOM:
        # Set to first season and episode
        element.current_season = 1
        element.last_episode_watched = 1
    elif new_status == Status.PLAN_TO_WATCH:
        # Set to first season and episode
        if list_type != ListType.MOVIES:
            element.current_season = 1
            element.last_episode_watched = 1

    # Compute total time spent and set last update
    if list_type == ListType.SERIES:
        series = Series.query.filter_by(id=element_id).first()
        set_last_update(media_name=series.name, media_type=list_type, old_status=old_status, new_status=new_status)
        compute_time_spent(cat_type="category", old_eps=last_episode_watched, old_seas=current_season, media=series,
                           old_status=old_status, new_status=new_status, list_type=list_type, all_seas_data=season_data)
    elif list_type == ListType.ANIME:
        anime = Anime.query.filter_by(id=element_id).first()
        set_last_update(media_name=anime.name, media_type=list_type, old_status=old_status, new_status=new_status)
        compute_time_spent(cat_type="category", old_eps=last_episode_watched, old_seas=current_season, media=anime,
                           old_status=old_status, new_status=new_status, list_type=list_type, all_seas_data=season_data)
    elif list_type == ListType.MOVIES:
        movie = Movies.query.filter_by(id=element_id).first()
        set_last_update(media_name=movie.name, media_type=list_type, old_status=old_status, new_status=new_status)
        compute_time_spent(cat_type="category", media=movie, old_status=old_status, new_status=new_status,
                           list_type=list_type)

    db.session.commit()
    app.logger.info('[{}] Category of the element with ID {} ({}) changed to {}'
                    .format(current_user.id, element_id, list_type, new_status))

    return '', 204


@bp.route('/add_element', methods=['POST'])
@login_required
def add_element():
    try:
        json_data = request.get_json()
        element_id = json_data['element_id']
        element_type = json_data['element_type']
        element_cat = json_data['element_cat']
    except:
        abort(400)

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        abort(400)

    # Check if the status is valid compared to the list type
    new_status = check_cat_type(list_type, element_cat)
    if new_status is None:
        abort(400)

    # Check if the element exist in the database
    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()
    elif list_type == ListType.MOVIES:
        element = Movies.query.filter_by(id=element_id).first()

    # Check if the element is already in the current user's list
    if list_type == ListType.SERIES:
        if SeriesList.query.filter_by(user_id=current_user.id, series_id=element.id).first():
            flash("This series is already in your list", "warning")
    elif list_type == ListType.ANIME:
        if AnimeList.query.filter_by(user_id=current_user.id, anime_id=element.id).first():
            flash("This anime is already in your list", "warning")
    elif list_type == ListType.MOVIES:
        if MoviesList.query.filter_by(user_id=current_user.id, movies_id=element.id).first():
            flash("This movie is already in your list", "warning")

    add_element_to_user(element, current_user.id, list_type, new_status)

    return '', 204


@bp.route('/lock_media', methods=['POST'])
@login_required
def lock_media():
    try:
        json_data = request.get_json()
        element_id = json_data['element_id']
        element_type = json_data['element_type']
        lock_status = json_data['lock_status']
    except:
        abort(400)

    # Check if the user is the admin
    if current_user.id == 3 or current_user.id == 2 or current_user.id == 1:
        pass
    else:
        abort(404)

    # Check if the list_type exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        abort(400)

    # Check if the lock_status is boolean
    if type(lock_status) is not bool:
        abort(400)

    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()
    elif list_type == ListType.MOVIES:
        element = Movies.query.filter_by(id=element_id).first()

    if element is None:
        abort(400)

    element.lock_status = lock_status
    db.session.commit()

    return '', 204


@bp.route('/media_sheet/<media_type>/<media_id>', methods=['GET', 'POST'])
@login_required
def media_sheet(media_type, media_id):
    if media_type == 'Series':
        list_type = ListType.SERIES
    elif media_type == 'Anime':
        list_type = ListType.ANIME
    elif media_type == 'Movies':
        list_type = ListType.MOVIES
    else:
        abort(404)

    # Check if the media sheet loading came from an account (so media_id = media_name)
    try:
        media_id = int(media_id)
        seek_media = None
    except:
        if media_id == 'Nip-Tuck':
            media_id = 'Nip/Tuck'
        if list_type == ListType.SERIES:
            seek_media = Series.query.filter((Series.name == media_id) | (Series.original_name == media_id)).first()
        elif list_type == ListType.ANIME:
            seek_media = Anime.query.filter((Anime.name == media_id) | (Anime.original_name == media_id)).first()
        else:
            seek_media = Movies.query.filter((Movies.name == media_id) | (Movies.original_name == media_id)).first()

    if seek_media:
        return redirect(url_for('main.media_sheet', media_type=media_type, media_id=seek_media.id))

    element_sheet = load_media_sheet(media_id, current_user.id, list_type)
    title = element_sheet['original_name']

    return render_template('media_sheet.html', title=title, data=element_sheet, media_list=list_type.value)


@bp.route('/check_media/<list_type>/<media_id>', methods=['GET', 'POST'])
@login_required
def check_media(list_type, media_id):
    # Check if the media_list exist and is valid
    try:
        list_type = ListType(list_type)
    except ValueError:
        abort(404)

    # Check if the element ID exist in the database
    if list_type == ListType.SERIES:
        element = Series.query.filter_by(themoviedb_id=media_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(themoviedb_id=media_id).first()
    elif list_type == ListType.MOVIES:
        element = Movies.query.filter_by(themoviedb_id=media_id).first()

    # If media ID exists, load the media sheet wihout API call
    if element:
        element_id = element.id
    else:
        element_id = add_element_in_db(media_id, list_type)

    if list_type == ListType.SERIES:
        media_type = 'Series'
    elif list_type == ListType.ANIME:
        media_type = 'Anime'
    elif list_type == ListType.MOVIES:
        media_type = 'Movies'

    return redirect(url_for('main.media_sheet', media_type=media_type, media_id=element_id))


@bp.route("/media_sheet_form/<media_type>/<media_id>", methods=['GET', 'POST'])
@login_required
def media_sheet_form(media_type, media_id):
    if current_user.id == 3 or current_user.id == 2 or current_user.id == 1:
        pass
    else:
        abort(404)

    form = EditMediaData()

    if media_type == 'Series':
        list_type = ListType.SERIES
    elif media_type == 'Anime':
        list_type = ListType.ANIME
    elif media_type == 'Movies':
        list_type = ListType.MOVIES
    else:
        abort(404)

    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=media_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=media_id).first()
    elif list_type == ListType.MOVIES:
        element = Movies.query.filter_by(id=media_id).first()

    if request.method == 'GET':
        form.original_name.data = element.original_name
        form.name.data = element.name
        form.homepage.data = element.homepage
        form.synopsis.data = element.synopsis
        # form.genres.data = ', '.join([r.genre for r in element.genres])
        form.actors.data = ', '.join([r.name for r in element.actors])
        if list_type != ListType.MOVIES:
            form.created_by.data = element.created_by
            form.first_air_date.data = element.first_air_date
            form.last_air_date.data = element.last_air_date
            form.production_status.data = element.status
            form.duration.data = element.episode_duration
            form.origin_country.data = element.origin_country
            form.networks.data = ', '.join([r.network for r in element.networks])
        elif list_type == ListType.MOVIES:
            form.directed_by.data = element.director_name
            form.release_date.data = element.release_date
            form.duration.data = element.runtime
            form.original_language.data = element.original_language
            form.tagline.data = element.tagline
            form.budget.data = element.budget
            form.revenue.data = element.revenue
    if form.validate_on_submit():
        if form.cover.data:
            element.image_cover = save_new_cover(form.cover.data, media_type)
        element.original_name = form.original_name.data
        element.name = form.name.data
        element.homepage = form.homepage.data
        element.synopsis = form.synopsis.data

        if list_type != ListType.MOVIES:
            element.created_by = form.created_by.data
            element.first_air_date = form.first_air_date.data
            element.last_air_date = form.last_air_date.data
            element.status = form.production_status.data
            element.episode_duration = form.duration.data
            element.origin_country = form.origin_country.data
        elif list_type == ListType.MOVIES:
            element.director_name = form.directed_by.data
            element.release_date = form.release_date.data
            element.runtime = form.duration.data
            element.original_language = form.original_language.data
            element.tagline = form.tagline.data
            element.budget = form.budget.data
            element.revenue = form.revenue.data

        db.session.commit()

        # Actors
        if [r.name for r in element.actors] == form.actors.data.split(', '):
            pass
        else:
            for actor in [r.name for r in element.actors]:
                if list_type == ListType.SERIES:
                    SeriesActors.query.filter_by(series_id=media_id, name=actor).delete()
                elif list_type == ListType.ANIME:
                    AnimeActors.query.filter_by(anime_id=media_id, name=actor).delete()
                elif list_type == ListType.MOVIES:
                    MoviesActors.query.filter_by(movies_id=media_id, name=actor).delete()
            db.session.commit()
            for actor in form.actors.data.split(', '):
                if list_type == ListType.SERIES:
                    add_actor = SeriesActors(series_id=media_id,
                                             name=actor)
                elif list_type == ListType.ANIME:
                    add_actor = AnimeActors(anime_id=media_id,
                                            name=actor)
                elif list_type == ListType.MOVIES:
                    add_actor = MoviesActors(movies_id=media_id,
                                             name=actor)
                db.session.add(add_actor)
            db.session.commit()

        # Genres
        # if [r.genre for r in element.genres] == form.genres.data.split(', '):
        #     pass
        # else:
        #     for genre in [r.genre for r in element.genres]:
        #         if list_type == ListType.SERIES:
        #             SeriesGenre.query.filter_by(series_id=media_id, genre=genre).delete()
        #         elif list_type == ListType.ANIME:
        #             AnimeGenre.query.filter_by(anime_id=media_id, genre=genre).delete()
        #         elif list_type == ListType.MOVIES:
        #             MoviesGenre.query.filter_by(movies_id=media_id, genre=genre).delete()
        #     db.session.commit()
        #     for genre in form.genres.data.split(', '):
        #         if list_type == ListType.SERIES:
        #             add_genre = SeriesGenre(series_id=media_id,
        #                                     genre=genre)
        #         elif list_type == ListType.ANIME:
        #             add_genre = AnimeGenre(anime_id=media_id,
        #                                    genre=genre)
        #         elif list_type == ListType.MOVIES:
        #             add_genre = MoviesGenre(movies_id=media_id,
        #                                     genre=genre)
        #         db.session.add(add_genre)
        #     db.session.commit()

        # Networks
        if list_type != ListType.MOVIES:
            if [r.network for r in element.networks] == form.networks.data.split(', '):
                pass
            else:
                for network in [r.network for r in element.networks]:
                    if list_type == ListType.SERIES:
                        SeriesNetwork.query.filter_by(series_id=media_id, network=network).delete()
                    elif list_type == ListType.ANIME:
                        AnimeNetwork.query.filter_by(anime_id=media_id, network=network).delete()
                db.session.commit()
                for network in form.networks.data.split(', '):
                    if list_type == ListType.SERIES:
                        add_network = SeriesNetwork(series_id=media_id,
                                                    network=network)
                    elif list_type == ListType.ANIME:
                        add_network = AnimeNetwork(anime_id=media_id,
                                                   network=network)
                    db.session.add(add_network)
                db.session.commit()

        return redirect(url_for('main.media_sheet', media_type=media_type, media_id=media_id))

    return render_template('media_sheet_form.html', form=form, media_type=media_type)


@bp.route('/search_media', methods=['GET'])
@login_required
def search_media():
    search = request.args['search']

    if search is None:
        flash('Sorry, no results found for your query.', 'warning')

    series_results, anime_results, movies_results = ApiData().media_search(search)

    if series_results is None and anime_results is None and movies_results is None:
        flash('Sorry, no results found for your query.', 'warning')
        return redirect(request.referrer)

    platform = str(request.user_agent.platform)
    if platform == "iphone" or platform == "android" or platform is None or platform == 'None':
        template = 'media_search_mobile.html'
    else:
        template = 'media_search.html'

    return render_template(template,
                           title="Media search",
                           series_results=series_results,
                           anime_results=anime_results,
                           movies_results=movies_results,
                           search=search)


@bp.route('/autocomplete', methods=['GET'])
@login_required
def autocomplete():
    search = request.args.get('q')
    results = ApiData().autocomplete_search(search)

    return jsonify(matching_results=results)
