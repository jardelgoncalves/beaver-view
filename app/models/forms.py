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


class RegrasQoSForm(FlaskForm):
    addr_src = StringField("addr_src")
    addr_dst = StringField("addr_dst")
    protocol = SelectField('tp', choices=[('UDP', 'UDP'),('TCP', 'TCP'),('ICMP', 'ICMP')], 
                                render_kw={"class": "browser-default"})
    port_src = StringField("port_src")
    port_dst = StringField("port_dst")
    dpid = StringField("dpid", validators=[InputRequired()])
    queue = StringField("queue", validators=[InputRequired()])

class QoSHostDockerForm(FlaskForm):
    ip        = StringField("ip", validators=[InputRequired()])
    iface     = StringField("iface", validators=[InputRequired()])
    rate      = StringField("rate", validators=[InputRequired()]) 
    latency   = StringField("latency", validators=[InputRequired()])
    burst     = StringField("burst", validators=[InputRequired()])
    peakrate  = StringField("peakrate", validators=[InputRequired()])
    minburst  = StringField("minburst", validators=[InputRequired()])

class PesquisarVethForm(FlaskForm):
    ip        = StringField("ip", validators=[InputRequired()])