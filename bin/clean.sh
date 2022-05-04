#!/bin/bash
rm -r \
    build \
    dist \
    db \
    bin/__pycache__ \
    dump.rdb \
    *.spec \
    traefik \
    share \
    2> /dev/null 
#remove crontab
crontab -r