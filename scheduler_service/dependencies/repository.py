from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from repository.task_scheduler_repository import TaskSchedulerRepository
from dependencies.db import get_db

def get_task_scheduler_repository(db: AsyncSession = Depends(get_db)) -> TaskSchedulerRepository:
    return TaskSchedulerRepository(db)
