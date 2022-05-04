#!/bin/bash

# add project directory to env variable for cron
echo "export PROJ_PATH=$(pwd)" >> ~/.bash_profile && . ~/.bash_profile

# TODO: build standalone app
# pyinstaller --onefile ./bin/python/getTop10.py

# start cronjob
. ~/.bash_profile crontab $PROJ_PATH/bin/cron.txt && mkdir -p $PROJ_PATH/var/log