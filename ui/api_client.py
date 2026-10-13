from typing import Any

import httpx


class MementoApiError(RuntimeError):
    pass


class MementoApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def list_notes(self, tag: str | None = None) -> list[dict[str, Any]]:
        params = {"tag": tag} if tag else None
        return self._request("GET", "/notes", params=params)

    def search_notes(self, query: str) -> list[dict[str, Any]]:
        return self._request("GET", "/notes/search", params={"q": query})

    def list_tags(self) -> list[str]:
        return self._request("GET", "/tags")

    def create_note(
        self,
        title: str,
        content: str,
        tags: list[str],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            "/notes",
            json={"title": title, "content": content, "tags": tags},
        )

    def update_note(
        self,
        note_id: str,
        title: str,
        content: str,
        tags: list[str],
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/notes/{note_id}",
            json={"title": title, "content": content, "tags": tags},
        )

    def delete_note(self, note_id: str) -> None:
        self._request("DELETE", f"/notes/{note_id}", expect_json=False)

    def _request(
        self,
        method: str,
        path: str,
        expect_json: bool = True,
        **kwargs: Any,
    ) -> Any:
        try:
            response = httpx.request(
                method,
                f"{self.base_url}{path}",
                timeout=5.0,
                **kwargs,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise MementoApiError(
                f"API returned {error.response.status_code}: {error.response.text}"
            ) from error
        except httpx.HTTPError as error:
            raise MementoApiError(f"API request failed: {error}") from error

        if not expect_json:
            return None
        return response.json()
