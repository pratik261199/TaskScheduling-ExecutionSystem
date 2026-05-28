from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.db import get_db
from services.task_service import TaskService

def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    return TaskService(db)

