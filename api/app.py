from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
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
    if "obj" in res:
        # use object properties to populate return value
        user_info_obj = res["obj"][0]
        user_id = user_info_obj[0]
        game_id = user_info_obj[1]
        r = httpx.get(
            f"http://127.0.0.1:9999/api/trackings/get_status?user_id={user_id}&game_id={game_id}"
        )
        guesses_left = r.json()[f"game-{game_id}"]["guesses_left"]
        words_guessed = r.json()[f"game-{game_id}"]["words_guessed"]
        return {
            "status": res["status"],
            "user_id": user_id,
            "game_id": game_id,
            "remaining": guesses_left,
            "guesses": words_guessed,
        }
    # start up tracking service with redis if all else is valid
    game_info = {"user_id": res["user_id"], "game_id": res["game_id"]}
    r = httpx.post(f"http://127.0.0.1:9999/api/trackings/start_game", json=game_info)
    return res


@app.post("/game/{game_id}")
async def new_guess(game_id: int, new_guess: NewGuessInfo):
    # get current date
    today = date.today()

    # check if user won already. if so do nothing
    r = httpx.get(
        f"http://127.0.0.1:9999/api/statistics/checkwin?user_id={new_guess.user_id}&game_id={game_id}"
    )
    if r.json()["status"] == True:
        return "Thank you for playing Wordle! Come back tomorrow and play again! :)"

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
    # if user has no guesses left OR tries to play twice in a day.
    if "detail" in r.json():
        return "Thank you for playing Wordle! Come back tomorrow and play again! :)"

    guesses_left = r.json()[f"game-{game_id}"]["guesses_left"]
    # Check to see if the guess is correct
    r = httpx.post(
        f"http://127.0.0.1:9999/api/checkings/checkanswer?answer={new_guess.guess}"
    )
    answer_res = r.json()["answerResults"]
    # TODO: if guesses_left is 0, save object as a LOSS, use the current date to update sql database, return sql object.
    # TODO: if guess is correct, save object as a WIN, use the current date to update sql database, return sql object.
    if answer_res == "Correct":
        # TODO: save object as a WIN, update sql database, return sql object
        game_results = {
            "game_id": game_id,
            "finished": str(today),
            "guesses": guesses_left,
            "game_status": True,
        }
        # update sql database
        r = httpx.post(
            f"http://127.0.0.1:9999/api/statistics/game_result/save/{new_guess.user_id}",
            json=game_results,
        )
        # get new user stats
        r = httpx.get(
            f"http://127.0.0.1:9999/api/statistics/get_stats/{new_guess.user_id}"
        )
        stats = r.json()
        return {
            "status": "win",
            "remaining": guesses_left,
            "currentStreak": stats["currentStreak"],
            "maxStreak": stats["maxStreak"],
            "guesses": stats["guesses"],
            "winPercentage": stats["winPercentage"],
            "gamesPlayed": stats["gamesPlayed"],
            "gamesWon": stats["gamesWon"],
            "averageGuesses": stats["averageGuesses"],
        }
    elif guesses_left == 0:
        game_results = {
            "game_id": game_id,
            "finished": str(today),
            "guesses": guesses_left,
            "game_status": False,
        }
        # update sql database
        r = httpx.post(
            f"http://127.0.0.1:9999/api/statistics/game_result/save/{new_guess.user_id}",
            json=game_results,
        )
        # get new user stats
        r = httpx.get(
            f"http://127.0.0.1:9999/api/statistics/get_stats/{new_guess.user_id}"
        )
        stats = r.json()
        return {
            "status": "loss",
            "remaining": guesses_left,
            "currentStreak": stats["currentStreak"],
            "maxStreak": stats["maxStreak"],
            "guesses": stats["guesses"],
            "winPercentage": stats["winPercentage"],
            "gamesPlayed": stats["gamesPlayed"],
            "gamesWon": stats["gamesWon"],
            "averageGuesses": stats["averageGuesses"],
        }
    # if have gotten to this point, the user has guesses remaining, and has not yet won!
    return {"status": "incorrect", "remaining": guesses_left, "letters": answer_res}
