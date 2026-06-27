from pathlib import Path
from datetime import date, timedelta

from novel_workbench.cli import main
from scripts.demo import main as demo_main


def test_cli_create_show_stats_search_backup_and_export(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"
    export_path = tmp_path / "book.md"
    backup_dir = tmp_path / "backups"
    custom_template = tmp_path / "custom-template.md"
    custom_export = tmp_path / "custom.md"

    assert main(["--workspace", str(workspace), "init"]) == 0
    assert main(["--workspace", str(workspace), "create", "first-novel", "First Novel"]) == 0
    summary_file = tmp_path / "summary.md"
    summary_file.write_text("A quiet opening turns dangerous.", encoding="utf-8")
    assert main(["--workspace", str(workspace), "add-chapter", "first-novel", "Opening", "--content", "Hello", "--summary-file", str(summary_file)]) == 0
    assert main(["--workspace", str(workspace), "add-chapter", "first-novel", "Ending", "--content", "Goodbye"]) == 0
    assert main(["--workspace", str(workspace), "add-chapter", "first-novel", "Cut Scene", "--content", "Remove"]) == 0
    assert main(["--workspace", str(workspace), "update-chapter", "first-novel", "1", "--summary", "The final beat reframes the opening."]) == 0
    assert main(["--workspace", str(workspace), "add-scene", "first-novel", "1", "First Image", "--summary", "A quiet clue appears."]) == 0
    assert main(["--workspace", str(workspace), "update-scene", "first-novel", "1", "1", "--status", "revising"]) == 0
    assert main(["--workspace", str(workspace), "list-scenes", "first-novel", "1"]) == 0
    assert main(["--workspace", str(workspace), "move-chapter", "first-novel", "2", "1"]) == 0
    assert main(["--workspace", str(workspace), "delete-chapter", "first-novel", "3"]) == 0
    assert main(["--workspace", str(workspace), "rename", "first-novel", "renamed-novel", "--title", "Renamed Novel"]) == 0
    revision_file = tmp_path / "revision.md"
    revision_file.write_text("Raise the stakes in act two.", encoding="utf-8")
    assert main(["--workspace", str(workspace), "set-metadata", "renamed-novel", "--genre", "science fiction", "--audience", "adult", "--revision-notes-file", str(revision_file)]) == 0
    assert main([
        "--workspace",
        str(workspace),
        "add-character",
        "renamed-novel",
        "Ada",
        "--role",
        "protagonist",
        "--goal",
        "Decode the archive signal.",
        "--conflict",
        "The station crew distrusts her.",
        "--arc",
        "Learns to ask for help.",
    ]) == 0
    location_notes = tmp_path / "location.md"
    location_notes.write_text("The lower vault floods during storms.", encoding="utf-8")
    assert main([
        "--workspace",
        str(workspace),
        "add-location",
        "renamed-novel",
        "Archive Vault",
        "--description",
        "A sealed records chamber below the city.",
        "--mood",
        "quiet dread",
        "--importance",
        "It hides the first relay.",
        "--notes-file",
        str(location_notes),
    ]) == 0
    assert main(["--workspace", str(workspace), "add-note", "renamed-novel", "Ada", "--kind", "character", "--content", "Engineer protagonist"]) == 0
    assert main(["--workspace", str(workspace), "list-notes", "renamed-novel"]) == 0
    progress_date = date.today().isoformat()
    assert main(["--workspace", str(workspace), "add-progress", "renamed-novel", "450", "--date", progress_date, "--note", "Drafted the new opening."]) == 0
    assert main(["--workspace", str(workspace), "update-progress", "renamed-novel", "1", "--words", "500", "--note", "Recounted the new opening."]) == 0
    assert main(["--workspace", str(workspace), "list-progress", "renamed-novel"]) == 0
    note_file = tmp_path / "note.md"
    note_file.write_text("Updated protagonist notes", encoding="utf-8")
    assert main(["--workspace", str(workspace), "update-note", "renamed-novel", "1", "--title", "Ada Byron", "--kind", "research", "--content-file", str(note_file)]) == 0
    assert main(["--workspace", str(workspace), "list-notes", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "doctor"]) == 0
    assert main(["--workspace", str(workspace), "dashboard"]) == 0
    assert main(["--workspace", str(workspace), "export-dashboard", str(tmp_path / "dashboard.md")]) == 0
    assert main(["--workspace", str(workspace), "show", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "focus", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "momentum", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "board", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "outline", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "plan", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "review", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "revision", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "stats", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "set-target", "renamed-novel", "10"]) == 0
    deadline = (date.today() + timedelta(days=4)).isoformat()
    assert main(["--workspace", str(workspace), "set-deadline", "renamed-novel", deadline]) == 0
    assert main(["--workspace", str(workspace), "stats", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "clear-target", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "clear-deadline", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "search", "renamed-novel", "hello"]) == 0
    custom_template.write_text("# {title}\n\n{status_summary}\n", encoding="utf-8")
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(export_path)]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(custom_export), "--template-file", str(custom_template)]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "focus.md"), "--template", "focus"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "momentum.md"), "--template", "momentum"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "board.md"), "--template", "board"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "outline.md"), "--template", "outline"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "frontmatter.md"), "--template", "frontmatter"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "progress.md"), "--template", "progress"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "review.md"), "--template", "review"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "revision.md"), "--template", "revision"]) == 0
    assert main(["--workspace", str(workspace), "delete-note", "renamed-novel", "1"]) == 0
    assert main(["--workspace", str(workspace), "backup", "renamed-novel", str(backup_dir)]) == 0
    backup_file = next(backup_dir.glob("renamed-novel-*.json"))
    assert main(["--workspace", str(workspace), "set-metadata", "renamed-novel", "--revision-notes", "Temporary change."]) == 0
    assert main(["--workspace", str(workspace), "restore-backup", str(backup_file), "--force"]) == 0

    captured = capsys.readouterr()
    assert "Renamed project: renamed-novel" in captured.out
    assert "Updated metadata for renamed-novel" in captured.out
    assert "Renamed Novel (renamed-novel)" in captured.out
    assert "# Renamed Novel Focus" in captured.out
    assert "# Renamed Novel Momentum" in captured.out
    assert "# Renamed Novel Status Board" in captured.out
    assert "# Renamed Novel Outline" in captured.out
    assert "# Renamed Novel Plan" in captured.out
    assert "# Renamed Novel Review" in captured.out
    assert "# Renamed Novel Revision Checklist" in captured.out
    assert "## Progress" in captured.out
    assert "## Notes" in captured.out
    assert "The final beat reframes the opening." in captured.out
    assert "Genre: science fiction" in captured.out
    assert "Audience: adult" in captured.out
    assert "Raise the stakes in act two." in captured.out
    assert "Moved chapter 2 to 1: Ending" in captured.out
    assert "Deleted chapter 3: Cut Scene" in captured.out
    assert "Added note 3: Ada [character]" in captured.out
    assert "Added character 1: Ada" in captured.out
    assert "Added location 2: Archive Vault" in captured.out
    assert "Decode the archive signal." in captured.out
    assert "A sealed records chamber below the city." in captured.out
    assert f"Logged progress 1: {progress_date} +450 words" in captured.out
    assert f"Updated progress 1: {progress_date} +500 words" in captured.out
    assert f"1. {progress_date}: +500 words - Recounted the new opening." in captured.out
    assert "Added scene 1.1: First Image" in captured.out
    assert "Updated scene 1.1: First Image" in captured.out
    assert "1.1. First Image [revising]" in captured.out
    assert "1. Ada [character]" in captured.out
    assert "Updated note 1: Ada Byron [research]" in captured.out
    assert "1. Ada Byron [research]" in captured.out
    assert "Updated protagonist notes" in captured.out
    assert "Deleted note 1: Ada Byron" in captured.out
    assert "Restored project: renamed-novel" in captured.out
    assert "Workspace healthy." in captured.out
    assert "Slug\tTitle\tChapters\tWords\tLogged\tStreak\tTarget\tProgress\tUpdated" in captured.out
    assert "renamed-novel\tRenamed Novel\t2\t2\t500\t1\t-\t-" in captured.out
    assert "Exported dashboard:" in captured.out
    assert "Notes: 3" in captured.out
    assert "Words: 2" in captured.out
    assert "Logged words: 500" in captured.out
    assert "Writing days: 1" in captured.out
    assert "Current streak: 1 days" in captured.out
    assert "Longest streak: 1 days" in captured.out
    assert "Average logged words: 500" in captured.out
    assert "Best writing day: 500 words" in captured.out
    assert "Target words: 10" in captured.out
    assert "Remaining words: 8" in captured.out
    assert "Progress: 20%" in captured.out
    assert f"Set target date for renamed-novel: {deadline}" in captured.out
    assert "Days until target date: 4" in captured.out
    assert "Required daily words: 2" in captured.out
    assert "Cleared target date for renamed-novel" in captured.out
    assert "Average chapter words: 1" in captured.out
    assert "Draft: 2 chapters / 2 words" in captured.out
    assert "Revising: 0 chapters / 0 words" in captured.out
    assert "Done: 0 chapters / 0 words" in captured.out
    assert "Chapter 2: Opening [draft]" in captured.out
    assert export_path.exists()
    assert "# Renamed Novel" in custom_export.read_text(encoding="utf-8")
    assert "# Novel Workbench Dashboard" in (tmp_path / "dashboard.md").read_text(encoding="utf-8")
    assert "Draft: 2 chapters / 2 words" in custom_export.read_text(encoding="utf-8")
    assert "# Renamed Novel Focus" in (tmp_path / "focus.md").read_text(encoding="utf-8")
    assert "# Renamed Novel Momentum" in (tmp_path / "momentum.md").read_text(encoding="utf-8")
    assert "# Renamed Novel Status Board" in (tmp_path / "board.md").read_text(encoding="utf-8")
    assert "# Renamed Novel Outline" in (tmp_path / "outline.md").read_text(encoding="utf-8")
    assert "# Renamed Novel Progress" in (tmp_path / "progress.md").read_text(encoding="utf-8")
    assert "# Renamed Novel Review" in (tmp_path / "review.md").read_text(encoding="utf-8")
    assert "# Renamed Novel Revision Checklist" in (tmp_path / "revision.md").read_text(encoding="utf-8")
    assert backup_file.exists()


def test_cli_writes_starter_and_imports_it(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"
    starter = tmp_path / "starter.md"

    assert main(["--workspace", str(workspace), "starter", str(starter), "--template", "hero-journey"]) == 0
    assert main(["--workspace", str(workspace), "import-markdown", "working-title", str(starter)]) == 0
    assert main(["--workspace", str(workspace), "stats", "working-title"]) == 0

    captured = capsys.readouterr()
    assert "Wrote starter manuscript:" in captured.out
    assert "Imported project: working-title (3 chapters)" in captured.out
    assert "Chapters: 3" in captured.out
    assert "Crossing the Threshold" in starter.read_text(encoding="utf-8")


def test_cli_import_markdown(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"
    markdown_path = tmp_path / "source.md"
    markdown_path.write_text(
        "# Moon Archive\n\n"
        "A historian finds a city under the lunar dust.\n\n"
        "## Chapter 1: Signal\n\n"
        "The first signal arrived.\n",
        encoding="utf-8",
    )

    assert main(["--workspace", str(workspace), "import-markdown", "moon-archive", str(markdown_path)]) == 0

    captured = capsys.readouterr()
    assert "Imported project: moon-archive (1 chapters)" in captured.out


def test_cli_sample_creates_demo_project(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"

    assert main(["--workspace", str(workspace), "sample"]) == 0
    assert main(["--workspace", str(workspace), "show", "moon-archive"]) == 0

    captured = capsys.readouterr()
    assert "Created sample project: moon-archive (2 chapters)" in captured.out
    assert "Moon Archive (moon-archive)" in captured.out


def test_cli_dashboard_reports_empty_workspace(tmp_path: Path, capsys) -> None:
    assert main(["--workspace", str(tmp_path), "dashboard"]) == 0

    captured = capsys.readouterr()
    assert "No projects found." in captured.out


def test_cli_exports_empty_dashboard(tmp_path: Path, capsys) -> None:
    output = tmp_path / "dashboard.md"

    assert main(["--workspace", str(tmp_path / "workspace"), "export-dashboard", str(output)]) == 0

    captured = capsys.readouterr()
    assert "Exported dashboard:" in captured.out
    assert output.read_text(encoding="utf-8") == "# Novel Workbench Dashboard\n\nNo projects found.\n"


def test_cli_deletes_progress_entry(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"

    assert main(["--workspace", str(workspace), "create", "first-novel", "First Novel"]) == 0
    assert main(["--workspace", str(workspace), "add-progress", "first-novel", "100", "--date", "2026-06-25"]) == 0
    assert main(["--workspace", str(workspace), "delete-progress", "first-novel", "1"]) == 0
    assert main(["--workspace", str(workspace), "list-progress", "first-novel"]) == 0

    captured = capsys.readouterr()
    assert "Deleted progress 1: 2026-06-25 +100 words" in captured.out
    assert "No progress entries found." in captured.out
    assert list((workspace / "backups").glob("first-novel-delete-progress-*.json"))


def test_cli_reports_validation_errors(tmp_path: Path, capsys) -> None:
    code = main(["--workspace", str(tmp_path), "create", "Bad Slug", "Title"])

    captured = capsys.readouterr()
    assert code == 2
    assert "Slug must use lowercase" in captured.err


def test_cli_reports_missing_content_file_as_validation_error(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"
    missing = tmp_path / "missing.md"

    assert main(["--workspace", str(workspace), "create", "first-novel", "First Novel"]) == 0
    code = main(["--workspace", str(workspace), "add-note", "first-novel", "Research", "--content-file", str(missing)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Could not read note content file" in captured.err


def test_cli_doctor_reports_invalid_workspace(tmp_path: Path, capsys) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "broken.json").write_text("{not json", encoding="utf-8")

    code = main(["--workspace", str(tmp_path), "doctor"])

    captured = capsys.readouterr()
    assert code == 2
    assert "Errors: 1" in captured.out
    assert "JSON syntax error at line 1" in captured.out
    assert "Hint: Fix the JSON syntax" in captured.out


def test_cli_migrates_legacy_workspace(tmp_path: Path, capsys) -> None:
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

    assert main(["--workspace", str(tmp_path), "migrate", "--dry-run"]) == 0
    assert '"schema_version"' not in legacy.read_text(encoding="utf-8")
    assert main(["--workspace", str(tmp_path), "migrate"]) == 0

    captured = capsys.readouterr()
    assert "Checked: 1" in captured.out
    assert "Migrated: 1" in captured.out
    assert "- Would migrate: legacy" in captured.out
    assert "- Migrated: legacy" in captured.out
    assert '"schema_version": 1' in legacy.read_text(encoding="utf-8")


def test_cli_prints_completion_scripts(capsys) -> None:
    assert main(["completion", "bash"]) == 0
    assert main(["completion", "zsh"]) == 0
    assert main(["completion", "powershell"]) == 0

    captured = capsys.readouterr()
    assert "complete -F _novel_completion novel" in captured.out
    assert "#compdef novel" in captured.out
    assert "Register-ArgumentCompleter" in captured.out
    assert "dashboard" in captured.out
    assert "export-dashboard" in captured.out
    assert "migrate" in captured.out
    assert "import-markdown" in captured.out
    assert "focus" in captured.out
    assert "momentum" in captured.out
    assert "board" in captured.out
    assert "plan" in captured.out
    assert "review" in captured.out
    assert "revision" in captured.out
    assert "set-metadata" in captured.out
    assert "set-deadline" in captured.out
    assert "add-character" in captured.out
    assert "add-location" in captured.out
    assert "update-note" in captured.out
    assert "add-progress" in captured.out
    assert "update-progress" in captured.out
    assert "delete-progress" in captured.out


def test_demo_script_runs(capsys) -> None:
    assert demo_main() == 0

    captured = capsys.readouterr()
    assert "Wrote starter manuscript:" in captured.out
    assert "Imported project: working-title (3 chapters)" in captured.out
    assert "Renamed project: journey-draft" in captured.out
    assert "Created sample project: moon-archive (2 chapters)" in captured.out
    assert "Moved chapter 2 to 1: Descent" in captured.out
    assert "Deleted chapter 2: Signal" in captured.out
    assert "Added character 1: Ada" in captured.out
    assert "Added location 2: Archive Vault" in captured.out
    assert "Added note 3: Underground rain [plot]" in captured.out
    assert "Updated note 3: Underground rain [research]" in captured.out
    assert "Updated progress 1: 2026-06-26 +1250 words" in captured.out
    assert "# Moon Archive Focus" in captured.out
    assert "# Moon Archive Momentum" in captured.out
    assert "# Moon Archive Status Board" in captured.out
    assert "# Moon Archive Review" in captured.out
    assert "# Moon Archive Revision Checklist" in captured.out
    assert "Words:" in captured.out
    assert "Target words: 80000" in captured.out
    assert "Exported dashboard:" in captured.out
    assert "Slug\tTitle\tChapters\tWords\tLogged\tStreak\tTarget\tProgress\tUpdated" in captured.out
    assert "moon-archive\tMoon Archive\t1\t8\t1250\t" in captured.out
    assert "moon-archive-outline.md" in captured.out
    assert "Backed up:" in captured.out
