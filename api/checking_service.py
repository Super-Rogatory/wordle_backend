from fastapi import FastAPI, HTTPException
from utils import start_connection
from validation_service import check_word
import random

app = FastAPI()

# connect to answers database
conn = start_connection(2)
c = conn.cursor()

# (cur_Word, id, value) in checkings database
CUR_WORD_STATUS = 0
ID = 1
WORD = 2


@app.post("/checkanswer")
async def check_answer(answer: str):
    # grab word of the day
    c.execute("SELECT * FROM answers WHERE cur_word=1")
    wordOTD = c.fetchone()[WORD]

    # use validation function to check if word is valid.
    cw = await check_word(answer)
    if not cw["isValidWord"] and answer != wordOTD:
        raise HTTPException(status_code=400, detail="Word is invalid.")

    # Word is valid from this point on. | In production replace object with a small list [1,2,3]
    statuses = {1: "absent", 2: "present", 3: "correct"}
    word_status = []  # list of objects. [{ "t", "present"}]
    index = 0
    isCorrect = False

    if answer == wordOTD:
        isCorrect = True
    else:
        for letter in answer:
            if letter == wordOTD[index]:
                word_status.append({letter: statuses[3]})
            elif wordOTD.find(letter) != -1:
                word_status.append({letter, statuses[2]})
            else:
                word_status.append({letter, statuses[1]})
            index = index + 1
    return {"answerResults": "Correct" if isCorrect else word_status}


@app.put("/changeanswer")
async def change_answer():
    # find maxId for random function
    c.execute("SELECT id FROM answers ORDER BY id DESC LIMIT 1")
    maxId = c.fetchone()[0]  # rip value from query
    randomId = random.randint(1, maxId)

    # we want to pick a different answer that we haven't chosen previously.
    while maxId == randomId:
        randomId = random.randint(1, maxId)

    # grab word of the day's id
    c.execute("SELECT * FROM answers WHERE cur_word=1")
    currentId = c.fetchone()[ID]

    # Turn current word of the day "off"
    c.execute("UPDATE answers SET cur_word=0 WHERE id=:id", {"id": currentId})

    # Turn new word of the day "on"
    c.execute("UPDATE answers SET cur_word=1 WHERE id=:id", {"id": randomId})
    c.execute("SELECT * FROM answers WHERE cur_word=1")
    answer_properties = c.fetchone()
    conn.commit()
    # Changes word of the day
    wordOTD = answer_properties[WORD]
    return {"word": wordOTD}
