from MyLists import app, db
from MyLists.models import User
from MyLists.account.forms import AddFollowForm
from flask_login import login_required, current_user
from flask import Blueprint, abort, url_for, flash, redirect, request, render_template
from MyLists.account.functions import get_account_data, get_follows_full_last_update, get_follows_last_update, \
    get_user_last_update


bp = Blueprint('account', __name__)


@bp.route('/account/<user_name>', methods=['GET', 'POST'])
@login_required
def account(user_name):
    user = User.query.filter_by(username=user_name).first()

    # No account with this username and protection of the admin account
    if user is None or user.id == 1 and current_user.id != 1:
        abort(404)

    # Check if the account is private or in the follow list
    if current_user.id == user.id or current_user.id == 1:
        pass
    elif user.private and not current_user.is_following(user):
        abort(404)

    # Add follows form
    follow_form = AddFollowForm()
    if follow_form.submit_follow.data and follow_form.validate():
        follow_username = follow_form.follow_to_add.data
        follow = User.query.filter_by(username=follow_username).first()

        if follow is None or follow.id == 1:
            app.logger.info('[{}] Attempt to follow user {}'.format(current_user.id, follow_username))
            flash('Sorry, this user does not exist', 'warning')
            return redirect(url_for('account.account', user_name=user_name, message='follows'))

        if current_user.id == follow.id:
            flash("You cannot follow yourself", 'warning')
            return redirect(url_for('account.account', user_name=user_name, message='follows'))

        current_user.add_follow(follow)
        db.session.commit()

        app.logger.info('[{}] is following the user with ID {}'.format(current_user.id, follow.id))
        flash("You are now following: {}.".format(follow.username), 'success')

        return redirect(url_for('account.account', user_name=user_name, message='follows'))

    # Recover account data
    account_data = get_account_data(user, user_name)

    # Recover the last updates of your follows for the follow TAB
    last_updates = get_follows_full_last_update(user)

    # Recover the last updates of the follows for the overview TAB
    if user.id == current_user.id:
        overview_updates = get_follows_last_update(user)
    else:
        overview_updates = get_user_last_update(user.id)

    # Reload on the specified TAB
    message_tab = request.args.get("message")
    if message_tab is None:
        message_tab = 'overview'

    return render_template('account.html',
                           title="{}'s account".format(user.username),
                           data=account_data,
                           follow_form=follow_form,
                           user_id=str(user.id),
                           user_name=user_name,
                           message_tab=message_tab,
                           last_updates=last_updates,
                           overview_updates=overview_updates,
                           user_biography=user.biography)