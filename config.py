import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'config.env'))

class Config(object):
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ['SQLALCHEMY_TRACK_MODIFICATIONS']
    SESSION_COOKIE_SECURE = os.environ['SESSION_COOKIE_SECURE']
    TESTING = os.environ['TESTING']
    # MAX_CONTENT_LENGTH = int(os.environ['MAX_CONTENT_LENGTH'])

    MAIL_SERVER = os.environ['MAIL_SERVER']
    MAIL_PORT = int(os.environ['MAIL_PORT'])
    MAIL_USE_TLS = os.environ['MAIL_USE_TLS']
    MAIL_USERNAME = os.environ['MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['MAIL_PASSWORD']
    MAIL_USE_SSL = os.environ['MAIL_USE_SSL']

    THEMOVIEDB_API_KEY = os.environ['THEMOVIEDB_API_KEY']
