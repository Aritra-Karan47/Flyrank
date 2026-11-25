from typing import Optional

from repository import TaskRepository


class ValidationError(Exception):
    """Raised when task input violates business rules."""


class TaskNotFoundError(Exception):
    """Raised when a requested task ID does not exist."""


class TaskService:
    """Storage-agnostic business logic layer for managing tasks."""

    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo

    def list_tasks(self) -> list[dict]:
        return self._repo.list_tasks()

    def get_task(self, task_id: int) -> dict:
        task = self._repo.get_task(task_id)
        if task is None:
            raise TaskNotFoundError("Task not found")
        return task

    def create_task(self, title: str) -> dict:
        cleaned = title.strip()
        if not cleaned:
            raise ValidationError("Title must not be empty")
        return self._repo.create_task(cleaned)

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        done: Optional[bool] = None,
    ) -> dict:
        if title is None and done is None:
            raise ValidationError("Provide at least one of 'title' or 'done' to update")
        cleaned_title: Optional[str] = None
        if title is not None:
            cleaned_title = title.strip()
            if not cleaned_title:
                raise ValidationError("Title must not be empty")
        task = self._repo.update_task(task_id, cleaned_title, done)
        if task is None:
            raise TaskNotFoundError("Task not found")
        return task

    def delete_task(self, task_id: int) -> None:
        deleted = self._repo.delete_task(task_id)
        if not deleted:
            raise TaskNotFoundError("Task not found")
