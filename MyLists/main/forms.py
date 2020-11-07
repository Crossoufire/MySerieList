from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
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


class EditGamesData(FlaskForm):
    cover = FileField('Game cover', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    name = StringField('Name')
    collection_name = StringField('Collection name')
    companies = StringField('Companies')
    platforms = StringField('Platforms')
    first_release_date = StringField('First release date')
    game_engine = StringField('Game engine')
    game_modes = StringField('Game modes')
    player_perspective = StringField('Player perspective')
    hltb_main_time = StringField('Main time')
    hltb_main_and_extra_time = StringField('Main + Extra time')
    hltb_total_complete_time = StringField('Complete time')
    genres = StringField('Genres')
    synopsis = TextAreaField('Summary')
    submit = SubmitField('Submit')


class MediaComment(FlaskForm):
    comment = TextAreaField('Comment')
    submit = SubmitField('Submit')
