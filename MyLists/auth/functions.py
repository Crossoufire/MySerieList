import functools
from MyLists.models import HomePage
from flask_login import current_user
from flask import url_for, abort, redirect


def return_user_homepage(homepage, username):
    if homepage != HomePage.ACCOUNT and homepage != HomePage.HALL_OF_FAME:
        return redirect(url_for('main.mymedialist', media_list=homepage.value, user_name=username))
    elif homepage == HomePage.ACCOUNT:
        return redirect(url_for('users.account', user_name=username))
    elif homepage == HomePage.HALL_OF_FAME:
        return redirect(url_for('users.hall_of_fame'))
    else:
        abort(404)


def check_if_auth(func):
    @functools.wraps(func)
    def wrapper_auth(*args, **kwargs):
        if current_user.is_authenticated:
            return return_user_homepage(current_user.homepage, current_user.username)
        return func(*args, **kwargs)
    return wrapper_auth
