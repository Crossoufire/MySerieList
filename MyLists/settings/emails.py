from pathlib import Path
from flask import url_for
from MyLists import app, mail
from flask_mail import Message


def send_email_update_email(user):
    token = user.get_token()
    msg = Message(subject='MyList - Email update request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.transition_email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    path = Path(app.root_path, "static/emails/email_update.html")
    email_template = open(path).read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('email_update_token', token=token, _external=True))
    msg.html = email_template

    mail.send(msg)
