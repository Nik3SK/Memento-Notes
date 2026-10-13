from fastapi.testclient import TestClient

from app.main import app, settings


def test_version_returns_app_metadata() -> None:
    client = TestClient(app)

    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {
        "app_name": settings.app_name,
        "version": settings.app_version,
    }
