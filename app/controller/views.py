# -*- coding: utf-8 -*-
import os, requests, json

# Lib Objetos/Metodos do Flask
from app import app, db, login_manager
from flask import render_template, url_for, flash, redirect
from flask_login import login_user, login_required, logout_user, current_user

# Importando as libs de fomurlario
from app.models.tables import User, DeviceTypes, Device, Link, Resource, HostDocker, Stats
from app.models.forms import LoginForm, TipoForm, RecursoForm, HostDockerForm, AddRegrasForm
from app.models.forms import ConfigOVSDBForm, ConfigQoSForm, UpdateQueueForm, RegrasQoSForm
from app.models.forms import QoSHostDockerForm, PesquisarVethForm
from sqlalchemy import desc

# usado no uploads de arquivos
from werkzeug.utils import secure_filename
from time import ctime
from sqlalchemy import or_
from hashlib import sha224

# Objetos utilziados para facilitar a integracao com as paginas html
from app.models.Obj import RegrasFirewall, applyRegras, RegrasQos, SwitchConfQoS, QoSQueue
from app.models.Obj import Veths, RulesVeth

# Classes de errors
from sqlalchemy.exc import IntegrityError
from requests.exceptions import ConnectionError

# Usado para retornar o USUARIO armazenado na sessao
@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()


# Rota /index (pagina de login) da ferramenta
@app.route("/", methods=['GET', 'POST'])
def index():
    logout_user() # Caso tenha um usuario logado, ele terá sua seção encerrada

    form = LoginForm() # Intancia de um objeto de form para criar o formulario na pagina
    if form.validate_on_submit(): # Verifica se o usuario submeteu os dados do form

        user = User.query.filter_by(email=form.email.data).first() # Select no banco
        if user and user.password == form.password.data: # autenticacao do usuario
            login_user(user) # login do usuario
            return redirect(url_for("dashboard")) # redirecionamento para a dashboard da ferramenta
        else:
            flash("Invalid login") # mensagem de erro

    return render_template("index.html", form=form) # renderização da página index


# Rota /dashboard da ferramenta
@app.route("/dashboard")
def dashboard():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        datas = {}
        vet=[1212,12123]
        switches = Device.query.all()
        for sw in switches:
            datas[sw.dpid]={"RX":[],"TX":[]}
            data = Stats.query.filter_by(ip_dpid=sw.dpid).order_by(desc(Stats.date)).limit(15).all()
            for d in data:
                datas[sw.dpid]["RX"].append(d.rx)
                datas[sw.dpid]["TX"].append(d.tx)
        print datas
        return render_template("dashboard.html", datas=datas) # renderização da página dashboard
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /topologia da ferramenta
@app.route("/topologia")
def topologia():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        d = Device.query.all() # retorna todos os switches cadastrado no banco de dados
        nodes = [] # vetor para armazenar dados em registros sobre os switches
        for device in d: # percorre todos os switches
            nodes.append({"id":device.dpid, "label":device.mac, "group":0}) # adiciona os registros

        edges = [] # armazenar dpid dos switches e a quem ele esta conecado
        l = Link.query.all() # retorna todos os links no banco de dados
        for device in l: # percorre todos os dispositivos que possui links
            edges.append({"from":device.dpid_src, "to":device.dpid_dst}) # adiciona os registros

        return render_template("topologia.html", nodes=nodes, edges=edges) # renderiza a página com as informações 
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /dispositivo da ferramenta
@app.route("/dispositivos")
def dispositivos():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        devices = Device.query.all() # retorna todos os switches cadastrado no banco de dados
        hosts = HostDocker.query.all() # retorna todos os Host Docker cadastrado no banco de dados
        types = DeviceTypes.query.all() # retorna todos os tipos de dispositivos cadastrado no banco de dados
        return render_template("dispositivos/index.html", 
                         devices=devices,types=types, hosts=hosts) # renderiza a página com as informações
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /dispositivo/ver_tipos da ferramenta
@app.route("/dispositivos/ver_tipos")
def ver_tipos():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        types = DeviceTypes.query.all() # retorna todos os tipos de dispositivos cadastrado no banco de dados
        return render_template("dispositivos/ver_tipos.html",types=types)
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


@app.route("/dispositivos/ver_tipos/apagar/", defaults={'id': None}, methods=["GET", "DELETE"])
@app.route("/dispositivos/ver_tipos/apagar/<id>")
def apagar_tipo(id):
    if current_user.is_authenticated: # verifica a autenticação do usuario
        tps = DeviceTypes.query.filter_by(id=int(id)).first() # faz um select no banco
        if id != None or id != "": # verifica se o id não é None ou vazio:
            # Deleta o dispositivo do banco e faz commit
            photo = os.path.join(
                      os.getcwd(), 'app/static/img/components', str(tps.filename)
                    )
            db.session.delete(tps)
            db.session.commit()
            os.remove(photo)
            flash("Device Type deleted.")
            return redirect(url_for("ver_tipos"))
        else:
            flash("Device type not deleted.")
            return redirect(url_for("ver_tipos"))
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)

# Rota /dispositivo/adicionar_tipo da ferramenta (Adicionar tipo de dispositivo)
@app.route("/dispositivos/adicionar_tipo", methods=['GET', 'POST'])
def adicionar_tipo(): 
    if current_user.is_authenticated:      # verifica a autenticação do usuario
        form = TipoForm()      # Intancia de um objeto de form para criar o formulario na pagina
        if form.validate_on_submit():      # Verifica se o usuario submeteu os dados do form
            try:
                # Pega os dados passado no form
                photo = form.photo.data 
                name = form.name.data
                # Cria um hash para salvar a foto com base no momento do upload
                hsh = sha224(ctime()).hexdigest()
                filename = "%s.png" %hsh
                # Instancia um objeto DeviceType passando o nome e a foto
                td = DeviceTypes(name, filename)
                # Adiciona no banco e faz commit
                db.session.add(td)
                db.session.commit()

                # Salva a foto na pasta components dentro de /static/img
                photo.save(os.path.join(
                    os.getcwd(), 'app/static/img/components', filename
                ))
                flash("added successfully")    # Mensagem de sucesso
                return redirect(url_for("ver_tipos"))
            except IntegrityError:
                flash("This TYPE OF DEVICE already exists.")

        return render_template("dispositivos/add_tipo.html", form=form)     # Renderiza a página com o formulario
    else:
        flash("Restricted area for registered users.")       # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index"))       # redirecionamento a página index (login)


# Rota /dispositivo/adicionar_dispositivo da ferramenta (adicionar host docker)
@app.route("/dispositivos/adicionar_dispositivo",  methods=['GET', 'POST'])
def adicionar_dispositivo(): 
    if current_user.is_authenticated:    # verifica a autenticação do usuario
        form = HostDockerForm()         # Intancia de um objeto de form para criar o formulario na pagina
        if form.validate_on_submit():     # Verifica se o usuario submeteu os dados do form
            types = DeviceTypes.query.all()     # Retorna todos os tipos de dispositivos
            id_type = None     # declara uma variavel None
            for tipo in types:      # percorre todos os tipos de dispositivos no banco
                if "DOCKER" in tipo.name.upper():     # verifica se algum tipo possui a palavra chave "Docker"
                    id_type = tipo.id       # Caso tenha a variavel a cima recebe o ID
            
            if id_type != None: # verifica se a variavel acima é diferente de None
                # Cria um objeto HostDocker passando os dados
                host = HostDocker(form.name.data,form.user.data,form.password.data,
                                  form.ip.data,int(id_type),form.bridge_docker.data)
                # Adiciona no banco e faz commit
                db.session.add(host)
                db.session.commit()
                flash("Added successfully") # Mensagem de sucesso
            else:
                flash("Host not added, please add the device type Docker.")

        return render_template("dispositivos/add_dispositivo.html", form=form) # renderiza a pagina com o form
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /dispositivo/remover_dispositivo da ferramenta
@app.route("/dispositivos/remover_dispositivo")
def remover_dispositivo():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        devices = Device.query.all() # retorna todos os switches
        hosts = HostDocker.query.all() # retorna todos os hosts Docker
        types = DeviceTypes.query.all() # retorna todos os tipos de dispositivo
        return render_template("dispositivos/rm_dispositivo.html", 
                               devices=devices,types=types, hosts=hosts) # renderiza a página com as informações
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /configuracao/remover_dispositivo/apagar/ da ferramenta (apaga de fato o dispositivo)
@app.route("/dispositivos/remover_dispositivo/apagar/", defaults={'id': None}, methods=["GET", "DELETE"])
@app.route("/dispositivos/remover_dispositivo/apagar/<id>")
def apagar_dispositivo(id):
    if current_user.is_authenticated: # verifica a autenticação do usuario
        dispositivo = Device.query.filter_by(id=int(id)).first() # faz um select no banco
        if id != None or id != "": # verifica se o id não é None ou vazio:
            # Deleta o dispositivo do banco e faz commit 
            db.session.delete(dispositivo)
            db.session.commit()
            # retona seus links seja ele como fonte ou como destino
            l1 = Link.query.filter_by(dpid_src=dispositivo.dpid).all()
            l2 = Link.query.filter_by(dpid_dst=dispositivo.dpid).all()

            # Verifica se a quantidade de link é maior que 0 e deleta os links
            if len(l1) > 0:
                for link in l1:
                    db.session.delete(link)
                    db.session.commit()
            if len(l2) > 0:
                for link in l2:
                    db.session.delete(link)
                    db.session.commit()
            flash("Device deleted.") # mensagem de sucesso
            return redirect(url_for("remover_dispositivo")) # redirecionamento para a página remover_dispositivo
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /dispositivos/apagar_host_docker/apagar da ferramenta (Apagar host docker)
@app.route("/dispositivos/apagar_host_docker/apagar/", defaults={'id': None}, methods=["GET", "DELETE"])
@app.route("/dispositivos/apagar_host_docker/apagar/<id>")
def apagar_host_docker(id):
    if current_user.is_authenticated: # verifica a autenticação do usuario
        host = HostDocker.query.filter_by(id=int(id)).first() # select no banco de dados
        # Verifica se o id é válido
        if id != None or id != "":
            # deleta o host docker e faz commit
            db.session.delete(host)
            db.session.commit()
            flash("Host Docker deleted.") # mensagem de sucesso
            return redirect(url_for("remover_dispositivo")) # redirecionamento para remover_dispositivo
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /configuracao da ferramenta
@app.route("/configuracao")
def configuracao():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        resources = Resource.query.all() # retorna a lista de recursos cadastrado no banco
        return render_template("configuracao/index.html",resources=resources) # renderiza a página
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /configuracao/add_recurso da ferramenta
@app.route("/configuracao/add_recurso", methods=['GET', 'POST'])
def add_recursos():
    form = RecursoForm()
    if current_user.is_authenticated: # verifica a autenticação do usuario
        if form.validate_on_submit(): # verifica se o usuario submeteu o form
            try:
                i = Resource(form.name.data, form.url.data) # cria um objeto passando seus valores
                # adiciona no banco e faz commit
                db.session.add(i)
                db.session.commit()
                flash("added successfully") # mensagem de sucesso
            except IntegrityError:
                # Caso dê o erro relacionado a integridade, é retornado essa mensagem de erro
                flash("PID duplicate, no inserted.")

        return render_template("configuracao/add_recurso.html", form=form) # renderiza a página
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /configuracao/recurso/apagar da ferramenta
@app.route("/configuracao/recurso/apagar/", defaults={'id': None}, methods=["GET", "DELETE"])
@app.route("/configuracao/recurso/apagar/<id>")
def apagar_recurso(id):
    if current_user.is_authenticated: # verifica a autenticação do usuario
        resource = Resource.query.filter_by(id=int(id)).first() # Retorna um recurso pelo id
        # Verifica se o id é diferente de None
        if id != None or id != "":
            # remove e faz commit
            db.session.delete(resource)
            db.session.commit()
            flash("Resource deleted.") # mensagem de sucesso
        return redirect(url_for("configuracao")) # redireciona a página configuracao 
    else:
        flash("Restricted area for registered users.") # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /configuracao/edit/ da ferramenta
@app.route("/configuracao/edit/", defaults={'id': None})
@app.route("/configuracao/edit/<id>", methods=['GET', 'POST'])
def edit_recurso(id):
    if current_user.is_authenticated: # verifica a autenticação do usuario
        form = RecursoForm() # Intancia de um objeto de form para criar o formulario
        resource = Resource.query.filter_by(id=int(id)).first() # retorna o recurso de acordo com o ID
        # Verifica se o id é diferente de None
        if id != None or id != "":
            if form.validate_on_submit(): # verifica se o usuário submeteu o form
                # Faz o update das informações
                resource.name = form.name.data
                resource.url = form.url.data
                try:
                    # adiciona o recurso (update) no banco e faz commit
                    db.session.add(resource)
                    db.session.commit()
                    flash("Resource updated.") # mensagem de sucesso
                    return redirect(url_for("configuracao"))
                except IntegrityError:
                    # em caso de erro (PID duplicado) retorna uma mensagem de erro 
                    flash("PID duplicate, no inserted.")

            return render_template("configuracao/edit_config.html", 
                                    form=form, resource=resource) # renderiza a página 
        else:
            return redirect(url_for("configuracao"))
    else:
        flash("Restricted area for registered users.") # # mensagem de erro caso falhe na autenticaçao
        return redirect(url_for("index")) # redirecionamento a página index (login)


# Rota /firewall da ferramenta
@app.route("/firewall")
def firewall():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        color="green"

        enable = False
        rules = []
        try:
            # obter os status de todos os switches
            denied = requests.get("http://localhost:8080/firewall/module/status")
            # verifica o status da requisição
            if denied.status_code == 200:
                count = 0
                for switch in json.loads(denied.text): 
                    if switch["status"] == 'disable':
                        # conta a quantidade de switches desabilitados
                        count += 1
                if count == 0:
                    # se a quantidade de switches for igual a zero, habilita o botão na página
                    enable = True
            # obter todas as regras
            r = requests.get("http://localhost:8080/firewall/rules/all")
            
            if r.status_code == 200:
                for rule in json.loads(r.text):
                    # adiciona por padrão o valor any nas variaveis a seguir (caso não exista)
                    src, dst, proto = "any","any","any"
                    if len(rule['access_control_list']) != 0:
                        for r in rule['access_control_list'][0]['rules']:
                            # verifica a existencia das variaveis na resposta da requisição
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
                            # Cria o objeto
                            rf = RegrasFirewall(rule['switch_id'],
                                            r['rule_id'],
                                            src,
                                            dst,
                                            proto,
                                            r['actions'])
                            # adiciona em um vetor para facilitar a renderização 
                            rules.append(rf)

        except ConnectionError:
            flash("Connection to Firewall application failed.")
            color="red"
        return render_template("firewall/index.html", enable=enable, rules=rules, color=color)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


# Rota/firewall/add_regras da ferramenta
@app.route("/firewall/add_regras", methods=['GET', 'POST'])
def add_regras_firewall():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        form = AddRegrasForm() # objeto do tipo formulario
        if form.validate_on_submit(): # verifica se o usuário submeteu o form
            dpid = form.dpid.data # pega o dpid que o usuario informou no form
            # Objeto para facilitar a aplicação das regras
            pay = applyRegras(form.src.data, form.prefix_src.data, form.dst.data, 
                              form.prefix_dst.data, form.proto.data, form.action.data)
            # adiciona a entrada no switch via rest api do controlador
            put = requests.post("http://localhost:8080/firewall/rules/%s" %(dpid), data = json.dumps(pay))
            if put.status_code == 200: # verifica o codigo de resposta
                flash("Rule added.") # mensagem de sucesso
                return redirect(url_for("firewall")) # redirecionamento para a pagina firewall
            else:
                # em caso de erro retorna uma mensagem de erro
                flash("An error has occurred. Rule not added.")
        # Renderização da pagina com o form instanciado anteriormente
        return render_template("firewall/add_regras.html", form=form)

    else:
        # falha de autenticação
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


# Rota /firewall/apagar da ferramenta
@app.route("/firewall/apagar/", defaults={'id': None, 'dpid':None}, methods=["GET", "DELETE"])
@app.route("/firewall/apagar/<id>/<dpid>")
def apagar_regra_firewall(id, dpid):
    if current_user.is_authenticated: # verifica a autenticação do usuario
        try:
            # deleta a regra de acordo com o id e o dpid do switch
            r = requests.delete("http://localhost:8080/firewall/rules/%s" %(dpid) ,data = json.dumps({"rule_id":str(id)}))
            if r.status_code == 200: # verifica o codigo de resposta
                flash("Rule successfully deleted.") # mensagem de sucesso
            else:
                flash("There was an error deleting rule.") # mensagem de erro
        except ConnectionError:
            flash("the connection failed.") # falha na conexão com o switch
        # redirecionamento para a página firewall
        return redirect(url_for('firewall'))
    else:
        # falha de autenticação
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))



# Rota /firewall/habilitar da ferramenta
@app.route("/firewall/habilitar")
def habilitar_firewall():
    if current_user.is_authenticated: # verifica a autenticação do usuario
        try:
            # Obtem o status de todos os switches
            r = requests.get("http://localhost:8080/firewall/module/status")
            if r.status_code == 200: # verifica o codigo de resposta
                device = json.loads(r.text)
                for switch in device:
                    # atualiza as informações no switche
                    resp = requests.put("http://localhost:8080/firewall/module/enable/%s" %switch["switch_id"])

        except ConnectionError:
            # falha de conexão
            flash("the connection failed.")
        # redirecionamento para a página firewall
        return redirect(url_for("firewall"))
    else:
        # falha de autenticação
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


# Rota /qos da ferramenta
@app.route("/qos")
def qos():
    if current_user.is_authenticated:
        cont = 0
        rules_obj = []
        try:
            # Obtem todos os switches
            switches = requests.get("http://localhost:8080/v1.0/conf/switches")
            if switches.status_code == 200:
                cont = len(json.loads(switches.text))
            # Obtem todas as regras
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
                flash("Rule added.")
            else:
                flash("Rule not added.")

        return render_template("qos/add_regras.html", form=form)
    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/docker/list", methods=["GET"])
def qos_docker_list():
    if current_user.is_authenticated:
        rules = []
        try:
            hosts = HostDocker.query.all()
            for host in hosts:
                r = requests.get("http://%s:5000/qos/rules" %host.ip)
                if r.status_code == 200:
                    resp = json.loads(r.text)
                    for v in resp:
                        rule = RulesVeth(v,resp[v]['IP'], resp[v]['ID'],resp[v]['rule']['rate'],
                                        resp[v]['rule']['burst'], resp[v]['rule']['latency'],
                                        resp[v]['rule']['peak'], resp[v]['rule']['minburst'],
                                        host.ip)
                        rules.append(rule)
        except ConnectionError:
            flash("connection error")

        return render_template("qos/docker_qos_list.html",rules=rules)



@app.route("/qos/docker/del", defaults={'veth': None,'ip_host':None}, methods=['GET','POST'])
@app.route("/qos/docker/del/<veth>/<ip_host>", methods=['GET','POST'])
def del_rule_docker(veth,ip_host):
    if current_user.is_authenticated:
        host = HostDocker.query.filter_by(ip=ip_host).first()
        d = {
                "veth":veth,
                "user": host.user,
                "pass": host.password
            }
        try:
            r = requests.delete("http://%s:5000/qos/rules" %host.ip, data=json.dumps(d))
            if r.status_code == 200:
                flash("Rule deleted.")
            else:
                flash("An error has occurred.")
                
        except ConnectionError:
            flash("connection error")
        
        return redirect(url_for("qos_docker_list"))

    else:
        flash("Restricted area for registered users.")
        return redirect(url_for("index"))


@app.route("/qos/docker/add", methods=['GET','POST'])
def qos_host_docker():
    if current_user.is_authenticated:
        color = 'green'
        form = QoSHostDockerForm()
        if form.validate_on_submit():
            try:
                host = HostDocker.query.filter_by(ip=form.ip.data).first()
                print host.ip
                d = {
                        "veth": form.iface.data,
                        "user": host.user,
                        "pass": host.password,
                        "rate": '%skbit' %form.rate.data,
                        "burst": '%skbit' %form.burst.data,
                        "latency": '%sms' %form.latency.data,
                        "peak": '%skbit' %form.peakrate.data,
                        "minburst": '%sb' %form.minburst.data
                    }
                try:
                    r = requests.post("http://%s:5000/qos/rules" %host.ip, data=json.dumps(d))
                    if r.status_code == 200:
                        flash("Rule added.")
                    else:
                        color="red"
                        flash("Rule not added.")
                        
                except ConnectionError:
                    color="red"
                    flash("the connection failed.")

            except AttributeError:
                color="red"
                flash("Host does not exist in the database.")

        return render_template("qos/docker_qos.html", form=form, color=color)
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
                    pass
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
