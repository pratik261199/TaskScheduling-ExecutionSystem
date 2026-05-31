from pydantic import computed_field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    EXECUTOR_POSTGRES_USER: str = "postgres"
    EXECUTOR_POSTGRES_PASSWORD: str = "postgres"
    EXECUTOR_POSTGRES_HOST: str = "postgres"
    EXECUTOR_POSTGRES_PORT: int = 5432
    EXECUTOR_POSTGRES_DB: str = "executor_db"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    SCHEDULER_BASE_URL: str = "http://localhost:8000"

    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    HOST_NAME: str = "http://executor"
    HOST_PORT: int = 8001

    @computed_field
    @property
    def EXECUTOR_DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.EXECUTOR_POSTGRES_USER}:{self.EXECUTOR_POSTGRES_PASSWORD}@{self.EXECUTOR_POSTGRES_HOST}:{self.EXECUTOR_POSTGRES_PORT}/{self.EXECUTOR_POSTGRES_DB}"


    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
