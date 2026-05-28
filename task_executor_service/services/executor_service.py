import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from repository.executor_repository import ExecutorRepository
from models.task import ExecutorTask

class ExecutorService:
    def __init__(self, db_session: AsyncSession):
        self.repo = ExecutorRepository(db_session)

    async def handle_async_task(self, payload: Dict[str, Any]) -> ExecutorTask:
        return await self.repo.create_task(payload)

    async def get_and_process_task_status(self, task_id: uuid.UUID) -> str:
        task = await self.repo.get_task(task_id)
        if not task:
            return None

        current_status = task.status
        
        if current_status == "QUEUED":
            await self.repo.update_task_status(task_id, "SUCCESS")
            
        return current_status
