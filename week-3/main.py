from contextlib import asynccontextmanager, closing
from pathlib import Path
import sqlite3

from fastapi import FastAPI
from fastapi.responses import JSONResponse

DB_PATH = Path(__file__).with_name("tasks.db")

SEED_TASKS = [
    ("Learn FastAPI basics", 1),
    ("Build CRUD endpoints", 0),
    ("Test API in Swagger UI", 0),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def row_to_task(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


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
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    return row_to_task(row)
