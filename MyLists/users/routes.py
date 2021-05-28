import json
from MyLists import app, db
from flask_login import login_required, current_user
from flask import Blueprint, request, render_template
from MyLists.models import User, ListType, Ranks, Frames, Notifications

bp = Blueprint('users', __name__)


@bp.route('/account/<user_name>', methods=['GET', 'POST'])
@login_required
def account(user_name):
    # Check if the user can see the <media_list>
    user = current_user.check_autorization(user_name)

    # Recover the user frame info (level, image)
    user_frame_info = user.get_user_frame()

    if request.form.get('all_follows'):
        all_follows = user.get_all_follows()
        return render_template('account_all_follows.html', title='Follows', user=user, frame=user_frame_info,
                               all_follows=all_follows)
    elif request.form.get('all_followers'):
        all_follows = user.get_all_followers()
        return render_template('account_all_follows.html', title='Followers', user=user, frame=user_frame_info,
                               all_follows=all_follows, followers=True)
    elif request.form.get('all_history'):
        media_update = user.get_media_updates(all_=True)
        return render_template('account_all_history.html', title='History', user=user, frame=user_frame_info,
                               media_updates=media_update)

    # Recover media data
    media_data = get_media_data(user)

    # Recover follows data and last updates
    follows_list, follows_update_list = user.get_follows_data()

    # Recover the Favorites
    favorites = get_favorites(user.id)

    # Commit the changes
    db.session.commit()

    return render_template('account.html', title=user.username+"'s account", user=user, frame=user_frame_info,
                           favorites=favorites, media_data=media_data, follows_list=follows_list,
                           follows_update_list=follows_update_list)


@bp.route("/hall_of_fame", methods=['GET', 'POST'])
@login_required
def hall_of_fame():
    users = current_user.followed.all()
    users.append(current_user)

    all_users_data = []
    for user in users:
        series_level = user.get_media_levels(ListType.SERIES)
        anime_level = user.get_media_levels(ListType.ANIME)
        movies_level = user.get_media_levels(ListType.MOVIES)
        games_level = user.get_media_levels(ListType.GAMES)
        knowledge_frame = user.get_knowledge_frame()

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
        follow_condition = bool(json_data['follow_status'])
    except:
        return '', 400

    # Check if <follow> exist in <User> table
    user = User.query.filter_by(id=follow_id).first()
    if not user:
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
