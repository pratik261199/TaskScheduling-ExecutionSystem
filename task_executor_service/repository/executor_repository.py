import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.task import ExecutorTask

class ExecutorRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, payload: Dict[str, Any]) -> ExecutorTask:
        """Creates a new task record in the executor's database."""
        new_task = ExecutorTask(payload=payload, status="SUCCESS")
        self.db.add(new_task)
        await self.db.commit()
        await self.db.refresh(new_task)
        return new_task

    async def get_task(self, task_id: uuid.UUID) -> Optional[ExecutorTask]:
        """Retrieves a task by its ID."""
        result = await self.db.execute(select(ExecutorTask).where(ExecutorTask.id == task_id))
        return result.scalar_one_or_none()

    async def update_task_status(self, task_id: uuid.UUID, new_status: str) -> Optional[ExecutorTask]:
        """Updates the status of a task."""
        task = await self.get_task(task_id)
        if task:
            task.status = new_status
            await self.db.commit()
            await self.db.refresh(task)
        return task
