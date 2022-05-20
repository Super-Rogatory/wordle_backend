from fastapi import FastAPI, HTTPException
from validation_service import check_word
from pydantic import BaseModel
import httpx

app = FastAPI()

# defines a valid game in request body
class NewGameInfo(BaseModel):
    username: str


# defines a valid game in request body
class Game(BaseModel):
    game_id: int
    finished: str
    guesses: int
    game_status: bool

@app.post("/game/new")
async def create_new_game(new_game: NewGameInfo):
    r = httpx.post(f"http://127.0.0.1:9999/api/statistics/new_game/{new_game.username}")
    return r.json()


@app.get("/game/{id}")
async def update_game(id: int):
    print(id)

@app.post("/game/{game_id}")
async def new_guess(guess: str, userid: int, game_status: Game):
    #Verify that the guess is a word allowed by the dictionary
    r = httpx.post(f"http://127.0.0.1:9999/api/validations/checkword/{guess}")
    #Check that the user has guesses remaining
    r = httpx.post(f"http://127.0.0.1:9999/api/statistics/game_result/{}")
