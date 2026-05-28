from celery import Celery
from config.settings import settings

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
