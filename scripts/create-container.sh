docker pull mongo
port=$(cat data/db/config.json | jq ".port")
docker run --name alt-viewer-mongo -p $port:$port mongo