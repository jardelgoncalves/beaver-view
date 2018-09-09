# -*- coding: utf-8 -*-
from app import app, db, login_manager
from flask import render_template, url_for, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user

from app.models.tables import User
from app.models.forms import LoginForm


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
            return redirect( url_for("dashboard") )
        else:
            flash("Invalid login")

    return render_template("index.html", form=form)


@app.route("/dashboard")
def dashboard():
    if current_user.is_authenticated:
        return render_template("dashboard.html")
    else:
        flash("Restricted area for registered users.")
        return redirect( url_for("index") )


@app.route("/topologia")
def topologia():
    if current_user.is_authenticated:
        return render_template("topologia.html")
    else:
        flash("Restricted area for registered users.")
        return redirect( url_for("index") )

@app.route("/logout")
def logout():
    logout_user()
    return redirect( url_for("index") )