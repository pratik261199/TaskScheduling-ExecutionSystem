from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

class RecurrenceType(str, Enum):
    NONE = "NONE"
    DAILY = "DAILY"
    HOURLY = "HOURLY"
    CUSTOM_CRON = "CUSTOM_CRON"

class Recurrence(BaseModel):
    type: RecurrenceType = RecurrenceType.NONE
    cron: Optional[str] = None

    @model_validator(mode='after')
    def cron_must_exist_for_custom(self) -> 'Recurrence':
        if self.type == RecurrenceType.CUSTOM_CRON and not self.cron:
            raise ValueError("`cron` is required for CUSTOM_CRON recurrence type")
        return self

class TaskCreate(BaseModel):
    name: str = Field(..., min_length=1, description="A descriptive name for the task.")
    execution_time: datetime = Field(..., description="The scheduled time for the task's first execution in ISO 8601 format.")
    webhook_url: str = Field(..., description="The URL that the executor service will call.")
    payload: Optional[Dict[str, Any]] = Field(None, description="The JSON payload to be sent to the webhook.")
    recurrence: Optional[Recurrence] = Field(default_factory=Recurrence, description="The recurrence rule for the task.")
    max_retries: Optional[int] = Field(3, ge=0, description="Maximum number of retries for the task before marking it as FAILED.")

    model_config = ConfigDict(use_enum_values=True)


class TaskExecutionResponse(BaseModel):
    id: int
    execution_time: datetime
    status: str
    payload: Optional[Dict[str, Any]]
    task_logs: Optional[List]

    model_config = ConfigDict(from_attributes=True)


class TaskDefinitionResponse(BaseModel):
    id: int
    name: str
    webhook_url: str
    recurrence: str
    max_retries: int
    executions: List[TaskExecutionResponse] = []

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    tasks: List[TaskDefinitionResponse]

class TaskCreateResponse(BaseModel):
    message: str
    task_definition_id: int
