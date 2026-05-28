import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_db_session():

    session = AsyncMock()
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    return session
