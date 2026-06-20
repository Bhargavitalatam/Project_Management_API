from src.controllers.auth import router as auth_router, get_current_user
from src.controllers.project import router as project_router
from src.controllers.task import router as task_router

__all__ = ["auth_router", "project_router", "task_router", "get_current_user"]
