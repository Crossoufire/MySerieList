from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm, RecaptchaField
from flask_login import current_user
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
            raise ValidationError("That Username is already taken. Please choose another one.")

    def validate_register_email(form, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError("That email already exist.")


class LoginForm(FlaskForm):
    login_username = StringField('Username', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    login_remember = BooleanField('Remember Me')
    login_submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError("That Username is already taken. Please choose another one.")

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError("That email already exist.")


class ChangePasswordForm(FlaskForm):
    actual_password = PasswordField('Actual Password', validators=[DataRequired()])
    new_password = PasswordField('Choose New Password', validators=[DataRequired(), Length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')


class AddFriendForm(FlaskForm):
    add_friend = StringField('Type a Username')
    submit = SubmitField('Send')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
