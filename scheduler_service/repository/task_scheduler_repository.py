from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from models.task import TaskDefinition, TaskExecution

class TaskSchedulerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_task_definition(self, name: str, webhook_url: str, recurrence: str, max_retries: int) -> TaskDefinition:
        result = await self.db.execute(select(TaskDefinition).filter(TaskDefinition.name == name))
        task_def = result.scalar_one_or_none()
        if not task_def:
            task_def = TaskDefinition(
                name=name, 
                webhook_url=webhook_url, 
                recurrence=recurrence,
                max_retries=max_retries
            )
            self.db.add(task_def)
            await self.db.commit()
            await self.db.refresh(task_def)
        return task_def

    async def create_task_execution(self, task_definition_id: int, execution_time: datetime, payload: Optional[Dict[str, Any]]) -> TaskExecution:
        new_execution = TaskExecution(
            task_definition_id=task_definition_id,
            execution_time=execution_time,
            payload=payload,
            status="PENDING"
        )
        self.db.add(new_execution)
        await self.db.commit()
        await self.db.refresh(new_execution)
        return new_execution

    async def get_due_executions_and_lock(self, limit: int) -> List[TaskExecution]:
        now = datetime.now(timezone.utc)
        due_tasks_stmt = (
            select(TaskExecution)
            .options(joinedload(TaskExecution.definition))
            .where(TaskExecution.status == "PENDING")
            .where(TaskExecution.execution_time <= now)
            .limit(limit)
            .with_for_update(skip_locked=True, of=TaskExecution)
        )
        result = await self.db.execute(due_tasks_stmt)
        due_tasks = result.scalars().unique().all()
        
        if due_tasks:
            for task in due_tasks:
                task.status = "RUNNING"
            await self.db.commit()
            for task in due_tasks:
                await self.db.refresh(task, attribute_names=['definition'])
                await self.db.refresh(task)

        return due_tasks

    async def get_execution_with_definition(self, execution_id: int) -> Optional[TaskExecution]:
        result = await self.db.execute(
            select(TaskExecution)
            .options(joinedload(TaskExecution.definition))
            .where(TaskExecution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def update_execution_status(self, execution_id: int, status: str) -> Optional[TaskExecution]:
        task_execution = await self.get_execution_with_definition(execution_id)
        if task_execution:
            task_execution.status = status
            await self.db.commit()
            await self.db.refresh(task_execution)
        return task_execution
        
    async def set_polling_state(self, execution_id: int, polling_url: str) -> Optional[TaskExecution]:
        task_execution = await self.get_execution_with_definition(execution_id)
        if task_execution:
            task_execution.status = "POLLING"
            task_execution.polling_url = polling_url
            await self.db.commit()
            await self.db.refresh(task_execution)
        return task_execution

    async def update_for_retry(self, execution_id: int, next_attempt_time: datetime, retries: int):
        """Updates a task execution for its next retry attempt."""
        task_execution = await self.get_execution_with_definition(execution_id)
        if task_execution:
            task_execution.status = "PENDING"
            task_execution.execution_time = next_attempt_time
            task_execution.retries = retries
            await self.db.commit()
        return task_execution

    async def append_log_to_execution(self, execution_id: int, log_message: str):
        """Appends a new log message to a task execution's log array."""
        task_execution = await self.get_execution_with_definition(execution_id)
        if task_execution:
            if task_execution.task_logs is None:
                task_execution.task_logs = []
            
            task_execution.task_logs = task_execution.task_logs + [log_message]
            await self.db.commit()

    async def get_all_executions(self):
        result = await self.db.execute(select(TaskExecution))
        return result.scalars().all()
