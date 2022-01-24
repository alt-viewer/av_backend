RED='\033[0;31m'
NC='\033[0m'
printf "This will ${RED}delete${NC} the whole Alt Viewer database. Are you sure?"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
	bash ./stop_db.sh
	docker rm dgraph
	echo "Deleted the Alt Viewer database."
	read -p "Would you like to reinitialise the database?" -n 1 -r
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		bash ./init_db.sh
	fi
fi
