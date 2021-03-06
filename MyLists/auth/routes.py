from datetime import datetime
from MyLists.models import User
from MyLists import app, bcrypt, db
from MyLists.auth.emails import send_register_email, send_reset_email
from MyLists.auth.functions import check_if_auth
from flask_login import login_user, current_user, logout_user, login_required
from flask import Blueprint, flash, request, redirect, url_for, render_template
from MyLists.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm


bp = Blueprint('auth', __name__)


@bp.route("/", methods=['GET', 'POST'])
@check_if_auth
def home():
    login_form = LoginForm()
    register_form = RegistrationForm()

    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.login_username.data.strip()).first()
        if user and not user.active:
            app.logger.info('[INFO] - [{}] Connexion attempt while account not activated'.format(user.id))
            flash('Your account is not activated. Please check your email address to activate your account.', 'danger')
        elif user and bcrypt.check_password_hash(user.password, login_form.login_password.data):
            login_user(user, remember=login_form.login_remember.data)
            app.logger.info('[INFO] - [{}] Logged in.'.format(user.id))

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)

            return redirect(url_for('users.account', user_name=user.username))
        else:
            flash('Login failed. Please check username and password.', 'warning')
    elif register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.register_password.data).decode('utf-8')
        user = User(username=register_form.register_username.data.strip(),
                    email=register_form.register_email.data,
                    password=hashed_password,
                    registered_on=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        app.logger.info('[INFO] - [{}] New account registration: Username: {}, email: {}'
                        .format(user.id, register_form.register_username.data.strip(),
                                register_form.register_email.data))
        try:
            send_register_email(user)
            flash('Your account has been created. Check your e-mail address to activate your account.', 'info')
        except Exception as e:
            app.logger.error('[ERROR] - Sending register email to account [{}]: {}.'.format(user.id, e))
            flash("An error occured while sending your register e-mail. Admin were advised. Please try again later.")
        return redirect(url_for('auth.home'))

    return render_template('home.html', login_form=login_form, register_form=register_form)


@bp.route("/logout", methods=['GET'])
@login_required
def logout():
    app.logger.info('[INFO] - [{}] Logged out'.format(current_user.id))
    logout_user()

    return redirect(url_for('auth.home'))


@bp.route("/reset_password", methods=['GET', 'POST'])
@check_if_auth
def reset_password():
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        try:
            send_reset_email(user)
            app.logger.info('[INFO] - [{}] Reset password email sent'.format(user.id))
            flash('An email has been sent with the instructions to reset your password.', 'info')
        except Exception as e:
            app.logger.error('[ERROR] - Failed sending reset password email to [{}]: {}'.format(user.email, e))
            flash("An error occured while sending the reset password email. Admin were advised. "
                  "Please try again later.")
        return redirect(url_for('auth.home'))

    return render_template('reset_password.html', title='Reset password', form=form)


@bp.route("/reset_password/<token>", methods=['GET', 'POST'])
@check_if_auth
def reset_password_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('This is an invalid or an expired token.', 'warning')
        return redirect(url_for('auth.reset_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        app.logger.info('[INFO] - [{}] Password reset via the reset password email.'.format(user.id))
        flash('Your password has been updated! You are now able to log in.', 'success')
        return redirect(url_for('auth.home'))

    return render_template('reset_password_token.html', title='Reset password', form=form)


@bp.route("/register_account/<token>", methods=['GET'])
@check_if_auth
def register_account_token(token):
    user = User.verify_token(token)
    if not user or user.active:
        flash('This is an invalid or an expired token.', 'warning')
        return redirect(url_for('auth.reset_password'))

    user.active = True
    user.activated_on = datetime.utcnow()
    db.session.commit()
    app.logger.info('[INFO] - [{}] Account activated'.format(user.id))
    flash('Your account has been activated.', 'success')

    return redirect(url_for('auth.home'))
