from fastapi import FastAPI, HTTPException
from utils import (
    start_connection,
    validate_game_result,
    get_streak,
    get_guesses,
    analyze_guess_data,
)
from datetime import datetime
import json

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
CREATE VIEW streaks
AS
    SELECT
        user_id,
        COUNT(*) AS streak,
        MIN(finished) AS beginning,
        MAX(finished) AS ending
    FROM
        groups
    GROUP BY
        user_id, base_date
    HAVING
        streak > 1
    ORDER BY
        user_id,
        finished
/* streaks(user_id,streak,beginning,ending) */;    
"""


@app.get("/statistics/top_ten_in_wins")
async def get_top_ten_in_wins():
    c.execute(
        """
            SELECT username FROM users JOIN wins USING(user_id) ORDER BY 'COUNT(won)' DESC LIMIT 10
        """
    )
    res = c.fetchall()
    return {"users": res}


@app.get("/statistics/top_ten_in_streaks")
async def get_top_ten_in_streaks():
    c.execute(
        """
            SELECT username FROM users JOIN streaks USING(user_id) ORDER BY streak DESC LIMIT 10
        """
    )
    res = c.fetchall()
    return {"users": res}


@app.get("/statistics/{user_id}")
async def get_statistics(user_id: int):
    # execute query to streak|guesses|won
    c.execute(
        """
            SELECT streak, guesses, won
            FROM games g
            LEFT JOIN streaks s
            USING(user_id)
            WHERE user_id=:uid 
            ORDER BY beginning DESC
        """,
        {"uid": user_id},
    )
    res = c.fetchall()
    (cur_streak, max_streak) = get_streak(res)
    guesses = get_guesses(res)
    (win_percentage, games_played, games_won, avg_guesses) = analyze_guess_data(guesses)
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
