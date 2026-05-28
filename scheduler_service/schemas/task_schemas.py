from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any
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

    class Config:
        use_enum_values = True




class TaskCreateResponse(BaseModel):
    message: str
    task_definition_id: int
