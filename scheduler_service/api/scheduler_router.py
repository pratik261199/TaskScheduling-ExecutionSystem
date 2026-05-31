from fastapi import APIRouter, Depends

from dependencies.controllers import get_task_controller
from schemas.task_schemas import TaskCreate, TaskCreateResponse, TaskListResponse
from controllers.task_controller import TaskController

router = APIRouter()

@router.post(
    "/tasks", 
    status_code=201, 
    summary="Create a new scheduled task",
    response_model=TaskCreateResponse
)
async def create_task(
    task_data: TaskCreate, 
    controller: TaskController = Depends(get_task_controller)
):
    """
    Endpoint to create a new scheduled task.
    """
    return await controller.create_new_task(task_data)

@router.get(
    "/tasks",
    summary="Get all tasks",
    response_model=TaskListResponse
)
async def get_tasks(
    controller: TaskController = Depends(get_task_controller)
):
    """
    API to get all tasks.
    """
    return await controller.get_all_tasks()
