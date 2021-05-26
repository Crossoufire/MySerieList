from MyLists import bcrypt
from flask_wtf import FlaskForm
from MyLists.models import User
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Profile picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'tiff'])])
    back_picture = FileField('Background picture', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'tiff'])])
    isprivate = BooleanField('Private mode')
    add_games = BooleanField('Activate the GamesList')
    submit_account = SubmitField('Update account')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError("This username is already taken. Please choose another one.")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError("This email already exist.")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('Choose new password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm new password', validators=[DataRequired(), EqualTo('new_password')])
    submit_password = SubmitField('Update Password')

    def validate_current_password(self, current_password):
        user = User.query.filter_by(id=current_user.get_id()).first()
        if not bcrypt.check_password_hash(user.password, current_password.data):
            raise ValidationError("Incorrect current password")


class ImportListForm(FlaskForm):
    csv_list = FileField('file.csv', validators=[FileAllowed(['csv'])])
    submit = SubmitField('Import')

