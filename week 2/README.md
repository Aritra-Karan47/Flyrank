# Week 2 — Task CRUD API (FastAPI)

A small in-memory To-Do list REST API built with **FastAPI** and **Python 3.11+**. It implements all four CRUD operations (`POST`, `GET`, `PUT`, `DELETE`), input validation, proper HTTP status codes (`200`, `201`, `204`, `400`, `404`), and interactive **Swagger UI** documentation at `/docs`.

> **Note:** Tasks are stored in memory only, so restarting the server resets the list back to the 3 initial sample tasks.

## Quick Start

From the `week 2` directory, install dependencies and start the server in one command:

```bash
pip install -r requirements.txt && python -m uvicorn main:app --reload
```

Once running, open:
- API Root: <http://127.0.0.1:8000/>
- Swagger UI: <http://127.0.0.1:8000/docs>

## Endpoints

| Method | Path | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API metadata (`name`, `version`, `endpoints`) | `200` |
| `GET` | `/health` | Health check (`{"status": "ok"}`) | `200` |
| `GET` | `/tasks` | List all tasks in memory | `200` |
| `GET` | `/tasks/{task_id}` | Get a single task by ID | `200`, `404` |
| `POST` | `/tasks` | Create a new task (`{"title": "..."}`) | `201`, `400` |
| `PUT` | `/tasks/{task_id}` | Update a task's `title` and/or `done` flag | `200`, `400`, `404` |
| `DELETE` | `/tasks/{task_id}` | Delete a task by ID | `204`, `404` |
| `GET` | `/docs` | Interactive Swagger UI | `200` |

## Example `curl -i` Output

Creating a new task with `POST /tasks`:

```bash
curl -i -X POST http://127.0.0.1:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
```

Response:

```http
HTTP/1.1 201 Created
date: Wed, 25 Nov 2026 19:33:52 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI Screenshot

Open <http://127.0.0.1:8000/docs> while the server is running to test all endpoints interactively with **Try it out** (and save a screenshot at `docs/swagger-ui.png`):

![Swagger UI](docs/swagger-ui.png)
