# Sharding database records into three different tables.
import os, sys
import sqlite3
import uuid

# finds the parent directory automatically
path_to_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(path_to_root)

from api.utils import start_connection

# laying down the groundwork for database information access
conn = start_connection(3)  # connect to stats db
shard_1 = start_connection("stats_1")  # prepare to insert into shard_1, 2, and 3
shard_2 = start_connection("stats_2")
shard_3 = start_connection("stats_3")
users = start_connection("users")

c = conn.cursor()
c_s1 = shard_1.cursor()
c_s2 = shard_2.cursor()
c_s3 = shard_3.cursor()
c_users = users.cursor()

# FOR SHARDS: Allows the storage of guid as the unique identifier for records
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: bytes(u.bytes_le))

c.execute("SELECT * FROM games")
c_s1.execute("DROP TABLE IF EXISTS games_1")
c_s1.execute(
    """
    CREATE TABLE IF NOT EXISTS games_1 (
        guid GUID,
        game_id INTEGER NOT NULL,
        finished DATE DEFAULT CURRENT_TIMESTAMP,
        guesses INTEGER,
        won BOOLEAN,
        PRIMARY KEY(guid, game_id)
    )
    """
)
c_s2.execute("DROP TABLE IF EXISTS games_2")
c_s2.execute(
    """
    CREATE TABLE IF NOT EXISTS games_2 (
        guid GUID,
        game_id INTEGER NOT NULL,
        finished DATE DEFAULT CURRENT_TIMESTAMP,
        guesses INTEGER,
        won BOOLEAN,
        PRIMARY KEY(guid, game_id)
    )
"""
)
c_s3.execute("DROP TABLE IF EXISTS games_3")
c_s3.execute(
    """
    CREATE TABLE IF NOT EXISTS games_3 (
        guid GUID,
        game_id INTEGER NOT NULL,
        finished DATE DEFAULT CURRENT_TIMESTAMP,
        guesses INTEGER,
        won BOOLEAN,
        PRIMARY KEY(guid, game_id)
    )
"""
)
c_users.execute("DROP TABLE IF EXISTS users")
c_users.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        guid GUID PRIMARY KEY,
        user_id INTEGER NOT NULL,
        username VARCHAR UNIQUE
    )
    """
)
# Use quote(guid) to access string value
shard_1.commit()
shard_2.commit()
shard_3.commit()
users.commit()

# FOR USERS: copying from users in statistics.db to users in users.db
c.execute("SELECT * FROM users")
all_users_in_main_db = c.fetchall()
for user in all_users_in_main_db:
    (user_id, username) = user
    c_users.execute(
        "INSERT INTO users VALUES(:guid, :uid, :name)",
        {"guid": uuid.uuid4(), "uid": user_id, "name": username},
    )

c_users.execute("SELECT * FROM users")
records_in_users = c_users.fetchall()
if len(records_in_users) == len(all_users_in_main_db):
    print("Users have been copied over successfully.")
else:
    print("Failed to copy from statistics db to users db!")

# FOR SHARDS: now we are ready to shard!
# take a user record, then use main stats db to find all games tied to users - mirror that info into the sharded games db
cases = {"shard_1": 0, "shard_2": 1, "shard_3": 2}
for record in records_in_users:
    (guid, user_id, username) = record
    c.execute("SELECT * FROM games WHERE user_id=:uid", {"uid": user_id})
    games = c.fetchall()
    for game in games:
        (_, game_id, finished, guesses, won) = game
        if int(guid) % 3 == cases["shard_1"]:
            c_s1.execute(
                "INSERT INTO games_1 VALUES (:guid, :gid, :finished, :guesses, :won)",
                {
                    "guid": guid,
                    "gid": game_id,
                    "finished": finished,
                    "guesses": guesses,
                    "won": won,
                },
            )
        elif int(guid) % 3 == cases["shard_2"]:
            c_s2.execute(
                "INSERT INTO games_2 VALUES (:guid, :gid, :finished, :guesses, :won)",
                {
                    "guid": guid,
                    "gid": game_id,
                    "finished": finished,
                    "guesses": guesses,
                    "won": won,
                },
            )
        elif int(guid) % 3 == cases["shard_3"]:
            c_s3.execute(
                "INSERT INTO games_3 VALUES (:guid, :gid, :finished, :guesses, :won)",
                {
                    "guid": guid,
                    "gid": game_id,
                    "finished": finished,
                    "guesses": guesses,
                    "won": won,
                },
            )

# FOR SHARDS: testing that the database has been sharded correctly with guid information
c_s1.execute("SELECT * FROM games_1")
c_s2.execute("SELECT * FROM games_2")
c_s3.execute("SELECT * FROM games_3")
c.execute("SELECT * FROM games")
records_in_shard_1 = c_s1.fetchall()
records_in_shard_2 = c_s2.fetchall()
records_in_shard_3 = c_s3.fetchall()
all_records_in_shards = (
    len(records_in_shard_1) + len(records_in_shard_2) + len(records_in_shard_3)
)
total_records = c.fetchall()
# FOR SHARDS: testing to see if the database has been successfully sharded
if all_records_in_shards == len(total_records):
    print("Database has been successfully sharded.")
else:
    print("Failed to shard DB!")

# testing query
# c_users.execute("SELECT * FROM users LIMIT 1")
# id = c_users.fetchone()[0]  # uuid.UUID(str(id)) == id
# print(id)
# c_s1.execute("SELECT guid FROM games_1 WHERE guid=:id", {"id": id})
# print(c_s1.fetchall())

# save changes
shard_1.commit()
shard_2.commit()
shard_3.commit()
users.commit()

# close connection
conn.close()
shard_1.close()
shard_2.close()
shard_3.close()
users.close()
