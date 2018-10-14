# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, HiddenField
from wtforms.validators import InputRequired, DataRequired, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models.tables import Device

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

class AddRegrasForm(FlaskForm):
    dpid = StringField("dpid", validators=[InputRequired()])
    src = StringField("src")
    prefix_src = StringField("prefix_src", render_kw={"placeholder": "/24"})
    dst = StringField("dst")
    prefix_dst = StringField("prefix_dst", render_kw={"placeholder": "/24"})
    proto = StringField("proto")
    action = SelectField('action',choices=[('allow', 'ALLOW'),('deny', 'DENY')], render_kw={"class": "browser-default"})

class ConfigOVSDBForm(FlaskForm):
    ip = StringField('ip', validators=[InputRequired()])
    dpid = StringField("dpid", validators=[InputRequired()])

class ConfigQoSForm(FlaskForm):
    dpid = StringField("dpid", validators=[InputRequired()])
    port = StringField("port", validators=[InputRequired()])
    tp = SelectField('tp', choices=[('linux-htb', 'linux-htb')], render_kw={"class": "browser-default"})
    max_rate = StringField("max_rate", validators=[InputRequired()])


class UpdateQueueForm(FlaskForm):
    util = HiddenField("util", render_kw={"id": "todas_queue"})
