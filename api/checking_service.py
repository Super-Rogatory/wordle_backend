from fastapi import FastAPI, HTTPException
from utils import start_connection
from validation_service import check_word

app = FastAPI()

# connect to answers database
conn = start_connection(2)
c = conn.cursor()

# select word of the day
# c.execute("SELECT * FROM answers ORDER BY RANDOM() LIMIT 1")
# wordOTD = c.fetchone()[1]
wordOTD = "tread"


@app.post("/checking/checkanswer")
async def check_answer(answer: str):
    # use validation function to check if word is valid.
    cw = await check_word(answer)
    if not cw["isValidWord"]:
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


# @app.post("/checking/changeanswer"):
# async def change_answer(answer: str):
#     # use validation function to check if word is valid.
#     cw = await check_word(answer)
#     if not cw["isValidWord"]:
#         raise HTTPException(status_code=400, detail="Word is invalid.")
