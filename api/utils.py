from multipledispatch import dispatch
import sqlite3
import re
from datetime import date, timedelta


@dispatch(int)
# START_CONNECTION - takes in a number n that determines which database to connect to
# returns conn object.
def start_connection(n):
    # n = 1 word_list | n = 2 answers | n = 3 statistics
    options = {1: "word_list", 2: "answers", 3: "statistics"}
    # Ensures that we connect to the database.
    try:
        conn = sqlite3.connect(
            f"db/{options[n]}.db"
        )  # create connection to db on error default to except clause.
        print(f"Successfully connected to {options[n]} database.")
        return conn

    except sqlite3.Error as error:
        print("Error occurred while connecting to word list database.", error)


@dispatch(str)
# START_CONNECTION - takes the name of a database to connect to
def start_connection(name=""):
    if not name:
        return
    # Ensures that we connect to the database.
    try:
        conn = sqlite3.connect(
            f"db/{name}.db", detect_types=sqlite3.PARSE_DECLTYPES
        )  # create connection to db on error default to except clause.
        print(f"Successfully connected to {name} database.")
        return conn

    except sqlite3.Error as error:
        print("Error occurred while connecting to word list database.", error)


# VALIDATE_GAME_RESULT - takes in specified parameters that are validated to ensure data consistency
def validate_game_result(status, finished, guesses):
    today = date.today().strftime("%Y-%m-%d")
    isValid = True
    # if guesses or status isn't in a valid range
    if guesses not in range(1, 7) or status not in range(0, 2):
        isValid = False
    # if date doesn't match regex..
    if re.search("^\d{4}-\d{2}-\d{2}$", finished) == None:
        isValid = False
    # if finished_date is ahead of present time..
    if finished > today:
        isValid = False
    return isValid


# GET_STREAK - takes in array of streak tuples and returns cur_streak, max_streak
def get_streak(query):
    print(query)
    FINISHED_DATE = 0
    GAME_STATUS = 2
    cur_streak = 0
    max_streak = 0
    # next_date = prev_date + timedelta(days=1)
    for i in range(0, len(query) - 1):
        # get prev date and cur date.
        prev_date = date.fromisoformat(query[i][FINISHED_DATE])
        cur_date = date.fromisoformat(query[i + 1][FINISHED_DATE])
        game_won = query[i + 1][GAME_STATUS]
        # check to see if next date is one day from cur date
        if prev_date + timedelta(days=1) == cur_date and game_won:
            cur_streak += 1
        else:
            if game_won:
                cur_streak = 1
            else:
                cur_streak = 0
        # set max streak to cur streak if cur streak is new max.
        if cur_streak > max_streak:
            max_streak = cur_streak

    # for (streak, _, _) in streaks:
    #     cur_streak = 0 if streak == None or streak == 0 else streak
    #     if cur_streak > max_streak:
    #         max_streak = streak
    return (cur_streak, max_streak)


get_streak(
    [
        ("2022-01-09", 6, 1),
        ("2022-01-29", 5, 0),
        ("2022-02-04", 5, 0),
        ("2022-02-08", 2, 1),
        ("2022-02-16", 6, 1),
        ("2022-02-24", 4, 1),
        ("2022-03-03", 2, 1),
        ("2022-03-05", 6, 1),
        ("2022-03-14", 3, 1),
        ("2022-04-01", 2, 1),
        ("2022-04-02", 1, 1),
        ("2022-04-03", 1, 1),
        ("2022-04-04", 1, 1),
        ("2022-04-05", 1, 1),
        ("2022-04-06", 3, 0),
        ("2022-04-07", 3, 1),
        ("2022-04-08", 3, 1),
    ]
)
# GET_GUESSES - takes in array of streak tuples and returns a guess_object.
def get_guesses(streaks):
    guess_obj = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "fail": 0}
    for (_, guess, won) in streaks:
        if won == 0:
            guess_obj["fail"] += 1
        else:
            guess_obj[str(guess)] += 1
    return guess_obj


# ANALYZE GUESS DATA - takes in the guess_object and parses it for relevant data.
def analyze_guess_data(guess_obj):
    wins = 0
    losses = 0
    avg_guesses = 0
    for (key, value) in guess_obj.items():
        if key == "fail":
            losses += value
        else:
            wins += value
            avg_guesses += int(key) * value  # 1 * 4 + 2 * 2 ... x/6
    total = wins + losses
    win_percentage = round(wins / total, 1) * 100  # calculate win percentage
    avg_guesses = round(avg_guesses / wins)
    return (win_percentage, total, wins, avg_guesses)
