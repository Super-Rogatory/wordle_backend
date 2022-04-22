import sqlite3
import uuid
from faker import Faker
from faker.factory import Factory
import sqlite_utils
import datetime
from datetime import date, timedelta
import collections

# use UUID in table
sqlite3.register_converter("GUID", lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)

# use faker to create fake user and game data
Faker = Factory.create
fake = Faker()
fake.seed(0)

num_users = 1000

fake_users = [
    {
        "user_id": str(uuid.uuid4()),
        "username": fake.user_name(),
    }
    for x in range(num_users)
]

# add fake users to users table
db = sqlite_utils.Database("./var/users.db")
db["users"].insert_all(fake_users)


# faker date_between() etc functions not working
start_date = datetime.date(2022, 1, 1)
end_date = datetime.date.today()
day_range = (end_date - start_date).days

shards = 3
shard_games = collections.defaultdict(list)


def getShardId(string_uuid):
    curr_uuid = uuid.UUID(string_uuid)
    return curr_uuid.int % shards


for i in range(num_users):
    user_id = fake_users[i].get("user_id")
    # generate games for this user
    games_played = fake.random_int(min=50, max=500)
    game_id = 0
    user_game = []
    for i in range(games_played):
        game_id += 1
        game = {
            "user_id": user_id,
            "game_id": game_id,
            "finished": (
                start_date
                + datetime.timedelta(days=fake.random_int(min=0, max=day_range))
            ),
            "guesses": fake.random_int(min=1, max=6),
            "won": fake.boolean(chance_of_getting_true=75),
        }
    # enter user's game into the correct shard
    shard_id = getShardId(user_id)
    shard_games[shard_id].append(game)


# add fake games to games table
games_db = ["./var/games0.db", "./var/games1.db", "./var/games2.db"]

for i in range(shards):
    db = sqlite_utils.Database(games_db[i])
    db["games"].insert_all(shard_games[i])
