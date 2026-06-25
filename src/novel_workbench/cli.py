from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .storage import ProjectStore, StorageError


def default_workspace() -> Path:
    configured = os.environ.get("NOVEL_WORKBENCH_HOME")
    return Path(configured).expanduser() if configured else Path.cwd() / "workspace"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="novel", description="Manage a local novel writing workspace.")
    parser.add_argument("--workspace", type=Path, default=default_workspace(), help="Workspace directory.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create the workspace directory.")
    subparsers.add_parser("list", help="List projects.")
    subparsers.add_parser("doctor", help="Validate workspace project files.")

    sample = subparsers.add_parser("sample", help="Create a small sample project.")
    sample.add_argument("--slug", default="moon-archive", help="Sample project slug.")

    create = subparsers.add_parser("create", help="Create a project.")
    create.add_argument("slug", help="Lowercase project identifier, for example: first-novel.")
    create.add_argument("title", help="Project title.")
    create.add_argument("--synopsis", default="", help="Short project synopsis.")

    import_markdown = subparsers.add_parser("import-markdown", help="Create a project from a Markdown manuscript.")
    import_markdown.add_argument("slug")
    import_markdown.add_argument("input", type=Path)

    show = subparsers.add_parser("show", help="Show project details.")
    show.add_argument("slug")

    stats = subparsers.add_parser("stats", help="Show drafting progress for a project.")
    stats.add_argument("slug")

    set_target = subparsers.add_parser("set-target", help="Set a project target word count.")
    set_target.add_argument("slug")
    set_target.add_argument("words", type=int)

    clear_target = subparsers.add_parser("clear-target", help="Clear a project target word count.")
    clear_target.add_argument("slug")

    search = subparsers.add_parser("search", help="Search chapter titles and content.")
    search.add_argument("slug")
    search.add_argument("query")

    add_chapter = subparsers.add_parser("add-chapter", help="Append a chapter.")
    add_chapter.add_argument("slug")
    add_chapter.add_argument("title")
    add_chapter.add_argument("--content", default="", help="Initial chapter content.")
    add_chapter.add_argument("--status", default="draft", help="draft, revising, or done.")

    update_chapter = subparsers.add_parser("update-chapter", help="Update an existing chapter.")
    update_chapter.add_argument("slug")
    update_chapter.add_argument("number", type=int)
    update_chapter.add_argument("--title")
    update_chapter.add_argument("--content")
    update_chapter.add_argument("--content-file", type=Path)
    update_chapter.add_argument("--status")

    export = subparsers.add_parser("export", help="Export a project to Markdown.")
    export.add_argument("slug")
    export.add_argument("output", type=Path)
    export.add_argument("--template", default="default", help="default or frontmatter.")

    backup = subparsers.add_parser("backup", help="Copy a project JSON file to a backup directory.")
    backup.add_argument("slug")
    backup.add_argument("output_dir", type=Path)

    return parser


def run(args: argparse.Namespace) -> int:
    store = ProjectStore(args.workspace)
    if args.command == "init":
        store.initialize()
        print(f"Workspace ready: {args.workspace}")
        return 0
    if args.command == "list":
        projects = store.list_projects()
        if not projects:
            print("No projects found.")
            return 0
        for project in projects:
            print(f"{project.slug}\t{project.title}\t{len(project.chapters)} chapters")
        return 0
    if args.command == "doctor":
        report = store.check_workspace()
        print(f"Checked: {report['checked']}")
        print(f"OK: {report['ok']}")
        errors = report["errors"]
        if not isinstance(errors, list):
            raise StorageError("Invalid doctor report.")
        if not errors:
            print("Workspace healthy.")
            return 0
        print(f"Errors: {len(errors)}")
        for error in errors:
            print(f"- {error['file']}: {error['error']}")
            if error.get("hint"):
                print(f"  Hint: {error['hint']}")
        return 2
    if args.command == "sample":
        project = store.create_sample_project(args.slug)
        print(f"Created sample project: {project.slug} ({len(project.chapters)} chapters)")
        return 0
    if args.command == "create":
        project = store.create_project(args.slug, args.title, args.synopsis)
        print(f"Created project: {project.slug}")
        return 0
    if args.command == "import-markdown":
        project = store.import_markdown(args.slug, args.input)
        print(f"Imported project: {project.slug} ({len(project.chapters)} chapters)")
        return 0
    if args.command == "show":
        project = store.get_project(args.slug)
        print(f"{project.title} ({project.slug})")
        if project.synopsis:
            print(project.synopsis)
        for chapter in sorted(project.chapters, key=lambda item: item.number):
            print(f"{chapter.number}. {chapter.title} [{chapter.status}]")
        return 0
    if args.command == "stats":
        stats = store.project_stats(args.slug)
        print(f"Chapters: {stats['chapters']}")
        print(f"Words: {stats['words']}")
        if stats["target_words"] is not None:
            print(f"Target words: {stats['target_words']}")
            print(f"Progress: {stats['progress_percent']}%")
        print(f"Characters: {stats['characters']}")
        print(f"Draft: {stats['draft']}")
        print(f"Revising: {stats['revising']}")
        print(f"Done: {stats['done']}")
        return 0
    if args.command == "set-target":
        project = store.set_target_words(args.slug, args.words)
        print(f"Set target words for {project.slug}: {project.target_words}")
        return 0
    if args.command == "clear-target":
        project = store.set_target_words(args.slug, None)
        print(f"Cleared target words for {project.slug}")
        return 0
    if args.command == "search":
        results = store.search(args.slug, args.query)
        if not results:
            print("No matches found.")
            return 0
        for result in results:
            print(f"{result['number']}. {result['title']} [{result['status']}]")
            print(f"   {result['snippet']}")
        return 0
    if args.command == "add-chapter":
        chapter = store.add_chapter(args.slug, args.title, args.content, args.status)
        print(f"Added chapter {chapter.number}: {chapter.title}")
        return 0
    if args.command == "update-chapter":
        if args.content is not None and args.content_file is not None:
            raise StorageError("Use either --content or --content-file, not both.")
        content = args.content
        if args.content_file is not None:
            content = args.content_file.read_text(encoding="utf-8")
        chapter = store.update_chapter(
            args.slug,
            args.number,
            title=args.title,
            content=content,
            status=args.status,
        )
        print(f"Updated chapter {chapter.number}: {chapter.title}")
        return 0
    if args.command == "export":
        output = store.export_markdown(args.slug, args.output, args.template)
        print(f"Exported: {output}")
        return 0
    if args.command == "backup":
        output = store.backup_project(args.slug, args.output_dir)
        print(f"Backed up: {output}")
        return 0
    raise StorageError(f"Unknown command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except StorageError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
