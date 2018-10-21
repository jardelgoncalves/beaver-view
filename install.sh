#!/bin/bash

criando_tabelas(){
	python run.py db init
	python run.py db migrate
	python run.py db upgrade
}

inserindo_valores(){
	insert=`mysql -u root -p${1} beaver_db < sql/populando.sql ;echo $?`
	if [ ${insert} = 0 ]; then
                echo "usuario inserido"
        else
                echo "usuario nao inserido"
        fi

}

add_user_e_db(){
	funfou=`mysql -u root -p${1} < sql/config.sql &> /dev/null ;echo $?`
	if [ ${funfou} = 0 ]; then
		echo "Deu certo"
		criando_tabelas
		inserindo_valores ${1}
	else
		echo "Nao deu certo"
	fi
}


while getopts "p:" OPTVAR
do
	add_user_e_db ${OPTARG}
	echo "$OPTVAR $OPTARG"
done


