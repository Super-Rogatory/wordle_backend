from fastapi import FastAPI, HTTPException
from utils import start_connection, validate_game_result
from datetime import datetime


app = FastAPI()

# connect to statistics database
conn = start_connection(3)
c = conn.cursor()
"""
    SCHEMA
    CREATE TABLE users(
        user_id INTEGER PRIMARY KEY,
        username VARCHAR UNIQUE
    );

    CREATE TABLE games(
        user_id INTEGER NOT NULL,
        game_id INTEGER NOT NULL,
        finished DATE DEFAULT CURRENT_TIMESTAMP,
        guesses INTEGER,
        won BOOLEAN,
        PRIMARY KEY(user_id, game_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
"""
# (user_id, game_id, finished, guesses, won) in statistics database
USER_ID = 0
GAME_ID = 1
FINISHED = 2
GUESSES = 3
WON_STATUS = 4


@app.post("/statistics/gameresult/{user_id}")
async def modify_game_result(
    user_id: int, game_id: int, status: int, finished: str, guesses: int
):
    # validate query
    isValid = validate_game_result(status, finished, guesses)
    if not isValid:
        raise HTTPException(status_code=400, detail="Query is invalid.")

    # uid and gid uniquely identify game, update properties
    c.execute(
        """
            UPDATE games 
            SET won=:status, finished=:finished, guesses=:guesses WHERE user_id=:uid AND game_id=:gid
        """,
        {
            "status": status,
            "finished": finished,
            "guesses": guesses,
            "uid": user_id,
            "gid": game_id,
        },
    )
    conn.commit()
    # retreive information after update to ensure it has updated.
    c.execute(
        "SELECT * FROM games WHERE game_id=:gid AND user_id=:uid",
        {"gid": game_id, "uid": user_id},
    )
    res = c.fetchone()

    return {"gameResults": res}
