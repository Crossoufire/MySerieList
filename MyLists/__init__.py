import redis
import logging
import smtplib
from rq import Queue
from flask import Flask
import email.utils as em
from config import Config
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_compress import Compress
from flask_login import LoginManager
from email.message import EmailMessage
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import SMTPHandler, RotatingFileHandler


# Recover the Flask app name (in .flaskenv) and check the config from the .env file
app = Flask(__name__)
app.config.from_object(Config)


# Initialization of the different Flask modules
mail = Mail(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
compress = Compress(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.home'
login_manager.login_message_category = 'info'
app.url_map.strict_slashes = False


# Add the redis server and the queue
app.r = redis.Redis()
app.q = Queue(connection=app.r)


# Recover and register all the blueprints of the app
from MyLists.auth.routes import bp as auth_bp
app.register_blueprint(auth_bp)

from MyLists.errors.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from MyLists.general.routes import bp as general_bp
app.register_blueprint(general_bp)

from MyLists.main.routes import bp as main_bp
app.register_blueprint(main_bp)

from MyLists.users.routes import bp as users_bp
app.register_blueprint(users_bp)

from MyLists.settings.routes import bp as settings_bp
app.register_blueprint(settings_bp)


# Send an email to the admin if an error is logged and create the rotating file handler
if not app.debug and not app.testing:
    class SSL_SMTPHandler(SMTPHandler):
        def emit(self, record):
            """ Emit a record. """
            try:
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP_SSL(self.mailhost, port, timeout=self.timeout)
                msg = EmailMessage()
                msg['From'] = self.fromaddr
                msg['To'] = ','.join(self.toaddrs)
                msg['Subject'] = self.getSubject(record)
                msg['Date'] = em.localtime()
                msg.set_content(self.format(record))
                if self.username:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg, self.fromaddr, self.toaddrs)
                smtp.quit()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)

    mail_handler = SSL_SMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                   fromaddr=app.config['MAIL_USERNAME'],
                                   toaddrs=app.config['MAIL_USERNAME'],
                                   subject='MyLists - Exceptions occurred',
                                   credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))

    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    handler = RotatingFileHandler("MyLists/static/log/mylists.log", maxBytes=3000000, backupCount=15)
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s"))
    handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.info('MyLists startup')


# Import the admin view at the end to avoid loop import
from MyLists import admin_views


# Import the command
from MyLists.scheduled_tasks import register
register(app)
