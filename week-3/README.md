# Week 3 — Task CRUD API with PostgreSQL & Docker Compose

A continuation of the Week 3 Task CRUD API that runs **PostgreSQL in Docker** with a named volume, loads configuration from `.env`, initializes the database schema via `init.sql`, swaps the in-memory repository for `PostgresTaskRepository` without touching the service or route layers, and launches the whole stack with `docker compose up`.

## Architecture & Repository Swap

The API is split into three clean layers inside `week-3/`:

- [`routes.py`](routes.py) — FastAPI HTTP endpoints (`GET /`, `GET /health`, `GET /tasks`, `GET /tasks/{task_id}`, `POST /tasks`, `PUT /tasks/{task_id}`, `DELETE /tasks/{task_id}`). Depends only on `TaskService`.
- [`service.py`](service.py) — `TaskService` business logic and input validation (`ValidationError`, `TaskNotFoundError`). Depends only on the `TaskRepository` interface.
- [`repository.py`](repository.py) — Defines the `TaskRepository` protocol and two implementations with the exact same interface:
  - `InMemoryTaskRepository` (reference in-memory store)
  - `PostgresTaskRepository` (real PostgreSQL store using `psycopg2`)
- [`main.py`](main.py) — Loads `.env` and swaps `PostgresTaskRepository(DATABASE_URL)` into `TaskService` -> `create_router(task_service)`. Neither `service.py` nor `routes.py` changed when swapping storage.

## Environment Configuration

- [`.env.example`](.env.example) is committed as a template.
- `.env` holds the local credentials and `DATABASE_URL`, and is gitignored via the root `.gitignore`.

Before running, copy `.env.example` to `.env` if it does not exist yet:

```bash
cp .env.example .env
```

## Database Initialization (`init.sql`)

[`init.sql`](init.sql) is mounted into Postgres at `/docker-entrypoint-initdb.d/init.sql`. On first initialization of the `postgres_data` volume, it creates the `tasks` table (`id`, `title`, `done`) and seeds 3 example tasks only if the table is empty.

## Run with Docker Compose

From the `week-3` directory, start both the FastAPI app and PostgreSQL together:

```bash
docker compose up --build
```

Once running:
- **API Root:** <http://127.0.0.1:8000/>
- **Swagger UI:** <http://127.0.0.1:8000/docs>

## Verifying Persistence Across App + Container Restarts

With the stack running (`docker compose up -d --build`):

1. Create a new task:
   ```bash
   curl -i -X POST http://127.0.0.1:8000/tasks \
     -H "Content-Type: application/json" \
     -d '{"title":"Survive Docker restart"}'
   ```
2. Restart both the app and Postgres containers (or recreate containers while preserving the `postgres_data` volume):
   ```bash
   docker compose down && docker compose up -d
   ```
3. Query `GET /tasks` again and confirm the created row is still returned:
   ```bash
   curl -i http://127.0.0.1:8000/tasks
   ```

*(Previous SQLite exploration queries and screenshot remain preserved in [`queries.sql`](queries.sql) and [`docs/db-viewer.png`](docs/db-viewer.png).)*
