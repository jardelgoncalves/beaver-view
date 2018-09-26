# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import InputRequired, DataRequired, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed

class LoginForm(FlaskForm):
    email = StringField("email", validators=[InputRequired(), Email()])
    password = PasswordField("password", validators=[DataRequired()])

class TipoForm(FlaskForm):
    name = StringField("name", validators=[InputRequired()])
    photo = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

class RecursoForm(FlaskForm):
    name = StringField("name", validators=[InputRequired()])
    url = StringField("url", validators=[InputRequired()])
    pid = IntegerField("pid", validators=[InputRequired()])

class HostDockerForm(FlaskForm):
    name = StringField("name", validators=[InputRequired()])
    user = StringField("user", validators=[InputRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    ip = StringField("ip", validators=[InputRequired()])
    bridge_docker = StringField("bridge_docker", validators=[InputRequired()])