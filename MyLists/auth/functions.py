import functools
from flask import url_for, redirect
from flask_login import current_user


def check_if_auth(func):
    @functools.wraps(func)
    def wrapper_auth(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('users.account', user_name=current_user.username))
        return func(*args, **kwargs)
    return wrapper_auth
