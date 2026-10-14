import json

import pytest

from app.storage import NoteNotFoundError, NoteStore


def test_store_initializes_notes_file(tmp_path) -> None:
    store = NoteStore(tmp_path)

    assert store.notes_file.exists()
    assert json.loads(store.notes_file.read_text(encoding="utf-8")) == []


def test_create_and_get_note(tmp_path) -> None:
    store = NoteStore(tmp_path)

    note = store.create_note(
        title="First note",
        content="Hello from storage",
        tags=["Python", " notes ", "python", ""],
    )

    saved_note = store.get_note(note.id)
    assert saved_note.id == note.id
    assert saved_note.title == "First note"
    assert saved_note.content == "Hello from storage"
    assert saved_note.tags == ["notes", "python"]
    assert saved_note.created_at
    assert saved_note.updated_at


def test_list_notes_returns_newest_updated_first(tmp_path) -> None:
    store = NoteStore(tmp_path)
    first_note = store.create_note("First", "Content")
    second_note = store.create_note("Second", "Content")

    notes = store.list_notes()

    assert [note.id for note in notes] == [second_note.id, first_note.id]


def test_update_note_preserves_created_at(tmp_path) -> None:
    store = NoteStore(tmp_path)
    note = store.create_note("Draft", "Initial content", ["draft"])

    updated_note = store.update_note(
        note_id=note.id,
        title="Final",
        content="Updated content",
        tags=["final"],
    )

    assert updated_note.id == note.id
    assert updated_note.title == "Final"
    assert updated_note.content == "Updated content"
    assert updated_note.tags == ["final"]
    assert updated_note.created_at == note.created_at
    assert updated_note.updated_at >= note.updated_at


def test_delete_note_removes_it_from_storage(tmp_path) -> None:
    store = NoteStore(tmp_path)
    note = store.create_note("Temporary", "Delete me")

    store.delete_note(note.id)

    assert store.list_notes() == []
    with pytest.raises(NoteNotFoundError):
        store.get_note(note.id)


def test_missing_note_operations_raise_not_found(tmp_path) -> None:
    store = NoteStore(tmp_path)

    with pytest.raises(NoteNotFoundError):
        store.get_note("missing")
    with pytest.raises(NoteNotFoundError):
        store.update_note("missing", "Title", "Content")
    with pytest.raises(NoteNotFoundError):
        store.delete_note("missing")
