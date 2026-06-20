from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from src.database import engine, SessionLocal
from src.models.base import Base
from src.models.user import User
from src.models.project import Project
from src.services.auth import AuthService
from src.controllers import auth_router, project_router, task_router, user_router
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create all tables in the database
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed the database if it is empty
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            auth_service = AuthService(db)
            # Create a default test user
            test_user = User(
                email="testuser@example.com",
                password_hash=auth_service.get_password_hash("password123")
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Create a default project for this user
            test_project = Project(
                name="Default Seeded Project",
                description="This project has been seeded automatically on application startup.",
                owner_id=test_user.id
            )
            db.add(test_project)
            db.commit()
    finally:
        db.close()
        
    yield

app = FastAPI(
    title="Project Management API",
    description="A robust, containerized RESTful API for Project and Task Management.",
    version="1.0.0",
    lifespan=lifespan
)

# Include controllers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)
app.include_router(user_router)

# Custom handler for FastAPI HTTPExceptions to return consistent {"error": detail} format
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
        headers=exc.headers
    )

# Custom handler for request validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg")
        errors.append(f"Field '{loc}': {msg}")
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "details": errors}
    )

# Custom handler for database integrity constraints
@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    err_msg = str(exc.orig)
    if "unique constraint" in err_msg.lower() or "duplicate key" in err_msg.lower():
        if "users_email_key" in err_msg or "email" in err_msg:
            return JSONResponse(
                status_code=409,
                content={"error": "Email already in use"}
            )
    return JSONResponse(
        status_code=400,
        content={"error": "Database integrity constraint violation"}
    )

# Global catch-all to prevent raw tracebacks from leaking
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )
