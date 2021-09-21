from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, length


class RegisterUserForm(FlaskForm):
    """Form for registering new users"""

    username = StringField(
        "Username",
        validators=[InputRequired(), length(max=20)])

    password = PasswordField(
        "Password",
        validators=[InputRequired(), length(max=100)])

    email = StringField(
        "Email",
        validators=[InputRequired(), length(max=50), Email()])

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), length(max=30)])

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), length(max=30)])


class LoginUserForm(FlaskForm):
    """Form for login users"""

    username = StringField(
        "Username",
        validators=[InputRequired()])

    password = PasswordField(
        "Password",
        validators=[InputRequired()])


class LogoutUserForm(FlaskForm):
    """Used to add CSRF protection to logout POST"""
