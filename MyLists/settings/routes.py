from MyLists import db, app, bcrypt
from MyLists.models import HomePage, User
from flask_login import login_required, current_user
from MyLists.settings.forms import UpdateAccountForm, ChangePasswordForm
from flask import Blueprint, flash, request, render_template, redirect, url_for
from MyLists.settings.functions import send_email_update_email, save_profile_picture


bp = Blueprint('settings', __name__)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    settings_form = UpdateAccountForm()
    password_form = ChangePasswordForm()

    # Account settings form
    if settings_form.submit_account.data and settings_form.validate():
        if settings_form.biography.data:
            current_user.biography = settings_form.biography.data
            db.session.commit()
            app.logger.info('[{}] Settings updated: Biography updated'.format(current_user.id))
        elif settings_form.biography.data == "":
            current_user.biography = None
            db.session.commit()
            app.logger.info('[{}] Settings updated: Biography updated'.format(current_user.id))
        if settings_form.picture.data:
            picture_file = save_profile_picture(settings_form.picture.data)
            old_picture_file = current_user.image_file
            current_user.image_file = picture_file
            db.session.commit()
            app.logger.info('[{}] Settings updated: old picture file = {}, new picture file = {}'
                            .format(current_user.id, old_picture_file, current_user.image_file))
        if settings_form.username.data != current_user.username:
            old_username = current_user.username
            current_user.username = settings_form.username.data
            db.session.commit()
            app.logger.info('[{}] Settings updated: old username = {}, new username = {}'
                            .format(current_user.id, old_username, current_user.username))
        if settings_form.isprivate.data != current_user.private:
            old_value = current_user.private
            current_user.private = settings_form.isprivate.data
            db.session.commit()
            app.logger.info('[{}] Settings updated: old private mode = {}, new private mode = {}'
                            .format(current_user.id, old_value, settings_form.isprivate.data))

        old_value = current_user.homepage
        if settings_form.homepage.data == "msl":
            current_user.homepage = HomePage.MYSERIESLIST
        elif settings_form.homepage.data == "mml":
            current_user.homepage = HomePage.MYMOVIESLIST
        elif settings_form.homepage.data == "mal":
            current_user.homepage = HomePage.MYANIMELIST
        elif settings_form.homepage.data == "acc":
            current_user.homepage = HomePage.ACCOUNT
        elif settings_form.homepage.data == "hof":
            current_user.homepage = HomePage.HALL_OF_FAME

        db.session.commit()
        app.logger.info('[{}] Settings updated: old homepage = {}, new homepage = {}'
                        .format(current_user.id, old_value, settings_form.homepage.data))

        email_changed = False
        if settings_form.email.data != current_user.email:
            old_email = current_user.email
            current_user.transition_email = settings_form.email.data
            db.session.commit()
            app.logger.info('[{}] Settings updated : old email = {}, new email = {}'
                            .format(current_user.id, old_email, current_user.transition_email))
            email_changed = True
            if send_email_update_email(current_user):
                success = True
            else:
                success = False
                app.logger.error('[SYSTEM] Error while sending the email update email to {}'.format(current_user.email))
        if not email_changed:
            flash("Your account has been updated! ", 'success')
        else:
            if success:
                flash("Your account has been updated! Please click on the link to validate your new email address.",
                      'success')
            else:
                flash("There was an error internal error. Please contact the administrator.", 'danger')
    elif request.method == 'GET':
        settings_form.biography.data = current_user.biography
        settings_form.username.data = current_user.username
        settings_form.email.data = current_user.email
        settings_form.isprivate.data = current_user.private

        if current_user.homepage == HomePage.MYSERIESLIST:
            settings_form.homepage.data = "msl"
        elif current_user.homepage == HomePage.MYMOVIESLIST:
            settings_form.homepage.data = "mml"
        elif current_user.homepage == HomePage.MYANIMELIST:
            settings_form.homepage.data = "mal"
        elif current_user.homepage == HomePage.ACCOUNT:
            settings_form.homepage.data = "acc"
        elif current_user.homepage == HomePage.HALL_OF_FAME:
            settings_form.homepage.data = "hof"

    # Password change form
    if password_form.submit_password.data and password_form.validate():
        hashed_password = bcrypt.generate_password_hash(password_form.confirm_new_password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        app.logger.info('[{}] Password updated'.format(current_user.id))
        flash('Your password has been successfully updated!', 'success')

    return render_template('settings.html',
                           title='Your settings',
                           settings_form=settings_form,
                           password_form=password_form)


@bp.route("/email_update/<token>", methods=['GET'])
@login_required
def email_update_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('home'))

    if user.id != current_user.id:
        return redirect(url_for('home'))

    old_email = user.email
    user.email = user.transition_email
    user.transition_email = None
    db.session.commit()
    app.logger.info('[{}] Email successfully changed from {} to {}'.format(user.id, old_email, user.email))
    flash('Email successfully updated!', 'success')

    return redirect(url_for('home'))
