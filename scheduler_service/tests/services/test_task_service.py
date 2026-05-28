import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from services.task_service import TaskService
from schemas.task_schemas import TaskCreate, Recurrence, RecurrenceType
from models.task import TaskDefinition, TaskExecution
import httpx
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_repo():

    repo = AsyncMock()
    repo.get_or_create_task_definition = AsyncMock()
    repo.create_task_execution = AsyncMock()
    repo.get_due_executions_and_lock = AsyncMock()
    repo.update_execution_status = AsyncMock()
    repo.set_polling_state = AsyncMock()
    repo.update_for_retry = AsyncMock()
    repo.get_execution_with_definition = AsyncMock()
    return repo

@pytest.fixture
def service(mock_repo):

    service = TaskService(AsyncMock())
    service.repo = mock_repo
    return service

async def test_create_task_service_logic(service, mock_repo):

    task_data = TaskCreate(
        name="Test Task",
        execution_time=datetime.now(),
        webhook_url="http://test.com",
        payload={"key": "value"},
        recurrence=Recurrence(type=RecurrenceType.DAILY),
        max_retries=5
    )
    mock_task_def = TaskDefinition(id=1, name="Test Task")
    mock_repo.get_or_create_task_definition.return_value = mock_task_def
    result = await service.create_task(task_data)
    mock_repo.get_or_create_task_definition.assert_called_once_with(
        name="Test Task", webhook_url="http://test.com", recurrence="DAILY", max_retries=5
    )
    mock_repo.create_task_execution.assert_called_once_with(
        task_definition_id=1, execution_time=task_data.execution_time, payload={"key": "value"}
    )
    assert result == mock_task_def

@patch('services.task_service.httpx.AsyncClient')
async def test_dispatch_due_tasks_failure_triggers_retry(mock_async_client, service, mock_repo):
    mock_task_def = TaskDefinition(id=1, name="Retry Task", max_retries=3)
    mock_task_exec = TaskExecution(id=1, definition=mock_task_def, retries=0, payload={})
    mock_repo.get_due_executions_and_lock.return_value = [mock_task_exec]

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError("Server Error", request=MagicMock(), response=mock_response)
    mock_async_client.return_value.__aenter__.return_value.post.return_value = mock_response

    await service.dispatch_due_tasks()
    mock_repo.update_for_retry.assert_called_once()
    mock_repo.update_execution_status.assert_not_called()

@patch('services.task_service.celery_app.send_task')
@patch('services.task_service.httpx.AsyncClient')
async def test_dispatch_due_tasks_async_triggers_polling(mock_async_client, mock_send_task, service, mock_repo):
    mock_task_def = TaskDefinition(id=2, name="Async Task")
    mock_task_exec = TaskExecution(id=2, definition=mock_task_def, payload={})
    mock_repo.get_due_executions_and_lock.return_value = [mock_task_exec]

    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.json.return_value = {"check_url": "http://poll.me/status/123"}
    mock_async_client.return_value.__aenter__.return_value.post.return_value = mock_response
    await service.dispatch_due_tasks()
    mock_repo.set_polling_state.assert_called_once_with(2, "http://poll.me/status/123")
    mock_send_task.assert_called_once_with('celery_worker.tasks.poll_webhook_status', args=[2])

@patch('services.task_service.httpx.AsyncClient')
async def test_poll_task_status_success(mock_async_client, service, mock_repo):
    mock_task_def = TaskDefinition(id=3, name="Polling Task", recurrence="NONE")
    mock_task_exec = TaskExecution(id=3, definition=mock_task_def, polling_url="http://poll.me/status/456", payload={})
    mock_repo.get_execution_with_definition.return_value = mock_task_exec

    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "SUCCESS"}
    mock_async_client.return_value.__aenter__.return_value.get.return_value = mock_response
    is_complete = await service.poll_task_status(3)

    assert is_complete is True
    mock_repo.update_execution_status.assert_called_once_with(3, "SUCCESS")
