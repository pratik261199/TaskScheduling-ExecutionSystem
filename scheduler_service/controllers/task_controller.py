from fastapi import HTTPException
from services.task_service import TaskService
from schemas.task_schemas import TaskCreate, TaskCreateResponse
import logging
logger = logging.getLogger(__name__)

class TaskController:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def create_new_task(self, task_data: TaskCreate) -> TaskCreateResponse:
        """
        Controller logic to handle the creation of a new task.
        """
        try:
            task_def = await self.task_service.create_task(task_data)
            return TaskCreateResponse(
                message="Task created successfully", 
                task_definition_id=task_def.id
            )
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the task.")
