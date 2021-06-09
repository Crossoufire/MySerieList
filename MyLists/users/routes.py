import json
from MyLists import app, db
from flask_login import login_required, current_user
from flask import Blueprint, request, render_template
from MyLists.models import User, Ranks, Frames, Notifications, UserLastUpdate, RoleType, get_models_type, SeriesList, \
    Series

bp = Blueprint('users', __name__)


@bp.route('/account/<user_name>', methods=['GET', 'POST'])
@login_required
def account(user_name):
    # Check if the user can see the <media_list>
    user = current_user.check_autorization(user_name)

    # Get the user frame info
    user_frame_info = user.get_frame_info()

    if request.form.get('all_follows'):
        follows = user.followed.all()
        return render_template('account_all_follows.html', title='Follows', user=user,
                               frame=user_frame_info, follows=follows)
    elif request.form.get('all_followers'):
        followers = user.followers.all()
        return render_template('account_all_follows.html', title='Followers', user=user,
                               frame=user_frame_info, followers=True, follows=followers)
    elif request.form.get('all_history'):
        media_updates = user.get_last_updates(all_=True)
        return render_template('account_all_history.html', title='History', user=user,
                               frame=user_frame_info, media_updates=media_updates)

    # Update the account view count
    if current_user.role != RoleType.ADMIN and user.id != current_user.id:
        user.profile_views += 1

    # Get the user last updates
    user_updates = user.get_last_updates(all_=False)

    # Get follows last updates
    follows_updates = user.get_follows_updates()

    # Get the all media info in a dict for each media type
    list_models = get_models_type('List')
    media_dict, total_time, total_media, total_media_and_eps, total_score, total_mean_score = {}, 0, 0, 0, 0, 0
    qte_media_type = len(list_models)
    for model in list_models:
        media_count = model.get_media_count_by_status(user.id)
        media_count_score = model.get_media_count_by_score(user.id)
        media_levels = model.get_media_levels(user)
        media_score = model.get_media_score(user.id)
        media_time = getattr(user, f"time_spent_{model.__name__.replace('List', '').lower()}")
        media_total_eps = model.get_media_total_eps(user.id)
        media_favorites = model.get_favorites(user.id)

        # Each media_data dict contains all the data for one type of media
        media_data = {'time_spent_hour': round(media_time/60), 'time_spent_day': round(media_time/1440, 2),
                      'media_count': media_count, 'media_count_score': media_count_score,
                      'media_total_eps': media_total_eps, 'media_levels': media_levels, 'media_score': media_score,
                      'media_favorites': media_favorites}

        # Recover the total time for all media in hours
        total_time += media_data['time_spent_hour']

        # Recover total number of media
        total_media += media_data['media_count']['total']

        # Recover total number of media
        total_media_and_eps += media_data['media_total_eps']

        # Recover the total score of all media
        total_score += media_data['media_score']['scored_media']

        # Recover the total mean score of all media
        try:
            total_mean_score += media_data['media_score']['mean_score']
        except:
            qte_media_type -= 1

        media_dict[f"{model.__name__.replace('List', '').lower()}"] = media_data

    # Add global media info to the <media_dict>
    media_dict['total_spent_hour'] = total_time
    media_dict['total_media'] = total_media
    media_dict['total_media_and_eps'] = total_media_and_eps
    media_dict['total_score'] = total_score
    try:
        media_dict['total_mean_score'] = round(total_mean_score/qte_media_type, 2)
    except:
        media_dict['total_mean_score'] = '-'

    # Commit the changes
    db.session.commit()

    return render_template('account.html', title=user.username+"'s account", user=user, frame=user_frame_info,
                           user_updates=user_updates, follows_updates=follows_updates, media_data=media_dict)


@bp.route("/hall_of_fame", methods=['GET', 'POST'])
@login_required
def hall_of_fame():
    all_users = current_user.followed.all()
    all_users.append(current_user)
    models_type = get_models_type('List')

    all_users_data = []
    for user in all_users:
        user_data = {}
        frame = user.get_frame_info()

        user_data["id"] = user.id
        user_data["username"] = user.username
        user_data["profile_picture"] = user.image_file
        user_data["knowledge_frame"] = frame
        user_data["add_games"] = user.add_games

        user_data["current_user"] = False
        if user.id == current_user.id:
            user_data["current_user"] = True

        for model in models_type:
            user_data[f"{model.__name__.replace('List', '').lower()}_data"] = model.get_media_levels(user)

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
