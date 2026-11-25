from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3

from fastapi import FastAPI

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


def init_db() -> None:
    with get_connection() as conn:
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
