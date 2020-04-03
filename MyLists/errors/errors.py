from MyLists import app
from flask_login import current_user
from flask import render_template, url_for, Blueprint


bp = Blueprint('errors', __name__)


@bp.app_errorhandler(400)
def error400(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', title='Error 400', error_code=400, image_error=image_error), 400


@bp.app_errorhandler(403)
def error403(e):
    image_error = url_for('static', filename='img/error.jpg')
    app.logger.info('[{}] User ID tried the /admin URL'.format(current_user.id))
    return render_template('error.html', title='Error 403', error_code=403, image_error=image_error), 403


@bp.app_errorhandler(404)
def error404(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', title='Error 404', error_code=404, image_error=image_error), 404


@bp.app_errorhandler(410)
def error410(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', title='Error 410', error_code=410, image_error=image_error), 410


@bp.app_errorhandler(413)
def error413(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', title='Error 413', error_code=413, image_error=image_error), 413


@bp.app_errorhandler(500)
def error500(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', title='Error 500', error_code=500, image_error=image_error), 500
