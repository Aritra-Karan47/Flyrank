from typing import Optional

from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StrictBool, StrictStr

from service import TaskNotFoundError, TaskService, ValidationError


class TaskCreate(BaseModel):
    title: StrictStr


class TaskUpdate(BaseModel):
    title: Optional[StrictStr] = None
    done: Optional[StrictBool] = None


def create_router(service: TaskService) -> APIRouter:
    """Build HTTP endpoints bound to a TaskService without storage coupling."""
    router = APIRouter()

    @router.get("/", description="Return basic API metadata and available endpoints.")
    def read_root():
        return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks"]}

    @router.get("/health", description="Check whether the API server is alive.")
    def health_check():
        return {"status": "ok"}

    @router.get("/tasks", description="Return all tasks from the configured repository.")
    def list_tasks():
        return service.list_tasks()

    @router.get("/tasks/{task_id}", description="Return a single task by ID.")
    def get_task(task_id: int):
        try:
            return service.get_task(task_id)
        except TaskNotFoundError as exc:
            return JSONResponse(status_code=404, content={"error": str(exc)})

    @router.post("/tasks", status_code=201, description="Create a new task.")
    def create_task(payload: TaskCreate):
        try:
            return service.create_task(payload.title)
        except ValidationError as exc:
            return JSONResponse(status_code=400, content={"error": str(exc)})

    @router.put("/tasks/{task_id}", description="Update an existing task.")
    def update_task(task_id: int, payload: TaskUpdate):
        try:
            return service.update_task(task_id, payload.title, payload.done)
        except ValidationError as exc:
            return JSONResponse(status_code=400, content={"error": str(exc)})
        except TaskNotFoundError as exc:
            return JSONResponse(status_code=404, content={"error": str(exc)})

    @router.delete("/tasks/{task_id}", status_code=204, description="Delete a task by ID.")
    def delete_task(task_id: int):
        try:
            service.delete_task(task_id)
            return Response(status_code=204)
        except TaskNotFoundError as exc:
            return JSONResponse(status_code=404, content={"error": str(exc)})

    return router
