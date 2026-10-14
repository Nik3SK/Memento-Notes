from fastapi.testclient import TestClient

from app.main import app


def test_version_returns_app_metadata() -> None:
    client = TestClient(app)

    response = client.get("/version")

    assert response.status_code == 200
    assert response.json()["app_name"] == "Memento Notes API"
    assert response.json()["version"] == "0.2.0"
