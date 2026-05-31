from fastapi import FastAPI
from api import scheduler_router
from logger_config import setup_logging

setup_logging()


app = FastAPI(
    title="Scheduler Service"
)

app.include_router(scheduler_router.router, prefix="/api/v1")
