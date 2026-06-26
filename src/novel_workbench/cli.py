from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import __version__
from .storage import STARTER_TEMPLATES, VALID_NOTE_KINDS, ProjectStore, StorageError


COMPLETION_COMMANDS = (
    "init",
    "list",
    "doctor",
    "sample",
    "starter",
    "create",
    "rename",
    "import-markdown",
    "show",
    "stats",
    "set-metadata",
    "set-target",
    "clear-target",
    "add-note",
    "list-notes",
    "update-note",
    "delete-note",
    "search",
    "add-chapter",
    "update-chapter",
    "move-chapter",
    "delete-chapter",
    "export",
    "backup",
    "completion",
)


def default_workspace() -> Path:
    configured = os.environ.get("NOVEL_WORKBENCH_HOME")
    return Path(configured).expanduser() if configured else Path.cwd() / "workspace"


def completion_script(shell: str) -> str:
    commands = " ".join(COMPLETION_COMMANDS)
    if shell == "bash":
        return f"""_novel_completion() {{
    local cur
    COMPREPLY=()
    cur="${{COMP_WORDS[COMP_CWORD]}}"
    if [[ ${{COMP_CWORD}} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "{commands}" -- "$cur") )
    fi
}}
complete -F _novel_completion novel
"""
    if shell == "zsh":
        zsh_commands = "\n    ".join(f"'{command}:novel {command}'" for command in COMPLETION_COMMANDS)
        return f"""#compdef novel
_novel() {{
  local -a commands
  commands=(
    {zsh_commands}
  )
  _describe 'command' commands
}}
_novel "$@"
"""
    if shell == "powershell":
        ps_commands = ", ".join(f"'{command}'" for command in COMPLETION_COMMANDS)
        return f"""Register-ArgumentCompleter -Native -CommandName novel -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)
    $commands = @({ps_commands})
    $commands |
        Where-Object {{ $_ -like "$wordToComplete*" }} |
        ForEach-Object {{ [System.Management.Automation.CompletionResult]::new($_, $_, 'ParameterValue', $_) }}
}}
"""
    raise StorageError(f"Unsupported shell: {shell}")


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

    starter = subparsers.add_parser("starter", help="Write an importable starter Markdown manuscript.")
    starter.add_argument("output", type=Path)
    starter.add_argument("--template", choices=sorted(STARTER_TEMPLATES), default="three-act", help="Starter structure.")
    starter.add_argument("--force", action="store_true", help="Overwrite the output file if it exists.")

    create = subparsers.add_parser("create", help="Create a project.")
    create.add_argument("slug", help="Lowercase project identifier, for example: first-novel.")
    create.add_argument("title", help="Project title.")
    create.add_argument("--synopsis", default="", help="Short project synopsis.")
    create.add_argument("--genre", default="", help="Project genre.")
    create.add_argument("--audience", default="", help="Intended audience.")

    rename = subparsers.add_parser("rename", help="Rename a project slug and optionally its title.")
    rename.add_argument("slug")
    rename.add_argument("new_slug")
    rename.add_argument("--title", help="New project title.")

    import_markdown = subparsers.add_parser("import-markdown", help="Create a project from a Markdown manuscript.")
    import_markdown.add_argument("slug")
    import_markdown.add_argument("input", type=Path)

    show = subparsers.add_parser("show", help="Show project details.")
    show.add_argument("slug")

    stats = subparsers.add_parser("stats", help="Show drafting progress for a project.")
    stats.add_argument("slug")

    set_metadata = subparsers.add_parser("set-metadata", help="Set project genre, audience, or revision notes.")
    set_metadata.add_argument("slug")
    set_metadata.add_argument("--genre")
    set_metadata.add_argument("--audience")
    set_metadata.add_argument("--revision-notes")
    set_metadata.add_argument("--revision-notes-file", type=Path)

    set_target = subparsers.add_parser("set-target", help="Set a project target word count.")
    set_target.add_argument("slug")
    set_target.add_argument("words", type=int)

    clear_target = subparsers.add_parser("clear-target", help="Clear a project target word count.")
    clear_target.add_argument("slug")

    add_note = subparsers.add_parser("add-note", help="Add a project note.")
    add_note.add_argument("slug")
    add_note.add_argument("title")
    add_note.add_argument("--content", default="", help="Note content.")
    add_note.add_argument("--content-file", type=Path)
    add_note.add_argument("--kind", choices=sorted(VALID_NOTE_KINDS), default="general", help="Note kind.")

    list_notes = subparsers.add_parser("list-notes", help="List project notes.")
    list_notes.add_argument("slug")
    list_notes.add_argument("--kind", choices=sorted(VALID_NOTE_KINDS), help="Filter by note kind.")

    update_note = subparsers.add_parser("update-note", help="Update a project note.")
    update_note.add_argument("slug")
    update_note.add_argument("id", type=int)
    update_note.add_argument("--title")
    update_note.add_argument("--content")
    update_note.add_argument("--content-file", type=Path)
    update_note.add_argument("--kind", choices=sorted(VALID_NOTE_KINDS))

    delete_note = subparsers.add_parser("delete-note", help="Delete a project note.")
    delete_note.add_argument("slug")
    delete_note.add_argument("id", type=int)

    search = subparsers.add_parser("search", help="Search chapters and project notes.")
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

    move_chapter = subparsers.add_parser("move-chapter", help="Move a chapter to a new number.")
    move_chapter.add_argument("slug")
    move_chapter.add_argument("number", type=int)
    move_chapter.add_argument("new_number", type=int)

    delete_chapter = subparsers.add_parser("delete-chapter", help="Delete a chapter and renumber the project.")
    delete_chapter.add_argument("slug")
    delete_chapter.add_argument("number", type=int)

    export = subparsers.add_parser("export", help="Export a project to Markdown.")
    export.add_argument("slug")
    export.add_argument("output", type=Path)
    export.add_argument("--template", default="default", help="default, frontmatter, or progress.")
    export.add_argument("--template-file", type=Path, help="Custom Markdown template file with named fields.")

    backup = subparsers.add_parser("backup", help="Copy a project JSON file to a backup directory.")
    backup.add_argument("slug")
    backup.add_argument("output_dir", type=Path)

    completion = subparsers.add_parser("completion", help="Print a shell completion script.")
    completion.add_argument("shell", choices=("bash", "zsh", "powershell"), help="Shell name.")

    return parser


def run(args: argparse.Namespace) -> int:
    if args.command == "completion":
        print(completion_script(args.shell), end="")
        return 0

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
    if args.command == "starter":
        output = store.write_starter_markdown(args.output, template=args.template, overwrite=args.force)
        print(f"Wrote starter manuscript: {output}")
        return 0
    if args.command == "create":
        project = store.create_project(args.slug, args.title, args.synopsis)
        if args.genre or args.audience:
            project = store.update_project_metadata(project.slug, genre=args.genre, audience=args.audience)
        print(f"Created project: {project.slug}")
        return 0
    if args.command == "rename":
        project = store.rename_project(args.slug, args.new_slug, args.title)
        print(f"Renamed project: {project.slug}")
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
        if project.genre:
            print(f"Genre: {project.genre}")
        if project.audience:
            print(f"Audience: {project.audience}")
        if project.revision_notes:
            print("Revision notes:")
            print(project.revision_notes)
        for chapter in sorted(project.chapters, key=lambda item: item.number):
            print(f"{chapter.number}. {chapter.title} [{chapter.status}]")
        return 0
    if args.command == "stats":
        stats = store.project_stats(args.slug)
        print(f"Chapters: {stats['chapters']}")
        print(f"Notes: {stats['notes']}")
        print(f"Words: {stats['words']}")
        if stats["target_words"] is not None:
            print(f"Target words: {stats['target_words']}")
            print(f"Remaining words: {stats['remaining_words']}")
            print(f"Progress: {stats['progress_percent']}%")
        if stats["average_chapter_words"] is not None:
            print(f"Average chapter words: {stats['average_chapter_words']}")
        print(f"Characters: {stats['characters']}")
        print(f"Draft: {stats['draft']} chapters / {stats['draft_words']} words")
        print(f"Revising: {stats['revising']} chapters / {stats['revising_words']} words")
        print(f"Done: {stats['done']} chapters / {stats['done_words']} words")
        return 0
    if args.command == "set-metadata":
        if args.revision_notes is not None and args.revision_notes_file is not None:
            raise StorageError("Use either --revision-notes or --revision-notes-file, not both.")
        revision_notes = args.revision_notes
        if args.revision_notes_file is not None:
            revision_notes = args.revision_notes_file.read_text(encoding="utf-8")
        project = store.update_project_metadata(
            args.slug,
            genre=args.genre,
            audience=args.audience,
            revision_notes=revision_notes,
        )
        print(f"Updated metadata for {project.slug}")
        return 0
    if args.command == "set-target":
        project = store.set_target_words(args.slug, args.words)
        print(f"Set target words for {project.slug}: {project.target_words}")
        return 0
    if args.command == "clear-target":
        project = store.set_target_words(args.slug, None)
        print(f"Cleared target words for {project.slug}")
        return 0
    if args.command == "add-note":
        if args.content and args.content_file is not None:
            raise StorageError("Use either --content or --content-file, not both.")
        content = args.content
        if args.content_file is not None:
            content = args.content_file.read_text(encoding="utf-8")
        note = store.add_note(args.slug, args.title, content, args.kind)
        print(f"Added note {note.id}: {note.title} [{note.kind}]")
        return 0
    if args.command == "list-notes":
        notes = store.list_notes(args.slug, args.kind)
        if not notes:
            print("No notes found.")
            return 0
        for note in notes:
            print(f"{note.id}. {note.title} [{note.kind}]")
            if note.content:
                print(f"   {note.content}")
        return 0
    if args.command == "update-note":
        if args.content is not None and args.content_file is not None:
            raise StorageError("Use either --content or --content-file, not both.")
        content = args.content
        if args.content_file is not None:
            content = args.content_file.read_text(encoding="utf-8")
        note = store.update_note(args.slug, args.id, title=args.title, content=content, kind=args.kind)
        print(f"Updated note {note.id}: {note.title} [{note.kind}]")
        return 0
    if args.command == "delete-note":
        note = store.delete_note(args.slug, args.id)
        print(f"Deleted note {note.id}: {note.title}")
        return 0
    if args.command == "search":
        results = store.search(args.slug, args.query)
        if not results:
            print("No matches found.")
            return 0
        for result in results:
            label = "Chapter" if result["type"] == "chapter" else "Note"
            print(f"{label} {result['number']}: {result['title']} [{result['status']}]")
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
    if args.command == "move-chapter":
        chapter = store.move_chapter(args.slug, args.number, args.new_number)
        print(f"Moved chapter {args.number} to {chapter.number}: {chapter.title}")
        return 0
    if args.command == "delete-chapter":
        chapter = store.delete_chapter(args.slug, args.number)
        print(f"Deleted chapter {args.number}: {chapter.title}")
        return 0
    if args.command == "export":
        if args.template_file is not None and args.template != "default":
            raise StorageError("Use either --template or --template-file, not both.")
        output = store.export_markdown(args.slug, args.output, args.template, args.template_file)
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
