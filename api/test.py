from unittest import result
from urllib.request import Request
from fastapi import FastAPI
from utils import start_connection

app = FastAPI()


conn = start_connection(1)  # bootstraps connection to db
c = conn.cursor()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/test")
async def getAll():
    c.execute("SELECT * FROM words;")
    results = c.fetchall()
    conn.commit()
    return {"words": results}


# @app.post("/validation/checkword")
# async def check_word(request: Request):
#     print(request.body())
#     return {"message": "LOL"}
