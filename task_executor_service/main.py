from fastapi import FastAPI
from api import executor_router
from logger_config import setup_logging

setup_logging()

app = FastAPI(
    title="Task Executor Service"
)

app.include_router(executor_router.router, prefix="/api/v1")
