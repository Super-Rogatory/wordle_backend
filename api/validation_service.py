from fastapi import FastAPI, HTTPException
from utils import start_connection

app = FastAPI()


conn = start_connection(1)  # bootstraps connection to db
c = conn.cursor()

# (id, value) in validation database
ID = 0
WORD = 1


@app.post("/checkword")
async def check_word(name: str):
    c.execute("SELECT DISTINCT * FROM words WHERE name=:name LIMIT 1", {"name": name})
    isValid = len(c.fetchall())  # returns 0 or 1 depending on if word exists.
    status = isValid == 1  # True or False
    conn.commit()
    return {"isValidWord": status}


@app.post("/addword", status_code=201)
async def add_word(name: str):
    # if length does not match five-letter requirement - raise error
    if len(name.strip()) != 5:
        raise HTTPException(
            status_code=400, detail="Malformed request syntax - check length of word."
        )

    # checks to see if word is already in the database - if it is return 400 status code
    c.execute("SELECT DISTINCT * FROM words WHERE name=:name LIMIT 1", {"name": name})
    doesWordExist = len(c.fetchall()) > 0
    if doesWordExist == True:
        raise HTTPException(
            status_code=400, detail="Word already exists in the database."
        )

    # if all goes well - continue here.
    # query to get highest id.
    c.execute("SELECT id FROM words ORDER BY id DESC LIMIT 1")
    maxId = c.fetchone()[ID]  # rip value from query
    obj = {"id": maxId + 1, "name": name}
    c.execute(
        "INSERT INTO words VALUES(:id, :name)", {"id": obj["id"], "name": obj["name"]}
    )
    conn.commit()
    return {"word": obj}


@app.delete("/removeword", status_code=204)
async def remove_word(name: str):
    c.execute("DELETE FROM words WHERE name=:name", {"name": name})
    conn.commit()
