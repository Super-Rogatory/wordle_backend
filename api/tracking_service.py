from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import validate_client
import redis
import json

app = FastAPI()
# start connection to redis server
r = redis.Redis(host="localhost", port=6379, db=0)

# defines a new game in request body
class Client(BaseModel):
    user_id: int
    game_id: int


# Format
# user_1 = {
#   game_<id>: {
#       data including number of guesses, boardState
#   },
#   game_<id>: {
#       data including number of guesses, boardState
#   }
# }

# redis-cli: HMGET <user_id> <game_id> should return the game info

# Functionality for returning game status
@app.get("/get_status")
async def add_guess(user_id: int, game_id: int):
    res = r.hmget(user_id, game_id)
    # if game is already played return error
    if res[0] == None:
        raise HTTPException(status_code=400, detail="User has not started this game.")
    # gets game object from redis
    game_information = json.loads(res[0])

    return {f"game-{game_id}": game_information}


# Functionality for starting a new game
@app.post("/start_game")
async def start_game(client: Client):
    valid_user = validate_client(client)
    res = r.hmget(client.user_id, client.game_id)
    # if game is already played return error
    if res[0] != None or not valid_user:
        raise HTTPException(
            status_code=400,
            detail="Could not start the game for this user. Check client information.",
        )

    # create new game in json format so it can be set in redis
    new_game = {
        "user_id": client.user_id,
        "guesses_left": 6,
        "words_guessed": [],
    }
    mapping = json.dumps(new_game)

    # set the new game object with user_id as the key
    r.hmset(
        client.user_id,
        {client.game_id: mapping},
    )
    return {f"game-{client.game_id}": new_game}


# Functionality for updating a game status
@app.post("/guess")
async def add_guess(guess: str, client: Client):
    valid_user = validate_client(client)
    res = r.hmget(client.user_id, client.game_id)
    # if game is already played return error
    if res[0] == None or not valid_user:
        raise HTTPException(
            status_code=400, detail="Failed to add guess. Check client information."
        )
    # gets game object from redis
    game_information = json.loads(res[0])
    if game_information["guesses_left"] == 0:
        raise HTTPException(status_code=400, detail="User has no guesses left")
    # modifies game_information
    game_information["guesses_left"] -= 1
    game_information["words_guessed"].append(guess)
    # save changes
    mapping = json.dumps(game_information)
    r.hmset(
        client.user_id,
        {client.game_id: mapping},
    )
    return {f"game-{client.game_id}": game_information}
