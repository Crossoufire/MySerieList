import json
import os
import platform
import secrets
import sys
import urllib
import time
import requests
import numpy as np
import re

from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from MyLists import app, db, bcrypt, mail, config
from MyLists.admin_views import User
from MyLists.forms import RegistrationForm, LoginForm, UpdateAccountForm, ChangePasswordForm, AddFriendForm, \
    ResetPasswordForm, ResetPasswordRequestForm
from MyLists.models import Series, SeriesList, SeriesEpisodesPerSeason, Status, ListType, SeriesGenre, SeriesNetwork, \
    Friend, SeriesEpisodeTimestamp, Anime, AnimeList, AnimeEpisodesPerSeason, AnimeGenre, AnimeNetwork, \
    AnimeEpisodeTimestamp, HomePage, HallOfFame, BookStatus, Book, BookList, AnimeAchievements


config.read('config.ini')
try:
    themoviedb_api_key = config['TheMovieDB']['api_key']
    google_book_api_key = config['GoogleBook']['api_key']
except:
    print("Config file error. Please read the README to configure the config.ini file properly. Exit.")
    sys.exit()


@app.before_first_request
def create_user():
    db.create_all()
    if User.query.filter_by(id='1').first() is None:
        admin = User(username='admin',
                     email='admin@admin.com',
                     password=bcrypt.generate_password_hash("password").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(admin)

    if User.query.filter_by(id='2').first() is None:
        test = User(username='test',
                    email='test@test.com',
                    password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                    image_file='default.jpg',
                    active=True,
                    private=True,
                    registered_on=datetime.utcnow(),
                    activated_on=datetime.utcnow())
        db.session.add(test)

    if User.query.filter_by(id='3').first() is None:
        test2 = User(username='test2',
                     email='test2@test2.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test2)

    if User.query.filter_by(id='4').first() is None:
        test3 = User(username='test3',
                     email='test3@test3.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test3)

    if User.query.filter_by(id='5').first() is None:
        test4 = User(username='test4',
                     email='test4@test4.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test4)

    if User.query.filter_by(id='6').first() is None:
        test5 = User(username='aaaa',
                     email='test5@test5.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test5)

    if User.query.filter_by(id='7').first() is None:
        test6 = User(username='Sudoer',
                     email='test6@test6.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test6)

    if User.query.filter_by(id='8').first() is None:
        test7 = User(username='aaa',
                     email='test7@test7.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=True,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test7)

    if User.query.filter_by(id='9').first() is None:
        test8 = User(username='I_Love_Anime',
                     email='test8@test8.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test8)

    if User.query.filter_by(id='10').first() is None:
        test9 = User(username='0010100011',
                     email='test9@test9.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test9)

    if User.query.filter_by(id='11').first() is None:
        test10 = User(username='Crossoufire',
                     email='test10@test10.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test10)

    if User.query.filter_by(id='12').first() is None:
        test11 = User(username='WynroZ',
                     email='test11@test11.com',
                     password=bcrypt.generate_password_hash("azerty").decode('utf-8'),
                     image_file='default.jpg',
                     active=True,
                     private=False,
                     registered_on=datetime.utcnow(),
                     activated_on=datetime.utcnow())
        db.session.add(test11)
    db.session.commit()


################################################### Anonymous routes ###################################################


@app.route("/", methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.login_username.data).first()
        if user and not user.active:
            app.logger.info('[{}] Connexion attempt while account not activated'.format(user.id))
            flash('Your Account is not activated. Please check your e-mail address to activate your account.', 'danger')
        elif user and bcrypt.check_password_hash(user.password, login_form.login_password.data):
            login_user(user, remember=login_form.login_remember.data)
            next_page = request.args.get('next')
            app.logger.info('[{}] Logged in'.format(user.id))
            flash("You're now logged in. Welcome {0}".format(login_form.login_username.data), "success")
            home_page = str(user.home_page.value)
            return redirect(next_page) if next_page else redirect(url_for(home_page))
        else:
            flash('Login Failed. Please check Username and Password', 'warning')

    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.register_password.data).decode('utf-8')
        user = User(username=register_form.register_username.data,
                    email=register_form.register_email.data,
                    password=hashed_password,
                    active=False,
                    private=False,
                    registered_on=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        app.logger.info('[{}] New account registration : username = {}, email = {}'.format(user.id,
                                                                                           register_form.register_username.data,
                                                                                           register_form.register_email.data))
        if send_register_email(user):
            flash('Your account has been created. Check your e-mail address to activate your account!', 'info')
            return redirect(url_for('home'))
        else:
            app.logger.error('[SYSTEM] Error while sending the registration email to {}'.format(user.email))
            image_error = url_for('static', filename='img/error.jpg')
            return render_template('error.html', error_code=500, title='Error', image_error=image_error), 500

    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.get_id()).first()
        if user.home_page == HomePage.ACCOUNT:
            return redirect(url_for('account'))
        elif user.home_page == HomePage.HALL_OF_FAME:
            return redirect(url_for('hall_of_fame'))
        elif user.home_page == HomePage.MYSERIESLIST:
            return redirect(url_for('myserieslist'))
        elif user.home_page == HomePage.MYANIMESLIST:
            return redirect(url_for('myanimeslist'))

    else:
        home_header = url_for('static', filename='img/home_header.jpg')
        img1 = url_for('static', filename='img/home_img1.jpg')
        img2 = url_for('static', filename='img/home_img2.jpg')
        return render_template('home.html',
                               title='Home',
                               login_form=login_form,
                               register_form=register_form,
                               image_header=home_header,
                               img1=img1,
                               img2=img2)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('myserieslist'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if send_reset_email(user):
            app.logger.info('[{}] Reset password email sent'.format(user.id))
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('home'))
        else:
            app.logger.error('[SYSTEM] Error while sending the reset password email to {}'.format(user.email))
            flash("There was an error while sending the reset password email. Please try again later.")
            return redirect(url_for('home'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('myserieslist'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        app.logger.info('[{}] Password reset via reset password email'.format(user.id))
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route("/register_account/<token>", methods=['GET', 'POST'])
def register_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('myserieslist'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_password'))

    user.active = True
    user.activated_on = datetime.utcnow()
    db.session.commit()
    app.logger.info('[{}] Account activated'.format(user.id))
    flash('Your account has been activated.', 'success')
    return redirect(url_for('home'))


@app.route("/test")
def test():
    return render_template('test.html')


################################################# Authenticated routes #################################################


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    pass


@app.route("/logout")
@login_required
def logout():
    user = User.query.filter_by(id=current_user.get_id()).first()
    logout_user()
    app.logger.info('[{}] Logged out'.format(user.id))
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    add_friend_form = AddFriendForm()
    if add_friend_form.validate_on_submit():
        if str(add_friend_form.add_friend.data) == str(current_user.username):
            flash("You cannot add yourself.", 'info')
            return redirect(url_for('account'))
        add_friend(add_friend_form.add_friend.data)

    # Profile picture
    profile_picture = url_for('static', filename='profile_pics/{0}'.format(current_user.image_file))

    # Friends list
    friends_list = Friend.query.filter_by(user_id=current_user.get_id()).all()
    friends_list_data = []
    for friend in friends_list:
        friend_data = {}
        friend_username = User.query.filter_by(id=friend.friend_id).first().username
        friend_picture = User.query.filter_by(id=friend.friend_id).first().image_file
        friend_data["username"] = friend_username
        friend_data["user_id"] = friend.friend_id
        friend_data["status"] = friend.status
        friend_data["picture"] = friend_picture
        friends_list_data.append(friend_data)

    # Series Statistics, scores and level
    series_stats = get_all_account_stats(current_user.get_id(), ListType.SERIES)

    # Animes Statistics, scores, level, and achievements
    anime_stats = get_all_account_stats(current_user.get_id(), ListType.ANIME)
    anime_achievements = get_animes_achievements(current_user.get_id())

    # Books Statistics, scores, and level
    book_stats = get_all_account_stats(current_user.get_id(), ListType.BOOK)

    # Total level calculation + grade
    total_level = int(series_stats[3][0]) + int(anime_stats[3][0]) + int(book_stats[3][0])
    list_total_rank_element = []

    if platform.system() == "Windows":
        fp = open("{0}".format(os.path.join(app.root_path, "static\\img\\Original\\Ranks_unity.csv")), "r")
    else:  # Linux & macOS
        fp = open("{0}".format(os.path.join(app.root_path, "static/img/Original/Ranks_unity.csv")), "r")

    for line in fp:
        list_total_rank_element.append(line.split(";"))
    fp.close()

    total_rank_data = []
    for i in range(0, len(list_total_rank_element)):
        if str(list_total_rank_element[i][0]) == str(total_level):
            total_rank_data.append([str(list_total_rank_element[i][1]), str(list_total_rank_element[i][2])])

    if len(total_rank_data) == 0:
        total_rank_data.append(["Knowledge_Emperor_Grade_4", "Knowledge Emperor Grade 4"])

    user_id = current_user.get_id()
    user_name = current_user.username
    return render_template('account.html',
                           title='Account',
                           profile_picture=profile_picture,
                           friends_list_data=friends_list_data,
                           form=add_friend_form,
                           series_stats=series_stats,
                           anime_stats=anime_stats,
                           book_stats=book_stats,
                           total_rank_data=total_rank_data,
                           achievements=anime_achievements,
                           user_id=user_id,
                           user_name=user_name)


@app.route("/user/account/<user_name>")
@login_required
def user_account(user_name):
    add_friend_form = AddFriendForm()
    if add_friend_form.validate_on_submit():
        if str(add_friend_form.add_friend.data) == str(current_user.username):
            flash("You cannot add yourself.", 'info')
            return redirect(url_for('account'))
        add_friend(add_friend_form.add_friend.data)

    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404
    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('account'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()
    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))
    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    # Profile picture
    profile_picture = url_for('static', filename='profile_pics/{0}'.format(user.image_file))

    # Friends list
    friends_list = Friend.query.filter_by(user_id=user.id).all()
    friends_list_data = []
    for friend in friends_list:
        friend_data = {}
        friend_username = User.query.filter_by(id=friend.friend_id).first().username
        friend_picture = User.query.filter_by(id=friend.friend_id).first().image_file
        friend_data["username"] = friend_username
        friend_data["user_id"] = friend.friend_id
        friend_data["status"] = friend.status
        friend_data["picture"] = friend_picture
        friends_list_data.append(friend_data)

    # Series Statistics, scores and level
    series_stats = get_all_account_stats(user.id, ListType.SERIES)

    # Animes Statistics, scores, level, and achievements
    anime_stats = get_all_account_stats(user.id, ListType.ANIME)
    anime_achievements = get_animes_achievements(user.id)

    # Books Statistics, scores, and level
    book_stats = get_all_account_stats(user.id, ListType.BOOK)

    # Total level calculation + grade
    total_level = int(series_stats[3][0]) + int(anime_stats[3][0]) + int(book_stats[3][0])
    list_total_rank_element = []

    if platform.system() == "Windows":
        fp = open("{0}".format(os.path.join(app.root_path, "static\\img\\Original\\Ranks_unity.csv")), "r")
    else:  # Linux & macOS
        fp = open("{0}".format(os.path.join(app.root_path, "static/img/Original/Ranks_unity.csv")), "r")

    for line in fp:
        list_total_rank_element.append(line.split(";"))
    fp.close()

    total_rank_data = []
    for i in range(0, len(list_total_rank_element)):
        if str(list_total_rank_element[i][0]) == str(total_level):
            total_rank_data.append([str(list_total_rank_element[i][1]), str(list_total_rank_element[i][2])])

    if len(total_rank_data) == 0:
        total_rank_data.append(["Knowledge_Emperor_Grade_4", "Knowledge Emperor Grade 4"])

    user_id = user.id
    user_name = user.username
    return render_template('account.html',
                           title='Account',
                           profile_picture=profile_picture,
                           form=add_friend_form,
                           friends_list_data=friends_list_data,
                           series_stats=series_stats,
                           anime_stats=anime_stats,
                           book_stats=book_stats,
                           total_rank_data=total_rank_data,
                           achievements=anime_achievements,
                           user_id=user_id,
                           user_name=user_name)


@app.route("/anime_achievements")
@login_required
def anime_achievements():
    return render_template('anime_achievements.html', title='Anime achievements')


@app.route("/level_grade_data")
@login_required
def level_grade_data():
    return render_template('level_grade_data.html', title='Level Grade Data')


@app.route("/knowledge_grade_data")
@login_required
def knowledge_grade_data():
    return render_template('knowledge_grade_data.html', title='Knowledge Grade Data')


@app.route("/account_settings", methods=['GET', 'POST'])
@login_required
def account_settings():
    form = UpdateAccountForm()

    user = User.query.filter_by(id=current_user.get_id()).first()
    is_private = user.private
    if is_private:
        is_private = "checked"
    else:
        is_private = "unchecked"

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_profile_picture(form.picture.data)
            old_picture_file = user.image_file
            user.image_file = picture_file
            db.session.commit()
            app.logger.info(
                '[{}] Settings updated : old picture file = {}, new picture file = {}'.format(user.id, old_picture_file,
                                                                                              user.image_file))
        if form.username.data != user.username:
            old_username = user.username
            user.username = form.username.data
            db.session.commit()
            app.logger.info('[{}] Settings updated : old username = {}, new username = {}'.format(user.id, old_username,
                                                                                                  user.username))
        email_changed = False
        if form.email.data != user.email:
            old_email = user.email
            user.transition_email = form.email.data
            db.session.commit()
            app.logger.info('[{}] Settings updated : old email = {}, new email = {}'.format(user.id, old_email,
                                                                                            user.transition_email))
            email_changed = True
            if send_email_update_email(user):
                success = True
            else:
                success = False
                app.logger.error('[SYSTEM] Error while sending the email update email to {}'.format(user.email))

        if not email_changed:
            flash("Your account has been updated ! ", 'success')
        else:
            if success:
                flash("Your account has been updated ! Please click on the link to validate your new email address.",
                      'success')
            else:
                flash("There was an error internal error. Please contact the administrator.", 'danger')

        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/{0}'.format(current_user.image_file))
    return render_template('account_settings.html',
                           title='Settings',
                           image_file=image_file,
                           form=form,
                           value_privacy=is_private,
                           home_page=str(user.home_page.value),
                           default_hof=str(user.default_hof.value))


@app.route("/default_page", methods=['POST'])
@login_required
def default_page():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        home_page = int(json_data['home_page'])
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    user = User.query.filter_by(id=current_user.get_id()).first()

    if home_page == 0:
        user.home_page = HomePage.ACCOUNT
    elif home_page == 1:
        user.home_page = HomePage.HALL_OF_FAME
    elif home_page == 2:
        user.home_page = HomePage.MYSERIESLIST
    elif home_page == 3:
        user.home_page = HomePage.MYANIMESLIST
    elif home_page == 4:
        user.home_page = HomePage.MYBOOKSLIST
    else:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    db.session.commit()
    return '', 204


@app.route('/private_mode', methods=['POST'])
@login_required
def private_mode():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        triggered = json_data['private']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    user = User.query.filter_by(id=current_user.get_id()).first()
    if triggered == "off":
        user.private = False
    elif triggered == "on":
        user.private = True
    else:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    db.session.commit()
    app.logger.info('[{}] Private mode updated to {}'.format(user.id, triggered))
    return '', 204


@app.route("/email_update/<token>", methods=['GET'])
@login_required
def email_update_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))

    if str(user.id) != current_user.get_id():
        return redirect(url_for('myserieslist'))

    old_email = user.email
    user.email = user.transition_email
    user.transition_email = None
    db.session.commit()
    app.logger.info('[{}] Email successfully changed from {} to {}'.format(user.id, old_email, user.email))
    flash('Email successfully updated !', 'success')
    return redirect(url_for('myserieslist'))


@app.route('/change_pass', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.get_id()).first()
        if user and bcrypt.check_password_hash(user.password, form.actual_password.data):
            hashed_password = bcrypt.generate_password_hash(form.confirm_new_password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            app.logger.info('[{}] Password updated'.format(user.id))
            flash('Your password has been successfully updated!', 'success')
            return redirect(url_for('account'))
        else:
            flash('Current password incorrect', 'danger')
    return render_template('change_pass.html', form=form)


@app.route("/friend_request", methods=['POST'])
@login_required
def friend_request():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        friend_id = json_data['response']
        value = json_data['request']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        friend_id = int(friend_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    if value == "accept":
        # Check if there is an actual pending request
        user = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id, status="pending").first()
        if user is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
        user.status = 'accepted'
        db.session.commit()

        user2 = Friend.query.filter_by(user_id=friend_id, friend_id=current_user.get_id(), status="request").first()
        if user2 is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
        user2.status = 'accepted'
        db.session.commit()
        app.logger.info('[{}] Friend request accepted from user with ID {}'.format(current_user.get_id(), friend_id))
    elif value == "decline":
        # Check if there is an actual pending request
        # Otherwise delete the pending request
        if not Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id, status="pending").delete():
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
        db.session.commit()

        if not Friend.query.filter_by(user_id=friend_id, friend_id=current_user.get_id(), status="request").delete():
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
        db.session.commit()
        app.logger.info('[{}] Friend request declined from user with ID {}'.format(current_user.get_id(), friend_id))
    else:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    return '', 204


@app.route('/delete_friend', methods=['POST'])
@login_required
def delete_friend():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        friend_id = json_data['delete']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        friend_id = int(friend_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the friend to delete is in the friend list
    if Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id).delete()
    Friend.query.filter_by(user_id=friend_id, friend_id=current_user.get_id()).delete()
    db.session.commit()
    app.logger.info('[{}] Friend with ID {} deleted'.format(current_user.get_id(), friend_id))
    return '', 204


@app.route("/hall_of_fame")
@login_required
def hall_of_fame():
    # Get list of all users except admin
    users = User.query.filter(User.id >= "2").order_by(User.username.asc()).all()

    current_user_friends = Friend.query.filter_by(user_id=current_user.get_id(), status="accepted").all()
    friends_list = []
    for friend in current_user_friends:
        friends_list.append(friend.friend_id)

    current_user_pending_friends = Friend.query.filter_by(user_id=current_user.get_id(), status="request").all()
    friends_pending_list = []
    for friend in current_user_pending_friends:
        friends_pending_list.append(friend.friend_id)

    # hall of fame
    all_user_data = []
    for user in users:
        ranks_and_levels_series = get_all_account_stats(user.id, ListType.SERIES)
        ranks_and_levels_animes = get_all_account_stats(user.id, ListType.ANIME)
        ranks_and_levels_books = get_all_account_stats(user.id, ListType.BOOK)

        total_level = int(ranks_and_levels_series[3][0]) + int(ranks_and_levels_animes[3][0]) + int(ranks_and_levels_books[3][0])
        list_total_rank = []
        if platform.system() == "Windows":
            fp = open("{0}".format(os.path.join(app.root_path, "static\\img\\Original\\Ranks_unity.csv")), "r")
        else:  # Linux & macOS
            fp = open("{0}".format(os.path.join(app.root_path, "static/img/Original/Ranks_unity.csv")), "r")

        for line in fp:
            list_total_rank.append(line.split(";"))
        fp.close()

        total_rank_data = []
        for i in range(0, len(list_total_rank)):
            if str(list_total_rank[i][0]) == str(total_level):
                total_rank_data.append([str(list_total_rank[i][1]), str(list_total_rank[i][2])])

        if len(total_rank_data) == 0:
            total_rank_data.append(["Knowledge_Emperor_Grade_4", "Knowledge Emperor Grade 4"])

        # profile picture
        profile_picture = url_for('static', filename='profile_pics/{0}'.format(user.image_file))

        user_data = {"profile_picture": profile_picture,
                     "username": user.username,
                     "series": ranks_and_levels_series,
                     "animes": ranks_and_levels_animes,
                     "books": ranks_and_levels_books,
                     "total": [total_level, total_rank_data]}

        if user.id in friends_list:
            user_data["isfriend"] = True
            user_data["ispendingfriend"] = False
        else:
            if user.id in friends_pending_list:
                user_data["ispendingfriend"] = True
            else:
                user_data["ispendingfriend"] = False
            user_data["isfriend"] = False

        if str(user.id) == current_user.get_id():
            user_data["isprivate"] = False
            user_data["iscurrentuser"] = True
        else:
            user_data["isprivate"] = user.private
            user_data["iscurrentuser"] = False

        all_user_data.append(user_data)

    return render_template("hall_of_fame.html",
                           title='Hall of Fame',
                           all_data=all_user_data)


@app.route("/add_friend_hof", methods=['POST'])
@login_required
def add_friend_hof():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        user_name = json_data['user_name']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    add_friend(user_name)
    return '', 204


@app.route("/anonymous")
@login_required
def anonymous():
    image_anonymous = url_for('static', filename='img/anonymous.jpg')
    return render_template("anonymous.html", title="Anonymous", image_anonymous=image_anonymous)


##################################################### Anime/Serie routes ###############################################


@app.route("/myanimeslist", methods=['GET', 'POST'])
@login_required
def myanimeslist():
    watching_list     = AnimeList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').all()
    completed_list    = AnimeList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list       = AnimeList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    random_list       = AnimeList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').all()
    dropped_list      = AnimeList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantowatch_list  = AnimeList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').all()

    animes_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    animes_data = get_list_data(animes_list, ListType.ANIME)
    element_type = "ANIME"
    user_id = current_user.get_id()
    return render_template('mymedialist.html',
                           title='MyAnimeList',
                           all_data=animes_data,
                           element_type=element_type,
                           user_id=user_id)


@app.route("/myserieslist", methods=['GET', 'POST'])
@login_required
def myserieslist():
    watching_list     = SeriesList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').all()
    completed_list    = SeriesList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list       = SeriesList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    random_list       = SeriesList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').all()
    dropped_list      = SeriesList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantowatch_list  = SeriesList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').all()

    series_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    series_data = get_list_data(series_list, ListType.SERIES)
    element_type = "SERIES"
    user_id = current_user.get_id()
    return render_template('mymedialist.html',
                           title='MySeriesList',
                           all_data=series_data,
                           element_type=element_type,
                           user_id=user_id)


@app.route("/myanimeslist_table", methods=['GET', 'POST'])
@login_required
def myanimeslist_table():
    watching_list    = AnimeList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').all()
    completed_list   = AnimeList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list      = AnimeList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    random_list      = AnimeList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').all()
    dropped_list     = AnimeList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantowatch_list = AnimeList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').all()

    animes_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    animes_data = get_list_data(animes_list, ListType.ANIME)
    element_type = "ANIME"
    user_id = current_user.get_id()
    return render_template('mymedialist_table.html',
                           title='MyAnimeList',
                           all_data=animes_data,
                           element_type=element_type,
                           user_id=user_id)


@app.route("/myserieslist_table", methods=['GET', 'POST'])
@login_required
def myserieslist_table():
    watching_list    = SeriesList.query.filter_by(user_id=current_user.get_id(), status='WATCHING').all()
    completed_list   = SeriesList.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list      = SeriesList.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    random_list      = SeriesList.query.filter_by(user_id=current_user.get_id(), status='RANDOM').all()
    dropped_list     = SeriesList.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantowatch_list = SeriesList.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').all()

    series_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    series_data = get_list_data(series_list, ListType.SERIES)
    element_type = "SERIES"
    user_id = current_user.get_id()
    return render_template('mymedialist_table.html',
                           title='MySeriesList',
                           all_data=series_data,
                           element_type=element_type,
                           user_id=user_id)


@app.route('/update_element_season', methods=['POST'])
@login_required
def update_element_season():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        season = json_data['season']
        element_id = json_data['element_id']
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        season = int(season)
        element_id = int(element_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element exists
    if element_type == "ANIME":
        if Anime.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if Series.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element is in the current user's list
    if element_type == "ANIME":
        if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the season number is between 1 and <last_season>
    if element_type == "ANIME":
        last_season = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id).order_by(
            AnimeEpisodesPerSeason.season.desc()).first().season
        if season + 1 < 1 or season + 1 > last_season:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

        update = AnimeList.query.filter_by(anime_id=element_id, user_id=current_user.get_id()).first()
        old_season = update.current_season

        if old_season < season + 1:
            for i in range(old_season, season + 1):
                for j in range(1, AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id,
                                                                         season=i).first().episodes + 1):
                    if AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                             anime_id=element_id,
                                                             season=i,
                                                             episode=j).first() is None:
                        ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                                   anime_id=element_id,
                                                   season=i,
                                                   episode=j,
                                                   timestamp=datetime.utcnow())
                        db.session.add(ep)
            ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                       anime_id=element_id,
                                       season=season + 1,
                                       episode=1,
                                       timestamp=datetime.utcnow())
            db.session.add(ep)
            db.session.commit()

        elif old_season > season + 1:
            for i in range(season + 1, old_season + 1):
                AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                      anime_id=element_id,
                                                      season=i).delete()
            ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                       anime_id=element_id,
                                       season=season + 1,
                                       episode=1,
                                       timestamp=datetime.utcnow())
            db.session.add(ep)
            db.session.commit()

        update.current_season = season + 1
        update.last_episode_watched = 1
        db.session.commit()
        app.logger.info('[{}] Season of the anime with ID {} updated to {}'.format(current_user.get_id(), element_id, season + 1))
    elif element_type == "SERIES":
        last_season = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id).order_by(
            SeriesEpisodesPerSeason.season.desc()).first().season
        if season + 1 < 1 or season + 1 > last_season:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

        update = SeriesList.query.filter_by(series_id=element_id, user_id=current_user.get_id()).first()
        old_season = update.current_season

        if old_season < season + 1:
            for i in range(old_season, season + 1):
                for j in range(1, SeriesEpisodesPerSeason.query.filter_by(series_id=element_id,
                                                                          season=i).first().episodes + 1):
                    if SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                              series_id=element_id,
                                                              season=i,
                                                              episode=j).first() is None:
                        ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                                    series_id=element_id,
                                                    season=i,
                                                    episode=j,
                                                    timestamp=datetime.utcnow())
                        db.session.add(ep)
            ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                        series_id=element_id,
                                        season=season + 1,
                                        episode=1,
                                        timestamp=datetime.utcnow())
            db.session.add(ep)
            db.session.commit()

        elif old_season > season + 1:
            for i in range(season + 1, old_season + 1):
                SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                       series_id=element_id,
                                                       season=i).delete()
            ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                        series_id=element_id,
                                        season=season + 1,
                                        episode=1,
                                        timestamp=datetime.utcnow())
            db.session.add(ep)
            db.session.commit()

        update.current_season = season + 1
        update.last_episode_watched = 1
        db.session.commit()
        app.logger.info('[{}] Season of the series with ID {} updated to {}'.format(current_user.get_id(), element_id, season + 1))

    return '', 204


@app.route('/update_element_episode', methods=['POST'])
@login_required
def update_element_episode():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        episode = json_data['episode']
        element_id = json_data['element_id']
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        episode = int(episode)
        element_id = int(element_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element exists
    if element_type == "ANIME":
        if Anime.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if Series.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element is in the current user's list
    if element_type == "ANIME":
        if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the episode number is between 1 and <last_episode>
    if element_type == "ANIME":
        current_season = AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).first().current_season
        last_episode = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id, season=current_season).first().episodes
        if episode + 1 < 1 or episode + 1 > last_episode:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

        update = AnimeList.query.filter_by(anime_id=element_id, user_id=current_user.get_id()).first()
        old_last_episode_watched = update.last_episode_watched
        current_season = update.current_season

        if episode + 1 > old_last_episode_watched:
            for i in range(old_last_episode_watched + 1, episode + 2):
                ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                           anime_id=element_id,
                                           season=current_season,
                                           episode=i,
                                           timestamp=datetime.utcnow())
                db.session.add(ep)
            db.session.commit()
        elif episode + 1 < old_last_episode_watched:
            for i in range(episode + 2, old_last_episode_watched + 1):
                AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                      anime_id=element_id,
                                                      season=current_season,
                                                      episode=i).delete()
            db.session.commit()

        update.last_episode_watched = episode + 1
        db.session.commit()
        app.logger.info('[{}] Episode of the anime with ID {} updated to {}'.format(current_user.get_id(), element_id, episode + 1))
    elif element_type == "SERIES":
        current_season = SeriesList.query.filter_by(user_id=current_user.get_id(),
                                                    series_id=element_id).first().current_season
        last_episode = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id, season=current_season).first().episodes
        if episode + 1 < 1 or episode + 1 > last_episode:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

        update = SeriesList.query.filter_by(series_id=element_id, user_id=current_user.get_id()).first()
        old_last_episode_watched = update.last_episode_watched
        current_season = update.current_season

        if episode + 1 > old_last_episode_watched:
            for i in range(old_last_episode_watched + 1, episode + 2):
                ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                            series_id=element_id,
                                            season=current_season,
                                            episode=i,
                                            timestamp=datetime.utcnow())
                db.session.add(ep)
            db.session.commit()
        elif episode + 1 < old_last_episode_watched:
            for i in range(episode + 2, old_last_episode_watched + 1):
                SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                       series_id=element_id,
                                                       season=current_season,
                                                       episode=i).delete()
            db.session.commit()

        update.last_episode_watched = episode + 1
        db.session.commit()
        app.logger.info('[{}] Episode of the series with ID {} updated to {}'.format(current_user.get_id(), element_id, episode + 1))

    return '', 204


@app.route('/delete_element', methods=['POST'])
@login_required
def delete_element():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        element_id = json_data['delete']
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        element_id = int(element_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element exists
    if element_type == "ANIME":
        if Anime.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if Series.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element is in the current user's list
    if element_type == "ANIME":
        if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    if element_type == "ANIME":
        AnimeList.query.filter_by(anime_id=element_id, user_id=current_user.get_id()).delete()
        db.session.commit()
        AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).delete()
        db.session.commit()
        app.logger.info('[{}] Anime with ID {} deleted'.format(current_user.get_id(), element_id))
    elif element_type == "SERIES":
        SeriesList.query.filter_by(series_id=element_id, user_id=current_user.get_id()).delete()
        db.session.commit()
        SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(), series_id=element_id).delete()
        db.session.commit()
        app.logger.info('[{}] Series with ID {} deleted'.format(current_user.get_id(), element_id))

    return '', 204


@app.route('/change_element_category', methods=['POST'])
@login_required
def change_element_category():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        element_new_category = json_data['status']
        element_id = json_data['element_id']
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    category_list = ["Watching", "Completed", "On Hold", "Random", "Dropped", "Plan to Watch"]
    if element_new_category not in category_list:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        element_id = int(element_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    if element_type == "ANIME":
        element = AnimeList.query.filter_by(anime_id=element_id, user_id=current_user.get_id()).first()
    elif element_type == "SERIES":
        element = SeriesList.query.filter_by(series_id=element_id, user_id=current_user.get_id()).first()

    if element_new_category == 'Watching':
        element.status = 'WATCHING'
    elif element_new_category == 'Completed':
        element.status = 'COMPLETED'
        # Set Season / Episode to max
        if element_type == "ANIME":
            number_season = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id).count()
            for i in range(number_season):
                number_episode = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id, season=i+1).first().episodes
                for j in range(number_episode):
                    if AnimeEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                             anime_id=element_id,
                                                             season=i+1,
                                                             episode=j+1).first() is None:
                        ep = AnimeEpisodeTimestamp(user_id=current_user.get_id(),
                                                    anime_id=element_id,
                                                    season=i+1,
                                                    episode=j+1,
                                                    timestamp=datetime.utcnow())
                        db.session.add(ep)
            element.current_season = number_season
            element.last_episode_watched = number_episode
            db.session.commit()
        elif element_type == "SERIES":
            number_season = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id).count()
            for i in range(number_season):
                number_episode = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id, season=i+1).first().episodes
                for j in range(number_episode):
                    if SeriesEpisodeTimestamp.query.filter_by(user_id=current_user.get_id(),
                                                              series_id=element_id,
                                                              season=i+1,
                                                              episode=j+1).first() is None:
                        ep = SeriesEpisodeTimestamp(user_id=current_user.get_id(),
                                                    series_id=element_id,
                                                    season=i+1,
                                                    episode=j+1,
                                                    timestamp=datetime.utcnow())
                        db.session.add(ep)
            element.current_season = number_season
            element.last_episode_watched = number_episode
            db.session.commit()
    elif element_new_category == 'On Hold':
        element.status = 'ON_HOLD'
    elif element_new_category == 'Random':
        element.status = 'RANDOM'
    elif element_new_category == 'Dropped':
        element.status = 'DROPPED'
    elif element_new_category == 'Plan to Watch':
        element.status = 'PLAN_TO_WATCH'
    db.session.commit()
    app.logger.info('[{}] Category of the element with ID {} changed to {}'.format(current_user.get_id(),
                                                                                   element_id,
                                                                                   element_new_category))
    return '', 204


@app.route('/refresh_single_element', methods=['POST'])
@login_required
def refresh_single_element():
    image_error = url_for('static', filename='img/error.jpg')

    try:
        json_data = request.get_json()
        element_id = json_data['element_id']
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        element_id = int(element_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element is currently in the user's list
    if element_type == "ANIME":
        if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if there is more than 30 min since the last update
    if element_type == "ANIME":
        last_update = Anime.query.filter_by(id=element_id).first().last_update
        time_delta = datetime.utcnow() - last_update
        if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
            refresh_element_data(element_id, ListType.ANIME)
    elif element_type == "SERIES":
        last_update = Series.query.filter_by(id=element_id).first().last_update
        time_delta = datetime.utcnow() - last_update
        if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
            refresh_element_data(element_id, ListType.SERIES)

    return '', 204


@app.route('/refresh_all_element', methods=['POST'])
@login_required
def refresh_all_element():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    if element_type == "ANIME":
        animes = AnimeList.query.filter_by(user_id=current_user.get_id()).all()
        for anime in animes:
            # Check if there is more than 30 min since the last update
            last_update = Anime.query.filter_by(id=anime.anime_id).first().last_update
            time_delta = datetime.utcnow() - last_update
            if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
                refresh_element_data(anime.anime_id, ListType.ANIME)
            else:
                pass
    elif element_type == "SERIES":
        series = SeriesList.query.filter_by(user_id=current_user.get_id()).all()
        for serie in series:
            # Check if there is more than 30 min since the last update
            last_update = Series.query.filter_by(id=series.series_id).first().last_update
            time_delta = datetime.utcnow() - last_update
            if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
                refresh_element_data(series.series_id, ListType.SERIES)
            else:
                pass

    return '', 204


@app.route("/user/animes/grid/<user_name>")
@login_required
def user_animes_grid(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404
    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('myanimeslist'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()
    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))
    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    watching_list     = AnimeList.query.filter_by(user_id=user.id, status='WATCHING').all()
    completed_list    = AnimeList.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list       = AnimeList.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    random_list       = AnimeList.query.filter_by(user_id=user.id, status='RANDOM').all()
    dropped_list      = AnimeList.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantowatch_list  = AnimeList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').all()

    animes_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    animes_data = get_list_data(animes_list, ListType.ANIME)
    user_id = user.id
    user_name = user.username
    element_type = "ANIME"
    return render_template('mymedialist.html',
                           title='{}\'s list'.format(user.username),
                           all_data=animes_data,
                           user_id=user_id,
                           user_name=user_name,
                           element_type=element_type)


@app.route("/user/series/grid/<user_name>")
@login_required
def user_series_grid(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404
    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('myserieslist'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()
    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))
    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    watching_list     = SeriesList.query.filter_by(user_id=user.id, status='WATCHING').all()
    completed_list    = SeriesList.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list       = SeriesList.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    random_list       = SeriesList.query.filter_by(user_id=user.id, status='RANDOM').all()
    dropped_list      = SeriesList.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantowatch_list  = SeriesList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').all()

    series_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    series_data = get_list_data(series_list, ListType.SERIES)
    user_id = user.id
    user_name = user.username
    element_type = "SERIES"
    return render_template('mymedialist.html',
                           title='{}\'s list'.format(user.username),
                           all_data=series_data,
                           user_id=user_id,
                           user_name=user_name,
                           element_type=element_type)


@app.route("/user/animes/table/<user_name>")
@login_required
def user_animes_table(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404
    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('myanimeslist_table'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()
    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))
    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    watching_list     = AnimeList.query.filter_by(user_id=user.id, status='WATCHING').all()
    completed_list    = AnimeList.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list       = AnimeList.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    random_list       = AnimeList.query.filter_by(user_id=user.id, status='RANDOM').all()
    dropped_list      = AnimeList.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantowatch_list  = AnimeList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').all()

    animes_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    animes_data = get_list_data(animes_list, ListType.ANIME)
    user_id = user.id
    user_name = user.username
    element_type = "ANIME"
    return render_template('mymedialist_table.html',
                           title='{}\'s list'.format(user.username),
                           all_data=animes_data,
                           user_id=user_id,
                           user_name=user_name,
                           element_type=element_type)


@app.route("/user/series/table/<user_name>")
@login_required
def user_series_table(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404
    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('myserieslist_table'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()
    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))
    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    watching_list     = SeriesList.query.filter_by(user_id=user.id, status='WATCHING').all()
    completed_list    = SeriesList.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list       = SeriesList.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    random_list       = SeriesList.query.filter_by(user_id=user.id, status='RANDOM').all()
    dropped_list      = SeriesList.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantowatch_list  = SeriesList.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').all()

    series_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    series_data = get_list_data(series_list, ListType.SERIES)
    user_id = user.id
    user_name = user.username
    element_type = "SERIES"
    return render_template('mymedialist_table.html',
                           title='{}\'s list'.format(user.username),
                           all_data=series_data,
                           user_id=user_id,
                           user_name=user_name,
                           element_type=element_type)


@app.route('/add_element', methods=['POST'])
@login_required
def add_element():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        element_id = json_data['element_id']
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    if element_type == "ANIME":
        add_element(element_id, ListType.ANIME)
    elif element_type == "SERIES":
        add_element(element_id, ListType.SERIES)

    return '', 204


@app.route('/add_score_element', methods=['POST'])
@login_required
def add_score_element():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        score_value = json_data['score_val']
        element_id = json_data['element_id']
        element_type = json_data['element_type']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        score_value = float(score_value)
        element_id = int(element_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element exists
    if element_type == "ANIME":
        if Anime.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if Series.query.filter_by(id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the element is in the current user's list
    if element_type == "ANIME":
        if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    elif element_type == "SERIES":
        if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element_id).first() is None:
            return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the score is between 0 and 10:
    if score_value > 10 or score_value < 0:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    if element_type == "ANIME":
        add_score = AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element_id).first()
        add_score.score = score_value
        db.session.commit()
        app.logger.info('[{}] Anime with ID {} scored {}'.format(current_user.get_id(), element_id, score_value))
    elif element_type == "SERIES":
        add_score = SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element_id).first()
        add_score.score = score_value
        db.session.commit()
        app.logger.info('[{}] Series with ID {} scored {}'.format(current_user.get_id(), element_id, score_value))

    return '', 204


@app.route('/autocomplete_animes', methods=['GET'])
@login_required
def autocomplete_animes():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])

    results = autocomplete_search_element(search, ListType.ANIME)
    return jsonify(matching_results=results)


@app.route('/autocomplete_series', methods=['GET'])
@login_required
def autocomplete_series():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])

    results = autocomplete_search_element(search, ListType.SERIES)
    return jsonify(matching_results=results)


###################################################### Books Routes ####################################################


@app.route("/mybookslist", methods=['GET', 'POST'])
@login_required
def mybookslist():
    reading_list    = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.READING).all()
    completed_list  = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.COMPLETED).all()
    onhold_list     = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.ON_HOLD).all()
    dropped_list    = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.DROPPED).all()
    plantoread_list = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.PLAN_TO_READ).all()

    book_list = [reading_list, completed_list, onhold_list, dropped_list, plantoread_list]
    book_data = get_list_data(book_list, ListType.BOOK)
    user_id = current_user.get_id()
    return render_template('mybookslist.html',
                           title='MyBooksList',
                           user_id=user_id,
                           all_data=book_data)


@app.route("/mybookslist_table", methods=['GET', 'POST'])
@login_required
def mybookslist_table():
    reading_list    = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.READING).all()
    completed_list  = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.COMPLETED).all()
    onhold_list     = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.ON_HOLD).all()
    dropped_list    = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.DROPPED).all()
    plantoread_list = BookList.query.filter_by(user_id=current_user.get_id(), status=BookStatus.PLAN_TO_READ).all()

    book_list = [reading_list, completed_list, onhold_list, dropped_list, plantoread_list]
    book_data = get_list_data(book_list, ListType.BOOK)
    user_id = current_user.get_id()
    return render_template('mybookslist_table.html',
                           title='MyBooksList',
                           user_id=user_id,
                           all_data=book_data)


@app.route("/user/books/grid/<user_name>", methods=['GET'])
@login_required
def user_bookslist_grid(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    # User not found
    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404

    # User found == current user
    if str(user.id) == current_user.get_id():
        return redirect(url_for('mybookslist'))

    # User found == admin
    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    # Check if user is in the current user's friends list
    # Admin bypasses private option
    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()
    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))

    reading_list    = BookList.query.filter_by(user_id=user.id, status=BookStatus.READING).all()
    completed_list  = BookList.query.filter_by(user_id=user.id, status=BookStatus.COMPLETED).all()
    onhold_list     = BookList.query.filter_by(user_id=user.id, status=BookStatus.ON_HOLD).all()
    dropped_list    = BookList.query.filter_by(user_id=user.id, status=BookStatus.DROPPED).all()
    plantoread_list = BookList.query.filter_by(user_id=user.id, status=BookStatus.PLAN_TO_READ).all()

    book_list = [reading_list, completed_list, onhold_list, dropped_list, plantoread_list]
    book_data = get_list_data(book_list, ListType.BOOK)
    user_id = user.id
    user_name = user.username
    return render_template('mybookslist.html',
                           title='MyBooksList',
                           user_id=user_id,
                           user_name=user_name,
                           all_data=book_data)


@app.route("/user/books/table/<user_name>", methods=['GET'])
@login_required
def user_bookslist_table(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    # User not found
    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404

    # User found == current user
    if str(user.id) == current_user.get_id():
        return redirect(url_for('mybookslist'))

    # User found == admin
    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    # Check if user is in the current user's friends list
    # Admin bypasses private option
    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()
    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))

    reading_list    = BookList.query.filter_by(user_id=user.id, status=BookStatus.READING).all()
    completed_list  = BookList.query.filter_by(user_id=user.id, status=BookStatus.COMPLETED).all()
    onhold_list     = BookList.query.filter_by(user_id=user.id, status=BookStatus.ON_HOLD).all()
    dropped_list    = BookList.query.filter_by(user_id=user.id, status=BookStatus.DROPPED).all()
    plantoread_list = BookList.query.filter_by(user_id=user.id, status=BookStatus.PLAN_TO_READ).all()

    book_list = [reading_list, completed_list, onhold_list, dropped_list, plantoread_list]
    book_data = get_list_data(book_list, ListType.BOOK)
    user_id = user.id
    user_name = user.username
    return render_template('mybookslist_table.html',
                           title='MyBooksList',
                           user_id=user_id,
                           user_name=user_name,
                           all_data=book_data)


@app.route('/delete_book', methods=['POST'])
@login_required
def delete_book():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        book_id = json_data['delete']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        book_id = int(book_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the book exists
    if Book.query.filter_by(id=book_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the book is in the current user's list
    if BookList.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    BookList.query.filter_by(book_id=book_id, user_id=current_user.get_id()).delete()
    db.session.commit()
    app.logger.info('[{}] Book with ID {} deleted'.format(current_user.get_id(), book_id))
    return '', 204


@app.route('/change_book_category', methods=['POST'])
@login_required
def change_book_category():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        book_new_category = json_data['status']
        book_id = json_data['book_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    category_list = ["Reading", "Completed", "On Hold", "Dropped", "Plan to Read"]
    if book_new_category not in category_list:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    try:
        book_id = int(book_id)
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    book = BookList.query.filter_by(book_id=book_id, user_id=current_user.get_id()).first()
    if book_new_category == 'Reading':
        book.status = BookStatus.READING
    elif book_new_category == 'Completed':
        book.status = BookStatus.COMPLETED
    elif book_new_category == 'On Hold':
        book.status = BookStatus.ON_HOLD
    elif book_new_category == 'Dropped':
        book.status = BookStatus.DROPPED
    elif book_new_category == 'Plan to Read':
        book.status = BookStatus.PLAN_TO_READ
    db.session.commit()
    app.logger.info('[{}] Category of the book with ID {} changed to {}'.format(current_user.get_id(),
                                                                                book_id,
                                                                                book_new_category))
    return '', 204


@app.route('/add_book', methods=['POST'])
@login_required
def add_book():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        book_id = json_data['book_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    add_element(book_id, ListType.BOOK)
    return '', 204


@app.route('/set_book_score', methods=['POST'])
@login_required
def set_book_score():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data   = request.get_json()
        score_value = round(float(json_data['score_value']), 2)
        book_id     = int(json_data['book_id'])
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the book exists
    if Book.query.filter_by(id=book_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the book is in the current user's list
    if BookList.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the score is between 0 and 10:
    if score_value > 10 or score_value < 0:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    book = BookList.query.filter_by(user_id=current_user.get_id(), book_id=book_id).first()
    book.score = score_value
    db.session.commit()
    app.logger.info('[{}] Book with ID {} scored {}'.format(current_user.get_id(), book_id, score_value))
    return '', 204


@app.route('/autocomplete_books', methods=['GET'])
@login_required
def autocomplete_books():
    search = request.args.get('q')
    if "%" in search:
        return jsonify([])

    results = autocomplete_search_element(search, ListType.BOOK)
    return jsonify(matching_results=results)


###################################################### Functions #######################################################


def get_all_account_stats(user_id, list_type):
    nb_of_element = get_list_count(user_id, list_type)
    total_element = sum(nb_of_element)
    total_time_element = get_total_time_spent(user_id, list_type)
    mean_score_element = get_mean_score(user_id, list_type)
    time_total_in_minutes_element = total_time_element[2]*3600

    element_level_tmp = "{:.2f}".format(round((np.sqrt(2500+200*(time_total_in_minutes_element))-50)/100, 2))
    element_level_tmp = str(element_level_tmp)
    element_level = element_level_tmp.split('.')

    list_rank_element = []
    if platform.system() == "Windows":
        fp = open("{0}".format(os.path.join(app.root_path, "static\\img\\Ranks\\Ranks.csv")), "r")
    else:  # Linux & macOS
        fp = open("{0}".format(os.path.join(app.root_path, "static/img/Ranks/Ranks.csv")), "r")
    for line in fp:
        list_rank_element.append(line.split(";"))
    fp.close()

    element_rank_data = []
    for i in range(0, len(list_rank_element)):
        if str(list_rank_element[i][0]) == str(element_level[0]):
            element_rank_data.append([str(list_rank_element[i][2]), str(list_rank_element[i][3])])

    if len(element_rank_data) == 0:
        element_rank_data.append(["General_Grade_4", "General Grade 4"])

    if total_element == 0:
        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            element_rate = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        elif list_type == ListType.BOOK:
            element_rate = [0.0, 0.0, 0.0, 0.0, 0.0]
    else:
        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            element_rate = [(float(nb_of_element[0]/total_element))*100,
                           (float(nb_of_element[1]/total_element))*100,
                           (float(nb_of_element[2]/total_element))*100,
                           (float(nb_of_element[3]/total_element))*100,
                           (float(nb_of_element[4]/total_element))*100,
                           (float(nb_of_element[5]/total_element))*100]
        elif list_type == ListType.BOOK:
            element_rate = [(float(nb_of_element[0]/total_element))*100,
                            (float(nb_of_element[1]/total_element))*100,
                            (float(nb_of_element[2]/total_element))*100,
                            (float(nb_of_element[3]/total_element))*100,
                            (float(nb_of_element[4]/total_element))*100]

    return [nb_of_element, total_time_element, mean_score_element, element_level, element_rank_data, element_rate]


def get_animes_achievements(user_id):
    all_achievements = []
    tmp_1, tmp_2, tmp_3, tmp_4, tmp_5, tmp_6, tmp_7, tmp_8, tmp_9, tmp_10 = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    animes = AnimeList.query.filter(AnimeList.status == "COMPLETED").filter_by(user_id=user_id).all()
    for anime in animes:
        genres = AnimeGenre.query.filter_by(anime_id=anime.anime_id).all()
        for genre in genres:
            a = genre.genre_id
            if a == 13:
                tmp_1 += 1
            elif a == 18:
                tmp_2 += 1
            elif a == 19:
                tmp_3 += 1
            elif a == 7:
                tmp_4 += 1
            elif a == 22:
                tmp_5 += 1
            elif a == 36:
                tmp_6 += 1
            elif a == 29:
                tmp_7 += 1
            elif a == 30:
                tmp_8 += 1
            elif a == 5 or a == 40:
                tmp_9 += 1
            elif a == 14 or a == 41:
                tmp_10 += 1
            else:
                pass

    ids = [13, 18, 19, 7, 22, 36, 29, 30, '5, 40', '14, 41']
    values = [tmp_1, tmp_2, tmp_3, tmp_4, tmp_5, tmp_6, tmp_7, tmp_8, tmp_9, tmp_10]
    for i in range(0, len(values)):
        achievements = AnimeAchievements.query.filter_by(genre=str(ids[i])).all()
        for achievement in achievements:
            threshold = achievement.threshold
            range_achiev = threshold.split("-")
            if int(range_achiev[0]) <= int(values[i]) <= int(range_achiev[1]):
                data_achiev = [achievement.image_id, achievement.level, achievement.title, achievement.description]
                all_achievements.append(data_achiev)

    return all_achievements


def get_list_count(user_id, list_type):
        if list_type is ListType.SERIES:
            watching = SeriesList.query.filter_by(user_id=user_id, status='WATCHING').count()
            completed = SeriesList.query.filter_by(user_id=user_id, status='COMPLETED').count()
            onhold = SeriesList.query.filter_by(user_id=user_id, status='ON_HOLD').count()
            random = SeriesList.query.filter_by(user_id=user_id, status='RANDOM').count()
            dropped = SeriesList.query.filter_by(user_id=user_id, status='DROPPED').count()
            plantowatch = SeriesList.query.filter_by(user_id=user_id, status='PLAN_TO_WATCH').count()
        elif list_type is ListType.ANIME:
            watching = AnimeList.query.filter_by(user_id=user_id, status='WATCHING').count()
            completed = AnimeList.query.filter_by(user_id=user_id, status='COMPLETED').count()
            onhold = AnimeList.query.filter_by(user_id=user_id, status='ON_HOLD').count()
            random = AnimeList.query.filter_by(user_id=user_id, status='RANDOM').count()
            dropped = AnimeList.query.filter_by(user_id=user_id, status='DROPPED').count()
            plantowatch = AnimeList.query.filter_by(user_id=user_id, status='PLAN_TO_WATCH').count()
        elif list_type is ListType.BOOK:
            reading = BookList.query.filter_by(user_id=user_id, status='READING').count()
            completed = BookList.query.filter_by(user_id=user_id, status='COMPLETED').count()
            onhold = BookList.query.filter_by(user_id=user_id, status='ON_HOLD').count()
            dropped = BookList.query.filter_by(user_id=user_id, status='DROPPED').count()
            plantoread = BookList.query.filter_by(user_id=user_id, status='PLAN_TO_READ').count()

        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            statistics = [watching, completed, onhold, random, dropped, plantowatch]
        elif list_type == ListType.BOOK:
            statistics = [reading, completed, onhold, dropped, plantoread]
        return statistics


def autocomplete_search_element(element_name, list_type):
    if list_type == ListType.SERIES:
        autocomplete_local_results = Series.query.filter(Series.name.like("%{0}%".format(element_name))).all()
        cover_url = url_for('static', filename="series_covers/")
    elif list_type == ListType.ANIME:
        autocomplete_local_results = Anime.query.filter(Anime.name.like("%{0}%".format(element_name))).all()
        cover_url = url_for('static', filename="animes_covers/")
    elif list_type == ListType.BOOK:
        autocomplete_local_results = Book.query.filter(Book.title.like("%{0}%".format(element_name))).all()
        cover_url = url_for('static', filename="books_covers/")

    if list_type == ListType.SERIES:
        local_results = []
        for i in range(5):
            try:
                tmp = {"id": "{0}".format(autocomplete_local_results[i].id),
                       "value": "{0}".format(autocomplete_local_results[i].name),
                       "category": "Local Database",
                       "label": "..{0}{1}".format(cover_url, autocomplete_local_results[i].image_cover)}
                local_results.append(tmp)
            except:
                pass

        if len(local_results) >= 3:
            return local_results

        else:
            while True:
                try:
                    response = requests.get("https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}"
                                            .format(themoviedb_api_key, element_name))
                except:
                    return None

                if response.status_code == 401:
                    app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
                    return None
                app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

                if response.headers["X-RateLimit-Remaining"] == "0":
                    app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
                    time.sleep(3)
                else:
                    break

            data = json.loads(response.text)
            if data["total_results"] == 0:
                if len(local_results) == 0:
                    return [{"category": "False"}]
                else:
                    return local_results
            else:
                tmdb_results = []
                for i in range(8):
                    try:
                        genre_id = data["results"][i]["genre_ids"]
                        country = data["results"][i]["origin_country"][0]

                        if 16 in genre_id:
                            if "JP" in country:
                                pass
                            else:
                                if data["results"][i]["poster_path"] is None:
                                    data["results"][i]["poster_path"] = url_for('static', filename="series_covers/default.jpg")
                                else:
                                    url = "http://image.tmdb.org/t/p/w300/"
                                    tmp = {"id": "{0}".format(data['results'][i]['id']),
                                           "value": "{0}".format(data["results"][i]["name"]),
                                           "category": "Online API Database",
                                           "label": "{0}{1}".format(url, data["results"][i]["poster_path"])}
                                tmdb_results.append(tmp)
                        else:
                            if data["results"][i]["poster_path"] is None:
                                data["results"][i]["poster_path"] = url_for('static', filename="animes_covers/default.jpg")
                            else:
                                url = "http://image.tmdb.org/t/p/w300/"
                                tmp = {"id": "{0}".format(data['results'][i]['id']),
                                       "value": "{0}".format(data["results"][i]["name"]),
                                       "category": "Online API Database",
                                       "label": "{0}{1}".format(url, data["results"][i]["poster_path"])}
                            tmdb_results.append(tmp)
                    except:
                        pass
                all_results = local_results + tmdb_results
                return all_results

    elif list_type == ListType.ANIME:
        local_results = []
        for i in range(5):
            try:
                tmp = {"id": "{0}".format(autocomplete_local_results[i].id),
                       "value": "{0}".format(autocomplete_local_results[i].name),
                       "category": "Local Database",
                       "label": "..{0}{1}".format(cover_url, autocomplete_local_results[i].image_cover)}
                local_results.append(tmp)
            except:
                pass

        if len(local_results) >= 3:
            return local_results

        else:
            while True:
                try:
                    response = requests.get("https://api.themoviedb.org/3/search/multi?api_key={0}&query={1}"
                                            .format(themoviedb_api_key, element_name))
                except:
                    return None

                if response.status_code == 401:
                    app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
                    return None
                app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

                if response.headers["X-RateLimit-Remaining"] == "0":
                    app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
                    time.sleep(3)
                else:
                    break

            data = json.loads(response.text)
            if data["total_results"] == 0:
                if len(local_results) == 0:
                    return [{"category":"False"}]
                else:
                    return local_results
            else:
                tmdb_results = []
                for i in range(8):
                    try:
                        genre_id = data["results"][i]["genre_ids"]
                        try:
                            country = data["results"][i]["origin_country"][0]
                        except:
                            country = data["results"][i]["original_language"]

                        if 16 in genre_id:
                            if "JP" in country:
                                if data["results"][i]["poster_path"] is None:
                                    data["results"][i]["poster_path"] = url_for('static', filename="animes_covers/default.jpg")
                                else:
                                    url = "http://image.tmdb.org/t/p/w300/"
                                    tmp = {"id": "{0}".format(data['results'][i]['id']),
                                           "value": "{0}".format(data["results"][i]["name"]),
                                           "category": "Online API Database",
                                           "label": "{0}{1}".format(url, data["results"][i]["poster_path"])}
                                tmdb_results.append(tmp)
                            # elif "ja" in country:
                            #     if data["results"][i]["poster_path"] is None:
                            #         data["results"][i]["poster_path"] = url_for('static', filename="animes_covers/default.jpg")
                            #     else:
                            #         url = "http://image.tmdb.org/t/p/w300/"
                            #         tmp = {"id": "{0}".format(data['results'][i]['id']),
                            #                "value": "{0}".format(data["results"][i]["title"]),
                            #                "category": "Online API Database",
                            #                "label": "{0}{1}".format(url, data["results"][i]["poster_path"])}
                            #     tmdb_results.append(tmp)
                            else:
                                pass
                        else:
                            pass
                    except:
                        pass

                all_results = local_results + tmdb_results
                return all_results

    elif list_type == ListType.BOOK:
        local_results = []
        for i in range(5):
            try:
                tmp = {"id": "{0}".format(autocomplete_local_results[i].id),
                       "value": "{0}".format(autocomplete_local_results[i].title),
                       "category": "Local Database",
                       "label": "..{0}{1}".format(cover_url, autocomplete_local_results[i].image_cover)}
                local_results.append(tmp)
            except:
                pass

        if len(local_results) >= 3:
            return local_results

        else:
            try:
                response = requests.get("https://www.googleapis.com/books/v1/volumes?q={0}&key={1}"
                                        .format(element_name, google_book_api_key))
            except:
                return None

            if response.status_code == 401:
                app.logger.error('[SYSTEM] Error requesting Google API :(')
                return None

            data = json.loads(response.text)
            if data["totalItems"] == 0:
                if len(local_results) == 0:
                    return [{"category": "False"}]
                else:
                    return local_results
            else:
                google_results = []
                for i in range(5):
                    try:
                        if data["items"][i]["volumeInfo"]["imageLinks"]["thumbnail"] is None:
                            data["items"][i]["volumeInfo"]["imageLinks"]["thumbnail"] = \
                                url_for('static', filename="books_covers/default.jpg")

                        tmp = {"id": "{0}".format(data["items"][i]["id"]),
                               "value": "{0}".format(data["items"][i]["volumeInfo"]["title"]),
                               "category": "Online API Database",
                               "label": "{0}".format(data["items"][i]["volumeInfo"]["imageLinks"]["thumbnail"])}
                        google_results.append(tmp)
                    except:
                        pass

                all_results = local_results + google_results
        print(all_results)
        return all_results


def add_element(element_id, list_type):
    if element_id == "":
        if list_type == ListType.SERIES:
            return redirect(url_for('myserieslist'))
        elif list_type == ListType.ANIME:
            return redirect(url_for('myanimeslist'))
        elif list_type == ListType.BOOK:
            return redirect(url_for('mybookslist'))

    # Check if the ID element exist in the database
    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
        if element is None:
            element = Series.query.filter_by(themoviedb_id=element_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()
        if element is None:
            element = Anime.query.filter_by(themoviedb_id=element_id).first()
    elif list_type == ListType.BOOK:
        element = Book.query.filter_by(id=element_id).first()
        if element is None:
            element = Book.query.filter_by(google_id=element_id).first()

    # If ID is correct, we know which one to add in the user's list
    if element is not None:
        # Check if the element is already in the current's user list
        if list_type == ListType.SERIES:
            if SeriesList.query.filter_by(user_id=current_user.get_id(), series_id=element.id).first() is not None:
                return flash("This series is already in your list", "warning")
        elif list_type == ListType.ANIME:
            if AnimeList.query.filter_by(user_id=current_user.get_id(), anime_id=element.id).first() is not None:
                return flash("This anime is already in your list", "warning")
        elif list_type == ListType.BOOK:
            if BookList.query.filter_by(user_id=current_user.get_id(), book_id=element.id).first() is not None:
                return flash("This book is already in your list", "warning")

        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            # Check if there is more than 30 min since the last update
            last_update = element.last_update
            time_delta = datetime.utcnow() - last_update
            if time_delta.days > 0 or (time_delta.seconds/1800 > 1):  # 30 min
                refresh_element_data(element.id, list_type)
            else:
                pass
        else:
            pass

        add_element_to_user(element.id, int(current_user.get_id()), list_type)

    # Otherwise we need to recover it from an online API
    else:
        if list_type == ListType.SERIES:
            series_data = get_element_data_from_api(element_id, ListType.SERIES)
            if series_data is None:
                return flash("There was a problem while getting series' info. Please try again later.",
                             "warning")

            cover_id = save_api_cover(series_data["poster_path"], ListType.SERIES)
            if cover_id is None:
                return flash("There was a problem while getting series' poster. Please try again later.",
                             "warning")

            series_id = add_element_in_base(series_data, cover_id, ListType.SERIES)
            add_element_to_user(series_id, int(current_user.get_id()), list_type)
            return redirect(url_for('myserieslist'))
        elif list_type == ListType.ANIME:
            anime_data = get_element_data_from_api(element_id, ListType.ANIME)
            if anime_data is None:
                return flash("There was a problem while getting series' info. Please try again later.",
                             "warning")

            cover_id = save_api_cover(anime_data["poster_path"], ListType.ANIME)
            if cover_id is None:
                return flash("There was a problem while getting series' poster. Please try again later.",
                             "warning")

            anime_id = add_element_in_base(anime_data, cover_id, list_type)
            add_element_to_user(anime_id, int(current_user.get_id()), list_type)
            return redirect(url_for('myanimeslist'))
        elif list_type == ListType.BOOK:
            book_data = get_element_data_from_api(element_id, ListType.BOOK)
            if book_data is None:
                return flash("There was a problem while getting book's info. Please try again later.", "warning")

            try:
                cover_id = save_api_cover(book_data["volumeInfo"]["imageLinks"]["small"], ListType.BOOK)
            except:
                cover_id = save_api_cover(book_data["volumeInfo"]["imageLinks"]["thumbnail"], ListType.BOOK)
            if cover_id is None:
                return flash("There was a problem while getting the book's cover. Please try again later.", "warning")

            book_id = add_element_in_base(book_data, cover_id, list_type)
            add_element_to_user(book_id, int(current_user.get_id()), list_type)
            return redirect(url_for('mybookslist'))


def get_element_data_from_api(api_id, list_type):
    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        try:
            response = requests.get(
                "https://api.themoviedb.org/3/tv/{0}?api_key={1}".format(api_id, themoviedb_api_key))
        except:
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
            return None

        app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

        if response.headers["X-RateLimit-Remaining"] == "0":
            app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
            time.sleep(3)
            get_element_data_from_api(api_id, list_type)
        else:
            pass
    if list_type == ListType.BOOK:
        try:
            response = requests.get("https://www.googleapis.com/books/v1/volumes/{0}".format(api_id))
        except:
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting google API :(')
            return None

    return json.loads(response.text)


def save_api_cover(cover_path, list_type):
    if cover_path is None:
        return "default.jpg"
    cover_id = "{}.jpg".format(secrets.token_hex(8))

    if list_type == ListType.SERIES:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\series_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/series_covers/")
    elif list_type == ListType.ANIME:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\\animes_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/animes_covers/")
    elif list_type == ListType.BOOK:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\\books_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/books_covers/")

    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        try:
            urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{0}".format(cover_path),
                                       "{}{}".format(local_covers_path, cover_id))
        except:
            return None
    elif list_type == ListType.BOOK:
        try:
            urllib.request.urlretrieve("{0}".format(cover_path), "{0}{1}".format(local_covers_path, cover_id))
        except:
            return None

    img = Image.open("{}{}".format(local_covers_path, cover_id))
    img = img.resize((300, 450), Image.ANTIALIAS)
    img.save("{0}{1}".format(local_covers_path, cover_id), quality=90)

    return cover_id


def add_element_in_base(element_data, element_cover_id, list_type):
    if list_type == ListType.SERIES:
        element = Series.query.filter_by(themoviedb_id=element_data["id"]).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(themoviedb_id=element_data["id"]).first()
    elif list_type == ListType.BOOK:
        element = Book.query.filter_by(google_id=element_data["id"]).first()

    if element is not None:
        return element.id

    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        name = element_data["name"]
        original_name = element_data["original_name"]
        first_air_date = element_data["first_air_date"]
        last_air_date = element_data["last_air_date"]
        homepage = element_data["homepage"]
        in_production = element_data["in_production"]
        total_seasons = element_data["number_of_seasons"]
        total_episodes = element_data["number_of_episodes"]
        status = element_data["status"]
        vote_average = element_data["vote_average"]
        vote_count = element_data["vote_count"]
        synopsis = element_data["overview"]
        popularity = element_data["popularity"]
        themoviedb_id = element_data["id"]

        try:
            created_by = ""
            for person in element_data["created_by"]:
                created_by = created_by + person["name"] + ", "
            if len(element_data["created_by"]) > 0:
                created_by = created_by[:-2]
            else:
                created_by = None
        except:
            created_by = None

        try:
            episode_duration = element_data["episode_run_time"][0]
        except:
            episode_duration = None

        try:
            origin_country = ""
            for country in element_data["origin_country"]:
                origin_country = origin_country + country + ", "
            if len(element_data["origin_country"]) > 0:
                origin_country = origin_country[:-2]
            else:
                origin_country = None
        except:
            origin_country = None

        # Check if there is a special season
        # We do not want to take it into account
        seasons_data = []
        if len(element_data["seasons"]) == 0:
            return None

        if element_data["seasons"][0]["season_number"] == 0:  # Special season
            for i in range(len(element_data["seasons"])):
                try:
                    seasons_data.append(element_data["seasons"][i + 1])
                except:
                    pass
        else:
            for i in range(len(element_data["seasons"])):
                try:
                    seasons_data.append(element_data["seasons"][i])
                except:
                    pass

        genres_data = []
        for i in range(len(element_data["genres"])):
            try:
                genres_data.append(element_data["genres"][i]["name"])
            except:
                pass

        networks_data = []
        for i in range(len(element_data["networks"])):
            try:
                networks_data.append(element_data["networks"][i]["name"])
            except:
                pass

        # Add the element into the table
        if list_type == ListType.SERIES:
            element = Series(name=name,
                             original_name=original_name,
                             image_cover=element_cover_id,
                             first_air_date=first_air_date,
                             last_air_date=last_air_date,
                             homepage=homepage,
                             in_production=in_production,
                             created_by=created_by,
                             total_seasons=total_seasons,
                             total_episodes=total_episodes,
                             episode_duration=episode_duration,
                             origin_country=origin_country,
                             status=status,
                             vote_average=vote_average,
                             vote_count=vote_count,
                             synopsis=synopsis,
                             popularity=popularity,
                             themoviedb_id=themoviedb_id,
                             last_update=datetime.utcnow())
        elif list_type == ListType.ANIME:
            element = Anime(name=name,
                            original_name=original_name,
                            image_cover=element_cover_id,
                            first_air_date=first_air_date,
                            last_air_date=last_air_date,
                            homepage=homepage,
                            in_production=in_production,
                            created_by=created_by,
                            total_seasons=total_seasons,
                            total_episodes=total_episodes,
                            episode_duration=episode_duration,
                            origin_country=origin_country,
                            status=status,
                            vote_average=vote_average,
                            vote_count=vote_count,
                            synopsis=synopsis,
                            popularity=popularity,
                            themoviedb_id=themoviedb_id,
                            last_update=datetime.utcnow())

        db.session.add(element)
        db.session.commit()

        # Add genres
        if list_type == ListType.SERIES:

            for genre_data in genres_data:
                genre = SeriesGenre(series_id=element.id,
                                    genre=genre_data)
                db.session.add(genre)
        elif list_type == ListType.ANIME:
            try:
                response = requests.get("https://api.jikan.moe/v3/search/anime?q={0}".format(element_data["name"]))
                data_mal = json.loads(response.text)
                mal_id = data_mal["results"][0]["mal_id"]

                response = requests.get("https://api.jikan.moe/v3/anime/{}".format(mal_id))
                data_mal = json.loads(response.text)
                genres = data_mal["genres"]

                for genre in genres:
                    add_genre = AnimeGenre(anime_id=element.id,
                                           genre=genre["name"],
                                           genre_id=int(genre["mal_id"]))
                    db.session.add(add_genre)
            except:
                for genre_data in genres_data:
                    add_genre = AnimeGenre(anime_id=element.id,
                                           genre=genre_data)
                    db.session.add(add_genre)

        # Add the different networks for each serie
        for network_data in networks_data:
            if list_type == ListType.SERIES:
                networks = SeriesNetwork(series_id=element.id,
                                         network=network_data)
            elif list_type == ListType.ANIME:
                networks = AnimeNetwork(anime_id=element.id,
                                        network=network_data)
            db.session.add(networks)

        # Add number of episodes for each season
        for season_data in seasons_data:
            if list_type == ListType.SERIES:
                season = SeriesEpisodesPerSeason(series_id=element.id,
                                                 season=season_data["season_number"],
                                                 episodes=season_data["episode_count"])
            elif list_type == ListType.ANIME:
                season = AnimeEpisodesPerSeason(anime_id=element.id,
                                                season=season_data["season_number"],
                                                episodes=season_data["episode_count"])
            db.session.add(season)
        db.session.commit()

    elif list_type == ListType.BOOK:
        title = element_data["volumeInfo"]["title"]
        authors = element_data["volumeInfo"]["authors"][0]
        published_date = element_data["volumeInfo"]["publishedDate"]
        try:
            published_date = published_date[0:4]
        except:
            pass

        def clean_html(raw_html):
            cleaner = re.compile('<.*?>')
            cleantext = re.sub(cleaner, '', raw_html)
            return cleantext

        description = clean_html(element_data["volumeInfo"]["description"])
        page_count = element_data["volumeInfo"]["pageCount"]
        categories = element_data["volumeInfo"]["categories"][0]
        google_id = element_data["id"]

        if "General" in categories:
            new_categories = categories.replace("/ General", "")
            categories = new_categories

        # Add the element into the table
        element = Book(title=title,
                       authors=authors,
                       image_cover=element_cover_id,
                       published_date=published_date,
                       description=description,
                       page_count=page_count,
                       categories=categories,
                       google_id=google_id)

        db.session.add(element)
        db.session.commit()

    return element.id


def add_element_to_user(element_id, user_id, list_type):
    if list_type == ListType.SERIES:
        user_list = SeriesList(user_id=user_id,
                               series_id=element_id,
                               current_season=1,
                               last_episode_watched=1,
                               status=Status.WATCHING)

        data = SeriesEpisodeTimestamp(user_id=user_id,
                                      series_id=element_id,
                                      season=1,
                                      episode=1,
                                      timestamp=datetime.utcnow())

        app.logger.info('[{}] Added series with the ID {}'.format(user_id, element_id))
        db.session.add(user_list)
        db.session.add(data)
        db.session.commit()
    elif list_type == ListType.ANIME:
        user_list = AnimeList(user_id=user_id,
                              anime_id=element_id,
                              current_season=1,
                              last_episode_watched=1,
                              status=Status.WATCHING)

        data = AnimeEpisodeTimestamp(user_id=user_id,
                                     anime_id=element_id,
                                     season=1,
                                     episode=1,
                                     timestamp=datetime.utcnow())

        app.logger.info('[{}] Added anime with the ID {}'.format(user_id, element_id))
        db.session.add(user_list)
        db.session.add(data)
        db.session.commit()
    elif list_type == ListType.BOOK:
        user_list = BookList(user_id=user_id,
                             book_id=element_id,
                             commentary= None,
                             read_year= None,
                             status=BookStatus.READING)

        app.logger.info('[{}] Added book with the ID {}'.format(user_id, element_id))
        db.session.add(user_list)
        db.session.commit()


def get_list_data(list, list_type):
    all_list_data = []
    for category in list:
        category_element_data = []
        for element in category:
            current_element = {}
            # Cover, name, genre and network of the element
            if list_type == ListType.SERIES:
                element_data = Series.query.filter_by(id=element.series_id).first()
                cover_url = url_for('static', filename="series_covers/{}".format(element_data.image_cover))
                element_data_genres = SeriesGenre.query.filter_by(series_id=element.series_id).all()
                element_data_networks = SeriesNetwork.query.filter_by(series_id=element.series_id).all()
            elif list_type == ListType.ANIME:
                element_data = Anime.query.filter_by(id=element.anime_id).first()
                cover_url = url_for('static', filename="animes_covers/{}".format(element_data.image_cover))
                element_data_genres = AnimeGenre.query.filter_by(anime_id=element.anime_id).all()
                element_data_networks = AnimeNetwork.query.filter_by(anime_id=element.anime_id).all()
            elif list_type == ListType.BOOK:
                element_data = Book.query.filter_by(id=element.book_id).first()
                cover_url = url_for('static', filename="books_covers/{}".format(element_data.image_cover))

            current_element["cover_url"] = cover_url

            if list_type == ListType.SERIES or list_type == ListType.ANIME:
                # Element meta data
                current_element["id"] = element_data.id
                current_element["name"] = element_data.name
                current_element["original_name"] = element_data.original_name

                tmp = []
                for i in range(0, len(element_data_genres)):
                    tmp.append(element_data_genres[i].genre)
                current_element["genre"] = ', '.join(tmp)

                tmp_fair_date = element_data.first_air_date.split('-')
                tmp_fair_date_2 = [tmp_fair_date[2], tmp_fair_date[1], tmp_fair_date[0]]
                fair_date = '-'.join(tmp_fair_date_2)
                current_element["first_air_date"] = fair_date

                tmp_lair_date = element_data.last_air_date.split('-')
                tmp_lair_date_2 = [tmp_lair_date[2], tmp_lair_date[1], tmp_lair_date[0]]
                lair_date = '-'.join(tmp_lair_date_2)
                current_element["last_air_date"] = lair_date

                current_element["homepage"] = element_data.homepage
                current_element["in_production"] = element_data.in_production

                tmp = []
                for i in range(0, len(element_data_networks)):
                    tmp.append(element_data_networks[i].network)
                current_element["network"] = ', '.join(tmp)

                current_element["created_by"] = element_data.created_by
                current_element["episode_duration"] = element_data.episode_duration
                current_element["total_seasons"] = element_data.total_seasons
                current_element["total_episodes"] = element_data.total_episodes
                current_element["origin_country"] = element_data.origin_country
                current_element["status"] = element_data.status
                current_element["synopsis"] = element_data.synopsis
                current_element["score"] = element.score

                # Can update
                time_delta = datetime.utcnow() - element_data.last_update
                if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
                    current_element["can_update"] = True
                else:
                    current_element["can_update"] = False

                # Number of season and the number of ep of each season
                if list_type == ListType.SERIES:
                    episodesperseason = SeriesEpisodesPerSeason.query.filter_by(series_id=element_data.id).order_by(SeriesEpisodesPerSeason.season.asc()).all()
                elif list_type == ListType.ANIME:
                    episodesperseason = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_data.id).order_by(AnimeEpisodesPerSeason.season.asc()).all()
                tmp = []
                for season in episodesperseason:
                    tmp.append(season.episodes)
                current_element["season_data"] = tmp

                current_element["current_season"] = element.current_season
                current_element["last_episode_watched"] = element.last_episode_watched
                category_element_data.append(current_element)
            elif list_type == ListType.BOOK:
                # Element meta data
                current_element["title"] = element_data.title
                current_element["authors"] = element_data.authors
                current_element["id"] = element_data.id
                current_element["published_date"] = element_data.published_date
                current_element["description"] = element_data.description
                current_element["page_count"] = element_data.page_count
                current_element["categories"] = element_data.categories
                current_element["score"] = element.score
                category_element_data.append(current_element)

        if list_type == ListType.SERIES or list_type == ListType.ANIME:
            category_element_data = sorted(category_element_data, key=lambda i: (i['name']))
        elif list_type == ListType.BOOK:
            category_element_data = sorted(category_element_data, key=lambda i: (i['title']))
        all_list_data.append(category_element_data)

    return all_list_data


def get_mean_score(user_id, list_type):
    if list_type is ListType.SERIES:
        all_scores  = SeriesList.query.filter_by(user_id=user_id).all()
    if list_type is ListType.ANIME:
         all_scores = AnimeList.query.filter_by(user_id=user_id).all()
    if list_type is ListType.BOOK:
        all_scores  = BookList.query.filter_by(user_id=user_id).all()

    # If no element in the list mean score = 0
    if len(all_scores) == 0:
        mean_score = 0.00
    else:
        no_score = 0
        score = 0
        for i in range(0, len(all_scores)):
            tmp = all_scores[i].score
            if tmp is None:
                no_score += 1
            else:
                score += float(all_scores[i].score)
        if len(all_scores) == no_score:
            mean_score = 0.00
        else:
            mean_score = round(score/(len(all_scores)-no_score), 2)

    return mean_score


def get_total_time_spent(user_id, list_type):
    if list_type == ListType.SERIES:
        list = SeriesList.query.filter(SeriesList.status != "PLAN_TO_WATCH").filter_by(user_id=user_id).all()
    elif list_type == ListType.ANIME:
        list = AnimeList.query.filter(AnimeList.status != "PLAN_TO_WATCH").filter_by(user_id=user_id).all()
    elif list_type == ListType.BOOK:
        list = BookList.query.filter(BookList.status == "COMPLETED").filter_by(user_id=user_id).all()

    if list_type == ListType.SERIES or list_type == ListType.ANIME:
        episodes_counter = 0
        time_spent_min = 0
        for element in list:
            if list_type == ListType.SERIES:
                episode_duration = Series.query.filter_by(id=element.series_id).first().episode_duration
            elif list_type == ListType.ANIME:
                episode_duration = Anime.query.filter_by(id=element.anime_id).first().episode_duration

            if episode_duration is None:
                continue

            current_season = element.current_season
            current_ep = element.last_episode_watched
            for i in range(1, current_season):
                if list_type == ListType.SERIES:
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=element.series_id, season=i).first().episodes
                elif list_type == ListType.ANIME:
                    ep = AnimeEpisodesPerSeason.query.filter_by(anime_id=element.anime_id, season=i).first().episodes
                episodes_counter += ep
                time_spent_min += ep*episode_duration

            episodes_counter += current_ep
            time_spent_min += current_ep*episode_duration

        time_spent_hours = int((time_spent_min/60))
        time_spent_days = round(time_spent_min/(60*24), 1)
        return [episodes_counter, time_spent_hours, time_spent_days]

    elif list_type == ListType.BOOK:
        total_pages = 0
        for book in list:
            pages_count = Book.query.filter_by(id=book.book_id).first().page_count
            total_pages += pages_count

        time_spent_hours = int(((total_pages*2)/60))
        time_spent_days = round((total_pages*2)/(60*24), 1)
        return [total_pages, time_spent_hours, time_spent_days]


def refresh_element_data(element_id, list_type):
    if list_type == ListType.SERIES:
        element = Series.query.filter_by(id=element_id).first()
    elif list_type == ListType.ANIME:
        element = Anime.query.filter_by(id=element_id).first()

    element_data = get_element_data_from_api(element.themoviedb_id, list_type)

    if element_data is None:
        return flash("There was an error while refreshing. Please try again later.")

    name            = element_data["name"]
    original_name   = element_data["original_name"]
    first_air_date  = element_data["first_air_date"]
    last_air_date   = element_data["last_air_date"]
    homepage        = element_data["homepage"]
    in_production   = element_data["in_production"]
    total_seasons   = element_data["number_of_seasons"]
    total_episodes  = element_data["number_of_episodes"]
    status          = element_data["status"]
    vote_average    = element_data["vote_average"]
    vote_count      = element_data["vote_count"]
    synopsis        = element_data["overview"]
    popularity      = element_data["popularity"]
    element_poster  = element_data["poster_path"]

    if list_type == ListType.SERIES:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\series_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/series_covers/")
    elif list_type == ListType.ANIME:
        if platform.system() == "Windows":
            local_covers_path = os.path.join(app.root_path, "static\\animes_covers\\")
        else:  # Linux & macOS
            local_covers_path = os.path.join(app.root_path, "static/animes_covers/")

    try:
        urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{0}".format(element_poster),
                                   "{}{}".format(local_covers_path, element.image_cover))
    except:
        return flash("There was an error while refreshing. Please try again later.")

    img = Image.open(local_covers_path + element.image_cover)
    img = img.resize((300, 450), Image.ANTIALIAS)
    img.save(local_covers_path + element.image_cover, quality=90)

    try:
        created_by = ""
        for person in element_data["created_by"]:
            created_by = created_by + person["name"] + ", "
        if len(element_data["created_by"]) > 0:
            created_by = created_by[:-2]
        else:
            created_by = None
    except:
        created_by = None

    try:
        episode_duration = element_data["episode_run_time"][0]
    except:
        episode_duration = None

    try:
        origin_country = ""
        for country in element_data["origin_country"]:
            origin_country = origin_country + country + ", "
        if len(element_data["origin_country"]) > 0:
            origin_country = origin_country[:-2]
        else:
            origin_country = None
    except:
        origin_country = None

    # Check if there is a special season
    # We do not want to take it into account
    seasons_data = []
    if element_data["seasons"][0]["season_number"] == 0:  # Special season
        for i in range(len(element_data["seasons"])):
            try:
                seasons_data.append(element_data["seasons"][i + 1])
            except:
                pass
    else:
        for i in range(len(element_data["seasons"])):
            try:
                seasons_data.append(element_data["seasons"][i])
            except:
                pass

    # Genres
    genres_data = []
    for i in range(len(element_data["genres"])):
        genres_data.append(element_data["genres"][i])

    # Networks
    networks_data = []
    for i in range(len(element_data["networks"])):
        networks_data.append(element_data["networks"][i])

    # Update the element
    element.name                = name
    element.original_name       = original_name
    element.first_air_date      = first_air_date
    element.last_air_date       = last_air_date
    element.homepage            = homepage
    element.in_production       = in_production
    element.created_by          = created_by
    element.total_seasons       = total_seasons
    element.total_episodes      = total_episodes
    element.episode_duration    = episode_duration
    element.origin_country      = origin_country
    element.status              = status
    element.vote_average        = vote_average
    element.vote_count          = vote_count
    element.synopsis            = synopsis
    element.popularity          = popularity
    element.last_update         = datetime.utcnow()

    # Update the number of seasons and episodes
    for season_data in seasons_data:
        if list_type == ListType.SERIES:
            season = SeriesEpisodesPerSeason.query.filter_by(series_id=element_id, season=season_data["season_number"]).first()
            if season is None:
                season = SeriesEpisodesPerSeason(series_id=element.id,
                                                 season=season_data["season_number"],
                                                 episodes=season_data["episode_count"])
                db.session.add(season)
            else:
                season.episodes = season_data["episode_count"]
        elif list_type == ListType.ANIME:
            season = AnimeEpisodesPerSeason.query.filter_by(anime_id=element_id,
                                                            season=season_data["season_number"]).first()
            if season is None:
                season = AnimeEpisodesPerSeason(anime_id=element.id,
                                                season=season_data["season_number"],
                                                episodes=season_data["episode_count"])
                db.session.add(season)
            else:
                season.episodes = season_data["episode_count"]

    # TODO : refresh Networks and Genres
    db.session.commit()
    app.logger.info("[{}] Refreshed the element with the ID {}".format(current_user.get_id(), element_id))


def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    try:
        i = Image.open(form_picture)
    except:
        return "default.jpg"
    i = i.resize((300, 300), Image.ANTIALIAS)
    i.save(picture_path, quality=90)
    return picture_fn


def add_friend(friend_username):
    friend_to_add = User.query.filter_by(username=friend_username).first()
    if friend_to_add is None or friend_to_add.id == 1:
        app.logger.info('[{}] Attempt of adding user {} as friend'.format(current_user.get_id(), friend_username))
        return flash('Sorry, no user with this username', 'info')

    else:
        friends = Friend.query.filter_by(user_id=current_user.get_id()).all()

        for friend in friends:
            if friend_to_add.id == friend.friend_id:
                return flash('Username already in your friend list', 'info')

        add_user = Friend(user_id=current_user.get_id(), friend_id=friend_to_add.id, status="request")
        db.session.add(add_user)
        db.session.commit()

        add_user_2 = Friend(user_id=friend_to_add.id, friend_id=current_user.get_id(), status="pending")
        db.session.add(add_user_2)
        db.session.commit()

        app.logger.info('[{}] Friend request sent to user with ID {}'.format(current_user.get_id(), friend_to_add.id))
        flash("Your friend request has been sent.", 'success')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\emails\\password_reset.html")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/emails/password_reset.html")

    email_template = open(path, 'r').read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('reset_token', token=token, _external=True))

    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised when sending reset email to user with the ID {} : {}'.format(user.id, e))
        return False


def send_register_email(user):
    token = user.get_register_token()
    msg = Message(subject='MyLists Register Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\emails\\register.html")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/emails/register.html")

    email_template = open(path, 'r').read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('register_token', token=token, _external=True))

    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised when sending register email to user with the ID {} : {}'.format(user.id, e))
        return False


def send_email_update_email(user):
    token = user.get_email_update_token()
    msg = Message(subject='MySerieList Email Update Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email],
                  bcc=[app.config['MAIL_USERNAME']],
                  reply_to=app.config['MAIL_USERNAME'])

    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\emails\\email_update.html")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/emails/email_update.html")

    email_template = open(path, 'r').read().replace("{1}", user.username)
    email_template = email_template.replace("{2}", url_for('email_update_token', token=token, _external=True))

    msg.html = email_template

    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error('[SYSTEM] Exception raised when sending email update email to user with the ID {} : {}'.format(user.id, e))
        return False


###################################################### CRAWL TEST ######################################################


def crawl_tmdb():
    import time
    start_time = time.time()

    for i in range(1, 501):

        response = requests.get("https://api.themoviedb.org/3/tv/{0}?api_key={1}".format(i, themoviedb_api_key))
        print(response.headers["X-RateLimit-Remaining"])

        if response.status_code == 200:
            series_data = json.loads(response.text)
            print("Serie ID {} : OK".format(i))
        else:
            print("Serie ID {} : NON OK".format(i))
            continue

        if series_data["poster_path"] is not None:
            cover_id = save_api_cover(series_data["poster_path"], ListType.SERIES)
            add_element_in_base(series_data, cover_id, ListType.SERIES)
        else:
            add_element_in_base(series_data, "default.jpg", ListType.SERIES)

    print("--- %s seconds ---" % (time.time() - start_time))


def test_stats_series():
    get_scores = SeriesList.query.filter_by(user_id=current_user.get_id()).all()

    ################################## Rating vs Count ###################################
    tier_1 = 0
    total_time_1 = 0
    tier_2 = 0
    total_time_2 = 0
    tier_3 = 0
    total_time_3 = 0
    tier_4 = 0
    total_time_4 = 0
    tier_5 = 0
    total_time_5 = 0
    tier_6 = 0
    total_time_6 = 0
    tier_7 = 0
    total_time_7 = 0
    tier_8 = 0
    total_time_8 = 0
    tier_9 = 0
    total_time_9 = 0
    tier_10 = 0
    total_time_10 = 0
    for i in range(0, len(get_scores)):
        if get_scores[i].score is None:
            pass
        else:
            if 0 <= get_scores[i].score < 1:
                tier_1 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_1 += time_spent_hours[0]

            elif 1 <= get_scores[i].score < 2:
                tier_2 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_2 += time_spent_hours[0]

            elif 2 <= get_scores[i].score < 3:
                tier_3 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_3 += time_spent_hours[0]

            elif 3 <= get_scores[i].score < 4:
                tier_4 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_4 += time_spent_hours[0]

            elif 4 <= get_scores[i].score < 5:
                tier_5 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_5 += time_spent_hours[0]

            elif 5 <= get_scores[i].score < 6:
                tier_6 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_6 += time_spent_hours[0]

            elif 6 <= get_scores[i].score < 7:
                tier_7 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_7 += time_spent_hours[0]

            elif 7 <= get_scores[i].score < 8:
                tier_8 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_8 += time_spent_hours[0]

            elif 8 <= get_scores[i].score < 9:
                tier_9 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_9 += time_spent_hours[0]

            elif 9 <= get_scores[i].score <= 10:
                tier_10 += 1

                duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration

                episodes_counter = 0
                time_spent_min = 0

                current_season = get_scores[i].current_season
                current_ep = get_scores[i].last_episode_watched

                for j in range(1, current_season):
                    ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id, season=j).first().episodes
                    episodes_counter += ep
                    time_spent_min += ep * duration

                time_spent_hours = divmod(time_spent_min, 60)
                total_time_10 += time_spent_hours[0]

    x = ['0-1', '1-2', '2-3', '3-4', '4-5', '5-6', '6-7', '7-8', '8-9', '9-10']
    y = [tier_1, tier_2, tier_3, tier_4, tier_5, tier_6, tier_7, tier_8, tier_9, tier_10]

    total_rated = tier_1+tier_2+tier_3+tier_4+tier_5+tier_6+tier_7+tier_8+tier_9+tier_10
    total_series = len(get_scores)
    try:
        pourcentage_series_rated = round((total_rated/total_series)*100, 2)
    except:
        pourcentage_series_rated = 0

    ################################ Rating vs time spent ##########################################

    y_2 = [total_time_1, total_time_2, total_time_3, total_time_4, total_time_5,
           total_time_6, total_time_7, total_time_8, total_time_9, total_time_10]

    total_time = get_total_time_spent(int(current_user.get_id()), ListType.SERIES)

    ################################ Rating vs Seasons count ##########################################

    list_all_seasons = []
    for i in range(0, len(get_scores)):
        duration = Series.query.filter_by(id=get_scores[i].series_id).first().episode_duration
        score = get_scores[i].score
        ep = SeriesEpisodesPerSeason.query.filter_by(series_id=get_scores[i].series_id).all()

        season_per_series = []
        for j in range(0, len(ep)):
            season_per_series.append(ep[j].episodes)


        list_all_seasons.append([len(season_per_series), score])

    x_2 = ["1-2", "3-4", "5-6", "7-8", "9-10", "11+"]

    tmp_1 = 0
    tmp_mean_score_1 = 0
    tmp_2 = 0
    tmp_mean_score_2 = 0
    tmp_3 = 0
    tmp_mean_score_3 = 0
    tmp_4 = 0
    tmp_mean_score_4 = 0
    tmp_5 = 0
    tmp_mean_score_5 = 0
    tmp_6 = 0
    tmp_mean_score_6 = 0
    for k in range(0, len(list_all_seasons)):
        if 1 <= list_all_seasons[k][0] <= 2:
            tmp_1 += 1
            if list_all_seasons[k][1] is None:
                pass
            else:
                tmp_mean_score_1 += list_all_seasons[k][1]
        elif 3 <= list_all_seasons[k][0] <= 4:
            tmp_2 += 1
            if list_all_seasons[k][1] is None:
                pass
            else:
                tmp_mean_score_2 += list_all_seasons[k][1]
        elif 5 <= list_all_seasons[k][0] <= 6:
            tmp_3 += 1
            if list_all_seasons[k][1] is None:
                pass
            else:
                tmp_mean_score_3 += list_all_seasons[k][1]
        elif 7 <= list_all_seasons[k][0] <= 8:
            tmp_4 += 1
            if list_all_seasons[k][1] is None:
                pass
            else:
                tmp_mean_score_4 += list_all_seasons[k][1]
        elif 9 <= list_all_seasons[k][0] <= 10:
            tmp_5 += 1
            if list_all_seasons[k][1] is None:
                pass
            else:
                tmp_mean_score_5 += list_all_seasons[k][1]
        elif list_all_seasons[k][0] > 10:
            tmp_6 += 1
            if list_all_seasons[k][1] is None:
                pass
            else:
                tmp_mean_score_6 += list_all_seasons[k][1]

    y_3 = [tmp_1, tmp_2, tmp_3, tmp_4, tmp_5, tmp_6]

    try:
        mean_1 = tmp_mean_score_1/tmp_1
    except:
        mean_1 = 0
    try:
        mean_2 = tmp_mean_score_2/tmp_2
    except:
        mean_2 = 0
    try:
        mean_3 = tmp_mean_score_3/tmp_3
    except:
        mean_3 = 0
    try:
        mean_4 = tmp_mean_score_4/tmp_4
    except:
        mean_4 = 0
    try:
        mean_5 = tmp_mean_score_5/tmp_5
    except:
        mean_5 = 0
    try:
        mean_6 = tmp_mean_score_6/tmp_6
    except:
        mean_6 = 0

    y_4 = [mean_1, mean_2, mean_3, mean_4, mean_5, mean_6]

    # import matplotlib.pyplot as plt
    #
    # fig, ax1 = plt.subplots()
    #
    # ax1.bar(x_2, y_3)
    # ax2 = ax1.twinx()
    # ax2.plot(x_2, y_4)
    #
    # fig.tight_layout()
    # plt.show()

    return [x, y]


def add_achievements():
    mypath = "D:\Bureau\MyLists_Misc\Achievements\Anime\JSON_Achievements\genre"
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for file in onlyfiles:
        with open("{}/{}".format(mypath, file), encoding='UTF-8', errors='ignore') as json_file:
            data = json.load(json_file)
            for i in range(0, len(data["achievements"])):
                achiev = AnimeAchievements(genre=str(data["requirement"]["genre"]),
                                           threshold=str(data["achievements"][i]["threshold"]),
                                           image_id=str(data["achievements"][i]["id"]),
                                           level=str(data["achievements"][i]["level"]),
                                           title=str(data["achievements"][i]["title"]),
                                           description=str(data["achievements"][i]["desc"]))
                db.session.add(achiev)
                db.session.commit()