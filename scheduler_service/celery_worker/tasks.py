import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncContextManager

from celery_worker.app import celery_app
from config.settings import settings
from db.database import AsyncSessionLocal
from services.task_service import TaskService

logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_service() -> AsyncContextManager[TaskService]:
    """Async context manager to provide a TaskService with a DB session."""
    db = AsyncSessionLocal()
    try:
        yield TaskService(db)
    finally:
        await db.close()

@celery_app.task(ignore_result=True)
def check_pending_tasks():
    """Celery task to periodically dispatch due tasks."""
    logger.info("Celery Task: dispatch_due_tasks triggered.")
    
    async def run_dispatch():
        async with get_service() as service:
            await service.dispatch_due_tasks()

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_dispatch())
    except Exception as e:
        logger.error(f"Celery Task: Error during dispatch: {e}", exc_info=True)

@celery_app.task(bind=True, max_retries=1, default_retry_delay=30)
def poll_webhook_status(self, execution_id: int):
    """
    Celery task to poll a webhook for status.
    """
    logger.info(f"Celery Task: poll_webhook_status triggered for execution {execution_id}.")
    
    loop = asyncio.get_event_loop()

    async def run_polling() -> bool:
        """
        Calls the service to poll the status.
        """
        async with get_service() as service:
            execution = await service.repo.get_execution_with_definition(execution_id)
            if not execution:
                return True

            self.max_retries = execution.definition.max_retries

            return await service.poll_task_status(execution_id)

    try:
        is_complete = loop.run_until_complete(run_polling())
        
        if not is_complete:
            try:
                delay = settings.EXPONENTIAL_RETRY_FOR_FAILURE_IN_SECONDS*(2**self.request.retries)
                logger.info(f"Polling for task {execution_id} not complete. Retrying in {delay}s.")
                self.retry(countdown=delay)
            except self.MaxRetriesExceededError:
                logger.error(f"Polling for task {execution_id} exceeded max retries. Marking as FAILED.")
                async def mark_failed():
                    async with get_service() as service:
                        await service.repo.update_execution_status(execution_id, "FAILED")
                loop.run_until_complete(mark_failed())

    except Exception as e:
        logger.error(f"Celery Task: Error during polling for execution {execution_id}: {e}", exc_info=True)
        try:
            self.retry()
        except self.MaxRetriesExceededError:
            logger.error(f"Polling for task {execution_id} exceeded max retries after an error. Marking as FAILED.")
            async def mark_failed():
                async with get_service() as service:
                    await service.repo.update_execution_status(execution_id, "FAILED")
            loop.run_until_complete(mark_failed())
