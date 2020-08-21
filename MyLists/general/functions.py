import json
import secrets
import requests
import urllib.request

from PIL import Image
from pathlib import Path
from MyLists import db, app
from datetime import datetime
from MyLists.models import ListType, Status, User, Movies, Badges, Ranks, Frames, MoviesCollections, get_total_time


def compute_media_time_spent(list_type):
    users = User.query.all()

    for user in users:
        media_list = get_total_time(user.id, list_type)

        if list_type != ListType.MOVIES:
            total_time = 0
            for media in media_list:
                if media[0].status == Status.COMPLETED:
                    try:
                        total_time += media[1].episode_duration*media[1].total_episodes*(1+media[0].rewatched)
                    except:
                        pass
                elif media[0].status != Status.PLAN_TO_WATCH or media[0].status != Status.RANDOM:
                    try:
                        episodes = [eps.episodes for eps in media[1].eps_per_season]
                        for i in range(1, media[0].current_season):
                            total_time += media[1].episode_duration*episodes[i - 1]
                        total_time += media[0].last_episode_watched*media[1].episode_duration
                    except:
                        pass
        elif list_type == ListType.MOVIES:
            total_time = 0
            for media in media_list:
                if media[0].status != Status.PLAN_TO_WATCH:
                    try:
                        total_time += media[1].runtime*(1+media[0].rewatched)
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
        ranks[i - 1].level = int(list_all_ranks[i][0])
        ranks[i - 1].image_id = list_all_ranks[i][1]
        ranks[i - 1].name = list_all_ranks[i][2]
        ranks[i - 1].type = list_all_ranks[i][3]


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
        badges[i - 1].threshold = int(list_all_badges[i][0])
        badges[i - 1].image_id = list_all_badges[i][1]
        badges[i - 1].title = list_all_badges[i][2]
        badges[i - 1].type = list_all_badges[i][3]
        badges[i - 1].genres_id = genre_id


def add_frames_to_db():
    list_all_frames = []
    path = Path(app.root_path, 'static/csv_data/icon_frames.csv')
    with open(path) as fp:
        for line in fp:
            list_all_frames.append(line.split(";"))

    for i in range(1, len(list_all_frames)):
        frame = Frames(level=int(list_all_frames[i][0]),
                       image_id=list_all_frames[i][1])
        db.session.add(frame)
    db.session.commit()


def refresh_db_frames():
    list_all_frames = []
    path = Path(app.root_path, 'static/csv_data/icon_frames.csv')
    with open(path) as fp:
        for line in fp:
            list_all_frames.append(line.split(";"))

    frames = Frames.query.order_by(Frames.id).all()
    for i in range(1, len(list_all_frames)):
        frames[i - 1].level = int(list_all_frames[i][0])
        frames[i - 1].image_id = list_all_frames[i][1]


def add_collections_movies():
    print('Started to add movies collection.')
    local_covers_path = Path(app.root_path, "static/covers/movies_collection_covers/")

    all_movies = Movies.query.filter_by().all()
    for index, movie in enumerate(all_movies):
        print("Movie: {}/{}".format(index + 1, len(all_movies)))
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
                    difference = (utc_now - part_date_datetime).total_seconds()
                    if float(difference) < 0:
                        remove += 1
                except:
                    pass

            collection_parts = len(data_collection["parts"]) - remove
            collection_poster_id = "{}.jpg".format(secrets.token_hex(8))

            urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{}".format(collection_poster),
                                       "{}/{}".format(local_covers_path, collection_poster_id))

            img = Image.open("{}/{}".format(local_covers_path, collection_poster_id))
            img = img.resize((300, 450), Image.ANTIALIAS)
            img.save("{0}/{1}".format(local_covers_path, collection_poster_id), quality=90)

            movie.collection_id = collection_id

            # Test if collection already in MoviesCollection
            if MoviesCollections.query.filter_by(collection_id=collection_id).first() is not None:
                db.session.commit()
                continue

            add_collection = MoviesCollections(collection_id=collection_id,
                                               parts=collection_parts,
                                               name=collection_name,
                                               movies_names=None,
                                               releases_dates=None,
                                               poster=collection_poster_id,
                                               overview=collection_overview)

            db.session.add(add_collection)
            db.session.commit()
        except:
            continue
    print('Finished adding movies collection.')


def refresh_collections_movies():
    print('Started to refresh movies collection.')

    all_collection_movies = MoviesCollections.query.filter_by().all()
    for index, collection in enumerate(all_collection_movies):
        print("Movie: {}/{}".format(index + 1, len(all_collection_movies)))
        try:
            response = requests.get("https://api.themoviedb.org/3/collection/{0}?api_key={1}"
                                    .format(collection.collection_id, app.config['THEMOVIEDB_API_KEY']))

            data = json.loads(response.text)

            remove = 0
            utc_now = datetime.utcnow()
            for part in data["parts"]:
                part_date = part['release_date']
                try:
                    part_date_datetime = datetime.strptime(part_date, '%Y-%m-%d')
                    difference = (utc_now - part_date_datetime).total_seconds()
                    if float(difference) < 0:
                        remove += 1
                except:
                    remove += 1

            collection.parts = len(data["parts"]) - remove
            collection.movies_names = ', '.join([part['title'] for part in data["parts"]])
            collection.releases_dates = ', '.join([part['release_date'] for part in data["parts"]])

            db.session.commit()
        except:
            continue
    print('Finished refreshing movies collection.')
