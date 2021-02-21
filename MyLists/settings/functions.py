import os
import imghdr
import secrets
import pandas as pd
from pathlib import Path
from MyLists import app, mail, db
from flask_mail import Message
from flask_login import current_user
from flask import url_for, flash, redirect

from MyLists.API_data import ApiData
from MyLists.main.add_db import AddtoDB
from MyLists.main.functions import set_last_update, compute_time_spent
from MyLists.main.media_object import MediaDetails
from MyLists.models import Movies, MoviesList, Status, ListType


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


def save_account_picture(form_picture, old_picture, profile=True):
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


def add_id_to_db(ids_to_add):
    new_ids = []
    for tmdb_id in ids_to_add:
        try:
            media_api_data = ApiData().get_details_and_credits_data(tmdb_id, ListType.MOVIES)
        except:
            pass
        try:
            media_details = MediaDetails(media_api_data, ListType.MOVIES).get_media_details()
        except:
            pass
        try:
            media = AddtoDB(media_details, ListType.MOVIES).add_media_to_db()
        except:
            pass
        try:
            new_ids.append(media.id)
        except:
            pass

    return new_ids


def add_id_to_user(ids_to_add):
    query = Movies.query.filter(Movies.id.in_(ids_to_add)).all()
    for media in query:
        user_list = MoviesList(user_id=current_user.id,
                               media_id=media.id,
                               status=Status.COMPLETED,
                               eps_watched=1)

        # Commit the changes
        db.session.add(user_list)

        app.logger.info('[User {}] {} Added [ID {}] in the category: {}'
                        .format(current_user.id, 'Movie', media.id, Status.COMPLETED.value))

        # Set the last update
        set_last_update(media=media, media_type=ListType.MOVIES, new_status=Status.COMPLETED)

        # Compute the new time spent
        compute_time_spent(media=media, list_type=ListType.MOVIES, movie_status=Status.COMPLETED, movie_add=True)

    db.session.commit()


def import_the_list(form):
    try:
        csv_data = pd.read_csv(form.csv_list.data, index_col='Type')
    except:
        flash('Impossible to recover the data from the CSV, please verify your file.', 'Warning')
        redirect(url_for('users.account', user_name=current_user.username))

    try:
        tv_data = csv_data.loc['tv']
        tv_TMDb_id = tv_data['TMDb ID']
    except:
        tv_data = None
        tv_TMDb_id = None

    try:
        movies_data = csv_data.loc['movie']
        movies_TMDb_id = movies_data['TMDb ID']
    except:
        movies_data = None
        movies_TMDb_id = None

    print(movies_data, movies_TMDb_id)

    if movies_data is not None and movies_TMDb_id is not None:
        query = Movies.query.filter(Movies.themoviedb_id.in_(movies_TMDb_id)).all()
        try:
            id_in_db = [q.id for q in query]
            tmdb_id_in_db = [q.themoviedb_id for q in query]
        except:
            id_in_db = []
            tmdb_id_in_db = []

        print(id_in_db, tmdb_id_in_db)
        id_not_in_db = list(set(movies_TMDb_id) - set(tmdb_id_in_db))
        print(id_not_in_db)

        query = MoviesList.query.filter(MoviesList.id.in_(id_in_db), MoviesList.user_id == current_user.id).all()
        try:
            id_in_list = [q.id for q in query]
        except:
            id_in_list = []
        id_not_in_list = list(set(id_in_db) - set(id_in_list))
        print(id_in_list, id_not_in_list)

        new_ids = add_id_to_db(id_not_in_db)
        add_id_to_user(new_ids + id_not_in_list)
