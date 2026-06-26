from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def run_step(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        details = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
        raise RuntimeError(details or f"Command failed with exit code {result.returncode}")
    return result.stdout.strip()


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    demo_root = Path(tempfile.mkdtemp(prefix="novel-workbench-demo-"))
    workspace = demo_root / "workspace"
    drafts = demo_root / "drafts"
    exports = demo_root / "exports"
    backups = demo_root / "backups"
    commands = [
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "starter", str(drafts / "working-title.md"), "--template", "hero-journey"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "import-markdown", "working-title", str(drafts / "working-title.md")],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "rename", "working-title", "journey-draft", "--title", "Journey Draft"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "sample"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "move-chapter", "moon-archive", "2", "1"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "delete-chapter", "moon-archive", "2"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "add-note", "moon-archive", "Underground rain", "--kind", "plot", "--content", "The moon city has weather below the dust."],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "update-note", "moon-archive", "1", "--kind", "research", "--content", "The lower city has sealed storm drains."],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "list-notes", "moon-archive"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "set-target", "moon-archive", "80000"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "show", "moon-archive"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "stats", "moon-archive"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "doctor"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "search", "moon-archive", "rain"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "export", "moon-archive", str(exports / "moon-archive.md")],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "export", "moon-archive", str(exports / "moon-archive-frontmatter.md"), "--template", "frontmatter"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "export", "moon-archive", str(exports / "moon-archive-progress.md"), "--template", "progress"],
        [sys.executable, "-m", "novel_workbench.cli", "--workspace", str(workspace), "backup", "moon-archive", str(backups)],
    ]

    for command in commands:
        print(f"$ {' '.join(command)}")
        output = run_step(command, repo_root)
        if output:
            print(output)
        print()

    print(f"Demo workspace: {demo_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
