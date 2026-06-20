from sqlalchemy.orm import Session
from src.models.project import Project
from typing import List, Dict, Any

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, project_id: int) -> Project | None:
        return self.db.query(Project).filter(Project.id == project_id).first()

    def get_all_by_owner(self, owner_id: int, limit: int = 10, offset: int = 0) -> List[Project]:
        return (
            self.db.query(Project)
            .filter(Project.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, project_data: Dict[str, Any], owner_id: int) -> Project:
        project = Project(**project_data, owner_id=owner_id)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project_id: int, update_data: Dict[str, Any]) -> Project | None:
        project = self.get_by_id(project_id)
        if not project:
            return None
        for key, value in update_data.items():
            if value is not None:
                setattr(project, key, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        project = self.get_by_id(project_id)
        if not project:
            return False
        self.db.delete(project)
        self.db.commit()
        return True
