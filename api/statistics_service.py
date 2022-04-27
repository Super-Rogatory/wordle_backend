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


# defines a valid game in request body
class Game(BaseModel):
    game_id: int
    finished: str
    guesses: int
    game_status: bool


# Allows us to retrieve NAME_OF_DB from Procfile
# class Settings(BaseSettings):
#     name_of_db: str


# Connect to necessary dependencies
app = FastAPI()
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

# every route connects to a db, depending on env
@app.get("/top_ten_in_wins")
async def get_top_ten_in_wins():
    shard_scan_results = []
    stats = []
    try:
        users_cur = users_db.cursor()
        # for every shard get their top ten then use filter func to sort and filter
        for (connection, _) in shard_connections:
            cur = connection.cursor()
            cur.execute("""SELECT * FROM wins ORDER BY "COUNT(won)" DESC LIMIT 10""")
            for result in cur.fetchall():
                shard_scan_results.append(result)
        filtered_list = filter_values(shard_scan_results)  # utilizing helper function
        # query each guid for the username that it is linked to
        for (guid, wins) in filtered_list:
            users_cur.execute(
                f"SELECT username FROM users WHERE guid=:id", {"id": guid}
            )
            name = users_cur.fetchone()[0]
            stats.append({"name": name, "wins": wins})
        return stats
    except Exception as e:
        print(f"An error has occured! => {e}")


@app.get("/top_ten_in_streaks")
async def get_top_ten_in_streaks():
    shard_scan_results = []
    stats = []
    try:
        users_cur = users_db.cursor()
        # for every shard get their top ten then use filter func to sort and filter
        for (connection, _) in shard_connections:
            cur = connection.cursor()
            cur.execute(
                """SELECT guid, streak FROM streaks ORDER BY streak DESC LIMIT 10"""
            )
            for result in cur.fetchall():
                shard_scan_results.append(result)
        filtered_list = filter_values(shard_scan_results)  # utilizing helper function
        # query each guid for the username that it is linked to
        for (guid, streak) in filtered_list:
            users_cur.execute(
                f"SELECT username FROM users WHERE guid=:id", {"id": guid}
            )
            name = users_cur.fetchone()[0]
            stats.append({"name": name, "streak": streak})
        return stats
    except Exception as e:
        print(f"An error has occured! => {e}")


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
