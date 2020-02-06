import secrets

from flask import flash
from datetime import datetime
from MyLists import db, current_app
from flask_login import current_user
from MyLists.API_data import ApiData
from MyLists.models import ListType, Status, User, AnimeList, Anime, AnimeEpisodesPerSeason, SeriesEpisodesPerSeason, \
    SeriesList, Series, MoviesList, Movies, SeriesGenre, AnimeGenre, MoviesGenre, UserLastUpdate, SeriesActors, \
    SeriesNetwork, AnimeNetwork, MoviesActors, MoviesCollections, AnimeActors


def check_cat_type(list_type, status):
    if list_type != ListType.MOVIES:
        if status == 'Watching':
            return Status.WATCHING
        elif status == 'Completed':
            return Status.COMPLETED
        elif status == 'On Hold':
            return Status.ON_HOLD
        elif status == 'Random':
            return Status.RANDOM
        elif status == 'Dropped':
            return Status.DROPPED
        elif status == 'Plan to Watch':
            return Status.PLAN_TO_WATCH
        else:
            return None
    elif list_type == ListType.MOVIES:
        if status == 'Completed':
            return Status.COMPLETED
        elif status == 'Plan to Watch':
            return Status.PLAN_TO_WATCH
        else:
            return None


def compute_time_spent(cat_type=None, old_eps=None, new_eps=None, old_seas=None, new_seas=None,
                       all_seas_data=None, media=None, old_status=None, new_status=None, list_type=None):

    def eps_watched_seasons(old_season, old_episode, new_season, all_seasons):
        nb_eps_watched = 0
        if new_season - old_season > 0:
            for i in range(old_season, new_season):
                nb_eps_watched += all_seasons[i-1].episodes
            nb_eps_watched += (1-old_episode)
        else:
            for i in range(new_season, old_season):
                nb_eps_watched += all_seasons[i-1].episodes
            nb_eps_watched += (1-old_episode)
            nb_eps_watched = - nb_eps_watched
        return nb_eps_watched

    def eps_watched_status(season, episode, all_seasons):
        nb_eps_watched = 0
        for i in range(1, season):
            nb_eps_watched += all_seasons[i-1].episodes
        nb_eps_watched += episode
        return nb_eps_watched

    if cat_type == 'episode':
        if list_type == ListType.SERIES:
            old_time = current_user.time_spent_series
            current_user.time_spent_series = old_time + ((new_eps-old_eps)*media.episode_duration)
        elif list_type == ListType.ANIME:
            old_time = current_user.time_spent_anime
            current_user.time_spent_anime = old_time + ((new_eps-old_eps)*media.episode_duration)

    elif cat_type == 'season':
        eps_watched = eps_watched_seasons(old_seas, old_eps, new_seas, all_seas_data)

        if list_type == ListType.SERIES:
            old_time = current_user.time_spent_series
            current_user.time_spent_series = old_time + (eps_watched*media.episode_duration)
        elif list_type == ListType.ANIME:
            old_time = current_user.time_spent_anime
            current_user.time_spent_anime = old_time + (eps_watched*media.episode_duration)

    elif cat_type == 'delete':
        if list_type == ListType.SERIES:
            eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
            old_time = current_user.time_spent_series
            current_user.time_spent_series = old_time - (eps_watched*media.episode_duration)
        elif list_type == ListType.ANIME:
            eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
            old_time = current_user.time_spent_anime
            current_user.time_spent_anime = old_time - (eps_watched*media.episode_duration)
        elif list_type == ListType.MOVIES:
            old_time = current_user.time_spent_movies
            current_user.time_spent_movies = old_time - media.runtime

    elif cat_type == 'category':
        if new_status == Status.WATCHING or new_status == Status.ON_HOLD or new_status == Status.DROPPED:
            if list_type == ListType.SERIES:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_series = current_user.time_spent_series + media.episode_duration
            elif list_type == ListType.ANIME:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_anime = current_user.time_spent_anime + media.episode_duration
        elif new_status == Status.COMPLETED or new_status == Status.COMPLETED_ANIMATION:
            if list_type == ListType.SERIES:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_series = current_user.time_spent_series + \
                                                    (media.total_episodes*media.episode_duration)
                else:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_series = current_user.time_spent_series + \
                                                    ((media.total_episodes-eps_watched)*media.episode_duration)
            elif list_type == ListType.ANIME:
                if old_status == Status.RANDOM or old_status == Status.PLAN_TO_WATCH or old_status is None:
                    current_user.time_spent_anime = current_user.time_spent_anime + \
                                                    (media.total_episodes*media.episode_duration)
                else:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_anime = current_user.time_spent_anime + \
                                                    ((media.total_episodes-eps_watched)*media.episode_duration)
            elif list_type == ListType.MOVIES:
                current_user.time_spent_movies = current_user.time_spent_movies + media.runtime
        elif new_status == Status.RANDOM:
            if list_type == ListType.SERIES:
                if old_status != Status.PLAN_TO_WATCH or old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_series = current_user.time_spent_series - eps_watched*media.episode_duration
            elif list_type == ListType.ANIME:
                if old_status != Status.PLAN_TO_WATCH or old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_anime = current_user.time_spent_anime - eps_watched*media.episode_duration
        elif new_status == Status.PLAN_TO_WATCH:
            if list_type == ListType.SERIES:
                if old_status != Status.RANDOM or old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_series = current_user.time_spent_series-(eps_watched*media.episode_duration)
            elif list_type == ListType.ANIME:
                if old_status != Status.RANDOM or old_status is not None:
                    eps_watched = eps_watched_status(old_seas, old_eps, all_seas_data)
                    current_user.time_spent_anime = current_user.time_spent_anime - eps_watched*media.episode_duration
            elif list_type == ListType.MOVIES:
                if old_status is not None:
                    current_user.time_spent_movies = current_user.time_spent_movies - media.runtime

    db.session.commit()


def get_medialist_data(element_data, list_type, covers_path, user_id):
    current_list = []
    if user_id != current_user.id:
        if list_type == ListType.ANIME:
            current_media = db.session.query(AnimeList.anime_id).filter_by(user_id=current_user.id).all()
        elif list_type == ListType.SERIES:
            current_media = db.session.query(SeriesList.series_id).filter_by(user_id=current_user.id).all()
        elif list_type == ListType.MOVIES:
            current_media = db.session.query(MoviesList.movies_id).filter_by(user_id=current_user.id).all()
        current_list = [r[0] for r in current_media]

    if list_type != ListType.MOVIES:
        watching_list = []
        completed_list = []
        onhold_list = []
        random_list = []
        dropped_list = []
        plantowatch_list = []

        common_elements = 0
        for element in element_data:
            # Get episodes per season
            nb_season = len(element[4].split(","))
            eps_per_season = element[6].split(",")[:nb_season]
            eps_per_season = [int(i) for i in eps_per_season]

            # Change first air time format
            first_air_date = element[0].first_air_date
            if 'Unknown' not in first_air_date:
                first_air_date = datetime.strptime(first_air_date, '%Y-%m-%d').strftime("%d %b %Y")

            # Change last air time format
            last_air_date = element[0].last_air_date
            if 'Unknown' not in last_air_date:
                last_air_date = datetime.strptime(last_air_date, '%Y-%m-%d').strftime("%d %b %Y")

            actors = element[5].replace(',', ', ')
            genres = element[2].replace(',', ', ')
            networks = element[3].replace(',', ', ')

            element_info = {"id": element[0].id,
                            "cover": "{}{}".format(covers_path, element[0].image_cover),
                            "name": element[0].name,
                            "original_name": element[0].original_name,
                            "first_air_date": first_air_date,
                            "last_air_date": last_air_date,
                            "created_by": element[0].created_by,
                            "episode_duration": element[0].episode_duration,
                            "homepage": element[0].homepage,
                            "in_production": element[0].in_production,
                            "origin_country": element[0].origin_country,
                            "total_seasons": element[0].total_seasons,
                            "total_episodes": element[0].total_episodes,
                            "status": element[0].status,
                            "vote_average": element[0].vote_average,
                            "vote_count": element[0].vote_count,
                            "synopsis": element[0].synopsis,
                            "popularity": element[0].popularity,
                            "last_episode_watched": element[1].last_episode_watched,
                            "eps_per_season": eps_per_season,
                            "current_season": element[1].current_season,
                            "score": element[1].score,
                            "actors": actors,
                            "genres": genres,
                            "networks": networks}

            if element[1].status == Status.WATCHING:
                if element[0].id in current_list:
                    watching_list.append([element_info, True])
                    common_elements += 1
                else:
                    watching_list.append([element_info, False])
            elif element[1].status == Status.COMPLETED:
                if element[0].id in current_list:
                    completed_list.append([element_info, True])
                    common_elements += 1
                else:
                    completed_list.append([element_info, False])
            elif element[1].status == Status.ON_HOLD:
                if element[0].id in current_list:
                    onhold_list.append([element_info, True])
                    common_elements += 1
                else:
                    onhold_list.append([element_info, False])
            elif element[1].status == Status.RANDOM:
                if element[0].id in current_list:
                    random_list.append([element_info, True])
                    common_elements += 1
                else:
                    random_list.append([element_info, False])
            elif element[1].status == Status.DROPPED:
                if element[0].id in current_list:
                    dropped_list.append([element_info, True])
                    common_elements += 1
                else:
                    dropped_list.append([element_info, False])
            elif element[1].status == Status.PLAN_TO_WATCH:
                if element[0].id in current_list:
                    plantowatch_list.append([element_info, True])
                    common_elements += 1
                else:
                    plantowatch_list.append([element_info, False])

        element_all_data = [[watching_list, "WATCHING"], [completed_list, "COMPLETED"], [onhold_list, "ON HOLD"],
                            [random_list, "RANDOM"], [dropped_list, "DROPPED"], [plantowatch_list, "PLAN TO WATCH"]]

        try:
            percentage = int((common_elements/len(element_data))*100)
        except ZeroDivisionError:
            percentage = 0
        all_data_media = {"all_data": element_all_data,
                          "common_elements": [common_elements, len(element_data), percentage]}

        return all_data_media
    elif list_type == ListType.MOVIES:
        completed_list = []
        completed_list_animation = []
        plantowatch_list = []

        common_elements = 0
        for element in element_data:
            # Change release date format
            release_date = element[0].release_date
            if 'Unknown' not in release_date:
                release_date = datetime.strptime(release_date, '%Y-%m-%d').strftime("%d %b %Y")

            actors = element[3].replace(',', ', ')
            genres = element[2].replace(',', ', ')

            element_info = {"id": element[0].id,
                            "cover": "{}{}".format(covers_path, element[0].image_cover),
                            "name": element[0].name,
                            "original_name": element[0].original_name,
                            "release_date": release_date,
                            "homepage": element[0].homepage,
                            "runtime": element[0].runtime,
                            "original_language": element[0].original_language,
                            "synopsis": element[0].synopsis,
                            "vote_average": element[0].vote_average,
                            "vote_count": element[0].vote_count,
                            "popularity": element[0].popularity,
                            "budget": element[0].budget,
                            "revenue": element[0].revenue,
                            "tagline": element[0].tagline,
                            "score": element[1].score,
                            "actors": actors,
                            "genres": genres}

            if element[1].status == Status.COMPLETED:
                if element[0].id in current_list:
                    completed_list.append([element_info, True])
                    common_elements += 1
                else:
                    completed_list.append([element_info, False])
            elif element[1].status == Status.COMPLETED_ANIMATION:
                if element[0].id in current_list:
                    completed_list_animation.append([element_info, True])
                    common_elements += 1
                else:
                    completed_list_animation.append([element_info, False])
            elif element[1].status == Status.PLAN_TO_WATCH:
                if element[0].id in current_list:
                    plantowatch_list.append([element_info, True])
                    common_elements += 1
                else:
                    plantowatch_list.append([element_info, False])

        element_all_data = [[completed_list, "COMPLETED"], [completed_list_animation, "COMPLETED ANIMATION"],
                            [plantowatch_list, "PLAN TO WATCH"]]

        try:
            percentage = int((common_elements/len(element_data))*100)
        except ZeroDivisionError:
            percentage = 0
        all_data_media = {"all_data": element_all_data,
                          "common_elements": [common_elements, len(element_data), percentage]}

        return all_data_media


def set_last_update(media_name, media_type, old_status=None, new_status=None, old_season=None,
                    new_season=None, old_episode=None, new_episode=None):
    user = User.query.filter_by(id=current_user.id).first()

    update = UserLastUpdate(user_id=user.id, media_name=media_name, media_type=media_type, old_status=old_status,
                            new_status=new_status, old_season=old_season, new_season=new_season,
                            old_episode=old_episode, new_episode=new_episode, date=datetime.utcnow())
    db.session.add(update)
    db.session.commit()


def add_element_to_user(element_id, user_id, list_type, status):
    if list_type == ListType.SERIES:
        # Set season/episode to max if the "completed" category is selected
        if status == Status.COMPLETED:
            seasons_eps = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id).all()
            user_list = SeriesList(user_id=user_id,
                                   series_id=element_id,
                                   current_season=len(seasons_eps),
                                   last_episode_watched=seasons_eps[-1].episodes,
                                   status=status)
        else:
            user_list = SeriesList(user_id=user_id,
                                   series_id=element_id,
                                   current_season=1,
                                   last_episode_watched=1,
                                   status=status)

        # Commit the changes
        db.session.add(user_list)
        db.session.commit()
        current_app.logger.info('[{}] Added a series with the ID {}'.format(user_id, element_id))

        # Set the last update
        media = Series.query.filter_by(id=element_id).first()
        set_last_update(media_name=media.name, media_type=list_type, new_status=status)
    elif list_type == ListType.ANIME:
        # Set season/episode to max if the "completed" category is selected
        if status == Status.COMPLETED:
            seasons_eps = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id).all()
            user_list = AnimeList(user_id=user_id,
                                  anime_id=element_id,
                                  current_season=len(seasons_eps),
                                  last_episode_watched=seasons_eps[-1].episodes,
                                  status=status)
        else:
            user_list = AnimeList(user_id=user_id,
                                  anime_id=element_id,
                                  current_season=1,
                                  last_episode_watched=1,
                                  status=status)

        # Commit the changes
        db.session.add(user_list)
        db.session.commit()
        current_app.logger.info('[{}] Added an anime with the ID {}'.format(user_id, element_id))

        # Set the last update
        media = Anime.query.filter_by(id=element_id).first()
        set_last_update(media_name=media.name, media_type=list_type, new_status=status)
    elif list_type == ListType.MOVIES:
        # If it contain the "Animation" genre add to "Completed Animation"
        if status == Status.COMPLETED:
            isanimation = MoviesGenre.query.filter_by(movies_id=element_id, genre="Animation").first()
            if isanimation:
                status = Status.COMPLETED_ANIMATION
            else:
                status = Status.COMPLETED
        user_list = MoviesList(user_id=user_id,
                               movies_id=element_id,
                               status=status)

        # Commit the changes
        db.session.add(user_list)
        db.session.commit()
        current_app.logger.info('[{}] Added movie with the ID {}'.format(user_id, element_id))

        # Set the last update
        media = Movies.query.filter_by(id=element_id).first()
        set_last_update(media_name=media.name, media_type=list_type, new_status=status)

    # Compute the new time spent
    compute_time_spent(cat_type="category", media=media, new_status=status, list_type=list_type)


def add_element_in_base(api_id, list_type, element_cat):
    details_data = ApiData().get_details_and_credits_data(api_id, list_type)

    # Check the API response
    if details_data is None:
        return flash("There was an error fetching the API data, please try again later", "error")

    # Get the media cover
    media_cover_path = details_data.get("poster_path") or None

    if media_cover_path:
        media_cover_name = "{}.jpg".format(secrets.token_hex(8))
        issuccess = ApiData().save_api_cover(media_cover_path, media_cover_name, list_type)
        if issuccess is False:
            media_cover_name = "default.jpg"
    else:
        media_cover_name = "default.jpg"

    if list_type != ListType.MOVIES:
        tv_data = {'name': details_data.get("name", "Unknown") or "Unknown",
                   'original_name': details_data.get("original_name", "Unknown") or "Unknown",
                   'first_air_date': details_data.get("first_air_date", "Unknown") or "Unknown",
                   'last_air_date': details_data.get("last_air_date", "Unknown") or "Unknown",
                   'homepage': details_data.get("homepage", "Unknown") or "Unknown",
                   'in_production': details_data.get("in_production", False) or False,
                   'total_seasons': details_data.get("number_of_seasons", 1) or 1,
                   'total_episodes': details_data.get("number_of_episodes", 1) or 1,
                   'status': details_data.get("status", "Unknown") or "Unknown",
                   'vote_average': details_data.get("vote_average", 0) or 0,
                   'vote_count': details_data.get("vote_count", 0) or 0,
                   'synopsis': details_data.get("overview", "No overview avalaible.") or "No overview avalaible.",
                   'popularity': details_data.get("popularity", 0) or 0, 'themoviedb_id': details_data.get("id"),
                   'image_cover': media_cover_name, 'last_update': datetime.utcnow()}

        # Episode duration: list
        episode_duration = details_data.get("episode_run_time") or None
        if episode_duration:
            tv_data['episode_duration'] = episode_duration[0]
        else:
            if list_type == ListType.ANIME:
                tv_data['episode_duration'] = 24
            elif list_type == ListType.SERIES:
                tv_data['episode_duration'] = 45

        # Origin country: list
        origin_country = details_data.get("origin_country", "Unknown") or "Unknown"
        if origin_country == "Unknown":
            tv_data['origin_country'] = 'Unknown'
        else:
            tv_data['origin_country'] = origin_country[0]

        # Created by: list
        created_by = details_data.get("created_by", "Unknown") or "Unknown"
        if created_by != "Unknown":
            creators = []
            for creator in created_by:
                tmp_created = creator.get("name") or None
                if tmp_created:
                    creators.append(tmp_created)
            tv_data['created_by'] = ", ".join(x for x in creators)
        else:
            tv_data['created_by'] = 'Unknown'

        # Seasons: list. Check if a special season exist, if so, ignore it
        seasons = details_data.get('seasons') or None
        seasons_data = []
        if seasons:
            if details_data["seasons"][0]["season_number"] == 0:
                for i in range(1, len(details_data["seasons"])):
                    seasons_data.append(details_data["seasons"][i])
            else:
                for i in range(0, len(details_data["seasons"])):
                    seasons_data.append(details_data["seasons"][i])

        # Genres: list
        genres = details_data.get('genres') or None
        genres_data = []
        if genres:
            for i in range(0, len(details_data["genres"])):
                genres_data.append([details_data["genres"][i]["name"], int(details_data["genres"][i]["id"])])

        # Network: list
        networks = details_data.get('networks') or None
        networks_data = []
        if networks:
            for i in range(0, len(details_data["networks"])):
                networks_data.append(details_data["networks"][i]["name"])
                if i == 4:
                    break

        # Actors: list
        actors = details_data.get('credits', {}).get('cast') or None
        actors_names = []
        if actors:
            for i in range(0, len(details_data["credits"]["cast"])):
                actors_names.append(details_data["credits"]["cast"][i]["name"])
                if i == 4:
                    break

        # Add the TV data to the database
        if list_type == ListType.SERIES:
            element = Series(**tv_data)
        elif list_type == ListType.ANIME:
            element = Anime(**tv_data)

        db.session.add(element)
        db.session.commit()

        # Add actors
        if list_type == ListType.SERIES:
            if len(actors_names) == 0:
                actors = SeriesActors(series_id=element.id,
                                      name="Unknown")
                db.session.add(actors)
            else:
                for name in actors_names:
                    actors = SeriesActors(series_id=element.id,
                                          name=name)
                    db.session.add(actors)
        elif list_type == ListType.ANIME:
            if len(actors_names) == 0:
                actors = AnimeActors(anime_id=element.id,
                                     name="Unknown")
                db.session.add(actors)
            else:
                for name in actors_names:
                    actors = AnimeActors(anime_id=element.id,
                                         name=name)
                    db.session.add(actors)

        # Add genres
        if list_type == ListType.SERIES:
            if len(genres_data) == 0:
                genre = SeriesGenre(series_id=element.id,
                                    genre="Unknown",
                                    genre_id=0)
                db.session.add(genre)
            else:
                for i in range(0, len(genres_data)):
                    genre = SeriesGenre(series_id=element.id,
                                        genre=genres_data[i][0],
                                        genre_id=genres_data[i][1])
                    db.session.add(genre)
        elif list_type == ListType.ANIME:
            anime_genres = ApiData().get_anime_genres(details_data["name"])
            if anime_genres:
                for genre in anime_genres:
                    add_genre = AnimeGenre(anime_id=element.id,
                                           genre=genre["name"],
                                           genre_id=int(genre["mal_id"]))
                    db.session.add(add_genre)
            else:
                if len(genres_data) == 0:
                    add_genre = AnimeGenre(anime_id=element.id,
                                           genre="Unknown",
                                           genre_id=0)
                    db.session.add(add_genre)
                else:
                    for i in range(0, len(genres_data)):
                        add_genre = AnimeGenre(anime_id=element.id,
                                               genre=genres_data[i][0],
                                               genre_id=genres_data[i][1])
                        db.session.add(add_genre)

        # Add networks
        if list_type == ListType.SERIES:
            if len(networks_data) == 0:
                network = SeriesNetwork(series_id=element.id,
                                        network="Unknown")
                db.session.add(network)
            else:
                for network_data in networks_data:
                    network = SeriesNetwork(series_id=element.id,
                                            network=network_data)
                    db.session.add(network)
        elif list_type == ListType.ANIME:
            if len(networks_data) == 0:
                network = AnimeNetwork(anime_id=element.id,
                                       network="Unknown")
                db.session.add(network)
            else:
                for network_data in networks_data:
                    network = AnimeNetwork(anime_id=element.id,
                                           network=network_data)
                    db.session.add(network)

        # Add seasons and episodes
        if list_type == ListType.SERIES:
            if len(seasons_data) == 0:
                season = SeriesEpisodesPerSeason(series_id=element.id,
                                                 season=1,
                                                 episodes=1)
                db.session.add(season)
            else:
                for season_data in seasons_data:
                    season = SeriesEpisodesPerSeason(series_id=element.id,
                                                     season=season_data["season_number"],
                                                     episodes=season_data["episode_count"])
                    db.session.add(season)
        elif list_type == ListType.ANIME:
            if len(seasons_data) == 0:
                season = AnimeEpisodesPerSeason(anime_id=element.id,
                                                season=1,
                                                episodes=1)
                db.session.add(season)
            else:
                for season_data in seasons_data:
                    season = AnimeEpisodesPerSeason(anime_id=element.id,
                                                    season=season_data["season_number"],
                                                    episodes=season_data["episode_count"])
                    db.session.add(season)

        db.session.commit()
    elif list_type == ListType.MOVIES:
        movie_data = {'name': details_data.get("title", "Unknown") or 'Unknown',
                      'original_name': details_data.get("original_title", "Unknown") or 'Unknown',
                      'release_date': details_data.get("release_date", "Unknown") or 'Unknown',
                      'homepage': details_data.get("homepage", "Unknown") or 'Unknown',
                      'released': details_data.get("status", False) or False,
                      'vote_average': details_data.get("vote_average", 0) or 0,
                      'vote_count': details_data.get("vote_count", 0) or 0,
                      'synopsis': details_data.get("overview", "No overview avalaible") or 'No overview avalaible',
                      'popularity': details_data.get("popularity", 0) or 0,
                      'budget': details_data.get("budget", 0) or 0, 'revenue': details_data.get("revenue", 0) or 0,
                      'tagline': details_data.get("tagline", "-") or '-',
                      'runtime': details_data.get("runtime", 0) or 0,
                      'original_language': details_data.get("original_language", "Unknown") or 'Unknown',
                      'collection_id': details_data.get("belongs_to_collection", {}).get("id") or None,
                      'themoviedb_id': details_data.get("id"), 'image_cover': media_cover_name}

        # Actors names: list
        actors = details_data.get("credits", {}).get("cast") or None
        actors_names = []
        if actors:
            for i in range(0, len(actors)):
                actors_names.append(details_data["credits"]["cast"][i]["name"])
                if i == 4:
                    break

        # Genres and genres ID: list
        genres = details_data.get('genres') or None
        genres_data = []
        if genres:
            for i in range(0, len(genres)):
                genres_data.append([details_data["genres"][i]["name"], int(details_data["genres"][i]["id"])])

        # Add movie data to the database
        element = Movies(**movie_data)

        db.session.add(element)
        db.session.commit()

        # Add actors
        if len(actors_names) == 0:
            actors = MoviesActors(movies_id=element.id,
                                  name="Unknown")
            db.session.add(actors)
        else:
            for name in actors_names:
                actors = MoviesActors(movies_id=element.id,
                                      name=name)
                db.session.add(actors)

        # Add genres
        if len(genres_data) == 0:
            genre = MoviesGenre(movies_id=element.id,
                                genre="Unknown",
                                genre_id=0)
            db.session.add(genre)
        else:
            for i in range(0, len(genres_data)):
                genre = MoviesGenre(movies_id=element.id,
                                    genre=genres_data[i][0],
                                    genre_id=genres_data[i][1])
                db.session.add(genre)

        # Add collection data
        collection_id = movie_data['collection_id']
        if collection_id:
            collection_data = ApiData().get_collection_data(collection_id)
            if collection_data:
                collection_parts = len(collection_data.get('parts', []) or [])
                collection_name = collection_data.get('name', "Unknown") or "Unknown"
                collection_overview = collection_data.get('overview', 'No overview available.')\
                                                          or 'No overview available.'

                # Get the collection media cover
                collection_cover_path = collection_data.get("poster_path")
                if collection_cover_path:
                    collection_cover_name = "{}.jpg".format(secrets.token_hex(8))
                    issuccess = ApiData().save_api_cover(collection_cover_path, collection_cover_name,
                                                         ListType.MOVIES, collection=True)
                    if issuccess is False:
                        collection_cover_name = "default.jpg"
                else:
                    collection_cover_name = "default.jpg"

                # Add the element to the database
                add_collection = MoviesCollections(collection_id=collection_id,
                                                   parts=collection_parts,
                                                   name=collection_name,
                                                   poster=collection_cover_name,
                                                   overview=collection_overview)
                db.session.add(add_collection)

        db.session.commit()

    add_element_to_user(element.id, current_user.id, list_type, element_cat)
