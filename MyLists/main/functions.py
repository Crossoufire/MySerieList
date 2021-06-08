import os
import secrets
from PIL import Image
from flask import flash

from MyLists import db, app
from datetime import datetime
from flask_login import current_user
from MyLists.models import MediaType, ListType, Status, UserLastUpdate, User


def check_cat_type(list_type, status):
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        tv_status_dict = {'Watching': Status.WATCHING,
                          'Completed': Status.COMPLETED,
                          'On Hold': Status.ON_HOLD,
                          'Random': Status.RANDOM,
                          'Dropped': Status.DROPPED,
                          'Plan to Watch': Status.PLAN_TO_WATCH}
        try:
            return tv_status_dict[status]
        except KeyError:
            return None
    elif list_type == ListType.MOVIES:
        movie_status_dict = {'Completed': Status.COMPLETED,
                             'Plan to Watch': Status.PLAN_TO_WATCH}
        try:
            return movie_status_dict[status]
        except KeyError:
            return None
    elif list_type == ListType.GAMES:
        games_status_dict = {'Completed': Status.COMPLETED,
                             'Endless': Status.ENDLESS,
                             'Multiplayer': Status.MULTIPLAYER}
        try:
            return games_status_dict[status]
        except KeyError:
            return None


def compute_time_spent(media=None, list_type=None, old_watched=0, new_watched=0, movie_status=None, movie_delete=False,
                       movie_add=False, new_rewatch=0, old_rewatch=0, movie_duration=0, old_gametime=0, new_gametime=0,
                       user_id=None):

    # Use for the list import function (redis and rq backgound process), can't import the current_user context
    if current_user:
        user = current_user
    else:
        user = User.query.filter(User.id == user_id).first()

    if list_type == ListType.SERIES:
        old_time = user.time_spent_series
        user.time_spent_series = old_time + ((new_watched-old_watched) * media.duration) + (
                media.total_episodes * media.duration * (new_rewatch - old_rewatch))
    elif list_type == ListType.ANIME:
        old_time = user.time_spent_anime
        user.time_spent_anime = old_time + ((new_watched-old_watched)*media.duration) + (
                media.total_episodes*media.duration*(new_rewatch-old_rewatch))
    elif list_type == ListType.MOVIES:
        old_time = user.time_spent_movies
        if movie_delete:
            if movie_status == Status.COMPLETED:
                user.time_spent_movies = old_time - media.duration + media.duration*(new_rewatch-old_rewatch)
        elif movie_add:
            if movie_status == Status.COMPLETED:
                user.time_spent_movies = old_time + media.duration
        else:
            if movie_status == Status.COMPLETED:
                user.time_spent_movies = old_time + movie_duration + media.duration*(new_rewatch-old_rewatch)
            else:
                user.time_spent_movies = old_time - movie_duration + media.duration*(new_rewatch-old_rewatch)
    elif list_type == ListType.GAMES:
        old_time = current_user.time_spent_games
        current_user.time_spent_games = old_time + new_gametime - old_gametime
