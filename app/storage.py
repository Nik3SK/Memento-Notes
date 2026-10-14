import json
import logging
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.models import Note


logger = logging.getLogger(__name__)


class NoteNotFoundError(ValueError):
    pass


class NoteStore:
    def __init__(self, storage_dir: str | Path) -> None:
        self.storage_dir = Path(storage_dir)
        self.notes_file = self.storage_dir / "notes.json"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        if not self.notes_file.exists():
            self._write_notes([])

    def list_notes(self, tag: str | None = None) -> list[Note]:
        notes = self._read_notes()
        if tag:
            normalized_tag = self._normalize_tag(tag)
            notes = [note for note in notes if normalized_tag in note.tags]
        return sorted(notes, key=lambda note: note.updated_at, reverse=True)

    def search_notes(self, query: str) -> list[Note]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            return self.list_notes()

        matching_notes = [
            note
            for note in self._read_notes()
            if normalized_query in note.title.lower()
            or normalized_query in note.content.lower()
            or any(normalized_query in tag for tag in note.tags)
        ]
        logger.info(
            "Search for '%s' returned %s notes",
            normalized_query,
            len(matching_notes),
        )
        return sorted(matching_notes, key=lambda note: note.updated_at, reverse=True)

    def list_tags(self) -> list[str]:
        tags = {tag for note in self._read_notes() for tag in note.tags}
        return sorted(tags)

    def get_note(self, note_id: str) -> Note:
        for note in self._read_notes():
            if note.id == note_id:
                return note
        raise NoteNotFoundError(f"Note '{note_id}' was not found")

    def create_note(
        self,
        title: str,
        content: str,
        tags: list[str] | None = None,
    ) -> Note:
        now = self._now()
        note = Note(
            id=str(uuid4()),
            title=title,
            content=content,
            tags=self._normalize_tags(tags or []),
            created_at=now,
            updated_at=now,
        )
        notes = self._read_notes()
        notes.append(note)
        self._write_notes(notes)
        logger.info("Created note %s", note.id)
        return note

    def update_note(
        self,
        note_id: str,
        title: str,
        content: str,
        tags: list[str] | None = None,
    ) -> Note:
        notes = self._read_notes()
        for index, note in enumerate(notes):
            if note.id == note_id:
                updated_note = Note(
                    id=note.id,
                    title=title,
                    content=content,
                    tags=self._normalize_tags(tags or []),
                    created_at=note.created_at,
                    updated_at=self._now(),
                )
                notes[index] = updated_note
                self._write_notes(notes)
                logger.info("Updated note %s", note_id)
                return updated_note
        raise NoteNotFoundError(f"Note '{note_id}' was not found")

    def delete_note(self, note_id: str) -> None:
        notes = self._read_notes()
        remaining_notes = [note for note in notes if note.id != note_id]
        if len(remaining_notes) == len(notes):
            raise NoteNotFoundError(f"Note '{note_id}' was not found")
        self._write_notes(remaining_notes)
        logger.info("Deleted note %s", note_id)

    def _read_notes(self) -> list[Note]:
        with self.notes_file.open("r", encoding="utf-8") as file:
            raw_notes = json.load(file)
        return [Note(**raw_note) for raw_note in raw_notes]

    def _write_notes(self, notes: list[Note]) -> None:
        raw_notes = [asdict(note) for note in notes]
        temporary_file = self.notes_file.with_suffix(".tmp")
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(raw_notes, file, ensure_ascii=False, indent=2)
            file.write("\n")
        temporary_file.replace(self.notes_file)

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    @staticmethod
    def _normalize_tags(tags: list[str]) -> list[str]:
        normalized_tags = {NoteStore._normalize_tag(tag) for tag in tags if tag.strip()}
        return sorted(normalized_tags)

    @staticmethod
    def _normalize_tag(tag: str) -> str:
        return tag.strip().lower()
