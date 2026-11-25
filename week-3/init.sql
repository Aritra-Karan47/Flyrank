CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    done BOOLEAN NOT NULL DEFAULT FALSE
);

INSERT INTO tasks (title, done)
SELECT title, done
FROM (
    VALUES
        ('Learn FastAPI basics', TRUE),
        ('Build CRUD endpoints', FALSE),
        ('Test API in Swagger UI', FALSE)
) AS seed(title, done)
WHERE NOT EXISTS (SELECT 1 FROM tasks);
