# -*- coding: utf-8 -*-
import os

from app import app, db, login_manager
from flask import render_template, url_for, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user

from app.models.tables import User, DeviceTypes, Device, Link, Resource, HostDocker
from app.models.forms import LoginForm, TipoForm, RecursoForm, HostDockerForm
from werkzeug.utils import secure_filename

from time import ctime
from sqlalchemy import or_
from hashlib import sha224
from sqlalchemy.exc import IntegrityError


@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()


@app.route("/", methods=['GET', 'POST'])
def index():

    logout_user()
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid login")

    return render_template("index.html", form=form)


@app.route("/dashboard")
def dashboard():
    if current_user.is_authenticated:
        return render_template("dashboard.html")
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/topologia")
def topologia():
    if current_user.is_authenticated:
        d = Device.query.all()
        nodes = []
        for device in d:
            nodes.append({"id":device.dpid, "label":device.mac, "group":0})

        edges = []
        l = Link.query.all()
        for device in l:
            edges.append({"from":device.dpid_src, "to":device.dpid_dst})

        
        print edges, nodes
        return render_template("topologia.html", nodes=nodes, edges=edges)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/dispositivos")
def dispositivos():
    if current_user.is_authenticated:
        devices = Device.query.all()
        types = DeviceTypes.query.all()
        return render_template("dispositivos/index.html", devices=devices,types=types)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/dispositivos/adicionar_tipo", methods=['GET', 'POST'])
def adicionar_tipo():
    if current_user.is_authenticated:
        form = TipoForm()
        if form.validate_on_submit():
            photo = form.photo.data
            name = form.name.data
            hsh = sha224(ctime()).hexdigest()
            filename = "%s.png" %hsh

            td = DeviceTypes(name, filename)
            db.session.add(td)
            db.session.commit()

            photo.save(os.path.join(
                os.getcwd(), 'app/static/img/components', filename
            ))
            flash("added successfully")

        return render_template("dispositivos/add_tipo.html", form=form)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/dispositivos/adicionar_dispositivo",  methods=['GET', 'POST'])
def adicionar_dispositivo():
    if current_user.is_authenticated:
        form = HostDockerForm()
        if form.validate_on_submit():
            types = DeviceTypes.query.all()
            id_type = None
            for tipo in types:
                if "DOCKER" in tipo.name.upper():
                    id_type = tipo.id
            
            if id_type != None:
                host = HostDocker(form.name.data,form.user.data,form.password.data,
                                  form.ip.data,id_type,form.bridge_docker.data)
                db.session.add(host)
                db.session.commit()
                flash("Added successfully")
            else:
                flash("Host not added, please add the device type Docker.")

        return render_template("dispositivos/add_dispositivo.html", form=form)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/dispositivos/remover_dispositivo")
def remover_dispositivo():
    if current_user.is_authenticated:
        devices = Device.query.all()
        types = DeviceTypes.query.all()
        return render_template("dispositivos/rm_dispositivo.html", devices=devices,types=types)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))

@app.route("/configuracao/remover_dispositivo/apagar/", defaults={'id': None})
@app.route("/configuracao/remover_dispositivo/apagar/<id>")
def apagar_dispositivo(id):
    if current_user.is_authenticated:
        dispositivo = Device.query.filter_by(id=int(id)).first()
        if id != None or id != "":
            db.session.delete(dispositivo)
            db.session.commit()
            l1 = Link.query.filter_by(dpid_src=dispositivo.dpid).all()
            l2 = Link.query.filter_by(dpid_dst=dispositivo.dpid).all()

            if len(l1) > 0:
                for link in l1:
                    db.session.delete(link)
                    db.session.commit()
            if len(l2) > 0:
                for link in l2:
                    db.session.delete(link)
                    db.session.commit()

            flash("Device deleted.")
            return redirect(url_for("dispositivos"))
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/configuracao")
def configuracao():
    if current_user.is_authenticated:
        resources = Resource.query.all()
        return render_template("configuracao/index.html",resources=resources)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/configuracao/add_recurso", methods=['GET', 'POST'])
def add_recursos():
    form = RecursoForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            try:
                i = Resource(form.name.data, form.url.data, form.pid.data)
                db.session.add(i)
                db.session.commit()
                flash("added successfully")
            except IntegrityError:
                flash("PID duplicate, no inserted.")
        return render_template("configuracao/add_recurso.html", form=form)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))

@app.route("/configuracao/recurso/apagar/", defaults={'id': None})
@app.route("/configuracao/recurso/apagar/<id>")
def apagar_recurso(id):
    if current_user.is_authenticated:
        resource = Resource.query.filter_by(id=int(id)).first()
        if id != None or id != "":
            db.session.delete(resource)
            db.session.commit()
            flash("Resource deleted.")
        return redirect("configuracao")
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/configuracao/edit/", defaults={'id': None})
@app.route("/configuracao/edit/<id>", methods=['GET', 'POST'])
def edit_recurso(id):
    if current_user.is_authenticated:
        form = RecursoForm()
        resource = Resource.query.filter_by(id=int(id)).first()
        if id != None or id != "":
            if form.validate_on_submit():
                resource.name = form.name.data
                resource.url = form.url.data
                resource.pid = form.pid.data
                try:
                    db.session.add(resource)
                    db.session.commit()
                    flash("Resource updated.")
                except IntegrityError:
                    flash("PID duplicate, no inserted.")

            return render_template("configuracao/edit_config.html", form=form, resource=resource)
        else:
            return redirect("configuracao")
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/configuracao/recursos")
def configuracao_recursos():
    if current_user.is_authenticated:
        return render_template("configuracao/edit_config.html")
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
