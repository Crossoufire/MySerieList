import json
import requests
from pathlib import Path
from MyLists import db, app
from flask_login import current_user
from MyLists.API_data import ApiData
from MyLists.main.add_db import AddtoDB
from MyLists.main.media_object import MediaDetails
from MyLists.models import ListType, Status, Movies, Badges, Ranks, Frames, SeriesGenre, SeriesList, Anime, Series, \
    AnimeList, MoviesList, AnimeGenre, MoviesGenre, get_total_time, SeriesActors, AnimeActors, MoviesActors, Games, \
    GamesList


def compute_media_time_spent():
    for list_type in ListType:
        query = get_total_time(list_type)
        for q in query:
            setattr(q[0], f"time_spent_{list_type.value.replace('list', '')}", q[3])


# --- DB add/refresh from CSV data -----------------------------------------------------------------------------


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


def correct_orphan_media():
    def get_orphan_genres_and_actors(api_id, list_type, media_id):
        media_data = ApiData().get_details_and_credits_data(api_id, list_type)
        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            data = MediaDetails(media_data, list_type).get_media_details()
            if not data['tv_data']:
                return None
        elif list_type == ListType.MOVIES:
            data = MediaDetails(media_data, list_type).get_media_details()
            if not data['movies_data']:
                return None

        if list_type == ListType.SERIES:
            for genre in data['genres_data']:
                genre.update({'media_id': media_id})
                db.session.add(SeriesGenre(**genre))
            for actor in data['actors_data']:
                actor.update({'media_id': media_id})
                db.session.add(SeriesActors(**actor))
        elif list_type == ListType.ANIME:
            if len(data['anime_genres_data']) > 0:
                for genre in data['anime_genres_data']:
                    genre.update({'media_id': media_id})
                    db.session.add(AnimeGenre(**genre))
            else:
                for genre in data['genres_data']:
                    genre.update({'media_id': media_id})
                    db.session.add(AnimeGenre(**genre))
            for actor in data['actors_data']:
                actor.update({'media_id': media_id})
                db.session.add(AnimeActors(**actor))
        elif list_type == ListType.MOVIES:
            for genre in data['genres_data']:
                genre.update({'media_id': media_id})
                db.session.add(MoviesGenre(**genre))
            for actor in data['actors_data']:
                actor.update({'media_id': media_id})
                db.session.add(MoviesActors(**actor))

        # Commit the new changes
        db.session.commit()

        return True

    query = db.session.query(Series, SeriesGenre).outerjoin(SeriesGenre, SeriesGenre.media_id == Series.id).all()
    for q in query:
        if q[1] is None:
            info = get_orphan_genres_and_actors(q[0].themoviedb_id, ListType.SERIES, media_id=q[0].id)
            if info is True:
                app.logger.info(f'Orphan series corrected with ID [{q[0].id}]: {q[0].name}')
            else:
                app.logger.info(f'Orphan series NOT corrected with ID [{q[0].id}]: {q[0].name}')

    query = db.session.query(Anime, AnimeGenre).outerjoin(AnimeGenre, AnimeGenre.media_id == Anime.id).all()
    for q in query:
        if q[1] is None:
            info = get_orphan_genres_and_actors(q[0].themoviedb_id, ListType.ANIME, media_id=q[0].id)
            if info is True:
                app.logger.info(f'Orphan anime corrected with ID [{q[0].id}]: {q[0].name}')
            else:
                app.logger.info(f'Orphan anime NOT corrected with ID [{q[0].id}]: {q[0].name}')

    query = db.session.query(Movies, MoviesGenre).outerjoin(MoviesGenre, MoviesGenre.media_id == Movies.id).all()
    for q in query:
        if q[1] is None:
            info = get_orphan_genres_and_actors(q[0].themoviedb_id, ListType.MOVIES, media_id=q[0].id)
            if info is True:
                app.logger.info(f'Orphan movie corrected with ID [{q[0].id}]: {q[0].name}')
            else:
                app.logger.info(f'Orphan movie NOT corrected with ID [{q[0].id}]: {q[0].name}')


def add_hltb_time():
    list_all_hltb_games = []
    path = Path(app.root_path, 'static/csv_data/HLTB_games.csv')
    with open(path, encoding='utf-8') as fp:
        for line in fp:
            list_all_hltb_games.append(line.split(";"))

    all_games = Games.query.all()
    for game in all_games:
        for htlb_game in list_all_hltb_games:
            if game.name == htlb_game[1]:
                print(game.name)
                try:
                    game.hltb_main_time = float(htlb_game[2])*60
                except:
                    pass
                try:
                    game.hltb_main_and_extra_time = float(htlb_game[3])*60
                except:
                    pass
                try:
                    game.hltb_total_complete_time = float(htlb_game[4])*60
                except:
                    pass
                db.session.commit()


def add_manual_games():
    headers = {'Client-ID': '5i5pi21s0ninkmp6jj09ix4l6fw5bd',
               'Authorization': 'Bearer ' + '46gsxkz0svtqzujd4znmjqilhq0xa5'}

    list_all_manual_games = []
    path = Path(app.root_path, 'static/csv_data/amazon_games.csv')
    with open(path, encoding='utf-8') as fp:
        for line in fp:
            list_all_manual_games.append(line.strip())

    all_games = Games.query.all()
    all_games_name = [x.name for x in all_games]
    for game in list_all_manual_games:
        if game in all_games_name:
            continue
        else:
            try:
                body = 'fields name, cover.image_id, collection.name, game_engines.name, game_modes.name, ' \
                       'platforms.name, genres.name, player_perspectives.name, total_rating, total_rating_count, ' \
                       'first_release_date, involved_companies.company.name, involved_companies.developer, ' \
                       'involved_companies.publisher, storyline, summary, themes.name, url, external_games.uid,' \
                       ' external_games.category; where name="{}";'.format(game)

                response = requests.post('https://api.igdb.com/v4/games', data=body, headers=headers)
                data = json.loads(response.text)

                media_details = MediaDetails(data, ListType.GAMES).get_media_details()
                media = AddtoDB(media_details, ListType.GAMES).add_media_to_db()

                in_user_list = GamesList.query.filter_by(user_id=current_user.id, media_id=media.id).first()
                if not in_user_list:
                    user_list = GamesList(user_id=current_user.id,
                                          media_id=media.id,
                                          status=Status.OWNED,
                                          completion=False,
                                          playtime=0)
                    db.session.add(user_list)
                    db.session.commit()
            except:
                continue

