import httpx
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from croniter import croniter

from repository.task_scheduler_repository import TaskSchedulerRepository
from models.task import TaskDefinition, TaskExecution
from celery_worker.app import celery_app
from schemas.task_schemas import TaskCreate, RecurrenceType

from config.settings import settings

logger = logging.getLogger(__name__)

class TaskService:
    def __init__(self, db_session: AsyncSession):
        self.repo = TaskSchedulerRepository(db_session)

    async def create_task(self, task_data: TaskCreate) -> TaskDefinition:
        """Orchestrates the creation of a new task."""
        recurrence_str = task_data.recurrence.cron if task_data.recurrence.type == RecurrenceType.CUSTOM_CRON else task_data.recurrence.type.value

        task_def = await self.repo.get_or_create_task_definition(
            name=task_data.name,
            webhook_url=task_data.webhook_url,
            recurrence=recurrence_str,
            max_retries=task_data.max_retries
        )
        
        await self.repo.create_task_execution(
            task_definition_id=task_def.id,
            execution_time=task_data.execution_time,
            payload=task_data.payload
        )
        
        return task_def

    async def dispatch_due_tasks(self):
        """Fetches pending tasks, calls their webhooks, and handles responses."""

        logger.info("TaskService: Checking for due tasks to dispatch...")
        due_tasks = await self.repo.get_due_executions_and_lock(limit=100)

        if not due_tasks:
            return

        logger.info(f"TaskService: Found {len(due_tasks)} tasks to process.")
        for task in due_tasks:
            await self.execute_webhook_and_handle_response(task)

    async def execute_webhook_and_handle_response(self, task: TaskExecution):
        """Makes the HTTP call for a single task and processes the outcome."""

        logger.info(f"Executing webhook for task {task.id} at {task.definition.webhook_url}")
        
        request_payload = {"payload": task.payload}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(task.definition.webhook_url, json=request_payload, timeout=10)
                response.raise_for_status()
            
            if response.status_code == 202:
                check_url = response.json().get("check_url")
                if check_url:
                    await self.repo.set_polling_state(task.id, check_url)
                    celery_app.send_task('celery_worker.tasks.poll_webhook_status', args=[task.id])
                else:
                    await self.repo.update_execution_status(task.id, "FAILED")
            else: # Synchronous success
                await self.repo.update_execution_status(task.id, "SUCCESS")
                await self._handle_recurrence(task.definition, task.payload)

        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            logger.warning(f"Request for task {task.id} failed: {e}. Attempting retry...")
            await self.handle_retry(task, str(e))

    async def poll_task_status(self, execution_id: int) -> bool:
        """
        Polls a task's status URL until specified maximum retries and updates the DB.
        """
        execution = await self.repo.get_execution_with_definition(execution_id)
        if not execution or not execution.polling_url:
            return True

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(execution.polling_url, timeout=10)
            
            status_data = response.json()
            status = status_data.get("status", "UNKNOWN").upper()

            if status == "SUCCESS":
                await self.repo.update_execution_status(execution_id, "SUCCESS")
                await self._handle_recurrence(execution.definition, execution.payload)
                return True
            elif status == "FAILED":
                await self.repo.update_execution_status(execution_id, "FAILED")
                return True
            else:
                return False

        except (httpx.RequestError, Exception) as e:
            log_message = f"Polling attempt failed: {str(e)}"
            await self.repo.append_log_to_execution(execution_id, log_message)
            return False

    async def handle_retry(self, task: TaskExecution, error_message: str):
        """Handles the retry logic for a failed task execution."""
        current_retries = task.retries
        
        log_message = f"Attempt {current_retries + 1} failed at {datetime.now(timezone.utc).isoformat()}: {error_message}"
        await self.repo.append_log_to_execution(task.id, log_message)

        if current_retries < task.definition.max_retries:
            new_retry_count = current_retries + 1
            backoff_seconds = settings.EXPONENTIAL_RETRY_FOR_FAILURE_IN_SECONDS * (2 ** current_retries)
            next_attempt_time = datetime.now(timezone.utc) + timedelta(seconds=backoff_seconds)
            
            await self.repo.update_for_retry(task.id, next_attempt_time, new_retry_count)
            logger.info(f"Task {task.id} failed. Rescheduled for retry {new_retry_count}/{task.definition.max_retries} at {next_attempt_time}.")
        else:
            await self.repo.update_execution_status(task.id, "FAILED")
            logger.error(f"Task {task.id} has exceeded max retries. Marking as FAILED.")

    async def _handle_recurrence(self, task_def: TaskDefinition, payload: dict):
        """Schedules the next execution if the task is recurring."""
        if not task_def.recurrence or task_def.recurrence == "NONE":
            return

        now = datetime.now(timezone.utc)
        
        try:
            if task_def.recurrence == "DAILY":
                next_execution_time = now + timedelta(days=1)
            elif task_def.recurrence == "HOURLY":
                next_execution_time = now + timedelta(hours=1)
            else:
                cron = croniter(task_def.recurrence, now)
                next_execution_time = cron.get_next(datetime)

            await self.repo.create_task_execution(
                task_definition_id=task_def.id,
                execution_time=next_execution_time,
                payload=payload
            )
            logger.info(f"Scheduled next run for task definition {task_def.id} at {next_execution_time}")
        
        except Exception as e:
            logger.error(f"Failed to schedule next run for task definition {task_def.id}: {e}")
