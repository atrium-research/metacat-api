import asyncio
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


def _get_event_loop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        return asyncio.new_event_loop()


@pytest.fixture
def client() -> TestClient:
    loop = _get_event_loop()
    with patch("asyncio.get_running_loop", return_value=loop):
        from metacat_api.main import app

        return TestClient(app)
