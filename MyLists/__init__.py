import sys
import configparser

from flask import Flask
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler


config = configparser.ConfigParser()
config.read('config.ini')
try:
    flask_secret = config['Flask']['secret']
    admin_email = config['Mail']['admin_email']
    email = config['Mail']['email']
    password = config['Mail']['password']
    server = config['Mail']['server']
    port = int(config['Mail']['port'])
    themoviedb_api = config['TheMovieDB']['api_key']
except:
    print("Config file error. Please read the README to configure the config.ini file properly. Exit.")
    sys.exit()


app = Flask(__name__)
Compress(app)


app.config["SECRET_KEY"] = flask_secret
app.config["SESSION_COOKIE_SECURE"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True

app.config['MAIL_ADMIN'] = admin_email
app.config['MAIL_SERVER'] = server
app.config['MAIL_PORT'] = port
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = email
app.config['MAIL_PASSWORD'] = password
app.config['THEMOVIEDB_API_KEY'] = themoviedb_api

app.config['MAX_CONTENT_LENGTH'] = 8*1024*1024


mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()
login_manager = LoginManager(app)
login_manager.login_view = 'home'
login_manager.login_message_category = 'info'


from MyLists.account.routes import bp as account_bp
app.register_blueprint(account_bp)

from MyLists.admin.routes import bp as admin_bp
app.register_blueprint(admin_bp)

from MyLists.auth.routes import bp as auth_bp
app.register_blueprint(auth_bp)

from MyLists.errors.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from MyLists.main.routes import bp as main_bp
app.register_blueprint(main_bp)

from MyLists.medialists.routes import bp as medialists_bp
app.register_blueprint(medialists_bp)

from MyLists.settings.routes import bp as settings_bp
app.register_blueprint(settings_bp)
