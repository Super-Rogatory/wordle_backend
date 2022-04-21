from datetime import date
from fastapi import FastAPI, HTTPException
from utils import (
    start_connection,
    validate_game_result,
    get_streak,
    get_guesses,
    analyze_guess_data,
)
from pydantic import BaseModel


class Game(BaseModel):
    game_id: int
    finished: str
    guesses: int
    game_status: bool


app = FastAPI()

# connect to statistics database
conn = start_connection(3)
c = conn.cursor()


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
    # execute query to finished|guesses|won
    c.execute(
        """
            SELECT finished, guesses, won
            FROM games g
            WHERE user_id=:uid 
            ORDER BY finished
        """,
        {"uid": user_id},
    )
    res = c.fetchall()
    # use helper functions to parse data instead of making extra calls to db
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


"""
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


@app.post("/statistics/game_result/{user_id}")
async def game_result(user_id: int, game: Game):
    # validate query
    isValid = validate_game_result(game.game_status, game.finished, game.guesses)
    if not isValid:
        raise HTTPException(status_code=400, detail="Query is invalid.")

    # avoiding duplicate dates - doesn't make sense for wordle game.
    c.execute(
        "SELECT * FROM games WHERE finished=:date_finished AND user_id=:uid",
        {"date_finished": game.finished, "uid": user_id},
    )
    res = c.fetchall()
    if len(res):
        raise HTTPException(status_code=400, detail="Duplicate dates error.")

    # uid and gid uniquely identify game, update properties
    c.execute(
        """
            INSERT INTO games
            VALUES (:uid, :gid, :finished, :guesses, :won) 
        """,
        {
            "uid": user_id,
            "gid": game.game_id,
            "finished": game.finished,
            "guesses": game.guesses,
            "won": game.game_status,
        },
    )
    conn.commit()
    # retreive information after update to ensure it has updated.
    c.execute(
        "SELECT * FROM games WHERE game_id=:gid AND user_id=:uid",
        {"gid": game.game_id, "uid": user_id},
    )
    res = c.fetchone()

    return {"gameResults": res}
