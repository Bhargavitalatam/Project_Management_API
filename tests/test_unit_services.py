from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException
from src.services.project import ProjectService
from src.services.task import TaskService
from src.models.project import Project
from src.models.task import Task
from src.schemas.project import ProjectUpdate, ProjectCreate
from src.schemas.task import TaskCreate

def test_update_project_unauthorized():
    # Arrange: Mock database session
    db_mock = MagicMock()
    project_service = ProjectService(db_mock)
    
    # Mock Repository return value for a project owned by user_id = 1
    mock_project = Project(id=10, name="Secret Project", owner_id=1)
    project_service.project_repo.get_by_id = MagicMock(return_value=mock_project)
    
    # Act & Assert: Call update with user_id = 2 (unauthorized)
    update_schema = ProjectUpdate(name="New Project Name")
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(project_id=10, schema=update_schema, current_user_id=2)
        
    assert exc_info.value.status_code == 403
    assert "Not authorized" in exc_info.value.detail

def test_create_project_delegates_to_repo():
    # Arrange
    db_mock = MagicMock()
    project_service = ProjectService(db_mock)
    
    mock_project = Project(id=1, name="New Project", owner_id=5)
    project_service.project_repo.create = MagicMock(return_value=mock_project)
    
    # Act
    create_schema = ProjectCreate(name="New Project", description="Some desc")
    result = project_service.create_project(create_schema, owner_id=5)
    
    # Assert
    project_service.project_repo.create.assert_called_once_with(
        {"name": "New Project", "description": "Some desc"}, 5
    )
    assert result.id == 1
    assert result.name == "New Project"

def test_get_project_not_found():
    # Arrange
    db_mock = MagicMock()
    project_service = ProjectService(db_mock)
    project_service.project_repo.get_by_id = MagicMock(return_value=None)
    
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_project_by_id(project_id=999, current_user_id=1)
        
    assert exc_info.value.status_code == 404
    assert "Project not found" in exc_info.value.detail

def test_create_task_unauthorized_project():
    # Arrange
    db_mock = MagicMock()
    task_service = TaskService(db_mock)
    
    # Project owned by owner 1
    mock_project = Project(id=20, name="Team Project", owner_id=1)
    task_service.project_repo.get_by_id = MagicMock(return_value=mock_project)
    
    # Act & Assert: User 3 tries to create task under project owned by User 1
    task_schema = TaskCreate(title="Unwanted Task", description="Spam")
    with pytest.raises(HTTPException) as exc_info:
        task_service.create_task(project_id=20, schema=task_schema, current_user_id=3)
        
    assert exc_info.value.status_code == 403
    assert "Not authorized" in exc_info.value.detail

def test_create_task_project_not_found():
    # Arrange
    db_mock = MagicMock()
    task_service = TaskService(db_mock)
    task_service.project_repo.get_by_id = MagicMock(return_value=None)
    
    # Act & Assert
    task_schema = TaskCreate(title="Floating Task")
    with pytest.raises(HTTPException) as exc_info:
        task_service.create_task(project_id=999, schema=task_schema, current_user_id=1)
        
    assert exc_info.value.status_code == 404
    assert "Project not found" in exc_info.value.detail
