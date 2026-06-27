from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from novel_workbench.storage import ProjectStore


def build_demo_site(output_dir: Path) -> Path:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="novel-workbench-pages-") as tmp:
        workspace = Path(tmp) / "workspace"
        store = ProjectStore(workspace)
        project = store.create_sample_project()
        store.update_project_metadata(
            project.slug,
            genre="science fiction",
            audience="adult",
            revision_notes="Use the descent as the discovery hook for the next drafting session.",
        )
        store.move_chapter(project.slug, 2, 1)
        store.add_progress(project.slug, 1200, "2026-06-26", "Drafted the descent sequence.")
        store.set_target_words(project.slug, 80000)
        store.export_site(project.slug, output_dir)
    return output_dir


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    output_dir = Path(args[0]) if args else Path("site")
    build_demo_site(output_dir)
    print(f"Built Pages demo site: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
