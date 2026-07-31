"""Health endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app


def test_healthz():
    with TestClient(app) as client:
        res = client.get("/healthz")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "ok"


def test_api_health():
    with TestClient(app) as client:
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
