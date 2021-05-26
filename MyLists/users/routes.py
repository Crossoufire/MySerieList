import json
from MyLists import app, db
from flask_login import login_required, current_user
from flask import Blueprint, request, render_template
from MyLists.models import User, ListType, Ranks, Frames, UserLastUpdate, Notifications
from MyLists.users.functions import get_media_data, get_media_levels, get_follows_data, get_updates, \
    get_user_data, get_favorites, get_all_follows_data, get_all_followers_data, get_header_data

bp = Blueprint('users', __name__)


@bp.route('/account/<user_name>', methods=['GET', 'POST'])
@login_required
def account(user_name):
    # Check if the user can see the <media_list>
    user = current_user.check_autorization(user_name)

    # Recover the account header data
    header_data = get_header_data(user)

    if request.form.get('all_follows'):
        all_follows = get_all_follows_data(user)
        return render_template('account_all_follows.html', title='Follows', all_follows=all_follows,
                               header_data=header_data)
    elif request.form.get('all_history'):
        updates = UserLastUpdate.query.filter_by(user_id=user.id).order_by(UserLastUpdate.date.desc()).all()
        media_update = get_updates(updates)
        return render_template('account_all_history.html', title='History', media_updates=media_update,
                               header_data=header_data)
    elif request.form.get('who_follows_you'):
        all_follows = get_all_followers_data(user)
        return render_template('account_all_follows.html', title='Followers', all_follows=all_follows,
                               header_data=header_data, followers=True)

    # Recover user data
    user_data = get_user_data(user)

    # Recover media data
    media_data = get_media_data(user)

    # Recover follows data and last updates
    follows_list, follows_update_list = get_follows_data(user)

    # Recover the Favorites
    favorites = get_favorites(user.id)

    # Commit the changes
    db.session.commit()

    return render_template('account.html', title=user.username+"'s account", header_data=header_data,
                           user_data=user_data, favorites=favorites, media_data=media_data, follows_list=follows_list,
                           follows_update_list=follows_update_list, user=user)


@bp.route("/hall_of_fame", methods=['GET', 'POST'])
@login_required
def hall_of_fame():
    users = current_user.followed.all()
    users.append(current_user)

    all_users_data = []
    for user in users:
        series_level = get_media_levels(user, ListType.SERIES)
        anime_level = get_media_levels(user, ListType.ANIME)
        movies_level = get_media_levels(user, ListType.MOVIES)
        games_level = get_media_levels(user, ListType.GAMES)
        knowledge_frame = Frames.get_knowledge_frame(user)

        user_data = {"id": user.id,
                     "username": user.username,
                     "profile_picture": user.image_file,
                     "series_data": series_level,
                     "anime_data": anime_level,
                     "movies_data": movies_level,
                     "games_data": games_level,
                     'knowledge_frame': knowledge_frame,
                     'current_user': False,
                     'add_games': user.add_games}

        if user.id == current_user.id:
            user_data["current_user"] = True

        all_users_data.append(user_data)

    return render_template("hall_of_fame.html", title='Hall of Fame', all_data=all_users_data)


@bp.route("/level_grade_data", methods=['GET'])
@login_required
def level_grade_data():
    ranks = Ranks.get_levels()
    return render_template('level_grade_data.html', title='Level grade data', data=ranks)


@bp.route("/knowledge_frame_data", methods=['GET'])
@login_required
def knowledge_frame_data():
    ranks = Frames.query.all()
    return render_template('knowledge_grade_data.html', title='Knowledge frame data', data=ranks)


# --- AJAX Methods ---------------------------------------------------------------------------------------------


@bp.route("/follow_status", methods=['POST'])
@login_required
def follow_status():
    try:
        json_data = request.get_json()
        follow_id = int(json_data['follow_id'])
        follow_condition = json_data['follow_status']
    except:
        return '', 400

    # Check if <follow> exist in <User> table and status is <bool>
    user = User.query.filter_by(id=follow_id).first()
    if not user or type(follow_condition) is not bool:
        return '', 400

    # Check the follow's status
    if follow_condition:
        current_user.add_follow(user)

        # Notify the followed user
        payload = {'username': current_user.username,
                   'message': '{} is following you.'.format(current_user.username)}
        app.logger.info('[{}] Follow the account with ID {}'.format(current_user.id, follow_id))
    else:
        # Remove the follow
        current_user.remove_follow(user)

        # Notify the followed user
        payload = {'username': current_user.username,
                   'message': '{} stopped following you.'.format(current_user.username)}
        app.logger.info('[{}] Unfollowed the account with ID {} '.format(current_user.id, follow_id))

    notif = Notifications(user_id=user.id, payload_json=json.dumps(payload))
    db.session.add(notif)
    db.session.commit()

    return '', 204
