from pathlib import Path

from novel_workbench.cli import main
from scripts.demo import main as demo_main


def test_cli_create_show_stats_search_backup_and_export(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"
    export_path = tmp_path / "book.md"
    backup_dir = tmp_path / "backups"

    assert main(["--workspace", str(workspace), "init"]) == 0
    assert main(["--workspace", str(workspace), "create", "first-novel", "First Novel"]) == 0
    assert main(["--workspace", str(workspace), "add-chapter", "first-novel", "Opening", "--content", "Hello"]) == 0
    assert main(["--workspace", str(workspace), "add-chapter", "first-novel", "Ending", "--content", "Goodbye"]) == 0
    assert main(["--workspace", str(workspace), "move-chapter", "first-novel", "2", "1"]) == 0
    assert main(["--workspace", str(workspace), "rename", "first-novel", "renamed-novel", "--title", "Renamed Novel"]) == 0
    assert main(["--workspace", str(workspace), "doctor"]) == 0
    assert main(["--workspace", str(workspace), "show", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "stats", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "set-target", "renamed-novel", "10"]) == 0
    assert main(["--workspace", str(workspace), "stats", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "clear-target", "renamed-novel"]) == 0
    assert main(["--workspace", str(workspace), "search", "renamed-novel", "hello"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(export_path)]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "frontmatter.md"), "--template", "frontmatter"]) == 0
    assert main(["--workspace", str(workspace), "export", "renamed-novel", str(tmp_path / "progress.md"), "--template", "progress"]) == 0
    assert main(["--workspace", str(workspace), "backup", "renamed-novel", str(backup_dir)]) == 0

    captured = capsys.readouterr()
    assert "Renamed project: renamed-novel" in captured.out
    assert "Renamed Novel (renamed-novel)" in captured.out
    assert "Moved chapter 2 to 1: Ending" in captured.out
    assert "Workspace healthy." in captured.out
    assert "Words: 2" in captured.out
    assert "Target words: 10" in captured.out
    assert "Progress: 20%" in captured.out
    assert "Opening [draft]" in captured.out
    assert export_path.exists()
    assert "# Renamed Novel Progress" in (tmp_path / "progress.md").read_text(encoding="utf-8")
    assert list(backup_dir.glob("renamed-novel-*.json"))


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


def test_cli_reports_validation_errors(tmp_path: Path, capsys) -> None:
    code = main(["--workspace", str(tmp_path), "create", "Bad Slug", "Title"])

    captured = capsys.readouterr()
    assert code == 2
    assert "Slug must use lowercase" in captured.err


def test_cli_doctor_reports_invalid_workspace(tmp_path: Path, capsys) -> None:
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "broken.json").write_text("{not json", encoding="utf-8")

    code = main(["--workspace", str(tmp_path), "doctor"])

    captured = capsys.readouterr()
    assert code == 2
    assert "Errors: 1" in captured.out
    assert "Hint: Restore the file from a backup" in captured.out


def test_cli_prints_completion_scripts(capsys) -> None:
    assert main(["completion", "bash"]) == 0
    assert main(["completion", "zsh"]) == 0
    assert main(["completion", "powershell"]) == 0

    captured = capsys.readouterr()
    assert "complete -F _novel_completion novel" in captured.out
    assert "#compdef novel" in captured.out
    assert "Register-ArgumentCompleter" in captured.out
    assert "import-markdown" in captured.out


def test_demo_script_runs(capsys) -> None:
    assert demo_main() == 0

    captured = capsys.readouterr()
    assert "Wrote starter manuscript:" in captured.out
    assert "Imported project: working-title (3 chapters)" in captured.out
    assert "Renamed project: journey-draft" in captured.out
    assert "Created sample project: moon-archive (2 chapters)" in captured.out
    assert "Moved chapter 2 to 1: Descent" in captured.out
    assert "Words:" in captured.out
    assert "Target words: 80000" in captured.out
    assert "Backed up:" in captured.out
