import json
import secrets
import requests
import urllib.request

from PIL import Image
from pathlib import Path
from flask import url_for
from MyLists import db, app
from sqlalchemy import func
from datetime import datetime
from MyLists.models import ListType, Status, User, AnimeList, Anime, AnimeEpisodesPerSeason, SeriesEpisodesPerSeason, \
    SeriesList, Series, MoviesList, Movies, Badges, SeriesActors, MoviesActors, MoviesCollections, AnimeActors, Ranks


def get_trending_data(trends_data, list_type):
    trending_list = []
    tmdb_posters_path = "http://image.tmdb.org/t/p/w300"

    i = 0
    if list_type == ListType.SERIES:
        trends_data = trends_data.get("results")
        if trends_data is None:
            return None

        for data in trends_data:
            series = {"title": data.get("name", "Unknown") or "Unknown"}
            media_cover_path = data.get("poster_path") or None
            if media_cover_path:
                series["poster_path"] = tmdb_posters_path + media_cover_path
            else:
                series["poster_path"] = url_for('static', filename='covers/default.jpg')
            series["first_air_date"] = data.get("first_air_date", "Unknown") or "Unknown"
            if series["first_air_date"] != "Unknown":
                series["first_air_date"] = datetime.strptime(series["first_air_date"], '%Y-%m-%d').strftime("%d %b %Y")
            series["overview"] = data.get("overview", "There is no overview for this series.") \
                                 or "There is no overview for this series."
            series["tmdb_link"] = "https://www.themoviedb.org/tv/{}".format(data.get("id"))
            trending_list.append(series)
            i += 1
            if i > 11:
                break

        return trending_list
    elif list_type == ListType.ANIME:
        trends_data = trends_data.get("top")
        if trends_data is None:
            return None

        for data in trends_data:
            anime = {"title": data.get("title", "Unknown") or "Unknown"}
            media_cover_path = data.get("image_url") or None
            if media_cover_path:
                anime["poster_path"] = media_cover_path
            else:
                anime["poster_path"] = url_for('static', filename='covers/default.jpg')
            anime["first_air_date"] = data.get("start_date", 'Unknown') or "Unknown"
            anime["overview"] = "There is no overview from this API. " \
                                "You can check it on MyAnimeList by clicking on the title"
            anime["tmdb_link"] = data.get("url")
            trending_list.append(anime)
            i += 1
            if i > 11:
                break

        return trending_list
    elif list_type == ListType.MOVIES:
        trends_data = trends_data.get("results")
        if trends_data is None:
            return None

        for data in trends_data:
            movies = {"title": data.get("title", "Unknown") or "Unknown"}
            media_cover_path = data.get("poster_path") or None
            if media_cover_path:
                movies["poster_path"] = tmdb_posters_path + media_cover_path
            else:
                movies["poster_path"] = url_for('static', filename='covers/default.jpg')
            movies["release_date"] = data.get("release_date", "Unknown") or "Unknown"
            if movies["release_date"] != "Unknown":
                movies["release_date"] = datetime.strptime(movies["release_date"], '%Y-%m-%d').strftime("%d %b %Y")
            movies["overview"] = data.get("overview", "No overview available for this movie.") or \
                                 'No overview available for this movie.'
            movies["tmdb_link"] = "https://www.themoviedb.org/movie/{}".format(data.get("id"))
            trending_list.append(movies)
            i += 1
            if i > 11:
                break

        return trending_list


def compute_media_time_spent(list_type):
    users = User.query.all()

    for user in users:
        if list_type == ListType.ANIME:
            element_data = db.session.query(AnimeList, Anime, func.group_concat(AnimeEpisodesPerSeason.episodes))\
                .join(Anime, Anime.id == AnimeList.anime_id)\
                .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.anime_id == AnimeList.anime_id)\
                .filter(AnimeList.user_id == user.id).group_by(AnimeList.anime_id)
        elif list_type == ListType.SERIES:
            element_data = db.session.query(SeriesList, Series, func.group_concat(SeriesEpisodesPerSeason.episodes))\
                .join(Series, Series.id == SeriesList.series_id)\
                .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.series_id == SeriesList.series_id)\
                .filter(SeriesList.user_id == user.id).group_by(SeriesList.series_id)
        elif list_type == ListType.MOVIES:
            element_data = db.session.query(MoviesList, Movies).join(Movies, Movies.id == MoviesList.movies_id)\
                .filter(MoviesList.user_id == user.id).group_by(MoviesList.movies_id)

        if list_type != ListType.MOVIES:
            total_time = 0
            for element in element_data:
                if element[0].status == Status.COMPLETED:
                    try:
                        total_time += element[1].episode_duration * element[1].total_episodes
                    except:
                        pass
                elif element[0].status != Status.PLAN_TO_WATCH or element[0].status != Status.RANDOM:
                    try:
                        episodes = element[2].split(",")
                        episodes = [int(x) for x in episodes]
                        for i in range(1, element[0].current_season):
                            total_time += element[1].episode_duration * episodes[i-1]
                        total_time += element[0].last_episode_watched * element[1].episode_duration
                    except:
                        pass
        elif list_type == ListType.MOVIES:
            total_time = 0
            for element in element_data:
                if element[0].status != Status.PLAN_TO_WATCH:
                    try:
                        total_time += element[1].runtime
                    except:
                        pass

        if list_type == ListType.ANIME:
            user.time_spent_anime = total_time
        elif list_type == ListType.SERIES:
            user.time_spent_series = total_time
        elif list_type == ListType.MOVIES:
            user.time_spent_movies = total_time

        db.session.commit()


# ---------------------------------------- DB add/refresh from CSV data ---------------------------------------------- #


def add_ranks_to_db():
    list_all_ranks = []
    path = Path(app.root_path, 'static/csv_data/ranks.csv')
    with open(path) as fp:
        for line in fp:
            list_all_ranks.append(line.split(";"))

    for i in range(1, len(list_all_ranks)):
        rank = Ranks(level=int(list_all_ranks[i][0]),
                     image_id=list_all_ranks[i][1],
                     name=list_all_ranks[i][2],
                     type=list_all_ranks[i][3])
        db.session.add(rank)
    db.session.commit()


def refresh_db_ranks():
    list_all_ranks = []
    path = Path(app.root_path, 'static/csv_data/ranks.csv')
    with open(path) as fp:
        for line in fp:
            list_all_ranks.append(line.split(";"))

    ranks = Ranks.query.order_by(Ranks.id).all()
    for i in range(1, len(list_all_ranks)):
        ranks[i-1].level = int(list_all_ranks[i][0])
        ranks[i-1].image_id = list_all_ranks[i][1]
        ranks[i-1].name = list_all_ranks[i][2]
        ranks[i-1].type = list_all_ranks[i][3]


def add_badges_to_db():
    list_all_badges = []
    path = Path(app.root_path, 'static/csv_data/badges.csv')
    with open(path) as fp:
        for line in fp:
            list_all_badges.append(line.split(";"))

    for i in range(1, len(list_all_badges)):
        try:
            genre_id = str(list_all_badges[i][4])
        except:
            genre_id = None
        badge = Badges(threshold=int(list_all_badges[i][0]),
                       image_id=list_all_badges[i][1],
                       title=list_all_badges[i][2],
                       type=list_all_badges[i][3],
                       genres_id=genre_id)
        db.session.add(badge)
    db.session.commit()


def refresh_db_badges():
    list_all_badges = []
    path = Path(app.root_path, 'static/csv_data/badges.csv')
    with open(path) as fp:
        for line in fp:
            list_all_badges.append(line.split(";"))

    badges = Badges.query.order_by(Badges.id).all()
    for i in range(1, len(list_all_badges)):
        try:
            genre_id = str(list_all_badges[i][4])
        except:
            genre_id = None
        badges[i-1].threshold = int(list_all_badges[i][0])
        badges[i-1].image_id = list_all_badges[i][1]
        badges[i-1].title = list_all_badges[i][2]
        badges[i-1].type = list_all_badges[i][3]
        badges[i-1].genres_id = genre_id


# -------------------------------------------- Add data Retroactively ------------------------------------------------ #


def add_actors_movies():
    all_movies = Movies.query.all()
    for i in range(0, len(all_movies)):
        tmdb_movies_id = all_movies[i].themoviedb_id
        movies_id = all_movies[i].id
        response = requests.get("https://api.themoviedb.org/3/movie/{0}/credits?api_key={1}"
                                .format(tmdb_movies_id, app.config['THEMOVIEDB_API_KEY']))
        element_actors = json.loads(response.text)

        try:
            actors_names = []
            for j in range(0, len(element_actors["cast"])):
                try:
                    actors_names.append(element_actors["cast"][j]["name"])
                    if j == 3:
                        break
                except:
                    pass
        except:
            pass

        if len(actors_names) == 0:
            actors = MoviesActors(movies_id=movies_id,
                                  name="Unknown")
            db.session.add(actors)
        else:
            for k in range(0, len(actors_names)):
                actors = MoviesActors(movies_id=movies_id,
                                      name=actors_names[k])
                db.session.add(actors)

        db.session.commit()


def add_collections_movies():
    local_covers_path = Path(app.root_path, "static\\covers\\movies_collection_covers\\")
    all_movies = Movies.query.filter_by(themoviedb_id=9799).all()
    for movie in all_movies:
        tmdb_movies_id = movie.themoviedb_id
        try:
            response = requests.get("https://api.themoviedb.org/3/movie/{0}?api_key={1}"
                                    .format(tmdb_movies_id, app.config['THEMOVIEDB_API_KEY']))

            data = json.loads(response.text)

            collection_id = data["belongs_to_collection"]["id"]
            collection_poster = data["belongs_to_collection"]["poster_path"]

            response_collection = requests.get("https://api.themoviedb.org/3/collection/{0}?api_key={1}"
                                               .format(collection_id, app.config['THEMOVIEDB_API_KEY']))

            data_collection = json.loads(response_collection.text)

            collection_name = data_collection["name"]
            collection_overview = data_collection["overview"]

            remove = 0
            utc_now = datetime.utcnow()
            for part in data_collection["parts"]:
                part_date = part['release_date']
                try:
                    part_date_datetime = datetime.strptime(part_date, '%Y-%m-%d')
                    difference = (utc_now-part_date_datetime).total_seconds()
                    if float(difference) < 0:
                        remove += 1
                except:
                    pass

            collection_parts = len(data_collection["parts"]) - remove

            collection_poster_id = "{}.jpg".format(secrets.token_hex(8))

            urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{}".format(collection_poster),
                                       "{}{}".format(local_covers_path, collection_poster_id))

            img = Image.open("{}{}".format(local_covers_path, collection_poster_id))
            img = img.resize((300, 450), Image.ANTIALIAS)
            img.save("{0}{1}".format(local_covers_path, collection_poster_id), quality=90)

            movie.collection_id = collection_id

            # Test if collection already in MoviesCollection
            if MoviesCollections.query.filter_by(collection_id=collection_id).first() is not None:
                db.session.commit()
                continue

            add_collection = MoviesCollections(collection_id=collection_id,
                                               parts=collection_parts,
                                               name=collection_name,
                                               poster=collection_poster_id,
                                               overview=collection_overview)

            db.session.add(add_collection)
            db.session.commit()
        except:
            continue


def add_actors_series():
    all_series = Series.query.all()
    for i in range(0, len(all_series)):
        tmdb_series_id = all_series[i].themoviedb_id
        series_id = all_series[i].id
        response = requests.get("https://api.themoviedb.org/3/tv/{0}/credits?api_key={1}"
                                .format(tmdb_series_id, app.config['THEMOVIEDB_API_KEY']))
        element_actors = json.loads(response.text)

        try:
            actors_names = []
            for j in range(0, len(element_actors["cast"])):
                try:
                    actors_names.append(element_actors["cast"][j]["name"])
                    if j == 3:
                        break
                except:
                    pass
        except:
            pass

        if len(actors_names) == 0:
            actors = SeriesActors(series_id=series_id,
                                  name="Unknown")
            db.session.add(actors)
        else:
            for k in range(0, len(actors_names)):
                actors = SeriesActors(series_id=series_id,
                                      name=actors_names[k])
                db.session.add(actors)

        db.session.commit()


def add_actors_anime():
    all_anime = Anime.query.all()
    for i in range(0, len(all_anime)):
        tmdb_anime_id = all_anime[i].themoviedb_id
        anime_id = all_anime[i].id
        response = requests.get("https://api.themoviedb.org/3/tv/{0}/credits?api_key={1}"
                                .format(tmdb_anime_id, app.config['THEMOVIEDB_API_KEY']))
        element_actors = json.loads(response.text)

        try:
            actors_names = []
            for j in range(0, len(element_actors["cast"])):
                try:
                    actors_names.append(element_actors["cast"][j]["name"])
                    if j == 3:
                        break
                except:
                    pass
        except:
            pass

        if len(actors_names) == 0:
            actors = AnimeActors(anime_id=anime_id,
                                 name="Unknown")
            db.session.add(actors)
        else:
            for k in range(0, len(actors_names)):
                actors = AnimeActors(anime_id=anime_id,
                                     name=actors_names[k])
                db.session.add(actors)

        db.session.commit()
