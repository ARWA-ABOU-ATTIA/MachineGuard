
from fastapi.testclient import TestClient

from app.main import app, THRESHOLD

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["model"] == "Tuned Gradient Boosting"
    assert data["version"] == "1.0.0"


def test_predict_valid_input():
    payload = {
        "air_temperature": 300.0,
        "process_temperature": 310.0,
        "rotational_speed": 1500,
        "torque": 40.0,
        "tool_wear": 100,
        "machine_type": "L"
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert 0 <= data["failure_score"] <= 1
    assert data["threshold"] == THRESHOLD
    assert data["prediction"] in [0, 1]

    expected_prediction = int(
        data["failure_score"] >= THRESHOLD
    )

    assert data["prediction"] == expected_prediction

    assert data["status"] in [
        "Failure Risk Detected",
        "No Failure Risk Detected"
    ]


def test_predict_invalid_machine_type():
    payload = {
        "air_temperature": 300.0,
        "process_temperature": 310.0,
        "rotational_speed": 1500,
        "torque": 40.0,
        "tool_wear": 100,
        "machine_type": "X"
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_negative_temperature():
    payload = {
        "air_temperature": -10.0,
        "process_temperature": 310.0,
        "rotational_speed": 1500,
        "torque": 40.0,
        "tool_wear": 100,
        "machine_type": "L"
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422


def test_predict_missing_field():
    payload = {
        "air_temperature": 300.0,
        "process_temperature": 310.0,
        "rotational_speed": 1500,
        "torque": 40.0,
        "machine_type": "L"
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 422
