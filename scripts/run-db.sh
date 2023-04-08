matches=$(ps -ef | grep -v grep | grep -c "dockerd")
if [ $matches -eq 0 ]; then
    echo "The docker daemon is not running. Starting docker..."
    sudo systemctl start docker
fi
echo -n "Started " && docker start alt-viewer-mongo