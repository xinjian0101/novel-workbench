from datetime import date, timedelta
from pathlib import Path

import pytest

from novel_workbench.storage import (
    DuplicateError,
    NotFoundError,
    ProjectStore,
    StorageError,
    board_lines,
    outline_lines,
    parse_markdown_chapters,
    planning_lines,
    revision_lines,
    workspace_dashboard_lines,
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


def test_workspace_dashboard_summarizes_projects(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The story begins.")
    store.set_target_words("first-novel", 10)
    store.add_progress("first-novel", 250, date.today().isoformat())
    store.create_project("second-novel", "Second Novel")

    rows = store.workspace_dashboard()

    by_slug = {str(row["slug"]): row for row in rows}

    assert by_slug["second-novel"]["title"] == "Second Novel"
    assert by_slug["second-novel"]["chapters"] == 0
    assert by_slug["second-novel"]["target_words"] is None
    assert by_slug["second-novel"]["progress_percent"] is None
    assert by_slug["first-novel"]["chapters"] == 1
    assert by_slug["first-novel"]["words"] == 3
    assert by_slug["first-novel"]["logged_words"] == 250
    assert by_slug["first-novel"]["current_streak_days"] == 1
    assert by_slug["first-novel"]["target_words"] == 10
    assert by_slug["first-novel"]["progress_percent"] == 30


def test_export_dashboard_writes_markdown_report(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First | Novel")
    store.add_chapter("first-novel", "Opening", "The story begins.")
    store.set_target_words("first-novel", 10)
    output = tmp_path / "reports" / "dashboard.md"

    store.export_dashboard(output)

    text = output.read_text(encoding="utf-8")
    assert text.startswith("# Novel Workbench Dashboard\n\n")
    assert "| Slug | Title | Chapters | Words | Logged | Streak | Target | Progress | Updated |" in text
    assert "| first-novel | First \\| Novel | 1 | 3 | 0 | 0 | 10 | 30% |" in text


def test_workspace_dashboard_lines_handles_empty_workspace() -> None:
    assert workspace_dashboard_lines([]) == ["# Novel Workbench Dashboard", "", "No projects found."]


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


def test_chapter_summary_is_stored_updated_and_shown_in_outline(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.add_chapter("first-novel", "Opening", "The story begins.", "draft", "Introduce the protagonist.")

    updated = store.update_chapter("first-novel", 1, summary="Reveal the first pressure point.")
    project = store.get_project("first-novel")

    assert updated.summary == "Reveal the first pressure point."
    assert project.chapters[0].summary == "Reveal the first pressure point."
    assert outline_lines(project) == [
        "# First Novel Outline",
        "",
        "A concise premise.",
        "",
        "## Chapters",
        "",
        "1. Opening [draft]",
        "   Reveal the first pressure point.",
    ]


def test_scene_crud_renumbers_and_updates_outline(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", summary="Set the initial pressure.")

    first = store.add_scene("first-novel", 1, "Arrival", "The crew reaches the archive.")
    second = store.add_scene("first-novel", 1, "Signal", "A hidden relay wakes up.", "revising")
    updated = store.update_scene("first-novel", 1, second.number, title="Signal Found", status="done")
    deleted = store.delete_scene("first-novel", 1, first.number)
    scenes = store.list_scenes("first-novel", 1)
    project = store.get_project("first-novel")

    assert first.number == 1
    assert updated.title == "Signal Found"
    assert updated.status == "done"
    assert deleted.title == "Arrival"
    assert [(scene.number, scene.title) for scene in scenes] == [(1, "Signal Found")]
    assert "   1.1 Signal Found [done]" in outline_lines(project)
    backups = list((tmp_path / "backups").glob("first-novel-delete-scene-*.json"))
    assert len(backups) == 1


def test_planning_lines_groups_project_progress_chapters_notes_and_log(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.update_project_metadata(
        "first-novel",
        genre="mystery",
        audience="adult",
        revision_notes="Keep the clue trail fair.",
    )
    store.set_target_words("first-novel", 10000)
    target_date = (date.today() + timedelta(days=10)).isoformat()
    store.set_target_date("first-novel", target_date)
    store.add_chapter("first-novel", "Opening", "The story begins.", "draft", "Introduce the central clue.")
    store.add_scene("first-novel", 1, "First clue", "The clue appears in plain sight.")
    store.add_note("first-novel", "Ada", "Engineer protagonist.", "character")
    store.add_note("first-novel", "Archive", "Underground records room.", "location")
    progress_date = date.today().isoformat()
    store.add_progress("first-novel", 400, progress_date, "Drafted opening pages.")

    lines = planning_lines(store.get_project("first-novel"))

    assert "# First Novel Plan" in lines
    assert "- Synopsis: A concise premise." in lines
    assert "- Genre: mystery" in lines
    assert "- Audience: adult" in lines
    assert "Keep the clue trail fair." in lines
    assert "- Target words: 10000" in lines
    assert f"- Target date: {target_date}" in lines
    assert "- Current streak: 1 days" in lines
    assert "- Longest streak: 1 days" in lines
    assert "1. Opening [draft] - 3 words" in lines
    assert "   1.1 First clue [draft]" in lines
    assert "### Character" in lines
    assert "- Ada" in lines
    assert "### Location" in lines
    assert "- Archive" in lines
    assert f"| {progress_date} | 400 | Drafted opening pages. |" in lines


def test_revision_lines_builds_actionable_revision_checklist(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.update_project_metadata("first-novel", revision_notes="Tighten the midpoint.")
    store.add_chapter("first-novel", "Opening", "The story begins.", "done", "Keep the hook.")
    store.add_chapter("first-novel", "Middle", "A second scene unfolds.", "revising")
    store.add_scene("first-novel", 2, "Confrontation", "Raise the cost.", "draft")
    store.add_note("first-novel", "Ada", "Engineer protagonist.", "character")

    lines = revision_lines(store.get_project("first-novel"))

    assert "# First Novel Revision Checklist" in lines
    assert "- Words: 7" in lines
    assert "Tighten the midpoint." in lines
    assert "- [x] Chapter 1: Opening [done] - 3 words" in lines
    assert "  - Summary: Keep the hook." in lines
    assert "- [ ] Chapter 2: Middle [revising] - 4 words" in lines
    assert "- [ ] 2.1 Confrontation [draft]" in lines
    assert "  - Raise the cost." in lines
    assert "- [ ] Ada [character]" in lines


def test_revision_lines_handles_empty_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    lines = revision_lines(store.get_project("first-novel"))

    assert "- [ ] Add chapters before starting a revision pass." in lines
    assert "No unfinished scenes." in lines
    assert "No planning notes yet." in lines


def test_board_lines_groups_chapters_by_status(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The story begins.", "draft", "Set the hook.")
    store.add_chapter("first-novel", "Middle", "A clue turns.", "revising")
    store.add_chapter("first-novel", "Ending", "The case closes.", "done")
    store.add_scene("first-novel", 2, "Midpoint", "Raise the pressure.", "draft")
    store.add_scene("first-novel", 2, "Quiet Beat", "Resolve a subplot.", "done")

    lines = board_lines(store.get_project("first-novel"))

    assert "# First Novel Status Board" in lines
    assert "## Draft" in lines
    assert "- Chapter 1: Opening (3 words)" in lines
    assert "  - Set the hook." in lines
    assert "## Revising" in lines
    assert "- Chapter 2: Middle (3 words)" in lines
    assert "  - Open scenes: 2.1 Midpoint [draft]" in lines
    assert "## Done" in lines
    assert "- Chapter 3: Ending (3 words)" in lines


def test_board_lines_handles_empty_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    assert board_lines(store.get_project("first-novel")) == [
        "# First Novel Status Board",
        "",
        "No chapters yet.",
    ]


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
    backups = list((tmp_path / "backups").glob("first-novel-delete-chapter-*.json"))
    assert len(backups) == 1
    assert '"title": "Middle"' in backups[0].read_text(encoding="utf-8")
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
    store.set_target_date("first-novel", "2026-12-31")
    store.update_project_metadata(
        "first-novel",
        genre="science fiction",
        audience="adult",
        revision_notes="Tighten the midpoint.",
    )
    store.add_chapter("first-novel", "Opening", "The story begins.")

    project = store.rename_project("first-novel", "second-novel", "Second Novel")

    assert project.slug == "second-novel"
    assert project.title == "Second Novel"
    assert project.target_words == 50000
    assert project.target_date == "2026-12-31"
    assert project.genre == "science fiction"
    assert project.audience == "adult"
    assert project.revision_notes == "Tighten the midpoint."
    assert project.chapters[0].title == "Opening"
    assert not (tmp_path / "workspace" / "projects" / "first-novel.json").exists()
    assert (tmp_path / "workspace" / "projects" / "second-novel.json").exists()
    backups = list((tmp_path / "workspace" / "backups").glob("first-novel-rename-*.json"))
    assert len(backups) == 1
    assert '"slug": "first-novel"' in backups[0].read_text(encoding="utf-8")
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
    store.set_target_date("first-novel", "2026-12-31")
    store.update_project_metadata(
        "first-novel",
        genre="science fiction",
        audience="adult",
        revision_notes='Resolve "Signal" continuity.',
    )
    store.add_chapter("first-novel", "Opening", "The story begins.")
    output = tmp_path / "exports" / "first-novel.md"

    store.export_markdown("first-novel", output, template="frontmatter")

    assert output.read_text(encoding="utf-8") == (
        "---\n"
        'title: "First Novel"\n'
        'slug: "first-novel"\n'
        'synopsis: "A concise premise."\n'
        'genre: "science fiction"\n'
        'audience: "adult"\n'
        'revision_notes: "Resolve \\"Signal\\" continuity."\n'
        "target_words: 50000\n"
        'target_date: "2026-12-31"\n'
        "---\n\n"
        "# First Novel\n\n"
        "A concise premise.\n\n"
        "## Chapter 1: Opening\n\n"
        "The story begins.\n"
    )


def test_export_markdown_outline_template(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.update_project_metadata("first-novel", genre="mystery", audience="adult")
    store.add_chapter("first-novel", "Opening", summary="Introduce the clue.")
    store.add_scene("first-novel", 1, "First clue", "A detail looks misplaced.", "revising")
    output = tmp_path / "exports" / "first-novel-outline.md"

    store.export_markdown("first-novel", output, template="outline")

    assert output.read_text(encoding="utf-8") == (
        "# First Novel Outline\n\n"
        "A concise premise.\n\n"
        "## Metadata\n\n"
        "- Genre: mystery\n"
        "- Audience: adult\n\n"
        "## Chapters\n\n"
        "1. Opening [draft]\n"
        "   Introduce the clue.\n"
        "   1.1 First clue [revising]\n"
        "      A detail looks misplaced.\n"
    )


def test_export_markdown_progress_template(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.set_target_words("first-novel", 10)
    store.update_project_metadata(
        "first-novel",
        genre="mystery",
        audience="young adult",
        revision_notes="Make the clue trail fair.",
    )
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
        "- Notes: 0\n"
        "- Words: 7\n"
        "- Characters: 40\n"
        "- Logged writing days: 0\n"
        "- Logged words: 0\n"
        "- Current streak: 0 days\n"
        "- Longest streak: 0 days\n"
        "- Genre: mystery\n"
        "- Audience: young adult\n"
        "- Target words: 10\n"
        "- Remaining words: 3\n"
        "- Progress: 70%\n"
        "- Average chapter words: 4\n\n"
        "## Revision Notes\n\n"
        "Make the clue trail fair.\n\n"
        "## Status\n\n"
        "- Draft: 0 chapters / 0 words\n"
        "- Revising: 1 chapters / 4 words\n"
        "- Done: 1 chapters / 3 words\n\n"
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


def test_export_markdown_custom_template_file(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel", "A concise premise.")
    store.set_target_words("first-novel", 10)
    store.update_project_metadata("first-novel", genre="fantasy", audience="adult")
    store.add_chapter("first-novel", "Opening", "The story begins.", "done")
    template = tmp_path / "template.md"
    template.write_text(
        "# {title}\n\n"
        "Genre: {genre}\n"
        "Audience: {audience}\n"
        "Words: {words}/{target_words}\n"
        "Remaining: {remaining_words}\n\n"
        "Streak: {current_streak_days}/{longest_streak_days}\n\n"
        "{status_summary}\n\n"
        "{status_board}\n\n"
        "{chapter_table}\n\n"
        "{revision_checklist}\n",
        encoding="utf-8",
    )
    output = tmp_path / "exports" / "custom.md"

    store.export_markdown("first-novel", output, template_path=template)

    assert output.read_text(encoding="utf-8") == (
        "# First Novel\n\n"
        "Genre: fantasy\n"
        "Audience: adult\n"
        "Words: 3/10\n"
        "Remaining: 7\n\n"
        "Streak: 0/0\n\n"
        "- Draft: 0 chapters / 0 words\n"
        "- Revising: 0 chapters / 0 words\n"
        "- Done: 1 chapters / 3 words\n\n"
        "# First Novel Status Board\n\n"
        "## Draft\n\n"
        "No chapters.\n\n"
        "## Revising\n\n"
        "No chapters.\n\n"
        "## Done\n\n"
        "- Chapter 1: Opening (3 words)\n\n"
        "| # | Title | Status | Words |\n"
        "|---:|---|---|---:|\n"
        "| 1 | Opening | done | 3 |\n\n"
        "# First Novel Revision Checklist\n\n"
        "## Snapshot\n\n"
        "- Slug: `first-novel`\n"
        "- Words: 3\n"
        "- Chapters: 1\n"
        "- Draft: 0 chapters / 0 words\n"
        "- Revising: 0 chapters / 0 words\n"
        "- Done: 1 chapters / 3 words\n\n"
        "## Chapter Pass\n\n"
        "- [x] Chapter 1: Opening [done] - 3 words\n\n"
        "## Scene Follow-Ups\n\n"
        "No unfinished scenes.\n\n"
        "## Planning Notes To Review\n\n"
        "No planning notes yet.\n"
    )


def test_export_markdown_custom_template_rejects_unknown_field(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel")
    template = tmp_path / "template.md"
    template.write_text("{unknown}", encoding="utf-8")

    with pytest.raises(StorageError, match="Unknown export template field"):
        store.export_markdown("first-novel", tmp_path / "book.md", template_path=template)


def test_project_stats_count_progress(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The story begins.", "done")
    store.add_chapter("first-novel", "Middle", "A second scene unfolds.", "revising")
    first_day = date.today() - timedelta(days=1)
    second_day = date.today()
    store.add_progress("first-novel", 500, first_day.isoformat(), "Drafted the opening.")
    store.add_progress("first-novel", 300, first_day.isoformat())
    store.add_progress("first-novel", 700, second_day.isoformat(), "Expanded the middle.")

    assert store.project_stats("first-novel") == {
        "chapters": 2,
        "notes": 0,
        "words": 7,
        "logged_words": 1500,
        "writing_days": 2,
        "current_streak_days": 2,
        "longest_streak_days": 2,
        "average_logged_words": 750,
        "best_day_words": 800,
        "target_words": None,
        "target_date": None,
        "remaining_words": None,
        "progress_percent": None,
        "days_until_target_date": None,
        "required_daily_words": None,
        "average_chapter_words": 4,
        "characters": 40,
        "draft": 0,
        "revising": 1,
        "done": 1,
        "draft_words": 0,
        "revising_words": 4,
        "done_words": 3,
    }


def test_project_stats_show_target_progress(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The story begins.", "draft")
    store.set_target_words("first-novel", 10)
    target_date = date.today() + timedelta(days=7)
    store.set_target_date("first-novel", target_date.isoformat())

    stats = store.project_stats("first-novel")

    assert stats["words"] == 3
    assert stats["notes"] == 0
    assert stats["logged_words"] == 0
    assert stats["writing_days"] == 0
    assert stats["current_streak_days"] == 0
    assert stats["longest_streak_days"] == 0
    assert stats["average_logged_words"] is None
    assert stats["best_day_words"] is None
    assert stats["target_words"] == 10
    assert stats["target_date"] == target_date.isoformat()
    assert stats["remaining_words"] == 7
    assert stats["progress_percent"] == 30
    assert stats["days_until_target_date"] == 7
    assert stats["required_daily_words"] == 1
    assert stats["average_chapter_words"] == 3


def test_set_target_words_validates_positive_values(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    with pytest.raises(StorageError):
        store.set_target_words("first-novel", 0)


def test_set_target_date_validates_iso_date(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    project = store.set_target_date("first-novel", "2026-12-31")

    assert project.target_date == "2026-12-31"
    with pytest.raises(StorageError, match="YYYY-MM-DD"):
        store.set_target_date("first-novel", "12/31/2026")


def test_progress_entries_are_stored_sorted_and_validated(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    second = store.add_progress("first-novel", 200, "2026-06-26", "Second session.")
    first = store.add_progress("first-novel", 100, "2026-06-25", "First session.")

    assert second.id == 1
    assert first.id == 2
    assert [(entry.date, entry.words, entry.note) for entry in store.list_progress("first-novel")] == [
        ("2026-06-25", 100, "First session."),
        ("2026-06-26", 200, "Second session."),
    ]

    with pytest.raises(StorageError, match="greater than zero"):
        store.add_progress("first-novel", 0, "2026-06-27")
    with pytest.raises(StorageError, match="YYYY-MM-DD"):
        store.add_progress("first-novel", 100, "06/27/2026")


def test_update_and_delete_progress_entries(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    first = store.add_progress("first-novel", 200, "2026-06-26", "Initial note.")
    second = store.add_progress("first-novel", 100, "2026-06-27", "Remove later.")

    updated = store.update_progress(
        "first-novel",
        first.id,
        entry_date="2026-06-25",
        words=250,
        note="Recounted pages.",
    )
    deleted = store.delete_progress("first-novel", second.id)
    entries = store.list_progress("first-novel")

    assert updated.date == "2026-06-25"
    assert updated.words == 250
    assert updated.note == "Recounted pages."
    assert deleted.id == second.id
    assert [(entry.id, entry.date, entry.words, entry.note) for entry in entries] == [
        (first.id, "2026-06-25", 250, "Recounted pages.")
    ]
    backups = list((tmp_path / "backups").glob("first-novel-delete-progress-*.json"))
    assert len(backups) == 1
    assert '"id": 2' in backups[0].read_text(encoding="utf-8")


def test_update_and_delete_progress_validate_inputs(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    entry = store.add_progress("first-novel", 100, "2026-06-25")

    with pytest.raises(StorageError, match="Provide at least one progress field"):
        store.update_progress("first-novel", entry.id)
    with pytest.raises(StorageError, match="Progress id must be greater than zero"):
        store.update_progress("first-novel", 0, words=100)
    with pytest.raises(StorageError, match="YYYY-MM-DD"):
        store.update_progress("first-novel", entry.id, entry_date="06/26/2026")
    with pytest.raises(StorageError, match="greater than zero"):
        store.update_progress("first-novel", entry.id, words=0)
    with pytest.raises(NotFoundError):
        store.update_progress("first-novel", 99, words=100)
    with pytest.raises(StorageError, match="Progress id must be greater than zero"):
        store.delete_progress("first-novel", 0)
    with pytest.raises(NotFoundError):
        store.delete_progress("first-novel", 99)


def test_clear_target_words(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.set_target_words("first-novel", 10)

    project = store.set_target_words("first-novel", None)

    assert project.target_words is None
    assert store.project_stats("first-novel")["progress_percent"] is None


def test_clear_target_date(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.set_target_date("first-novel", "2026-12-31")

    project = store.set_target_date("first-novel", None)

    assert project.target_date is None
    assert store.project_stats("first-novel")["days_until_target_date"] is None


def test_update_project_metadata_changes_optional_fields(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    project = store.update_project_metadata(
        "first-novel",
        genre=" fantasy ",
        audience=" adult ",
        revision_notes="  Cut chapter three.  ",
    )
    loaded = store.get_project("first-novel")

    assert project.genre == "fantasy"
    assert project.audience == "adult"
    assert project.revision_notes == "Cut chapter three."
    assert loaded.genre == "fantasy"
    assert loaded.audience == "adult"
    assert loaded.revision_notes == "Cut chapter three."


def test_update_project_metadata_requires_a_field(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    with pytest.raises(StorageError):
        store.update_project_metadata("first-novel")


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
    assert project.target_date is None
    assert project.notes == []
    assert project.progress == []
    assert project.genre == ""
    assert project.audience == ""
    assert project.revision_notes == ""
    assert project.schema_version == 0


def test_migrate_workspace_normalizes_legacy_project_and_snapshots(tmp_path: Path) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    legacy = projects / "legacy.json"
    legacy.write_text(
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

    dry_run = store.migrate_workspace(dry_run=True)

    assert dry_run == {"checked": 1, "migrated": 1, "projects": ["legacy"]}
    assert '"schema_version"' not in legacy.read_text(encoding="utf-8")

    report = store.migrate_workspace()
    migrated_text = legacy.read_text(encoding="utf-8")

    assert report == {"checked": 1, "migrated": 1, "projects": ["legacy"]}
    assert '"schema_version": 1' in migrated_text
    assert '"target_words": null' in migrated_text
    assert '"target_date": null' in migrated_text
    assert '"notes": []' in migrated_text
    assert '"progress": []' in migrated_text
    backups = list((tmp_path / "backups").glob("legacy-migrate-*.json"))
    assert len(backups) == 1
    assert '"schema_version"' not in backups[0].read_text(encoding="utf-8")


def test_migrate_workspace_reports_noop_for_current_schema(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    report = store.migrate_workspace()

    assert report == {"checked": 1, "migrated": 0, "projects": []}


def test_add_list_and_delete_notes(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    first = store.add_note("first-novel", "Ada", "Engineer protagonist", "character")
    second = store.add_note("first-novel", "Dock", "Rainy port", "location")

    assert first.id == 1
    assert second.id == 2
    assert [note.title for note in store.list_notes("first-novel")] == ["Ada", "Dock"]
    assert [note.title for note in store.list_notes("first-novel", "character")] == ["Ada"]
    assert store.project_stats("first-novel")["notes"] == 2

    deleted = store.delete_note("first-novel", 1)

    assert deleted.title == "Ada"
    assert [note.title for note in store.list_notes("first-novel")] == ["Dock"]
    assert store.project_stats("first-novel")["notes"] == 1
    backups = list((tmp_path / "backups").glob("first-novel-delete-note-*.json"))
    assert len(backups) == 1
    assert '"title": "Ada"' in backups[0].read_text(encoding="utf-8")


def test_update_note_changes_fields(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    note = store.add_note("first-novel", "Ada", "Engineer protagonist", "character")

    updated = store.update_note(
        "first-novel",
        note.id,
        title="Ada Byron",
        content="Lead systems engineer",
        kind="research",
    )
    loaded = store.list_notes("first-novel")[0]

    assert updated.title == "Ada Byron"
    assert updated.content == "Lead systems engineer"
    assert updated.kind == "research"
    assert loaded.title == "Ada Byron"
    assert loaded.content == "Lead systems engineer"
    assert loaded.kind == "research"


def test_notes_validate_kind_and_id(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")

    with pytest.raises(StorageError):
        store.add_note("first-novel", "Bad", kind="unknown")
    note = store.add_note("first-novel", "Ada")
    with pytest.raises(StorageError):
        store.update_note("first-novel", note.id)
    with pytest.raises(StorageError):
        store.update_note("first-novel", 0, title="Bad")
    with pytest.raises(StorageError):
        store.update_note("first-novel", note.id, kind="unknown")
    with pytest.raises(StorageError):
        store.delete_note("first-novel", 0)
    with pytest.raises(NotFoundError):
        store.delete_note("first-novel", 99)


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


def test_import_markdown_reports_invalid_utf8(tmp_path: Path) -> None:
    markdown_path = tmp_path / "source.md"
    markdown_path.write_bytes(b"\xff\xfe")
    store = ProjectStore(tmp_path / "workspace")

    with pytest.raises(StorageError, match="Markdown file is not valid UTF-8"):
        store.import_markdown("moon-archive", markdown_path)


def test_export_markdown_custom_template_reports_invalid_utf8(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "First Novel")
    template = tmp_path / "template.md"
    template.write_bytes(b"\xff\xfe")

    with pytest.raises(StorageError, match="Template file is not valid UTF-8"):
        store.export_markdown("first-novel", tmp_path / "book.md", template_path=template)


def test_search_returns_matching_chapters(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening", "The signal arrives before sunrise.", "draft")
    store.update_chapter("first-novel", 1, summary="A hidden relay wakes up.")
    store.add_chapter("first-novel", "Aftermath", "Everyone waits.", "done")
    store.add_scene("first-novel", 2, "Waiting Room", "The team debates the relay signal.")
    store.add_note("first-novel", "Signal origin", "The beacon is under the sea.", "plot")

    results = store.search("first-novel", "signal")

    assert results == [
        {
            "type": "chapter",
            "number": 1,
            "title": "Opening",
            "status": "draft",
            "snippet": "The signal arrives before sunrise.",
        },
        {
            "type": "chapter",
            "number": 2,
            "title": "Aftermath",
            "status": "done",
            "snippet": "The team debates the relay signal.",
        },
        {
            "type": "note",
            "number": 1,
            "title": "Signal origin",
            "status": "plot",
            "snippet": "The beacon is under the sea.",
        },
    ]

    summary_results = store.search("first-novel", "relay")
    assert [result["title"] for result in summary_results] == ["Opening", "Aftermath"]
    assert summary_results[0]["snippet"] == "A hidden relay wakes up."
    assert summary_results[1]["snippet"] == "The team debates the relay signal."


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


def test_restore_backup_creates_project_from_backup(tmp_path: Path) -> None:
    source = ProjectStore(tmp_path / "source")
    source.create_project("first-novel", "First Novel", "A concise premise.")
    source.add_chapter("first-novel", "Opening", "The story begins.")
    backup_path = source.backup_project("first-novel", tmp_path / "backups")
    restored = ProjectStore(tmp_path / "restored")

    project = restored.restore_backup(backup_path)

    assert project.slug == "first-novel"
    assert restored.get_project("first-novel").chapters[0].title == "Opening"


def test_restore_backup_requires_force_before_overwrite(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "Original")
    backup_path = store.backup_project("first-novel", tmp_path / "backups")
    store.update_project_metadata("first-novel", revision_notes="Changed after backup.")

    with pytest.raises(DuplicateError):
        store.restore_backup(backup_path)


def test_restore_backup_force_overwrites_and_snapshots_current_project(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path / "workspace")
    store.create_project("first-novel", "Original")
    store.add_chapter("first-novel", "Original Chapter", "Keep me in the restore snapshot.")
    backup_path = store.backup_project("first-novel", tmp_path / "backups")
    store.update_chapter("first-novel", 1, title="Changed Chapter")

    project = store.restore_backup(backup_path, overwrite=True)

    assert project.chapters[0].title == "Original Chapter"
    backups = list((tmp_path / "workspace" / "backups").glob("first-novel-restore-*.json"))
    assert len(backups) == 1
    assert '"title": "Changed Chapter"' in backups[0].read_text(encoding="utf-8")


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
    assert "JSON syntax error at line 1" in report["errors"][0]["error"]
    assert "reported line and column" in report["errors"][0]["hint"]


def test_check_workspace_reports_missing_required_field(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.initialize()
    (tmp_path / "projects" / "missing-title.json").write_text(
        '{\n'
        '  "slug": "missing-title",\n'
        '  "chapters": [],\n'
        '  "created_at": "2026-06-25T00:00:00+00:00",\n'
        '  "updated_at": "2026-06-25T00:00:00+00:00"\n'
        '}\n',
        encoding="utf-8",
    )

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "missing required field: title" in report["errors"][0]["error"]
    assert "Add the missing required field" in report["errors"][0]["hint"]


def test_check_workspace_reports_invalid_field_value(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.initialize()
    (tmp_path / "projects" / "bad-target.json").write_text(
        '{\n'
        '  "slug": "bad-target",\n'
        '  "title": "Bad Target",\n'
        '  "synopsis": "",\n'
        '  "target_words": "many",\n'
        '  "chapters": [],\n'
        '  "created_at": "2026-06-25T00:00:00+00:00",\n'
        '  "updated_at": "2026-06-25T00:00:00+00:00"\n'
        '}\n',
        encoding="utf-8",
    )

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "invalid field value" in report["errors"][0]["error"]
    assert "matches the project schema" in report["errors"][0]["hint"]


def test_check_workspace_reports_invalid_chapter_status(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening")
    path = tmp_path / "projects" / "first-novel.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"status": "draft"', '"status": "blocked"'), encoding="utf-8")

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "Status must be one of" in report["errors"][0]["error"]
    assert "matches the project schema" in report["errors"][0]["hint"]


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


def test_check_workspace_reports_scene_number_hint(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_chapter("first-novel", "Opening")
    store.add_scene("first-novel", 1, "Arrival")
    path = tmp_path / "projects" / "first-novel.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"number": 1,\n          "title": "Arrival"', '"number": 2,\n          "title": "Arrival"'), encoding="utf-8")

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "non-sequential scene numbers" in report["errors"][0]["error"]
    assert "Renumber scenes" in report["errors"][0]["hint"]


def test_check_workspace_reports_invalid_progress_entry(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.add_progress("first-novel", 100, "2026-06-25")
    path = tmp_path / "projects" / "first-novel.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"words": 100', '"words": 0'), encoding="utf-8")

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "Progress words must be greater than zero" in report["errors"][0]["error"]


def test_check_workspace_reports_invalid_target_date(tmp_path: Path) -> None:
    store = ProjectStore(tmp_path)
    store.create_project("first-novel", "First Novel")
    store.set_target_date("first-novel", "2026-12-31")
    path = tmp_path / "projects" / "first-novel.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"target_date": "2026-12-31"', '"target_date": "soon"'), encoding="utf-8")

    report = store.check_workspace()

    assert report["checked"] == 1
    assert report["ok"] == 0
    assert "Target date must use YYYY-MM-DD format" in report["errors"][0]["error"]
