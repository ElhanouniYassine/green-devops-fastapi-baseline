from __future__ import annotations
import os, pytest
from fastapi.testclient import TestClient
from src.app.main import app

@pytest.fixture(scope="session", autouse=True)
def _set_test_env():
    os.environ.setdefault("API_TOKEN", "devtoken")

@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture()
def auth_headers():
    return {"Authorization": f"Bearer {os.environ.get('API_TOKEN','devtoken')}"}
