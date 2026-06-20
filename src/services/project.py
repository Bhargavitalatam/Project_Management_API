from sqlalchemy.orm import Session
from src.repositories.project import ProjectRepository
from src.models.project import Project
from src.schemas.project import ProjectCreate, ProjectUpdate
from fastapi import HTTPException, status
from typing import List

class ProjectService:
    def __init__(self, db: Session):
        self.project_repo = ProjectRepository(db)

    def create_project(self, schema: ProjectCreate, owner_id: int) -> Project:
        return self.project_repo.create(schema.model_dump(), owner_id)

    def get_projects(self, owner_id: int, limit: int = 10, offset: int = 0) -> List[Project]:
        return self.project_repo.get_all_by_owner(owner_id, limit, offset)

    def get_project_by_id(self, project_id: int, current_user_id: int) -> Project:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project"
            )
        return project

    def update_project(self, project_id: int, schema: ProjectUpdate, current_user_id: int) -> Project:
        project = self.get_project_by_id(project_id, current_user_id)
        updated = self.project_repo.update(project.id, schema.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return updated

    def delete_project(self, project_id: int, current_user_id: int) -> None:
        project = self.get_project_by_id(project_id, current_user_id)
        deleted = self.project_repo.delete(project.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
