import uuid
from fastapi import HTTPException, status
from services.executor_service import ExecutorService
from schemas.task_schemas import TaskPayload
from config.settings import settings
class ExecutorController:
    def __init__(self, executor_service: ExecutorService):
        self.executor_service = executor_service

    async def handle_sync_webhook(self, payload: TaskPayload):
        """Controller logic for the synchronous webhook."""
        return {"status": "SUCCESS", "message": "Task processed synchronously."}

    async def handle_async_webhook(self, payload: TaskPayload):
        """Controller logic for the asynchronous webhook."""
        task = await self.executor_service.handle_async_task(payload.payload)
        check_url = f"{settings.HOST_NAME}:{settings.HOST_PORT}/api/v1/status/{task.id}"
        return {"status": "QUEUED", "check_url": check_url, "status_code": status.HTTP_202_ACCEPTED}

    async def get_task_status(self, task_id: uuid.UUID):
        """Controller logic for the status polling endpoint."""
        current_status = await self.executor_service.get_and_process_task_status(task_id)

        if not current_status:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        return {"status": current_status}
