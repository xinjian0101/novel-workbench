from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Chapter:
    number: int
    title: str
    content: str = ""
    status: str = "draft"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Chapter":
        return cls(
            number=int(data["number"]),
            title=str(data["title"]),
            content=str(data.get("content", "")),
            status=str(data.get("status", "draft")),
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


@dataclass(slots=True)
class NovelProject:
    slug: str
    title: str
    synopsis: str = ""
    target_words: int | None = None
    chapters: list[Chapter] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title": self.title,
            "synopsis": self.synopsis,
            "target_words": self.target_words,
            "chapters": [chapter.to_dict() for chapter in self.chapters],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NovelProject":
        return cls(
            slug=str(data["slug"]),
            title=str(data["title"]),
            synopsis=str(data.get("synopsis", "")),
            target_words=_target_words_from_dict(data),
            chapters=[Chapter.from_dict(item) for item in data.get("chapters", [])],
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
        )


def _target_words_from_dict(data: dict[str, Any]) -> int | None:
    value = data.get("target_words")
    return None if value is None else int(value)
