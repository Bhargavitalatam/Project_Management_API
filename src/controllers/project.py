from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from src.database import get_db
from src.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from src.services.project import ProjectService
from src.controllers.auth import get_current_user
from src.models.user import User
from typing import List

router = APIRouter(prefix="/api/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    schema: ProjectCreate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    return project_service.create_project(schema, current_user.id)

@router.get("", response_model=List[ProjectResponse])
def list_projects(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    return project_service.get_projects(current_user.id, limit=limit, offset=offset)

@router.get("/{id}", response_model=ProjectResponse)
def get_project(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    return project_service.get_project_by_id(id, current_user.id)

@router.put("/{id}", response_model=ProjectResponse)
def update_project(
    id: int,
    schema: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    return project_service.update_project(id, schema, current_user.id)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    project_service = ProjectService(db)
    project_service.delete_project(id, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
