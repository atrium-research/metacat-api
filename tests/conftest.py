from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

import tests
from metacat_api.main import app


@pytest.fixture
def client() -> Generator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def client_auth(client) -> Generator[TestClient]:
    client.headers["x-api-key"] = tests.api_key
    yield client
    client.headers.clear()
