from sqlalchemy.orm import Session
from src.models.task import Task
from typing import List, Dict, Any

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_all_by_project(self, project_id: int) -> List[Task]:
        return self.db.query(Task).filter(Task.project_id == project_id).all()

    def create(self, task_data: Dict[str, Any], project_id: int) -> Task:
        task = Task(**task_data, project_id=project_id)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task_id: int, update_data: Dict[str, Any]) -> Task | None:
        task = self.get_by_id(task_id)
        if not task:
            return None
        for key, value in update_data.items():
            if value is not None:
                setattr(task, key, value)
        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        task = self.get_by_id(task_id)
        if not task:
            return False
        self.db.delete(task)
        self.db.commit()
        return True
