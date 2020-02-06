import sys
import logging
import smtplib
import email.utils
import configparser

from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask import Flask, current_app
from flask_login import LoginManager
from email.message import EmailMessage
from flask_sqlalchemy import SQLAlchemy
from flask_apscheduler import APScheduler
from logging.handlers import SMTPHandler, RotatingFileHandler


mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
scheduler = APScheduler()
login_manager = LoginManager()
login_manager.login_view = 'auth.home'
login_manager.login_message_category = 'info'


config = configparser.ConfigParser()
config.read('config.ini')
try:
    flask_secret = config['Flask']['secret']
    email = config['Mail']['email']
    password = config['Mail']['password']
    server = config['Mail']['server']
    port = int(config['Mail']['port'])
    themoviedb_key = config['TheMovieDB']['api_key']
except:
    print("Config file error. Please read the README to configure the config.ini file properly. Exit.")
    sys.exit()


def create_app():
    app = Flask(__name__)
    Compress(app)

    app.config["SECRET_KEY"] = flask_secret
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    app.config['MAX_CONTENT_LENGTH'] = 8*1024*1024

    app.config['MAIL_SERVER'] = server
    app.config['MAIL_PORT'] = port
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = email
    app.config['MAIL_PASSWORD'] = password
    app.config['THEMOVIEDB_API_KEY'] = themoviedb_key

    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    scheduler.init_app(app)
    scheduler.start()
    login_manager.init_app(app)

    from MyLists.admin.routes import bp as admin_bp
    app.register_blueprint(admin_bp)

    from MyLists.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from MyLists.errors.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from MyLists.general.routes import bp as general_bp
    app.register_blueprint(general_bp)

    from MyLists.main.routes import bp as main_bp
    app.register_blueprint(main_bp)

    from MyLists.profile.routes import bp as profile_bp
    app.register_blueprint(profile_bp)

    from MyLists.settings.routes import bp as settings_bp
    app.register_blueprint(settings_bp)

    if not app.debug and not app.testing:
        class SSLSMTPHandler(SMTPHandler):
            def emit(self, record):
                """ Emit a record. """
                try:
                    port = self.mailport
                    if not port:
                        port = smtplib.SMTP_PORT
                    smtp = smtplib.SMTP_SSL(self.mailhost, port)
                    msg = EmailMessage()
                    msg['From'] = self.fromaddr
                    msg['To'] = ','.join(self.toaddrs)
                    msg['Subject'] = self.getSubject(record)
                    msg['Date'] = email.utils.localtime()
                    msg.set_content(self.format(record))
                    if self.username:
                        smtp.login(self.username, self.password)
                    smtp.send_message(msg, self.fromaddr, self.toaddrs)
                    smtp.quit()
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    self.handleError(record)
        mail_handler = SSLSMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                      fromaddr=app.config['MAIL_USERNAME'],
                                      toaddrs=app.config['MAIL_USERNAME'],
                                      subject='Mylists - exceptions occurred!',
                                      credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

        handler = RotatingFileHandler("MyLists/static/log/mylists.log", maxBytes=10000000, backupCount=5)
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
        handler.setLevel(logging.INFO)
        app.logger.setLevel(logging.INFO)
        app.logger.addHandler(handler)
        app.logger.info('MyLists startup')

    return app

from MyLists import models
