from fastapi import FastAPI
from api import scheduler_router


app = FastAPI(
    title="Scheduler Service"
)

app.include_router(scheduler_router.router, prefix="/api/v1")
