from __future__ import annotations

import html
import json
import math
import re
import shutil
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .models import CURRENT_SCHEMA_VERSION, Chapter, NovelProject, ProgressEntry, ProjectNote, Scene, utc_now_iso

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHAPTER_HEADING_PATTERN = re.compile(r"^##\s+(?:Chapter\s+\d+:\s*)?(?P<title>.+?)\s*$", re.IGNORECASE)
VALID_STATUSES = {"draft", "revising", "done"}
VALID_NOTE_KINDS = {"general", "character", "location", "plot", "research"}
EXPORT_TEMPLATES = {
    "board",
    "default",
    "focus",
    "frontmatter",
    "handoff",
    "momentum",
    "outline",
    "pitch",
    "progress",
    "review",
    "revision",
}
EXPORT_PACK_TEMPLATES = (
    ("manuscript", "default", "{slug}.md"),
    ("frontmatter", "frontmatter", "{slug}-frontmatter.md"),
    ("pitch", "pitch", "{slug}-pitch.md"),
    ("focus", "focus", "{slug}-focus.md"),
    ("handoff", "handoff", "{slug}-handoff.md"),
    ("momentum", "momentum", "{slug}-momentum.md"),
    ("board", "board", "{slug}-board.md"),
    ("outline", "outline", "{slug}-outline.md"),
    ("progress", "progress", "{slug}-progress.md"),
    ("review", "review", "{slug}-review.md"),
    ("revision", "revision", "{slug}-revision.md"),
)
SITE_THEMES = ("classic", "editorial", "focus")
SAMPLE_PROJECT = {
    "slug": "moon-archive",
    "title": "Moon Archive",
    "synopsis": "A historian finds a city under the lunar dust.",
    "chapters": [
        {
            "title": "Signal",
            "content": "The first signal arrived at 03:17.",
            "scenes": [
                ("Night Shift", "Ada notices a repeating pulse hidden in archive static.", "done"),
                ("False Map", "The team traces the pulse to a city grid that should not exist.", "draft"),
            ],
        },
        {
            "title": "Descent",
            "content": "They opened the hatch and heard rain below.",
            "scenes": [
                ("Hatch Pressure", "Ada chooses to descend before the signal window closes.", "revising"),
                ("Underground Rain", "The lower city answers with weather, voices, and a locked door.", "draft"),
            ],
        },
    ],
}
STARTER_TEMPLATES = {
    "three-act": """# Working Title

One paragraph premise: protagonist, pressure, stakes, and the change that makes the story worth writing.

## Chapter 1: Opening Image

Draft the first scene here. Start close to the character, show the ordinary world under tension, and end with a reason to turn the page.

## Chapter 2: Inciting Incident

Draft the moment that changes the protagonist's plans.

## Chapter 3: First Choice

Draft the first irreversible decision.
""",
    "hero-journey": """# Working Title

One paragraph premise: the ordinary world, the call, the refusal, and the transformation the protagonist cannot avoid.

## Chapter 1: Ordinary World

Show the protagonist before the journey begins.

## Chapter 2: Call to Adventure

Introduce the invitation, threat, or discovery that demands action.

## Chapter 3: Crossing the Threshold

Draft the moment the protagonist leaves safety behind.
""",
    "mystery": """# Working Title

One paragraph premise: the crime, the investigator, the hidden pressure, and why solving it matters now.

## Chapter 1: The Body

Open with the discovery, disappearance, or impossible event.

## Chapter 2: First Suspect

Introduce the first plausible answer and the detail that makes it unstable.

## Chapter 3: False Pattern

Draft the clue trail that seems obvious but points in the wrong direction.
""",
    "romance": """# Working Title

One paragraph premise: the two leads, what they want, what keeps them apart, and why choosing love will cost something.

## Chapter 1: First Spark

Show the first charged encounter and the reason neither lead can ignore the other.

## Chapter 2: Forced Proximity

Create the situation that keeps the leads in each other's orbit.

## Chapter 3: First Vulnerability

Draft the moment one lead reveals a need, fear, or wound they meant to hide.
""",
    "sci-fi": """# Working Title

One paragraph premise: the speculative idea, the person closest to its consequences, the system under pressure, and the choice that changes the future.

## Chapter 1: The Anomaly

Open with the discovery, malfunction, signal, or impossible data point.

## Chapter 2: First Contact

Draft the first encounter with the force, machine, place, or intelligence that changes the rules.

## Chapter 3: System Failure

Show the moment the old assumptions stop protecting anyone.
""",
    "thriller": """# Working Title

One paragraph premise: the threat, the target, the deadline, and the secret that makes escape harder.

## Chapter 1: The Trigger

Open with the incident that turns ordinary danger into a countdown.

## Chapter 2: No Safe Place

Take away the obvious refuge, ally, or explanation.

## Chapter 3: First Reversal

Draft the reveal that proves the protagonist misunderstood the threat.
""",
}


class StorageError(Exception):
    """Base exception for recoverable storage and validation errors."""


class NotFoundError(StorageError):
    """Raised when a project or chapter cannot be found."""


class DuplicateError(StorageError):
    """Raised when creating a resource that already exists."""


def validate_slug(slug: str) -> str:
    normalized = slug.strip().lower()
    if not SLUG_PATTERN.fullmatch(normalized):
        raise StorageError("Slug must use lowercase letters, numbers, and single hyphens.")
    return normalized


def validate_title(title: str) -> str:
    normalized = title.strip()
    if not normalized:
        raise StorageError("Title is required.")
    if len(normalized) > 120:
        raise StorageError("Title must be 120 characters or fewer.")
    return normalized


def validate_status(status: str) -> str:
    normalized = status.strip().lower()
    if normalized not in VALID_STATUSES:
        allowed = ", ".join(sorted(VALID_STATUSES))
        raise StorageError(f"Status must be one of: {allowed}.")
    return normalized


def validate_note_kind(kind: str) -> str:
    normalized = kind.strip().lower()
    if normalized not in VALID_NOTE_KINDS:
        allowed = ", ".join(sorted(VALID_NOTE_KINDS))
        raise StorageError(f"Note kind must be one of: {allowed}.")
    return normalized


def validate_target_words(target_words: int) -> int:
    if target_words < 1:
        raise StorageError("Target word count must be greater than zero.")
    return target_words


def validate_progress_words(words: int) -> int:
    if words < 1:
        raise StorageError("Progress words must be greater than zero.")
    return words


def validate_progress_date(value: str) -> str:
    normalized = value.strip()
    try:
        date.fromisoformat(normalized)
    except ValueError as exc:
        raise StorageError("Progress date must use YYYY-MM-DD format.") from exc
    return normalized


def validate_target_date(value: str) -> str:
    normalized = value.strip()
    try:
        date.fromisoformat(normalized)
    except ValueError as exc:
        raise StorageError("Target date must use YYYY-MM-DD format.") from exc
    return normalized


def validate_optional_metadata(value: str, field_name: str) -> str:
    normalized = value.strip()
    if len(normalized) > 240:
        raise StorageError(f"{field_name} must be 240 characters or fewer.")
    return normalized


def validate_export_template(template: str) -> str:
    normalized = template.strip().lower()
    if normalized not in EXPORT_TEMPLATES:
        allowed = ", ".join(sorted(EXPORT_TEMPLATES))
        raise StorageError(f"Export template must be one of: {allowed}.")
    return normalized


def validate_starter_template(template: str) -> str:
    normalized = template.strip().lower()
    if normalized not in STARTER_TEMPLATES:
        allowed = ", ".join(sorted(STARTER_TEMPLATES))
        raise StorageError(f"Starter template must be one of: {allowed}.")
    return normalized


def count_words(content: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", content))


def parse_markdown_chapters(content: str) -> tuple[str, str, list[tuple[str, str]]]:
    lines = content.lstrip("\ufeff").splitlines()
    title = ""
    synopsis_lines: list[str] = []
    chapters: list[tuple[str, list[str]]] = []
    current_chapter: tuple[str, list[str]] | None = None

    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        match = CHAPTER_HEADING_PATTERN.match(line)
        if match:
            if current_chapter is not None:
                chapters.append(current_chapter)
            current_chapter = (match.group("title").strip(), [])
            continue
        if current_chapter is None:
            synopsis_lines.append(line)
        else:
            current_chapter[1].append(line)

    if current_chapter is not None:
        chapters.append(current_chapter)
    if not title:
        raise StorageError("Markdown must start with a '# Title' heading.")
    if not chapters:
        raise StorageError("Markdown must contain at least one '## Chapter' heading.")

    parsed_chapters = [(chapter_title, "\n".join(body).strip()) for chapter_title, body in chapters]
    return title, "\n".join(synopsis_lines).strip(), parsed_chapters


class ProjectStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.projects_dir = root / "projects"
        self.backups_dir = root / "backups"

    def initialize(self) -> None:
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def project_path(self, slug: str) -> Path:
        return self.projects_dir / f"{validate_slug(slug)}.json"

    def list_projects(self) -> list[NovelProject]:
        self.initialize()
        projects = [self._read_project(path) for path in sorted(self.projects_dir.glob("*.json"))]
        return sorted(projects, key=lambda project: project.updated_at, reverse=True)

    def workspace_dashboard(self) -> list[dict[str, str | int | None]]:
        rows: list[dict[str, str | int | None]] = []
        for project in self.list_projects():
            stats = _stats_for_project(project)
            rows.append(
                {
                    "slug": project.slug,
                    "title": project.title,
                    "chapters": stats["chapters"],
                    "words": stats["words"],
                    "logged_words": stats["logged_words"],
                    "current_streak_days": stats["current_streak_days"],
                    "target_words": stats["target_words"],
                    "progress_percent": stats["progress_percent"],
                    "updated_at": project.updated_at,
                }
            )
        return rows

    def export_dashboard(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(workspace_dashboard_lines(self.workspace_dashboard())).rstrip() + "\n", encoding="utf-8")
        return output_path

    def check_workspace(self) -> dict[str, int | list[dict[str, str]]]:
        self.initialize()
        checked = 0
        errors: list[dict[str, str]] = []
        for path in sorted(self.projects_dir.glob("*.json")):
            checked += 1
            try:
                project = self._read_project(path)
                if path.stem != project.slug:
                    errors.append(
                        {
                            "file": str(path),
                            "error": f"File name '{path.stem}' does not match project slug '{project.slug}'.",
                            "hint": f"Rename the file to '{project.slug}.json' or update the project slug.",
                        }
                    )
                _validate_chapter_numbers(project)
                _validate_scene_numbers(project)
            except StorageError as exc:
                errors.append({"file": str(path), "error": str(exc), "hint": _doctor_hint(str(exc))})
        return {"checked": checked, "ok": checked - len(errors), "errors": errors}

    def migrate_workspace(self, *, dry_run: bool = False) -> dict[str, int | list[str]]:
        self.initialize()
        checked = 0
        migrated: list[str] = []
        for path in sorted(self.projects_dir.glob("*.json")):
            checked += 1
            project = self._read_project(path)
            if path.stem != project.slug:
                raise StorageError(f"File name '{path.stem}' does not match project slug '{project.slug}'.")
            _validate_chapter_numbers(project)
            _validate_scene_numbers(project)
            normalized = _normalized_project_json(project)
            current = path.read_text(encoding="utf-8")
            if current == normalized:
                continue
            migrated.append(project.slug)
            if dry_run:
                continue
            self._snapshot_project(project, "migrate")
            path.write_text(normalized, encoding="utf-8")
        return {"checked": checked, "migrated": len(migrated), "projects": migrated}

    def create_project(self, slug: str, title: str, synopsis: str = "") -> NovelProject:
        self.initialize()
        project = NovelProject(slug=validate_slug(slug), title=validate_title(title), synopsis=synopsis.strip())
        path = self.project_path(project.slug)
        if path.exists():
            raise DuplicateError(f"Project '{project.slug}' already exists.")
        self._write_project(project)
        return project

    def create_sample_project(self, slug: str = SAMPLE_PROJECT["slug"]) -> NovelProject:
        project = self.create_project(slug, SAMPLE_PROJECT["title"], SAMPLE_PROJECT["synopsis"])
        for chapter_data in SAMPLE_PROJECT["chapters"]:
            if isinstance(chapter_data, dict):
                chapter = self.add_chapter(project.slug, str(chapter_data["title"]), str(chapter_data["content"]))
                for title, summary, status in chapter_data.get("scenes", []):
                    self.add_scene(project.slug, chapter.number, title, summary, status)
            else:
                chapter_title, content = chapter_data
                self.add_chapter(project.slug, chapter_title, content)
        return self.get_project(project.slug)

    def import_markdown(self, slug: str, markdown_path: Path) -> NovelProject:
        if not markdown_path.exists():
            raise NotFoundError(f"Markdown file does not exist: {markdown_path}")
        title, synopsis, chapters = parse_markdown_chapters(_read_utf8_text(markdown_path, "Markdown file"))
        project = self.create_project(slug, title, synopsis)
        for chapter_title, content in chapters:
            self.add_chapter(project.slug, chapter_title, content)
        return self.get_project(project.slug)

    def write_starter_markdown(self, output_path: Path, *, template: str = "three-act", overwrite: bool = False) -> Path:
        template = validate_starter_template(template)
        if output_path.exists() and not overwrite:
            raise DuplicateError(f"Starter file already exists: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(STARTER_TEMPLATES[template], encoding="utf-8")
        return output_path

    def get_project(self, slug: str) -> NovelProject:
        path = self.project_path(slug)
        if not path.exists():
            raise NotFoundError(f"Project '{validate_slug(slug)}' does not exist.")
        return self._read_project(path)

    def rename_project(self, slug: str, new_slug: str, new_title: str | None = None) -> NovelProject:
        project = self.get_project(slug)
        old_path = self.project_path(project.slug)
        normalized_slug = validate_slug(new_slug)
        new_path = self.project_path(normalized_slug)
        if new_path.exists() and new_path != old_path:
            raise DuplicateError(f"Project '{normalized_slug}' already exists.")
        self._snapshot_project(project, "rename")
        project.slug = normalized_slug
        if new_title is not None:
            project.title = validate_title(new_title)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        if old_path != new_path:
            old_path.unlink()
        return self.get_project(project.slug)

    def add_chapter(self, slug: str, title: str, content: str = "", status: str = "draft", summary: str = "") -> Chapter:
        project = self.get_project(slug)
        next_number = max((chapter.number for chapter in project.chapters), default=0) + 1
        chapter = Chapter(
            number=next_number,
            title=validate_title(title),
            content=content,
            summary=summary.strip(),
            status=validate_status(status),
        )
        project.chapters.append(chapter)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return chapter

    def update_chapter(
        self,
        slug: str,
        number: int,
        *,
        title: str | None = None,
        content: str | None = None,
        summary: str | None = None,
        status: str | None = None,
    ) -> Chapter:
        if number < 1:
            raise StorageError("Chapter number must be greater than zero.")
        project = self.get_project(slug)
        chapter = next((item for item in project.chapters if item.number == number), None)
        if chapter is None:
            raise NotFoundError(f"Chapter {number} does not exist in project '{project.slug}'.")
        if title is not None:
            chapter.title = validate_title(title)
        if content is not None:
            chapter.content = content
        if summary is not None:
            chapter.summary = summary.strip()
        if status is not None:
            chapter.status = validate_status(status)
        chapter.updated_at = utc_now_iso()
        project.updated_at = chapter.updated_at
        self._write_project(project)
        return chapter

    def move_chapter(self, slug: str, number: int, new_number: int) -> Chapter:
        if number < 1 or new_number < 1:
            raise StorageError("Chapter numbers must be greater than zero.")
        project = self.get_project(slug)
        chapters = sorted(project.chapters, key=lambda item: item.number)
        if new_number > len(chapters):
            raise StorageError(f"New chapter number must be between 1 and {len(chapters)}.")
        index = next((idx for idx, item in enumerate(chapters) if item.number == number), None)
        if index is None:
            raise NotFoundError(f"Chapter {number} does not exist in project '{project.slug}'.")
        chapter = chapters.pop(index)
        chapters.insert(new_number - 1, chapter)
        now = utc_now_iso()
        for idx, item in enumerate(chapters, start=1):
            item.number = idx
            if item is chapter:
                item.updated_at = now
        project.chapters = chapters
        project.updated_at = now
        self._write_project(project)
        return chapter

    def delete_chapter(self, slug: str, number: int) -> Chapter:
        if number < 1:
            raise StorageError("Chapter number must be greater than zero.")
        project = self.get_project(slug)
        chapters = sorted(project.chapters, key=lambda item: item.number)
        index = next((idx for idx, item in enumerate(chapters) if item.number == number), None)
        if index is None:
            raise NotFoundError(f"Chapter {number} does not exist in project '{project.slug}'.")
        self._snapshot_project(project, "delete-chapter")
        chapter = chapters.pop(index)
        now = utc_now_iso()
        for idx, item in enumerate(chapters, start=1):
            item.number = idx
        project.chapters = chapters
        project.updated_at = now
        self._write_project(project)
        return chapter

    def add_scene(
        self,
        slug: str,
        chapter_number: int,
        title: str,
        summary: str = "",
        status: str = "draft",
    ) -> Scene:
        project = self.get_project(slug)
        chapter = _find_chapter(project, chapter_number)
        next_number = max((scene.number for scene in chapter.scenes), default=0) + 1
        scene = Scene(
            number=next_number,
            title=validate_title(title),
            summary=summary.strip(),
            status=validate_status(status),
        )
        chapter.scenes.append(scene)
        now = utc_now_iso()
        chapter.updated_at = now
        project.updated_at = now
        self._write_project(project)
        return scene

    def list_scenes(self, slug: str, chapter_number: int) -> list[Scene]:
        project = self.get_project(slug)
        return sorted(_find_chapter(project, chapter_number).scenes, key=lambda item: item.number)

    def update_scene(
        self,
        slug: str,
        chapter_number: int,
        scene_number: int,
        *,
        title: str | None = None,
        summary: str | None = None,
        status: str | None = None,
    ) -> Scene:
        if title is None and summary is None and status is None:
            raise StorageError("Provide at least one scene field to update.")
        project = self.get_project(slug)
        chapter = _find_chapter(project, chapter_number)
        scene = _find_scene(chapter, scene_number, project.slug)
        if title is not None:
            scene.title = validate_title(title)
        if summary is not None:
            scene.summary = summary.strip()
        if status is not None:
            scene.status = validate_status(status)
        now = utc_now_iso()
        scene.updated_at = now
        chapter.updated_at = now
        project.updated_at = now
        self._write_project(project)
        return scene

    def delete_scene(self, slug: str, chapter_number: int, scene_number: int) -> Scene:
        project = self.get_project(slug)
        chapter = _find_chapter(project, chapter_number)
        scenes = sorted(chapter.scenes, key=lambda item: item.number)
        index = next((idx for idx, item in enumerate(scenes) if item.number == scene_number), None)
        if index is None:
            raise NotFoundError(
                f"Scene {scene_number} does not exist in chapter {chapter.number} of project '{project.slug}'."
            )
        self._snapshot_project(project, "delete-scene")
        scene = scenes.pop(index)
        for idx, item in enumerate(scenes, start=1):
            item.number = idx
        now = utc_now_iso()
        chapter.scenes = scenes
        chapter.updated_at = now
        project.updated_at = now
        self._write_project(project)
        return scene

    def add_note(self, slug: str, title: str, content: str = "", kind: str = "general") -> ProjectNote:
        project = self.get_project(slug)
        next_id = max((note.id for note in project.notes), default=0) + 1
        note = ProjectNote(id=next_id, title=validate_title(title), content=content, kind=validate_note_kind(kind))
        project.notes.append(note)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return note

    def list_notes(self, slug: str, kind: str | None = None) -> list[ProjectNote]:
        project = self.get_project(slug)
        if kind is None:
            return sorted(project.notes, key=lambda item: item.id)
        normalized_kind = validate_note_kind(kind)
        return [note for note in sorted(project.notes, key=lambda item: item.id) if note.kind == normalized_kind]

    def delete_note(self, slug: str, note_id: int) -> ProjectNote:
        if note_id < 1:
            raise StorageError("Note id must be greater than zero.")
        project = self.get_project(slug)
        index = next((idx for idx, item in enumerate(project.notes) if item.id == note_id), None)
        if index is None:
            raise NotFoundError(f"Note {note_id} does not exist in project '{project.slug}'.")
        self._snapshot_project(project, "delete-note")
        note = project.notes.pop(index)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return note

    def update_note(
        self,
        slug: str,
        note_id: int,
        *,
        title: str | None = None,
        content: str | None = None,
        kind: str | None = None,
    ) -> ProjectNote:
        if note_id < 1:
            raise StorageError("Note id must be greater than zero.")
        if title is None and content is None and kind is None:
            raise StorageError("Provide at least one note field to update.")
        project = self.get_project(slug)
        note = next((item for item in project.notes if item.id == note_id), None)
        if note is None:
            raise NotFoundError(f"Note {note_id} does not exist in project '{project.slug}'.")
        if title is not None:
            note.title = validate_title(title)
        if content is not None:
            note.content = content
        if kind is not None:
            note.kind = validate_note_kind(kind)
        note.updated_at = utc_now_iso()
        project.updated_at = note.updated_at
        self._write_project(project)
        return note

    def add_progress(self, slug: str, words: int, entry_date: str, note: str = "") -> ProgressEntry:
        project = self.get_project(slug)
        next_id = max((entry.id for entry in project.progress), default=0) + 1
        entry = ProgressEntry(
            id=next_id,
            date=validate_progress_date(entry_date),
            words=validate_progress_words(words),
            note=note.strip(),
        )
        project.progress.append(entry)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return entry

    def list_progress(self, slug: str) -> list[ProgressEntry]:
        project = self.get_project(slug)
        return sorted(project.progress, key=lambda item: (item.date, item.id))

    def update_progress(
        self,
        slug: str,
        progress_id: int,
        *,
        entry_date: str | None = None,
        words: int | None = None,
        note: str | None = None,
    ) -> ProgressEntry:
        if progress_id < 1:
            raise StorageError("Progress id must be greater than zero.")
        if entry_date is None and words is None and note is None:
            raise StorageError("Provide at least one progress field to update.")
        project = self.get_project(slug)
        entry = next((item for item in project.progress if item.id == progress_id), None)
        if entry is None:
            raise NotFoundError(f"Progress entry {progress_id} does not exist in project '{project.slug}'.")
        if entry_date is not None:
            entry.date = validate_progress_date(entry_date)
        if words is not None:
            entry.words = validate_progress_words(words)
        if note is not None:
            entry.note = note.strip()
        entry.updated_at = utc_now_iso()
        project.updated_at = entry.updated_at
        self._write_project(project)
        return entry

    def delete_progress(self, slug: str, progress_id: int) -> ProgressEntry:
        if progress_id < 1:
            raise StorageError("Progress id must be greater than zero.")
        project = self.get_project(slug)
        index = next((idx for idx, item in enumerate(project.progress) if item.id == progress_id), None)
        if index is None:
            raise NotFoundError(f"Progress entry {progress_id} does not exist in project '{project.slug}'.")
        self._snapshot_project(project, "delete-progress")
        entry = project.progress.pop(index)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return entry

    def set_target_words(self, slug: str, target_words: int | None) -> NovelProject:
        project = self.get_project(slug)
        project.target_words = None if target_words is None else validate_target_words(target_words)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return project

    def set_target_date(self, slug: str, target_date: str | None) -> NovelProject:
        project = self.get_project(slug)
        project.target_date = None if target_date is None else validate_target_date(target_date)
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return project

    def update_project_metadata(
        self,
        slug: str,
        *,
        genre: str | None = None,
        audience: str | None = None,
        revision_notes: str | None = None,
    ) -> NovelProject:
        if genre is None and audience is None and revision_notes is None:
            raise StorageError("Provide at least one metadata field to update.")
        project = self.get_project(slug)
        if genre is not None:
            project.genre = validate_optional_metadata(genre, "Genre")
        if audience is not None:
            project.audience = validate_optional_metadata(audience, "Audience")
        if revision_notes is not None:
            project.revision_notes = revision_notes.strip()
        project.updated_at = utc_now_iso()
        self._write_project(project)
        return project

    def project_stats(self, slug: str) -> dict[str, int | None]:
        project = self.get_project(slug)
        return _stats_for_project(project)

    def project_context(self, slug: str) -> dict[str, object]:
        project = self.get_project(slug)
        return _context_for_project(project)

    def export_context_json(self, slug: str, output_path: Path) -> Path:
        context = self.project_context(slug)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(context, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return output_path

    def export_site(self, slug: str, output_dir: Path, theme: str = "classic", base_url: str = "") -> list[Path]:
        project = self.get_project(slug)
        theme = validate_site_theme(theme)
        base_url = _normalize_site_base_url(base_url)
        output_dir.mkdir(parents=True, exist_ok=True)
        social_card_name = "social-card.svg"
        social_card_url = f"{base_url}/{social_card_name}" if base_url else social_card_name
        feed_url = f"{base_url}/feed.xml" if base_url else ""
        llms_url = f"{base_url}/llms.txt" if base_url else ""
        manifest_url = f"{base_url}/site.webmanifest" if base_url else ""
        files = {
            output_dir / "index.html": _site_index_html(project, theme, social_card_url, feed_url, llms_url, manifest_url),
            output_dir / "manuscript.html": _site_manuscript_html(project, theme, social_card_url, feed_url, llms_url, manifest_url),
            output_dir / "context.json": json.dumps(_context_for_project(project), indent=2, ensure_ascii=False) + "\n",
            output_dir / social_card_name: social_card_svg(project, theme),
        }
        if base_url:
            files[output_dir / "sitemap.xml"] = _site_sitemap_xml(base_url)
            files[output_dir / "robots.txt"] = _site_robots_txt(base_url)
            files[output_dir / "feed.xml"] = _site_feed_xml(project, base_url)
            files[output_dir / "llms.txt"] = _site_llms_txt(project, base_url)
            files[output_dir / "site.webmanifest"] = _site_webmanifest(project, base_url, theme)
        for path, content in files.items():
            path.write_text(content, encoding="utf-8")
        return list(files)

    def export_social_card(self, slug: str, output_path: Path, theme: str = "classic") -> Path:
        project = self.get_project(slug)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(social_card_svg(project, theme), encoding="utf-8")
        return output_path

    def export_launch_copy(self, slug: str, output_path: Path, base_url: str = "") -> Path:
        project = self.get_project(slug)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(launch_copy_lines(project, _normalize_site_base_url(base_url))).rstrip() + "\n", encoding="utf-8")
        return output_path

    def search(self, slug: str, query: str) -> list[dict[str, str | int]]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            raise StorageError("Search query is required.")
        project = self.get_project(slug)
        results: list[dict[str, str | int]] = []
        for chapter in project.chapters:
            scene_text = "\n".join(f"{scene.title}\n{scene.summary}" for scene in chapter.scenes)
            haystack = f"{chapter.title}\n{chapter.summary}\n{chapter.content}\n{scene_text}".lower()
            if normalized_query not in haystack:
                continue
            snippet_source = _first_matching_text(
                normalized_query,
                chapter.content,
                chapter.summary,
                *(scene.summary for scene in chapter.scenes),
                *(scene.title for scene in chapter.scenes),
                chapter.title,
            )
            results.append(
                {
                    "type": "chapter",
                    "number": chapter.number,
                    "title": chapter.title,
                    "status": chapter.status,
                    "snippet": _snippet(snippet_source, normalized_query),
                }
            )
        for note in project.notes:
            haystack = f"{note.title}\n{note.content}\n{note.kind}".lower()
            if normalized_query not in haystack:
                continue
            results.append(
                {
                    "type": "note",
                    "number": note.id,
                    "title": note.title,
                    "status": note.kind,
                    "snippet": _snippet(note.content or note.title, normalized_query),
                }
            )
        return results

    def backup_project(self, slug: str, output_dir: Path) -> Path:
        project = self.get_project(slug)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = _backup_timestamp()
        output_path = output_dir / f"{project.slug}-{timestamp}.json"
        shutil.copy2(self.project_path(project.slug), output_path)
        return output_path

    def restore_backup(self, backup_path: Path, *, overwrite: bool = False) -> NovelProject:
        if not backup_path.exists():
            raise NotFoundError(f"Backup file does not exist: {backup_path}")
        project = self._read_project(backup_path)
        target_path = self.project_path(project.slug)
        if target_path.exists():
            if not overwrite:
                raise DuplicateError(f"Project '{project.slug}' already exists. Use --force to overwrite it.")
            current = self._read_project(target_path)
            self._snapshot_project(current, "restore")
        self._write_project(project)
        return project

    def export_markdown(self, slug: str, output_path: Path, template: str = "default", template_path: Path | None = None) -> Path:
        project = self.get_project(slug)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if template_path is not None:
            if not template_path.exists():
                raise NotFoundError(f"Template file does not exist: {template_path}")
            lines = _custom_export_lines(project, _read_utf8_text(template_path, "Template file"))
        else:
            template = validate_export_template(template)
            if template == "frontmatter":
                lines = _frontmatter_export_lines(project)
            elif template == "board":
                lines = board_lines(project)
            elif template == "focus":
                lines = focus_lines(project)
            elif template == "handoff":
                lines = handoff_lines(project)
            elif template == "momentum":
                lines = momentum_lines(project)
            elif template == "outline":
                lines = outline_lines(project)
            elif template == "pitch":
                lines = pitch_lines(project)
            elif template == "progress":
                lines = _progress_export_lines(project)
            elif template == "review":
                lines = review_lines(project)
            elif template == "revision":
                lines = revision_lines(project)
            else:
                lines = _default_export_lines(project)
        output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return output_path

    def export_pack(self, slug: str, output_dir: Path) -> list[Path]:
        project = self.get_project(slug)
        output_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        for _name, template, filename in EXPORT_PACK_TEMPLATES:
            output_path = output_dir / filename.format(slug=project.slug)
            paths.append(self.export_markdown(project.slug, output_path, template))
        return paths

    def export_share_kit(self, slug: str, output_dir: Path, theme: str = "classic", base_url: str = "") -> list[Path]:
        project = self.get_project(slug)
        normalized_base_url = _normalize_site_base_url(base_url)
        output_dir.mkdir(parents=True, exist_ok=True)

        pitch_path = output_dir / f"{project.slug}-pitch.md"
        announcement_path = output_dir / f"{project.slug}-announcement.md"
        launch_copy_path = output_dir / f"{project.slug}-launch-copy.md"
        outreach_plan_path = output_dir / f"{project.slug}-outreach-plan.md"
        social_card_path = output_dir / f"{project.slug}-social-card.svg"
        pitch_path.write_text("\n".join(pitch_lines(project)).rstrip() + "\n", encoding="utf-8")
        announcement_path.write_text("\n".join(share_announcement_lines(project, normalized_base_url)).rstrip() + "\n", encoding="utf-8")
        launch_copy_path.write_text("\n".join(launch_copy_lines(project, normalized_base_url)).rstrip() + "\n", encoding="utf-8")
        outreach_plan_path.write_text("\n".join(outreach_plan_lines(project, normalized_base_url)).rstrip() + "\n", encoding="utf-8")
        social_card_path.write_text(social_card_svg(project, theme), encoding="utf-8")

        site_paths = self.export_site(project.slug, output_dir / "site", theme=theme, base_url=normalized_base_url)
        pack_paths = self.export_pack(project.slug, output_dir / "pack")
        return [pitch_path, announcement_path, launch_copy_path, outreach_plan_path, social_card_path, *site_paths, *pack_paths]

    def _read_project(self, path: Path) -> NovelProject:
        try:
            raw = path.read_text(encoding="utf-8")
            data = json.loads(raw)
            project = NovelProject.from_dict(data)
        except UnicodeDecodeError as exc:
            raise StorageError(f"Project file is invalid: {path} (file is not valid UTF-8)") from exc
        except json.JSONDecodeError as exc:
            raise StorageError(
                f"Project file is invalid: {path} (JSON syntax error at line {exc.lineno}, column {exc.colno}: {exc.msg})"
            ) from exc
        except KeyError as exc:
            field = str(exc.args[0])
            raise StorageError(f"Project file is invalid: {path} (missing required field: {field})") from exc
        except (TypeError, ValueError) as exc:
            detail = str(exc) or exc.__class__.__name__
            raise StorageError(f"Project file is invalid: {path} (invalid field value: {detail})") from exc
        try:
            _validate_project_fields(project)
        except StorageError as exc:
            raise StorageError(f"Project file is invalid: {path} (invalid field value: {exc})") from exc
        return project

    def _write_project(self, project: NovelProject) -> None:
        path = self.project_path(project.slug)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_normalized_project_json(project), encoding="utf-8")

    def _snapshot_project(self, project: NovelProject, action: str) -> Path:
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.backups_dir / f"{project.slug}-{action}-{_backup_timestamp()}.json"
        shutil.copy2(self.project_path(project.slug), output_path)
        return output_path


def _default_export_lines(project: NovelProject) -> list[str]:
    lines = [f"# {project.title}", ""]
    if project.synopsis:
        lines.extend([project.synopsis, ""])
    for chapter in sorted(project.chapters, key=lambda item: item.number):
        lines.extend([f"## Chapter {chapter.number}: {chapter.title}", "", chapter.content.strip(), ""])
    return lines


def workspace_dashboard_lines(rows: list[dict[str, str | int | None]]) -> list[str]:
    lines = ["# Novel Workbench Dashboard", ""]
    if not rows:
        lines.append("No projects found.")
        return lines
    lines.extend(
        [
            "| Slug | Title | Chapters | Words | Logged | Streak | Target | Progress | Updated |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in rows:
        target = "" if row["target_words"] is None else str(row["target_words"])
        progress = "" if row["progress_percent"] is None else f"{row['progress_percent']}%"
        lines.append(
            "| "
            f"{_escape_table_cell(str(row['slug']))} | "
            f"{_escape_table_cell(str(row['title']))} | "
            f"{row['chapters']} | "
            f"{row['words']} | "
            f"{row['logged_words']} | "
            f"{row['current_streak_days']} | "
            f"{target} | "
            f"{progress} | "
            f"{_escape_table_cell(str(row['updated_at']))} |"
        )
    return lines


def validate_site_theme(theme: str) -> str:
    normalized = theme.strip().lower()
    if normalized not in SITE_THEMES:
        choices = ", ".join(SITE_THEMES)
        raise StorageError(f"Unknown site theme '{theme}'. Choose one of: {choices}.")
    return normalized


def _site_index_html(
    project: NovelProject,
    theme: str = "classic",
    image_url: str = "social-card.svg",
    feed_url: str = "",
    llms_url: str = "",
    manifest_url: str = "",
) -> str:
    stats = _stats_for_project(project)
    chapters = sorted(project.chapters, key=lambda item: item.number)
    notes = sorted(project.notes, key=lambda item: item.id)
    progress = sorted(project.progress, key=lambda item: (item.date, item.id), reverse=True)[:8]
    next_action = _context_next_action(project, next((chapter for chapter in chapters if chapter.status != "done"), None))
    metadata = [
        ("Chapters", str(stats["chapters"])),
        ("Words", str(stats["words"])),
        ("Logged", str(stats["logged_words"])),
        ("Streak", f"{stats['current_streak_days']} days"),
        ("Target", "-" if stats["target_words"] is None else str(stats["target_words"])),
        ("Progress", "-" if stats["progress_percent"] is None else f"{stats['progress_percent']}%"),
    ]
    body = [
        '<!doctype html>',
        f'<html lang="en" data-theme="{_html(theme)}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_html(project.title)} - Novel Workbench</title>",
        _site_meta_tags(project, "Project dashboard", image_url),
        _site_feed_link(project, feed_url),
        _site_llms_link(llms_url),
        _site_manifest_link(manifest_url),
        f"<style>{_site_css()}</style>",
        "</head>",
        "<body>",
        '<header class="hero">',
        '<div class="wrap">',
        '<p class="eyebrow">Novel Workbench</p>',
        f"<h1>{_html(project.title)}</h1>",
        f"<p>{_html(project.synopsis or 'A local-first novel project workspace.')}</p>",
        '<nav><a href="manuscript.html">Read manuscript</a><a href="context.json">Download context JSON</a></nav>',
        "</div>",
        "</header>",
        '<main class="wrap">',
        '<section class="metrics" aria-label="Project metrics">',
    ]
    for label, value in metadata:
        body.append(f'<div><span>{_html(label)}</span><strong>{_html(value)}</strong></div>')
    body.extend(
        [
            "</section>",
            '<section class="panel">',
            "<h2>Next Action</h2>",
            f"<p>{_html(str(next_action['prompt']))}</p>",
            "</section>",
            '<section class="grid">',
            '<div class="panel">',
            "<h2>Chapters</h2>",
            _site_chapter_list(chapters),
            "</div>",
            '<div class="panel">',
            "<h2>Notes</h2>",
            _site_note_list(notes),
            "</div>",
            "</section>",
            '<section class="panel">',
            "<h2>Recent Progress</h2>",
            _site_progress_table(progress),
            "</section>",
            '<section class="panel callout">',
            "<h2>Try Novel Workbench</h2>",
            "<p>This static project site was exported from a local Novel Workbench workspace.</p>",
            '<pre><code>python -m pip install "git+https://github.com/xinjian0101/novel-workbench.git"\nnovel --workspace workspace tour --output-dir exports</code></pre>',
            '<p><a href="https://github.com/xinjian0101/novel-workbench">Open the GitHub repository</a></p>',
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )
    return "\n".join(body) + "\n"


def _site_manuscript_html(
    project: NovelProject,
    theme: str = "classic",
    image_url: str = "social-card.svg",
    feed_url: str = "",
    llms_url: str = "",
    manifest_url: str = "",
) -> str:
    body = [
        '<!doctype html>',
        f'<html lang="en" data-theme="{_html(theme)}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{_html(project.title)} Manuscript</title>",
        _site_meta_tags(project, "Manuscript", image_url),
        _site_feed_link(project, feed_url),
        _site_llms_link(llms_url),
        _site_manifest_link(manifest_url),
        f"<style>{_site_css()}</style>",
        "</head>",
        "<body>",
        '<main class="wrap manuscript">',
        f'<p><a href="index.html">Back to project dashboard</a></p>',
        f"<h1>{_html(project.title)}</h1>",
    ]
    if project.synopsis:
        body.append(f'<p class="synopsis">{_html(project.synopsis)}</p>')
    chapters = sorted(project.chapters, key=lambda item: item.number)
    if not chapters:
        body.append("<p>No chapters yet.</p>")
    for chapter in chapters:
        body.extend(
            [
                f"<article><h2>Chapter {chapter.number}: {_html(chapter.title)}</h2>",
                f"<p>{_html(chapter.content.strip()).replace(chr(10), '<br>')}</p></article>",
            ]
        )
    body.extend(["</main>", "</body>", "</html>"])
    return "\n".join(body) + "\n"


def _site_meta_tags(project: NovelProject, page_label: str, image_url: str = "social-card.svg") -> str:
    title = f"{project.title} - {page_label}"
    description = project.synopsis or "A local-first novel project workspace exported by Novel Workbench."
    return "\n".join(
        [
            '<meta name="generator" content="Novel Workbench">',
            f'<meta name="description" content="{_html(description)}">',
            f'<meta property="og:title" content="{_html(title)}">',
            f'<meta property="og:description" content="{_html(description)}">',
            f'<meta property="og:image" content="{_html(image_url)}">',
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Novel Workbench">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{_html(title)}">',
            f'<meta name="twitter:description" content="{_html(description)}">',
            f'<meta name="twitter:image" content="{_html(image_url)}">',
        ]
    )


def _site_feed_link(project: NovelProject, feed_url: str) -> str:
    if not feed_url:
        return ""
    return f'<link rel="alternate" type="application/rss+xml" title="{_html(project.title)} updates" href="{_html(feed_url)}">'


def _site_llms_link(llms_url: str) -> str:
    if not llms_url:
        return ""
    return f'<link rel="help" type="text/plain" href="{_html(llms_url)}">'


def _site_manifest_link(manifest_url: str) -> str:
    if not manifest_url:
        return ""
    return f'<link rel="manifest" href="{_html(manifest_url)}">'


def social_card_svg(project: NovelProject, theme: str = "classic") -> str:
    theme = validate_site_theme(theme)
    palette = {
        "classic": ("#0f172a", "#14b8a6", "#d1fae5", "#f8fafc", "#cbd5e1"),
        "editorial": ("#1f2937", "#b45309", "#fef3c7", "#fff7ed", "#e5e7eb"),
        "focus": ("#111827", "#4f46e5", "#e0e7ff", "#f9fafb", "#d1d5db"),
    }[theme]
    background, accent, accent_soft, foreground, muted = palette
    stats = _stats_for_project(project)
    title_lines = _svg_wrap_text(project.title, 23, 2)
    synopsis = project.synopsis or "A local-first novel project managed with Novel Workbench."
    synopsis_lines = _svg_wrap_text(synopsis, 56, 3)
    metadata = []
    if project.genre:
        metadata.append(project.genre)
    if project.audience:
        metadata.append(f"{project.audience} readers")
    metadata.append(_count_label(stats["chapters"], "chapter"))
    metadata.append(_count_label(stats["words"], "word"))
    if stats["target_words"] is not None:
        metadata.append(f"{stats['progress_percent']}% of {stats['target_words']} words")
    metadata_line = " / ".join(metadata)

    title_svg = "\n".join(
        f'<text x="96" y="{156 + index * 78}" class="title">{_html(line)}</text>' for index, line in enumerate(title_lines)
    )
    synopsis_start = 318 if len(title_lines) == 2 else 250
    synopsis_svg = "\n".join(
        f'<text x="96" y="{synopsis_start + index * 44}" class="synopsis">{_html(line)}</text>'
        for index, line in enumerate(synopsis_lines)
    )
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="640" viewBox="0 0 1280 640" role="img">',
            f"<title>{_html(project.title)} social preview</title>",
            "<style>",
            ".label{font:700 24px Arial,sans-serif;letter-spacing:2px;text-transform:uppercase}",
            ".title{font:800 66px Arial,sans-serif}",
            ".synopsis{font:400 34px Arial,sans-serif}",
            ".meta{font:700 28px Arial,sans-serif}",
            ".footer{font:700 24px Arial,sans-serif}",
            "</style>",
            f'<rect width="1280" height="640" fill="{background}"/>',
            f'<rect x="46" y="46" width="1188" height="548" rx="28" fill="{background}" stroke="{accent}" stroke-width="4"/>',
            f'<path d="M930 46h304v548H790z" fill="{accent}" opacity="0.18"/>',
            f'<path d="M1040 46h194v548H900z" fill="{accent_soft}" opacity="0.12"/>',
            f'<text x="96" y="104" class="label" fill="{accent_soft}">Novel Workbench Share Card</text>',
            title_svg.replace('class="title"', f'class="title" fill="{foreground}"'),
            synopsis_svg.replace('class="synopsis"', f'class="synopsis" fill="{muted}"'),
            f'<rect x="96" y="474" width="1088" height="74" rx="18" fill="{accent}" opacity="0.22"/>',
            f'<text x="126" y="521" class="meta" fill="{foreground}">{_html(metadata_line)}</text>',
            f'<text x="96" y="584" class="footer" fill="{accent_soft}">local-first / markdown export / static HTML demo</text>',
            "</svg>",
        ]
    ) + "\n"


def _svg_wrap_text(value: str, limit: int, max_lines: int) -> list[str]:
    raw_words = value.strip().split()
    if not raw_words:
        return [""]
    words: list[str] = []
    for word in raw_words:
        if len(word) <= limit:
            words.append(word)
            continue
        words.extend(word[index : index + limit] for index in range(0, len(word), limit))
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    used_words = " ".join(lines).split()
    if len(used_words) < len(words) and lines:
        lines[-1] = lines[-1].rstrip(".") + "..."
    return lines


def _count_label(count: int, singular: str) -> str:
    suffix = "" if count == 1 else "s"
    return f"{count} {singular}{suffix}"


def _normalize_site_base_url(base_url: str) -> str:
    base_url = base_url.strip().rstrip("/")
    if not base_url:
        return ""
    if not (base_url.startswith("https://") or base_url.startswith("http://")):
        raise StorageError("Site base URL must start with http:// or https://.")
    return base_url


def _site_sitemap_xml(base_url: str) -> str:
    urls = ["index.html", "manuscript.html", "context.json", "social-card.svg", "feed.xml", "llms.txt", "site.webmanifest"]
    entries = "\n".join(f"  <url><loc>{_html(base_url + '/' + url)}</loc></url>" for url in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>\n"
    )


def _site_robots_txt(base_url: str) -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"


def _site_feed_xml(project: NovelProject, base_url: str) -> str:
    description = project.synopsis or "A local-first novel project workspace exported by Novel Workbench."
    updated_at = project.updated_at or project.created_at
    items = [
        (
            f"{project.title} project dashboard",
            f"{base_url}/index.html",
            "Project status, chapter plan, notes, and writing progress.",
        ),
        (
            f"{project.title} manuscript",
            f"{base_url}/manuscript.html",
            "Readable manuscript export for review.",
        ),
        (
            f"{project.title} context JSON",
            f"{base_url}/context.json",
            "Structured project context for editors and AI handoff.",
        ),
    ]
    item_xml = "\n".join(
        "    <item>\n"
        f"      <title>{_html(title)}</title>\n"
        f"      <link>{_html(link)}</link>\n"
        f"      <guid isPermaLink=\"true\">{_html(link)}</guid>\n"
        f"      <description>{_html(summary)}</description>\n"
        f"      <pubDate>{_rss_pub_date(updated_at)}</pubDate>\n"
        "    </item>"
        for title, link, summary in items
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        f"    <title>{_html(project.title)} - Novel Workbench</title>\n"
        f"    <link>{_html(base_url)}/</link>\n"
        f"    <description>{_html(description)}</description>\n"
        "    <generator>Novel Workbench</generator>\n"
        f"    <lastBuildDate>{_rss_pub_date(updated_at)}</lastBuildDate>\n"
        f"{item_xml}\n"
        "  </channel>\n"
        "</rss>\n"
    )


def _rss_pub_date(timestamp: str) -> str:
    normalized = timestamp.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return "Thu, 01 Jan 1970 00:00:00 +0000"
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")


def _site_llms_txt(project: NovelProject, base_url: str) -> str:
    description = project.synopsis or "A local-first novel project workspace exported by Novel Workbench."
    lines = [
        f"# {project.title}",
        "",
        f"> {description}",
        "",
        "This is a static Novel Workbench project export. Use these public files to understand the project without requiring an account, server, database, or background network calls.",
        "",
        "## Core Files",
        "",
        f"- [Project dashboard]({base_url}/index.html): project summary, chapter state, notes, and recent writing progress.",
        f"- [Manuscript]({base_url}/manuscript.html): readable manuscript export.",
        f"- [Context JSON]({base_url}/context.json): structured AI/editor handoff context with project data, stats, next action, chapter state, and recent progress.",
        f"- [Social preview]({base_url}/social-card.svg): SVG preview card for public posts.",
        f"- [RSS feed]({base_url}/feed.xml): update feed for the public static export.",
        "",
        "## Tooling",
        "",
        "- Source project: https://github.com/xinjian0101/novel-workbench",
        "- Recommended local trial: `novel --workspace workspace tour --output-dir exports`",
        "- Data model: local UTF-8 JSON projects plus generated Markdown, HTML, SVG, RSS, and context JSON exports.",
        "",
        "## Use Guidelines",
        "",
        "- Prefer `context.json` for structured automation and editor handoff.",
        "- Prefer `manuscript.html` for prose review.",
        "- Prefer `index.html` for project status and navigation.",
        "- Do not assume private workspace files exist beyond the public export listed here.",
    ]
    return "\n".join(lines) + "\n"


def _site_webmanifest(project: NovelProject, base_url: str, theme: str) -> str:
    palette = {
        "classic": ("#2563eb", "#f8fafc"),
        "editorial": ("#7c2d12", "#fff7ed"),
        "focus": ("#047857", "#ecfdf5"),
    }[validate_site_theme(theme)]
    manifest = {
        "name": f"{project.title} - Novel Workbench",
        "short_name": project.title[:24] or "Novel Workbench",
        "description": project.synopsis or "A local-first novel project workspace exported by Novel Workbench.",
        "start_url": f"{base_url}/index.html",
        "scope": f"{base_url}/",
        "display": "standalone",
        "background_color": palette[1],
        "theme_color": palette[0],
        "icons": [
            {
                "src": f"{base_url}/social-card.svg",
                "type": "image/svg+xml",
                "sizes": "any",
                "purpose": "any",
            }
        ],
    }
    return json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"


def _site_chapter_list(chapters: list[Chapter]) -> str:
    if not chapters:
        return "<p>No chapters yet.</p>"
    items = []
    for chapter in chapters:
        summary = f"<p>{_html(chapter.summary)}</p>" if chapter.summary else ""
        scenes = _site_scene_list(chapter)
        items.append(
            "<li>"
            f"<strong>{chapter.number}. {_html(chapter.title)}</strong>"
            f"<span>{_html(chapter.status)} / {count_words(chapter.content)} words</span>"
            f"{summary}"
            f"{scenes}"
            "</li>"
        )
    return f"<ol>{''.join(items)}</ol>"


def _site_scene_list(chapter: Chapter) -> str:
    if not chapter.scenes:
        return ""
    items = []
    for scene in sorted(chapter.scenes, key=lambda item: item.number):
        summary = f"<p>{_html(scene.summary)}</p>" if scene.summary else ""
        items.append(
            "<li>"
            f"<strong>{chapter.number}.{scene.number} {_html(scene.title)}</strong>"
            f"<span>{_html(scene.status)}</span>"
            f"{summary}"
            "</li>"
        )
    return '<ol class="scenes">' + "".join(items) + "</ol>"


def _site_note_list(notes: list[ProjectNote]) -> str:
    if not notes:
        return "<p>No planning notes yet.</p>"
    items = []
    for note in notes[:8]:
        preview = _note_preview(note.content) if note.content else ""
        items.append(
            "<li>"
            f"<strong>{_html(note.title)}</strong>"
            f"<span>{_html(note.kind)}</span>"
            f"<p>{_html(preview)}</p>"
            "</li>"
        )
    return f"<ul>{''.join(items)}</ul>"


def _site_progress_table(entries: list[ProgressEntry]) -> str:
    if not entries:
        return "<p>No progress entries yet.</p>"
    rows = [
        f"<tr><td>{_html(entry.date)}</td><td>{entry.words}</td><td>{_html(entry.note)}</td></tr>"
        for entry in entries
    ]
    return "<table><thead><tr><th>Date</th><th>Words</th><th>Note</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table>"


def _site_css() -> str:
    return (
        ":root{color-scheme:light;--ink:#1f2933;--muted:#5f6c7b;--line:#d8dee6;--paper:#f7f8fa;--accent:#0f766e;}"
        "[data-theme=editorial]{--ink:#27201c;--muted:#74665c;--line:#d8cfc5;--paper:#fbf7f0;--accent:#9f3a25;}"
        "[data-theme=focus]{--ink:#172033;--muted:#536179;--line:#cfd8e6;--paper:#f2f7ff;--accent:#2563eb;}"
        "*{box-sizing:border-box}body{margin:0;font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--ink);background:var(--paper);line-height:1.6}"
        ".wrap{width:min(1040px,92vw);margin:0 auto}.hero{background:#111827;color:white;padding:56px 0 40px}.hero p{max-width:760px;color:#d1d5db}"
        "[data-theme=editorial] .hero{background:#3b241d}[data-theme=focus] .hero{background:#172554}"
        ".eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:12px;font-weight:700;color:#99f6e4}.hero h1{font-size:clamp(36px,7vw,72px);line-height:1;margin:0 0 16px}"
        "nav{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}a{color:var(--accent);font-weight:700}nav a{color:white;border:1px solid #5eead4;padding:10px 14px;text-decoration:none}"
        ".metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px;margin:24px 0}.metrics div,.panel{background:white;border:1px solid var(--line);padding:18px}"
        ".metrics span{display:block;color:var(--muted);font-size:13px}.metrics strong{font-size:24px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}"
        "h2{margin-top:0}ol,ul{padding-left:22px}li{margin:0 0 14px}li span{display:block;color:var(--muted);font-size:14px}"
        ".scenes{margin-top:10px;padding-left:18px;border-left:3px solid var(--line)}.scenes li{margin-bottom:10px}"
        "table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid var(--line);padding:10px}.manuscript{background:white;padding:30px;margin-top:24px;margin-bottom:24px}"
        ".manuscript article{border-top:1px solid var(--line);padding-top:20px}.synopsis{color:var(--muted);font-size:18px}"
        ".callout{margin:24px 0 40px}.callout pre{overflow:auto;background:#0f172a;color:#e5e7eb;padding:14px;border:1px solid #1f2937}"
    )


def _html(value: object) -> str:
    return html.escape(str(value), quote=True)


def outline_lines(project: NovelProject) -> list[str]:
    lines = [f"# {project.title} Outline", ""]
    if project.synopsis:
        lines.extend([project.synopsis, ""])
    if project.genre or project.audience:
        lines.append("## Metadata")
        lines.append("")
        if project.genre:
            lines.append(f"- Genre: {project.genre}")
        if project.audience:
            lines.append(f"- Audience: {project.audience}")
        lines.append("")
    lines.extend(["## Chapters", ""])
    if not project.chapters:
        lines.append("No chapters yet.")
        return lines
    for chapter in sorted(project.chapters, key=lambda item: item.number):
        lines.append(f"{chapter.number}. {chapter.title} [{chapter.status}]")
        if chapter.summary:
            lines.append(f"   {chapter.summary}")
        for scene in sorted(chapter.scenes, key=lambda item: item.number):
            lines.append(f"   {chapter.number}.{scene.number} {scene.title} [{scene.status}]")
            if scene.summary:
                lines.append(f"      {scene.summary}")
    return lines


def board_lines(project: NovelProject) -> list[str]:
    lines = [f"# {project.title} Status Board", ""]
    chapters = sorted(project.chapters, key=lambda item: item.number)
    if not chapters:
        lines.append("No chapters yet.")
        return lines
    for status in ("draft", "revising", "done"):
        items = [chapter for chapter in chapters if chapter.status == status]
        lines.extend([f"## {status.title()}", ""])
        if not items:
            lines.append("No chapters.")
        else:
            for chapter in items:
                lines.append(f"- Chapter {chapter.number}: {chapter.title} ({count_words(chapter.content)} words)")
                if chapter.summary:
                    lines.append(f"  - {chapter.summary}")
                unfinished_scenes = [scene for scene in chapter.scenes if scene.status != "done"]
                if unfinished_scenes:
                    scene_labels = ", ".join(
                        f"{chapter.number}.{scene.number} {scene.title} [{scene.status}]" for scene in unfinished_scenes
                    )
                    lines.append(f"  - Open scenes: {scene_labels}")
        lines.append("")
    if lines[-1] == "":
        lines.pop()
    return lines


def focus_lines(project: NovelProject) -> list[str]:
    stats = _stats_for_project(project)
    lines = [f"# {project.title} Focus", ""]
    lines.extend(
        [
            "## Current Position",
            "",
            f"- Words: {stats['words']}",
            f"- Logged words: {stats['logged_words']}",
            f"- Current streak: {stats['current_streak_days']} days",
        ]
    )
    if stats["target_words"] is not None:
        lines.append(f"- Target progress: {stats['progress_percent']}%")
        lines.append(f"- Remaining words: {stats['remaining_words']}")
    if stats["required_daily_words"] is not None:
        lines.append(f"- Required daily words: {stats['required_daily_words']}")

    chapters = sorted(project.chapters, key=lambda item: item.number)
    next_chapter = next((chapter for chapter in chapters if chapter.status != "done"), None)
    lines.extend(["", "## Next Writing Move", ""])
    if next_chapter is None:
        if chapters:
            lines.append("- All chapters are marked done. Review the revision checklist or export the manuscript.")
        else:
            lines.append("- Add the first chapter.")
    else:
        lines.append(
            f"- Work on Chapter {next_chapter.number}: {next_chapter.title} "
            f"[{next_chapter.status}] - {count_words(next_chapter.content)} words"
        )
        if next_chapter.summary:
            lines.append(f"  - Summary: {next_chapter.summary}")
        open_scenes = [scene for scene in sorted(next_chapter.scenes, key=lambda item: item.number) if scene.status != "done"]
        if open_scenes:
            lines.append("  - Open scenes:")
            for scene in open_scenes:
                lines.append(f"    - {next_chapter.number}.{scene.number} {scene.title} [{scene.status}]")
                if scene.summary:
                    lines.append(f"      {scene.summary}")

    lines.extend(["", "## Recent Writing", ""])
    recent_entries = sorted(project.progress, key=lambda item: (item.date, item.id), reverse=True)[:3]
    if not recent_entries:
        lines.append("No progress entries yet.")
    else:
        for entry in recent_entries:
            line = f"- {entry.date}: +{entry.words} words"
            if entry.note:
                line = f"{line} - {entry.note}"
            lines.append(line)

    revision_notes = project.revision_notes.strip()
    if revision_notes:
        lines.extend(["", "## Revision Reminder", "", revision_notes])
    return lines


def handoff_lines(project: NovelProject) -> list[str]:
    stats = _stats_for_project(project)
    chapters = sorted(project.chapters, key=lambda item: item.number)
    next_chapter = next((chapter for chapter in chapters if chapter.status != "done"), None)

    lines = [f"# {project.title} Handoff", ""]
    lines.extend(["## Project Snapshot", ""])
    lines.append(f"- Slug: `{project.slug}`")
    if project.synopsis.strip():
        lines.append(f"- Synopsis: {project.synopsis}")
    if project.genre.strip():
        lines.append(f"- Genre: {project.genre}")
    if project.audience.strip():
        lines.append(f"- Audience: {project.audience}")
    lines.append(f"- Manuscript words: {stats['words']}")
    lines.append(f"- Logged words: {stats['logged_words']}")
    lines.append(f"- Current streak: {stats['current_streak_days']} days")
    if stats["target_words"] is not None:
        lines.append(f"- Target words: {stats['target_words']}")
        lines.append(f"- Remaining words: {stats['remaining_words']}")
        lines.append(f"- Progress: {stats['progress_percent']}%")
    if stats["required_daily_words"] is not None:
        lines.append(f"- Required daily words: {stats['required_daily_words']}")

    lines.extend(["", "## Next Action", ""])
    if next_chapter is None:
        if chapters:
            lines.append("- All chapters are marked done. Start with a revision pass or export review.")
        else:
            lines.append("- Add the first chapter.")
    else:
        lines.append(
            f"- Continue Chapter {next_chapter.number}: {next_chapter.title} "
            f"[{next_chapter.status}] - {count_words(next_chapter.content)} words"
        )
        if next_chapter.summary:
            lines.append(f"  - Summary: {next_chapter.summary}")
        open_scenes = [scene for scene in sorted(next_chapter.scenes, key=lambda item: item.number) if scene.status != "done"]
        if open_scenes:
            lines.append("  - Open scenes:")
            for scene in open_scenes:
                lines.append(f"    - {next_chapter.number}.{scene.number} {scene.title} [{scene.status}]")
                if scene.summary:
                    lines.append(f"      {scene.summary}")

    lines.extend(["", "## Continuity Notes", ""])
    if project.revision_notes.strip():
        lines.append(project.revision_notes.strip())
    elif not project.notes:
        lines.append("No continuity notes yet.")
    if project.notes:
        for note in sorted(project.notes, key=lambda item: item.id)[:8]:
            lines.append(f"- {note.title} [{note.kind}]")
            if note.content.strip():
                lines.append(f"  {_note_preview(note.content)}")

    lines.extend(["", "## Chapter State", "", "| # | Title | Status | Words | Summary |", "|---:|---|---|---:|---|"])
    if not chapters:
        lines.append("| - | No chapters yet | - | 0 | - |")
    else:
        for chapter in chapters:
            title = _escape_table_cell(chapter.title)
            summary = _escape_table_cell(chapter.summary)
            lines.append(f"| {chapter.number} | {title} | {chapter.status} | {count_words(chapter.content)} | {summary} |")

    lines.extend(["", "## Recent Progress", ""])
    recent_entries = sorted(project.progress, key=lambda item: (item.date, item.id), reverse=True)[:5]
    if not recent_entries:
        lines.append("No progress entries yet.")
    else:
        lines.extend(["| Date | Words | Note |", "|---|---:|---|"])
        for entry in recent_entries:
            note = _escape_table_cell(entry.note)
            lines.append(f"| {entry.date} | {entry.words} | {note} |")

    lines.extend(["", "## Prompt", ""])
    if next_chapter is None and chapters:
        lines.append("Review the manuscript using the snapshot, continuity notes, and chapter state above.")
    elif next_chapter is None:
        lines.append("Help start this project by proposing the first chapter from the snapshot above.")
    else:
        lines.append(
            f"Continue Chapter {next_chapter.number}: {next_chapter.title}. "
            "Preserve the synopsis, continuity notes, current chapter status, and recent progress."
        )
    return lines


def pitch_lines(project: NovelProject) -> list[str]:
    stats = _stats_for_project(project)
    chapters = sorted(project.chapters, key=lambda item: item.number)
    next_chapter = next((chapter for chapter in chapters if chapter.status != "done"), None)
    character_notes = [note for note in sorted(project.notes, key=lambda item: item.id) if note.kind == "character"]
    location_notes = [note for note in sorted(project.notes, key=lambda item: item.id) if note.kind == "location"]

    lines = [f"# {project.title} Pitch", ""]
    lines.extend(["## Logline", ""])
    if project.synopsis.strip():
        lines.append(project.synopsis.strip())
    else:
        lines.append("Add a one-paragraph synopsis before sharing this pitch.")

    lines.extend(["", "## Positioning", ""])
    if project.genre.strip():
        lines.append(f"- Genre: {project.genre}")
    if project.audience.strip():
        lines.append(f"- Audience: {project.audience}")
    lines.append(f"- Manuscript words: {stats['words']}")
    lines.append(f"- Chapters: {stats['chapters']}")
    if stats["target_words"] is not None:
        lines.append(f"- Target progress: {stats['progress_percent']}% of {stats['target_words']} words")

    lines.extend(["", "## Story Assets", ""])
    if character_notes:
        names = ", ".join(note.title for note in character_notes[:5])
        lines.append(f"- Characters: {names}")
    else:
        lines.append("- Characters: add character notes to make the pitch more concrete.")
    if location_notes:
        names = ", ".join(note.title for note in location_notes[:5])
        lines.append(f"- Locations: {names}")
    else:
        lines.append("- Locations: add location notes when setting is part of the hook.")

    lines.extend(["", "## Current Hook", ""])
    if next_chapter is None:
        if chapters:
            lines.append("- Draft chapters are marked done; use the review report to prepare the next pitch pass.")
        else:
            lines.append("- Add the first chapter to show the opening situation.")
    else:
        lines.append(f"- Next chapter: {next_chapter.number}. {next_chapter.title} [{next_chapter.status}]")
        if next_chapter.summary:
            lines.append(f"  - {next_chapter.summary}")

    lines.extend(["", "## Share Copy", ""])
    if project.synopsis.strip():
        lines.append(_project_share_copy(project))
    else:
        lines.append(f"{project.title} is ready for a sharper public pitch once synopsis, genre, and audience are set.")
    return lines


def share_announcement_lines(project: NovelProject, base_url: str = "") -> list[str]:
    lines = [f"# {project.title} Share Kit", ""]
    lines.extend(["## Short Post", ""])
    if project.synopsis.strip():
        lines.append(_project_share_copy(project))
    else:
        lines.append(f"{project.title} is a work-in-progress novel project ready for a clearer synopsis.")
    lines.extend(
        [
            "",
            "Built with Novel Workbench, a local-first writing workspace that exports Markdown, project context, and a static HTML preview.",
            "",
            "## Share Assets",
            "",
            f"- Pitch brief: `{project.slug}-pitch.md`",
            "- Static preview: `site/index.html`",
            "- Report pack: `pack/`",
        ]
    )
    if base_url:
        lines.append(f"- Public preview: {base_url}")
    lines.extend(["", "## Suggested Follow-Up", ""])
    lines.append("- Ask readers whether the premise, genre, audience, and current hook are clear.")
    lines.append("- Regenerate this kit after major synopsis, chapter, or pitch changes.")
    return lines


def launch_copy_lines(project: NovelProject, base_url: str = "") -> list[str]:
    stats = _stats_for_project(project)
    share_copy = _project_share_copy(project) if project.synopsis.strip() else f"{project.title} is a local-first novel project."
    preview_url = base_url or "Add a public preview URL after exporting with --base-url."
    repo_url = "https://github.com/xinjian0101/novel-workbench"
    lines = [f"# {project.title} Launch Copy", ""]
    lines.extend(
        [
            "## One-Line Pitch",
            "",
            share_copy,
            "",
            "## Short Social Post",
            "",
            f"{share_copy}",
            "",
            f"Preview: {preview_url}",
            "Built with Novel Workbench: local JSON projects, Markdown exports, AI/editor context, and static HTML previews.",
            "",
            "## Community Post",
            "",
            f"I am sharing {project.title}, a {project.genre or 'novel'} project managed with Novel Workbench.",
            "",
            project.synopsis.strip() or "The project is ready for a sharper public synopsis.",
            "",
            f"Current shape: {_count_label(stats['chapters'], 'chapter')}, {_count_label(stats['words'], 'word')}.",
            f"Preview: {preview_url}",
            f"Tool: {repo_url}",
            "",
            "I would especially value feedback on whether the premise, audience, genre, and current hook are clear.",
            "",
            "## Awesome List Entry",
            "",
            f"- [{project.title}]({preview_url}) - {share_copy}",
            "",
            "## Follow-Up Reply",
            "",
            "Thanks for taking a look. The project data stays local; the shared files are exported Markdown, SVG, JSON, and static HTML.",
        ]
    )
    return lines


def outreach_plan_lines(project: NovelProject, base_url: str = "") -> list[str]:
    demo_url = base_url or "https://xinjian0101.github.io/novel-workbench/"
    repo_url = "https://github.com/xinjian0101/novel-workbench"
    release_url = "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1"
    slug = project.slug
    lines = [
        f"# {project.title} Outreach Plan",
        "",
        "Use this checklist after generating a share kit. Keep each post pointed at the same repository, demo, release, and discussion links so interested readers can try the project quickly.",
        "",
        "## Core Links",
        "",
        f"- Repository: {repo_url}",
        f"- Demo: {demo_url}",
        f"- Release: {release_url}",
        f"- Tour command: `novel --workspace workspace tour --output-dir exports`",
        "",
        "## Channel Checklist",
        "",
        "| Channel | Primary asset | Link target | Success signal |",
        "|---|---|---|---|",
        f"| GitHub Discussion | `{slug}-announcement.md` | Repository | replies, stars, follow-up issues |",
        f"| Awesome list or directory | `{slug}-launch-copy.md` awesome-list entry | Repository | accepted listing or maintainer feedback |",
        f"| Developer forum | `{slug}-launch-copy.md` community post | Demo | questions about install, workflow, or examples |",
        f"| Writing community | `{slug}-pitch.md` plus `{slug}-social-card.svg` | Demo | readers asking for templates or export examples |",
        f"| Personal site or newsletter | `site/index.html` and `pack/{slug}-handoff.md` | Demo | clicks, stars, and concrete workflow replies |",
        "",
        "## Follow-Up Loop",
        "",
        "- Turn repeated install questions into README or FAQ updates.",
        "- Turn unclear workflow questions into `docs/USE_CASES.md` examples.",
        "- Turn feature requests into small issues labeled `good first issue` or `help wanted` when they fit the local-first model.",
        "- Re-run `python scripts/verify_github_metadata.py` and `python scripts/verify_public_links.py` after updating public launch surfaces.",
    ]
    return lines


def _project_share_copy(project: NovelProject) -> str:
    descriptor = f"{project.genre.strip()} project" if project.genre.strip() else "novel project"
    audience = f" for {project.audience.strip()} readers" if project.audience.strip() else ""
    return f"{project.title} is a {descriptor}{audience}: {project.synopsis.strip()}"


def momentum_lines(project: NovelProject) -> list[str]:
    stats = _stats_for_project(project)
    lines = [f"# {project.title} Momentum", ""]
    lines.extend(
        [
            "## Overview",
            "",
            f"- Manuscript words: {stats['words']}",
            f"- Logged words: {stats['logged_words']}",
            f"- Writing days: {stats['writing_days']}",
            f"- Current streak: {stats['current_streak_days']} days",
            f"- Longest streak: {stats['longest_streak_days']} days",
        ]
    )
    if stats["average_logged_words"] is not None:
        lines.append(f"- Average logged words: {stats['average_logged_words']}")
    if stats["best_day_words"] is not None:
        lines.append(f"- Best writing day: {stats['best_day_words']} words")
    if stats["target_words"] is not None:
        lines.append(f"- Target words: {stats['target_words']}")
        lines.append(f"- Remaining words: {stats['remaining_words']}")
        lines.append(f"- Progress: {stats['progress_percent']}%")
    if stats["required_daily_words"] is not None:
        lines.append(f"- Required daily words: {stats['required_daily_words']}")

    lines.extend(["", "## Weekly Totals", ""])
    if not project.progress:
        lines.append("No progress entries yet.")
        return lines

    weekly: dict[tuple[int, int], int] = {}
    for entry in project.progress:
        year, week, _ = date.fromisoformat(entry.date).isocalendar()
        key = (year, week)
        weekly[key] = weekly.get(key, 0) + entry.words

    lines.extend(["| Week | Words |", "|---|---:|"])
    for year, week in sorted(weekly, reverse=True):
        lines.append(f"| {year}-W{week:02d} | {weekly[(year, week)]} |")

    lines.extend(["", "## Recent Entries", "", "| Date | Words | Note |", "|---|---:|---|"])
    for entry in sorted(project.progress, key=lambda item: (item.date, item.id), reverse=True)[:7]:
        note = _escape_table_cell(entry.note)
        lines.append(f"| {entry.date} | {entry.words} | {note} |")
    return lines


def review_lines(project: NovelProject) -> list[str]:
    stats = _stats_for_project(project)
    lines = [f"# {project.title} Review", ""]
    lines.extend(
        [
            "## Summary",
            "",
            f"- Chapters: {stats['chapters']}",
            f"- Words: {stats['words']}",
            f"- Notes: {stats['notes']}",
            f"- Draft: {stats['draft']} chapters / {stats['draft_words']} words",
            f"- Revising: {stats['revising']} chapters / {stats['revising_words']} words",
            f"- Done: {stats['done']} chapters / {stats['done_words']} words",
        ]
    )

    findings: list[str] = []
    if not project.synopsis.strip():
        findings.append("Add a synopsis so the project has a clear premise.")
    if not project.genre.strip():
        findings.append("Set a genre to clarify reader expectations.")
    if not project.audience.strip():
        findings.append("Set an audience to clarify tone and positioning.")
    if project.target_words is None:
        findings.append("Set a target word count to measure drafting progress.")
    if not project.progress:
        findings.append("Log writing progress so streaks and pace are meaningful.")
    if not project.chapters:
        findings.append("Add at least one chapter.")

    chapters = sorted(project.chapters, key=lambda item: item.number)
    empty_chapters = [chapter for chapter in chapters if not chapter.content.strip()]
    missing_summaries = [chapter for chapter in chapters if not chapter.summary.strip()]
    unfinished_chapters = [chapter for chapter in chapters if chapter.status != "done"]
    unfinished_scenes = [
        (chapter, scene)
        for chapter in chapters
        for scene in sorted(chapter.scenes, key=lambda item: item.number)
        if scene.status != "done"
    ]
    if empty_chapters:
        labels = ", ".join(f"{chapter.number}. {chapter.title}" for chapter in empty_chapters)
        findings.append(f"Draft content for empty chapters: {labels}.")
    if missing_summaries:
        labels = ", ".join(f"{chapter.number}. {chapter.title}" for chapter in missing_summaries)
        findings.append(f"Add chapter summaries for planning clarity: {labels}.")
    if unfinished_chapters:
        labels = ", ".join(f"{chapter.number}. {chapter.title} [{chapter.status}]" for chapter in unfinished_chapters)
        findings.append(f"Move unfinished chapters forward: {labels}.")
    if unfinished_scenes:
        labels = ", ".join(f"{chapter.number}.{scene.number} {scene.title} [{scene.status}]" for chapter, scene in unfinished_scenes)
        findings.append(f"Resolve unfinished scenes: {labels}.")

    lines.extend(["", "## Findings", ""])
    if not findings:
        lines.append("No review findings.")
    else:
        for finding in findings:
            lines.append(f"- [ ] {finding}")

    lines.extend(["", "## Strengths", ""])
    strengths: list[str] = []
    if project.synopsis.strip():
        strengths.append("Synopsis is present.")
    if project.genre.strip() and project.audience.strip():
        strengths.append("Genre and audience are set.")
    if project.target_words is not None:
        strengths.append("Target word count is set.")
    if project.progress:
        strengths.append("Writing progress is being logged.")
    if project.notes:
        strengths.append("Planning notes are available.")
    if chapters and all(chapter.status == "done" for chapter in chapters):
        strengths.append("All chapters are marked done.")
    if not strengths:
        lines.append("No strengths recorded yet.")
    else:
        for strength in strengths:
            lines.append(f"- {strength}")
    return lines


def planning_lines(project: NovelProject) -> list[str]:
    stats = _stats_for_project(project)
    lines = [f"# {project.title} Plan", ""]
    lines.extend(["## Project", ""])
    lines.append(f"- Slug: `{project.slug}`")
    if project.synopsis:
        lines.append(f"- Synopsis: {project.synopsis}")
    if project.genre:
        lines.append(f"- Genre: {project.genre}")
    if project.audience:
        lines.append(f"- Audience: {project.audience}")
    if project.revision_notes:
        lines.extend(["", "## Revision Notes", "", project.revision_notes])
    lines.extend(["", "## Progress", ""])
    lines.append(f"- Manuscript words: {stats['words']}")
    lines.append(f"- Logged words: {stats['logged_words']}")
    lines.append(f"- Writing days: {stats['writing_days']}")
    lines.append(f"- Current streak: {stats['current_streak_days']} days")
    lines.append(f"- Longest streak: {stats['longest_streak_days']} days")
    if stats["target_words"] is not None:
        lines.append(f"- Target words: {stats['target_words']}")
        lines.append(f"- Remaining words: {stats['remaining_words']}")
        lines.append(f"- Progress: {stats['progress_percent']}%")
    if stats["target_date"] is not None:
        lines.append(f"- Target date: {stats['target_date']}")
        lines.append(f"- Days until target date: {stats['days_until_target_date']}")
    if stats["required_daily_words"] is not None:
        lines.append(f"- Required daily words: {stats['required_daily_words']}")
    lines.extend(["", "## Chapters", ""])
    if project.chapters:
        for chapter in sorted(project.chapters, key=lambda item: item.number):
            lines.append(f"{chapter.number}. {chapter.title} [{chapter.status}] - {count_words(chapter.content)} words")
            if chapter.summary:
                lines.append(f"   {chapter.summary}")
            for scene in sorted(chapter.scenes, key=lambda item: item.number):
                lines.append(f"   {chapter.number}.{scene.number} {scene.title} [{scene.status}]")
                if scene.summary:
                    lines.append(f"      {scene.summary}")
    else:
        lines.append("No chapters yet.")
    lines.extend(["", "## Notes", ""])
    if project.notes:
        for kind in sorted(VALID_NOTE_KINDS):
            notes = [note for note in sorted(project.notes, key=lambda item: item.id) if note.kind == kind]
            if not notes:
                continue
            lines.extend([f"### {kind.title()}", ""])
            for note in notes:
                lines.append(f"- {note.title}")
                if note.content:
                    lines.extend(_indent_lines(note.content, "  "))
            lines.append("")
        if lines[-1] == "":
            lines.pop()
    else:
        lines.append("No notes yet.")
    if project.progress:
        lines.extend(["", "## Writing Log", "", "| Date | Words | Note |", "|---|---:|---|"])
        for entry in sorted(project.progress, key=lambda item: (item.date, item.id)):
            note = entry.note.replace("|", "\\|")
            lines.append(f"| {entry.date} | {entry.words} | {note} |")
    return lines


def revision_lines(project: NovelProject) -> list[str]:
    lines = [f"# {project.title} Revision Checklist", ""]
    stats = _stats_for_project(project)
    lines.extend(
        [
            "## Snapshot",
            "",
            f"- Slug: `{project.slug}`",
            f"- Words: {stats['words']}",
            f"- Chapters: {stats['chapters']}",
            f"- Draft: {stats['draft']} chapters / {stats['draft_words']} words",
            f"- Revising: {stats['revising']} chapters / {stats['revising_words']} words",
            f"- Done: {stats['done']} chapters / {stats['done_words']} words",
        ]
    )
    if project.revision_notes:
        lines.extend(["", "## Project Revision Notes", "", project.revision_notes])

    lines.extend(["", "## Chapter Pass", ""])
    chapters = sorted(project.chapters, key=lambda item: item.number)
    if not chapters:
        lines.append("- [ ] Add chapters before starting a revision pass.")
    else:
        for chapter in chapters:
            marker = "x" if chapter.status == "done" else " "
            lines.append(
                f"- [{marker}] Chapter {chapter.number}: {chapter.title} "
                f"[{chapter.status}] - {count_words(chapter.content)} words"
            )
            if chapter.summary:
                lines.append(f"  - Summary: {chapter.summary}")

    scene_rows = [
        (chapter, scene)
        for chapter in chapters
        for scene in sorted(chapter.scenes, key=lambda item: item.number)
        if scene.status != "done"
    ]
    lines.extend(["", "## Scene Follow-Ups", ""])
    if not scene_rows:
        lines.append("No unfinished scenes.")
    else:
        for chapter, scene in scene_rows:
            lines.append(f"- [ ] {chapter.number}.{scene.number} {scene.title} [{scene.status}]")
            if scene.summary:
                lines.append(f"  - {scene.summary}")

    notes = sorted(project.notes, key=lambda item: (item.kind, item.id))
    lines.extend(["", "## Planning Notes To Review", ""])
    if not notes:
        lines.append("No planning notes yet.")
    else:
        for note in notes:
            lines.append(f"- [ ] {note.title} [{note.kind}]")
    return lines


def _frontmatter_export_lines(project: NovelProject) -> list[str]:
    lines = [
        "---",
        f'title: "{_escape_yaml(project.title)}"',
        f'slug: "{_escape_yaml(project.slug)}"',
    ]
    if project.synopsis:
        lines.append(f'synopsis: "{_escape_yaml(project.synopsis)}"')
    if project.genre:
        lines.append(f'genre: "{_escape_yaml(project.genre)}"')
    if project.audience:
        lines.append(f'audience: "{_escape_yaml(project.audience)}"')
    if project.revision_notes:
        lines.append(f'revision_notes: "{_escape_yaml(project.revision_notes)}"')
    if project.target_words is not None:
        lines.append(f"target_words: {project.target_words}")
    if project.target_date is not None:
        lines.append(f'target_date: "{_escape_yaml(project.target_date)}"')
    lines.extend(["---", ""])
    lines.extend(_default_export_lines(project))
    return lines


def _progress_export_lines(project: NovelProject) -> list[str]:
    stats = _stats_for_project(project)
    lines = [f"# {project.title} Progress", ""]
    if project.synopsis:
        lines.extend([project.synopsis, ""])
    lines.extend(
        [
            "## Overview",
            "",
            f"- Slug: `{project.slug}`",
            f"- Chapters: {stats['chapters']}",
            f"- Notes: {stats['notes']}",
            f"- Words: {stats['words']}",
            f"- Characters: {stats['characters']}",
            f"- Logged writing days: {stats['writing_days']}",
            f"- Logged words: {stats['logged_words']}",
            f"- Current streak: {stats['current_streak_days']} days",
            f"- Longest streak: {stats['longest_streak_days']} days",
        ]
    )
    if stats["average_logged_words"] is not None:
        lines.append(f"- Average logged words: {stats['average_logged_words']}")
    if stats["best_day_words"] is not None:
        lines.append(f"- Best writing day: {stats['best_day_words']} words")
    if project.genre:
        lines.append(f"- Genre: {project.genre}")
    if project.audience:
        lines.append(f"- Audience: {project.audience}")
    if stats["target_words"] is not None:
        lines.extend(
            [
                f"- Target words: {stats['target_words']}",
                f"- Remaining words: {stats['remaining_words']}",
                f"- Progress: {stats['progress_percent']}%",
            ]
        )
    if stats["target_date"] is not None:
        lines.append(f"- Target date: {stats['target_date']}")
        lines.append(f"- Days until target date: {stats['days_until_target_date']}")
    if stats["required_daily_words"] is not None:
        lines.append(f"- Required daily words: {stats['required_daily_words']}")
    if stats["average_chapter_words"] is not None:
        lines.append(f"- Average chapter words: {stats['average_chapter_words']}")
    if project.revision_notes:
        lines.extend(["", "## Revision Notes", "", project.revision_notes])
    lines.extend(
        [
            "",
            "## Status",
            "",
            f"- Draft: {stats['draft']} chapters / {stats['draft_words']} words",
            f"- Revising: {stats['revising']} chapters / {stats['revising_words']} words",
            f"- Done: {stats['done']} chapters / {stats['done_words']} words",
            "",
            "## Chapters",
            "",
            "| # | Title | Status | Words |",
            "|---:|---|---|---:|",
        ]
    )
    for chapter in sorted(project.chapters, key=lambda item: item.number):
        title = chapter.title.replace("|", "\\|")
        lines.append(f"| {chapter.number} | {title} | {chapter.status} | {count_words(chapter.content)} |")
    if project.progress:
        lines.extend(
            [
                "",
                "## Progress Log",
                "",
                "| Date | Words | Note |",
                "|---|---:|---|",
            ]
        )
        for entry in sorted(project.progress, key=lambda item: (item.date, item.id)):
            note = entry.note.replace("|", "\\|")
            lines.append(f"| {entry.date} | {entry.words} | {note} |")
    return lines


def _custom_export_lines(project: NovelProject, template: str) -> list[str]:
    stats = _stats_for_project(project)
    values = {
        "title": project.title,
        "slug": project.slug,
        "synopsis": project.synopsis,
        "genre": project.genre,
        "audience": project.audience,
        "revision_notes": project.revision_notes,
        "target_words": "" if project.target_words is None else str(project.target_words),
        "target_date": "" if project.target_date is None else project.target_date,
        "words": str(stats["words"]),
        "logged_words": str(stats["logged_words"]),
        "writing_days": str(stats["writing_days"]),
        "current_streak_days": str(stats["current_streak_days"]),
        "longest_streak_days": str(stats["longest_streak_days"]),
        "remaining_words": "" if stats["remaining_words"] is None else str(stats["remaining_words"]),
        "progress_percent": "" if stats["progress_percent"] is None else str(stats["progress_percent"]),
        "days_until_target_date": "" if stats["days_until_target_date"] is None else str(stats["days_until_target_date"]),
        "required_daily_words": "" if stats["required_daily_words"] is None else str(stats["required_daily_words"]),
        "average_chapter_words": "" if stats["average_chapter_words"] is None else str(stats["average_chapter_words"]),
        "average_logged_words": "" if stats["average_logged_words"] is None else str(stats["average_logged_words"]),
        "best_day_words": "" if stats["best_day_words"] is None else str(stats["best_day_words"]),
        "chapters_markdown": "\n".join(_default_export_lines(project)).strip(),
        "focus_brief": "\n".join(focus_lines(project)),
        "handoff_brief": "\n".join(handoff_lines(project)),
        "momentum_report": "\n".join(momentum_lines(project)),
        "status_board": "\n".join(board_lines(project)),
        "chapter_table": "\n".join(_chapter_table_lines(project)),
        "status_summary": "\n".join(
            [
                f"- Draft: {stats['draft']} chapters / {stats['draft_words']} words",
                f"- Revising: {stats['revising']} chapters / {stats['revising_words']} words",
                f"- Done: {stats['done']} chapters / {stats['done_words']} words",
            ]
        ),
        "progress_log": "\n".join(_progress_log_lines(project)),
        "pitch_brief": "\n".join(pitch_lines(project)),
        "review_report": "\n".join(review_lines(project)),
        "revision_checklist": "\n".join(revision_lines(project)),
    }
    try:
        rendered = template.format(**values)
    except KeyError as exc:
        allowed = ", ".join(sorted(values))
        raise StorageError(f"Unknown export template field '{exc.args[0]}'. Allowed fields: {allowed}.") from exc
    except ValueError as exc:
        raise StorageError(f"Export template is invalid: {exc}") from exc
    return rendered.splitlines()


def _chapter_table_lines(project: NovelProject) -> list[str]:
    lines = ["| # | Title | Status | Words |", "|---:|---|---|---:|"]
    for chapter in sorted(project.chapters, key=lambda item: item.number):
        title = chapter.title.replace("|", "\\|")
        lines.append(f"| {chapter.number} | {title} | {chapter.status} | {count_words(chapter.content)} |")
    return lines


def _note_preview(content: str) -> str:
    for line in content.splitlines():
        normalized = line.strip()
        if normalized and not normalized.startswith("#"):
            return normalized
    return content.strip().splitlines()[0].strip()


def _progress_log_lines(project: NovelProject) -> list[str]:
    lines = ["| Date | Words | Note |", "|---|---:|---|"]
    for entry in sorted(project.progress, key=lambda item: (item.date, item.id)):
        note = entry.note.replace("|", "\\|")
        lines.append(f"| {entry.date} | {entry.words} | {note} |")
    return lines


def _indent_lines(content: str, prefix: str) -> list[str]:
    return [f"{prefix}{line}" if line else "" for line in content.splitlines()]


def _stats_for_project(project: NovelProject) -> dict[str, int | None]:
    words = sum(count_words(chapter.content) for chapter in project.chapters)
    progress_percent = None
    remaining_words = None
    days_until_target_date = None
    required_daily_words = None
    if project.target_words is not None:
        progress_percent = min(round((words / project.target_words) * 100), 999)
        remaining_words = max(project.target_words - words, 0)
    if project.target_date is not None:
        days_until_target_date = max((date.fromisoformat(project.target_date) - date.today()).days, 0)
    if remaining_words is not None and days_until_target_date is not None:
        divisor = max(days_until_target_date, 1)
        required_daily_words = math.ceil(remaining_words / divisor)
    words_by_status = {
        status: sum(count_words(chapter.content) for chapter in project.chapters if chapter.status == status)
        for status in VALID_STATUSES
    }
    logged_words = sum(entry.words for entry in project.progress)
    progress_dates = {entry.date for entry in project.progress}
    writing_days = len(progress_dates)
    current_streak_days, longest_streak_days = _progress_streaks(progress_dates)
    average_chapter_words = None if not project.chapters else round(words / len(project.chapters))
    average_logged_words = None if writing_days == 0 else round(logged_words / writing_days)
    best_day_words = None
    if project.progress:
        words_by_date: dict[str, int] = {}
        for entry in project.progress:
            words_by_date[entry.date] = words_by_date.get(entry.date, 0) + entry.words
        best_day_words = max(words_by_date.values())
    return {
        "chapters": len(project.chapters),
        "notes": len(project.notes),
        "words": words,
        "logged_words": logged_words,
        "writing_days": writing_days,
        "current_streak_days": current_streak_days,
        "longest_streak_days": longest_streak_days,
        "average_logged_words": average_logged_words,
        "best_day_words": best_day_words,
        "target_words": project.target_words,
        "target_date": project.target_date,
        "remaining_words": remaining_words,
        "progress_percent": progress_percent,
        "days_until_target_date": days_until_target_date,
        "required_daily_words": required_daily_words,
        "average_chapter_words": average_chapter_words,
        "characters": sum(len(chapter.content) for chapter in project.chapters),
        "draft": sum(1 for chapter in project.chapters if chapter.status == "draft"),
        "revising": sum(1 for chapter in project.chapters if chapter.status == "revising"),
        "done": sum(1 for chapter in project.chapters if chapter.status == "done"),
        "draft_words": words_by_status["draft"],
        "revising_words": words_by_status["revising"],
        "done_words": words_by_status["done"],
    }


def _context_for_project(project: NovelProject) -> dict[str, object]:
    chapters = sorted(project.chapters, key=lambda item: item.number)
    next_chapter = next((chapter for chapter in chapters if chapter.status != "done"), None)
    recent_progress = sorted(project.progress, key=lambda item: (item.date, item.id), reverse=True)[:5]
    continuity_notes = sorted(project.notes, key=lambda item: item.id)[:8]
    return {
        "format": "novel-workbench-project-context",
        "format_version": 1,
        "project": project.to_dict(),
        "stats": _stats_for_project(project),
        "next_action": _context_next_action(project, next_chapter),
        "chapter_state": [_context_chapter(chapter) for chapter in chapters],
        "recent_progress": [entry.to_dict() for entry in recent_progress],
        "continuity_notes": [_context_note(note) for note in continuity_notes],
    }


def _context_next_action(project: NovelProject, chapter: Chapter | None) -> dict[str, object]:
    if chapter is None:
        if project.chapters:
            return {
                "kind": "review_manuscript",
                "prompt": "Review the manuscript using the project snapshot, continuity notes, and chapter state.",
            }
        return {
            "kind": "start_project",
            "prompt": "Propose the first chapter from the project snapshot.",
        }

    open_scenes = [scene for scene in sorted(chapter.scenes, key=lambda item: item.number) if scene.status != "done"]
    return {
        "kind": "continue_chapter",
        "chapter_number": chapter.number,
        "chapter_title": chapter.title,
        "chapter_status": chapter.status,
        "chapter_words": count_words(chapter.content),
        "chapter_summary": chapter.summary,
        "open_scenes": [scene.to_dict() for scene in open_scenes],
        "prompt": (
            f"Continue Chapter {chapter.number}: {chapter.title}. "
            "Preserve the synopsis, continuity notes, current chapter status, and recent progress."
        ),
    }


def _context_chapter(chapter: Chapter) -> dict[str, object]:
    return {
        "number": chapter.number,
        "title": chapter.title,
        "status": chapter.status,
        "words": count_words(chapter.content),
        "summary": chapter.summary,
        "scenes": [
            {
                **scene.to_dict(),
                "label": f"{chapter.number}.{scene.number}",
            }
            for scene in sorted(chapter.scenes, key=lambda item: item.number)
        ],
    }


def _context_note(note: ProjectNote) -> dict[str, object]:
    data = note.to_dict()
    data["preview"] = _note_preview(note.content) if note.content.strip() else ""
    return data


def _progress_streaks(progress_dates: set[str]) -> tuple[int, int]:
    if not progress_dates:
        return 0, 0
    dates = sorted(date.fromisoformat(value) for value in progress_dates)
    longest = 1
    current_run = 1
    for previous, current in zip(dates, dates[1:]):
        if (current - previous).days == 1:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    today = date.today()
    streak_anchor = today if today in dates else today - timedelta(days=1)
    if streak_anchor not in dates:
        return 0, longest

    active_streak = 0
    cursor = streak_anchor
    date_set = set(dates)
    while cursor in date_set:
        active_streak += 1
        cursor = cursor - timedelta(days=1)
    return active_streak, longest


def _escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _escape_table_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _backup_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _read_utf8_text(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise StorageError(f"{label} is not valid UTF-8: {path}") from exc
    except OSError as exc:
        raise StorageError(f"Could not read {label.lower()}: {path} ({exc.strerror or exc})") from exc


def _snippet(content: str, query: str, radius: int = 40) -> str:
    normalized_content = content.lower()
    index = normalized_content.find(query)
    if index == -1:
        return content[: radius * 2].strip()
    start = max(index - radius, 0)
    end = min(index + len(query) + radius, len(content))
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(content) else ""
    return f"{prefix}{content[start:end].strip()}{suffix}"


def _first_matching_text(query: str, *values: str) -> str:
    for value in values:
        if query in value.lower():
            return value
    return next((value for value in values if value), "")


def _find_chapter(project: NovelProject, number: int) -> Chapter:
    if number < 1:
        raise StorageError("Chapter number must be greater than zero.")
    chapter = next((item for item in project.chapters if item.number == number), None)
    if chapter is None:
        raise NotFoundError(f"Chapter {number} does not exist in project '{project.slug}'.")
    return chapter


def _find_scene(chapter: Chapter, number: int, slug: str) -> Scene:
    if number < 1:
        raise StorageError("Scene number must be greater than zero.")
    scene = next((item for item in chapter.scenes if item.number == number), None)
    if scene is None:
        raise NotFoundError(f"Scene {number} does not exist in chapter {chapter.number} of project '{slug}'.")
    return scene


def _validate_chapter_numbers(project: NovelProject) -> None:
    numbers = [chapter.number for chapter in project.chapters]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        raise StorageError(f"Project '{project.slug}' has non-sequential chapter numbers.")


def _validate_scene_numbers(project: NovelProject) -> None:
    for chapter in project.chapters:
        numbers = [scene.number for scene in chapter.scenes]
        expected = list(range(1, len(numbers) + 1))
        if numbers != expected:
            raise StorageError(f"Chapter {chapter.number} in project '{project.slug}' has non-sequential scene numbers.")


def _validate_project_fields(project: NovelProject) -> None:
    if project.schema_version < 0 or project.schema_version > CURRENT_SCHEMA_VERSION:
        raise StorageError(f"Schema version must be between 0 and {CURRENT_SCHEMA_VERSION}.")
    validate_slug(project.slug)
    validate_title(project.title)
    validate_optional_metadata(project.genre, "Genre")
    validate_optional_metadata(project.audience, "Audience")
    if project.target_words is not None:
        validate_target_words(project.target_words)
    if project.target_date is not None:
        validate_target_date(project.target_date)
    note_ids: set[int] = set()
    progress_ids: set[int] = set()
    for chapter in project.chapters:
        if chapter.number < 1:
            raise StorageError("Chapter number must be greater than zero.")
        validate_title(chapter.title)
        validate_status(chapter.status)
        for scene in chapter.scenes:
            if scene.number < 1:
                raise StorageError("Scene number must be greater than zero.")
            validate_title(scene.title)
            validate_status(scene.status)
    for note in project.notes:
        if note.id < 1:
            raise StorageError("Note id must be greater than zero.")
        if note.id in note_ids:
            raise StorageError(f"Note id {note.id} is duplicated.")
        note_ids.add(note.id)
        validate_title(note.title)
        validate_note_kind(note.kind)
    for entry in project.progress:
        if entry.id < 1:
            raise StorageError("Progress id must be greater than zero.")
        if entry.id in progress_ids:
            raise StorageError(f"Progress id {entry.id} is duplicated.")
        progress_ids.add(entry.id)
        validate_progress_date(entry.date)
        validate_progress_words(entry.words)


def _doctor_hint(error: str) -> str:
    if "JSON syntax error" in error:
        return "Fix the JSON syntax at the reported line and column, or restore the file from a backup."
    if "not valid UTF-8" in error:
        return "Save the file as UTF-8 JSON, or restore it from a backup."
    if "missing required field" in error:
        return "Add the missing required field shown in the error, or restore the file from a backup."
    if "invalid field value" in error:
        return "Fix the invalid value shown in the error so it matches the project schema."
    if "Schema version" in error:
        return "Use a Novel Workbench version that supports this project file, or restore it from a compatible backup."
    if "Project file is invalid" in error:
        return "Restore the file from a backup or fix the JSON syntax before running other commands."
    if "non-sequential chapter numbers" in error:
        return "Renumber chapters so they start at 1 and increase by 1 without gaps or duplicates."
    if "non-sequential scene numbers" in error:
        return "Renumber scenes so they start at 1 within each chapter and increase by 1 without gaps or duplicates."
    return "Inspect the project file, fix the reported data, then rerun `novel doctor`."


def _normalized_project_json(project: NovelProject) -> str:
    project.schema_version = CURRENT_SCHEMA_VERSION
    payload = json.dumps(project.to_dict(), ensure_ascii=False, indent=2)
    return payload + "\n"
