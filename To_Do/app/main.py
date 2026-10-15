from contextlib import asynccontextmanager
from pathlib import Path
import _sqlite3

from fastapi import FastApi,HTTPException, status 
from fastapi.responses import FileResponse
from fastapi.staticfile import StaticFiles
from pydantic import BaseModel, Field

from app.database import get_connection, init_db

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR =BASE_DIR / "frontend"

@asynccontextmanager
async def lifspan(app:FastApi):
    init_db()
    yield

app=FastApi(
    title="MY TO_DO",
    version="1.0.0",
    lifspan=lifspan,
)

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="Static",
)

class TaskCreate(BaseModel):
    title: str= Field(min_length=1,max_length=200)

class TaskUpdate(BaseModel):
    completed: bool

def serialize_task(row: _sqlite3.Row) -> dict:
    return {
        "id":row[id],
        "title":row["title"],
        "completed":bool(row["completed"]),
    }

@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR/ "index.html")

@app.get("/api/tasks")
def get_task():
    with get_connection() as connection:
        rows=connection.execute(
            "Select id, title, Complete From Task"
        ).fetchall()
    return [serialize_task(row) for row in rows]

@app.post("/api/task",status_code=201)
def create_task(task:TaskCreate):
    title=task.title.strip()