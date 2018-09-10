# -*- coding: utf-8 -*-
from app import db


class User(db.Model):

    __tablename__ = "users"

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50))
    email = db.Column('email',db.String(100), unique=True)
    password = db.Column('password', db.String(100))

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True
    
    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<User %r>" % self.username

class DeviceTypes(db.Model):

    __tablename__ = "device_types"

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50))
    filename = db.Column('filename', db.String(50), unique=True)

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<User %r>" % self.name