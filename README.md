# Containerized Project Management API

A containerized RESTful API built with Python (FastAPI), SQLAlchemy, PostgreSQL, and Docker. It features JWT-based authentication, a strict Layered Architecture conforming to the Repository pattern, input validation, and robust exception handling.

## Default Seeded Credentials

On application startup, if the database is empty, it will automatically be seeded with the following evaluator credentials:
- **Email:** `testuser@example.com`
- **Password:** `password123`
- **Seeded Project:** `Default Seeded Project`

## Quick Start (Docker Compose)

To build and run the entire environment in containerized mode (API + PostgreSQL DB):

```bash
docker-compose up --build
```

The database container will start first, complete its initialization healthcheck (`pg_isready`), and the API container will start once the database is healthy.

The API will then be available at:
- **Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Base URL:** `http://localhost:8000`

## Local Development & Testing

To run the application locally without Docker:

1. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment Variables:**
   A local `.env` file is provided, which configures the database connection to use an in-memory or file-based SQLite database (`sqlite:///./local_dev.db`) for fast local runs.
4. **Run Server:**
   ```bash
   uvicorn src.main:app --reload
   ```
5. **Run Tests:**
   ```bash
   pytest
   ```

## Architecture & Project Structure

- `src/models/`: Declarative SQLAlchemy models (`User`, `Project`, `Task`).
- `src/repositories/`: Classes handling database operations. The core code never writes direct SQL or calls ORM sessions outside repositories.
- `src/services/`: Core business logic, tenant isolation rules, password hashing (Bcrypt), and token issuance (PyJWT).
- `src/controllers/`: FastAPI routes implementing URL bindings, nested/standalone routing, and token validation checks.
- `src/schemas/`: DTO schemas (Pydantic) for validation.
- `tests/`: Unit and integration test suites using an isolated SQLite in-memory engine.

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user profile.
- `POST /api/auth/login` - Authenticate credentials and get JWT Bearer token.

### Projects (Requires Authorization: Bearer <token>)
- `POST /api/projects` - Create project.
- `GET /api/projects` - List caller's projects (supports offset/limit pagination).
- `GET /api/projects/{id}` - Retrieve details of a project owned by caller.
- `PUT /api/projects/{id}` - Update a project owned by caller.
- `DELETE /api/projects/{id}` - Delete a project owned by caller (cascades task deletion).

### Tasks (Requires Authorization: Bearer <token>)
- `POST /api/projects/{projectId}/tasks` - Create a task under a project (validates ownership).
- `GET /api/projects/{projectId}/tasks` - List tasks under a project.
- `PUT /api/tasks/{id}` - Update task status/details (validates ownership of parent project).
- `DELETE /api/tasks/{id}` - Delete task (validates ownership of parent project).
