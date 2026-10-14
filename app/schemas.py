from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1)
    content: str = ""
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: str = Field(min_length=1)
    content: str = ""
    tags: list[str] = Field(default_factory=list)


class NoteResponse(BaseModel):
    id: str
    title: str
    content: str
    tags: list[str]
    created_at: str
    updated_at: str
