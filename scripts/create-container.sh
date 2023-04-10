sh scripts/_check-running.sh docker
docker pull mongo
port=$(cat data/db/config.json | jq ".port")
docker run -d --name alt-viewer-mongo -p $port:$port mongo