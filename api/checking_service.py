from fastapi import FastAPI
from utils import start_connection

app = FastAPI()

# connect to answers database
conn = start_connection(2)
c = conn.cursor()

# select word of the day
c.execute("SELECT * FROM answers ORDER BY RANDOM() LIMIT 1")
wordOTD = c.fetchone()[1]

@app.get("/")
async def root():
    return {"word of the day": wordOTD}

@app.post("/checking/checkanswer")
async def check_answer(answer: str):
    isCorrect= str(answer == wordOTD)  # returns True or False if answer is correct
    conn.commit()
    return {"isAnswerCorrect": isCorrect}
