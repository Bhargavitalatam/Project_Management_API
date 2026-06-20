# Containerized Project Management API

A production-grade, containerized RESTful API for Project and Task management built with:

- **Python / FastAPI** — high-performance web framework
- **SQLAlchemy (ORM)** — strict Layered Architecture + Repository Pattern
- **PostgreSQL** — relational database with FK constraints and cascading deletes
- **Docker / Docker Compose** — zero-install containerization with healthchecks
- **JWT (HS256)** — stateless authentication via `PyJWT`
- **Bcrypt** — secure password hashing

---

## Quick Start (Docker Compose)

> **Prerequisites:** Docker Desktop installed and running.

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd ProjectManagAPI

# 2. Copy environment variables
copy .env.example .env

# 3. Launch the full stack (DB + API)
docker-compose up --build
```

That's all. Docker will:
1. Pull `postgres:15-alpine` and initialize the database.
2. Run a `pg_isready` healthcheck on the database before starting the API.
3. Build the FastAPI image and start the server.
4. Auto-create all database tables on first boot.
5. Auto-seed a default test user and project.

The API is available at:
| Resource | URL |
|---|---|
| **Base URL** | `http://localhost:8000` |
| **Swagger UI (Interactive API Docs)** | `http://localhost:8000/docs` |
| **OpenAPI Schema** | `http://localhost:8000/openapi.json` |

---

## Test / Evaluator Credentials

The database is **automatically seeded** on first startup if empty:

| Field | Value |
|---|---|
| **Email** | `testuser@example.com` |
| **Password** | `password123` |
| **Seeded Project** | `Default Seeded Project` |

Use these credentials to call `POST /api/auth/login` and obtain a Bearer token immediately.

---

## Local Development (Without Docker)

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\activate        # Windows
# source .venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure local environment (uses SQLite by default)
copy .env.example .env
# Edit .env: DATABASE_URL=sqlite:///./local_dev.db

# 4. Run the development server
uvicorn src.main:app --reload
```

---

## Running Automated Tests

```bash
.\.venv\Scripts\pytest          # Windows
# pytest                        # macOS/Linux
```

Expected output:
```
collected 6 items

tests\test_integration_api.py .     [ 16%]
tests\test_unit_services.py   ..... [100%]

======================== 6 passed in X.XXs =========================
```

The tests use an **isolated SQLite in-memory database** — no running PostgreSQL required.

---

## Architecture Overview

The project enforces a strict **Layered Architecture** with the **Repository Pattern**:

```
Client
  └─► Controller   (src/controllers/)  — HTTP parsing, validation, routing
        └─► Service    (src/services/)  — Business logic, auth rules, tenant isolation
              └─► Repository (src/repositories/) — Database queries (ONLY layer to touch SQLAlchemy)
                    └─► ORM Model  (src/models/)  — SQLAlchemy table definitions
                          └─► PostgreSQL Database
```

> Controllers **never** write SQL or call ORM sessions directly.
> Services **never** touch `db.query()` — they call Repository methods exclusively.

### Directory Structure

```
ProjectManagAPI/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── README.md
├── src/
│   ├── main.py              # App entrypoint, exception handlers, lifespan seeding
│   ├── config.py            # Environment variable loading
│   ├── database.py          # SQLAlchemy engine & session factory
│   ├── models/              # ORM entity definitions (User, Project, Task)
│   ├── repositories/        # Data access layer (UserRepo, ProjectRepo, TaskRepo)
│   ├── services/            # Business logic (AuthService, ProjectService, TaskService)
│   ├── controllers/         # FastAPI routers (auth, project, task, user)
│   └── schemas/             # Pydantic DTOs for request/response validation
└── tests/
    ├── conftest.py           # Isolated SQLite test DB fixtures
    ├── test_unit_services.py # Service layer unit tests (mocked repos)
    └── test_integration_api.py # Full HTTP lifecycle integration tests
```

---

## API Reference

### Authentication

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | No | Register new user (bcrypt hashed password) |
| `POST` | `/api/auth/login` | No | Authenticate and receive JWT Bearer token |
| `GET` | `/api/users/me` | ✅ Bearer | Retrieve authenticated user profile |

### Projects

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/projects` | ✅ Bearer | Create a new project |
| `GET` | `/api/projects` | ✅ Bearer | List all projects owned by current user |
| `GET` | `/api/projects/{id}` | ✅ Bearer | Get a specific project (ownership verified) |
| `PUT` | `/api/projects/{id}` | ✅ Bearer | Update a project (ownership verified) |
| `DELETE` | `/api/projects/{id}` | ✅ Bearer | Delete project and all its tasks (cascades) |

### Tasks

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `POST` | `/api/projects/{projectId}/tasks` | ✅ Bearer | Create task in a project (ownership verified) |
| `GET` | `/api/projects/{projectId}/tasks` | ✅ Bearer | List all tasks in a project (ownership verified) |
| `GET` | `/api/tasks/{id}` | ✅ Bearer | Retrieve a task (parent project ownership verified) |
| `PUT` | `/api/tasks/{id}` | ✅ Bearer | Update a task (parent project ownership verified) |
| `DELETE` | `/api/tasks/{id}` | ✅ Bearer | Delete a task (parent project ownership verified) |

---

## Environment Variables

Copy `.env.example` to `.env` to configure the application:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@db:5432/project_db` |
| `SECRET_KEY` | HS256 JWT signing secret (min 32 chars) | `dfc3c0ef2ea5d02f37e42d65...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifespan in minutes | `60` |

> **Security Note:** Never commit real `.env` files containing production secrets. The `.gitignore` explicitly excludes `.env`. Only `.env.example` (with dummy values) is committed.

---

## Security Implementation

| Feature | Implementation |
|---|---|
| Password Hashing | `bcrypt` with auto-generated salt per user |
| Token Signing | `PyJWT` with HS256 algorithm, 60-minute expiration |
| Token Verification | Signature check + expiration validation on every protected request |
| Tenant Isolation | Every project/task operation verifies `owner_id == current_user.id` |
| Error Sanitization | No raw stack traces exposed to clients; global exception handler returns clean JSON |

---

## Docker Details

### Dockerfile

- Base image: `python:3.11-slim`
- Layer-caching optimized: `requirements.txt` installed before source copy
- Startup command: `uvicorn src.main:app --host 0.0.0.0 --port 8000`

### docker-compose.yml

- `db` service: `postgres:15-alpine` with persistent named volume (`postgres_data`)
- `db` healthcheck: `pg_isready -U postgres -d project_db` (prevents API startup race condition)
- `api` service: `depends_on: db: condition: service_healthy`
