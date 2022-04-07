import sqlite3

# START_CONNECTION - takes in a number n that determines which database to connect to
# returns conn object.
def start_connection(n):
    # n = 1 word_list | n = 2 answers
    options = {1: "word_list", 2: "answers"}
    # Ensures that we connect to the database.
    try:
        conn = sqlite3.connect(
            f"db/{options[n]}.db"
        )  # create connection to db on error default to except clause.
        print(f"Successfully connected to {options[n]} database.")
        return conn

    except sqlite3.Error as error:
        print("Error occurred while connecting to word list database.", error)
