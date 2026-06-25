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
    assert main(["--workspace", str(workspace), "doctor"]) == 0
    assert main(["--workspace", str(workspace), "show", "first-novel"]) == 0
    assert main(["--workspace", str(workspace), "stats", "first-novel"]) == 0
    assert main(["--workspace", str(workspace), "search", "first-novel", "hello"]) == 0
    assert main(["--workspace", str(workspace), "export", "first-novel", str(export_path)]) == 0
    assert main(["--workspace", str(workspace), "backup", "first-novel", str(backup_dir)]) == 0

    captured = capsys.readouterr()
    assert "First Novel (first-novel)" in captured.out
    assert "Workspace healthy." in captured.out
    assert "Words: 1" in captured.out
    assert "Opening [draft]" in captured.out
    assert export_path.exists()
    assert list(backup_dir.glob("first-novel-*.json"))


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


def test_demo_script_runs(capsys) -> None:
    assert demo_main() == 0

    captured = capsys.readouterr()
    assert "Created sample project: moon-archive (2 chapters)" in captured.out
    assert "Words:" in captured.out
    assert "Backed up:" in captured.out
