import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'lets-go-guys'
    ENV = os.environ.get('FLASK_ENV')
    SESSION_COOKIE_SECURE = True  # bool(os.environ.get('FLASK_SESSION_COOKIE_SECURE'))
    SQLALCHEMY_DATABASE_URI = os.environ.get('FLASK_SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = bool(os.environ.get('FLASK_TESTING'))
    MAX_CONTENT_LENGTH = 8*1024*1024
    FLASK_ADMIN_SWATCH = 'cyborg'
    MAIL_SERVER = os.environ.get('FLASK_MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('FLASK_MAIL_PORT') or 25)
    MAIL_USE_TLS = False
    MAIL_USE_SSL = bool(os.environ.get('FLASK_MAIL_USE_SSL'))
    MAIL_USERNAME = os.environ.get('FLASK_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('FLASK_MAIL_PASSWORD')
    THEMOVIEDB_API_KEY = os.environ.get('FLASK_THEMOVIEDB_API_KEY')
    CLIENT_IGDB = os.environ.get('CLIENT_IGDB')
    SECRET_IGDB = os.environ.get('SECRET_IGDB')
    IGDB_API_KEY = os.environ.get('IGDB_API_KEY')


