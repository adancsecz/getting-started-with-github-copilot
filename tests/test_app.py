import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": [],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == []


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up student@example.com for Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == [
        "student@example.com"
    ]


def test_signup_rejects_duplicate_participant(client):
    signup_url = "/activities/Chess%20Club/signup"
    params = {"email": "student@example.com"}
    client.post(signup_url, params=params)

    response = client.post(signup_url, params=params)

    assert response.status_code == 400
    assert client.get("/activities").json()["Chess Club"]["participants"] == [
        "student@example.com"
    ]


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant(client):
    signup_url = "/activities/Chess%20Club/signup"
    params = {"email": "student@example.com"}
    client.post(signup_url, params=params)

    response = client.delete("/activities/Chess%20Club/participants", params=params)

    assert response.status_code == 200
    assert response.json() == {"message": "Removed student@example.com from Chess Club"}
    assert client.get("/activities").json()["Chess Club"]["participants"] == []


def test_remove_participant_from_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_unregistered_participant(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"