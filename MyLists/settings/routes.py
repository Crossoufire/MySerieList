import pandas as pd
from MyLists.models import User
from MyLists import db, app, bcrypt
from flask_login import login_required, current_user
from MyLists.settings.functions import send_email_update_email, save_account_picture
from MyLists.settings.forms import UpdateAccountForm, ChangePasswordForm, ImportListForm
from flask import Blueprint, flash, request, render_template, redirect, url_for, jsonify

bp = Blueprint('settings', __name__)


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    import_form = ImportListForm()
    settings_form = UpdateAccountForm()
    password_form = ChangePasswordForm()

    # if import_form.submit.data and import_form.validate():
    #     if import_form.csv_list.data:
    #         if current_user.get_task_in_progress('import_list'):
    #             flash('An import task is already in progress', 'warning')
    #         else:
    #             try:
    #                 csv_data = pd.read_csv(import_form.csv_list.data, index_col='Type')
    #                 current_user.launch_task('import_list', 'Importing List...', csv_data)
    #                 db.session.commit()
    #             except:
    #                 flash("Your file couldn't be processed. Please check your file or contact an admin.", 'warning')
    #         return redirect(url_for('users.account', user_name=current_user.username))
    if settings_form.submit_account.data and settings_form.validate():
        if settings_form.picture.data:
            old_picture_file = current_user.image_file
            current_user.image_file = save_account_picture(settings_form.picture.data, old_picture_file)
            app.logger.info('[{}] Settings updated: Old picture file = {}. New picture file = {}'
                            .format(current_user.id, old_picture_file, current_user.image_file))
        if settings_form.back_picture.data:
            old_background_picture = current_user.background_image
            current_user.background_image = save_account_picture(settings_form.back_picture.data,
                                                                 old_background_picture, profile=False)
            app.logger.info('[{}] Settings updated: Old background picture = {}. New background picture = {}'
                            .format(current_user.id, old_background_picture, current_user.background_image))
        if settings_form.username.data.strip() != current_user.username:
            old_username = current_user.username
            current_user.username = settings_form.username.data.strip()
            app.logger.info('[{}] Settings updated: Old username = {}. New username = {}'
                            .format(current_user.id, old_username, current_user.username))
        if settings_form.isprivate.data != current_user.private:
            old_value = current_user.private
            current_user.private = settings_form.isprivate.data
            app.logger.info('[{}] Settings updated: Old private mode = {}. New private mode = {}'
                            .format(current_user.id, old_value, settings_form.isprivate.data))
        if settings_form.add_games.data != current_user.add_games:
            old_value = current_user.add_games
            current_user.add_games = settings_form.add_games.data
            app.logger.info('[{}] Settings updated: Old games value = {}. New games mode = {}'
                            .format(current_user.id, old_value, settings_form.add_games.data))
        if settings_form.email.data != current_user.email:
            old_email = current_user.email
            current_user.transition_email = settings_form.email.data
            app.logger.info('[{}] Settings updated : Old email = {}. New email = {}'
                            .format(current_user.id, old_email, current_user.transition_email))
            try:
                send_email_update_email(current_user)
                flash("Your account has been updated! Please click on the link to validate your new email address.",
                      'success')
            except Exception as e:
                flash("There was an error. Please contact an admin.", 'warning')
                app.logger.error('[SYSTEM] Error: {}. Sending the email update to {}'.format(e, current_user.email))
        else:
            flash("Your settings has been updated!", 'success')
        db.session.commit()
    elif password_form.submit_password.data and password_form.validate():
        hashed_password = bcrypt.generate_password_hash(password_form.confirm_new_password.data).decode('utf-8')
        current_user.password = hashed_password

        db.session.commit()
        app.logger.info('[{}] Password updated'.format(current_user.id))
        flash('Your password has been successfully updated!', 'success')

    settings_form.username.data = current_user.username
    settings_form.email.data = current_user.email
    settings_form.isprivate.data = current_user.private
    settings_form.add_games.data = current_user.add_games

    back_pic = False
    pic = False
    if request.args.get('from') == 'back_pic':
        back_pic = True
    elif request.args.get('from') == 'profile_pic':
        pic = True

    return render_template('settings.html', title='Your settings', settings_form=settings_form,
                           password_form=password_form, import_form=import_form, back_pic=back_pic, pic=pic)


@bp.route("/email_update/<token>", methods=['GET'])
@login_required
def email_update_token(token):
    user = User.verify_token(token)

    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.home'))

    if user.id != current_user.id:
        return redirect(url_for('auth.home'))

    old_email = user.email
    user.email = user.transition_email
    user.transition_email = None

    db.session.commit()
    app.logger.info('[{}] Email successfully changed from {} to {}'.format(user.id, old_email, user.email))
    flash('Email successfully updated!', 'success')

    return redirect(url_for('auth.home'))


# --- AJAX Methods -----------------------------------------------------------------------------------------------


@bp.route('/progress_import', methods=['POST'])
@login_required
def progress_import():
    try:
        request.get_json()
    except:
        return '', 400

    task = current_user.get_task_in_progress('import_list')
    if task:
        progress = {'progress': round(task.get_progress(), 2)}
    else:
        progress = {'progress': 100}

    return jsonify(progress=progress), 200
