import httpx
import pytest

from ui.api_client import MementoApiClient, MementoApiError


def test_api_client_lists_notes(monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == "http://testserver/notes?tag=python"
        return httpx.Response(200, json=[{"id": "note-1"}])

    transport = httpx.MockTransport(handler)

    def fake_request(method: str, url: str, **kwargs):
        with httpx.Client(transport=transport) as client:
            return client.request(method, url, **kwargs)

    monkeypatch.setattr(httpx, "request", fake_request)

    client = MementoApiClient("http://testserver/")

    assert client.list_notes(tag="python") == [{"id": "note-1"}]


def test_api_client_creates_note(monkeypatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url == "http://testserver/notes"
        assert request.read() == (
            b'{"title":"Title","content":"Content","tags":["work"]}'
        )
        return httpx.Response(201, json={"id": "note-1", "title": "Title"})

    transport = httpx.MockTransport(handler)

    def fake_request(method: str, url: str, **kwargs):
        with httpx.Client(transport=transport) as client:
            return client.request(method, url, **kwargs)

    monkeypatch.setattr(httpx, "request", fake_request)

    client = MementoApiClient("http://testserver")

    assert client.create_note("Title", "Content", ["work"]) == {
        "id": "note-1",
        "title": "Title",
    }


def test_api_client_raises_for_http_errors(monkeypatch) -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="broken")

    transport = httpx.MockTransport(handler)

    def fake_request(method: str, url: str, **kwargs):
        with httpx.Client(transport=transport) as client:
            return client.request(method, url, **kwargs)

    monkeypatch.setattr(httpx, "request", fake_request)

    client = MementoApiClient("http://testserver")

    with pytest.raises(MementoApiError, match="API returned 500"):
        client.health()
