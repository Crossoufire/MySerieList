from MyLists import bcrypt
from flask_wtf import FlaskForm
from MyLists.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import StringField, SubmitField, TextAreaField, DecimalField


class EditMediaData(FlaskForm):
    cover = FileField('Media cover', validators=[FileAllowed(['jpg', 'png'])])
    original_name = StringField('Original name')
    name = StringField('Name')
    directed_by = StringField('Directed by')
    created_by = StringField('Created by')
    airing_dates = StringField('Airing dates')
    release_date = StringField('Release date')
    production_status = StringField('Production status')
    genres = StringField('Genres')
    actors = StringField('Actors')
    duration = DecimalField('Duration (min)')
    origin_country = StringField('Origin country')
    original_language = StringField('Original language')
    newtorks = StringField('Newtorks')
    tagline = StringField('Tagline')
    homepage = StringField('Homepage')
    synopsis = TextAreaField('Synopsis')
    submit = SubmitField('Submit')
