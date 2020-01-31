import pytz

from MyLists import db
from flask import url_for
from sqlalchemy import func
from flask_login import current_user

from MyLists.main.functions import get_level_and_grade, get_knowledge_grade
from MyLists.models import ListType, UserLastUpdate, SeriesList, AnimeList, MoviesList, Status, \
    AnimeEpisodesPerSeason, SeriesEpisodesPerSeason


def get_account_data(user, user_name):
    # Recover the follows list
    follows_list = user.followed.all()

    follows_list_data = []
    for follow in follows_list:
        picture_url = url_for('static', filename='profile_pics/{}'.format(follow.image_file))
        follow_data = {"username": follow.username,
                       "user_id": follow.id,
                       "picture": picture_url}

        if follow.private:
            if current_user.id == 1 or current_user.is_following(follow):
                follows_list_data.append(follow_data)
            elif current_user.id == follow.id:
                follows_list_data.append(follow_data)
        else:
            follows_list_data.append(follow_data)

    # Recover the number of user that follows you
    followers = user.followers.count()

    # Recover the view count of the account and the media lists
    if current_user.id != 1 and user.id != current_user.id:
        user.profile_views += 1
        profile_view_count = user.profile_views
        db.session.commit()
    else:
        profile_view_count = user.profile_views
    view_count = {"profile": profile_view_count,
                  "series": user.series_views,
                  "anime": user.anime_views,
                  "movies": user.movies_views}

    account_data = {"series": {},
                    "movies": {},
                    "anime": {},
                    "id": user.id,
                    "username": user_name,
                    "follows": follows_list_data,
                    "followers": followers,
                    "view_count": view_count,
                    "register": user.registered_on.strftime("%d %b %Y")}

    if user.id != current_user.id and current_user.is_following(user):
        account_data["isfollowing"] = True
    else:
        account_data["isfollowing"] = False

    # Recover the profile picture
    account_data["profile_picture"] = url_for('static', filename='profile_pics/{0}'.format(user.image_file))

    # Time spent in hours for all media
    account_data["series"]["time_spent_hour"] = round(user.time_spent_series/60)
    account_data["movies"]["time_spent_hour"] = round(user.time_spent_movies/60)
    account_data["anime"]["time_spent_hour"] = round(user.time_spent_anime/60)

    # Time spent in days for all media
    account_data["series"]["time_spent_day"] = round(user.time_spent_series/1440, 2)
    account_data["movies"]["time_spent_day"] = round(user.time_spent_movies/1440, 2)
    account_data["anime"]["time_spent_day"] = round(user.time_spent_anime/1440, 2)

    def get_list_count(user_id, list_type):
        if list_type == ListType.SERIES:
            media_count = db.session.query(SeriesList, func.count(SeriesList.status)) \
                .filter_by(user_id=user_id).group_by(SeriesList.status).all()
        if list_type == ListType.ANIME:
            media_count = db.session.query(AnimeList, func.count(AnimeList.status)) \
                .filter_by(user_id=user_id).group_by(AnimeList.status).all()
        if list_type == ListType.MOVIES:
            media_count = db.session.query(MoviesList, func.count(MoviesList.status)) \
                .filter_by(user_id=user_id).group_by(MoviesList.status).all()

        watching, completed, completed_animation, onhold, random, dropped, plantowatch = [0 for _ in range(7)]
        for media in media_count:
            if media[0].status == Status.WATCHING:
                watching = media[1]
            elif media[0].status == Status.COMPLETED:
                completed = media[1]
            elif media[0].status == Status.COMPLETED_ANIMATION:
                completed_animation = media[1]
            elif media[0].status == Status.ON_HOLD:
                onhold = media[1]
            elif media[0].status == Status.RANDOM:
                random = media[1]
            elif media[0].status == Status.DROPPED:
                dropped = media[1]
            elif media[0].status == Status.PLAN_TO_WATCH:
                plantowatch = media[1]
        total = sum(tot[1] for tot in media_count)

        return {"watching": watching,
                "completed": completed,
                "completed_animation": completed_animation,
                "onhold": onhold,
                "random": random,
                "dropped": dropped,
                "plantowatch": plantowatch,
                "total": total - plantowatch}

    # Count media elements of each category
    series_count = get_list_count(user.id, ListType.SERIES)
    account_data["series"]["watching_count"] = series_count["watching"]
    account_data["series"]["completed_count"] = series_count["completed"]
    account_data["series"]["onhold_count"] = series_count["onhold"]
    account_data["series"]["random_count"] = series_count["random"]
    account_data["series"]["dropped_count"] = series_count["dropped"]
    account_data["series"]["plantowatch_count"] = series_count["plantowatch"]
    account_data["series"]["total_count"] = series_count["total"]

    anime_count = get_list_count(user.id, ListType.ANIME)
    account_data["anime"]["watching_count"] = anime_count["watching"]
    account_data["anime"]["completed_count"] = anime_count["completed"]
    account_data["anime"]["onhold_count"] = anime_count["onhold"]
    account_data["anime"]["random_count"] = anime_count["random"]
    account_data["anime"]["dropped_count"] = anime_count["dropped"]
    account_data["anime"]["plantowatch_count"] = anime_count["plantowatch"]
    account_data["anime"]["total_count"] = anime_count["total"]

    movies_count = get_list_count(user.id, ListType.MOVIES)
    account_data["movies"]["completed_count"] = movies_count["completed"]
    account_data["movies"]["completed_animation_count"] = movies_count["completed_animation"]
    account_data["movies"]["plantowatch_count"] = movies_count["plantowatch"]
    account_data["movies"]["total_count"] = movies_count["total"]

    # Count the total number of seen episodes for the series
    series_data = db.session.query(SeriesList, SeriesEpisodesPerSeason,
                                   func.group_concat(SeriesEpisodesPerSeason.episodes))\
        .join(SeriesEpisodesPerSeason, SeriesEpisodesPerSeason.series_id == SeriesList.series_id)\
        .filter(SeriesList.user_id == user.id).group_by(SeriesList.series_id).all()

    nb_eps_watched = 0
    for element in series_data:
        if element[0].status != Status.PLAN_TO_WATCH and element[0].status != Status.RANDOM:
            episodes = element[2].split(",")
            episodes = [int(x) for x in episodes]
            for i in range(1, element[0].current_season):
                nb_eps_watched += episodes[i-1]
            nb_eps_watched += element[0].last_episode_watched
    account_data["series"]["nb_ep_watched"] = nb_eps_watched

    # Count the total number of seen episodes for the anime
    anime_data = db.session.query(AnimeList, AnimeEpisodesPerSeason,
                                  func.group_concat(AnimeEpisodesPerSeason.episodes))\
        .join(AnimeEpisodesPerSeason, AnimeEpisodesPerSeason.anime_id == AnimeList.anime_id)\
        .filter(AnimeList.user_id == user.id).group_by(AnimeList.anime_id)

    nb_eps_watched = 0
    for element in anime_data:
        if element[0].status != Status.PLAN_TO_WATCH and element[0].status != Status.RANDOM:
            episodes = element[2].split(",")
            episodes = [int(x) for x in episodes]
            for i in range(1, element[0].current_season):
                nb_eps_watched += episodes[i-1]
            nb_eps_watched += element[0].last_episode_watched
    account_data["anime"]["nb_ep_watched"] = nb_eps_watched

    # Media percentages
    if account_data["series"]["nb_ep_watched"] == 0:
        account_data["series"]["element_percentage"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        account_data["series"]["element_percentage"] = [
            (float(account_data["series"]["watching_count"]/account_data["series"]["total_count"]))*100,
            (float(account_data["series"]["completed_count"]/account_data["series"]["total_count"]))*100,
            (float(account_data["series"]["onhold_count"]/account_data["series"]["total_count"]))*100,
            (float(account_data["series"]["random_count"]/account_data["series"]["total_count"]))*100,
            (float(account_data["series"]["dropped_count"]/account_data["series"]["total_count"]))*100,
            (float(account_data["series"]["plantowatch_count"]/account_data["series"]["total_count"]))*100]
    if account_data["anime"]["nb_ep_watched"] == 0:
        account_data["anime"]["element_percentage"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        account_data["anime"]["element_percentage"] = [
            (float(account_data["anime"]["watching_count"]/account_data["anime"]["total_count"]))*100,
            (float(account_data["anime"]["completed_count"]/account_data["anime"]["total_count"]))*100,
            (float(account_data["anime"]["onhold_count"]/account_data["anime"]["total_count"]))*100,
            (float(account_data["anime"]["random_count"]/account_data["anime"]["total_count"]))*100,
            (float(account_data["anime"]["dropped_count"]/account_data["anime"]["total_count"]))*100,
            (float(account_data["anime"]["plantowatch_count"]/account_data["anime"]["total_count"]))*100]
    if account_data["movies"]["total_count"] == 0:
        account_data["movies"]["element_percentage"] = [0.0, 0.0, 0.0]
    else:
        account_data["movies"]["element_percentage"] = [
            (float(account_data["movies"]["completed_count"]/account_data["movies"]["total_count"]))*100,
            (float(account_data["movies"]["completed_animation_count"]/account_data["movies"]["total_count"]))*100,
            (float(account_data["movies"]["plantowatch_count"]/account_data["movies"]["total_count"]))*100]

    # Grades and levels for each media
    series_level = get_level_and_grade(user.time_spent_series)
    account_data["series_level"] = series_level["level"]
    account_data["series_percent"] = series_level["level_percent"]
    account_data["series_grade_id"] = series_level["grade_id"]
    account_data["series_grade_title"] = series_level["grade_title"]

    anime_level = get_level_and_grade(user.time_spent_anime)
    account_data["anime_level"] = anime_level["level"]
    account_data["anime_percent"] = anime_level["level_percent"]
    account_data["anime_grade_id"] = anime_level["grade_id"]
    account_data["anime_grade_title"] = anime_level["grade_title"]

    movies_level = get_level_and_grade(user.time_spent_movies)
    account_data["movies_level"] = movies_level["level"]
    account_data["movies_percent"] = movies_level["level_percent"]
    account_data["movies_grade_id"] = movies_level["grade_id"]
    account_data["movies_grade_title"] = movies_level["grade_title"]

    knowledge_level = int(series_level["level"] + anime_level["level"] + movies_level["level"])
    knowledge_grade = get_knowledge_grade(knowledge_level)
    account_data["knowledge_level"] = knowledge_level
    account_data["knowledge_grade_id"] = knowledge_grade["grade_id"]
    account_data["knowledge_grade_title"] = knowledge_grade["grade_title"]

    return account_data


def get_follows_full_last_update(user):
    follows_update = user.followed_last_updates()

    tmp = ""
    follows_data = []
    for i in range(0, len(follows_update)):
        element = follows_update[i]
        if element[0].username != tmp:
            tmp = element[0].username
            follow_data = {"username": element[0].username,
                           "update": []}

        element_data = {}
        # Season or episode update
        if element[3].old_status is None and element[3].new_status is None:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element[3].old_season, element[3].old_episode),
                                      "S{:02d}.E{:02d}".format(element[3].new_season, element[3].new_episode)]

        # Category update
        elif element[3].old_status is not None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element[3].new_status.value).replace("Animation", "Anime")]

        # Media newly added
        elif element[3].old_status is None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].new_status.value)]

        element_data["date"] = element[3].date.replace(tzinfo=pytz.UTC).isoformat()
        element_data["media_name"] = element[3].media_name

        if element[3].media_type == ListType.SERIES:
            element_data["category"] = "series"
        elif element[3].media_type == ListType.ANIME:
            element_data["category"] = "anime"
        elif element[3].media_type == ListType.MOVIES:
            element_data["category"] = "movie"

        # TODO: TEMP FIX
        if len(follow_data["update"]) <= 5:
            follow_data["update"].append(element_data)

        try:
            if element[0].username != follows_update[i+1][0].username:
                follows_data.append(follow_data)
            else:
                pass
        except:
            follows_data.append(follow_data)

    return follows_data


def get_user_last_update(user_id):
    last_update = UserLastUpdate.query.filter_by(user_id=user_id).order_by(UserLastUpdate.date.desc()).limit(4)
    update = []
    for element in last_update:
        element_data = {}
        # Season or episode update
        if element.old_status is None and element.new_status is None:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element.old_season, element.old_episode),
                                      "S{:02d}.E{:02d}".format(element.new_season, element.new_episode)]

        # Category update
        elif element.old_status is not None and element.new_status is not None:
            element_data["update"] = ["{}".format(element.old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element.new_status.value).replace("Animation", "Anime")]

        # Newly added media
        elif element.old_status is None and element.new_status is not None:
            element_data["update"] = ["{}".format(element.new_status.value)]

        # Update date
        element_data["date"] = element.date.replace(tzinfo=pytz.UTC).isoformat()

        element_data["media_name"] = element.media_name

        if element.media_type == ListType.SERIES:
            element_data["category"] = "series"
        elif element.media_type == ListType.ANIME:
            element_data["category"] = "anime"
        elif element.media_type == ListType.MOVIES:
            element_data["category"] = "movie"

        update.append(element_data)

    return update


def get_follows_last_update(user):
    follows_update = user.followed_last_updates_overview()

    update = []
    for element in follows_update:
        element_data = {}
        # Season or episode update
        if element[3].old_status is None and element[3].new_status is None:
            element_data["update"] = ["S{:02d}.E{:02d}".format(element[3].old_season, element[3].old_episode),
                                      "S{:02d}.E{:02d}".format(element[3].new_season, element[3].new_episode)]

        # Category update
        elif element[3].old_status is not None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].old_status.value).replace("Animation", "Anime"),
                                      "{}".format(element[3].new_status.value).replace("Animation", "Anime")]

        # Newly added media
        elif element[3].old_status is None and element[3].new_status is not None:
            element_data["update"] = ["{}".format(element[3].new_status.value)]

        # Update date
        element_data["date"] = element[3].date.replace(tzinfo=pytz.UTC).isoformat()

        element_data["media_name"] = element[3].media_name

        if element[3].media_type == ListType.SERIES:
            element_data["category"] = "series"
        elif element[3].media_type == ListType.ANIME:
            element_data["category"] = "anime"
        elif element[3].media_type == ListType.MOVIES:
            element_data["category"] = "movie"

        element_data["username"] = element[0].username

        update.append(element_data)

    return update
