from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm, RecaptchaField
from flask_login import current_user

from MyLists import bcrypt
from MyLists.models import User


class RegistrationForm(FlaskForm):
    register_username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])
    register_email = StringField('Email', validators=[DataRequired(), Email()])
    register_password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    register_confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('register_password')])
    register_submit = SubmitField('Register')

    def validate_register_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError("This username is already taken. Please choose another one.")

    def validate_register_email(form, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError("This email already exist.")


class LoginForm(FlaskForm):
    login_username = StringField('Username', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    login_remember = BooleanField('Remember Me')
    login_submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Profile picture', validators=[FileAllowed(['jpg', 'png'])])
    movies_csv = FileField('Movies titles csv', validators=[FileAllowed(['csv'])])
    isprivate = BooleanField('Private mode')
    homepage = SelectField('Default homepage', choices=[('msl', 'MySeriesList'), ('mml', 'MyMoviesList'), ('mal', 'MyAnimesList'), ('mbl', 'MyBooksList'), ('acc', 'Account'), ('hof', 'Hall of Fame')])
    submit_account = SubmitField('Update account')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError("This username is already taken. Please choose another one.")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError("This email already exist.")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('Choose new password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm new password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

    def validate_current_password(self, current_password):
        user = User.query.filter_by(id=current_user.get_id()).first()
        if not bcrypt.check_password_hash(user.password, current_password.data):
            raise ValidationError("Incorrect current password")


class AddFriendForm(FlaskForm):
    friend_to_add = StringField('Type a Username')
    submit = SubmitField('Send friend request')

    def validate_friend_to_add(self, friend_to_add):
        if friend_to_add.data == current_user.username:
            raise ValidationError("You cannot add yourself")
        user = User.query.filter_by(username=friend_to_add.data).first()
        if user is None or user.id == 1:
            raise ValidationError("User not found")


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
