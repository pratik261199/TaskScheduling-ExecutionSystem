from fastapi import APIRouter, Depends

from dependencies.controllers import get_task_controller
from schemas.task_schemas import TaskCreate, TaskCreateResponse
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
