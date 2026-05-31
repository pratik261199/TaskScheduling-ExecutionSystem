from celery import Celery
from celery.signals import setup_logging as setup_celery_logging
from config.settings import settings
from logger_config import setup_logging as setup_file_logging

@setup_celery_logging.connect
def setup_logging(**kwargs):
    """
    Setup logging for celery workers.
    """
    setup_file_logging()


celery_app = Celery(
    "scheduler_tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    include=["celery_worker.tasks"]
)


celery_app.conf.beat_schedule = {
    'check-pending-tasks': {
        'task': 'celery_worker.tasks.check_pending_tasks',
        'schedule': settings.PERIODIC_SCHEDULER_EXECUTION_IN_SECONDS,
    },
}
celery_app.conf.timezone = 'UTC'
