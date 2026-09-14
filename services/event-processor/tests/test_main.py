import base64
import json
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app, validate_event


client = TestClient(app)


def valid_event():
    return {
        "event_id": "test-event-001",
        "type": "EARTHQUAKE",
        "latitude": 59.3293,
        "longitude": 18.0686,
        "source": "USGS",
        "severity": "HIGH",
    }


def test_validate_valid_event():
    validate_event(valid_event())


def test_validate_missing_event_id():
    event = valid_event()
    del event["event_id"]

    try:
        validate_event(event)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_validate_invalid_latitude():
    event = valid_event()
    event["latitude"] = 100

    try:
        validate_event(event)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_validate_invalid_longitude():
    event = valid_event()
    event["longitude"] = 200

    try:
        validate_event(event)
        assert False, "Expected ValueError"
    except ValueError:
        assert True


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["service"] == "event-processor"


def test_pubsub_without_data():
    response = client.post(
        "/pubsub",
        json={"message": {}},
    )

    assert response.status_code == 400


def test_pubsub_invalid_event():
    invalid_event = {
        "event_id": "invalid-event",
        "latitude": 1000,
    }

    encoded_data = base64.b64encode(
        json.dumps(invalid_event).encode("utf-8")
    ).decode("utf-8")

    response = client.post(
        "/pubsub",
        json={
            "message": {
                "data": encoded_data,
            }
        },
    )

    assert response.status_code == 400