from uuid import uuid4
from fastapi import FastAPI, HTTPException
from validation_service import check_word
from pydantic import BaseModel
import httpx
import uuid

app = FastAPI()

# defines a valid game in request body
class NewGameInfo(BaseModel):
    username: str


class NewGuessInfo(BaseModel):
    user_id: uuid.UUID
    guess: str


@app.post("/game/new")
async def create_new_game(new_game: NewGameInfo):
    # create game in the database for persistent storage
    r = httpx.post(f"http://127.0.0.1:9999/api/statistics/new_game/{new_game.username}")
    res = r.json()
    # an error attribute is return if there is a user who game is not finished yet for that day.
    if "detail" in res:
        return res["detail"]
    # start up tracking service with redis if all else is valid
    game_info = {"user_id": res["user_id"], "game_id": res["game_id"]}
    r = httpx.post(f"http://127.0.0.1:9999/api/trackings/start_game", json=game_info)
    return res


@app.post("/game/{game_id}")
async def new_guess(game_id: int, new_guess: NewGuessInfo):
    # Verify that the guess is a word allowed by the dictionary
    # http://127.0.0.1:9999/api/validations/checkword?name=table
    r = httpx.post(
        f"http://127.0.0.1:9999/api/validations/checkword?name={new_guess.guess}"
    )
    is_valid_word = r.json()["isValidWord"]
    # Check that the user has guesses remaining
    #     {
    #   "game_id": 0,
    #   "finished": "string",
    #   "guesses": 0,
    #   "game_status": true
    # }

    # r = httpx.post(f"http://127.0.0.1:9999/api/statistics/game_result/{}")

    if is_valid_word is not True:
        raise HTTPException(
            status_code=400, detail={"status": "invalid", "remaining": "TODO"}
        )
