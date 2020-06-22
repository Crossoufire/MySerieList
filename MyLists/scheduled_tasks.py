import os

from pathlib import Path
from sqlalchemy import and_
from MyLists import app, db
from datetime import datetime
from MyLists.API_data import ApiData
from MyLists.main.functions import get_details
from MyLists.general.functions import compute_media_time_spent
from MyLists.models import ListType, Series, SeriesActors, SeriesList, SeriesGenre, SeriesNetwork, \
    SeriesEpisodesPerSeason, UserLastUpdate, Notifications, Anime, AnimeList, AnimeActors, Movies, MoviesActors, \
    MoviesGenre, AnimeGenre, AnimeNetwork, AnimeEpisodesPerSeason, MoviesList, MoviesCollections, Status


class ScheduledTask:
    def __init__(self):
        self.remove_non_list_media()
        self.remove_old_covers()
        self.automatic_media_refresh()
        self.new_releasing_movies()
        self.new_releasing_series()
        self.new_releasing_anime()

        compute_media_time_spent(ListType.SERIES)
        compute_media_time_spent(ListType.ANIME)
        compute_media_time_spent(ListType.MOVIES)

    @staticmethod
    def remove_non_list_media():
        app.logger.info('[SYSTEM] - Starting media remover')

        # SERIES DELETIONS
        series = db.session.query(Series, SeriesList).outerjoin(SeriesList, SeriesList.series_id == Series.id).all()
        count = 0
        to_delete = []
        for tv_series in series:
            if tv_series[1] is None:
                to_delete.append(tv_series[0].id)
        for deletion in to_delete:
            Series.query.filter_by(id=deletion).delete()
            SeriesActors.query.filter_by(series_id=deletion).delete()
            SeriesGenre.query.filter_by(series_id=deletion).delete()
            SeriesNetwork.query.filter_by(series_id=deletion).delete()
            SeriesEpisodesPerSeason.query.filter_by(series_id=deletion).delete()
            UserLastUpdate.query.filter_by(media_type=ListType.SERIES, media_id=deletion).delete()
            Notifications.query.filter_by(media_type='serieslist', media_id=deletion).delete()
            count += 1

            app.logger.info('Removed series with ID: {}'.format(deletion))
        app.logger.info('Total series removed: {}'.format(count))

        # ANIME DELETIONS
        anime = db.session.query(Anime, AnimeList).outerjoin(AnimeList, AnimeList.anime_id == Anime.id).all()
        count = 0
        to_delete = []
        for tv_anime in anime:
            if tv_anime[1] is None:
                to_delete.append(tv_anime[0].id)
        for deletion in to_delete:
            Anime.query.filter_by(id=deletion).delete()
            AnimeActors.query.filter_by(anime_id=deletion).delete()
            AnimeGenre.query.filter_by(anime_id=deletion).delete()
            AnimeNetwork.query.filter_by(anime_id=deletion).delete()
            AnimeEpisodesPerSeason.query.filter_by(anime_id=deletion).delete()
            UserLastUpdate.query.filter_by(media_type=ListType.ANIME, media_id=deletion).delete()
            Notifications.query.filter_by(media_type='animelist', media_id=deletion).delete()
            count += 1

            app.logger.info('Removed anime with ID: {}'.format(deletion))
        app.logger.info('Total anime removed: {}'.format(count))

        # MOVIES DELETIONS
        movies = db.session.query(Movies, MoviesList).outerjoin(MoviesList, MoviesList.movies_id == Movies.id).all()
        count = 0
        to_delete = []
        for movie in movies:
            if movie[1] is None:
                to_delete.append(movie[0].id)
        for deletion in to_delete:
            Movies.query.filter_by(id=deletion).delete()
            MoviesActors.query.filter_by(movies_id=deletion).delete()
            MoviesGenre.query.filter_by(movies_id=deletion).delete()
            UserLastUpdate.query.filter_by(media_type=ListType.MOVIES, media_id=deletion).delete()
            Notifications.query.filter_by(media_type='movieslist', media_id=deletion).delete()
            count += 1
            app.logger.info('Removed movie with ID: {0}'.format(deletion))
        app.logger.info('Total movies removed: {}'.format(count))

        db.session.commit()
        app.logger.info('[SYSTEM] - Automatic non user media remover finished')

    @staticmethod
    def remove_old_covers():
        app.logger.info('[SYSTEM] - Starting old covers remover')

        # SERIES OLD COVERS
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
        app.logger.info('Finished, Total old series covers deleted: {}'.format(count))

        # ANIME OLD COVERS
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
        app.logger.info('Finished, Total old anime covers deleted: {}'.format(count))

        # MOVIES OLD COVERS
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
        app.logger.info('Finished, Total old movies covers deleted: {}'.format(count))

        # MOVIES COLLECTION OLD COVERS
        movies_collec = MoviesCollections.query.all()
        path_movies_collec_covers = Path(app.root_path, 'static/covers/movies_collection_covers/')

        images_in_db = []
        for movie in movies_collec:
            images_in_db.append(movie.poster)

        images_saved = []
        for file in os.listdir(path_movies_collec_covers):
            images_saved.append(file)

        count = 0
        for image in images_saved:
            if image not in images_in_db and image != 'default.jpg':
                os.remove('{0}/{1}'.format(path_movies_collec_covers, image))
                app.logger.info('Removed old movie collection cover with name: {}'.format(image))
                count += 1

        app.logger.info('Finished, Total old movies collections covers deleted: {}'.format(count))
        app.logger.info('[SYSTEM] - Automatic old covers remover finished')

    @staticmethod
    def refresh_element_data(api_id, list_type):
        if list_type != ListType.MOVIES:
            data = get_details(api_id, list_type)
            if data['tv_data'] is None:
                return None
        elif list_type == ListType.MOVIES:
            data = get_details(api_id, list_type)
            if data['movies_data'] is None:
                return None

        # Update the main details data
        if list_type == ListType.SERIES:
            Series.query.filter_by(themoviedb_id=api_id).update(data['tv_data'])
        elif list_type == ListType.ANIME:
            Anime.query.filter_by(themoviedb_id=api_id).update(data['tv_data'])
        elif list_type == ListType.MOVIES:
            Movies.query.filter_by(themoviedb_id=api_id).update(data['movies_data'])

        db.session.commit()

        # Refresh Seasons and Episodes
        def get_total_eps(user, eps_per_season):
            if user.status == Status.PLAN_TO_WATCH or user.status == Status.RANDOM:
                nb_eps_watched = 1
            else:
                nb_eps_watched = 0
                for i in range(1, user.current_season):
                    nb_eps_watched += eps_per_season[i - 1]
                nb_eps_watched += user.last_episode_watched

            return nb_eps_watched

        if list_type != ListType.MOVIES:
            if list_type == ListType.SERIES:
                element = Series.query.filter_by(themoviedb_id=api_id).first()
                old_seas_eps = \
                    [n.episodes for n in SeriesEpisodesPerSeason.query.filter_by(series_id=element.id).all()]
            elif list_type == ListType.ANIME:
                element = Anime.query.filter_by(themoviedb_id=api_id).first()
                old_seas_eps = \
                    [n.episodes for n in AnimeEpisodesPerSeason.query.filter_by(anime_id=element.id).all()]

            new_seas_eps = [d['episodes'] for d in data['seasons_data']]

            if new_seas_eps != old_seas_eps:
                if list_type == ListType.SERIES:
                    users_list = SeriesList.query.filter_by(series_id=element.id).all()

                    for user in users_list:
                        episodes_watched = get_total_eps(user, old_seas_eps)

                        count = 0
                        for i in range(0, len(data['seasons_data'])):
                            count += data['seasons_data'][i]['episodes']
                            if count == episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes']
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count > episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes'] - \
                                                            (count - episodes_watched)
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count < episodes_watched:
                                try:
                                    data['seasons_data'][i + 1]['season']
                                except IndexError:
                                    user.last_episode_watched = data['seasons_data'][i]['episodes']
                                    user.current_season = data['seasons_data'][i]['season']
                                    break
                        db.session.commit()

                    SeriesEpisodesPerSeason.query.filter_by(series_id=element.id).delete()
                    db.session.commit()

                    for seas in data['seasons_data']:
                        season = SeriesEpisodesPerSeason(series_id=element.id,
                                                         season=seas['season'],
                                                         episodes=seas['episodes'])
                        db.session.add(season)
                    db.session.commit()
                elif list_type == ListType.ANIME:
                    users_list = AnimeList.query.filter_by(anime_id=element.id).all()

                    for user in users_list:
                        episodes_watched = get_total_eps(user, old_seas_eps)

                        count = 0
                        for i in range(0, len(data['seasons_data'])):
                            count += data['seasons_data'][i]['episodes']
                            if count == episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes']
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count > episodes_watched:
                                user.last_episode_watched = data['seasons_data'][i]['episodes'] - (
                                        count - episodes_watched)
                                user.current_season = data['seasons_data'][i]['season']
                                break
                            elif count < episodes_watched:
                                try:
                                    data['seasons_data'][i + 1]['season']
                                except IndexError:
                                    user.last_episode_watched = data['seasons_data'][i]['episodes']
                                    user.current_season = data['seasons_data'][i]['season']
                                    break
                        db.session.commit()

                    AnimeEpisodesPerSeason.query.filter_by(anime_id=element.id).delete()
                    db.session.commit()

                    for seas in data['seasons_data']:
                        season = AnimeEpisodesPerSeason(anime_id=element.id,
                                                        season=seas['season'],
                                                        episodes=seas['episodes'])
                        db.session.add(season)
                    db.session.commit()

        return True

    def automatic_media_refresh(self):
        app.logger.info('[SYSTEM] - Starting automatic refresh')

        # Recover all the data
        all_series_tmdb_id = [m.themoviedb_id for m in Series.query.filter(Series.lock_status != True)]
        all_anime_tmdb_id = [m.themoviedb_id for m in db.session.query(Anime).filter(Anime.lock_status != True)]
        all_movies_tmdb_id = [m.themoviedb_id for m in db.session.query(Movies).filter(Movies.lock_status != True)]

        # Recover from API all the changed <TV_show> ID
        try:
            all_id_tv_changes = ApiData().get_changed_data(list_type=ListType.SERIES)
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the changed data from TMDB API: {}'.format(e))
            return

        # Recover from API all the changed <Movies> ID
        try:
            all_id_movies_changes = ApiData().get_changed_data(list_type=ListType.MOVIES)
        except Exception as e:
            app.logger.error('[SYSTEM] Error requesting the changed data from TMDB API: {}'.format(e))
            return

        # Series
        for element in all_id_tv_changes["results"]:
            if element["id"] in all_series_tmdb_id:
                try:
                    self.refresh_element_data(element["id"], ListType.SERIES)
                    app.logger.info('Refreshed Series with TMDb_ID: {}'.format(element["id"]))
                except Exception as e:
                    app.logger.error('Error while refreshing: {}'.format(e))

        # Anime
        for element in all_id_tv_changes["results"]:
            if element["id"] in all_anime_tmdb_id:
                try:
                    self.refresh_element_data(element["id"], ListType.ANIME)
                    app.logger.info('Refreshed Anime with TMDb_ID: {}'.format(element["id"]))
                except Exception as e:
                    app.logger.error('Error while refreshing: {}'.format(e))

        # Refresh movies
        for element in all_id_movies_changes["results"]:
            if element["id"] in all_movies_tmdb_id:
                try:
                    self.refresh_element_data(element["id"], ListType.MOVIES)
                    app.logger.info('Refresh Movie with TMDb_ID: {}'.format(element["id"]))
                except Exception as e:
                    app.logger.error('Error while refreshing: {}'.format(e))

        app.logger.info('[SYSTEM] - Automatic refresh completed')

    @staticmethod
    def new_releasing_movies():
        all_movies = Movies.query.all()

        movies_id = []
        for movie in all_movies:
            try:
                diff = (datetime.utcnow() - datetime.strptime(movie.release_date, '%Y-%m-%d')).total_seconds()
                # Check if he movie released in one week or less (7 days)
                if diff < 0 and abs(diff/(3600*24)) <= 7:
                    movies_id.append(movie.id)
            except:
                pass

        movies_in_ptw = db.session.query(Movies, MoviesList) \
            .join(MoviesList, MoviesList.movies_id == Movies.id) \
            .filter(MoviesList.movies_id.in_(movies_id), MoviesList.status == Status.PLAN_TO_WATCH).all()

        for info in movies_in_ptw:
            if not bool(Notifications.query.filter_by(user_id=info[1].user_id,
                                                      media_type='movieslist',
                                                      media_id=info[0].id).first()):
                data = Notifications(user_id=info[1].user_id,
                                     media_type='movieslist',
                                     media_id=info[0].id,
                                     media_name=info[0].name,
                                     release_date=info[0].release_date)
                db.session.add(data)

        db.session.commit()

    @staticmethod
    def new_releasing_series():
        all_series = Series.query.filter(Series.next_episode_to_air != None).all()

        series_id = []
        for series in all_series:
            try:
                diff = (datetime.utcnow() - datetime.strptime(series.next_episode_to_air, '%Y-%m-%d')).total_seconds()
                # Check if the next episode of the series is releasing in one week or less (7 days)
                if diff < 0 and abs(diff/(3600*24)) <= 7:
                    series_id.append(series.id)
            except:
                pass

        series_in_ptw = db.session.query(Series, SeriesList) \
            .join(SeriesList, SeriesList.series_id == Series.id) \
            .filter(SeriesList.series_id.in_(series_id), and_(SeriesList.status != Status.RANDOM,
                                                              SeriesList.status != Status.DROPPED)).all()

        for info in series_in_ptw:
            if not bool(Notifications.query.filter_by(user_id=info[1].user_id,
                                                      media_type='serieslist',
                                                      media_id=info[0].id).first()):
                data = Notifications(user_id=info[1].user_id,
                                     media_type='serieslist',
                                     media_id=info[0].id,
                                     media_name=info[0].name,
                                     release_date=info[0].next_episode_to_air,
                                     season=info[0].season_to_air,
                                     episode=info[0].episode_to_air)
                db.session.add(data)

        db.session.commit()

    @staticmethod
    def new_releasing_anime():
        all_anime = Series.query.filter(Anime.next_episode_to_air != None).all()

        anime_id = []
        for anime in all_anime:
            try:
                diff = (datetime.utcnow() - datetime.strptime(anime.next_episode_to_air, '%Y-%m-%d')).total_seconds()
                # Check if the next episode of the series is releasing in one week or less (7 days)
                if diff < 0 and abs(diff/(3600*24)) <= 7:
                    anime_id.append(anime.id)
            except:
                pass

        anime_in_ptw = db.session.query(Anime, AnimeList) \
            .join(AnimeList, AnimeList.anime_id == Anime.id) \
            .filter(AnimeList.anime_id.in_(anime_id), and_(AnimeList.status != Status.RANDOM,
                                                           AnimeList.status != Status.DROPPED)).all()

        for info in anime_in_ptw:
            if not bool(Notifications.query.filter_by(user_id=info[1].user_id,
                                                      media_type='animelist',
                                                      media_id=info[0].id).first()):
                data = Notifications(user_id=info[1].user_id,
                                     media_type='animelist',
                                     media_id=info[0].id,
                                     media_name=info[0].name,
                                     release_date=info[0].next_episode_to_air,
                                     season=info[0].season_to_air,
                                     episode=info[0].episode_to_air)
                db.session.add(data)

        db.session.commit()


app.apscheduler.add_job(func=ScheduledTask(), trigger='cron', id='scheduled_task', hour=3, minute=0)
