import sys
from MyLists import db, app
from rq import get_current_job
from MyLists.API_data import ApiData
from MyLists.models import RedisTasks
from MyLists.main.add_db import AddtoDB
from MyLists.main.media_object import MediaDetails
from MyLists.main.functions import set_last_update, compute_time_spent
from MyLists.models import Movies, MoviesList, Status, ListType, Series, Anime, SeriesList, AnimeList


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        task = RedisTasks.query.get(job.get_id())
        if progress >= 100:
            task.complete = True
        db.session.commit()


def add_id_to_db(ids_to_add, list_type, begin=0, maxi=0):
    series_id = []
    anime_id = []
    movies_id = []
    for i, tmdb_id in enumerate(ids_to_add):
        if list_type != ListType.MOVIES:
            _set_task_progress(i * (maxi/len(ids_to_add)))
        else:
            _set_task_progress(begin + i*((90-begin)/len(ids_to_add)))
        try:
            api_data = ApiData().get_details_and_credits_data(tmdb_id, list_type)
            if list_type != ListType.MOVIES:
                genres = [g['id'] for g in api_data.get('genres')]
                if api_data.get('origin_country') == 'JP' or api_data.get('original_language') == 'ja' and 16 in genres:
                    list_type = ListType.ANIME
                else:
                    list_type = ListType.SERIES
            media_details = MediaDetails(api_data, list_type).get_media_details()
            media = AddtoDB(media_details, list_type).add_media_to_db()

            if list_type == ListType.SERIES:
                series_id.append(media.id)
            elif list_type == ListType.ANIME:
                anime_id.append(media.id)
            elif list_type == ListType.MOVIES:
                movies_id.append(media.id)

        except Exception as e:
            print(e)

    db.session.commit()
    return series_id, anime_id, movies_id


def add_id_to_user(user_id, ids_to_add, list_type):
    if list_type == ListType.SERIES:
        query = Series.query.filter(Series.id.in_(ids_to_add)).all()
    elif list_type == ListType.ANIME:
        query = Anime.query.filter(Anime.id.in_(ids_to_add)).all()
    elif list_type == ListType.MOVIES:
        query = Movies.query.filter(Movies.id.in_(ids_to_add)).all()

    data = []
    for media in query:
        if list_type == ListType.SERIES:
            user_list = SeriesList(user_id=user_id,
                                   media_id=media.id,
                                   current_season=len(media.eps_per_season),
                                   last_episode_watched=media.eps_per_season[-1].episodes,
                                   status=Status.COMPLETED,
                                   eps_watched=media.total_episodes)
        elif list_type == ListType.ANIME:
            user_list = AnimeList(user_id=user_id,
                                  media_id=media.id,
                                  current_season=len(media.eps_per_season),
                                  last_episode_watched=media.eps_per_season[-1].episodes,
                                  status=Status.COMPLETED,
                                  eps_watched=media.total_episodes)
        elif list_type == ListType.MOVIES:
            user_list = MoviesList(user_id=user_id,
                                   media_id=media.id,
                                   status=Status.COMPLETED,
                                   eps_watched=1)

        db.session.add(user_list)
        app.logger.info('[User {}] {} Added [ID {}] in the category: Completed'
                        .format(user_id, list_type.value.replace('list', ''), media.id))

        # Set the last update
        set_last_update(media=media, media_type=list_type, new_status=Status.COMPLETED, user_id=user_id)

        # Compute the new time spent
        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            compute_time_spent(media=media, new_watched=media.total_episodes, list_type=list_type, user_id=user_id)
        elif list_type == ListType.MOVIES:
            compute_time_spent(media=media, list_type=list_type, movie_status=Status.COMPLETED, movie_add=True,
                               user_id=user_id)

        if list_type == ListType.SERIES:
            covers_path = "../static/covers/series_covers"
        elif list_type == ListType.ANIME:
            covers_path = "../static/covers/anime_covers"
        elif list_type == ListType.MOVIES:
            covers_path = "../static/covers/movies_covers"

        data.append({'name': media.name,
                     'cover': f'{covers_path}/{media.image_cover}',
                     'type': list_type.value.replace('list', '')})

    db.session.commit()
    return data


def get_the_ids(ids_to_add, movies=False):
    ids_in_db = []
    if movies:
        DB = [Movies]
    else:
        DB = [Series, Anime]
    for media in DB:
        query = media.query.filter(media.themoviedb_id.in_(ids_to_add)).all()
        try:
            ids_in_db.append([q.id for q in query])
            tmp = [q.themoviedb_id for q in query]
        except:
            ids_in_db.append([])
            tmp = []
        ids_to_add = list(set(ids_to_add) - set(tmp))

    return ids_to_add, ids_in_db


def check_in_user_list(user_id, ids_to_check, movies=False):
    ids_to_add = []
    if movies:
        DB = [MoviesList]
    else:
        DB = [SeriesList, AnimeList]
    for i, medialist in enumerate(DB):
        query = medialist.query.filter(medialist.media_id.in_(ids_to_check[i]), medialist.user_id == user_id).all()
        try:
            tmp = [q.id for q in query]
        except:
            tmp = []
        ids_to_add.append(list(set(ids_to_check[i]) - set(tmp)))

    return ids_to_add


def import_list(user_id, csv_data):
    _set_task_progress(0)
    try:
        try:
            tv_data = csv_data.loc['tv']
            tv_data = tv_data['TMDb ID']
        except:
            tv_data = None

        try:
            movies_data = csv_data.loc['movie']
            movies_data = movies_data['TMDb ID']
        except:
            movies_data = None

        if tv_data is None and movies_data is None:
            _set_task_progress(100)
            return None

        # First are TMDb IDs to add from API, second are intern IDs to check if not already in user's list
        tv_tmdb_ids_to_add, tv_ids_in_db = get_the_ids(tv_data, movies=False)
        movies_tmdb_ids_to_add, movies_id_in_db = get_the_ids(movies_data, movies=True)

        # Recover the intern IDs to add that are not already in the user's list
        tv_ids_to_add = check_in_user_list(user_id, tv_ids_in_db, movies=False)
        movies_ids_to_add = check_in_user_list(user_id, movies_id_in_db, movies=True)

        # Get the total number of TMDb IDs to add to get a time estimation
        tv_time = len(tv_tmdb_ids_to_add)
        movie_time = len(movies_tmdb_ids_to_add)
        total_time = tv_time + movie_time

        # Add the TMDb IDs to the intern DB
        series_id, anime_id, _ = add_id_to_db(tv_tmdb_ids_to_add, ListType.SERIES, maxi=(tv_time/total_time)*100)
        _, _, movies_id = add_id_to_db(movies_tmdb_ids_to_add, ListType.MOVIES, begin=(tv_time/total_time)*100)

        # Group the series, anime and movies together
        all_series_id = series_id + tv_ids_to_add[0]
        all_anime_id = anime_id + tv_ids_to_add[1]
        all_movies_id = movies_id + movies_ids_to_add[0]

        # Add each media type to the user
        add_id_to_user(user_id, all_series_id, ListType.SERIES)
        add_id_to_user(user_id, all_anime_id, ListType.ANIME)
        add_id_to_user(user_id, all_movies_id, ListType.MOVIES)

    except:
        app.logger.error('[RQ ERROR]', exc_info=sys.exc_info())
    finally:
        _set_task_progress(100)

