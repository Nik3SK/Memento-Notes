from dataclasses import dataclass, field


@dataclass(frozen=True)
class Note:
    id: str
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
