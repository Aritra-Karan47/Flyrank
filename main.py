from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, StrictBool, StrictStr

app = FastAPI()

tasks = [
    {"id": 1, "title": "Learn FastAPI basics", "done": True},
    {"id": 2, "title": "Build CRUD endpoints", "done": False},
    {"id": 3, "title": "Test API in Swagger UI", "done": False},
]
next_id = 4


class TaskCreate(BaseModel):
    title: StrictStr


class TaskUpdate(BaseModel):
    title: Optional[StrictStr] = None
    done: Optional[StrictBool] = None


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body"},
    )


def find_task(task_id: int):
    return next((t for t in tasks if t["id"] == task_id), None)


def not_found_response(task_id: int) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return not_found_response(task_id)
    return task


@app.post("/tasks", status_code=201)
def create_task(payload: TaskCreate):
    global next_id
    title = payload.title.strip()
    if not title:
        return JSONResponse(status_code=400, content={"error": "Title must not be empty"})
    task = {"id": next_id, "title": title, "done": False}
    next_id += 1
    tasks.append(task)
    return task


@app.put("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        return not_found_response(task_id)
    if payload.title is None and payload.done is None:
        return JSONResponse(
            status_code=400,
            content={"error": "Provide at least one of 'title' or 'done' to update"},
        )
    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            return JSONResponse(status_code=400, content={"error": "Title must not be empty"})
        task["title"] = title
    if payload.done is not None:
        task["done"] = payload.done
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        return not_found_response(task_id)
    tasks.remove(task)
    return Response(status_code=204)
