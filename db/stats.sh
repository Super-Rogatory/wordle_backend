#!/bin/bash

# populate database
USER_DB='users.db'
GAMES_DB0='games0.db'
GAMES_DB1='games1.db'
GAMES_DB2='games2.db'

if [ ! -f "./var/$USER_DB" ]
then
    mkdir -p var/log
    sqlite3 ./var/$USER_DB < ./share/users.sql 
    sqlite3 ./var/$GAMES_DB0 < ./share/games.sql && \
    sqlite3 ./var/$GAMES_DB1 < ./share/games.sql && \
    sqlite3 ./var/$GAMES_DB2 < ./share/games.sql && \
    python3 ./db/stats_populate.py
else
    echo "$USER_DB already exists"
fi
