import os
import platform
import secrets

from PIL import Image
from flask import url_for
from flask_mail import Message
from MyLists import current_app, mail


def send_email_update_email(user):
    token = user.get_email_update_token()
    msg = Message(subject='MyList Email Update Request',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[current_app.config['MAIL_USERNAME']],
                  reply_to=current_app.config['MAIL_USERNAME'])

    if platform.system() == "Windows":
        path = os.path.join(current_app.root_path, "static\\emails\\email_update.html")
    else:  # Linux & macOS
        path = os.path.join(current_app.root_path, "static/emails/email_update.html")

    email_template = open(path, 'r').read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('email_update_token', token=token, _external=True))
    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error('[SYSTEM] Exception raised sending email update email to account ID {}: {}'.format(user.id, e))
        return False


def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    try:
        i = Image.open(form_picture)
    except:
        return "default.jpg"
    i = i.resize((300, 300), Image.ANTIALIAS)
    i.save(picture_path, quality=90)

    return picture_fn
