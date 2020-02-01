import os
import platform

from MyLists import app, db
from MyLists.models import User
from MyLists.profile.forms import AddFollowForm
from flask_login import login_required, current_user
from flask import Blueprint, abort, url_for, flash, redirect, request, render_template
from MyLists.profile.functions import get_account_data, get_follows_full_last_update, get_follows_last_update, \
    get_user_last_update, get_level_and_grade, get_knowledge_grade, get_badges


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
        user_data = {"id": user.id,
                     "username": user.username,
                     "profile_picture": user.image_file}

        series_level = get_level_and_grade(user.time_spent_series)
        user_data["series_level"] = series_level["level"]
        user_data["series_percent"] = series_level["level_percent"]
        user_data["series_grade_id"] = series_level["grade_id"]
        user_data["series_grade_title"] = series_level["grade_title"]

        anime_level = get_level_and_grade(user.time_spent_anime)
        user_data["anime_level"] = anime_level["level"]
        user_data["anime_percent"] = anime_level["level_percent"]
        user_data["anime_grade_id"] = anime_level["grade_id"]
        user_data["anime_grade_title"] = anime_level["grade_title"]

        movies_level = get_level_and_grade(user.time_spent_movies)
        user_data["movies_level"] = movies_level["level"]
        user_data["movies_percent"] = movies_level["level_percent"]
        user_data["movies_grade_id"] = movies_level["grade_id"]
        user_data["movies_grade_title"] = movies_level["grade_title"]

        knowledge_level = int(series_level["level"] + anime_level["level"] + movies_level["level"])
        knowledge_grade = get_knowledge_grade(knowledge_level)
        user_data["knowledge_level"] = knowledge_level
        user_data["knowledge_grade_id"] = knowledge_grade["grade_id"]
        user_data["knowledge_grade_title"] = knowledge_grade["grade_title"]

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

    return render_template("hall_of_fame.html",
                           title='Hall of Fame',
                           all_data=all_users_data)


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
    elif user.private and current_user.is_following(user) is False:
        abort(404)

    user_badges = get_badges(user.id)[0]
    return render_template('badges.html',
                           title="{}'s badges".format(user_name),
                           user_badges=user_badges)


@app.route("/level_grade_data", methods=['GET'])
@login_required
def level_grade_data():
    all_ranks_list = []
    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\\csv_data\\levels_ranks.csv")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/csv_data/levels_ranks.csv")
    with open(path, "r") as fp:
        for line in fp:
            all_ranks_list.append(line.split(";"))

    all_ranks_list.pop(0)

    i, low, incr = [0, 0, 0]
    data = []
    while True:
        rank = all_ranks_list[i][2]
        if rank == 'ReachRank49':
            data.append(["ReachRank49", "Inheritor", [147, "+"], [(20*low)*(1+low), "+"],
                         [int(((20*low)*(1+low))/60), "+"]])
            break
        for j in range(i, len(all_ranks_list)):
            if str(rank) == all_ranks_list[j][2]:
                incr += 1
            else:
                data.append([rank, all_ranks_list[j-1][3], [low, incr-1],
                             [(20*low)*(1+low), ((20*incr)*(1+incr))-1],
                             [int(((20*low)*(1+low))/60), int((((20*incr)*(1+incr))-1)/60)]])
                i = j
                low = incr
                break

    return render_template('level_grade_data.html',
                           title='Level grade data',
                           data=data)


@app.route("/knowledge_grade_data", methods=['GET'])
@login_required
def knowledge_grade_data():
    all_knowledge_ranks_list = []
    if platform.system() == "Windows":
        path = os.path.join(app.root_path, "static\\csv_data\\knowledge_ranks.csv")
    else:  # Linux & macOS
        path = os.path.join(app.root_path, "static/csv_data/knowledge_ranks.csv")
    with open(path, "r") as fp:
        for line in fp:
            all_knowledge_ranks_list.append(line.split(";"))

    i, low, incr = [1, 1, 1]
    data = []
    while True:
        rank = all_knowledge_ranks_list[i][1]
        if i == 346:
            data.append(["Knowledge_Emperor_Grade_4", "Knowledge Emperor Grade 4", [345, "+"]])
            break
        for j in range(i, len(all_knowledge_ranks_list)):
            if str(rank) == all_knowledge_ranks_list[j][1]:
                incr += 1
            else:
                data.append([rank, all_knowledge_ranks_list[j - 1][2], [low-1, incr-2]])
                i = j
                low = incr
                break

    return render_template('knowledge_grade_data.html',
                           title='Knowledge grade data',
                           data=data)


@app.route("/follow_status", methods=['POST'])
@login_required
def follow_status():
    try:
        json_data = request.get_json()
        follow_id = int(json_data['follow_id'])
        status = json_data['follow_status']
    except:
        abort(400)

    # Check if the follow ID exist in the User database and status is boolean
    user = User.query.filter_by(id=follow_id).first()
    if user is None or type(status) is not bool:
        abort(400)

    # Check the status
    if status is True:
        current_user.add_follow(user)
        db.session.commit()
        app.logger.info('[{}] Follow the account with ID {}'.format(current_user.id, follow_id))
    else:
        current_user.remove_follow(user)
        db.session.commit()
        app.logger.info('[{}] Follow with ID {} unfollowed'.format(current_user.id, follow_id))

    return '', 204
