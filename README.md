# Beaver View

## Pendências
- Instalar `git`, `mysql`, `pip` e outras libs importantes:
```
apt update && apt install git python-pip mysql-server build-essential libssl-dev libffi-dev python-dev -y
```
- Com o `git` instalado, clone o repositório:
```
git clone https://github.com/JardelGoncalves/Beaver-View.git
```
- Acesse o diretório do repositório clonado:
```
cd Beaver-View
```
- Instale as dependências:
```
pip install -r requeriments.txt
```

- Agora execute o script de instalação `install.sh` da seguinte fotma:
```
bash install.sh -p <senha do usuario root do mysql>
```
-Vale ressaltar que esse script utilzia outros arquivos que podem ser encontrado no diretorio `sql/` para configurar a ferramenta, caso aconteça algum problema durante a execução do script, possivelmente será necessário o usuário  apagar o banco e o usuario, no entanto, disponibilizamos outro script dentro do diretório citado anteriormente chamado de `delete_config.sh` que deve ser executado da mesma forma 
```
bash delete_config.sh -p <senha do usuario root mysql>
```

- Feito isso, basta executar a ferramenta:
```
python run.py runserver --host=0.0.0.0
```
- Agora abra o browser e acesse a URL `http://<ip_do host>:5000`
- As credenciais são:
```
email = admin@beaver.com
senha = admin123
```
