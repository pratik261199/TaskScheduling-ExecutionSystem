from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    SCHEDULER_POSTGRES_USER: str = "postgres"
    SCHEDULER_POSTGRES_PASSWORD: str = "postgres"
    SCHEDULER_POSTGRES_HOST: str = "postgres"
    SCHEDULER_POSTGRES_PORT: int = 5432
    SCHEDULER_POSTGRES_DB: str = "scheduler_db"

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10


    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    

    @computed_field
    @property
    def SCHEDULER_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.SCHEDULER_POSTGRES_USER}:{self.SCHEDULER_POSTGRES_PASSWORD}@{self.SCHEDULER_POSTGRES_HOST}:{self.SCHEDULER_POSTGRES_PORT}/{self.SCHEDULER_POSTGRES_DB}"

    PERIODIC_SCHEDULER_EXECUTION_IN_SECONDS: int = 10
    EXPONENTIAL_RETRY_FOR_FAILURE_IN_SECONDS: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
