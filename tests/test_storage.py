from pathlib import Path

import pytest

from novel_workbench.storage import (
    DuplicateError,
    NotFoundError,
    ProjectStore,
    StorageError,
    parse_markdown_chapters,
)


def test_create_project_and_add_chapter(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    project = store.create_project("first-novel", "First Novel", "A concise premise.")

    chapter = store.add_chapter(project.slug, "Opening", "The story begins.", "draft")
    loaded = store.get_project(project.slug)

    assert loaded.title == "First Novel"
    assert loaded.synopsis == "A concise premise."
    assert chapter.number == 1
    assert loaded.chapters[0].content == "The story begins."


def test_rejects_duplicate_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    with pytest.raises(DuplicateError):
        store.create_project("first-novel", "Another Title")


def test_create_sample_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)

    project = store.create_sample_project()

    assert project.slug == "moon-archive"
    assert project.title == "Moon Archive"
    assert len(project.chapters) == 2
    assert project.chapters[0].title == "Signal"


def test_create_sample_project_rejects_duplicate_slug(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_sample_project()

    with pytest.raises(DuplicateError):
        store.create_sample_project()


def test_validates_slug_title_and_status(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)

    with pytest.raises(StorageError):
        store.create_project("Bad Slug", "Title")

    with pytest.raises(StorageError):
        store.create_project("valid-slug", "")

    store.create_project("valid-slug", "Title")
    with pytest.raises(StorageError):
        store.add_chapter("valid-slug", "Chapter", status="unknown")


def test_update_chapter_from_existing_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening")

    updated = store.update_chapter("first-novel", 1, content="Revised.", status="done")

    assert updated.content == "Revised."
    assert updated.status == "done"


def test_move_chapter_reorders_and_renumbers(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "One")
    store.add_chapter("first-novel", "Middle", "Two")
    store.add_chapter("first-novel", "Ending", "Three")

    moved = store.move_chapter("first-novel", 3, 1)
    project = store.get_project("first-novel")

    assert moved.title == "Ending"
    assert [(chapter.number, chapter.title) for chapter in project.chapters] == [
        (1, "Ending"),
        (2, "Opening"),
        (3, "Middle"),
    ]
    assert store.check_workspace() == {"checked": 1, "ok": 1, "errors": []}


def test_move_chapter_validates_target_number(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening")

    with pytest.raises(StorageError):
        store.move_chapter("first-novel", 1, 0)
    with pytest.raises(StorageError):
        store.move_chapter("first-novel", 1, 2)


def test_delete_chapter_removes_and_renumbers(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "One")
    store.add_chapter("first-novel", "Middle", "Two")
    store.add_chapter("first-novel", "Ending", "Three")

    deleted = store.delete_chapter("first-novel", 2)
    project = store.get_project("first-novel")

    assert deleted.title == "Middle"
    assert [(chapter.number, chapter.title) for chapter in project.chapters] == [
        (1, "Opening"),
        (2, "Ending"),
    ]
    assert store.check_workspace() == {"checked": 1, "ok": 1, "errors": []}


def test_delete_chapter_validates_number(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    with pytest.raises(StorageError):
        store.delete_chapter("first-novel", 0)
    with pytest.raises(NotFoundError):
        store.delete_chapter("first-novel", 1)


def test_missing_project_and_chapter_raise_clear_errors(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)

    with pytest.raises(NotFoundError):
        store.get_project("missing")

    store.create_project("first-novel", "First Novel")
    with pytest.raises(NotFoundError):
        store.update_chapter("first-novel", 99, content="No chapter.")


def test_rename_project_updates_slug_title_and_file(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel")
    store.set_target_words("first-novel", 50000)
    store.add_chapter("first-novel", "Opening", "The story begins.")

    project = store.rename_project("first-novel", "second-novel", "Second Novel")

    assert project.slug == "second-novel"
    assert project.title == "Second Novel"
    assert project.target_words == 50000
    assert project.chapters[0].title == "Opening"
    assert not (tmp_path / "workspace" / "projects" / "first-novel.json").exists()
    assert (tmp_path / "workspace" / "projects" / "second-novel.json").exists()
    with pytest.raises(NotFoundError):
        store.get_project("first-novel")


def test_rename_project_rejects_existing_slug(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel")
    store.create_project("second-novel", "Second Novel")

    with pytest.raises(DuplicateError):
        store.rename_project("first-novel", "second-novel")

    assert store.get_project("first-novel").title == "First Novel"
    assert store.get_project("second-novel").title == "Second Novel"


def test_export_markdown(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.add_chapter("first-novel", "Opening", "The story begins.")
    output = tmp_path / "exports" / "first-novel.md"

    store.export_markdown("first-novel", output)

    assert output.read_text(encoding="utf-8") == (
        "# First Novel\n\n"
        "A concise premise.\n\n"
        "## Chapter 1: Opening\n\n"
        "The story begins.\n"
    )


def test_export_markdown_frontmatter_template(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.set_target_words("first-novel", 50000)
    store.add_chapter("first-novel", "Opening", "The story begins.")
    output = tmp_path / "exports" / "first-novel.md"

    store.export_markdown("first-novel", output, template="frontmatter")

    assert output.read_text(encoding="utf-8") == (
        "---\n"
        'title: "First Novel"\n'
        'slug: "first-novel"\n'
        'synopsis: "A concise premise."\n'
        "target_words: 50000\n"
        "---\n\n"
        "# First Novel\n\n"
        "A concise premise.\n\n"
        "## Chapter 1: Opening\n\n"
        "The story begins.\n"
    )


def test_export_markdown_progress_template(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.set_target_words("first-novel", 10)
    store.add_chapter("first-novel", "Opening", "The story begins.", "done")
    store.add_chapter("first-novel", "Middle", "A second scene unfolds.", "revising")
    output = tmp_path / "reports" / "first-novel-progress.md"

    store.export_markdown("first-novel", output, template="progress")

    assert output.read_text(encoding="utf-8") == (
        "# First Novel Progress\n\n"
        "A concise premise.\n\n"
        "## Overview\n\n"
        "- Slug: `first-novel`\n"
        "- Chapters: 2\n"
        "- Words: 7\n"
        "- Characters: 40\n"
        "- Target words: 10\n"
        "- Progress: 70%\n\n"
        "## Status\n\n"
        "- Draft: 0\n"
        "- Revising: 1\n"
        "- Done: 1\n\n"
        "## Chapters\n\n"
        "| # | Title | Status | Words |\n"
        "|---:|---|---|---:|\n"
        "| 1 | Opening | done | 3 |\n"
        "| 2 | Middle | revising | 4 |\n"
    )


def test_export_markdown_rejects_unknown_template(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel")

    with pytest.raises(StorageError):
        store.export_markdown("first-novel", tmp_path / "book.md", template="unknown")


def test_project_stats_count_progress(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The story begins.", "done")
    store.add_chapter("first-novel", "Middle", "A second scene unfolds.", "revising")

    assert store.project_stats("first-novel") == {
        "chapters": 2,
        "words": 7,
        "target_words": None,
        "progress_percent": None,
        "characters": 40,
        "draft": 0,
        "revising": 1,
        "done": 1,
    }


def test_project_stats_show_target_progress(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The story begins.", "draft")
    store.set_target_words("first-novel", 10)

    stats = store.project_stats("first-novel")

    assert stats["words"] == 3
    assert stats["target_words"] == 10
    assert stats["progress_percent"] == 30


def test_set_target_words_validates_positive_values(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    with pytest.raises(StorageError):
        store.set_target_words("first-novel", 0)


def test_clear_target_words(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.set_target_words("first-novel", 10)

    project = store.set_target_words("first-novel", None)

    assert project.target_words is None
    assert store.project_stats("first-novel")["progress_percent"] is None


def test_existing_project_json_without_target_words_still_loads(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "legacy.json").write_text(
        '{\n'
        '  "slug": "legacy",\n'
        '  "title": "Legacy",\n'
        '  "synopsis": "",\n'
        '  "chapters": [],\n'
        '  "created_at": "2026-06-25T00:00:00+00:00",\n'
        '  "updated_at": "2026-06-25T00:00:00+00:00"\n'
        '}\n',
        encoding="utf-8",
    )
    store = ProjectStore(tmp_path)

    project = store.get_project("legacy")

    assert project.target_words is None


def test_parse_markdown_chapters() -> None:
    title, synopsis, chapters = parse_markdown_chapters(
        "# Moon Archive\n\n"
        "A historian finds a city under the lunar dust.\n\n"
        "## Chapter 1: Signal\n\n"
        "The first signal arrived.\n\n"
        "## Chapter 2: Descent\n\n"
        "They opened the hatch.\n"
    )

    assert title == "Moon Archive"
    assert synopsis == "A historian finds a city under the lunar dust."
    assert chapters == [
        ("Signal", "The first signal arrived."),
        ("Descent", "They opened the hatch."),
    ]


def test_parse_markdown_chapters_accepts_utf8_bom() -> None:
    title, _, chapters = parse_markdown_chapters(
        "\ufeff# Moon Archive\n\n"
        "## Chapter 1: Signal\n\n"
        "The first signal arrived.\n"
    )

    assert title == "Moon Archive"
    assert chapters == [("Signal", "The first signal arrived.")]


def test_import_markdown_creates_project(tmp_path: Path) -> None:
    markdown_path = tmp_path / "source.md"
    markdown_path.write_text(
        "# Moon Archive\n\n"
        "A historian finds a city under the lunar dust.\n\n"
        "## Chapter 1: Signal\n\n"
        "The first signal arrived.\n",
        encoding="utf-8",
    )
    store = ProjectStore(tmp_path / "workspace")

    project = store.import_markdown("moon-archive", markdown_path)

    assert project.title == "Moon Archive"
    assert project.synopsis == "A historian finds a city under the lunar dust."
    assert project.chapters[0].title == "Signal"
    assert project.chapters[0].content == "The first signal arrived."


def test_starter_markdown_can_be_imported(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    starter = tmp_path / "starter.md"

    store.write_starter_markdown(starter)
    project = store.import_markdown("working-title", starter)

    assert project.title == "Working Title"
    assert len(project.chapters) == 3
    assert project.chapters[0].title == "Opening Image"


def test_starter_markdown_supports_named_templates(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    starter = tmp_path / "mystery.md"

    store.write_starter_markdown(starter, template="mystery")
    project = store.import_markdown("mystery-draft", starter)

    assert project.title == "Working Title"
    assert [chapter.title for chapter in project.chapters] == ["The Body", "First Suspect", "False Pattern"]


def test_starter_markdown_rejects_unknown_template(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")

    with pytest.raises(StorageError):
        store.write_starter_markdown(tmp_path / "starter.md", template="unknown")


def test_starter_markdown_does_not_overwrite_without_force(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    starter = tmp_path / "starter.md"
    starter.write_text("keep me", encoding="utf-8")

    with pytest.raises(DuplicateError):
        store.write_starter_markdown(starter)

    assert starter.read_text(encoding="utf-8") == "keep me"
    store.write_starter_markdown(starter, overwrite=True)
    assert starter.read_text(encoding="utf-8").startswith("# Working Title")


def test_import_markdown_rejects_missing_chapters(tmp_path: Path) -> None:
    markdown_path = tmp_path / "source.md"
    markdown_path.write_text("# Moon Archive\n\nNo chapter headings yet.\n", encoding="utf-8")
    store = ProjectStore(tmp_path / "workspace")

    with pytest.raises(StorageError):
        store.import_markdown("moon-archive", markdown_path)


def test_search_returns_matching_chapters(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The signal arrives before sunrise.", "draft")
    store.add_chapter("first-novel", "Aftermath", "Everyone waits.", "done")

    results = store.search("first-novel", "signal")

    assert results == [
        {
            "number": 1,
            "title": "Opening",
            "status": "draft",
            "snippet": "The signal arrives before sunrise.",
        }
    ]


def test_search_requires_query(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    with pytest.raises(StorageError):
        store.search("first-novel", " ")


def test_backup_project_copies_json(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel")
    backup_path = store.backup_project("first-novel", tmp_path / "backups")

    assert backup_path.exists()
    assert backup_path.name.startswith("first-novel-")
    assert '"title": "First Novel"' in backup_path.read_text(encoding="utf-8")


def test_check_workspace_reports_healthy_projects(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening")

    assert store.check_workspace() == {"checked": 1, "ok": 1, "errors": []}


def test_check_workspace_reports_invalid_project_files(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.initialize()
    (tmp_path / "projects" / "broken.json").write_text("{not json", encoding="utf-8")

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert report["errors"]
    assert "Restore the file from a backup" in report["errors"][0]["hint"]


def test_check_workspace_reports_slug_mismatch(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    source = tmp_path / "projects" / "first-novel.json"
    target = tmp_path / "projects" / "wrong-name.json"
    source.rename(target)

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "does not match project slug" in report["errors"][0]["error"]
    assert "Rename the file" in report["errors"][0]["hint"]


def test_check_workspace_reports_chapter_number_hint(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening")
    path = tmp_path / "projects" / "first-novel.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"number": 1', '"number": 2'), encoding="utf-8")

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "non-sequential chapter numbers" in report["errors"][0]["error"]
    assert "Renumber chapters" in report["errors"][0]["hint"]
