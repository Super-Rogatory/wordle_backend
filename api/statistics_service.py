import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from utils import (
    start_connection,
    validate_game_result,
    get_streak,
    get_guesses,
    analyze_guess_data,
)
from pydantic import BaseModel, BaseSettings


class Game(BaseModel):
    game_id: int
    finished: str
    guesses: int
    game_status: bool


class Settings(BaseSettings):
    name_of_db: str


app = FastAPI()
settings = Settings()


def get_db():
    try:
        db = start_connection(settings.name_of_db)
        return db
    except:
        print("Error connecting to the db!")


@app.get("/")
async def get_all():
    try:
        db = get_db()
        c = db.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name = c.fetchone()[0]
        c.execute(f"SELECT game_id FROM {table_name} LIMIT 10")
        print(c.fetchall())
    except Exception as e:
        print(f"ERROR in get_all function! => {e}")
    finally:
        db.close()


# every route connects to a db, depending on env
@app.get("/statistics/top_ten_in_wins")
async def get_top_ten_in_wins(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute(
        """
            SELECT username FROM users JOIN wins USING(user_id) ORDER BY 'COUNT(won)' DESC LIMIT 10
        """
    )
    res = c.fetchall()
    return {"users": res}


@app.get("/statistics/top_ten_in_streaks")
async def get_top_ten_in_streaks(db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute(
        """
            SELECT username FROM users JOIN streaks USING(user_id) ORDER BY streak DESC LIMIT 10
        """
    )
    res = c.fetchall()
    return {"users": res}


@app.get("/statistics/{user_id}")
async def get_statistics(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    # execute query to finished|guesses|won
    c = db.cursor()
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
async def game_result(
    user_id: int, game: Game, db: sqlite3.Connection = Depends(get_db)
):
    c = db.cursor()
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
    db.commit()
    # retreive information after update to ensure it has updated.
    c.execute(
        "SELECT * FROM games WHERE game_id=:gid AND user_id=:uid",
        {"gid": game.game_id, "uid": user_id},
    )
    res = c.fetchone()

    return {"gameResults": res}
