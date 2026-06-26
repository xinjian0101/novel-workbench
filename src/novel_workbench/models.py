from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

CURRENT_SCHEMA_VERSION = 1


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Scene:
    number: int
    title: str
    summary: str = ""
    status: str = "draft"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "summary": self.summary,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Scene":
        return cls(
            number=int(data["number"]),
            title=str(data["title"]),
            summary=str(data.get("summary", "")),
            status=str(data.get("status", "draft")),
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


@dataclass(slots=True)
class Chapter:
    number: int
    title: str
    content: str = ""
    summary: str = ""
    status: str = "draft"
    scenes: list[Scene] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "status": self.status,
            "scenes": [scene.to_dict() for scene in self.scenes],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Chapter":
        return cls(
            number=int(data["number"]),
            title=str(data["title"]),
            content=str(data.get("content", "")),
            summary=str(data.get("summary", "")),
            status=str(data.get("status", "draft")),
            scenes=[Scene.from_dict(item) for item in data.get("scenes", [])],
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


@dataclass(slots=True)
class ProjectNote:
    id: int
    title: str
    content: str = ""
    kind: str = "general"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "kind": self.kind,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectNote":
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            content=str(data.get("content", "")),
            kind=str(data.get("kind", "general")),
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


@dataclass(slots=True)
class ProgressEntry:
    id: int
    date: str
    words: int
    note: str = ""
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "words": self.words,
            "note": self.note,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProgressEntry":
        return cls(
            id=int(data["id"]),
            date=str(data["date"]),
            words=int(data["words"]),
            note=str(data.get("note", "")),
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


@dataclass(slots=True)
class NovelProject:
    slug: str
    title: str
    schema_version: int = CURRENT_SCHEMA_VERSION
    synopsis: str = ""
    genre: str = ""
    audience: str = ""
    revision_notes: str = ""
    target_words: int | None = None
    target_date: str | None = None
    chapters: list[Chapter] = field(default_factory=list)
    notes: list[ProjectNote] = field(default_factory=list)
    progress: list[ProgressEntry] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "slug": self.slug,
            "title": self.title,
            "synopsis": self.synopsis,
            "genre": self.genre,
            "audience": self.audience,
            "revision_notes": self.revision_notes,
            "target_words": self.target_words,
            "target_date": self.target_date,
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "notes": [note.to_dict() for note in self.notes],
            "progress": [entry.to_dict() for entry in self.progress],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NovelProject":
        return cls(
            schema_version=int(data.get("schema_version", 0)),
            slug=str(data["slug"]),
            title=str(data["title"]),
            synopsis=str(data.get("synopsis", "")),
            genre=str(data.get("genre", "")),
            audience=str(data.get("audience", "")),
            revision_notes=str(data.get("revision_notes", "")),
            target_words=_target_words_from_dict(data),
            target_date=_target_date_from_dict(data),
            chapters=[Chapter.from_dict(item) for item in data.get("chapters", [])],
            notes=[ProjectNote.from_dict(item) for item in data.get("notes", [])],
            progress=[ProgressEntry.from_dict(item) for item in data.get("progress", [])],
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


def _target_words_from_dict(data: dict[str, Any]) -> int | None:
    value = data.get("target_words")
    return None if value is None else int(value)


def _target_date_from_dict(data: dict[str, Any]) -> str | None:
    value = data.get("target_date")
    return None if value is None else str(value)
