from pathlib import Path
from flask import url_for
from MyLists import app, mail
from flask_mail import Message


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    path = Path(app.root_path, "static/emails/password_reset.html")
    email_template = open(path).read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('auth.reset_password_token', token=token, _external=True))
    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] - Exception sending password reset email to account ID {}: {}'.format(user.id, e))
        return False


def send_register_email(user):
    token = user.get_register_token()
    msg = Message(subject='MyLists Register Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    path = Path(app.root_path, "static/emails/register.html")
    email_template = open(path).read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('auth.register_account_token', token=token, _external=True))
    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised when sending register email to account with the ID {} : {}'
                         .format(user.id, e))
        return False
