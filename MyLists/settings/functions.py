import os
import imghdr
import secrets
import pandas as pd
from pathlib import Path
from MyLists import app, mail
from flask_mail import Message
from flask_login import current_user
from flask import url_for, flash, redirect
from MyLists.models import Series, SeriesList


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

    mail.send(msg)


def save_profile_picture(form_picture, old_picture, profile=True):
    if imghdr.what(form_picture) == 'gif' or imghdr.what(form_picture) == 'jpeg' \
            or imghdr.what(form_picture) == 'png':
        file = form_picture
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        if profile:
            file.save(os.path.join(app.root_path, 'static/profile_pics', picture_fn))
        else:
            file.save(os.path.join(app.root_path, 'static/background_pics', picture_fn))
    else:
        picture_fn = "default.jpg"
        app.logger.error('[SYSTEM] Invalid picture format: {}'.format(imghdr.what(form_picture)))

    try:
        if old_picture != 'default.jpg':
            if profile:
                os.remove(os.path.join(app.root_path, 'static/profile_pics', old_picture))
                app.logger.info('Settings updated: Removed the old picture: {}'.format(old_picture))
            else:
                os.remove(os.path.join(app.root_path, 'static/background_pics', old_picture))
                app.logger.info('Settings updated: Removed the old background: {}'.format(old_picture))
    except:
        pass

    return picture_fn


def import_the_list(form):
    try:
        data = pd.read_csv(form.csv_list.data, index_col='Type')
    except:
        flash('Impossible to recover the data from the CSV, please verify your file.', 'Warning')
        redirect(url_for('users.account', user_name=current_user.username))

    tv_data = data.loc['tv']
    all_TMDb_id = tv_data['TMDb ID']

    query = Series.query.filter(Series.themoviedb_id.in_(all_TMDb_id)).all()
    TV_id = [q.id for q in query]
    print(TV_id)
    in_list = SeriesList.query.filter(SeriesList.id.in_(TV_id), SeriesList.user_id == current_user.id).all()
    print(in_list)

