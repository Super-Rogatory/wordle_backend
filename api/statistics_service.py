import sqlite3
import uuid
from fastapi import FastAPI, HTTPException
from utils import (
    start_connection,
    validate_game_result,
    get_streak,
    get_guesses,
    analyze_guess_data,
    filter_values,
)
from pydantic import BaseModel
import redis
import json


# defines a valid game in request body
class Game(BaseModel):
    game_id: int
    finished: str
    guesses: int
    game_status: bool


# Connect to necessary dependencies
app = FastAPI()

# connect to redis
r = redis.Redis(
    host="localhost", port=6379, db=0, charset="utf-8", decode_responses=True
)

# settings = Settings()
users_db = start_connection("users")
shard_connections = [
    (start_connection("stats_1"), "games_1"),
    (start_connection("stats_2"), "games_2"),
    (start_connection("stats_3"), "games_3"),
]

# So we can see the uuid in the terminal!
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: bytes(u.bytes_le))

# pull leaderboard from redis
@app.get("/top10/streaks")
def top10_streaks():
    top10streaks = r.zrevrange(name="streaks", start=0, end=9, withscores=True)
    return json.dumps(top10streaks)


@app.get("/top10/wins")
def top10_wins():
    top10wins = r.zrevrange(name="wins", start=0, end=9, withscores=True)
    return json.dumps(top10wins)


# every route connects to a db, depending on env
@app.get("/{username}")
async def get_statistics(username: str):
    user_guid = -1
    query_results = []
    try:
        users_cur = users_db.cursor()
        # find the user id from the username(since usname is unique)
        users_cur.execute(
            "SELECT guid FROM users WHERE username=:name", {"name": username}
        )
        result = users_cur.fetchone()
        user_guid = result[0] if result != None else -1
    except Exception as e:
        print(f"An error has occured! => {e}")

    # if user_guid is still -1, we did not find a user.
    if type(user_guid) == int and user_guid == -1:
        raise HTTPException(status_code=400, detail="User not found in database.")

    try:
        # for every shard look up the user_guid to see if you can find it in there.
        for (connection, tbl_name) in shard_connections:
            cur = connection.cursor()
            cur.execute(f"SELECT * FROM {tbl_name} WHERE guid=:id", {"id": user_guid})
            # once you match the id to a shard, fetch data from db to be filtered
            if cur.fetchall() != []:
                cur.execute(
                    f"""
                        SELECT finished, guesses, won
                        FROM {tbl_name}
                        WHERE guid=:uid
                        ORDER BY finished
                    """,
                    {"uid": user_guid},
                )
                query_results = cur.fetchall()
                break
        # use helper functions to parse data instead of making extra calls to db
        (cur_streak, max_streak) = get_streak(query_results)
        guesses = get_guesses(query_results)
        (win_percentage, games_played, games_won, avg_guesses) = analyze_guess_data(
            guesses
        )
        return {
            "stats": {
                "currentStreak": cur_streak,
                "maxStreak": max_streak,
                "guesses": guesses,
                "winPercentage": win_percentage,
                "gamesPlayed": games_played,
                "gamesWon": games_won,
                "averageGuesses": avg_guesses,
            }
        }
    except Exception as e:
        print(f"An error has occured! => {e}")


@app.post("/game_result/{username}")
async def game_result(username: str, game: Game):
    user_guid = -1
    # try to find the user in the db. if cannot find - raise HTTPException.
    try:
        users_cur = users_db.cursor()
        # find the user id from the username(since usname is unique)
        users_cur.execute(
            "SELECT guid FROM users WHERE username=:name", {"name": username}
        )
        result = users_cur.fetchone()
        user_guid = result[0] if result != None else -1
    except Exception as e:
        print(f"An error has occured! => {e}")

    # if user_guid is still -1, we did not find a user.
    if type(user_guid) == int and user_guid == -1:
        raise HTTPException(status_code=400, detail="User not found in database.")

    # validate query
    isValid = validate_game_result(game.game_status, game.finished, game.guesses)
    if not isValid:
        raise HTTPException(status_code=400, detail="Query is invalid.")

    # locate the shard that contains the user information
    try:
        # we're iterating through each (connection, tablename) in our shard connections list.
        # as soon as we identify the user in one of the shards, break.
        # we'll still have access to the connection and tbl_name from the moment looping stops
        for (connection, tbl_name) in shard_connections:
            cur = connection.cursor()
            cur.execute(f"SELECT * FROM {tbl_name} WHERE guid=:id", {"id": user_guid})
            # once you match the id to a shard, fetch data from db to be filtered
            if cur.fetchall() != []:
                # since there is more logic here - for readability track index
                break
        # cur comes from match loop ^
        cur.execute(
            f"SELECT * FROM {tbl_name} WHERE finished=:date_finished AND guid=:uid",
            {"date_finished": game.finished, "uid": user_guid},
        )
    except Exception as e:
        print(f"An error has occured! => {e}")

    # if there is a record with duplicate date attached to same user - break - error
    if len(cur.fetchall()):
        raise HTTPException(status_code=400, detail="Duplicate dates error.")

    # insert new records in sharded games table
    cur.execute(
        f"""
            INSERT INTO {tbl_name}
            VALUES (:uid, :gid, :finished, :guesses, :won)
        """,
        {
            "uid": user_guid,
            "gid": game.game_id,
            "finished": game.finished,
            "guesses": game.guesses,
            "won": game.game_status,
        },
    )
    connection.commit()
    # retreive information after update to ensure it has updated.
    cur.execute(
        f"SELECT * FROM {tbl_name} WHERE game_id=:gid AND guid=:uid",
        {"gid": game.game_id, "uid": user_guid},
    )
    res = cur.fetchone()

    return {"gameResults": res}
