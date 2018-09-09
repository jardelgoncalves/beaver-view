# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, DataRequired, Email

class LoginForm(FlaskForm):
    email = StringField("email", validators=[InputRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])