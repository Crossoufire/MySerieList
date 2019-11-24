import configparser
import sys

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy


config = configparser.ConfigParser()
config.read('config.ini')
try:
    flask_secret = config['Flask']['secret']
    email = config['Mail']['email']
    password = config['Mail']['password']
    server = config['Mail']['server']
    port = int(config['Mail']['port'])
    captcha_public = config['Captcha']['public_key']
    captcha_private = config['Captcha']['private_key']
except:
    print("Config file error. Please read the README to configure the config.ini file properly. Exit.")
    sys.exit()


app = Flask(__name__)

app.config["SECRET_KEY"] = flask_secret

app.config["SESSION_COOKIE_SECURE"] = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['RECAPTCHA_PUBLIC_KEY'] = captcha_public
app.config['RECAPTCHA_PRIVATE_KEY'] = captcha_private
app.config['RECAPTCHA_DATA_ATTRS'] = {'theme': 'dark', 'size': 'small'}

app.config['TESTING'] = False

app.config['MAIL_SERVER'] = server
app.config['MAIL_PORT'] = port
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = email
app.config['MAIL_PASSWORD'] = password

app.config['MAX_CONTENT_LENGTH'] = 8*1024*1024


mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'
login_manager.login_message_category = 'info'


from MyLists import routes
import MyLists.errors
