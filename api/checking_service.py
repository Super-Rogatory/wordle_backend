from fastapi import FastAPI
from utils import start_connection

app = FastAPI()

# connect to answers database
conn = start_connection(2)
c = conn.cursor()

@app.get("/")
async def root():
    return {"message": "Hello World"}
