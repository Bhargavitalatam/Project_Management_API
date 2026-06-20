from sqlalchemy.orm import Session
from src.repositories.task import TaskRepository
from src.repositories.project import ProjectRepository
from src.models.task import Task
from src.schemas.task import TaskCreate, TaskUpdate
from fastapi import HTTPException, status
from typing import List

class TaskService:
    def __init__(self, db: Session):
        self.task_repo = TaskRepository(db)
        self.project_repo = ProjectRepository(db)

    def create_task(self, project_id: int, schema: TaskCreate, current_user_id: int) -> Task:
        # 1. Does the Project identified by projectId exist in the database?
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # 2. Does the currently authenticated user own the Project identified by projectId?
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add tasks to this project"
            )
            
        # 3. Create the task via the Repository
        return self.task_repo.create(schema.model_dump(), project_id)

    def get_tasks_by_project(self, project_id: int, current_user_id: int) -> List[Task]:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access tasks for this project"
            )
        return self.task_repo.get_all_by_project(project_id)

    def get_task_by_id(self, task_id: int, current_user_id: int) -> Task:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        
        if task.project.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this task"
            )
        return task

    def update_task(self, task_id: int, schema: TaskUpdate, current_user_id: int) -> Task:
        task = self.get_task_by_id(task_id, current_user_id)
        updated = self.task_repo.update(task.id, schema.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return updated

    def delete_task(self, task_id: int, current_user_id: int) -> None:
        task = self.get_task_by_id(task_id, current_user_id)
        deleted = self.task_repo.delete(task.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
