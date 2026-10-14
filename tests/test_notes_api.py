import pytest
from fastapi.testclient import TestClient

from app.main import app, get_note_store
from app.storage import NoteStore


@pytest.fixture()
def client(tmp_path):
    store = NoteStore(tmp_path)
    app.dependency_overrides[get_note_store] = lambda: store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_note(client: TestClient) -> None:
    response = client.post(
        "/notes",
        json={
            "title": "API note",
            "content": "Created through HTTP",
            "tags": ["API", "notes"],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == "API note"
    assert body["content"] == "Created through HTTP"
    assert body["tags"] == ["api", "notes"]
    assert body["created_at"]
    assert body["updated_at"]


def test_list_notes(client: TestClient) -> None:
    first_note = client.post("/notes", json={"title": "First"}).json()
    second_note = client.post("/notes", json={"title": "Second"}).json()

    response = client.get("/notes")

    assert response.status_code == 200
    assert [note["id"] for note in response.json()] == [
        second_note["id"],
        first_note["id"],
    ]


def test_get_note_by_id(client: TestClient) -> None:
    created_note = client.post(
        "/notes",
        json={"title": "Readable", "content": "Details"},
    ).json()

    response = client.get(f"/notes/{created_note['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created_note["id"]
    assert response.json()["title"] == "Readable"


def test_update_note_by_id(client: TestClient) -> None:
    created_note = client.post("/notes", json={"title": "Draft"}).json()

    response = client.put(
        f"/notes/{created_note['id']}",
        json={
            "title": "Final",
            "content": "Updated text",
            "tags": ["final"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created_note["id"]
    assert body["title"] == "Final"
    assert body["content"] == "Updated text"
    assert body["tags"] == ["final"]
    assert body["created_at"] == created_note["created_at"]


def test_delete_note_by_id(client: TestClient) -> None:
    created_note = client.post("/notes", json={"title": "Temporary"}).json()

    delete_response = client.delete(f"/notes/{created_note['id']}")
    get_response = client.get(f"/notes/{created_note['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_unknown_note_returns_404(client: TestClient) -> None:
    assert client.get("/notes/missing").status_code == 404
    assert client.put("/notes/missing", json={"title": "Nope"}).status_code == 404
    assert client.delete("/notes/missing").status_code == 404


def test_note_title_is_required(client: TestClient) -> None:
    response = client.post("/notes", json={"title": ""})

    assert response.status_code == 422
