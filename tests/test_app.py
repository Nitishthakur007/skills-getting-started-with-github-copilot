import os
import sys
import importlib

import pytest
from fastapi.testclient import TestClient

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import app as application_module


@pytest.fixture(autouse=True)
def reset_app_module():
    # Reload module before each test to reset in-memory state
    importlib.reload(application_module)
    yield


def test_get_activities():
    client = TestClient(application_module.app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    client = TestClient(application_module.app)
    email = "testuser@example.com"

    # Sign up
    resp = client.post("/activities/Chess%20Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    participants = resp.json()["Chess Club"]["participants"]
    assert email in participants

    # Unregister
    resp = client.delete("/activities/Chess%20Club/participants", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # Verify participant removed
    resp = client.get("/activities")
    participants = resp.json()["Chess Club"]["participants"]
    assert email not in participants
