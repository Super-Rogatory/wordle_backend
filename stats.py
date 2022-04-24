import sqlite3
import contextlib
import logging.config

from fastapi import FastAPI, Depends, Response, HTTPException, status, Request
from pydantic import BaseSettings


class Settings(BaseSettings):
    database: str
    logging_config: str

    class Config:
        env_file = "stats.env"


settings = Settings()
app = FastAPI(openapi_url="/api/v1/openapi.json")


def get_db():
    with contextlib.closing(sqlite3.connect(settings.database)) as db:
        db.row_factory = sqlite3.Row
        yield db


@app.get("/users")
def list_users(db: sqlite3.Connection = Depends(get_db)):
    users = db.execute("SELECT * FROM users")
    return {"user": users.fetchall()}
