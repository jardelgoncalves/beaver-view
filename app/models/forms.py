# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, DataRequired, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    email = StringField("email", validators=[InputRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])

class TipoForm(FlaskForm):
    name = StringField("name", validators=[InputRequired()])
    photo = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])