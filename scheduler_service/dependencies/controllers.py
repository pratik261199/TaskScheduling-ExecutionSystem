from fastapi import Depends

from controllers.task_controller import TaskController
from dependencies.service import get_task_service
from services.task_service import TaskService


def get_task_controller(service: TaskService = Depends(get_task_service)) -> TaskController:
    return TaskController(service)
