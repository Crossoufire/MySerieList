from pathlib import Path
from MyLists import app, db
from MyLists.profile.forms import AddFollowForm
from MyLists.models import User, ListType, Ranks
from flask_login import login_required, current_user
from flask import Blueprint, abort, url_for, flash, redirect, request, render_template
from MyLists.profile.functions2 import get_follows_last_update, get_media_data, \
    get_level_and_grade, get_knowledge_grade, get_badges, get_follows_data, get_user_data


bp = Blueprint('profile', __name__)


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
            app.logger.info('[{}] Attempt to follow account {}'.format(current_user.id, follow_username))
            flash('Sorry, this account does not exist', 'warning')
            return redirect(url_for('profile.account', user_name=user_name, message='follows'))
        if current_user.id == follow.id:
            flash("You cannot follow yourself", 'warning')
            return redirect(url_for('profile.account', user_name=user_name, message='follows'))

        current_user.add_follow(follow)
        db.session.commit()

        app.logger.info('[{}] is following the account with ID {}'.format(current_user.id, follow.id))
        flash("You are now following: {}.".format(follow.username), 'success')
        return redirect(url_for('profile.account', user_name=user_name, message='follows'))

    # Recover user data
    user_data = get_user_data(user)

    # Recover media data
    series_data = get_media_data(user, ListType.SERIES)
    anime_data = get_media_data(user, ListType.ANIME)
    movies_data = get_media_data(user, ListType.MOVIES)

    # Recover follows data
    follows_data = get_follows_data(user)

    # Recover the last updates of your follows for the follow TAB
    # last_updates = get_follows_full_last_update(user)

    # Recover the last updates of the follows for the overview TAB
    overview_updates = get_follows_last_update(user)

    # Reload on the specified TAB
    message_tab = request.args.get("message") or None
    if not message_tab:
        message_tab = 'overview'

    return render_template('account.html',
                           title="{}'s account".format(user.username),
                           user_data=user_data,
                           series_data=series_data,
                           anime_data=anime_data,
                           movies_data=movies_data,
                           follow_form=follow_form,
                           follows_data=follows_data,
                           message_tab=message_tab,
                           overview_updates=overview_updates)


@app.route("/hall_of_fame", methods=['GET'])
@login_required
def hall_of_fame():
    users = User.query.filter(User.id >= "2", User.active == True).order_by(User.username.asc()).all()

    # Get the follows of the current account
    follows_list = []
    for follows in current_user.followed.all():
        follows_list.append(follows.id)

    all_users_data = []
    for user in users:
        series_level = get_level_and_grade(user, ListType.SERIES)
        anime_level = get_level_and_grade(user, ListType.ANIME)
        movies_level = get_level_and_grade(user, ListType.MOVIES)
        knowledge_grade = get_knowledge_grade(user)

        user_data = {"id": user.id,
                     "username": user.username,
                     "profile_picture": user.image_file,
                     "series_data": series_level,
                     "anime_data": anime_level,
                     "movies_data": movies_level,
                     'knowledge_grade': knowledge_grade}

        if user.id in follows_list:
            user_data["isfollowing"] = True
        else:
            user_data["isfollowing"] = False

        if user.id == current_user.id:
            user_data["isprivate"] = False
            user_data["iscurrentuser"] = True
        else:
            user_data["isprivate"] = user.private
            user_data["iscurrentuser"] = False

        all_users_data.append(user_data)

    return render_template("hall_of_fame.html", title='Hall of Fame', all_data=all_users_data)


@app.route("/badges/<user_name>", methods=['GET', 'POST'])
@login_required
def badges(user_name):
    user = User.query.filter_by(username=user_name).first()

    # No account with this username and protection of the admin account
    if user is None or user.id == 1 and current_user.id != 1:
        abort(404)

    # Check if the account is private or in the follow list
    if current_user.id == user.id or current_user.id == 1:
        pass
    elif user.private and not current_user.is_following(user):
        abort(404)

    user_badges = get_badges(user.id)[0]
    return render_template('badges.html', title="{}'s badges".format(user_name), user_badges=user_badges)


@app.route("/level_grade_data", methods=['GET'])
@login_required
def level_grade_data():
    ranks = Ranks.query.filter_by(type='media_rank\n').order_by(Ranks.level.asc()).all()

    return render_template('level_grade_data.html', title='Level grade data', data=ranks)


@app.route("/knowledge_grade_data", methods=['GET'])
@login_required
def knowledge_grade_data():
    ranks = Ranks.query.filter_by(type='knowledge_rank\n').order_by(Ranks.level.asc()).all()

    return render_template('knowledge_grade_data.html', title='Knowledge grade data', data=ranks)


@app.route("/follow_status", methods=['POST'])
@login_required
def follow_status():
    try:
        json_data = request.get_json()
        follow_id = int(json_data['follow_id'])
        follow_condition = json_data['follow_status']
    except:
        abort(400)

    # Check if the follow ID exist in the User database and status is boolean
    user = User.query.filter_by(id=follow_id).first()
    if user is None or type(follow_status) is not bool:
        abort(400)

    # Check the status of the follow
    if follow_condition:
        current_user.add_follow(user)
        db.session.commit()
        app.logger.info('[{}] Follow the account with ID {}'.format(current_user.id, follow_id))
    else:
        current_user.remove_follow(user)
        db.session.commit()
        app.logger.info('[{}] Follow with ID {} unfollowed'.format(current_user.id, follow_id))

    return '', 204
