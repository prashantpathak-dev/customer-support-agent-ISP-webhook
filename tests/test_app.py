from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "HEALTHY"}

def test_get_config():
    payload = {
        "fulfillmentInfo": {"tag": "get_config"},
        "sessionInfo": {
            "session": "projects/p/locations/l/agents/a/sessions/s123",
            "parameters": {}
        }
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    params = response.json()["sessionInfo"]["parameters"]
    assert params["config_fetched"] is True
    assert "throttle_playbook" in params

def test_outage_check_active():
    payload = {
        "fulfillmentInfo": {"tag": "check_outage"},
        "sessionInfo": {
            "session": "projects/p/locations/l/agents/a/sessions/s123",
            "parameters": {"zip_code": "560001"}
        }
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    params = response.json()["sessionInfo"]["parameters"]
    assert params["outage_exists"] is True
    assert params["outage_eta"] == "18:30"

def test_ticket_check_valid():
    payload = {
        "fulfillmentInfo": {"tag": "check_ticket"},
        "sessionInfo": {
            "session": "projects/p/locations/l/agents/a/sessions/s123",
            "parameters": {"ticket_id": "INC-10291"}
        }
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    params = response.json()["sessionInfo"]["parameters"]
    assert params["ticket_status"] == "IN_PROGRESS"

def test_backend_failure_handling():
    payload = {
        "fulfillmentInfo": {"tag": "check_outage"},
        "sessionInfo": {
            "session": "projects/p/locations/l/agents/a/sessions/s123",
            "parameters": {"zip_code": "999999"}
        }
    }
    response = client.post("/webhook", json=payload)
    assert response.status_code == 500
    assert response.json()["sessionInfo"]["parameters"]["webhook_status"] == "FAILED"