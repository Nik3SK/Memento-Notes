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

    def list_notes(self) -> list[Note]:
        notes = self._read_notes()
        return sorted(notes, key=lambda note: note.updated_at, reverse=True)

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
        normalized_tags = {tag.strip().lower() for tag in tags if tag.strip()}
        return sorted(normalized_tags)
