from fastapi import FastAPI
from utils import start_connection

app = FastAPI()


conn = start_connection(1)  # bootstraps connection to db
c = conn.cursor()
c.execute("SELECT * FROM words;")
print(c.fetchall())


@app.get("/")
async def root():
    return {"message": "Hello World"}


conn.close()
