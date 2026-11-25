from contextlib import asynccontextmanager, closing
from pathlib import Path
import sqlite3
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StrictBool, StrictStr

DB_PATH = Path(__file__).with_name("tasks.db")

SEED_TASKS = [
    ("Learn FastAPI basics", 1),
    ("Build CRUD endpoints", 0),
    ("Test API in Swagger UI", 0),
]


class TaskCreate(BaseModel):
    title: StrictStr


class TaskUpdate(BaseModel):
    title: Optional[StrictStr] = None
    done: Optional[StrictBool] = None


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def not_found_response() -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": "Task not found"})


def init_db() -> None:
    with closing(get_connection()) as conn, conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                SEED_TASKS,
            )


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task API",
    version="2.0",
    description="SQLite-backed to-do list CRUD API.",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


@app.get("/", description="Return basic API metadata and available endpoints.")
def read_root():
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/health", description="Check whether the API server is alive.")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", description="Return all tasks stored in the SQLite database.")
def list_tasks():
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        ).fetchall()
    return [row_to_task(row) for row in rows]


@app.get("/tasks/{task_id}", description="Return a single task from the database by ID.")
def get_task(task_id: int):
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
    if row is None:
        return not_found_response()
    return row_to_task(row)


@app.post("/tasks", status_code=201, description="Insert a new task into the database.")
def create_task(payload: TaskCreate):
    title = payload.title.strip()
    if not title:
        return JSONResponse(status_code=400, content={"error": "Title must not be empty"})
    with closing(get_connection()) as conn, conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, 0)",
            (title,),
        )
        task_id = cursor.lastrowid
    return {"id": task_id, "title": title, "done": False}


@app.put("/tasks/{task_id}", description="Update an existing task in the database.")
def update_task(task_id: int, payload: TaskUpdate):
    if payload.title is None and payload.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide at least one of 'title' or 'done' to update"},
        )
    new_title: Optional[str] = None
    if payload.title is not None:
        new_title = payload.title.strip()
        if not new_title:
            return JSONResponse(status_code=400, content={"error": "Title must not be empty"})

    with closing(get_connection()) as conn, conn:
        row = conn.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return not_found_response()
        updated_title = new_title if new_title is not None else row["title"]
        updated_done = int(payload.done) if payload.done is not None else row["done"]
        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (updated_title, updated_done, task_id),
        )
    return {"id": task_id, "title": updated_title, "done": bool(updated_done)}


@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task from the database.")
def delete_task(task_id: int):
    with closing(get_connection()) as conn, conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,),
        )
    if cursor.rowcount == 0:
        return not_found_response()
    return Response(status_code=204)
