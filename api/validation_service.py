from fastapi import FastAPI
from utils import start_connection

app = FastAPI()


conn = start_connection(1)  # bootstraps connection to db
c = conn.cursor()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/validation/checkword")
async def check_word(name: str):
    c.execute("SELECT * FROM words WHERE name=:name", {"name": name})
    isValid = len(c.fetchall())  # returns 0 or 1 depending on if word exists.
    status = str(isValid == 1)  # string True or False
    conn.commit()
    return {"isValidWord": status}
