import os
import json
import logging
from pathlib import Path
from MyLists import app, db
from sqlalchemy import and_, desc
from MyLists.API_data import ApiData
from datetime import datetime, timedelta
from MyLists.main.media_object import MediaDetails
from MyLists.general.functions import compute_media_time_spent
from MyLists.models import Series, SeriesList, SeriesActors, SeriesGenre, SeriesNetwork, SeriesEpisodesPerSeason, \
    UserLastUpdate, Notifications, ListType, Anime, AnimeList, AnimeActors, AnimeGenre, AnimeNetwork, Status, Movies, \
    AnimeEpisodesPerSeason, MoviesList, MoviesActors, MoviesGenre, GlobalStats, MyListsStats, User, RoleType


def remove_non_list_media():
    app.logger.info('###################################################################')
    app.logger.info('[SYSTEM] - Starting automatic media remover')

    # Series remover
    series = db.session.query(Series, SeriesList).outerjoin(SeriesList, SeriesList.media_id == Series.id).all()
    count = 0
    to_delete = []
    for tv_series in series:
        if not tv_series[1]:
            to_delete.append(tv_series[0].id)
    for deletion in to_delete:
        Series.query.filter_by(id=deletion).delete()
        SeriesActors.query.filter_by(media_id=deletion).delete()
        SeriesGenre.query.filter_by(media_id=deletion).delete()
        SeriesNetwork.query.filter_by(media_id=deletion).delete()
        SeriesEpisodesPerSeason.query.filter_by(media_id=deletion).delete()
        UserLastUpdate.query.filter_by(media_type=ListType.SERIES, media_id=deletion).delete()
        Notifications.query.filter_by(media_type='serieslist', media_id=deletion).delete()
        count += 1

        app.logger.info('Removed series with ID: [{}]'.format(deletion))
    app.logger.info('Total series removed: {}'.format(count))

    # Anime remover
    anime = db.session.query(Anime, AnimeList).outerjoin(AnimeList, AnimeList.media_id == Anime.id).all()
    count = 0
    to_delete = []
    for tv_anime in anime:
        if not tv_anime[1]:
            to_delete.append(tv_anime[0].id)
    for deletion in to_delete:
        Anime.query.filter_by(id=deletion).delete()
        AnimeActors.query.filter_by(media_id=deletion).delete()
        AnimeGenre.query.filter_by(media_id=deletion).delete()
        AnimeNetwork.query.filter_by(media_id=deletion).delete()
        AnimeEpisodesPerSeason.query.filter_by(media_id=deletion).delete()
        UserLastUpdate.query.filter_by(media_type=ListType.ANIME, media_id=deletion).delete()
        Notifications.query.filter_by(media_type='animelist', media_id=deletion).delete()
        count += 1

        app.logger.info('Removed anime with ID: [{}]'.format(deletion))
    app.logger.info('Total anime removed: {}'.format(count))

    # Movies remover
    movies = db.session.query(Movies, MoviesList).outerjoin(MoviesList, MoviesList.media_id == Movies.id).all()
    count = 0
    to_delete = []
    for movie in movies:
        if not movie[1]:
            to_delete.append(movie[0].id)
    for deletion in to_delete:
        Movies.query.filter_by(id=deletion).delete()
        MoviesActors.query.filter_by(media_id=deletion).delete()
        MoviesGenre.query.filter_by(media_id=deletion).delete()
        UserLastUpdate.query.filter_by(media_type=ListType.MOVIES, media_id=deletion).delete()
        Notifications.query.filter_by(media_type='movieslist', media_id=deletion).delete()
        count += 1

        app.logger.info('Removed movie with ID: [{}]'.format(deletion))
    app.logger.info('Total movies removed: {}'.format(count))

    db.session.commit()
    app.logger.info('[SYSTEM] - Finished Automatic media remover')
    app.logger.info('###################################################################')


def remove_old_covers():
    app.logger.info('###################################################################')
    app.logger.info('[SYSTEM] - Starting automatic covers remover')

    # Series old cover remover
    series = Series.query.all()
    path_series_covers = Path(app.root_path, 'static/covers/series_covers/')

    images_in_db = []
    for tv_show in series:
        images_in_db.append(tv_show.image_cover)

    images_saved = []
    for file in os.listdir(path_series_covers):
        images_saved.append(file)

    count = 0
    for image in images_saved:
        if image not in images_in_db and image != 'default.jpg':
            os.remove('{0}/{1}'.format(path_series_covers, image))
            app.logger.info('Removed old series cover with name: {}'.format(image))
            count += 1
    app.logger.info('Total old series covers deleted: {}'.format(count))

    # Anime old cover remover
    anime = Anime.query.all()
    path_anime_covers = Path(app.root_path, 'static/covers/anime_covers/')

    images_in_db = []
    for tv_show in anime:
        images_in_db.append(tv_show.image_cover)

    images_saved = []
    for file in os.listdir(path_anime_covers):
        images_saved.append(file)

    count = 0
    for image in images_saved:
        if image not in images_in_db and image != 'default.jpg':
            os.remove('{0}/{1}'.format(path_anime_covers, image))
            app.logger.info('Removed old anime cover with name: {}'.format(image))
            count += 1
    app.logger.info('Total old anime covers deleted: {}'.format(count))

    # Movies old cover remover
    movies = Movies.query.all()
    path_movies_covers = Path(app.root_path, 'static/covers/movies_covers/')

    images_in_db = []
    for movie in movies:
        images_in_db.append(movie.image_cover)

    images_saved = []
    for file in os.listdir(path_movies_covers):
        images_saved.append(file)

    count = 0
    for image in images_saved:
        if image not in images_in_db and image != 'default.jpg':
            os.remove('{0}/{1}'.format(path_movies_covers, image))
            app.logger.info('Removed old movie cover with name: {}'.format(image))
            count += 1
    app.logger.info('Total old movies covers deleted: {}'.format(count))

    app.logger.info('[SYSTEM] - Finished automatic covers remover')
    app.logger.info('###################################################################')


def refresh_element_data(api_id, list_type):
    media_data = ApiData().get_details_and_credits_data(api_id, list_type)
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        data = MediaDetails(media_data, list_type, updating=True).get_media_details()
        if not data['tv_data']:
            return None
    elif list_type == ListType.MOVIES:
        data = MediaDetails(media_data, list_type, updating=True).get_media_details()
        if not data['movies_data']:
            return None

    # Update the main details for each media
    if list_type == ListType.SERIES:
        Series.query.filter_by(themoviedb_id=api_id).update(data['tv_data'])
    elif list_type == ListType.ANIME:
        Anime.query.filter_by(themoviedb_id=api_id).update(data['tv_data'])
    elif list_type == ListType.MOVIES:
        Movies.query.filter_by(themoviedb_id=api_id).update(data['movies_data'])

    # Commit the new changes
    db.session.commit()

    # Check the episodes/seasons
    if list_type != ListType.MOVIES:
        if list_type == ListType.SERIES:
            media = Series.query.filter_by(themoviedb_id=api_id).first()
            old_seas_eps = [n.episodes for n in SeriesEpisodesPerSeason.query.filter_by(media_id=media.id).all()]
        elif list_type == ListType.ANIME:
            media = Anime.query.filter_by(themoviedb_id=api_id).first()
            old_seas_eps = [n.episodes for n in AnimeEpisodesPerSeason.query.filter_by(media_id=media.id).all()]

        new_seas_eps = [d['episodes'] for d in data['seasons_data']]

        if new_seas_eps != old_seas_eps:
            if list_type == ListType.SERIES:
                users_list = SeriesList.query.filter_by(media_id=media.id).all()

                for user in users_list:
                    episodes_watched = user.eps_watched

                    count = 0
                    for i in range(0, len(data['seasons_data'])):
                        count += data['seasons_data'][i]['episodes']
                        if count == episodes_watched:
                            user.last_episode_watched = data['seasons_data'][i]['episodes']
                            user.current_season = data['seasons_data'][i]['season']
                            break
                        elif count > episodes_watched:
                            user.last_episode_watched = data['seasons_data'][i]['episodes']-(count-episodes_watched)
                            user.current_season = data['seasons_data'][i]['season']
                            break
                        elif count < episodes_watched:
                            try:
                                data['seasons_data'][i + 1]['season']
                            except IndexError:
                                user.last_episode_watched = data['seasons_data'][i]['episodes']
                                user.current_season = data['seasons_data'][i]['season']
                                break

                SeriesEpisodesPerSeason.query.filter_by(media_id=media.id).delete()
                db.session.commit()

                for seas in data['seasons_data']:
                    season = SeriesEpisodesPerSeason(media_id=media.id,
                                                     season=seas['season'],
                                                     episodes=seas['episodes'])
                    db.session.add(season)
                db.session.commit()
            elif list_type == ListType.ANIME:
                users_list = AnimeList.query.filter_by(media_id=media.id).all()

                for user in users_list:
                    episodes_watched = user.eps_watched

                    count = 0
                    for i in range(0, len(data['seasons_data'])):
                        count += data['seasons_data'][i]['episodes']
                        if count == episodes_watched:
                            user.last_episode_watched = data['seasons_data'][i]['episodes']
                            user.current_season = data['seasons_data'][i]['season']
                            break
                        elif count > episodes_watched:
                            user.last_episode_watched = data['seasons_data'][i]['episodes']-(count-episodes_watched)
                            user.current_season = data['seasons_data'][i]['season']
                            break
                        elif count < episodes_watched:
                            try:
                                data['seasons_data'][i + 1]['season']
                            except IndexError:
                                user.last_episode_watched = data['seasons_data'][i]['episodes']
                                user.current_season = data['seasons_data'][i]['season']
                                break

                AnimeEpisodesPerSeason.query.filter_by(media_id=media.id).delete()
                db.session.commit()

                for seas in data['seasons_data']:
                    season = AnimeEpisodesPerSeason(media_id=media.id,
                                                    season=seas['season'],
                                                    episodes=seas['episodes'])
                    db.session.add(season)
                db.session.commit()

    return True


def automatic_media_refresh():
    app.logger.info('###################################################################')
    app.logger.info('[SYSTEM] - Starting automatic media refresh')

    # Recover all the data
    all_series_tmdb_id = [m.themoviedb_id for m in Series.query.filter(Series.lock_status != True)]
    all_anime_tmdb_id = [m.themoviedb_id for m in Anime.query.filter(Anime.lock_status != True)]
    all_movies_tmdb_id = [m.themoviedb_id for m in Movies.query.filter(Movies.lock_status != True)]

    # Recover from API all the changed <TV_show> ID
    try:
        all_id_tv_changes = ApiData().get_changed_data(list_type=ListType.SERIES)
    except Exception as e:
        app.logger.error('[ERROR] - Requesting the changed data from TMDB API: {}'.format(e))
        return

    # Recover from API all the changed <Movies> ID
    try:
        all_id_movies_changes = ApiData().get_changed_data(list_type=ListType.MOVIES)
    except Exception as e:
        app.logger.error('[ERROR] - Requesting the changed data from TMDB API: {}'.format(e))
        return

    # Refresh Series
    for element in all_id_tv_changes['results']:
        if element['id'] in all_series_tmdb_id:
            try:
                a = refresh_element_data(element['id'], ListType.SERIES)
                if not a:
                    raise
                app.logger.info('[INFO] - Refreshed Series with TMDB ID: [{}]'.format(element['id']))
            except Exception as e:
                app.logger.error('[ERROR] - While refreshing: {}'.format(e))

    # Refresh Anime
    for element in all_id_tv_changes["results"]:
        if element["id"] in all_anime_tmdb_id:
            try:
                refresh_element_data(element["id"], ListType.ANIME)
                app.logger.info('[INFO] - Refreshed Anime with TMDB ID: [{}]'.format(element['id']))
            except Exception as e:
                app.logger.error('[ERROR] - While refreshing: {}'.format(e))

    # Refresh movies
    for element in all_id_movies_changes["results"]:
        if element["id"] in all_movies_tmdb_id:
            try:
                refresh_element_data(element["id"], ListType.MOVIES)
                app.logger.info('[INFO] - Refreshed Movie with TMDB ID: [{}]'.format(element['id']))
            except Exception as e:
                app.logger.error('[ERROR] - While refreshing: {}'.format(e))

    app.logger.info('[SYSTEM] - Automatic refresh completed')
    app.logger.info('###################################################################')


def new_releasing_series():
    app.logger.info('###################################################################')
    app.logger.info('[SYSTEM] - Start adding the new releasing series')

    all_series = Series.query.filter(Series.next_episode_to_air != None).all()

    media_id = []
    for series in all_series:
        try:
            diff = (datetime.utcnow() - datetime.strptime(series.next_episode_to_air, '%Y-%m-%d')).total_seconds()
            # Check if the next episode of the series is releasing in one week or less (7 days)
            if diff < 0 and abs(diff / (3600 * 24)) <= 7:
                media_id.append(series.id)
        except:
            pass

    series_in_ptw = db.session.query(Series, SeriesList) \
        .join(SeriesList, SeriesList.media_id == Series.id) \
        .filter(SeriesList.media_id.in_(media_id), and_(SeriesList.status != Status.RANDOM,
                                                        SeriesList.status != Status.DROPPED)).all()

    for info in series_in_ptw:
        series = Notifications.query.filter_by(user_id=info[1].user_id, media_type='serieslist',
                                               media_id=info[0].id) \
            .order_by(desc(Notifications.timestamp)).first()

        if series:
            payload_series = json.loads(series.payload_json)
            if int(payload_series['season']) < int(info[0].season_to_air):
                pass
            elif int(payload_series['season']) == int(info[0].season_to_air):
                if int(payload_series['episode']) < int(info[0].episode_to_air):
                    pass
                else:
                    continue
            else:
                continue

        release_date = datetime.strptime(info[0].next_episode_to_air, '%Y-%m-%d').strftime("%b %d")
        payload = {'name': info[0].name,
                   'release_date': release_date,
                   'season': '{:02d}'.format(info[0].season_to_air),
                   'episode': '{:02d}'.format(info[0].episode_to_air)}

        data = Notifications(user_id=info[1].user_id,
                             media_type='serieslist',
                             media_id=info[0].id,
                             payload_json=json.dumps(payload))
        db.session.add(data)

    db.session.commit()
    app.logger.info('[SYSTEM] - Finish adding the new releasing series')
    app.logger.info('###################################################################')


def new_releasing_anime():
    app.logger.info('###################################################################')
    app.logger.info('[SYSTEM] - Start adding the new releasing anime')

    all_anime = Anime.query.filter(Anime.next_episode_to_air != None).all()

    media_id = []
    for anime in all_anime:
        try:
            diff = (datetime.utcnow() - datetime.strptime(anime.next_episode_to_air, '%Y-%m-%d')).total_seconds()
            # Check if the next episode of the series is releasing in one week or less (7 days)
            if diff < 0 and abs(diff / (3600 * 24)) <= 7:
                media_id.append(anime.id)
        except:
            pass

    anime_in_ptw = db.session.query(Anime, AnimeList).join(AnimeList, AnimeList.media_id == Anime.id) \
        .filter(AnimeList.media_id.in_(media_id), and_(AnimeList.status != Status.RANDOM,
                                                       AnimeList.status != Status.DROPPED)).all()

    for info in anime_in_ptw:
        anime = Notifications.query.filter_by(user_id=info[1].user_id, media_type='animelist', media_id=info[0].id) \
            .order_by(desc(Notifications.timestamp)).first()

        if anime:
            payload_anime = json.loads(anime.payload_json)
            if int(payload_anime['season']) < int(info[0].season_to_air):
                pass
            elif int(payload_anime['season']) == int(info[0].season_to_air):
                if int(payload_anime['episode']) < int(info[0].episode_to_air):
                    pass
                else:
                    continue
            else:
                continue

        release_date = datetime.strptime(info[0].next_episode_to_air, '%Y-%m-%d').strftime("%b %d %Y")
        payload = {'name': info[0].name,
                   'release_date': release_date,
                   'season': '{:02d}'.format(info[0].season_to_air),
                   'episode': '{:02d}'.format(info[0].episode_to_air)}

        data = Notifications(user_id=info[1].user_id,
                             media_type='animelist',
                             media_id=info[0].id,
                             payload_json=json.dumps(payload))
        db.session.add(data)

    db.session.commit()
    app.logger.info('[SYSTEM] - Finish adding the new releasing anime')
    app.logger.info('###################################################################')


def new_releasing_movies():
    app.logger.info('###################################################################')
    app.logger.info('[SYSTEM] - Start adding the new releasing movies')

    all_movies = Movies.query.all()

    media_id = []
    for movie in all_movies:
        try:
            diff = (datetime.utcnow() - datetime.strptime(movie.release_date, '%Y-%m-%d')).total_seconds()
            # Check if he movie released in one week or less (7 days)
            if diff < 0 and abs(diff / (3600 * 24)) <= 7:
                media_id.append(movie.id)
        except:
            pass

    movies_in_ptw = db.session.query(Movies, MoviesList) \
        .join(MoviesList, MoviesList.media_id == Movies.id) \
        .filter(MoviesList.media_id.in_(media_id), MoviesList.status == Status.PLAN_TO_WATCH).all()

    for info in movies_in_ptw:
        if not bool(Notifications.query.filter_by(user_id=info[1].user_id,
                                                  media_type='movieslist',
                                                  media_id=info[0].id).first()):
            release_date = datetime.strptime(info[0].release_date, '%Y-%m-%d').strftime("%b %d")
            payload = {'name': info[0].name,
                       'release_date': release_date}

            data = Notifications(user_id=info[1].user_id,
                                 media_type='movieslist',
                                 media_id=info[0].id,
                                 payload_json=json.dumps(payload))
            db.session.add(data)

    db.session.commit()
    app.logger.info('[SYSTEM] - Finish adding the new releasing movies')
    app.logger.info('###################################################################')


def automatic_movies_locking():
    app.logger.info('###################################################################')
    app.logger.info('[SYSTEM] - Starting automatic movies locking')
    all_movies = Movies.query.filter(Movies.lock_status != True).all()

    count_locked = 0
    count_not_locked = 0
    now_date = (datetime.utcnow() - timedelta(minutes=225000))  # About 5 months
    for movie in all_movies:
        try:
            release_date = datetime.strptime(movie.release_date, '%Y-%m-%d')
            if release_date < now_date and movie.image_cover != 'default.jpg':
                movie.lock_status = True
                count_locked += 1
            else:
                movie.lock_status = False
                count_not_locked += 1
        except:
            movie.lock_status = False
            count_not_locked += 1

    db.session.commit()
    app.logger.info('Number of movies locked: {}'.format(count_locked))
    app.logger.info('Number of movies not locked: {}'.format(count_not_locked))
    app.logger.info('[SYSTEM] - Finished automatic movies locking')
    app.logger.info('###################################################################')


def update_Mylists_stats():
    stats = GlobalStats()

    def create_dict(data):
        series_list, anime_list, movies_list = [], [], []
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

        return {"series": series_list, "anime": anime_list, "movies": movies_list}

    times_spent = stats.get_total_time_spent()
    total_time = {"total": 0, "series": 0, "anime": 0, "movies": 0}
    if times_spent[0]:
        total_time = {"total": sum(times_spent[0]), "series": int(times_spent[0][0]/60),
                      "anime": int(times_spent[0][1]/60), "movies": int(times_spent[0][2]/60)}

    top_media = stats.get_top_media()
    most_present_media = create_dict(top_media)

    media_genres = stats.get_top_genres()
    most_genres_media = create_dict(media_genres)

    media_actors = stats.get_top_actors()
    most_actors_media = create_dict(media_actors)

    media_directors = stats.get_top_directors()
    most_directors_media = create_dict(media_directors)

    media_dropped = stats.get_top_dropped()
    top_dropped_media = create_dict(media_dropped)

    total_media_eps_seas = stats.get_total_eps_seasons()
    total_seasons_media = {"series": total_media_eps_seas[0][0][1], "anime": total_media_eps_seas[1][0][1]}
    total_episodes_media = {"series": total_media_eps_seas[0][0][0], "anime": total_media_eps_seas[1][0][0]}

    total_movies = stats.get_total_movies()
    total_movies_dict = {"movies": total_movies}

    nb_users = User.query.filter(User.role != RoleType.ADMIN, User.active == True).all()
    nb_series = Series.query.all()
    nb_anime = Anime.query.all()
    nb_movies = Movies.query.all()
    nb_media = {"series": len(nb_series), "anime": len(nb_anime), "movies": len(nb_movies)}

    stats_to_add = MyListsStats(
        nb_users=len(nb_users), nb_media=json.dumps(nb_media),
        total_time=json.dumps(total_time), top_media=json.dumps(most_present_media),
        top_genres=json.dumps(most_genres_media), top_actors=json.dumps(most_actors_media),
        top_directors=json.dumps(most_directors_media), top_dropped=json.dumps(top_dropped_media),
        total_episodes=json.dumps(total_episodes_media), total_seasons=json.dumps(total_seasons_media),
        total_movies=json.dumps(total_movies_dict)
    )
    db.session.add(stats_to_add)
    db.session.commit()


# ---------------------------------------------------------------------------------------------------------------


@app.cli.command()
def scheduled_task():
    """Run the scheduled jobs."""
    app.logger.setLevel(logging.INFO)
    remove_non_list_media()
    remove_old_covers()
    automatic_media_refresh()
    new_releasing_movies()
    new_releasing_series()
    new_releasing_anime()
    automatic_movies_locking()
    compute_media_time_spent()
    update_Mylists_stats()
