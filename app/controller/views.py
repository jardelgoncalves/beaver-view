# -*- coding: utf-8 -*-
import os, requests, json

from app import app, db, login_manager
from flask import render_template, url_for, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user

from app.models.tables import User, DeviceTypes, Device, Link, Resource, HostDocker
from app.models.forms import LoginForm, TipoForm, RecursoForm, HostDockerForm, AddRegrasForm
from app.models.forms import ConfigOVSDBForm, ConfigQoSForm, UpdateQueueForm, RegrasQoSForm
from app.models.forms import QoSHostDockerForm, PesquisarVethForm
from werkzeug.utils import secure_filename
from time import ctime
from sqlalchemy import or_
from hashlib import sha224

from app.models.Obj import RegrasFirewall, applyRegras, RegrasQos, SwitchConfQoS, QoSQueue, Veths

from sqlalchemy.exc import IntegrityError
from requests.exceptions import ConnectionError


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
        vet = [1,2,23,65,75,32,11]
        return render_template("dashboard.html", vet=vet)
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

        return render_template("topologia.html", nodes=nodes, edges=edges)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/dispositivos")
def dispositivos():
    if current_user.is_authenticated:
        devices = Device.query.all()
        hosts = HostDocker.query.all()
        types = DeviceTypes.query.all()
        return render_template("dispositivos/index.html", devices=devices,types=types, hosts=hosts)
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
                print id_type
                host = HostDocker(form.name.data,form.user.data,form.password.data,
                                  form.ip.data,int(id_type),form.bridge_docker.data)
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
        hosts = HostDocker.query.all()
        types = DeviceTypes.query.all()
        return render_template("dispositivos/rm_dispositivo.html", devices=devices,types=types, hosts=hosts)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))

@app.route("/configuracao/remover_dispositivo/apagar/", defaults={'id': None}, methods=["GET", "DELETE"])
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
            return redirect(url_for("remover_dispositivo"))
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/configuracao/apagar_host_docker/apagar/", defaults={'id': None}, methods=["GET", "DELETE"])
@app.route("/configuracao/apagar_host_docker/apagar/<id>")
def apagar_host_docker(id):
    if current_user.is_authenticated:
        host = HostDocker.query.filter_by(id=int(id)).first()
        if id != None or id != "":
            db.session.delete(host)
            db.session.commit()
            flash("Host Docker deleted.")
            return redirect(url_for("remover_dispositivo"))
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

@app.route("/configuracao/recurso/apagar/", defaults={'id': None}, methods=["GET", "DELETE"])
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


@app.route("/firewall")
def firewall():
    if current_user.is_authenticated:
        enable = False
        rules = []
        try:
            denied = requests.get("http://localhost:8080/firewall/module/status")
            if denied.status_code == 200:
                count = 0
                for switch in json.loads(denied.text): 
                    if switch["status"] == 'disable':
                        count += 1
                if count == 0:
                    enable = True
            
            r = requests.get("http://localhost:8080/firewall/rules/all")
            
            if r.status_code == 200:
                for rule in json.loads(r.text):
                    src, dst, proto = "any","any","any"
                    if len(rule['access_control_list']) != 0:
                        for r in rule['access_control_list'][0]['rules']:
                            try:
                                src = r['nw_src']
                            except KeyError:
                                pass

                            try:
                                dst = r['nw_dst']
                            except KeyError:
                                pass

                            try:
                                proto = r['nw_proto']
                            except KeyError:
                                pass
                            
                            rf = RegrasFirewall(rule['switch_id'],
                                            r['rule_id'],
                                            src,
                                            dst,
                                            proto,
                                            r['actions'])
                            rules.append(rf)

        except ConnectionError:
            flash("the connection failed.")
        return render_template("firewall/index.html", enable=enable, rules=rules)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/firewall/add_regras", methods=['GET', 'POST'])
def add_regras_firewall():
    if current_user.is_authenticated:
        form = AddRegrasForm()
        if form.validate_on_submit():
            dpid = form.dpid.data
            pay = applyRegras(form.src.data, form.prefix_src.data, form.dst.data, 
                              form.prefix_dst.data, form.proto.data, form.action.data)
            
            put = requests.post("http://localhost:8080/firewall/rules/%s" %(dpid), data = json.dumps(pay))
            if put.status_code == 200:
                flash("Rule added.")
                return redirect("firewall")
            else:
                flash("An error has occurred. Rule not added.")

        return render_template("firewall/add_regras.html", form=form)

    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/firewall/apagar/", defaults={'id': None, 'dpid':None}, methods=["GET", "DELETE"])
@app.route("/firewall/apagar/<id>/<dpid>")
def apagar_regra_firewall(id, dpid):
    if current_user.is_authenticated:
        try:
            r = requests.delete("http://localhost:8080/firewall/rules/%s" %(dpid) ,data = json.dumps({"rule_id":str(id)}))
            if r.status_code == 200:
                flash("Rule successfully deleted.")
            else:
                flash("There was an error deleting rule.")
        except ConnectionError:
            flash("the connection failed.")
        
        return redirect(url_for('firewall'))
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))





@app.route("/firewall/habilitar")
def habilitar_firewall():
    if current_user.is_authenticated:
        try:
            r = requests.get("http://localhost:8080/firewall/module/status")
            if r.status_code == 200:
                device = json.loads(r.text)
                for switch in device:
                    resp = requests.put("http://localhost:8080/firewall/module/enable/%s" %switch["switch_id"])

        except ConnectionError:
            flash("the connection failed.")
        return redirect(url_for("firewall"))
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))

@app.route("/qos")
def qos():
    if current_user.is_authenticated:
        cont = 0
        rules_obj = []
        try:
            switches = requests.get("http://localhost:8080/v1.0/conf/switches")
            if switches.status_code == 200:
                cont = len(json.loads(switches.text))

            rules = requests.get("http://localhost:8080/qos/rules/all")
            if rules.status_code == 200:
                for rule in json.loads(rules.text):
                    if len(rule['command_result']) != 0:
                        #regra = RegrasQos("")
                        for cada in rule['command_result'][0]['qos']:
                            sw_id = rule['switch_id']
                            prio = cada['priority']
                            protocol = cada['nw_proto']
                            addr_dst = 'any'
                            port_dst = 'any'

                            addr_src = 'any'
                            port_src = 'any'
                            if 'tp_dst' in cada:
                                port_dst = cada['tp_dst']
                            if 'nw_dst' in cada:
                                addr_dst = cada['nw_dst']

                            if 'tp_src' in cada:
                                port_src = cada['tp_src']
                            if 'nw_src' in cada:
                                addr_src = cada['nw_src']

                            qos_id = cada['qos_id']
                            action = "queue %s" %cada['actions'][0]['queue']
                            regra = RegrasQos(sw_id, prio, protocol, qos_id, action, 
                                              addr_dst, port_dst, addr_src, port_src)
                            rules_obj.append(regra)
        except ConnectionError:
            pass
        return render_template("qos/index.html",cont=cont,rules=rules_obj)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/config")
def qos_config():
    if current_user.is_authenticated:
        switches = []

        r = requests.get("http://localhost:8080/qos/queue/all")
        if r.status_code == 200:
            for switch in json.loads(r.text):
                if switch["command_result"]['result'] != "failure":
                    dpid = switch["switch_id"]
                    for iface in switch["command_result"]['details']:
                        port = iface
                        obj = SwitchConfQoS(dpid,port)
                        switches.append(obj)

        return render_template("qos/config_qos.html", switches=switches)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/config/add", methods=["GET","POST"])
def config_qos_add():
    if current_user.is_authenticated:
        color = "white"
        form = ConfigQoSForm()

        if form.validate_on_submit():
            r = requests.post("http://localhost:8080/qos/queue/%s" %form.dpid.data, 
                            data=json.dumps({"port_name":form.port.data,
                                            "type":form.tp.data,
                                            "max_rate":form.max_rate.data}))
            if r.status_code == 200:
                flash ("configuration successfully added")
                return redirect(url_for("qos_config"))
            else:
                color="red"
                flash ("An error has occurred. Configuration not added")
        return render_template("qos/config_sw.html", form=form,color=color)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))



@app.route("/qos/config/apagar", defaults={'dpid': None})
@app.route("/qos/config/apagar/<dpid>")
def apagar_config_switch(dpid):
    if current_user.is_authenticated:
        r = requests.delete("http://localhost:8080/qos/queue/%s" %dpid)
        if r.status_code == 200:
            flash("Deleted setting.")
        else:
            flash("An error has occurred. Configuration not deleted")
        return redirect(url_for("qos_config"))
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/config/ver_queue", defaults={'dpid': None,'iface':None})
@app.route("/qos/config/ver_queue/<dpid>/<iface>")
def ver_config_queue(dpid,iface):
    if current_user.is_authenticated:
        queues = []
        r = requests.get("http://localhost:8080/qos/queue/%s" %dpid)
        if r.status_code == 200:
            response = json.loads(r.text)
            if response[0]['command_result']['result'] != "failure":
                for queue in response[0]['command_result']['details'][iface]:
                    q = QoSQueue(queue)
                    config = response[0]['command_result']['details'][iface][queue]['config']
                    if "max-rate" in config:
                        q.max_rate = config['max-rate']
                    if "min-rate" in config:
                        q.min_rate = config['min-rate']
                    queues.append(q)
        else:
            flash("There was an error loading the queues.")
        return render_template("qos/ver_queue.html", queues=queues,dpid=dpid, iface=iface)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))

@app.route("/qos/config/ver_queue/update", defaults={'dpid': None}, methods=["GET", "POST"])
@app.route("/qos/config/ver_queue/update/<dpid>", methods=["GET", "POST"])
def atualizar_queue(dpid):
    if current_user.is_authenticated:
        form = UpdateQueueForm()
        if form.validate_on_submit():
            response = json.loads(form.util.data)
            queues = {"queues":[]}
            for q in response["queue"]:
                if q['min_rate'] == '-' and q['max_rate'] != "-":
                    queues["queues"].append({"max_rate":"%s" %q['max_rate']})
                elif q['min_rate'] != '-' and q['max_rate'] == '-':
                    queues["queues"].append({"min_rate":"%s" %q['min_rate']})
                elif q['min_rate'] != '-' and q['max_rate'] != '-':
                    queues["queues"].append({"max_rate":"%s" %q['max_rate'], "min_rate":"%s" %q['min_rate']})
            if len(queues['queues']) > 0:
                r = requests.post("http://localhost:8080/qos/queue/%s" %dpid, data=json.dumps(queues))
                if r.status_code == 200:
                    flash("Queues added to the configuration.")
                    return redirect(url_for('qos_config'))
                else:
                    flash("Queues not added.")
        return render_template("qos/update.html", form=form)

    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))



@app.route("/qos/regra/apagar", defaults={'qos_id': None, 'sw_id':None})
@app.route("/qos/regra/apagar/<qos_id>/<sw_id>")
def apagar_regra_qos(qos_id,sw_id):
    if current_user.is_authenticated:
        try:
            r = requests.delete("http://localhost:8080/qos/rules/%s" %(sw_id) ,data = json.dumps({"qos_id":qos_id}))
            if r.status_code == 200:
                flash("Rule successfully deleted.")
            else:
                flash("There was an error deleting rule.")
        except ConnectionError:
            flash("the connection failed.")
        return redirect(url_for('qos'))
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))

@app.route("/qos/ovsdb", methods=['GET', 'PUT','POST'])
def qos_ovsdb():
    if current_user.is_authenticated:
        color="white"
        cont=0
        form = ConfigOVSDBForm()
        if form.validate_on_submit():
            ip = form.ip.data
            dpid = form.dpid.data
            try:
                switches = requests.get("http://localhost:8080/v1.0/conf/switches")
                if switches.status_code == 200:
                    cont = len(json.loads(switches.text))

                r = requests.put("http://localhost:8080/v1.0/conf/switches/%s/ovsdb_addr" %dpid, data='"tcp:%s:6634"' %ip)
                if r.status_code == 201:
                    switches = requests.get("http://localhost:8080/v1.0/conf/switches")
                    if switches.status_code == 200:
                        c = len(json.loads(switches.text))
                        if cont < c:
                            color = "green"
                            flash("ovsdb_addr was successfully defined.")
                        else:
                            print r.text
                            color = "red"
                            flash("An error occurred while setting ovsdb_addr.")
            except ConnectionError:
                color="red"
                flash("the connection failed.")
            
        return render_template("qos/ovsdb.html", form=form, color=color)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/add_regras", methods=['GET','POST'])
def add_qos_regras():
    if current_user.is_authenticated:
        form = RegrasQoSForm()
        match={"match":{},"actions":{}}
        if form.validate_on_submit():
            if form.addr_dst.data != '':
                match["match"]['nw_dst'] = form.addr_dst.data

            if form.port_dst.data != '':
                match["match"]['tp_dst'] = form.port_dst.data

            if form.addr_src.data != '':
                match["match"]['nw_src'] = form.addr_src.data

            if form.port_src.data != '':
                match["match"]['tp_src'] = form.port_src.data

            match["match"]["nw_proto"] = form.protocol.data
            match['actions']['queue'] = form.queue.data

            r = requests.post("http://localhost:8080/qos/rules/%s" %form.dpid.data, data=json.dumps(match))
            if r.status_code == 200:
                print "show"
            else:
                print "não"

        return render_template("qos/add_regras.html", form=form)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/qos_host_docker", methods=['GET','POST'])
def qos_host_docker():
    if current_user.is_authenticated:
        form = QoSHostDockerForm()
        if form.validate_on_submit():
            print form.latency.data
        return render_template("qos/docker_qos.html", form=form)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/qos_host_docker/pesquisar_veths", methods=['GET','POST'])
def pesquisar_veth():
    if current_user.is_authenticated:
        form = PesquisarVethForm()
        pesquisa=False
        veths=[]
        try:
            if form.validate_on_submit():
                r = requests.get("http://%s:5000/ifaces" %form.ip.data)
                if r.status_code == 200:
                    resp = json.loads(r.text)
                    pesquisa=True
                    for c in resp:
                        v = Veths(resp[c][0]["IP"],resp[c][0]["veth"])
                        veths.append(v)
                else:
                    print "deu merda"
        except ConnectionError:
            flash("Error while trying to connect to host.")
        return render_template("qos/veths.html", form=form, pesquisa=pesquisa,
                               veths=veths, tam=len(veths))
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
