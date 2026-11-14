"""
BhashaVerse - Backend API Test Suite
Validates all FastAPI routes, request/response models, moderation workflows,
exports, search filters, and AI chat endpoints using TestClient.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from Backend.main import app
from Backend.config import get_moderator_key


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Bhashaverse"
    assert "/docs" in data["documentation"]


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["database_connected"] is True
    assert data["total_proverbs"] >= 20


def test_list_proverbs_pagination(client):
    response = client.get("/api/proverbs?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 5
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total_count"] >= 20
    assert data["total_pages"] >= 4


def test_list_proverbs_filter_language(client):
    response = client.get("/api/proverbs?language=Telugu")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["language"] == "Telugu"


def test_get_proverb_by_id(client):
    # Fetch list first to get a valid ID
    list_resp = client.get("/api/proverbs?page_size=1")
    first_id = list_resp.json()["items"][0]["id"]

    response = client.get(f"/api/proverbs/{first_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == first_id
    assert "proverb" in data
    assert "meaning" in data


def test_get_proverb_not_found(client):
    response = client.get("/api/proverbs/99999999")
    assert response.status_code == 404


def test_submit_proverb_success_and_validation(client):
    # 1. Invalid submission (missing meaning)
    invalid_payload = {
        "proverb": "ఆలస్యం అమృతం విషం",
        "language": "Telugu",
        "meaning": "Hi",  # too short
        "terms_confirmed": True
    }
    resp_invalid = client.post("/api/proverbs", json=invalid_payload)
    assert resp_invalid.status_code in (400, 422)

    # 2. Valid submission
    token = uuid.uuid4().hex[:6]
    valid_payload = {
        "proverb": f"టెస్ట్ సామెత ఇది కేవలం టెస్టింగ్ కోసం {token}",
        "language": "Telugu",
        "meaning": "This is a test proverb for automated unit testing.",
        "english_translation": "Testing proverb translation",
        "cultural_context": "Created during automated backend tests",
        "category": "Wisdom",
        "contributor_name": "API Test Suite",
        "contributor_email": "tester@example.com",
        "terms_confirmed": True
    }
    resp_valid = client.post("/api/proverbs", json=valid_payload)
    assert resp_valid.status_code == 201
    created = resp_valid.json()
    assert created["proverb"] == valid_payload["proverb"]
    assert created["status"] == "pending"


def test_analytics_stats(client):
    response = client.get("/api/analytics/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_approved"] >= 20
    assert data["languages_represented"] >= 10
    assert "Telugu" in data["language_counts"]
    assert "Hindi" in data["language_counts"]


def test_moderator_auth(client):
    valid_key = get_moderator_key()
    resp_valid = client.post("/api/moderation/auth", json={"passkey": valid_key})
    assert resp_valid.status_code == 200
    assert resp_valid.json()["authenticated"] is True

    resp_invalid = client.post("/api/moderation/auth", json={"passkey": "bad_key_12345"})
    assert resp_invalid.status_code == 200
    assert resp_invalid.json()["authenticated"] is False


def test_moderation_queue_and_actions(client):
    # Submit a proverb to ensure pending queue has at least one
    mod_token = uuid.uuid4().hex[:6]
    test_sub = {
        "proverb": f"కొత్త సామెత పరిశీలన కొరకు మాత్రమే {mod_token}",
        "language": "Telugu",
        "meaning": "Another test proverb to verify moderation approve/reject flow.",
        "terms_confirmed": True
    }
    create_resp = client.post("/api/proverbs", json=test_sub)
    new_id = create_resp.json()["id"]

    # Reject it
    reject_resp = client.post(
        f"/api/moderation/{new_id}/reject",
        json={"reason": "Test rejection reason", "moderator_name": "TestMod"}
    )
    assert reject_resp.status_code == 200

    # Verify in rejected list
    rej_list = client.get("/api/moderation/rejected").json()
    rej_ids = [p["id"] for p in rej_list]
    assert new_id in rej_ids

    # Approve it
    approve_resp = client.post(
        f"/api/moderation/{new_id}/approve",
        json={"moderator_name": "TestMod"}
    )
    assert approve_resp.status_code == 200


def test_export_endpoints(client):
    resp_csv = client.get("/api/exports/csv")
    assert resp_csv.status_code == 200
    assert resp_csv.headers["content-type"].startswith("text/csv")
    assert len(resp_csv.content) > 500

    resp_json = client.get("/api/exports/json")
    assert resp_json.status_code == 200
    assert isinstance(resp_json.json(), list)
    assert len(resp_json.json()) >= 20


def test_chat_endpoint(client):
    payload = {
        "query": "Tell me a proverb about water or perseverance",
        "language_filter": "All",
        "engine_choice": "Offline Corpus Engine"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 10
