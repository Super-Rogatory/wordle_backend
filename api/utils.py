import sqlite3
import re

# START_CONNECTION - takes in a number n that determines which database to connect to
# returns conn object.
def start_connection(n):
    # n = 1 word_list | n = 2 answers
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


# VALIDATE_GAME_RESULT - takes in specified parameters that are validated to ensure data consistency
def validate_game_result(status, finished, guesses):
    isValid = True
    # if guesses or status isn't in a valid range
    if guesses not in range(1, 7) or status not in range(0, 2):
        isValid = False
    # if date doesn't match regex..
    if re.search("^\d{4}-\d{2}-\d{2}$", finished) == None:
        isValid = False
    return isValid


# GET_STREAK - takes in array of streak tuples and returns cur_streak, max_streak
def get_streak(streaks):
    cur_streak = 0
    max_streak = 0
    for (streak, _, _) in streaks:
        cur_streak = 0 if streak == None else streak
        if cur_streak > max_streak:
            max_streak = streak
    return (cur_streak, max_streak)


# GET_GUESSES - takes in array of streak tuples and returns a guess_object.
def get_guesses(streaks):
    guess_obj = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "fail": 0}
    for (_, guess, won) in streaks:
        if won == 0:
            guess_obj["fail"] += 1
        guess_obj[str(guess)] += 1
    return guess_obj
