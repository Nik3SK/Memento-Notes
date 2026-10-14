import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import Depends, FastAPI, HTTPException, Response, status

from app.config import load_settings
from app.schemas import NoteCreate, NoteResponse, NoteUpdate
from app.storage import NoteNotFoundError, NoteStore


settings = load_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

logger = logging.getLogger(__name__)
note_store: NoteStore | None = None


def get_note_store() -> NoteStore:
    global note_store
    if note_store is None:
        note_store = NoteStore(settings.storage_dir)
    return note_store


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    logger.info("Memento Notes API started")
    yield


app = FastAPI(
    title=settings.app_name,
    description="A minimal local notes service powered by FastAPI.",
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/version")
async def version() -> dict[str, str]:
    logger.info("Version requested")
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
    }


@app.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    payload: NoteCreate,
    store: NoteStore = Depends(get_note_store),
) -> NoteResponse:
    note = store.create_note(
        title=payload.title,
        content=payload.content,
        tags=payload.tags,
    )
    logger.info("Create note request completed for %s", note.id)
    return NoteResponse(**asdict(note))


@app.get("/notes", response_model=list[NoteResponse])
async def list_notes(store: NoteStore = Depends(get_note_store)) -> list[NoteResponse]:
    notes = store.list_notes()
    logger.info("List notes request completed with %s notes", len(notes))
    return [NoteResponse(**asdict(note)) for note in notes]


@app.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    store: NoteStore = Depends(get_note_store),
) -> NoteResponse:
    try:
        note = store.get_note(note_id)
    except NoteNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    logger.info("Get note request completed for %s", note_id)
    return NoteResponse(**asdict(note))


@app.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: str,
    payload: NoteUpdate,
    store: NoteStore = Depends(get_note_store),
) -> NoteResponse:
    try:
        note = store.update_note(
            note_id=note_id,
            title=payload.title,
            content=payload.content,
            tags=payload.tags,
        )
    except NoteNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    logger.info("Update note request completed for %s", note_id)
    return NoteResponse(**asdict(note))


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: str,
    store: NoteStore = Depends(get_note_store),
) -> Response:
    try:
        store.delete_note(note_id)
    except NoteNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))
    logger.info("Delete note request completed for %s", note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
