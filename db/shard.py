# Sharding database records into three different tables.
import os, sys
import sqlite3
import uuid

# finds the parent directory automatically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils import start_connection

# laying down the groundwork for database information access
conn = start_connection(3)  # connect to stats db
shard_1 = start_connection("stats_1")  # prepare to insert into shard_1, 2, and 3
shard_2 = start_connection("stats_2")
shard_3 = start_connection("stats_3")
c = conn.cursor()
c_s1 = shard_1.cursor()
c_s2 = shard_2.cursor()
c_s3 = shard_3.cursor()

# Allows the storage of guid as the unique identifier for records
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

c.execute("SELECT * FROM games")
c_s1.execute("DROP TABLE IF EXISTS games_1")
c_s1.execute(
    """
    CREATE TABLE IF NOT EXISTS games_1 (
        guid GUID PRIMARY KEY,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        finished DATE DEFAULT CURRENT_TIMESTAMP,
        guesses INTEGER,
        won BOOLEAN
        won BOOLEAN
    )
    """
)
c_s2.execute("DROP TABLE IF EXISTS games_2")
c_s2.execute(
    """
    CREATE TABLE IF NOT EXISTS games_2 (
        guid GUID PRIMARY KEY,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        finished DATE DEFAULT CURRENT_TIMESTAMP,
        guesses INTEGER,
        won BOOLEAN
    )
"""
)
c_s3.execute("DROP TABLE IF EXISTS games_3")
c_s3.execute(
    """
    CREATE TABLE IF NOT EXISTS games_3 (
        guid GUID PRIMARY KEY,
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        finished DATE DEFAULT CURRENT_TIMESTAMP,
        guesses INTEGER,
        won BOOLEAN
    )
"""
)
# Use quote(guid) to access string value
shard_1.commit()
shard_2.commit()
shard_3.commit()

# now we are ready to shard!
all_records = c.fetchall()
for record in all_records:
    cases = {"shard_1": 0, "shard_2": 1, "shard_3": 2}
    (user_id, game_id, finished, guesses, won) = record
    if user_id % 3 == cases["shard_1"]:
        c_s1.execute(
            "INSERT INTO games_1 VALUES (:guid, :uid, :gid, :finished, :guesses, :won)",
            {
                "guid": uuid.uuid4(),
                "uid": user_id,
                "gid": game_id,
                "finished": finished,
                "guesses": guesses,
                "won": won,
            },
        )
    elif user_id % 3 == cases["shard_2"]:
        c_s2.execute(
            "INSERT INTO games_2 VALUES (:guid, :uid, :gid, :finished, :guesses, :won)",
            {
                "guid": uuid.uuid4(),
                "uid": user_id,
                "gid": game_id,
                "finished": finished,
                "guesses": guesses,
                "won": won,
            },
        )
    elif user_id % 3 == cases["shard_3"]:
        c_s3.execute(
            "INSERT INTO games_3 VALUES (:guid, :uid, :gid, :finished, :guesses, :won)",
            {
                "guid": uuid.uuid4(),
                "uid": user_id,
                "gid": game_id,
                "finished": finished,
                "guesses": guesses,
                "won": won,
            },
        )

# save changes
shard_1.commit()
shard_2.commit()
shard_3.commit()

# testing that the database has been sharded correctly with guid information
c_s1.execute("SELECT DISTINCT COUNT(guid) FROM games_1")
c_s2.execute("SELECT DISTINCT COUNT(guid) FROM games_2")
c_s3.execute("SELECT DISTINCT COUNT(guid) FROM games_3")
records_in_shard_1 = c_s1.fetchone()[0]
records_in_shard_2 = c_s2.fetchone()[0]
records_in_shard_3 = c_s3.fetchone()[0]

# testing to see if the database has been successfully sharded
if records_in_shard_1 + records_in_shard_2 + records_in_shard_3 == len(all_records):
    print("Database has been successfully sharded")
else:
    print("Failed to shard DB.")

# close connection
conn.close()
shard_1.close()
shard_2.close()
shard_3.close()
