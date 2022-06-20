from flask_wtf import FlaskForm
from wtforms import Form, StringField, SubmitField, BooleanField
from wtforms.fields import PasswordField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")