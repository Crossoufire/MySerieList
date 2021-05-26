import os
import imghdr
import secrets
from MyLists import app


def save_account_picture(form_picture, old_picture, profile=True):
    if imghdr.what(form_picture) == 'gif' or imghdr.what(form_picture) == 'jpeg' \
            or imghdr.what(form_picture) == 'png' or imghdr.what(form_picture) == 'tiff':
        file = form_picture
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(form_picture.filename)
        picture_fn = random_hex + f_ext
        if profile:
            file.save(os.path.join(app.root_path, 'static/profile_pics', picture_fn))
        else:
            file.save(os.path.join(app.root_path, 'static/background_pics', picture_fn))
    else:
        picture_fn = "default.jpg"
        app.logger.error('[SYSTEM] Invalid picture format: {}'.format(imghdr.what(form_picture)))

    try:
        if old_picture != 'default.jpg':
            if profile:
                os.remove(os.path.join(app.root_path, 'static/profile_pics', old_picture))
                app.logger.info('Settings updated: Removed the old picture: {}'.format(old_picture))
            else:
                os.remove(os.path.join(app.root_path, 'static/background_pics', old_picture))
                app.logger.info('Settings updated: Removed the old background: {}'.format(old_picture))
    except:
        pass

    return picture_fn
