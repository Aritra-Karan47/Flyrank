from contextlib import closing
from typing import Optional, Protocol

import psycopg2
from psycopg2.extras import RealDictCursor


class TaskRepository(Protocol):
    """Storage interface shared by in-memory and Postgres task repositories."""

    def list_tasks(self) -> list[dict]: ...

    def get_task(self, task_id: int) -> Optional[dict]: ...

    def create_task(self, title: str) -> dict: ...

    def update_task(
        self,
        task_id: int,
        title: Optional[str],
        done: Optional[bool],
    ) -> Optional[dict]: ...

    def delete_task(self, task_id: int) -> bool: ...


class InMemoryTaskRepository:
    """In-memory task repository (from A2) kept as a drop-in reference."""

    def __init__(self) -> None:
        self._tasks = [
            {"id": 1, "title": "Learn FastAPI basics", "done": True},
            {"id": 2, "title": "Build CRUD endpoints", "done": False},
            {"id": 3, "title": "Test API in Swagger UI", "done": False},
        ]
        self._next_id = 4

    def list_tasks(self) -> list[dict]:
        return [dict(task) for task in self._tasks]

    def get_task(self, task_id: int) -> Optional[dict]:
        task = next((t for t in self._tasks if t["id"] == task_id), None)
        return dict(task) if task is not None else None

    def create_task(self, title: str) -> dict:
        task = {"id": self._next_id, "title": title, "done": False}
        self._next_id += 1
        self._tasks.append(task)
        return dict(task)

    def update_task(
        self,
        task_id: int,
        title: Optional[str],
        done: Optional[bool],
    ) -> Optional[dict]:
        task = next((t for t in self._tasks if t["id"] == task_id), None)
        if task is None:
            return None
        if title is not None:
            task["title"] = title
        if done is not None:
            task["done"] = done
        return dict(task)

    def delete_task(self, task_id: int) -> bool:
        task = next((t for t in self._tasks if t["id"] == task_id), None)
        if task is None:
            return False
        self._tasks.remove(task)
        return True


class PostgresTaskRepository:
    """PostgreSQL implementation of TaskRepository using psycopg2."""

    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def _connect(self):
        return psycopg2.connect(self._database_url, cursor_factory=RealDictCursor)

    @staticmethod
    def _to_dict(row: dict) -> dict:
        return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

    def list_tasks(self) -> list[dict]:
        with closing(self._connect()) as conn, conn, conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks ORDER BY id")
            rows = cur.fetchall()
        return [self._to_dict(row) for row in rows]

    def get_task(self, task_id: int) -> Optional[dict]:
        with closing(self._connect()) as conn, conn, conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
            row = cur.fetchone()
        return self._to_dict(row) if row is not None else None

    def create_task(self, title: str) -> dict:
        with closing(self._connect()) as conn, conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, FALSE) RETURNING id, title, done",
                (title,),
            )
            row = cur.fetchone()
        return self._to_dict(row)

    def update_task(
        self,
        task_id: int,
        title: Optional[str],
        done: Optional[bool],
    ) -> Optional[dict]:
        with closing(self._connect()) as conn, conn, conn.cursor() as cur:
            cur.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
            existing = cur.fetchone()
            if existing is None:
                return None
            new_title = title if title is not None else existing["title"]
            new_done = done if done is not None else existing["done"]
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
                (new_title, new_done, task_id),
            )
            row = cur.fetchone()
        return self._to_dict(row)

    def delete_task(self, task_id: int) -> bool:
        with closing(self._connect()) as conn, conn, conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
            return cur.rowcount > 0
