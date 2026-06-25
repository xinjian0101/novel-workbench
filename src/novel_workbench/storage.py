from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from .models import Chapter, NovelProject, utc_now_iso

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHAPTER_HEADING_PATTERN = re.compile(r"^##\s+(?:Chapter\s+\d+:\s*)?(?P<title>.+?)\s*$", re.IGNORECASE)
VALID_STATUSES = {"draft", "revising", "done"}


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

    def initialize(self) -> None:
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def project_path(self, slug: str) -> Path:
        return self.projects_dir / f"{validate_slug(slug)}.json"

    def list_projects(self) -> list[NovelProject]:
        self.initialize()
        projects = [self._read_project(path) for path in sorted(self.projects_dir.glob("*.json"))]
        return sorted(projects, key=lambda project: project.updated_at, reverse=True)

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
                        }
                    )
                _validate_chapter_numbers(project)
            except StorageError as exc:
                errors.append({"file": str(path), "error": str(exc)})
        return {"checked": checked, "ok": checked - len(errors), "errors": errors}

    def create_project(self, slug: str, title: str, synopsis: str = "") -> NovelProject:
        self.initialize()
        project = NovelProject(slug=validate_slug(slug), title=validate_title(title), synopsis=synopsis.strip())
        path = self.project_path(project.slug)
        if path.exists():
            raise DuplicateError(f"Project '{project.slug}' already exists.")
        self._write_project(project)
        return project

    def import_markdown(self, slug: str, markdown_path: Path) -> NovelProject:
        if not markdown_path.exists():
            raise NotFoundError(f"Markdown file does not exist: {markdown_path}")
        title, synopsis, chapters = parse_markdown_chapters(markdown_path.read_text(encoding="utf-8"))
        project = self.create_project(slug, title, synopsis)
        for chapter_title, content in chapters:
            self.add_chapter(project.slug, chapter_title, content)
        return self.get_project(project.slug)

    def get_project(self, slug: str) -> NovelProject:
        path = self.project_path(slug)
        if not path.exists():
            raise NotFoundError(f"Project '{validate_slug(slug)}' does not exist.")
        return self._read_project(path)

    def add_chapter(self, slug: str, title: str, content: str = "", status: str = "draft") -> Chapter:
        project = self.get_project(slug)
        next_number = max((chapter.number for chapter in project.chapters), default=0) + 1
        chapter = Chapter(
            number=next_number,
            title=validate_title(title),
            content=content,
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
        if status is not None:
            chapter.status = validate_status(status)
        chapter.updated_at = utc_now_iso()
        project.updated_at = chapter.updated_at
        self._write_project(project)
        return chapter

    def project_stats(self, slug: str) -> dict[str, int]:
        project = self.get_project(slug)
        return {
            "chapters": len(project.chapters),
            "words": sum(count_words(chapter.content) for chapter in project.chapters),
            "characters": sum(len(chapter.content) for chapter in project.chapters),
            "draft": sum(1 for chapter in project.chapters if chapter.status == "draft"),
            "revising": sum(1 for chapter in project.chapters if chapter.status == "revising"),
            "done": sum(1 for chapter in project.chapters if chapter.status == "done"),
        }

    def search(self, slug: str, query: str) -> list[dict[str, str | int]]:
        normalized_query = query.strip().lower()
        if not normalized_query:
            raise StorageError("Search query is required.")
        project = self.get_project(slug)
        results: list[dict[str, str | int]] = []
        for chapter in project.chapters:
            haystack = f"{chapter.title}\n{chapter.content}".lower()
            if normalized_query not in haystack:
                continue
            results.append(
                {
                    "number": chapter.number,
                    "title": chapter.title,
                    "status": chapter.status,
                    "snippet": _snippet(chapter.content or chapter.title, normalized_query),
                }
            )
        return results

    def backup_project(self, slug: str, output_dir: Path) -> Path:
        project = self.get_project(slug)
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = utc_now_iso().replace(":", "").replace("+", "Z")
        output_path = output_dir / f"{project.slug}-{timestamp}.json"
        shutil.copy2(self.project_path(project.slug), output_path)
        return output_path

    def export_markdown(self, slug: str, output_path: Path) -> Path:
        project = self.get_project(slug)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# {project.title}", ""]
        if project.synopsis:
            lines.extend([project.synopsis, ""])
        for chapter in sorted(project.chapters, key=lambda item: item.number):
            lines.extend([f"## Chapter {chapter.number}: {chapter.title}", "", chapter.content.strip(), ""])
        output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return output_path

    def _read_project(self, path: Path) -> NovelProject:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return NovelProject.from_dict(data)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise StorageError(f"Project file is invalid: {path}") from exc

    def _write_project(self, project: NovelProject) -> None:
        path = self.project_path(project.slug)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(project.to_dict(), ensure_ascii=False, indent=2)
        path.write_text(payload + "\n", encoding="utf-8")


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


def _validate_chapter_numbers(project: NovelProject) -> None:
    numbers = [chapter.number for chapter in project.chapters]
    expected = list(range(1, len(numbers) + 1))
    if numbers != expected:
        raise StorageError(f"Project '{project.slug}' has non-sequential chapter numbers.")
