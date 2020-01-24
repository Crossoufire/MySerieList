from MyLists import app
from flask import render_template, url_for


@app.errorhandler(400)
def error400(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', error_code=400, title='Error 400', image_error=image_error), 400


@app.errorhandler(403)
def error403(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', error_code=403, title='Error 403', image_error=image_error), 403


@app.errorhandler(404)
def error404(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', error_code=404, title='Error 404', image_error=image_error), 404


@app.errorhandler(410)
def error410(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', error_code=410, title='Error 410', image_error=image_error), 410


@app.errorhandler(413)
def error413(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', error_code=413, title='Error 413', image_error=image_error), 413


@app.errorhandler(500)
def error500(e):
    image_error = url_for('static', filename='img/error.jpg')
    return render_template('error.html', error_code=500, title='Error 500', image_error=image_error), 500
