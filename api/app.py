from fastapi import FastAPI, HTTPException
from validation_service import check_word
from pydantic import BaseModel
import httpx

app = FastAPI()

# defines a valid game in request body
class NewGameInfo(BaseModel):
    username: str


@app.post("/game/new")
async def create_new_game(new_game: NewGameInfo):
    r = httpx.post(f"http://127.0.0.1:9999/api/statistics/new_game/{new_game.username}")
    return r.json()


@app.get("/game/{id}")
async def update_game(id: int):
    print(id)
