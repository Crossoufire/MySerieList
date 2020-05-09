import os
import imghdr
import secrets

from pathlib import Path
from flask import url_for
from MyLists import app, mail
from flask_mail import Message


def send_email_update_email(user):
    token = user.get_email_update_token()
    msg = Message(subject='MyList Email Update Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.transition_email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    path = Path(app.root_path, "static/emails/email_update.html")
    email_template = open(path).read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('email_update_token', token=token, _external=True))
    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised sending email update email to account ID {}: {}'.format(user.id, e))
        return False


def save_profile_picture(form_picture, old_picture):
    if imghdr.what(form_picture) == 'gif' or imghdr.what(form_picture) == 'jpeg' \
            or imghdr.what(form_picture) == 'png' or imghdr.what(form_picture) == 'jpg':
        file = form_picture
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        file.save(os.path.join(app.root_path, 'static/profile_pics', picture_fn))
    else:
        picture_fn = "default.jpg"
        app.logger.error('[SYSTEM] Invalid picture format: {}'.format(imghdr.what(form_picture)))

    # Remove old cover
    os.remove(os.path.join(app.root_path, 'static/profile_pics', old_picture))
    app.logger.info('Settings updated: Removed the old picture: {}'.format(old_picture))

    return picture_fn
