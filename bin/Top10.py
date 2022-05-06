#!/usr/bin/env python3
import itertools
import sqlite3
import uuid
import collections
import os
import redis
from sqlite_utils import Database

sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: bytes(u.bytes_le))

r = redis.Redis(
    host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True
)

database_dir = os.environ["PROJ_PATH"] + "/db/"


def top10_wins():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    for i in range(3):
        shard = i + 1
        db = Database(sqlite3.connect(f"{database_dir}stats_{shard}.db"))
        db.attach("users", f"{database_dir}users.db")
        shard_top10[shard] = db.execute(
            "SELECT wins.wins, users.username FROM wins INNER JOIN users ON wins.guid=users.guid ORDER BY wins DESC LIMIT 10"
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    for user in range(30):
        score = all_list[user][0]
        username = all_list[user][1]
        r.zadd("wins", {username: score})


def top10_streaks():
    shard_top10 = collections.defaultdict(list)
    temp = []
    all_list = []
    for i in range(3):
        shard = i + 1
        db = Database(sqlite3.connect(f"{database_dir}stats_{shard}.db"))
        db.attach("users", f"{database_dir}users.db")
        shard_top10[shard] = db.execute(
            "SELECT streaks.streak, users.username FROM streaks INNER JOIN users ON streaks.guid=users.guid ORDER BY streak DESC LIMIT 10"
        ).fetchall()
        temp.append(shard_top10[shard])
    all_list = list(itertools.chain(*temp))
    for user in range(30):
        score = all_list[user][0]
        username = all_list[user][1]
        r.zadd("streaks", {username: score})


top10_streaks()
top10_wins()
