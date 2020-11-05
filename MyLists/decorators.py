import functools
from flask_login import current_user
from MyLists.auth.functions import return_user_homepage


def check_if_auth(func):
    @functools.wraps(func)
    def wrapper_auth(*args, **kwargs):
        if current_user.is_authenticated:
            return return_user_homepage(current_user.homepage, current_user.username)
        return func(*args, **kwargs)
    return wrapper_auth
