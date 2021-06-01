import json
import pytz
from MyLists import db, app
from datetime import datetime
from MyLists.API_data import ApiData
from MyLists.main.add_db import AddtoDB
from flask_login import login_required, current_user
from MyLists.main.forms import EditMediaData, MediaComment, SearchForm
from MyLists.main.media_object import MediaDict, change_air_format, Autocomplete
from MyLists.main.functions import set_last_update, compute_time_spent, check_cat_type, save_new_cover
from flask import Blueprint, url_for, request, abort, render_template, flash, jsonify, redirect, session
from MyLists.models import Movies, MoviesActors, Series, SeriesList, SeriesNetwork, Anime, AnimeActors, AnimeNetwork, \
    AnimeList, ListType, SeriesActors, MoviesList, Status, RoleType, MediaType, get_next_airing, check_media, User, \
    get_media_query, GamesList, get_more_stats, get_games_stats, UserLastUpdate, get_models_group

bp = Blueprint('main', __name__)


@bp.route("/<media_list>/<user_name>/", methods=['GET', 'POST'])
@bp.route("/<media_list>/<user_name>/<category>/", methods=['GET', 'POST'])
@bp.route("/<media_list>/<user_name>/<category>/genre/<genre>/by/<sorting>/page/<page_val>", methods=['GET', 'POST'])
@login_required
def mymedialist(media_list, user_name, category=None, genre='All', sorting=None, page_val=1):
    # Check if <media_list> is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return abort(400)

    # Check if <user> can see <media_list>
    user = current_user.check_autorization(user_name)

    # Add <views_count> to the profile
    current_user.add_view_count(user, list_type)

    # Initialize the search form
    search_form = SearchForm()

    # Recover the query if it exists
    q = request.args.get('q')

    # Recover the sorting
    if sorting is None:
        sorting = 'Title A-Z'
        if list_type == ListType.GAMES:
            sorting = 'Playtime +'

    # Recover the category
    if category is None:
        category = Status.WATCHING
        if list_type == ListType.MOVIES or list_type == ListType.GAMES:
            category = Status.COMPLETED

    # Recover the template
    html_template = 'medialist_tv.html'
    if list_type == ListType.MOVIES:
        html_template = 'medialist_movies.html'
    elif list_type == ListType.GAMES:
        html_template = 'medialist_games.html'

    # Retrieve the corresponding data depending on the selected category
    if category != 'Stats':
        category, media_data = get_media_query(user.id, list_type, category, genre, sorting, page_val, q)
    else:
        if list_type == ListType.GAMES:
            media_data = get_games_stats(user)
        else:
            media_data = get_more_stats(user, list_type)

    return render_template(html_template, title="{}'s {}".format(user_name, media_list), user=user, username=user_name,
                           user_id=user.id, media_list=media_list, search_form=search_form, search_q=q,
                           category=category, genre=genre, sorting=sorting, page=page_val, data=media_data)


@bp.route("/comment/<media_type>/<media_id>", methods=['GET', 'POST'])
@login_required
def write_comment(media_type, media_id):
    # Check if <media_type> is valid
    try:
        media_type = MediaType(media_type)
        models = get_models_group(media_type)
    except ValueError:
        abort(400)

    # Check if the <media> is in the current user's list
    media = db.session.query(models[0], models[1])\
        .join(models[0], models[0].id == models[1].media_id)\
        .filter(models[0].id == media_id, models[1].user_id == current_user.id).first()
    if not media:
        return '', 400

    form = MediaComment()
    if request.method == 'GET':
        form.comment.data = media[1].comment
        session['back_url'] = request.referrer or '/'
    if form.validate_on_submit():
        comment = form.comment.data
        media[1].comment = comment

        db.session.commit()
        app.logger.info('[{}] added a comment on {} with ID [{}]'.format(current_user.id, media_type, media_id))

        if not comment or comment == '':
            flash('Your comment has been removed (or is empty).', 'warning')
        else:
            flash('Comment successfully added/modified.', 'success')

        return redirect(session['back_url'])

    return render_template('medialist_comment.html', title='Add comment', form=form, media_name=media[0].name)


@bp.route('/media_sheet/<media_type>/<media_id>', methods=['GET', 'POST'])
@login_required
def media_sheet(media_type, media_id):
    # Check if <media_type> is valid
    try:
        media_type = MediaType(media_type)
        models = get_models_group(media_type)
    except ValueError:
        abort(400)

    # Check if <media_id> came from an API
    from_api = request.args.get('search')

    # Check if <media> is in local DB
    media = models[0].media_sheet_check(media_id, from_api=from_api)

    # If <media> does not exist and <api_id> is provived: Add the <media> to DB, else abort.
    if not media:
        if from_api:
            API_model = ApiData.get_API_model(media_type)
            try:
                api_info = API_model().get_details_and_credits_data(media_id)
            except Exception as e:
                flash('Sorry, a problem occured trying to load the media info. Please try again later.', 'warning')
                app.logger.error('[ERROR] - Impossible to get the details and credits from API ({}) ID [{}]: {}'
                                 .format(media_type.value, media_id, e))
                return redirect(request.referrer)
            try:
                media_details = API_model().from_API_to_dict(api_info)
            except Exception as e:
                flash('Sorry, a problem occured trying to load the media info. Please try again later.', 'warning')
                app.logger.error('[ERROR] - Occured trying to parse the API data to dict ({}) ID [{}]: {}'
                                 .format(media_type.value, media_id, e))
                return redirect(request.referrer)
            try:
                media = AddtoDB(media_details, list_type).add_media_to_db()
                db.session.commit()
            except Exception as e:
                flash('Sorry, a problem occured trying to load the media info. Please try again later.', 'warning')
                app.logger.error('[ERROR] - Occured trying to add media ({}) ID [{}] to DB: {}'
                                 .format(media_type.value, media_id, e))
                return redirect(request.referrer)
        else:
            abort(404)

    # If <media> and <api_id> provived: redirect to get URL with media.id instead of media.api_id
    if media and from_api:
        return redirect(url_for('main.media_sheet', media_type=media_type.value, media_id=media.id))

    media_info = MediaDict(media, list_type).create_list_dict()
    title = media_info['display_name']

    # Get the HTML template
    html_template = models[0].media_sheet_template()

    return render_template(html_template, title=title, data=media_info, media_list=list_type.value)


@bp.route("/media_sheet_form/<media_type>/<media_id>", methods=['GET', 'POST'])
@login_required
def media_sheet_form(media_type, media_id):
    if current_user.role == RoleType.USER:
        abort(403)

    form = EditMediaData()

    # Check if <media_type> is valid
    try:
        media_type = MediaType(media_type)
    except ValueError:
        abort(404)

    if media_type == MediaType.SERIES:
        list_type = ListType.SERIES
        media = Series.query.filter_by(id=media_id).first()
    elif media_type == MediaType.ANIME:
        list_type = ListType.ANIME
        media = Anime.query.filter_by(id=media_id).first()
    elif media_type == MediaType.MOVIES:
        list_type = ListType.MOVIES
        media = Movies.query.filter_by(id=media_id).first()

    if not media:
        abort(404)

    if request.method == 'GET':
        form.original_name.data = media.original_name
        form.name.data = media.name
        form.homepage.data = media.homepage
        form.synopsis.data = media.synopsis
        # form.genres.data = ', '.join([r.genre for r in media.genres])
        form.actors.data = ', '.join([r.name for r in media.actors])
        if list_type != ListType.MOVIES:
            form.created_by.data = media.created_by
            form.first_air_date.data = media.first_air_date
            form.last_air_date.data = media.last_air_date
            form.production_status.data = media.status
            form.duration.data = media.duration
            form.origin_country.data = media.origin_country
            form.networks.data = ', '.join([r.network for r in media.networks])
        elif list_type == ListType.MOVIES:
            form.directed_by.data = media.director_name
            form.release_date.data = media.release_date
            form.duration.data = media.duration
            form.original_language.data = media.original_language
            form.tagline.data = media.tagline
            form.budget.data = media.budget
            form.revenue.data = media.revenue
    if form.validate_on_submit():
        if form.cover.data:
            media.image_cover = save_new_cover(form.cover.data, media_type)
        media.original_name = form.original_name.data
        media.name = form.name.data
        media.homepage = form.homepage.data
        media.synopsis = form.synopsis.data
        if list_type != ListType.MOVIES:
            media.created_by = form.created_by.data
            media.first_air_date = form.first_air_date.data
            media.last_air_date = form.last_air_date.data
            media.status = form.production_status.data
            media.duration = form.duration.data
            media.origin_country = form.origin_country.data
        elif list_type == ListType.MOVIES:
            media.director_name = form.directed_by.data
            media.release_date = form.release_date.data
            media.duration = form.duration.data
            media.original_language = form.original_language.data
            media.tagline = form.tagline.data
            media.budget = form.budget.data
            media.revenue = form.revenue.data

        db.session.commit()

        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            if [r.name for r in media.actors] == form.actors.data.split(', '):
                pass
            else:
                for actor in [r.name for r in media.actors]:
                    if list_type == ListType.SERIES:
                        SeriesActors.query.filter_by(media_id=media_id, name=actor).delete()
                    elif list_type == ListType.ANIME:
                        AnimeActors.query.filter_by(media_id=media_id, name=actor).delete()
                    elif list_type == ListType.MOVIES:
                        MoviesActors.query.filter_by(media_id=media_id, name=actor).delete()
                db.session.commit()
                for actor in form.actors.data.split(', '):
                    if list_type == ListType.SERIES:
                        add_actor = SeriesActors(media_id=media_id,
                                                 name=actor)
                    elif list_type == ListType.ANIME:
                        add_actor = AnimeActors(media_id=media_id,
                                                name=actor)
                    elif list_type == ListType.MOVIES:
                        add_actor = MoviesActors(media_id=media_id,
                                                 name=actor)
                    db.session.add(add_actor)
                db.session.commit()

            # Genres
            # if [r.genre for r in element.genres] == form.genres.data.split(', '):
            #     pass
            # else:
            #     for genre in [r.genre for r in element.genres]:
            #         if list_type == ListType.SERIES:
            #             SeriesGenre.query.filter_by(media_id=media_id, genre=genre).delete()
            #         elif list_type == ListType.ANIME:
            #             AnimeGenre.query.filter_by(media_id=media_id, genre=genre).delete()
            #         elif list_type == ListType.MOVIES:
            #             MoviesGenre.query.filter_by(media_id=media_id, genre=genre).delete()
            #     db.session.commit()
            #     for genre in form.genres.data.split(', '):
            #         if list_type == ListType.SERIES:
            #             add_genre = SeriesGenre(media_id=media_id,
            #                                     genre=genre)
            #         elif list_type == ListType.ANIME:
            #             add_genre = AnimeGenre(media_id=media_id,
            #                                    genre=genre)
            #         elif list_type == ListType.MOVIES:
            #             add_genre = MoviesGenre(media_id=media_id,
            #                                     genre=genre)
            #         db.session.add(add_genre)
            #     db.session.commit()

            # Networks
        elif list_type != ListType.MOVIES:
            if [r.network for r in media.networks] == form.networks.data.split(', '):
                pass
            else:
                for network in [r.network for r in media.networks]:
                    if list_type == ListType.SERIES:
                        SeriesNetwork.query.filter_by(media_id=media_id, network=network).delete()
                    elif list_type == ListType.ANIME:
                        AnimeNetwork.query.filter_by(media_id=media_id, network=network).delete()
                db.session.commit()
                for network in form.networks.data.split(', '):
                    if list_type == ListType.SERIES:
                        add_network = SeriesNetwork(media_id=media_id,
                                                    network=network)
                    elif list_type == ListType.ANIME:
                        add_network = AnimeNetwork(media_id=media_id,
                                                   network=network)
                    db.session.add(add_network)
                db.session.commit()

        return redirect(url_for('main.media_sheet', media_type=media_type.value, media_id=media_id))

    return render_template('media_sheet_form.html', title='Media Form', form=form, media_type=media_type.value)


@bp.route("/your_next_airing", methods=['GET', 'POST'])
@login_required
def your_next_airing():
    next_series_airing = get_next_airing(ListType.SERIES)
    next_anime_airing = get_next_airing(ListType.ANIME)
    next_movies_airing = get_next_airing(ListType.MOVIES)

    series_dates = []
    for series in next_series_airing:
        series_dates.append(change_air_format(series[0].next_episode_to_air))

    anime_dates = []
    for anime in next_anime_airing:
        anime_dates.append(change_air_format(anime[0].next_episode_to_air))

    movies_dates = []
    for movies in next_movies_airing:
        movies_dates.append(change_air_format(movies[0].release_date))

    return render_template('your_next_airing.html',title='Your next airing', airing_series=next_series_airing,
                           series_dates=series_dates, airing_anime=next_anime_airing, anime_dates=anime_dates,
                           airing_movies=next_movies_airing, movies_dates=movies_dates)


@bp.route('/search_media', methods=['GET', 'POST'])
@login_required
def search_media():
    search = request.args.get('search')
    page = request.args.get('page', 1)

    if not search or len(search) == 0:
        return redirect(request.referrer)

    # Get the series, anime and movies results
    try:
        data_search = ApiData().TMDb_search(search, page=page)
    except Exception as e:
        data_search = {}
        app.logger.error('[SYSTEM] - Error requesting the TMDb API: {}'.format(e))
        flash('Sorry, an error occured, the TMDb API is unreachable for now.', 'warning')

    if data_search.get("total_results", 0) == 0:
        flash('Sorry, no results found for your query.', 'warning')
        return redirect(request.referrer)

    # Recover 1 page of results (20 max, series, anime, movies) without peoples
    media_results = []
    for result in data_search["results"]:
        if result.get('known_for_department'):
            continue

        media_data = {'name': result.get('original_title') or result.get('original_name'),
                      'overview': result.get('overview'),
                      'first_air_date': result.get('first_air_date') or result.get('release_date'),
                      'api_id': result['id']}

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
            media_data['media'] = 'Series'
            if result['origin_country'] == 'JP' or result['original_language'] == 'ja' \
                    and 16 in result['genre_ids']:
                media_data['media_type'] = ListType.ANIME.value
                media_data['name'] = result['name']
                media_data['media'] = 'Anime'
                media_results.append(media_data)
            else:
                media_data['media_type'] = ListType.SERIES.value
                media_results.append(media_data)
        elif result['media_type'] == 'movie':
            media_data['media'] = 'Movies'
            media_data['media_type'] = ListType.MOVIES.value
            media_data['url'] = f"https://www.themoviedb.org/movie/{result['id']}"
            if result['original_language'] == 'ja' and 16 in result['genre_ids']:
                media_data['name'] = result['title']
            media_results.append(media_data)

    games_results = []
    if current_user.add_games:
        # Get the games results
        try:
            games_data = ApiData().IGDB_search(search)
        except Exception as e:
            games_data = {}
            app.logger.error('[ERROR] - Requesting the IGDB API: {}'.format(e))
            flash('Sorry, an error occured, the IGDB API is unreachable for now.', 'warning')

        # Recover the games results
        if len(games_data) > 0:
            for result in games_data:
                media_data = {'name': result.get('name'),
                              'overview': result.get('storyline'),
                              'first_air_date': change_air_format(result.get('first_release_date'), games=True),
                              'api_id': result.get('id'),
                              'poster_path': url_for('static', filename="covers/games_covers/default.jpg")}

                # Recover the poster_path or take a default image
                if result.get('cover'):
                    igdb_cover_link = "https://images.igdb.com/igdb/image/upload/t_1080p/"
                    media_data['poster_path'] = "{}{}.jpg".format(igdb_cover_link, result['cover']['image_id'])

                # Put data in different lists in function of media type
                media_data['media'] = 'Games'
                media_data['media_type'] = ListType.GAMES.value

                games_results.append(media_data)

    media_results += games_results

    return render_template("media_search.html", title="Search", all_results=media_results, search=search,
                           page=int(page), total_results=data_search['total_results'])


@bp.route('/graph_test', methods=['GET', 'POST'])
@login_required
def test_graph_date():
    series_data = UserLastUpdate.query.filter_by(user_id=3, media_type=ListType.SERIES)\
        .group_by(UserLastUpdate.date).all()

    all_dates = {}
    for d in series_data:
        try:
            date = d.date.strftime('%b-%Y')
            if d.new_status == Status.COMPLETED:
                if all_dates.get('{}'.format(date)) is not None:
                    all_dates['{}'.format(date)] += 1
                else:
                    all_dates['{}'.format(date)] = 1
        except:
            pass

    series_labels = ", ".join([k for k in all_dates.keys()])
    series_data = ", ".join([str(k) for k in all_dates.values()])

    anime_data = UserLastUpdate.query.filter_by(user_id=3, media_type=ListType.ANIME)\
        .group_by(UserLastUpdate.date).all()

    all_dates = {}
    for d in anime_data:
        try:
            date = d.date.strftime('%b-%Y')
            if d.new_status == Status.COMPLETED:
                if all_dates.get('{}'.format(date)) is not None:
                    all_dates['{}'.format(date)] += 1
                else:
                    all_dates['{}'.format(date)] = 1
        except:
            pass

    anime_labels = ", ".join([k for k in all_dates.keys()])
    anime_data = ", ".join([str(k) for k in all_dates.values()])

    movies_data = UserLastUpdate.query.filter_by(user_id=3, media_type=ListType.MOVIES)\
        .group_by(UserLastUpdate.date).all()

    all_dates = {}
    for d in movies_data:
        try:
            date = d.date.strftime('%b-%Y')
            if d.new_status == Status.COMPLETED:
                if all_dates.get('{}'.format(date)) is not None:
                    all_dates['{}'.format(date)] += 1
                else:
                    all_dates['{}'.format(date)] = 1
        except:
            pass

    movies_labels = ", ".join([k for k in all_dates.keys()])
    movies_data = ", ".join([str(k) for k in all_dates.values()])

    games_data = UserLastUpdate.query.filter_by(user_id=3, media_type=ListType.GAMES)\
        .group_by(UserLastUpdate.date).all()

    all_dates = {}
    for d in games_data:
        try:
            date = d.date.strftime('%b-%Y')
            if d.new_status == Status.COMPLETED:
                if all_dates.get('{}'.format(date)) is not None:
                    all_dates['{}'.format(date)] += 1
                else:
                    all_dates['{}'.format(date)] = 1
        except:
            pass

    games_labels = ", ".join([k for k in all_dates.keys()])
    games_data = ", ".join([str(k) for k in all_dates.values()])

    return render_template('graph_test.html', title='Graph_test', series_labels=series_labels, series_data=series_data,
                           games_labels=games_labels, games_data=games_data, movies_labels=movies_labels,
                           movies_data=movies_data, anime_labels=anime_labels, anime_data=anime_data)


# --- AJAX Methods -----------------------------------------------------------------------------------------------


@bp.route('/update_element_season', methods=['POST'])
@login_required
def update_element_season():
    try:
        json_data = request.get_json()
        new_season = int(json_data['season']) + 1
        media_id = int(json_data['element_id'])
        media_list = json_data['element_type']
    except:
        return '', 400

    # Check if the <media_list> exist and is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400
    finally:
        if list_type == ListType.MOVIES:
            return '', 400

    # Check if the media exists
    media = check_media(media_id, list_type)
    if not media or media[1].status == Status.RANDOM or media[1].status == Status.PLAN_TO_WATCH:
        return '', 400

    # Check if the season number is between 1 and <last_season>
    if 1 > new_season > media[0].eps_per_season[-1].season:
        return '', 400

    # Get the old data
    old_season = media[1].current_season
    old_episode = media[1].last_episode_watched
    old_watched = media[1].eps_watched

    # Set the new data
    new_watched = sum([x.episodes for x in media[0].eps_per_season[:new_season-1]]) + 1
    media[1].current_season = new_season
    media[1].last_episode_watched = 1
    media[1].eps_watched = new_watched + (media[1].rewatched * media[0].total_episodes)
    app.logger.info('[User {}] - [Media {}] - [ID {}] season updated from {} to {}'
                    .format(current_user.id, list_type.value.replace('list', ''), media_id, old_season, new_season))

    # Commit the changes
    db.session.commit()

    # Set the last updates
    set_last_update(media=media[0], media_type=list_type, old_season=old_season, new_season=new_season, new_episode=1,
                    old_episode=old_episode)

    # Compute the new time spent
    compute_time_spent(media=media[0], list_type=list_type, old_watched=old_watched, new_watched=new_watched)

    # Commit the changes
    db.session.commit()

    return '', 204


@bp.route('/update_element_episode', methods=['POST'])
@login_required
def update_element_episode():
    try:
        json_data = request.get_json()
        new_episode = int(json_data['episode']) + 1
        media_id = int(json_data['element_id'])
        media_list = json_data['element_type']
    except:
        return '', 400

    # Check if the media_list exist and is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400
    finally:
        if list_type == ListType.MOVIES:
            return '', 400

    # Check if the media exists
    media = check_media(media_id, list_type)
    if not media or media[1].status == Status.RANDOM or media[1].status == Status.PLAN_TO_WATCH:
        return '', 400

    # Check if the episode number is between 1 and <last_episode>
    if 1 > new_episode > media[0].eps_per_season[media[1].current_season - 1].episodes:
        return '', 400

    # Get the old data
    old_season = media[1].current_season
    old_episode = media[1].last_episode_watched
    old_watched = media[1].eps_watched

    # Set the new data
    new_watched = sum([x.episodes for x in media[0].eps_per_season[:old_season-1]]) + new_episode
    media[1].last_episode_watched = new_episode
    media[1].eps_watched = new_watched + (media[1].rewatched * media[0].total_episodes)
    app.logger.info('[User {}] {} [ID {}] episode updated from {} to {}'
                    .format(current_user.id, list_type.value.replace('list', ''), media_id, old_episode, new_episode))

    # Commit the changes
    db.session.commit()

    # Set the last updates
    set_last_update(media=media[0], media_type=list_type, old_season=old_season, new_season=old_season,
                    old_episode=old_episode, new_episode=new_episode)

    # Compute the new time spent
    compute_time_spent(media=media[0], old_watched=old_watched, new_watched=new_watched, list_type=list_type)

    # Commit the changes
    db.session.commit()

    return '', 204


@bp.route('/change_element_category', methods=['POST'])
@login_required
def change_element_category():
    try:
        json_data = request.get_json()
        media_new_cat = json_data['status']
        media_id = int(json_data['element_id'])
        media_list = json_data['element_type']
    except:
        return '', 400

    # Check the <media_list> parameter
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    # Check if the <status> parameter
    new_status = check_cat_type(list_type, media_new_cat)
    if not new_status:
        return '', 400

    # Recover the media
    media = check_media(media_id, list_type)
    if not media:
        return '', 400

    # Get the old status
    old_status = media[1].status

    # Set the new status
    media[1].status = new_status

    if list_type != ListType.GAMES:
        # Get the old rewatched
        old_rewatch = media[1].rewatched
        # Reset the rewatched time multiplier
        media[1].rewatched = 0

    # Set and change accordingly <last_episode_watched>, <current_season> and <eps_watched> for anime and series
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        old_watched = media[1].eps_watched
        if new_status == Status.COMPLETED:
            media[1].current_season = len(media[0].eps_per_season)
            media[1].last_episode_watched = media[0].eps_per_season[-1].episodes
            media[1].eps_watched = media[0].total_episodes
            new_watched = media[0].total_episodes
        elif new_status == Status.RANDOM or new_status == Status.PLAN_TO_WATCH:
            media[1].current_season = 1
            media[1].last_episode_watched = 0
            media[1].eps_watched = 0
            new_watched = 0
        else:
            new_watched = old_watched
    elif list_type == ListType.MOVIES:
        if new_status == Status.COMPLETED:
            media[1].eps_watched = 1
        else:
            media[1].eps_watched = 0

    # Set the last updates
    set_last_update(media=media[0], media_type=list_type, old_status=old_status, new_status=new_status)

    # Compute the new time spent
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        compute_time_spent(media=media[0], list_type=list_type, old_watched=old_watched, new_watched=new_watched,
                           old_rewatch=old_rewatch)
    elif list_type == ListType.MOVIES:
        compute_time_spent(media=media[0], list_type=list_type, movie_status=media[1].status, old_rewatch=old_rewatch,
                           movie_duration=media[0].duration)

    db.session.commit()
    app.logger.info("[User {}] {}'s category [ID {}] changed from {} to {}."
                    .format(current_user.id, media_id, list_type.value.replace('list', ''), old_status.value,
                            new_status.value))

    return '', 204


@bp.route('/update_score', methods=['POST'])
@login_required
def update_score():
    try:
        json_data = request.get_json()
        new_score = json_data['score']
        media_id = int(json_data['element_id'])
        media_list = json_data['element_type']
    except:
        return '', 400

    # Check if <media_list> exist and valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    # Check that <new_score> is '---' or between [0-10]
    try:
        if 0 > float(new_score) > 10:
            return '', 400
    except:
        new_score = -1

    media = check_media(media_id, list_type)
    if not media:
        return '', 400

    # Get the old data
    old_score = media[1].score

    # Set the new data
    media[1].score = new_score
    app.logger.info('[{}] Series ID {} score updated from {} to {}'
                    .format(current_user.id, media_id, old_score, new_score))

    # Commit the changes
    db.session.commit()

    return '', 204


@bp.route('/update_playtime', methods=['POST'])
@login_required
def update_playtime():
    try:
        json_data = request.get_json()
        new_playtime = int(json_data['playtime'])*60        # To get minutes
        media_id = int(json_data['media_id'])
        media_list = json_data['media_type']
    except:
        return '', 400

    # Check if <media_list> exist and valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    media = check_media(media_id, list_type)
    if not media:
        return '', 400

    # Get the old data
    old_playtime = media[1].playtime

    # Set the new data
    media[1].playtime = new_playtime
    app.logger.info('[{}] Games ID {} playtime updated from {} to {}'
                    .format(current_user.id, media_id, old_playtime, new_playtime))

    compute_time_spent(media=media[0], list_type=list_type, old_gametime=old_playtime, new_gametime=new_playtime)

    # Commit the changes
    db.session.commit()

    return '', 204


@bp.route('/update_rewatch', methods=['POST'])
@login_required
def update_rewatch():
    try:
        json_data = request.get_json()
        new_rewatch = int(json_data['rewatch'])
        media_id = int(json_data['element_id'])
        media_list = json_data['element_type']
    except:
        return '', 400

    # Check if the <media_list> exist and is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    # Check that <new_rewatch> is between [0-10]
    if 0 > new_rewatch > 10:
        return '', 400

    media = check_media(media_id, list_type)
    if not media or media[1].status != Status.COMPLETED:
        return '', 400

    # Get the old data
    old_rewatch = media[1].rewatched

    # Set the new data
    media[1].rewatched = new_rewatch
    app.logger.info('[{}] Series ID {} re-watched {}x times'.format(current_user.id, media_id, new_rewatch))

    # total eps/movies watched
    if list_type != ListType.MOVIES:
        media[1].eps_watched = media[0].total_episodes + (new_rewatch * media[0].total_episodes)
    elif list_type == ListType.MOVIES:
        media[1].eps_watched = 1 + new_rewatch

    # Commit the changes
    db.session.commit()

    # Compute the new time spent
    if list_type != ListType.MOVIES:
        compute_time_spent(media=media[0], list_type=list_type, old_rewatch=old_rewatch, new_rewatch=new_rewatch)
    elif list_type == ListType.MOVIES:
        compute_time_spent(media=media[0], list_type=list_type, movie_status=media[1].status, old_rewatch=old_rewatch,
                           new_rewatch=new_rewatch)

    return '', 204


@bp.route('/add_favorite', methods=['POST'])
@login_required
def add_favorite():
    try:
        json_data = request.get_json()
        media_id = int(json_data['element_id'])
        media_list = json_data['element_type']
        favorite = bool(json_data['favorite'])
    except:
        return '', 400

    # Check if the <media_list> exist and is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    models = get_models_group(list_type)

    # Check if the <media_id> is in the current user's list
    media = models[1].query.filter_by(user_id=current_user.id, media_id=media_id).first()
    if not media:
        return '', 400

    # Add <favorite> and commit the changes
    media.favorite = favorite
    db.session.commit()

    return '', 204


@bp.route('/add_element', methods=['POST'])
@login_required
def add_element():
    try:
        json_data = request.get_json()
        media_id = json_data['element_id']
        media_list = json_data['element_type']
        media_cat = json_data['element_cat']
    except:
        return '', 400

    # Check if the <media_list> exist and is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    # Check if <status> is valid compared to <list_type>
    new_status = check_cat_type(list_type, media_cat)
    if not new_status:
        return '', 400

    # Check if the <media> exists
    media = check_media(media_id, list_type, add=True)
    if not media:
        return '', 400

    # Setup the <season>, <episode> and <category> of the <media>
    new_watched = 1
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        new_season = 1
        new_episode = 1
        if new_status == Status.COMPLETED:
            new_season = len(media.eps_per_season)
            new_episode = media.eps_per_season[-1].episodes
            new_watched = media.total_episodes
        elif new_status == Status.RANDOM or new_status == Status.PLAN_TO_WATCH:
            new_episode = 0
            new_watched = 0
    elif list_type == ListType.MOVIES:
        if new_status != Status.COMPLETED:
            new_watched = 0

    # Add <media> to the <user>
    if list_type == ListType.SERIES:
        user_list = SeriesList(user_id=current_user.id,
                               media_id=media.id,
                               current_season=new_season,
                               last_episode_watched=new_episode,
                               status=new_status,
                               eps_watched=new_watched)
    elif list_type == ListType.ANIME:
        user_list = AnimeList(user_id=current_user.id,
                              media_id=media.id,
                              current_season=new_season,
                              last_episode_watched=new_episode,
                              status=new_status,
                              eps_watched=new_watched)
    elif list_type == ListType.MOVIES:
        user_list = MoviesList(user_id=current_user.id,
                               media_id=media.id,
                               status=new_status,
                               eps_watched=new_watched)
    elif list_type == ListType.GAMES:
        user_list = GamesList(user_id=current_user.id,
                              media_id=media.id,
                              status=new_status,
                              completion=False,
                              playtime=0)

    # Commit the changes
    db.session.add(user_list)
    db.session.commit()
    app.logger.info('[User {}] {} Added [ID {}] in the category: {}'
                    .format(current_user.id, list_type.value.replace('list', ''), media_id, new_status.value))

    # Set the last update
    set_last_update(media=media, media_type=list_type, new_status=new_status)

    # Compute the new time spent
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        compute_time_spent(media=media, new_watched=new_watched, list_type=list_type)
    elif list_type == ListType.MOVIES:
        compute_time_spent(media=media, list_type=list_type, movie_status=new_status, movie_add=True)

    # Commit the last updates and the new time spent changes
    db.session.commit()

    return '', 204


@bp.route('/delete_element', methods=['POST'])
@login_required
def delete_element():
    try:
        json_data = request.get_json()
        media_id = int(json_data['delete'])
        media_list = json_data['element_type']
    except:
        return '', 400

    # Check if the <media_list> exist and is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    media = check_media(media_id, list_type)
    if not media:
        return '', 400

    # Get the old data
    if list_type != ListType.GAMES:
        old_rewatch = media[1].rewatched

    # Compute the new time spent
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        old_watched = media[1].eps_watched
        compute_time_spent(media=media[0], old_watched=old_watched, list_type=list_type, old_rewatch=old_rewatch)
    elif list_type == ListType.MOVIES:
        compute_time_spent(media=media[0], list_type=list_type, movie_status=media[1].status, movie_delete=True,
                           old_rewatch=old_rewatch)
    elif list_type == ListType.GAMES:
        compute_time_spent(media=media[0], list_type=list_type, old_gametime=media[1].playtime)

    # Delete the media from the user's list
    db.session.delete(media[1])
    db.session.commit()
    app.logger.info('[User {}] {} [ID {}] successfully removed.'
                    .format(current_user.id, list_type.value.replace('list', ''), media_id))

    return '', 204


@bp.route('/lock_media', methods=['POST'])
@login_required
def lock_media():
    try:
        json_data = request.get_json()
        media_id = json_data['element_id']
        media_list = json_data['element_type']
        lock_status = bool(json_data['lock_status'])
    except:
        return '', 400

    # Check if the user is admin or manager
    if current_user.role == RoleType.USER:
        return '', 403

    # Check if <list_type> exist and is valid
    try:
        list_type = ListType(media_list)
    except ValueError:
        return '', 400

    models = get_models_group(list_type)
    media = models[0].query.filter_by(id=media_id).first()

    if not media:
        return '', 400

    media.lock_status = lock_status
    db.session.commit()

    return '', 204


@bp.route('/autocomplete', methods=['GET'])
@login_required
def autocomplete():
    search = request.args.get('q')

    # Get the users results
    users = User.query.filter(User.username.like('%'+search+'%')).all()
    users_results = []
    for user in users:
        users_results.append(Autocomplete(user).get_user_dict())

    # Get the media results
    try:
        media_data = ApiData().TMDb_search(search)
    except Exception as e:
        media_data = {}
        app.logger.error('[ERROR] - Requesting the TMDB API: {}'.format(e))

    media_results = []
    if media_data.get('total_results', 0) or 0 > 0:
        for i, result in enumerate(media_data["results"]):
            if i >= media_data["total_results"] or i > 19 or len(media_results) >= 7:
                break
            if result.get('known_for_department'):
                continue
            media_results.append(Autocomplete(result).get_autocomplete_dict())

    games_results = []
    if current_user.add_games:
        # Get the games results
        try:
            games_data = ApiData().IGDB_search(search)
        except Exception as e:
            games_data = {}
            app.logger.error('[ERROR] - Requesting the IGDB API: {}'.format(e))

        if len(games_data) > 0:
            for result in games_data:
                if len(games_results) >= 5:
                    break
                games_results.append(Autocomplete(result).get_games_autocomplete_dict())

    # Create the <total_results> list
    total_results = media_results + users_results + games_results
    if len(total_results) == 0:
        return jsonify(search_results=[{'nb_results': 0, 'category': None}]), 200

    total_results = sorted(total_results, key=lambda i: i['category'])

    return jsonify(search_results=total_results), 200


@bp.route('/read_notifications', methods=['GET'])
@login_required
def read_notifications():
    # Change the last time the <current_user> looked at the notifications and commit the changes
    current_user.last_notif_read_time = datetime.utcnow()
    db.session.commit()

    # Get the user's notfications
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
