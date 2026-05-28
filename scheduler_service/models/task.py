from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from db.database import Base

class TaskDefinition(Base):
    __tablename__ = "task_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    webhook_url = Column(String, nullable=False)
    recurrence = Column(String, default="NONE")
    max_retries = Column(Integer, default=3)

    executions = relationship("TaskExecution", back_populates="definition")

class TaskExecution(Base):
    __tablename__ = "task_executions"

    id = Column(Integer, primary_key=True, index=True)
    task_definition_id = Column(Integer, ForeignKey("task_definitions.id"), nullable=False)
    execution_time = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSON)
    status = Column(String, default="PENDING")
    retries = Column(Integer, default=0)
    polling_url = Column(String, nullable=True)
    task_logs = Column(JSON, nullable=True)
    definition = relationship("TaskDefinition", back_populates="executions")
