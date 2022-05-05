#!/usr/bin/env python3
import sqlite3
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, BaseSettings

import redis 

class Settings(BaseSettings):
    user_db: str   #user_db
    shard1_db: str #stats_1 db
    shard2_db: str #stats_2 db
    shard3_db: str #stats_3 db

app = FastAPI()
settings = Settings()

sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: bytes(u.bytes_le))

db = [
    sqlite3.connect(settings.user_db),
    sqlite3.connect(settings.shard1_db),
    sqlite3.connect(settings.shard2_db),
    sqlite3.connect(settings.shard3_db)
]

for i in db:
    i.row_factory = sqlite3.Row


r = redis.Redis(
    host = "localhost", port = 6379, db = 0, charset = "utf-8", decode_responses=True
)

table_view = []
num_wins = []
for shard in range(3):
    try:
        cur = db[shard].cursor()
        cur.execute("""SELECT * FROM wins ORDER BY "COUNT(won)" DESC LIMIT 10""")
        data = cur.fetchall()
        for row in data:
            table_view.append(row)

        for i in range(table_view):
            r.zadd("Wins",{num_wins[i]})

    except Exception as e:
        print(f"An error has occured! => {e}")


num_streaks = []
for shard in range(3):
    try:
        cur = db[shard].cursor()
        cur.execute("""SELECT * FROM streaks ORDER BY streak DESC LIMIT 10""")
        data = cur.fetchall()
        for row in data:
            table_view.append(row)

        for i in range(table_view):
            r.zadd("Streaks",{num_streaks[i]})

    except Exception as e:
        print(f"An error has occured! => {e}")

