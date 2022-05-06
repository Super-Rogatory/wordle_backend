#!/usr/bin/env python3
import itertools
import sqlite3
import uuid
import collections
import os
import redis 

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, BaseSettings

app = FastAPI()

sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: bytes(u.bytes_le))

r = redis.Redis(
    host = "localhost", port = 6379, db = 0, charset = "utf-8", decode_responses=True
)

database_dir = os.environ["PROJ_PATH"] + "/db"

def top10_wins():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    for shard in range(3):
        db = sqlite3.connect(f"./db/stats_1.db")
        shard_top10[shard] = db.execute(
            """SELECT * FROM wins ORDER BY "COUNT(won)" DESC LIMIT 10"""
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    for i in len(shard_top10):
        r.zadd("wins",shard_top10[i])

def top10_streaks():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    for shard in range(3):
        db = sqlite3.connect(f"./db/stats_1.db")
        shard_top10[shard] = db.execute(
            """SELECT * FROM streaks ORDER BY streak DESC LIMIT 10"""
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    for i in len(shard_top10):
        r.zadd("streaks", shard_top10[i])



#db = [
#    sqlite3.connect("./db/stats_1.db"),
#    sqlite3.connect("./db/stats_2.db"),
#    sqlite3.connect("./db/stats_3.db")
#]

#table_view = []
#num_wins = []
#
#for shard in range(3):
#    try:
#        cur = db[shard].cursor()
#        cur.execute("""SELECT * FROM wins ORDER BY "COUNT(won)" DESC LIMIT 10""")
#        data = cur.fetchall()
#        for row in data:
#            table_view.append(row)
#
#        for i in range(table_view):
#            r.zadd("wins",num_wins[i])
#            print('wins added')
#
#    except Exception as e:
#        print(f"An error has occured! => {e}")
#
#
#num_streaks = []
#for shard in range(3):
#    try:
#        cur = db[shard].cursor()
#        cur.execute("""SELECT * FROM streaks ORDER BY streak DESC LIMIT 10""")
#        data = cur.fetchall()
#        for row in data:
#            table_view.append(row)
#
#        for i in range(table_view):
#            r.zadd("streaks",num_streaks[i])
#            print('Streaks added')
#
#    except Exception as e:
#        print(f"An error has occured! => {e}")