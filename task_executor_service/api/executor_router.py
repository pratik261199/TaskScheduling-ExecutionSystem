import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Dict, Any

from services.executor_service import ExecutorService
from db.database import get_db
from config.settings import settings

router = APIRouter()

class TaskPayload(BaseModel):
    payload: Dict[str, Any]

def get_executor_service(db: AsyncSession = Depends(get_db)) -> ExecutorService:
    return ExecutorService(db)

@router.post("/sync-webhook", status_code=status.HTTP_200_OK)
async def sync_webhook(payload: TaskPayload,
                       executor_service: ExecutorService = Depends(get_executor_service)
                       ):
    await executor_service.handle_async_task(payload.payload)
    return {"status": "FAILED", "message": "Task processed synchronously."}

@router.post("/async-webhook", status_code=status.HTTP_202_ACCEPTED)
async def async_webhook(
    payload: TaskPayload,
    executor_service: ExecutorService = Depends(get_executor_service)
):
    task = await executor_service.handle_async_task(payload.payload)
    check_url = f"{settings.HOST_NAME}:{settings.HOST_PORT}/api/v1/status/{task.id}"
    return {"status": "QUEUED", "check_url": check_url}

@router.get("/status/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_status(
    task_id: uuid.UUID,
    executor_service: ExecutorService = Depends(get_executor_service)
):
    current_status = await executor_service.get_and_process_task_status(task_id)

    if not current_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return {"status": current_status}
