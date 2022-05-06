#!/bin/bash

# install traefik depdendency
mkdir temp
curl --silent -L -o traefik.tar.gz https://github.com/traefik/traefik/releases/download/v2.6.3/traefik_v2.6.3_linux_amd64.tar.gz
tar -xf traefik.tar.gz -C temp 2>&1 1>/dev/null
mv ./temp/traefik ./proxy 
rm -rf temp
rm traefik.tar.gz

# add project directory to env variable for cron
echo "export PROJ_PATH=$(pwd)" > ~/wordle.env && . ~/wordle.env

# TODO: build standalone app
pyinstaller --onefile ./bin/Top10.py

# start redis-server in background
redis-server --daemonize yes

# start cronjob
crontab ./bin/cron.txt && mkdir -p ./var/log