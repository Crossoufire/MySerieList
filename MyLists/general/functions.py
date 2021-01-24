from pathlib import Path
from MyLists import db, app
from MyLists.models import ListType, Status, User, Movies, Badges, Ranks, Frames, get_total_time, SeriesList, \
    AnimeList, Series, Anime, MoviesList


def compute_media_time_spent():
    users = User.query.all()

    for user in users:
        for list_type in ListType:
            media_list = get_total_time(user.id, list_type)
            total_time = 0
            if list_type == ListType.SERIES or list_type == ListType.ANIME:
                for media in media_list:
                    try:
                        total_time += media[0].episode_duration * media[1].eps_watched
                    except Exception as e:
                        app.logger.info('[ERROR] - {}. [MEDIA]: {}'.format(e, media[0].name))
            elif list_type == ListType.MOVIES:
                for media in media_list:
                    try:
                        total_time += media[0].runtime * media[1].eps_watched
                    except Exception as e:
                        app.logger.info('[ERROR] - {}. [MEDIA]: {}'.format(e, media[0].name))

            if list_type == ListType.SERIES:
                user.time_spent_series = total_time
            elif list_type == ListType.ANIME:
                user.time_spent_anime = total_time
            elif list_type == ListType.MOVIES:
                user.time_spent_movies = total_time


# ---------------------------------------- DB add/refresh from CSV data ------------------------------------------- #


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


def add_eps_watched():
    series_list = db.session.query(Series, SeriesList).join(Series, Series.id == SeriesList.media_id).all()
    anime_list = db.session.query(Anime, AnimeList).join(Anime, Anime.id == AnimeList.media_id).all()
    movies_list = db.session.query(Movies, MoviesList).join(Movies, Movies.id == MoviesList.media_id).all()

    for series in series_list:
        if series[1].status == Status.RANDOM or series[1].status == Status.PLAN_TO_WATCH:
            series[1].eps_watched = 0
        else:
            season = series[1].current_season
            rewatched = series[1].rewatched
            eps = series[1].last_episode_watched
            eps_seasons = [x.episodes for x in series[0].eps_per_season]
            series[1].eps_watched = (sum(eps_seasons[:season-1]) + eps) + (rewatched * series[0].total_episodes)
    db.session.commit()

    for anime in anime_list:
        if anime[1].status == Status.RANDOM or anime[1].status == Status.PLAN_TO_WATCH:
            anime[1].eps_watched = 0
        else:
            season = anime[1].current_season
            rewatched = anime[1].rewatched
            eps = anime[1].last_episode_watched
            eps_seasons = [x.episodes for x in anime[0].eps_per_season]
            anime[1].eps_watched = (sum(eps_seasons[:season-1]) + eps) + (rewatched * anime[0].total_episodes)

    for movie in movies_list:
        if movie[1].status == Status.PLAN_TO_WATCH:
            movie[1].eps_watched = 0
        else:
            movie[1].eps_watched = 1 + movie[1].rewatched
    db.session.commit()
