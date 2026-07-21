import pytest
from fastapi.testclient import TestClient

from metacat_api.config import settings
from metacat_api.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def set_settings():
    settings.json_data_dir = "./example_data"
