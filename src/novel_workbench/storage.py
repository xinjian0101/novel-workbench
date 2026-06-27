from __future__ import annotations

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
    "momentum",
    "outline",
    "progress",
    "review",
    "revision",
}
EXPORT_PACK_TEMPLATES = (
    ("manuscript", "default", "{slug}.md"),
    ("frontmatter", "frontmatter", "{slug}-frontmatter.md"),
    ("focus", "focus", "{slug}-focus.md"),
    ("momentum", "momentum", "{slug}-momentum.md"),
    ("board", "board", "{slug}-board.md"),
    ("outline", "outline", "{slug}-outline.md"),
    ("progress", "progress", "{slug}-progress.md"),
    ("review", "review", "{slug}-review.md"),
    ("revision", "revision", "{slug}-revision.md"),
)
SAMPLE_PROJECT = {
    "slug": "moon-archive",
    "title": "Moon Archive",
    "synopsis": "A historian finds a city under the lunar dust.",
    "chapters": [
        ("Signal", "The first signal arrived at 03:17."),
        ("Descent", "They opened the hatch and heard rain below."),
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
        for chapter_title, content in SAMPLE_PROJECT["chapters"]:
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
            elif template == "momentum":
                lines = momentum_lines(project)
            elif template == "outline":
                lines = outline_lines(project)
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
