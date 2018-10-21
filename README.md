# Beaver View

## Pendências
- Instalar `git` e o `pip`:
```
apt update && apt install git python-pip mysql-server -y
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
- **OBS:** Caso durante a instalação apareça esse erro:`Failed building wheel for cryptography`
execute o comando a seguir para corrigir:`apt-get install build-essential libssl-dev libffi-dev python-dev` e execute o comando para instalar as dependências novamente.



