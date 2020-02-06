from datetime import datetime
from MyLists.models import User, HomePage
from MyLists import current_app, bcrypt, db
from MyLists.auth.functions import send_register_email, send_reset_email
from flask_login import login_user, current_user, logout_user, login_required
from flask import Blueprint, flash, request, redirect, url_for, abort, render_template
from MyLists.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm


bp = Blueprint('auth', __name__)


@bp.route("/", methods=['GET', 'POST'])
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
            app.logger.info('[{}] Logged in'.format(user.id))
            flash("You're now logged in. Welcome {0}".format(user.username), "success")
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                if user.homepage != HomePage.ACCOUNT or user.homepage != HomePage.HALL_OF_FAME:
                    return redirect(url_for('main.mymedialist', media_list=user.homepage.value,
                                            user_name=current_user.username))
                elif user.homepage == HomePage.ACCOUNT:
                    return redirect(url_for('profile.account', user_name=current_user.username))
                elif user.homepage == HomePage.HALL_OF_FAME:
                    return redirect(url_for('profile.hall_of_fame'))
                else:
                    abort(404)
        else:
            flash('Login Failed. Please check Username and Password', 'warning')
    if register_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(register_form.register_password.data).decode('utf-8')
        user = User(username=register_form.register_username.data,
                    email=register_form.register_email.data,
                    password=hashed_password,
                    registered_on=datetime.utcnow())
        db.session.add(user)
        db.session.commit()
        app.logger.info('[{}] New account registration : username = {}, email = {}'
                        .format(user.id, register_form.register_username.data, register_form.register_email.data))
        if send_register_email(user):
            flash('Your account has been created. Check your e-mail address to activate your account!', 'info')
            return redirect(url_for('auth.home'))
        else:
            app.logger.error('[SYSTEM] Error while sending the registration email to {}'.format(user.email))
            abort(500)
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user.homepage != HomePage.ACCOUNT or user.homepage != HomePage.HALL_OF_FAME:
            return redirect(url_for('main.mymedialist', media_list=user.homepage.value,
                                    user_name=current_user.username))
        elif user.homepage == HomePage.ACCOUNT:
            return redirect(url_for('profile.account', user_name=current_user.username))
        elif user.homepage == HomePage.HALL_OF_FAME:
            return redirect(url_for('profile.hall_of_fame'))
        else:
            abort(404)

    return render_template('home.html',
                           login_form=login_form,
                           register_form=register_form)


@bp.route("/logout", methods=['GET'])
@login_required
def logout():
    app.logger.info('[{}] Logged out'.format(current_user.id))
    logout_user()

    return redirect(url_for('auth.home'))


@bp.route("/reset_password", methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordRequestForm()

    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if send_reset_email(user):
            app.logger.info('[{}] Reset password email sent'.format(user.id))
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('auth.home'))
        else:
            app.logger.error('[SYSTEM] Error while sending the reset password email to {}'.format(user.email))
            flash("There was an error while sending the reset password email. Please try again later.")
            return redirect(url_for('auth.home'))

    return render_template('reset_password.html', title='Reset Password', form=form)


@bp.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_passord_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        app.logger.info('[{}] Password reset via reset password email'.format(user.id))
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('auth.home'))

    return render_template('reset_passord_token.html', title='Reset Password', form=form)


@bp.route("/register_account/<token>", methods=['GET'])
def register_account_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('auth.home'))

    user = User.verify_reset_token(token)
    if user is None or user.active:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('auth.reset_password'))

    user.active = True
    user.activated_on = datetime.utcnow()
    db.session.commit()
    app.logger.info('[{}] Account activated'.format(user.id))
    flash('Your account has been activated.', 'success')

    return redirect(url_for('auth.home'))
