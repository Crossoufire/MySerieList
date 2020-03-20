from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class AddFollowForm(FlaskForm):
    follow_to_add = StringField('Type a Username')
    submit_follow = SubmitField('follow')
