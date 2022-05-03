#!/bin/bash

# add project directory to env variable for cron
echo "export PROJ_PATH=$(pwd)" >> ~/.bash_profile && . ~/.bash_profile

# TODO: build standalone app
# pyinstaller --onefile $PROJ_PATH/bin/python/getTop10.py

# start cronjob
crontab $PROJ_PATH/bin/cron.txt