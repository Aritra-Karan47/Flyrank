import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from repository import PostgresTaskRepository
from routes import create_router
from service import TaskService

load_dotenv(Path(__file__).with_name(".env"))


def create_app(repo=None) -> FastAPI:
    """Wire repository -> service -> routes into a FastAPI application."""
    application = FastAPI(
        title="Task API",
        version="3.0",
        description="PostgreSQL-backed to-do list CRUD API running in Docker.",
    )

    @application.exception_handler(RequestValidationError)
    def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=400, content={"error": "Invalid request body"})

    if repo is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is required")
        repo = PostgresTaskRepository(database_url)

    task_service = TaskService(repo)
    application.include_router(create_router(task_service))
    return application


app = create_app()
