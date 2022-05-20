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
    # Make an API call to check word in order to see if the guess is valid
    r = httpx.post(
        f"http://127.0.0.1:9999/api/validations/checkword?name={new_guess.guess}"
    )
    # extract boolean status from response
    is_valid_word = r.json()["isValidWord"]

    # Check that the user has guesses remaining
    # use REDIS services for tracking information. Get redis object.
    r = httpx.get(
        f"http://127.0.0.1:9999/api/trackings/get_status?user_id={new_guess.user_id}&game_id={game_id}"
    )
    guesses_left = r.json()[f"game-{game_id}"]["guesses_left"]
    has_guesses_left = False if guesses_left == 0 else True

    # before checking if word is valid, make sure there are guesses left.
    if has_guesses_left is not True:
        # TODO: when guesses is 1, on an incorrect guess save object as a LOSS, get the current date, update sql database, return sql object.
        # TODO: fetch sql object everytime this condition is met.
        return 0
    # if word is invalid return error object
    if is_valid_word is not True:
        raise HTTPException(
            status_code=400, detail={"status": "invalid", "remaining": guesses_left}
        )

    # Record the guess and update the number of guesses remaining
    # create game_info object,for the body of post request
    game_info = {"user_id": str(new_guess.user_id), "game_id": game_id}
    # Using add_word function in tracking_service to handle recording the guess and returning number of guesses remaining
    r = httpx.post(
        f"http://127.0.0.1:9999/api/trackings/guess?guess={new_guess.guess}",
        json=game_info,
    )
    guesses_left = r.json()[f"game-{game_id}"]["guesses_left"]

    # TODO: if guesses_left is 0, save object as a LOSS, get the current date, update sql database, return sql object.

    # Check to see if the guess is correct
    r = httpx.post(
        f"http://127.0.0.1:9999/api/checkings/checkanswer?answer={new_guess.guess}"
    )
    answer_res = r.json()["answerResults"]
    if answer_res == "Correct":
        # TODO: save object as a WIN, update sql database, return sql object
        return "win"

    # if have gotten to this point, the user has guesses remaining, and has not yet won!
    return {"status": "incorrect", "remaining": guesses_left, "letters": answer_res}
