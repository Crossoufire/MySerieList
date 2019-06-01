import json
import os
import platform
import secrets
import sys
import urllib
import time
import requests

from datetime import datetime
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

from MyLists import app, db, bcrypt, mail, config
from MyLists.admin_views import User
from MyLists.forms import RegistrationForm, LoginForm, UpdateAccountForm, SearchForm, ChangePasswordForm, \
    Add_FriendForm, ResetPasswordForm, RequestResetForm
from MyLists.models import Serie, List, Episodesperseason, Status, Genre, Network, Friend, Episodetimestamp

config.read('config.ini')
try:
    themoviedb_api_key = config['TheMovieDB']['api_key']
except:
    print("Config file error. Exit.")
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
        db.session.commit()


################################################### Anonymous pages ###################################################


@app.route("/", methods=['GET', 'POST'])
def home():
    login_form = LoginForm()
    register_form = RegistrationForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.login_username.data).first()
        if user and not user.active:
            app.logger.info('[{}] Connexion attempt while account not activated'.format(user.id))
            flash('Your Account is not activated', 'danger')
        elif user and bcrypt.check_password_hash(user.password, login_form.login_password.data):
            login_user(user, remember=login_form.login_remember.data)
            next_page = request.args.get('next')
            app.logger.info('[{}] Logged in'.format(user.id))
            flash("You're now logged in. Welcome {0}".format(login_form.login_username.data), "success")
            return redirect(next_page) if next_page else redirect(url_for('mylist'))
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
        return redirect(url_for('mylist'))
    else:
        home_header = url_for('static', filename='img/home_header.jpg')
        img1 = url_for('static', filename='img/home_img1.jpg')
        img2 = url_for('static', filename='img/home_img2_bis.jpg')
        return render_template('home.html', title='Home', login_form=login_form, register_form=register_form,
                               image_header=home_header, img1=img1, img2=img2)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('mylist'))
    form = RequestResetForm()
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
        return redirect(url_for('mylist'))
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
        return redirect(url_for('mylist'))

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

################################################# Authenticated pages #################################################


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
    form = Add_FriendForm()
    if form.validate_on_submit():
        if str(form.add_friend.data) == str(current_user.username):
            flash("You cannot add yourself.", 'info')
            return redirect(url_for('account'))
        add_friend(form.add_friend.data)

    # Profile picture
    image_file = url_for('static', filename='profile_pics/{0}'.format(current_user.image_file))

    # Friends list
    friends_list = Friend.query.filter_by(user_id=current_user.get_id()).all()
    friends_list_data = []
    for friend in friends_list:
        friend_data = {}
        friend_username = User.query.filter_by(id=friend.friend_id).first().username
        friend_data["username"] = friend_username
        friend_data["user_id"] = friend.friend_id
        friend_data["status"] = friend.status
        friends_list_data.append(friend_data)

    # Statistics
    nb_of_series = get_series_stats()
    total_time = get_total_time_spent(current_user.get_id())

    get_graphic_data = Episodetimestamp.query.filter_by(user_id=current_user.get_id()).all()

    datetime_user = []
    serie_ids = []
    for i in range(0, len(get_graphic_data)):
        tmp1 = get_graphic_data[i]
        tmp2 = [str(tmp1.timestamp.date().year), str(tmp1.timestamp.date().month), int(tmp1.serie_id)]
        datetime_user.append(tmp2)
        tmp3 = tmp1.serie_id
        if serie_ids.count(int(tmp3)) == 0:
            serie_ids.append(int(tmp3))
        else:
            pass

    for i in range(0, len(serie_ids)):
        duration_request = Serie.query.filter_by(id=serie_ids[i]).first()
        duration = int(duration_request.episode_duration) - 4
        for j in range(0, len(datetime_user)):
            if serie_ids[i] == datetime_user[j][2]:
                datetime_user[j].append(int(duration))
            else:
                pass

    year_now = str(datetime.now().year)

    january = 0
    february = 0
    march = 0
    april = 0
    may = 0
    june = 0
    july = 0
    august = 0
    september = 0
    october = 0
    november = 0
    december = 0
    january_time = 0
    february_time = 0
    march_time = 0
    april_time = 0
    may_time = 0
    june_time = 0
    july_time = 0
    august_time = 0
    september_time = 0
    october_time = 0
    november_time = 0
    december_time = 0
    for i in range(0, len(datetime_user)):
        if datetime_user[i][0] != year_now:
            pass
        else:
            if datetime_user[i][1] == '1':
                january += 1
                january_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '2':
                february += 1
                february_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '3':
                march += 1
                march_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '4':
                april += 1
                april_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '5':
                may += 1
                may_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '6':
                june += 1
                june_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '7':
                july += 1
                july_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '8':
                august += 1
                august_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '9':
                september += 1
                september_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '10':
                october += 1
                october_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '11':
                november += 1
                november_time += int(datetime_user[i][3])
            if datetime_user[i][1] == '12':
                december += 1
                december_time += int(datetime_user[i][3])

    nb_episodes_watched = [january, february, march, april, may, june, july, august, september, october, november, december]
    maxi_val = max(nb_episodes_watched) + 1

    time_episodes_watched = [
                            round(january_time / 60, 2),
                            round(february_time / 60, 2),
                            round(march_time / 60, 2),
                            round(april_time / 60, 2),
                            round(may_time / 60, 2),
                            round(june_time / 60, 2),
                            round(july_time / 60, 2),
                            round(august_time / 60, 2),
                            round(september_time / 60, 2),
                            round(october_time / 60, 2),
                            round(november_time / 60, 2),
                            round(december_time / 60, 2)]

    return render_template('account.html', title='Account', image_file=image_file, nb_of_series=nb_of_series,
                           time_spend_total=total_time,
                           friends_list_data=friends_list_data,
                           form=form,
                           values_nb=nb_episodes_watched,
                           values_time=time_episodes_watched,
                           maxival=maxi_val)


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
            flash("Your account have been updated ! ", 'success')
        else:
            if success:
                flash("Your account have been updated ! Please click on the link to validate your new email address.",
                      'success')
            else:
                flash("There was an error internal error. Please contact the administrator.", 'danger')

        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/{0}'.format(current_user.image_file))
    return render_template('account_settings.html', title='Settings', image_file=image_file, form=form,
                           value_privacy=is_private)


@app.route("/email_update/<token>", methods=['GET'])
def email_update_token(token):
    if current_user.is_anonymous:
        return redirect(url_for('home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))

    if str(user.id) != current_user.get_id():
        return redirect(url_for('mylist'))

    old_email = user.email
    user.email = user.transition_email
    user.transition_email = None
    db.session.commit()
    app.logger.info('[{}] Email successfully changed from {} to {}'.format(user.id, old_email, user.email))
    flash('Email successfully updated !', 'success')
    return redirect(url_for('mylist'))


@app.route('/private_mode', methods=['POST'])
@login_required
def private_data():
    image_error = url_for('static', filename='img/error.jpg')
    # TODO : get the actual value of the trigger
    try:
        json_data = request.get_json()
        triggered = json_data['private']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    user = User.query.filter_by(id=current_user.get_id()).first()
    is_private = user.private
    if is_private:
        user.private = False
    else:
        user.private = True
    db.session.commit()
    app.logger.info('[{}] Private mode updated'.format(user.id))
    return '', 204


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


@app.route("/accept", methods=['POST'])
@login_required
def accept_friend_request():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        friend_id = json_data['reponse']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    if type(friend_id) is not int:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

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
    return '', 204


@app.route("/decline", methods=['POST'])
@login_required
def decline_friend_request():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        decline_friend = json_data['reponse']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    if type(decline_friend) is not int:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if there is an actual pending request
    # Otherwise delete the pending request
    if not Friend.query.filter_by(user_id=current_user.get_id(), friend_id=decline_friend, status="pending").delete():
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    db.session.commit()

    if not Friend.query.filter_by(user_id=decline_friend, friend_id=current_user.get_id(), status="request").delete():
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400
    db.session.commit()
    app.logger.info('[{}] Friend request declined from user with ID {}'.format(current_user.get_id(), decline_friend))
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
    if type(friend_id) is not int:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the friend to delete is in the friend list
    if Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    Friend.query.filter_by(user_id=current_user.get_id(), friend_id=friend_id).delete()
    Friend.query.filter_by(user_id=friend_id, friend_id=current_user.get_id()).delete()
    db.session.commit()
    app.logger.info('[{}] Friend with ID {} deleted'.format(current_user.get_id(), friend_id))
    return '', 204


@app.route("/mylist", methods=['GET', 'POST'])
@login_required
def mylist():
    form = SearchForm()
    if form.validate_on_submit():
        add_serie(form.serie.data.strip())

    watching_list = List.query.filter_by(user_id=current_user.get_id(), status='WATCHING').all()
    completed_list = List.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').all()
    onhold_list = List.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').all()
    random_list = List.query.filter_by(user_id=current_user.get_id(), status='RANDOM').all()
    dropped_list = List.query.filter_by(user_id=current_user.get_id(), status='DROPPED').all()
    plantowatch_list = List.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').all()

    serie_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    serie_data = get_list_data(serie_list)
    return render_template('mylist.html', title='MyList', form=form, all_data=serie_data)


@app.route('/update_season', methods=['POST'])
@login_required
def update_season():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        season = json_data['season']
        serie_id = json_data['serie_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    if not (type(season) is int and type(serie_id) is int):
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Serie.query.filter_by(id=serie_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if List.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the season number is between 1 and <last_season>
    last_season = Episodesperseason.query.filter_by(serie_id=serie_id).order_by(
        Episodesperseason.season.desc()).first().season
    if season + 1 < 1 or season + 1 > last_season:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    update = List.query.filter_by(serie_id=serie_id, user_id=current_user.get_id()).first()

    old_season = update.current_season

    if old_season < season + 1:
        for i in range(old_season, season + 1):
            for j in range(1, Episodesperseason.query.filter_by(serie_id=serie_id, season=i).first().episodes + 1):
                if Episodetimestamp.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id, season=i,
                                                    episode=j).first() is None:
                    ep = Episodetimestamp(user_id=current_user.get_id(),
                                          serie_id=serie_id,
                                          season=i,
                                          episode=j,
                                          timestamp=datetime.utcnow())
                    db.session.add(ep)
        ep = Episodetimestamp(user_id=current_user.get_id(),
                              serie_id=serie_id,
                              season=season + 1,
                              episode=1,
                              timestamp=datetime.utcnow())
        db.session.add(ep)
        db.session.commit()

    elif old_season > season + 1:
        for i in range(season + 1, old_season + 1):
            Episodetimestamp.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id, season=i).delete()
        ep = Episodetimestamp(user_id=current_user.get_id(),
                              serie_id=serie_id,
                              season=season + 1,
                              episode=1,
                              timestamp=datetime.utcnow())
        db.session.add(ep)
        db.session.commit()

    update.current_season = season + 1
    update.last_episode_watched = 1
    db.session.commit()
    app.logger.info(
        '[{}] Season of the serie with ID {} updated to {}'.format(current_user.get_id(), serie_id, season + 1))
    return '', 204


@app.route('/update_episode', methods=['POST'])
@login_required
def update_episode():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        episode = json_data['episode']
        serie_id = json_data['serie_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    if not (type(episode) is int and type(serie_id) is int):
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Serie.query.filter_by(id=serie_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if List.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the episode number is between 1 and <last_episode>
    current_season = List.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id).first().current_season
    last_episode = Episodesperseason.query.filter_by(serie_id=serie_id, season=current_season).first().episodes
    if episode + 1 < 1 or episode + 1 > last_episode:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    update = List.query.filter_by(serie_id=serie_id, user_id=current_user.get_id()).first()
    old_last_episode_watched = update.last_episode_watched
    current_season = update.current_season

    if episode + 1 > old_last_episode_watched:
        for i in range(old_last_episode_watched + 1, episode + 2):
            ep = Episodetimestamp(user_id=current_user.get_id(),
                                  serie_id=serie_id,
                                  season=current_season,
                                  episode=i,
                                  timestamp=datetime.utcnow())
            db.session.add(ep)
        db.session.commit()
    elif episode + 1 < old_last_episode_watched:
        for i in range(episode + 2, old_last_episode_watched + 1):
            Episodetimestamp.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id, season=current_season,
                                             episode=i).delete()
        db.session.commit()

    update.last_episode_watched = episode + 1
    db.session.commit()

    app.logger.info(
        '[{}] Episode of the serie with ID {} updated to {}'.format(current_user.get_id(), serie_id, episode + 1))
    return '', 204


@app.route('/delete_serie', methods=['POST'])
@login_required
def delete_serie():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        serie_id = json_data['delete']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the inputs are digits
    if type(serie_id) is not int:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie exists
    if Serie.query.filter_by(id=serie_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is in the current user's list
    if List.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    List.query.filter_by(serie_id=serie_id, user_id=current_user.get_id()).delete()
    db.session.commit()

    Episodetimestamp.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id).delete()
    db.session.commit()

    app.logger.info('[{}] Serie with ID {} deleted'.format(current_user.get_id(), serie_id))
    return '', 204


@app.route('/change_serie_category', methods=['POST'])
@login_required
def change_serie_status():
    image_error = url_for('static', filename='img/error.jpg')
    try:
        json_data = request.get_json()
        serie_new_category = json_data['status']
        serie_id = json_data['serie_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    category_list = ["Watching", "Completed", "On Hold", "Random", "Dropped", "Plan to Watch"]
    if serie_new_category not in category_list:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    serie = List.query.filter_by(serie_id=serie_id, user_id=current_user.get_id()).first()
    if serie_new_category == 'Watching':
        serie.status = 'WATCHING'
    elif serie_new_category == 'Completed':
        serie.status = 'COMPLETED'
        # Set Season / Episode to max
        number_season = Episodesperseason.query.filter_by(serie_id=serie_id).count()
        for i in range(number_season):
            number_episode = Episodesperseason.query.filter_by(serie_id=serie_id, season=i+1).first().episodes
            for j in range(number_episode):
                if Episodetimestamp.query.filter_by(user_id=current_user.get_id(),
                                                    serie_id=serie_id,
                                                    season=i+1,
                                                    episode=j+1).first() is None:
                    ep = Episodetimestamp(user_id=current_user.get_id(),
                                          serie_id=serie_id,
                                          season=i+1,
                                          episode=j+1,
                                          timestamp=datetime.utcnow())
                    db.session.add(ep)
        serie.current_season = number_season
        serie.last_episode_watched = number_episode
        db.session.commit()
    elif serie_new_category == 'On Hold':
        serie.status = 'ON_HOLD'
    elif serie_new_category == 'Random':
        serie.status = 'RANDOM'
    elif serie_new_category == 'Dropped':
        serie.status = 'DROPPED'
    elif serie_new_category == 'Plan to Watch':
        serie.status = 'PLAN_TO_WATCH'
    db.session.commit()
    app.logger.info('[{}] Category of the serie with ID {} changed to {}'.format(current_user.get_id(), serie_id,
                                                                                 serie_new_category))
    return '', 204


@app.route('/refresh_single_serie', methods=['POST'])
@login_required
def refresh_single_serie():
    image_error = url_for('static', filename='img/error.jpg')

    try:
        json_data = request.get_json()
        serie_id = json_data['serie_id']
    except:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if the serie is currently in the user's list
    if List.query.filter_by(user_id=current_user.get_id(), serie_id=serie_id).first() is None:
        return render_template('error.html', error_code=400, title='Error', image_error=image_error), 400

    # Check if there is more than 30 min since the last update
    last_update = Serie.query.filter_by(id=serie_id).first().last_update
    time_delta = datetime.utcnow() - last_update
    if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
        refresh_serie_data(serie_id)

    return '', 204


@app.route('/refresh_all_series', methods=['POST'])
@login_required
def refresh_all_series():
    series = List.query.filter_by(user_id=current_user.get_id()).all()
    for serie in series:
        # Check if there is more than 30 min since the last update
        last_update = Serie.query.filter_by(id=serie.serie_id).first().last_update
        time_delta = datetime.utcnow() - last_update
        if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
            refresh_serie_data(serie.serie_id)
        else:
            pass
    return '', 204


@app.route("/user/<user_name>")
@login_required
def user_list(user_name):
    image_error = url_for('static', filename='img/error.jpg')
    user = User.query.filter_by(username=user_name).first()

    if user is None:
        return render_template('error.html', error_code=404, title='Error', image_error=image_error), 404

    if user and str(user.id) == current_user.get_id():
        return redirect(url_for('mylist'))

    friend = Friend.query.filter_by(user_id=current_user.get_id(), friend_id=user.id).first()

    if user.private:
        if current_user.get_id() == "1":
            pass
        elif friend is None or friend.status != "accepted":
            return redirect(url_for('anonymous'))

    if user.id == 1:
        return render_template('error.html', error_code=403, title='Error', image_error=image_error), 403

    watching_list = List.query.filter_by(user_id=user.id, status='WATCHING').all()
    completed_list = List.query.filter_by(user_id=user.id, status='COMPLETED').all()
    onhold_list = List.query.filter_by(user_id=user.id, status='ON_HOLD').all()
    random_list = List.query.filter_by(user_id=user.id, status='RANDOM').all()
    dropped_list = List.query.filter_by(user_id=user.id, status='DROPPED').all()
    plantowatch_list = List.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').all()

    serie_list = [watching_list, completed_list, onhold_list, random_list, dropped_list, plantowatch_list]
    serie_data = get_list_data(serie_list)
    return render_template('user_list.html', title='{}\'s list'.format(user.username), all_data=serie_data)


@app.route("/hall_of_fame")
@login_required
def hall_of_fame():
    # Get list of all users except admin
    users = User.query.filter(User.id >= "2").order_by(User.username.asc()).all()
    friends_of_current_user = Friend.query.filter_by(user_id=current_user.get_id()).all()
    friends_list = []
    for friend in friends_of_current_user:
        friends_list.append(friend.friend_id)

    all_user_data = []
    for user in users:
        watching = List.query.filter_by(user_id=user.id, status='WATCHING').count()
        completed = List.query.filter_by(user_id=user.id, status='COMPLETED').count()
        onhold = List.query.filter_by(user_id=user.id, status='ON_HOLD').count()
        random = List.query.filter_by(user_id=user.id, status='RANDOM').count()
        dropped = List.query.filter_by(user_id=user.id, status='DROPPED').count()
        plantowatch = List.query.filter_by(user_id=user.id, status='PLAN_TO_WATCH').count()

        total = watching + completed + onhold + random + dropped + plantowatch
        spent = get_total_time_spent(user.id)

        user_data = {"username": user.username,
                     "watching": watching,
                     "completed": completed,
                     "onhold": onhold,
                     "random": random,
                     "dropped": dropped,
                     "plantowatch": plantowatch,
                     "total": total,
                     "days": spent[0],
                     "episodes": spent[2]}

        if user.id in friends_list:
            user_data["isfriend"] = True
        else:
            user_data["isfriend"] = False

        if str(user.id) == current_user.get_id():
            user_data["isprivate"] = False
            user_data["iscurrentuser"] = True
        else:
            user_data["isprivate"] = user.private
            user_data["iscurrentuser"] = False

        all_user_data.append(user_data)
    return render_template("hall_of_fame.html", title='Hall of Fame', all_user_data=all_user_data)


@app.route("/anonymous")
@login_required
def anonymous():
    image_anonymous = url_for('static', filename='img/anonymous.jpg')
    return render_template("anonymous.html", title="Anonymous", image_anonymous=image_anonymous)


###################################################### Functions ######################################################


def get_list_data(serie_list):
    all_serie_data = []
    for category in serie_list:
        category_serie_data = []
        for serie in category:
            current_serie = {}
            # Cover of the serie and its name
            serie_data = Serie.query.filter_by(id=serie.serie_id).first()
            cover_url = url_for('static', filename="serie_covers/{}".format(serie_data.image_cover))
            current_serie["cover_url"] = cover_url
            current_serie["cover_id"] = current_serie["cover_url"][
                                        21:-4]  # /static/serie_covers/377d305d73a2689b.jpg -> 377d305d73a2689b

            # Serie meta data
            current_serie["serie_name"] = serie_data.name
            current_serie["serie_original_name"] = serie_data.original_name
            current_serie["serie_id"] = serie_data.id
            current_serie["first_air_date"] = serie_data.first_air_date
            current_serie["last_air_date"] = serie_data.last_air_date
            current_serie["homepage"] = serie_data.homepage
            current_serie["in_production"] = serie_data.in_production
            current_serie["created_by"] = serie_data.created_by
            current_serie["episode_duration"] = serie_data.episode_duration
            current_serie["total_seasons"] = serie_data.total_seasons
            current_serie["total_episodes"] = serie_data.total_episodes
            current_serie["origin_country"] = serie_data.origin_country
            current_serie["status"] = serie_data.status
            current_serie["synopsis"] = serie_data.synopsis

            # Can update
            time_delta = datetime.utcnow() - serie_data.last_update
            if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
                current_serie["can_update"] = True
            else:
                current_serie["can_update"] = False

            # Number of season and the number of ep of each season
            episodesperseason = Episodesperseason.query.filter_by(serie_id=serie_data.id).order_by(
                Episodesperseason.season.asc()).all()
            tmp = []
            for season in episodesperseason:
                tmp.append(season.episodes)
            current_serie["season_data"] = tmp

            current_serie["current_season"] = serie.current_season
            current_serie["last_episode_watched"] = serie.last_episode_watched

            category_serie_data.append(current_serie)
        category_serie_data = sorted(category_serie_data, key=lambda i: (i['serie_name']))
        all_serie_data.append(category_serie_data)
    return all_serie_data


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
        flash("Your friend request was sent", 'success')


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(subject='Password Reset Request',
                  sender=app.config['MAIL_USERNAME'],
                  recipients=[user.email])

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
                  recipients=[user.email])

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
                  recipients=[user.email])

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


def add_serie(serie_name):
    if serie_name == "":
        return redirect(url_for('mylist'))
    serie = Serie.query.filter(Serie.name.like("%{}%".format(serie_name))).first()
    if serie:  # Serie already in base
        # Check if the serie is already in the current's user list
        if List.query.filter_by(user_id=current_user.get_id(), serie_id=serie.id).first() is not None:
            return flash("The serie is already in your list", "warning")
        else:
            # Check if there is more than 30 min since the last update
            last_update = serie.last_update
            time_delta = datetime.utcnow() - last_update
            if time_delta.days > 0 or (time_delta.seconds / 1800 > 1):  # 30 min
                refresh_serie_data(serie.id)
            else:
                pass

            # Create a link between the user and the serie
            user_list = List(user_id=int(current_user.get_id()),
                             serie_id=serie.id,
                             current_season=1,
                             last_episode_watched=1,
                             status=Status.WATCHING)
            db.session.add(user_list)
            db.session.commit()
            app.logger.info('[{}] Added serie with the ID {} (already in base)'.format(current_user.get_id(), serie.id))

            # Add the serie in the Episodetimestamp table
            data = Episodetimestamp(user_id=int(current_user.get_id()),
                                    serie_id=serie.id,
                                    season=1,
                                    episode=1,
                                    timestamp=datetime.utcnow())
            db.session.add(data)
            db.session.commit()

            return redirect(url_for('mylist'))
    else:
        themoviedb_id = search_serie(serie_name)
        if themoviedb_id is None:
            return flash("Serie not found", "warning")

        serie_data = get_serie_data_from_api(themoviedb_id)
        if serie_data is None:
            return flash("There was a problem while getting serie's info. Please try again later.", "warning")

        cover_id = save_themoviedb_serie_cover(serie_data["poster_path"])
        if cover_id is None:
            return flash("There was a problem while getting serie's poster. Please try again later.", "warning")

        serie_id = add_serie_in_base(serie_data, cover_id)

        add_serie_to_user(serie_id, int(current_user.get_id()))

        app.logger.info('[{}] Added serie with the ID {} (new serie)'.format(current_user.get_id(), serie_id))

        return redirect(url_for('mylist'))


def search_serie(serie_name):
    while True:
        try:
            response = requests.get(
                "https://api.themoviedb.org/3/search/tv?api_key={0}&query={1}".format(themoviedb_api_key, serie_name))
        except:
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
            return None

        app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

        if response.headers["X-RateLimit-Remaining"] == "0":
            app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
            time.sleep(3)
            continue
        else:
            break

    data = json.loads(response.text)
    if data["total_results"] == 0:
        return None
    return data["results"][0]["id"]


def get_serie_data_from_api(themoviedb_id):
    while True:
        try:
            response = requests.get(
                "https://api.themoviedb.org/3/tv/{0}?api_key={1}".format(themoviedb_id, themoviedb_api_key))
        except:
            return None

        if response.status_code == 401:
            app.logger.error('[SYSTEM] Error requesting themoviedb API : invalid API key')
            return None

        app.logger.info('[SYSTEM] Number of requests available : {}'.format(response.headers["X-RateLimit-Remaining"]))

        if response.headers["X-RateLimit-Remaining"] == "0":
            app.logger.info('[SYSTEM] themoviedb maximum rate limit reached')
            time.sleep(3)
            continue
        else:
            break
    return json.loads(response.text)


def save_themoviedb_serie_cover(serie_cover_path):
    serie_cover_id = "{}.jpg".format(secrets.token_hex(8))
    if platform.system() == "Windows":
        local_covers_path = os.path.join(app.root_path, "static\serie_covers\\")
    else:  # Linux & macOS
        local_covers_path = os.path.join(app.root_path, "static/serie_covers/")
    try:
        urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{0}".format(serie_cover_path),
                                   "{}{}".format(local_covers_path, serie_cover_id))
    except:
        return None

    img = Image.open("{}{}".format(local_covers_path, serie_cover_id))
    img = img.resize((300, 450), Image.ANTIALIAS)
    img.save("{}{}".format(local_covers_path, serie_cover_id), quality=90)
    return serie_cover_id


def add_serie_in_base(serie_data, serie_cover_id):
    serie = Serie.query.filter_by(themoviedb_id=serie_data["id"]).first()
    if serie is not None:
        return serie.id

    name = serie_data["name"]
    original_name = serie_data["original_name"]
    first_air_date = serie_data["first_air_date"]
    last_air_date = serie_data["last_air_date"]
    homepage = serie_data["homepage"]
    in_production = serie_data["in_production"]
    total_seasons = serie_data["number_of_seasons"]
    total_episodes = serie_data["number_of_episodes"]
    status = serie_data["status"]
    vote_average = serie_data["vote_average"]
    vote_count = serie_data["vote_count"]
    synopsis = serie_data["overview"]
    popularity = serie_data["popularity"]
    themoviedb_id = serie_data["id"]

    try:
        created_by = ""
        for person in serie_data["created_by"]:
            created_by = created_by + person["name"] + ", "
        if len(serie_data["created_by"]) > 0:
            created_by = created_by[:-2]
        else:
            created_by = None
    except:
        created_by = None

    try:
        episode_duration = serie_data["episode_run_time"][0]
    except:
        episode_duration = None

    try:
        origin_country = ""
        for country in serie_data["origin_country"]:
            origin_country = origin_country + country + ", "
        if len(serie_data["origin_country"]) > 0:
            origin_country = origin_country[:-2]
        else:
            origin_country = None
    except:
        origin_country = None

    # Check if there is a special season
    # We do not want to take it into account
    seasons_data = []
    if serie_data["seasons"][0]["season_number"] == 0:  # Special season
        for i in range(len(serie_data["seasons"])):
            try:
                seasons_data.append(serie_data["seasons"][i + 1])
            except:
                pass
    else:
        for i in range(len(serie_data["seasons"])):
            try:
                seasons_data.append(serie_data["seasons"][i])
            except:
                pass

    genres_data = []
    for i in range(len(serie_data["genres"])):
        try:
            genres_data.append(serie_data["genres"][i]["name"])
        except:
            pass

    networks_data = []
    for i in range(len(serie_data["networks"])):
        try:
            networks_data.append(serie_data["networks"][i]["name"])
        except:
            pass

    # Add the serie into the Serie table
    serie = Serie(name=name,
                  original_name=original_name,
                  image_cover=serie_cover_id,
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

    db.session.add(serie)
    db.session.commit()

    # Add the genres for each serie
    for genre_data in genres_data:
        genre = Genre(serie_id=serie.id,
                      genre=genre_data)
        db.session.add(genre)

    # Add the different networks for each serie
    for network_data in networks_data:
        networks = Network(serie_id=serie.id,
                           network=network_data)
        db.session.add(networks)

    # Add number of episodes for each season
    for season_data in seasons_data:
        season = Episodesperseason(serie_id=serie.id,
                                   season=season_data["season_number"],
                                   episodes=season_data["episode_count"])
        db.session.add(season)
    db.session.commit()
    return serie.id


def add_serie_to_user(serie_id, user_id):
    user_list = List(user_id=user_id,
                     serie_id=serie_id,
                     current_season=1,
                     last_episode_watched=1,
                     status=Status.WATCHING)
    db.session.add(user_list)
    db.session.commit()

    data = Episodetimestamp(user_id=user_id,
                            serie_id=serie_id,
                            season=1,
                            episode=1,
                            timestamp=datetime.utcnow())
    db.session.add(data)
    db.session.commit()


def get_series_stats():
    watching = List.query.filter_by(user_id=current_user.get_id(), status='WATCHING').count()
    completed = List.query.filter_by(user_id=current_user.get_id(), status='COMPLETED').count()
    onhold = List.query.filter_by(user_id=current_user.get_id(), status='ON_HOLD').count()
    random = List.query.filter_by(user_id=current_user.get_id(), status='RANDOM').count()
    dropped = List.query.filter_by(user_id=current_user.get_id(), status='DROPPED').count()
    plantowatch = List.query.filter_by(user_id=current_user.get_id(), status='PLAN_TO_WATCH').count()

    statistics = [watching, completed, onhold, random, dropped, plantowatch]
    return statistics


def get_total_time_spent(user_id):
    series_id_request = db.engine.execute(
        "SELECT serie_id, current_season, last_episode_watched, status FROM list WHERE user_id = {0} AND status != 'PLAN_TO_WATCH'".format(user_id))
    series_id = series_id_request.fetchall()

    series_duration = []
    for i in range(0, len(series_id)):
        tmp = series_id[i][0]
        series_duration_request = db.engine.execute("SELECT episode_duration FROM serie WHERE id = {}".format(tmp))
        series_duration.append(series_duration_request.first())

    series_episodes = []
    for i in range(0, len(series_duration)):
        tmp = series_id[i][0]
        series_episodes_request = db.engine.execute(
            "SELECT episodes FROM episodesperseason WHERE serie_id = {} order by season".format(tmp))
        series_episodes.append(series_episodes_request.fetchall())

    time_spend_per_serie = []
    episodes_watched_per_serie = []
    for i in range(0, len(series_id)):
        a = 0
        tmp = int(series_id[i][1])
        if tmp == 1:
            episodes_watched_per_serie.append(int(series_id[i][2]))
            a = (int(series_id[i][2]) * int(series_duration[i][0]))
            time_spend_per_serie.append(a)
        else:
            tmp = tmp - 1
            for j in range(0, tmp):
                a = a + int(series_episodes[i][j][0])
            episodes_watched_per_serie.append(a + int(series_id[i][2]))
            a = a * int(series_duration[i][0])
            a = a + int((series_id[i][2]) * int(series_duration[i][0]))
            time_spend_per_serie.append(a)

    episodes_watched_total = 0
    for l in range(len(episodes_watched_per_serie)):
        episodes_watched_total = episodes_watched_total + episodes_watched_per_serie[l]

    time_spend_total = 0
    for k in range(len(time_spend_per_serie)):
        time_spend_total = time_spend_total + time_spend_per_serie[k]

    time_correction = episodes_watched_total * 4
    time_spend_total_days = round((time_spend_total - time_correction)/(60*24), 1)
    time_spend_total_hours = round((time_spend_total - time_correction)/60, 1)

    return [time_spend_total_days, episodes_watched_total, time_spend_total_hours]


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


def refresh_serie_data(serie_id):
    serie = Serie.query.filter_by(id=serie_id).first()
    serie_data = get_serie_data_from_api(serie.themoviedb_id)

    if serie_data is None:
        return flash("There was an error while refreshing the serie. Please try again later.")

    name = serie_data["name"]
    original_name = serie_data["original_name"]
    first_air_date = serie_data["first_air_date"]
    last_air_date = serie_data["last_air_date"]
    homepage = serie_data["homepage"]
    in_production = serie_data["in_production"]
    total_seasons = serie_data["number_of_seasons"]
    total_episodes = serie_data["number_of_episodes"]
    status = serie_data["status"]
    vote_average = serie_data["vote_average"]
    vote_count = serie_data["vote_count"]
    synopsis = serie_data["overview"]
    popularity = serie_data["popularity"]
    serie_poster = serie_data["poster_path"]

    if platform.system() == "Windows":
        local_covers_path = os.path.join(app.root_path, "static\serie_covers\\")
    else:  # Linux & macOS
        local_covers_path = os.path.join(app.root_path, "static/serie_covers/")
    try:
        urllib.request.urlretrieve("http://image.tmdb.org/t/p/w300{0}".format(serie_poster),
                                   "{}{}".format(local_covers_path, serie.image_cover))
    except:
        return flash("There was an error while refreshing the serie. Please try again later.")

    img = Image.open(local_covers_path + serie.image_cover)
    img = img.resize((300, 450), Image.ANTIALIAS)
    img.save(local_covers_path + serie.image_cover, quality=90)

    try:
        created_by = ""
        for person in serie_data["created_by"]:
            created_by = created_by + person["name"] + ", "
        if len(serie_data["created_by"]) > 0:
            created_by = created_by[:-2]
        else:
            created_by = None
    except:
        created_by = None

    try:
        episode_duration = serie_data["episode_run_time"][0]
    except:
        episode_duration = None

    try:
        origin_country = ""
        for country in serie_data["origin_country"]:
            origin_country = origin_country + country + ", "
        if len(serie_data["origin_country"]) > 0:
            origin_country = origin_country[:-2]
        else:
            origin_country = None
    except:
        origin_country = None

    # Check if there is a special season
    # We do not want to take it into account
    seasons_data = []
    if serie_data["seasons"][0]["season_number"] == 0:  # Special season
        for i in range(len(serie_data["seasons"])):
            try:
                seasons_data.append(serie_data["seasons"][i + 1])
            except:
                pass
    else:
        for i in range(len(serie_data["seasons"])):
            try:
                seasons_data.append(serie_data["seasons"][i])
            except:
                pass

    # We get the genres from the API
    genres_data = []
    for i in range(len(serie_data["genres"])):
        genres_data.append(serie_data["genres"][i])

    # We get the networks from the API
    networks_data = []
    for i in range(len(serie_data["networks"])):
        networks_data.append(serie_data["networks"][i])

    # Update the serie
    serie.name = name
    serie.original_name = original_name
    serie.first_air_date = first_air_date
    serie.last_air_date = last_air_date
    serie.homepage = homepage
    serie.in_production = in_production
    serie.created_by = created_by
    serie.total_seasons = total_seasons
    serie.total_episodes = total_episodes
    serie.episode_duration = episode_duration
    serie.origin_country = origin_country
    serie.status = status
    serie.vote_average = vote_average
    serie.vote_count = vote_count
    serie.synopsis = synopsis
    serie.popularity = popularity
    serie.last_update = datetime.utcnow()

    # Update the number of seasons and episodes
    for season_data in seasons_data:
        season = Episodesperseason.query.filter_by(serie_id=serie_id, season=season_data["season_number"]).first()
        if season is None:
            season = Episodesperseason(serie_id=serie.id,
                                       season=season_data["season_number"],
                                       episodes=season_data["episode_count"])
            db.session.add(season)
        else:
            season.episodes = season_data["episode_count"]
    # TODO : refresh Networks and Genres
    db.session.commit()
    app.logger.info("[{}] Refreshed the serie with the ID {}".format(current_user.get_id(), serie_id))
