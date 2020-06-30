import json

import pytz

from MyLists import db, app
from datetime import datetime
from MyLists.API_data import ApiData
from MyLists.main.forms import EditMediaData
from flask_login import login_required, current_user
from flask import Blueprint, url_for, request, abort, render_template, flash, jsonify, redirect
from MyLists.main.functions import get_medialist_data, set_last_update, compute_time_spent, check_cat_type, \
    add_element_to_user, add_element_in_db, load_media_sheet, save_new_cover
from MyLists.models import Movies, MoviesActors, Series, SeriesList, SeriesEpisodesPerSeason, SeriesNetwork, Anime, \
    AnimeActors, AnimeEpisodesPerSeason, AnimeNetwork, AnimeList, ListType, SeriesActors, MoviesList, Status, \
    MoviesCollections, RoleType

bp = Blueprint('main', __name__)


@bp.route("/<string:media_list>/<string:user_name>", methods=['GET', 'POST'])
@login_required
def mymedialist(media_list, user_name):
    # Check if the user can see the <media_list>
    user = current_user.check_autorization(user_name)

    # Check if <media_list> is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        abort(404)

    # Add views_count to the profile
    current_user.add_view_count(user, list_type)

    # Retrieve the <media_data>
    if list_type == ListType.SERIES:
        series_data = SeriesList.get_series_info(user.id)
        covers_path = url_for('static', filename='covers/series_covers/')
        media_data = get_medialist_data(series_data, list_type, covers_path, user.id)
    elif list_type == ListType.ANIME:
        anime_data = AnimeList.get_anime_info(user.id)
        covers_path = url_for('static', filename='covers/anime_covers/')
        media_data = get_medialist_data(anime_data, list_type, covers_path, user.id)
    elif list_type == ListType.MOVIES:
        movies_data = MoviesList.get_movies_info(user.id)
        covers_path = url_for('static', filename='covers/movies_covers/')
        media_data = get_medialist_data(movies_data, list_type, covers_path, user.id)

    if list_type != ListType.MOVIES:
        return render_template('medialist_tv.html',
                               title="{}'s {}".format(user_name, media_list),
                               media_data=media_data["grouping"],
                               common_elements=media_data["common_elements"],
                               media_list=media_list,
                               target_user_name=user_name,
                               target_user_id=str(user.id))
    elif list_type == ListType.MOVIES:
        return render_template('medialist_movies.html',
                               title="{}'s {}".format(user_name, media_list),
                               media_data=media_data["grouping"],
                               common_elements=media_data["common_elements"],
                               media_list=media_list,
                               target_user_name=user_name,
                               target_user_id=str(user.id))


@bp.route("/movies_collection/<string:user_name>", methods=['GET', 'POST'])
@login_required
def movies_collection(user_name):
    # Check if the user can see the <movie_collection_list>
    user = current_user.check_autorization(user_name)

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
                           length_ongoing=len(ongoing_collections),
                           target_user_name=user_name,
                           target_user_id=str(user.id))


@bp.route('/media_sheet/<string:media_type>/<int:media_id>', methods=['GET', 'POST'])
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

    # Check if <media_id> came from TMDB and if in local DB
    tmdb_id = request.args.get('search')
    if tmdb_id:
        searching = {'themoviedb_id': media_id}
    else:
        searching = {'id': media_id}

    if list_type == ListType.SERIES:
        media = Series.query.filter_by(**searching).first()
    elif list_type == ListType.ANIME:
        media = Anime.query.filter_by(**searching).first()
    elif list_type == ListType.MOVIES:
        media = Movies.query.filter_by(**searching).first()

    # If <media> is None and a TMDB ID was provived add the media to the local DB else abort.
    if not media:
        if tmdb_id:
            try:
                media = add_element_in_db(media_id, list_type)
            except Exception as e:
                app.logger.error('[SYSYEM] - Error occured trying to add media ({}) ID {} to local DB: {}'
                                 .format(list_type, media_id, e))
                flash('Sorry, a problem occured trying to load the media info. Please try again later.')
                return redirect(request.referrer)
        else:
            abort(404)

    # If <media> exist and a TMDB ID was provived redirect to get a nice URL.
    if media and tmdb_id:
        return redirect(url_for('main.media_sheet', media_type=media_type, media_id=media.id))

    element_sheet = load_media_sheet(media, current_user.id, list_type)
    title = element_sheet['original_name']

    return render_template('media_sheet.html', title=title, data=element_sheet, media_list=list_type.value)


@bp.route("/media_sheet_form/<string:media_type>/<int:media_id>", methods=['GET', 'POST'])
@login_required
def media_sheet_form(media_type, media_id):
    if current_user.role != RoleType.ADMIN and current_user.role != RoleType.MANAGER:
        abort(403)

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

    if not element:
        abort(404)

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

    return render_template('media_sheet_form.html', title='Media Form', form=form, media_type=media_type)


@bp.route('/update_element_season', methods=['POST'])
@login_required
def update_element_season():
    try:
        json_data = request.get_json()
        new_season = int(json_data['season']) + 1
        element_id = int(json_data['element_id'])
        element_type = json_data['element_type']
    except:
        return '', 400

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        return '', 400

    if list_type == ListType.SERIES:
        # Check if the element is in the database (also used for watched_time and last_update)
        series = Series.query.filter_by(id=element_id).first()
        if series is None:
            return '', 400

        # Check if the element is in the current account's list
        series_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
        if series_list is None:
            return '', 400

        # Check if the season number is between 1 and <last_season>
        all_seasons = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id)\
            .order_by(SeriesEpisodesPerSeason.season).all()
        if 1 > new_season > all_seasons[-1].season:
            return '', 400

        # Set the new data
        old_season = series_list.current_season
        old_episode = series_list.last_episode_watched
        series_list.current_season = new_season
        series_list.last_episode_watched = 1
        app.logger.info('[{}] Series season with ID {} updated: {}'.format(current_user.id, element_id, new_season))

        # Commit the changes
        db.session.commit()

        # Set the last updates
        set_last_update(media=series, media_type=list_type, old_season=old_season,
                        new_season=new_season, old_episode=old_episode, new_episode=1)

        # Compute the new time spent
        compute_time_spent(cat_type="season", old_eps=old_episode, old_seas=old_season, new_seas=new_season,
                           all_seas_data=all_seasons, media=series, list_type=list_type)
    elif list_type == ListType.ANIME:
        # Check if the element is in the database (also used for watched_time and last_update)
        anime = Anime.query.filter_by(id=element_id).first()
        if anime is None:
            return '', 400

        # Check if the element is in the current account's list
        anime_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
        if anime_list is None:
            return '', 400

        # Check if the season number is between 1 and <last_season>
        all_seasons = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id)\
            .order_by(AnimeEpisodesPerSeason.season).all()
        if 1 > new_season > all_seasons[-1].season:
            return '', 400

        # Set the new data
        old_season = anime_list.current_season
        old_episode = anime_list.last_episode_watched
        anime_list.current_season = new_season
        anime_list.last_episode_watched = 1
        app.logger.info("[{}] Anime season with ID {} updated: {}".format(current_user.id, element_id, new_season))

        # Commit the changes
        db.session.commit()

        # Set the last update
        set_last_update(media=anime, media_type=list_type, old_season=old_season,
                        new_season=new_season, old_episode=old_episode, new_episode=1)

        # Compute the new time spent
        compute_time_spent(cat_type="season", old_eps=old_episode, old_seas=old_season, new_seas=new_season,
                           all_seas_data=all_seasons, media=anime, list_type=list_type)

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
        return '', 400

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        return '', 400

    if list_type == ListType.SERIES:
        # Check if the element is in the database (also used for watched_time and last_update)
        series = Series.query.filter_by(id=element_id).first()
        if series is None:
            return '', 400

        # Check if the element is in the current user's list
        series_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
        if series_list is None:
            return '', 400

        # Check if the episode number is between 1 and <last_episode>
        last_episode = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id, season=series_list.current_season)\
            .first().episodes
        if 1 > new_episode > last_episode:
            return '', 400

        # Set the new data
        old_season = series_list.current_season
        old_episode = series_list.last_episode_watched
        series_list.last_episode_watched = new_episode
        app.logger.info('[{}] Series episode with ID {} updated: {}'.format(current_user.id, element_id, new_episode))

        # Commit the changes
        db.session.commit()

        # Set the last update
        set_last_update(media=series, media_type=list_type, old_season=old_season, new_season=old_season,
                        old_episode=old_episode, new_episode=new_episode)

        # Compute the new time spent
        compute_time_spent(cat_type='episode', new_eps=new_episode, old_eps=old_episode, media=series,
                           list_type=list_type)
    elif list_type == ListType.ANIME:
        # Check if the element is in the database (also used for watched_time and last_update)
        anime = Anime.query.filter_by(id=element_id).first()
        if anime is None:
            return '', 400

        # Check if the element is in the current user's list
        anime_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
        if anime_list is None:
            return '', 400

        # Check if the episode number is between 1 and <last_episode>
        last_episode = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id, season=anime_list.current_season) \
            .first().episodes
        if 1 > new_episode > last_episode:
            return '', 400

        # Set the new data
        old_season = anime_list.current_season
        old_episode = anime_list.last_episode_watched
        anime_list.last_episode_watched = new_episode
        app.logger.info('[{}] Anime episode with ID {} updated: {}'.format(current_user.id, element_id, new_episode))

        # Commit the changes
        db.session.commit()

        # Set the last update
        set_last_update(media=anime, media_type=list_type, old_season=old_season, new_season=old_season,
                        old_episode=old_episode, new_episode=new_episode)

        # Compute the new time spent
        compute_time_spent(cat_type='episode', new_eps=new_episode, old_eps=old_episode, media=anime,
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
        return '', 400

    # Check if the medialist exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        return '', 400

    # Check if favorite is boolean
    if type(favorite) is not bool:
        return '', 400

    # Check if the element is in the current user's list
    if list_type == ListType.ANIME:
        element_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
    elif list_type == ListType.SERIES:
        element_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
    elif list_type == ListType.MOVIES:
        element_list = MoviesList.query.filter_by(user_id=current_user.id, movies_id=element_id).first()

    if element_list is None:
        return '', 400

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
        return '', 400

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        return '', 400

    if list_type == ListType.SERIES:
        # Check if series exists in the database (also used for watched_time and last_update)
        series = Series.query.filter_by(id=element_id).first()
        if series is None:
            return '', 400

        # Check if series exists in the current user's list
        series_list = SeriesList.query.filter_by(user_id=current_user.id, series_id=element_id).first()
        if series_list is None:
            return '', 400

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
        # Check if anime exists in the database (also used for watched_time and last_update)
        anime = Anime.query.filter_by(id=element_id).first()
        if anime is None:
            return '', 400

        # Check if anime exists in list of the current account
        anime_list = AnimeList.query.filter_by(user_id=current_user.id, anime_id=element_id).first()
        if anime_list is None:
            return '', 400

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
        # Check if movie exists in the database (also used for watched_time and last_update)
        movies = Movies.query.filter_by(id=element_id).first()
        if movies is None:
            return '', 400

        # Check if movie exists in the account's list
        movies_list = MoviesList.query.filter_by(user_id=current_user.id, movies_id=element_id).first()
        if movies_list is None:
            return '', 400

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
        return '', 400

    # Check the <media_list> parameter
    try:
        list_type = ListType(element_type)
    except ValueError:
        return '', 400

    # Check if the <status> parameter
    new_status = check_cat_type(list_type, element_new_category)
    if new_status is None:
        return '', 400

    # Recover the media
    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
        season_data = element.eps_per_season
        element_list = db.session.query(SeriesList).filter_by(user_id=current_user.id, series_id=element.id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()
        element_list = db.session.query(AnimeList).filter_by(user_id=current_user.id, anime_id=element.id).first()
        season_data = element.eps_per_season
    elif list_type == ListType.MOVIES:
        element = Movies.query.filter_by(id=element_id).first()
        element_list = db.session.query(MoviesList).filter_by(user_id=current_user.id, movies_id=element.id).first()

    # Check if media in user's list
    if not element_list:
        return '', 400

    old_status = element_list.status
    element_list.status = new_status

    # Set and change accordingly <last_episode_watched> and <current_season>
    if list_type != ListType.MOVIES:
        current_season = element_list.current_season
        last_episode_watched = element_list.last_episode_watched
        if new_status == Status.COMPLETED:
            element_list.current_season = len(season_data)
            element_list.last_episode_watched = season_data[-1].episodes
        elif new_status == Status.RANDOM or new_status == Status.PLAN_TO_WATCH:
            element_list.current_season = 1
            element_list.last_episode_watched = 1

    # Compute <total_time_spent> and set <last_update>
    set_last_update(media=element, media_type=list_type, old_status=old_status, new_status=new_status)
    if list_type != ListType.MOVIES:
        compute_time_spent(cat_type="category", old_eps=last_episode_watched, old_seas=current_season, media=element,
                           old_status=old_status, new_status=new_status, list_type=list_type, all_seas_data=season_data)
    elif list_type == ListType.MOVIES:
        compute_time_spent(cat_type="category", media=element, old_status=old_status, new_status=new_status,
                           list_type=list_type)

    db.session.commit()
    app.logger.info('[{}] Category of element ID {} ({}) changed from {} to {}.'
                    .format(current_user.id, element_id, list_type.value, old_status.value, new_status.value))

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
        return '', 400

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        return '', 400

    # Check if the status is valid compared to the list type
    new_status = check_cat_type(list_type, element_cat)
    if new_status is None:
        return '', 400

    # Check if the element exist in the database
    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()
    elif list_type == ListType.MOVIES:
        element = Movies.query.filter_by(id=element_id).first()

    if element is None:
        return '', 400

    # Check if the element is already in the current user's list
    if list_type == ListType.SERIES:
        if SeriesList.query.filter_by(user_id=current_user.id, series_id=element.id).first():
            return '', 400
    elif list_type == ListType.ANIME:
        if AnimeList.query.filter_by(user_id=current_user.id, anime_id=element.id).first():
            return '', 400
    elif list_type == ListType.MOVIES:
        if MoviesList.query.filter_by(user_id=current_user.id, movies_id=element.id).first():
            return '', 400

    try:
        add_element_to_user(element, current_user.id, list_type, new_status)
        app.logger.info('[{}] Added the Media ({}) "{}", with ID: {}'
                        .format(current_user.id, list_type.value, element.name, element.id))
    except Exception as e:
        app.logger.error("Error occured: {}. Could not add media with ID {} to user {}."
                         .format(e, element_id, current_user.id))
        return '', 400

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
        return '', 400

    # Check if the user is admin or manager
    if current_user.role != RoleType.ADMIN and current_user.role != RoleType.MANAGER:
        return '', 403

    # Check if the list_type exist and is valid
    try:
        list_type = ListType(element_type)
    except ValueError:
        return '', 400

    # Check if the lock_status is boolean
    if type(lock_status) is not bool:
        return '', 400

    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()
    elif list_type == ListType.MOVIES:
        element = Movies.query.filter_by(id=element_id).first()

    if element is None:
        return '', 400

    element.lock_status = lock_status
    db.session.commit()

    return '', 204


@bp.route('/search_media', methods=['GET'])
@login_required
def search_media():
    search = request.args.get('search')

    if len(search) == 0 or not search:
        flash('Sorry, no results found for your query.', 'warning')
        return redirect(request.referrer)

    try:
        data = ApiData().TMDb_search(search)
    except Exception as e:
        app.logger.error('[SYSTEM] Error requesting themoviedb API: {}'.format(e))
        flash('Sorry, an error occured, the API is not reachable.', 'warning')
        return redirect(request.referrer)

    if data.get("total_results", 0) == 0:
        flash('Sorry, no results found for your query.', 'warning')
        return redirect(request.referrer)

    # Recover 1 page of results (20 max) without peoples
    series_results, anime_results, movies_results = [], [], []
    for result in data["results"]:
        if result.get('known_for_department'):
            continue

        media_data = {'name': result.get('original_title') or result.get('original_name'),
                      'overview': result.get('overview'),
                      'first_air_date': result.get('first_air_date') or result.get('release_date'),
                      'tmdb_id': result['id']}

        # Modify the first_air_date / release_date format
        if media_data['first_air_date'] == '':
            media_data['first_air_date'] = 'Unknown'

        # Recover the poster_path or take a default image
        if result["poster_path"]:
            media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300", result["poster_path"])
        else:
            media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")

        # Put data in different lists in function of media type
        if result['media_type'] == 'tv':
            media_data['url'] = f"https://www.themoviedb.org/tv/{result['id']}"
            if result['origin_country'] == 'JP' or result['original_language'] == 'ja' \
                    and 16 in result['genre_ids']:
                media_data['media_type'] = ListType.ANIME.value
                media_data['name'] = result['name']
                anime_results.append(media_data)
            else:
                media_data['media_type'] = ListType.SERIES.value
                series_results.append(media_data)
        elif result['media_type'] == 'movie':
            media_data['media_type'] = ListType.MOVIES.value
            media_data['url'] = f"https://www.themoviedb.org/movie/{result['id']}"
            if result['original_language'] == 'ja' and 16 in result['genre_ids']:
                media_data['name'] = result['title']
            movies_results.append(media_data)

    # Get the proper plateform to display the template
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

    try:
        data = ApiData().TMDb_search(search)
    except Exception as e:
        app.logger.error('[SYSTEM] Error requesting the TMDB API: {}'.format(e))
        return jsonify(search_results=[{'nb_results': 0}]), 200

    if data.get("total_results", 0) == 0:
        return jsonify(search_results=[{'nb_results': 0}]), 200

    # Recover 7 results without peoples
    results = []
    for i, result in enumerate(data["results"]):
        if i >= data["total_results"] or i > 19 or len(results) >= 7:
            break

        if result.get('known_for_department'):
            continue

        media_data = {'name': result.get('original_title') or result.get('original_name'),
                      "first_air_date": result.get('first_air_date') or result.get('release_date'),
                      'tmdb_id': result["id"]}

        if media_data['first_air_date'] == '':
            media_data['first_air_date'] = 'Unknown'

        if result['media_type'] == 'tv':
            if result['origin_country'] == 'JP' or result['original_language'] == 'ja' \
                    and 16 in result['genre_ids']:
                media_data['media_type'] = ListType.ANIME.value
                media_data['name'] = result['name']
            else:
                media_data['media_type'] = ListType.SERIES.value
        elif result['media_type'] == 'movie':
            media_data['media_type'] = ListType.MOVIES.value
            if result['original_language'] == 'ja' and 16 in result['genre_ids']:
                media_data['name'] = result['title']

        if result["poster_path"]:
            media_data["poster_path"] = "{}{}".format("http://image.tmdb.org/t/p/w300", result["poster_path"])
        else:
            media_data["poster_path"] = url_for('static', filename="covers/anime_covers/default.jpg")
        results.append(media_data)

    return jsonify(search_results=results), 200


@bp.route('/read_notifications', methods=['GET'])
@login_required
def read_notifications():
    current_user.last_notif_read_time = datetime.utcnow()
    db.session.commit()

    notifications = current_user.get_notifications()

    results = []
    if notifications:
        for info in notifications:
            timestamp = info.timestamp.replace(tzinfo=pytz.UTC).isoformat()
            results.append({'media_type': info.media_type,
                            'media_id': info.media_id,
                            'timestamp': timestamp,
                            'payload': json.loads(info.payload_json)})

    return jsonify(results=results), 200
