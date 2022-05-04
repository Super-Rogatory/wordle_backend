#!/bin/bash

# add project directory to env variable for cron
echo "export PROJ_PATH=$(pwd)" >> ~/.bash_profile && . ~/.bash_profile

# TODO: build standalone app
# pyinstaller --onefile ./bin/python/getTop10.py

# start cronjob
crontab ./bin/cron.txt && mkdir -p ./var/log