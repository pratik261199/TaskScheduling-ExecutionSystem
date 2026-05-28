import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from datetime import datetime, timezone

from main import app
from db.database import get_db
from models.task import TaskDefinition

client = TestClient(app)

@pytest.fixture
def override_get_db():

    mock_repo = AsyncMock()
    mock_repo.get_or_create_task_definition.return_value = TaskDefinition(id=1)
    mock_repo.create_task_execution = AsyncMock()

    from services.task_service import TaskService
    
    original_init = TaskService.__init__
    def new_init(self, db_session):
        original_init(self, db_session)
        self.repo = mock_repo
    
    TaskService.__init__ = new_init

    app.dependency_overrides[get_db] = lambda: AsyncMock()
    
    yield
    
    app.dependency_overrides.clear()
    TaskService.__init__ = original_init


def test_create_task_api_success(override_get_db):

    test_payload = {
        "name": "Integration Test Task",
        "execution_time": datetime.now(timezone.utc).isoformat(),
        "webhook_url": "http://integration-test.com",
        "payload": {"test": "true"},
        "max_retries": 3,
        "recurrence": {"type": "NONE"}
    }

    response = client.post("/api/v1/tasks", json=test_payload)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["message"] == "Task created successfully"
    assert response_data["task_definition_id"] == 1

def test_create_task_api_validation_error(override_get_db):

    test_payload = {
        "name": "Validation Error Task",
        "execution_time": datetime.now(timezone.utc).isoformat(),
        "webhook_url": "http://integration-test.com",
        "payload": {},
        "recurrence": {"type": "CUSTOM_CRON"}
    }

    response = client.post("/api/v1/tasks", json=test_payload)
    assert response.status_code == 422
    response_data = response.json()
    assert "is required for CUSTOM_CRON" in response_data["detail"][0]["msg"]
