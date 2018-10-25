delete(){
	funfou=`mysql -u root -p${1} < delete.sql &> /dev/null ;echo $?`
	if [ ${funfou} = 0 ]; then
		echo "Configurações do MSQL deletada com sucesso"
	else
		echo "Ocorreu um erro ao deletar usuario e o banco"
	fi
}

while getopts "p:" OPTVAR
do
	if [ ${OPTVAR} = 'p' ]; then
		delete ${OPTARG}
	else
		echo "Necessario passar a senha de root do usuario mysql"
	fi
done

