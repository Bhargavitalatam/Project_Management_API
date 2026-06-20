from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from src.services.task import TaskService
from src.controllers.auth import get_current_user
from src.models.user import User
from typing import List

router = APIRouter(tags=["Tasks"])

@router.post("/api/projects/{projectId}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    projectId: int,
    schema: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.create_task(projectId, schema, current_user.id)

@router.get("/api/projects/{projectId}/tasks", response_model=List[TaskResponse])
def list_tasks(
    projectId: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.get_tasks_by_project(projectId, current_user.id)

@router.get("/api/tasks/{id}", response_model=TaskResponse)
def get_task(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.get_task_by_id(id, current_user.id)

@router.put("/api/tasks/{id}", response_model=TaskResponse)
def update_task(
    id: int,
    schema: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    return task_service.update_task(id, schema, current_user.id)

@router.delete("/api/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task_service = TaskService(db)
    task_service.delete_task(id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
