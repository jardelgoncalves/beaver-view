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
    name = db.Column('name', db.String(50), unique=True)
    filename = db.Column('filename', db.String(150), unique=True)

    def __init__(self, name, filename):
        self.name = name
        self.filename = filename

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<Device Type %r>" % self.name

class Device(db.Model):
    __tablename__ = "devices"

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    device_type_id = db.Column('device_type_id', db.Integer)
    dpid = db.Column('dpid', db.String(50), unique=True)
    mac = db.Column('mac', db.String(50), unique=True)

    def __init__(self, device_type_id, dpid, mac):
        self.device_type_id = device_type_id
        self.dpid = dpid
        self.mac = mac

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<Device %r>" % self.mac


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    dpid_src = db.Column('dpid_src', db.String(50))
    dpid_dst = db.Column('dpid_dst', db.String(50))

    def get_id(self):
        return unicode(self.id)


class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50))
    url = db.Column('url', db.String(200))
    pid = db.Column('pid', db.Integer, unique=True)

    def __init__(self, name,url,pid):
        self.name = name
        self.url = url
        self.pid = pid

    def get_id(self):
        return unicode(self.id)


class HostDocker(db.Model):
    __tablename__ = "hosts_docker"

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(50))
    user = db.Column('user', db.String(50))
    password = db.Column('password', db.String(100))
    ip = db.Column('ip', db.String(20))
    type_device_id = db.Column('type_device_id', db.String(80))
    bridge_docker = db.Column('bridge_docker', db.String(80))

    def __init__(self, name,user,password,ip, type_device_id, bridge_docker):
        self.name = name
        self.user = user
        self.password = password
        self.ip = ip
        self.type_device_id = type_device_id
        self.bridge_docker = bridge_docker

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<Host Docker %r>" % self.name