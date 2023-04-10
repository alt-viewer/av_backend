target=$1
matches=$(ps -ef | grep -v "grep\|check-running" | grep -c "$target")
if [ $matches -eq 0 ]; then
    echo "$target is not running. Starting $target..."
    sudo systemctl start $target
fi