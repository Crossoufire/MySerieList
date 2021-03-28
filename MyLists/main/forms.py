from flask import request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, DataRequired
from wtforms import StringField, SubmitField, TextAreaField, IntegerField


class EditMediaData(FlaskForm):
    cover = FileField('Media cover', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    original_name = StringField('Original name')
    name = StringField('Name')
    directed_by = StringField('Directed by')
    created_by = StringField('Created by')
    first_air_date = StringField('First air date')
    last_air_date = StringField('Last air date')
    release_date = StringField('Release date')
    production_status = StringField('Production status')
    genres = StringField('Genres')
    actors = StringField('Actors')
    duration = IntegerField('Duration (min)')
    origin_country = StringField('Origin country')
    original_language = StringField('Original language')
    networks = StringField('Newtorks')
    tagline = StringField('Tagline')
    homepage = StringField('Homepage')
    budget = StringField('Budget')
    revenue = StringField('Revenue')
    synopsis = TextAreaField('Synopsis')
    submit = SubmitField('Submit')


class MediaComment(FlaskForm):
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField('Search titles, actors...', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
