import pytz
import random
import operator

from MyLists import db
from flask import url_for
from sqlalchemy import func, text
from flask_login import current_user
from _collections import OrderedDict
from MyLists.models import ListType, UserLastUpdate, SeriesList, AnimeList, MoviesList, Status, User, Series, Anime, \
    AnimeEpisodesPerSeason, SeriesEpisodesPerSeason, Movies, Ranks, followers, Frames, SeriesGenre, RoleType


def get_media_count(user_id, list_type):
    if list_type == ListType.SERIES:
        media_count = db.session.query(SeriesList.status, func.count(SeriesList.status)) \
            .filter_by(user_id=user_id).group_by(SeriesList.status).all()
    if list_type == ListType.ANIME:
        media_count = db.session.query(AnimeList.status, func.count(AnimeList.status)) \
            .filter_by(user_id=user_id).group_by(AnimeList.status).all()
    if list_type == ListType.MOVIES:
        media_count = db.session.query(MoviesList.status, func.count(MoviesList.status)) \
            .filter_by(user_id=user_id).group_by(MoviesList.status).all()

    data = {}
    total = sum(x[1] for x in media_count)
    categories = [Status.WATCHING, Status.COMPLETED, Status.COMPLETED_ANIMATION,
                  Status.ON_HOLD, Status.RANDOM, Status.DROPPED, Status.PLAN_TO_WATCH]
    for media in media_count:
        if media[0] in categories:
            data[media[0].value] = {"count": media[1],
                                    "percent": (media[1]/total)*100}
    for media in categories:
        if media.value not in data.keys():
            data[media.value] = {"count": 0,
                                 "percent": 0}

    data['total'] = total
    if total == 0:
        data['nodata'] = True
    else:
        data['nodata'] = False

    return data


def get_media_total_eps(user_id, list_type):
    if list_type == ListType.SERIES:
        media_data = db.session.query(SeriesList, SeriesEpisodesPerSeason,
                                      func.group_concat(SeriesEpisodesPerSeason.episodes)) \
            .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.media_id == SeriesList.media_id) \
            .filter(SeriesList.user_id == user_id).group_by(SeriesList.media_id).all()
    elif list_type == ListType.ANIME:
        media_data = db.session.query(AnimeList, AnimeEpisodesPerSeason,
                                      func.group_concat(AnimeEpisodesPerSeason.episodes)) \
            .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.media_id == AnimeList.media_id) \
            .filter(AnimeList.user_id == user_id).group_by(AnimeList.media_id)

    nb_eps_watched = 0
    for element in media_data:
        if element[0].status != Status.PLAN_TO_WATCH and element[0].status != Status.RANDOM:
            episodes = element[2].split(",")
            episodes = [int(x) for x in episodes]
            for i in range(1, element[0].current_season):
                nb_eps_watched += episodes[i-1]
            nb_eps_watched += element[0].last_episode_watched

    return nb_eps_watched


def get_media_score(user_id, list_type):
    if list_type == ListType.SERIES:
        media_score = db.session.query(func.count(SeriesList.score), func.count(SeriesList.media_id),
                                       func.sum(SeriesList.score)) \
            .filter(SeriesList.user_id == user_id, SeriesList.status != Status.PLAN_TO_WATCH).all()
    if list_type == ListType.ANIME:
        media_score = db.session.query(func.count(AnimeList.score), func.count(AnimeList.media_id),
                                       func.sum(AnimeList.score)) \
            .filter(AnimeList.user_id == user_id, AnimeList.status != Status.PLAN_TO_WATCH).all()
    if list_type == ListType.MOVIES:
        media_score = db.session.query(func.count(MoviesList.score), func.count(MoviesList.media_id),
                                       func.sum(MoviesList.score)) \
            .filter(MoviesList.user_id == user_id, MoviesList.status != Status.PLAN_TO_WATCH).all()

    try:
        percentage = int(int(media_score[0][0])/int(media_score[0][1])*100)
    except (ZeroDivisionError, TypeError):
        percentage = '-'

    try:
        mean_score = round(int(media_score[0][2])/int(media_score[0][0]), 2)
    except (ZeroDivisionError, TypeError):
        mean_score = '-'

    data = {'scored_media': media_score[0][0],
            'total_media': media_score[0][1],
            'percentage': percentage,
            'mean_score': mean_score}

    return data


def get_favorites(user_id):
    series_favorites = db.session.query(Series, SeriesList) \
        .join(Series, Series.id == SeriesList.media_id) \
        .filter(SeriesList.user_id == user_id, SeriesList.favorite == True).group_by(SeriesList.media_id).all()
    random.shuffle(series_favorites)

    anime_favorites = db.session.query(Anime, AnimeList) \
        .join(Anime, Anime.id == AnimeList.media_id) \
        .filter(AnimeList.user_id == user_id, AnimeList.favorite == True).group_by(AnimeList.media_id).all()
    random.shuffle(anime_favorites)

    movies_favorites = db.session.query(Movies, MoviesList) \
        .join(Movies, Movies.id == MoviesList.media_id) \
        .filter(MoviesList.user_id == user_id, MoviesList.favorite == True).group_by(MoviesList.media_id).all()
    random.shuffle(movies_favorites)

    favorites = [series_favorites, anime_favorites, movies_favorites]

    return favorites


def get_media_levels(user, list_type):
    if list_type == ListType.SERIES:
        total_time_min = user.time_spent_series
    elif list_type == ListType.ANIME:
        total_time_min = user.time_spent_anime
    elif list_type == ListType.MOVIES:
        total_time_min = user.time_spent_movies

    # Compute the corresponding level and percentage from the media time
    element_level_tmp = "{:.2f}".format(round((((400+80*total_time_min)**(1/2))-20)/40, 2))
    element_level = int(element_level_tmp.split('.')[0])
    element_percentage = int(element_level_tmp.split('.')[1])

    query_rank = Ranks.query.filter_by(level=element_level, type='media_rank\n').first()
    if query_rank:
        grade_id = url_for('static', filename='img/levels_ranks/{}'.format(query_rank.image_id))
        grade_title = query_rank.name
    else:
        grade_id = url_for('static', filename='img/levels_ranks/ReachRank49')
        grade_title = "Inheritor"

    level_info = {"level": element_level,
                  "level_percent": element_percentage,
                  "grade_id": grade_id,
                  "grade_title": grade_title}

    return level_info


def get_knowledge_grade(user):
    # Compute the corresponding level and percentage from the media time
    knowledge_level = int((((400+80*user.time_spent_series)**(1/2))-20)/40) +\
                      int((((400+80*user.time_spent_anime)**(1/2))-20)/40) +\
                      int((((400+80*user.time_spent_movies)**(1/2))-20)/40)

    query_rank = Ranks.query.filter_by(level=knowledge_level, type='knowledge_rank\n').first()
    if query_rank:
        grade_id = url_for('static', filename='img/knowledge_ranks/{}'.format(query_rank.image_id))
        grade_title = query_rank.name
    else:
        grade_id = url_for('static', filename='img/knowledge_ranks/Knowledge_Emperor_Grade_4')
        grade_title = "Knowledge Emperor Grade 4"

    return {"level": knowledge_level,
            "grade_id": grade_id,
            "grade_title": grade_title}


def get_knowledge_frame(user):
    # Compute the corresponding level and percentage from the media time
    knowledge_level = int((((400+80*user.time_spent_series)**(1/2))-20)/40) +\
                      int((((400+80*user.time_spent_anime)**(1/2))-20)/40) +\
                      int((((400+80*user.time_spent_movies)**(1/2))-20)/40)

    frame_level = round(knowledge_level/8, 0) + 1
    query_frame = Frames.query.filter_by(level=frame_level).first()

    if query_frame:
        frame_id = url_for('static', filename='img/icon_frames/new/{}'.format(query_frame.image_id))
    else:
        frame_id = url_for('static', filename='img/icon_frames/new/border_40')

    return {"level": knowledge_level,
            "frame_id": frame_id,
            "frame_level": frame_level}


def get_updates(last_update):
    update = []
    for element in last_update:
        element_data = {}
        # Season or episode update
        if not element.old_status and not element.new_status:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element.old_season, element.old_episode),
                                      "S{:02d}.E{:02d}".format(element.new_season, element.new_episode)]

        # Category update
        elif element.old_status and element.new_status:
            element_data["update"] = ["{}".format(element.old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element.new_status.value).replace("Animation", "Anime")]

        # Newly added media
        elif not element.old_status and element.new_status:
            element_data["update"] = ["{}".format(element.new_status.value)]

        # Update date and add media name
        element_data["date"] = element.date.replace(tzinfo=pytz.UTC).isoformat()
        element_data["media_name"] = element.media_name
        element_data["media_id"] = element.media_id

        if element.media_type == ListType.SERIES:
            element_data["category"] = "Series"
            element_data["icon-color"] = "fas fa-tv text-series"
            element_data["border"] = "#216e7d"
        elif element.media_type == ListType.ANIME:
            element_data["category"] = "Anime"
            element_data["icon-color"] = "fas torii-gate text-anime"
            element_data["border"] = "#945141"
        elif element.media_type == ListType.MOVIES:
            element_data["category"] = "Movies"
            element_data["icon-color"] = "fas fa-film text-movies"
            element_data["border"] = "#8c7821"

        update.append(element_data)

    return update


# ----------------------------------------------------------------------------------------------------------


def get_header_data(user):
    # Check if the current user follows the user's account
    isfollowing = False
    if user.id != current_user.id and current_user.is_following(user):
        isfollowing = True

    # Recover the number of person that follows the user
    followers = user.followers.count()

    # Recover the knowledge frame and level of the user
    knowledge_info = get_knowledge_frame(user)

    # Header info
    header_data = {"id": str(user.id),
                   "username": user.username,
                   "profile_picture": url_for('static', filename='profile_pics/{0}'.format(user.image_file)),
                   "register": user.registered_on.strftime("%d %b %Y"),
                   "followers": followers,
                   "isfollowing": isfollowing,
                   "knowledge_info": knowledge_info}

    return header_data


def get_user_data(user):
    # Recover the view count of the account and the media lists
    profile_view_count = user.profile_views
    if current_user.role != RoleType.ADMIN and user.id != current_user.id:
        user.profile_views += 1
        profile_view_count = user.profile_views
        db.session.commit()
    view_count = {"profile": profile_view_count,
                  "series": user.series_views,
                  "anime": user.anime_views,
                  "movies": user.movies_views}

    # Recover the overview user's last update
    last_update = UserLastUpdate.query.filter_by(user_id=user.id).order_by(UserLastUpdate.date.desc()).limit(7)
    media_update = get_updates(last_update)

    user_data = {"media_update": media_update,
                 "view_count": view_count}

    return user_data


def get_media_data(user):
    all_lists = [["series", ListType.SERIES, user.time_spent_series], ["anime", ListType.ANIME, user.time_spent_anime],
                 ["movies", ListType.MOVIES, user.time_spent_movies]]

    # Create dict with media as key; values are dict or list of dict with the data
    media_dict = {}
    for list_type in all_lists:
        media_count = get_media_count(user.id, list_type[1])
        media_levels = get_media_levels(user, list_type[1])
        media_score = get_media_score(user.id, list_type[1])
        media_time = list_type[2]

        media_total_eps = None
        if list_type[1] != ListType.MOVIES:
            media_total_eps = get_media_total_eps(user.id, list_type[1])

        # Each media_data dict contains all the data for one type of media
        media_data = {'time_spent_hour': round(media_time/60),
                      'time_spent_day': round(media_time/1440, 2),
                      'media_count': media_count,
                      'media_total_eps': media_total_eps,
                      'media_levels': media_levels,
                      'media_score': media_score}

        # return a media_dict with 3 keys (anime, series, movies) with media_data as values
        media_dict['{}'.format(list_type[0])] = media_data

    return media_dict


def get_follows_data(user):
    # If not <current_user>, check <follows> to show (remove the private ones if <current_user> doesn't follow them)
    if current_user.id != user.id:
        followed_by_user = user.followed.all()
        current_user_follows = current_user.followed.all()

        follows_list = []
        for follow in followed_by_user:
            if follow.private:
                if follow in current_user_follows or current_user.id == follow.id:
                    follows_list.append(follow)
            else:
                follows_list.append(follow)

        follows_to_update = []
        for follow in follows_list:
            follows_to_update.append(follow.id)

        follows_update = db.session.query(User, followers, UserLastUpdate)\
            .join(followers, followers.c.followed_id == User.id)\
            .join(UserLastUpdate, UserLastUpdate.user_id == User.id)\
            .filter(followers.c.followed_id.in_(follows_to_update), followers.c.follower_id == user.id)\
            .order_by(UserLastUpdate.date.desc()).all()
    else:
        follows_update = db.session.query(User, followers, UserLastUpdate)\
            .join(followers, followers.c.followed_id == User.id)\
            .join(UserLastUpdate, UserLastUpdate.user_id == User.id)\
            .filter(followers.c.follower_id == user.id)\
            .order_by(UserLastUpdate.date.desc()).all()

        follows_list = user.followed.all()

    follows_update_list = []
    for follow in follows_update[:11]:
        follows = {'username': follow[0].username}
        follows.update(get_updates([follow[3]])[0])
        follows_update_list.append(follows)

    return follows_list, follows_update_list


def get_more_stats(user):

    def get_episodes_and_time(element):
        if element[1].status == Status.COMPLETED or element[1].status == Status.COMPLETED_ANIMATION:
            try:
                return [1, element[0].runtime]
            except:
                return [element[0].total_episodes, int(element[0].episode_duration)*element[0].total_episodes]
        elif element[1].status != Status.PLAN_TO_WATCH and element[1].status != Status.RANDOM:
            nb_episodes = [m.episodes for m in element[0].eps_per_season]
            
            ep_duration = int(element[0].episode_duration)
            ep_counter = 0
            for i in range(0, element[1].current_season - 1):
                ep_counter += int(nb_episodes[i])
            episodes_watched = ep_counter + element[1].last_episode_watched
            time_watched = (ep_duration * episodes_watched)
            return [episodes_watched, time_watched]
        else:
            return [0, 0]

    series_data = db.session.query(Series, SeriesList) \
        .join(SeriesList, SeriesList.media_id == Series.id) \
        .filter(SeriesList.user_id == user.id)

    # test = db.session.query(func.strftime('%Y', Series.first_air_date).label('year'),
    #                         func.count(Series.first_air_date))\
    #     .join(SeriesList, Series.id == SeriesList.media_id)\
    #     .filter(SeriesList.user_id == current_user.id)\
    #     .group_by(func.strftime('%Y', Series.first_air_date)).order_by(text('year desc')).all()

    # test = db.session.query(func.strftime('%Y', Movies.release_date).label('year'),
    #                         func.count(Movies.release_date))\
    #     .join(MoviesList, Movies.id == MoviesList.media_id)\
    #     .filter(MoviesList.user_id == current_user.id)\
    #     .group_by(func.strftime('%Y', Movies.release_date)).order_by(text('year desc')).all()

    test = db.session.query(SeriesGenre.genre, func.count(SeriesGenre.genre).label('count')) \
        .join(SeriesList, SeriesGenre.media_id == SeriesList.media_id) \
        .join(Series, Series.id == SeriesList.media_id) \
        .filter(SeriesList.user_id == current_user.id)\
        .group_by(SeriesGenre.genre).order_by(text('count desc')).all()

    anime_data = db.session.query(Anime, AnimeList) \
        .join(AnimeList, AnimeList.media_id == Anime.id) \
        .filter(AnimeList.user_id == user.id)

    movies_data = db.session.query(Movies, MoviesList) \
        .join(MoviesList, MoviesList.media_id == Movies.id) \
        .filter(MoviesList.user_id == user.id)

    media_data = [series_data, anime_data, movies_data]

    data = {}
    for index, media in enumerate(media_data):
        genres_time = {}
        periods_time = OrderedDict({'1960-1969': 0, '1970-1979': 0, '1980-1989': 0, '1990-1999': 0, '2000-2009': 0,
                                    '2010-2019': 0, '2020+': 0})
        episodes_time = OrderedDict({'1-19': 0, '20-49': 0, '50-99': 0, '100-149': 0, '150-199': 0, '200-299': 0,
                                     '300-399': 0, '400-499': 0, '500+': 0})
        movies_time = OrderedDict({'<1h': 0, '1h-1h29': 0, '1h30-1h59': 0, '2h00-2h29': 0, '2h30-2h59': 0, '3h+': 0})
        for element in media:
            # Number of episodes and the time watched by element
            episodes_watched, time_watched = get_episodes_and_time(element)

            # Genres stats
            for genre in [m.genre for m in element[0].genres]:
                if genre not in genres_time:
                    genres_time[genre] = time_watched
                else:
                    genres_time[genre] += time_watched

            # Period stats
            try:
                airing_year = int(element[0].first_air_date.split('-')[0])
            except:
                try:
                    airing_year = int(element[0].release_date.split('-')[0])
                except:
                    airing_year = 0

            if 1960 <= airing_year < 1970:
                periods_time['1960-1969'] += 1
            elif 1970 <= airing_year < 1980:
                periods_time['1970-1979'] += 1
            elif 1980 <= airing_year < 1990:
                periods_time['1980-1989'] += 1
            elif 1990 <= airing_year < 2000:
                periods_time['1990-1999'] += 1
            elif 2000 <= airing_year < 2010:
                periods_time['2000-2009'] += 1
            elif 2010 <= airing_year < 2020:
                periods_time['2010-2019'] += 1
            elif airing_year >= 2020:
                periods_time['2020+'] += 1

            # Episodes / time stats
            if index != 2:
                if 1 <= episodes_watched < 19:
                    episodes_time['1-19'] += 1
                elif 20 <= episodes_watched < 49:
                    episodes_time['20-49'] += 1
                elif 50 <= episodes_watched < 99:
                    episodes_time['50-99'] += 1
                elif 100 <= episodes_watched < 149:
                    episodes_time['100-149'] += 1
                elif 150 <= episodes_watched < 199:
                    episodes_time['150-199'] += 1
                elif 200 <= episodes_watched < 299:
                    episodes_time['200-299'] += 1
                elif 300 <= episodes_watched < 399:
                    episodes_time['300-399'] += 1
                elif 400 <= episodes_watched < 499:
                    episodes_time['400-499'] += 1
                elif episodes_watched >= 500:
                    episodes_time['500+'] += 1
            else:
                if time_watched < 60:
                    movies_time['<1h'] += 1
                elif 60 <= time_watched < 90:
                    movies_time['1h-1h29'] += 1
                elif 90 <= time_watched < 120:
                    movies_time['1h30-1h59'] += 1
                elif 120 <= time_watched < 150:
                    movies_time['2h00-2h29'] += 1
                elif 150 <= time_watched < 180:
                    movies_time['2h30-2h59'] += 1
                elif time_watched >= 180:
                    movies_time['3h+'] += 1

        # Rename
        if index == 0:
            genres_time['Action/Adventure'] = genres_time.pop('Action & Adventure', 0)
            genres_time['War/Politics'] = genres_time.pop('War & Politics', 0)
            genres_time['Sci-Fi/Fantasy'] = genres_time.pop('Sci-Fi & Fantasy', 0)
            genres_time.pop('Unknown', 0)

        if all(x == 0 for x in genres_time.values()):
            genres_time = {}
        else:
            genres_time = sorted(genres_time.items(), key=operator.itemgetter(1), reverse=True)
        if all(x == 0 for x in periods_time.values()):
            periods_time = {}
        if all(x == 0 for x in episodes_time.values()):
            episodes_time = {}
        if all(x == 0 for x in movies_time.values()):
            movies_time = {}

        if index == 0:
            data.update({'Series_genres': genres_time,
                         'Series_periods': periods_time,
                         'Series_episodes': episodes_time})
        elif index == 1:
            data.update({'Anime_genres': genres_time,
                         'Anime_periods': periods_time,
                         'Anime_episodes': episodes_time})
        else:
            data.update({'Movies_genres': genres_time,
                         'Movies_periods': periods_time,
                         'Movies_times': movies_time})

    return data


def get_all_follows_data(user):
    # If not <current_user>, check <follows> to show (remove the private ones if <current_user> does not follow them)
    if current_user.id != user.id:
        followed_by_user = user.followed.all()
        current_user_follows = current_user.followed.all()

        follows_to_display = []
        for follow in followed_by_user:
            if follow.private:
                if follow in current_user_follows or current_user.id == follow.id:
                    follows_to_display.append(follow)
            else:
                follows_to_display.append(follow)
    else:
        follows_to_display = current_user.followed.all()

    return follows_to_display
