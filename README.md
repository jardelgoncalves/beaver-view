# Beaver View

Pendências
==========
Instalar `git`, `mysql`, `pip` e outras libs importantes:
```
apt update && apt install git python-pip mysql-server build-essential libssl-dev libffi-dev python-dev -y
```
Instalação da Ferramenta
==========
Com o `git` instalado, clone o repositório::
```
git clone https://github.com/JardelGoncalves/Beaver-View.git
```
Acesse o diretório do repositório clonado:
```
cd Beaver-View
```
Instale as dependências:
```
pip install -r requeriments.txt
```
Agora execute o script de instalação `install.sh` da seguinte fotma:
```
bash install.sh -p <senha do usuario root do mysql>
```

Vale ressaltar que esse script utilzia outros arquivos que podem ser encontrado no diretorio `sql/` para configurar a ferramenta, caso aconteça algum problema durante a execução do script, possivelmente será necessário o usuário  apagar o banco e o usuario, no entanto, disponibilizamos outro script dentro do diretório citado anteriormente chamado de `delete_config.sh` que deve ser executado da mesma forma 
```
bash delete_config.sh -p <senha do usuario root mysql>
 ```
Agent de monitoramento da Ferramenta
==========
É necessário iniciar o modulo de monitoração, para isso execute o comando `crontab -e` e adicione as seguintes linhas:
```
* * * * * sleep 30 && python /home/<user>/<path>/Beaver-View/monitoring/agent.py
* * * * * sleep 60 && python /home/<user>/<path>/Beaver-View/monitoring/agent.py
```
Troque `<user>` pelo usuario da máquina e `<path>` pelo restatnte do caminho até o diretório da ferramenta.

Essas linhas permite que o `agent.py` colete as informações dos switches, porém é necessário que pelo menos a aplicação `ofctl_rest.py` esteja sendo executado, pois o mesmo fornece a REST API.

Instalação do Ryu
==========
Para fazer uso do controlador `ryu`, clone o repositório (fora do diretorio da ferramenta)
```
git clone https://github.com/JardelGoncalves/ryu.git
```
Acesse o diretório do ryu e instale as dependências:
```
cd ryu; pip install .
```
No diretório `my_app` possui algumas aplicações disponibilizadas pela comunidade e outras modificadas para atender as necessidades da ferramenta. Caso o administrador deseje usar suas aplicações, o diretório/biblioteca `func_lib` dentro de `my_app` deve ser portado para o local de suas aplicações, e deve ser implementado pelo menos em uma de suas aplicações os eventos `EventSwitchEnter` e `event.EventLinkAdd` adicionando os métodos `register_device(msg, "Switch")` que cadastra o switch no banco de dados e o método `register_link(msg)` que cadastra o link no banco de dados, um exemplo pode ser observado no arquivo `switch_L2.py` dentro de `my_app`.

Para o funcionamento correto do `agent.py` o administrador deve está ciente da execução do `ofctl_rest.py` também pode ser encontrado dentro de `my_app`.

Execução da Ferramenta Beaver View
==========
Feito isso, basta executar a ferramenta:
```
python run.py runserver --host=0.0.0.0
```
Agora abra o browser e acesse a URL `http://<ip_do host>:5000`

As credenciais são:
```
email = admin@beaver.com
senha = admin123
```
