from MyLists.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError


class RegistrationForm(FlaskForm):
    register_username = StringField('Username', validators=[DataRequired(), Length(min=3, max=15)])
    register_email = StringField('Email', validators=[DataRequired(), Email()])
    register_password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    register_confirm_password = PasswordField('Confirm Password',
                                              validators=[DataRequired(), EqualTo('register_password')])
    register_submit = SubmitField('Register')

    def validate_register_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            raise ValidationError("This username is already taken. Please choose another one.")

    def validate_register_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user is not None:
            raise ValidationError("This email already exist.")


class LoginForm(FlaskForm):
    login_username = StringField('Username', validators=[DataRequired()])
    login_password = PasswordField('Password', validators=[DataRequired()])
    login_remember = BooleanField('Remember Me')
    login_submit = SubmitField('Login')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
