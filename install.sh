#!/bin/bash

criando_tabelas(){
	python run.py db init
	python run.py db migrate
	python run.py db upgrade
}

inserindo_valores(){
	insert=`mysql -u root -p${1} beaver_db < sql/populando.sql &> /dev/null ;echo $?`
	if [ ${insert} = 0 ]; then
                echo "Usuario inserido"
        else
                echo "Usuario nao inserido"
        fi

}

add_user_e_db(){
	funfou=`mysql -u root -p${1} < sql/config.sql &> /dev/null ;echo $?`
	if [ ${funfou} = 0 ]; then
		criando_tabelas
		inserindo_valores ${1}
	else
		echo "Ocorreu um erro ao criar o usuario e o banco"
	fi
}


while getopts "p:" OPTVAR
do
	if [ ${OPTVAR} = 'p' ]; then
		add_user_e_db ${OPTARG}
	else
		echo "Necessario passar a senha de root do usuario mysql"
	fi
done


