from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .storage import (
    STARTER_TEMPLATES,
    VALID_NOTE_KINDS,
    ProjectStore,
    StorageError,
    board_lines,
    focus_lines,
    outline_lines,
    planning_lines,
    revision_lines,
)


COMPLETION_COMMANDS = (
    "init",
    "list",
    "dashboard",
    "export-dashboard",
    "doctor",
    "migrate",
    "sample",
    "starter",
    "create",
    "rename",
    "import-markdown",
    "show",
    "focus",
    "board",
    "outline",
    "plan",
    "revision",
    "stats",
    "set-metadata",
    "set-target",
    "clear-target",
    "set-deadline",
    "clear-deadline",
    "add-character",
    "add-location",
    "add-note",
    "list-notes",
    "update-note",
    "delete-note",
    "add-progress",
    "list-progress",
    "update-progress",
    "delete-progress",
    "search",
    "add-chapter",
    "update-chapter",
    "move-chapter",
    "delete-chapter",
    "add-scene",
    "list-scenes",
    "update-scene",
    "delete-scene",
    "export",
    "backup",
    "restore-backup",
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


def _read_text_option(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise StorageError(f"{label} file is not valid UTF-8: {path}") from exc
    except OSError as exc:
        raise StorageError(f"Could not read {label.lower()} file: {path} ({exc.strerror or exc})") from exc


def _structured_note_content(fields: list[tuple[str, str | None]], trailing_notes: str | None = None) -> str:
    lines: list[str] = []
    for label, value in fields:
        normalized = "" if value is None else value.strip()
        if normalized:
            lines.extend([f"## {label}", "", normalized, ""])
    if trailing_notes is not None and trailing_notes.strip():
        lines.extend(["## Notes", "", trailing_notes.strip(), ""])
    return "\n".join(lines).strip()


def _print_indented(content: str, prefix: str = "   ") -> None:
    for line in content.splitlines():
        print(f"{prefix}{line}" if line else "")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="novel", description="Manage a local novel writing workspace.")
    parser.add_argument("--workspace", type=Path, default=default_workspace(), help="Workspace directory.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Create the workspace directory.")
    subparsers.add_parser("list", help="List projects.")
    subparsers.add_parser("dashboard", help="Show a workspace progress dashboard.")
    export_dashboard = subparsers.add_parser("export-dashboard", help="Export the workspace dashboard to Markdown.")
    export_dashboard.add_argument("output", type=Path)
    subparsers.add_parser("doctor", help="Validate workspace project files.")
    migrate = subparsers.add_parser("migrate", help="Normalize project files to the current schema.")
    migrate.add_argument("--dry-run", action="store_true", help="Report projects that would change without writing files.")

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

    focus = subparsers.add_parser("focus", help="Show the next writing focus for a project.")
    focus.add_argument("slug")

    board = subparsers.add_parser("board", help="Show a chapter status board.")
    board.add_argument("slug")

    outline = subparsers.add_parser("outline", help="Show a structured project outline.")
    outline.add_argument("slug")

    plan = subparsers.add_parser("plan", help="Show a planning view with progress, chapters, scenes, and notes.")
    plan.add_argument("slug")

    revision = subparsers.add_parser("revision", help="Show a revision checklist for a project.")
    revision.add_argument("slug")

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

    set_deadline = subparsers.add_parser("set-deadline", help="Set a project target completion date.")
    set_deadline.add_argument("slug")
    set_deadline.add_argument("date", help="Target date in YYYY-MM-DD format.")

    clear_deadline = subparsers.add_parser("clear-deadline", help="Clear a project target completion date.")
    clear_deadline.add_argument("slug")

    add_character = subparsers.add_parser("add-character", help="Add a structured character note.")
    add_character.add_argument("slug")
    add_character.add_argument("name")
    add_character.add_argument("--role", help="Story role, such as protagonist, antagonist, mentor, or suspect.")
    add_character.add_argument("--goal", help="What the character wants.")
    add_character.add_argument("--conflict", help="What blocks or pressures the character.")
    add_character.add_argument("--arc", help="How the character changes.")
    add_character.add_argument("--notes", help="Additional character notes.")
    add_character.add_argument("--notes-file", type=Path, help="Read additional notes from a UTF-8 text file.")

    add_location = subparsers.add_parser("add-location", help="Add a structured location note.")
    add_location.add_argument("slug")
    add_location.add_argument("name")
    add_location.add_argument("--description", help="What the place looks, feels, or functions like.")
    add_location.add_argument("--mood", help="Atmosphere or emotional tone.")
    add_location.add_argument("--importance", help="Why the location matters to the story.")
    add_location.add_argument("--notes", help="Additional location notes.")
    add_location.add_argument("--notes-file", type=Path, help="Read additional notes from a UTF-8 text file.")

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

    add_progress = subparsers.add_parser("add-progress", help="Log words written on a date.")
    add_progress.add_argument("slug")
    add_progress.add_argument("words", type=int)
    add_progress.add_argument("--date", help="Writing date in YYYY-MM-DD format. Defaults to today.")
    add_progress.add_argument("--note", default="", help="Optional progress note.")

    list_progress = subparsers.add_parser("list-progress", help="List writing progress entries.")
    list_progress.add_argument("slug")

    update_progress = subparsers.add_parser("update-progress", help="Update a writing progress entry.")
    update_progress.add_argument("slug")
    update_progress.add_argument("id", type=int)
    update_progress.add_argument("--date", help="Writing date in YYYY-MM-DD format.")
    update_progress.add_argument("--words", type=int, help="Words written.")
    update_progress.add_argument("--note", help="Progress note.")

    delete_progress = subparsers.add_parser("delete-progress", help="Delete a writing progress entry.")
    delete_progress.add_argument("slug")
    delete_progress.add_argument("id", type=int)

    search = subparsers.add_parser("search", help="Search chapters and project notes.")
    search.add_argument("slug")
    search.add_argument("query")

    add_chapter = subparsers.add_parser("add-chapter", help="Append a chapter.")
    add_chapter.add_argument("slug")
    add_chapter.add_argument("title")
    add_chapter.add_argument("--content", default="", help="Initial chapter content.")
    add_chapter.add_argument("--summary", default="", help="Short chapter outline summary.")
    add_chapter.add_argument("--summary-file", type=Path, help="Read the chapter summary from a UTF-8 text file.")
    add_chapter.add_argument("--status", default="draft", help="draft, revising, or done.")

    update_chapter = subparsers.add_parser("update-chapter", help="Update an existing chapter.")
    update_chapter.add_argument("slug")
    update_chapter.add_argument("number", type=int)
    update_chapter.add_argument("--title")
    update_chapter.add_argument("--content")
    update_chapter.add_argument("--content-file", type=Path)
    update_chapter.add_argument("--summary")
    update_chapter.add_argument("--summary-file", type=Path)
    update_chapter.add_argument("--status")

    move_chapter = subparsers.add_parser("move-chapter", help="Move a chapter to a new number.")
    move_chapter.add_argument("slug")
    move_chapter.add_argument("number", type=int)
    move_chapter.add_argument("new_number", type=int)

    delete_chapter = subparsers.add_parser("delete-chapter", help="Delete a chapter and renumber the project.")
    delete_chapter.add_argument("slug")
    delete_chapter.add_argument("number", type=int)

    add_scene = subparsers.add_parser("add-scene", help="Add a scene outline to a chapter.")
    add_scene.add_argument("slug")
    add_scene.add_argument("chapter", type=int)
    add_scene.add_argument("title")
    add_scene.add_argument("--summary", default="", help="Short scene summary.")
    add_scene.add_argument("--summary-file", type=Path, help="Read the scene summary from a UTF-8 text file.")
    add_scene.add_argument("--status", default="draft", help="draft, revising, or done.")

    list_scenes = subparsers.add_parser("list-scenes", help="List scene outlines for a chapter.")
    list_scenes.add_argument("slug")
    list_scenes.add_argument("chapter", type=int)

    update_scene = subparsers.add_parser("update-scene", help="Update a scene outline.")
    update_scene.add_argument("slug")
    update_scene.add_argument("chapter", type=int)
    update_scene.add_argument("scene", type=int)
    update_scene.add_argument("--title")
    update_scene.add_argument("--summary")
    update_scene.add_argument("--summary-file", type=Path)
    update_scene.add_argument("--status")

    delete_scene = subparsers.add_parser("delete-scene", help="Delete a scene outline and renumber the chapter scenes.")
    delete_scene.add_argument("slug")
    delete_scene.add_argument("chapter", type=int)
    delete_scene.add_argument("scene", type=int)

    export = subparsers.add_parser("export", help="Export a project to Markdown.")
    export.add_argument("slug")
    export.add_argument("output", type=Path)
    export.add_argument("--template", default="default", help="board, default, focus, frontmatter, outline, progress, or revision.")
    export.add_argument("--template-file", type=Path, help="Custom Markdown template file with named fields.")

    backup = subparsers.add_parser("backup", help="Copy a project JSON file to a backup directory.")
    backup.add_argument("slug")
    backup.add_argument("output_dir", type=Path)

    restore_backup = subparsers.add_parser("restore-backup", help="Restore a project JSON file from a backup.")
    restore_backup.add_argument("backup", type=Path)
    restore_backup.add_argument("--force", action="store_true", help="Overwrite an existing project with the same slug.")

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
    if args.command == "dashboard":
        rows = store.workspace_dashboard()
        if not rows:
            print("No projects found.")
            return 0
        print("Slug\tTitle\tChapters\tWords\tLogged\tStreak\tTarget\tProgress\tUpdated")
        for row in rows:
            target = "-" if row["target_words"] is None else str(row["target_words"])
            progress = "-" if row["progress_percent"] is None else f"{row['progress_percent']}%"
            print(
                f"{row['slug']}\t{row['title']}\t{row['chapters']}\t{row['words']}\t"
                f"{row['logged_words']}\t{row['current_streak_days']}\t{target}\t{progress}\t{row['updated_at']}"
            )
        return 0
    if args.command == "export-dashboard":
        output = store.export_dashboard(args.output)
        print(f"Exported dashboard: {output}")
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
    if args.command == "migrate":
        report = store.migrate_workspace(dry_run=args.dry_run)
        print(f"Checked: {report['checked']}")
        print(f"Migrated: {report['migrated']}")
        projects = report["projects"]
        if not isinstance(projects, list):
            raise StorageError("Invalid migration report.")
        for slug in projects:
            action = "Would migrate" if args.dry_run else "Migrated"
            print(f"- {action}: {slug}")
        return 0
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
            if chapter.summary:
                print(f"   {chapter.summary}")
        return 0
    if args.command == "focus":
        project = store.get_project(args.slug)
        print("\n".join(focus_lines(project)))
        return 0
    if args.command == "board":
        project = store.get_project(args.slug)
        print("\n".join(board_lines(project)))
        return 0
    if args.command == "outline":
        project = store.get_project(args.slug)
        print("\n".join(outline_lines(project)))
        return 0
    if args.command == "plan":
        project = store.get_project(args.slug)
        print("\n".join(planning_lines(project)))
        return 0
    if args.command == "revision":
        project = store.get_project(args.slug)
        print("\n".join(revision_lines(project)))
        return 0
    if args.command == "stats":
        stats = store.project_stats(args.slug)
        print(f"Chapters: {stats['chapters']}")
        print(f"Notes: {stats['notes']}")
        print(f"Words: {stats['words']}")
        print(f"Logged words: {stats['logged_words']}")
        print(f"Writing days: {stats['writing_days']}")
        print(f"Current streak: {stats['current_streak_days']} days")
        print(f"Longest streak: {stats['longest_streak_days']} days")
        if stats["average_logged_words"] is not None:
            print(f"Average logged words: {stats['average_logged_words']}")
        if stats["best_day_words"] is not None:
            print(f"Best writing day: {stats['best_day_words']} words")
        if stats["target_words"] is not None:
            print(f"Target words: {stats['target_words']}")
            print(f"Remaining words: {stats['remaining_words']}")
            print(f"Progress: {stats['progress_percent']}%")
        if stats["target_date"] is not None:
            print(f"Target date: {stats['target_date']}")
            print(f"Days until target date: {stats['days_until_target_date']}")
        if stats["required_daily_words"] is not None:
            print(f"Required daily words: {stats['required_daily_words']}")
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
            revision_notes = _read_text_option(args.revision_notes_file, "Revision notes")
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
    if args.command == "set-deadline":
        project = store.set_target_date(args.slug, args.date)
        print(f"Set target date for {project.slug}: {project.target_date}")
        return 0
    if args.command == "clear-deadline":
        project = store.set_target_date(args.slug, None)
        print(f"Cleared target date for {project.slug}")
        return 0
    if args.command == "add-character":
        if args.notes is not None and args.notes_file is not None:
            raise StorageError("Use either --notes or --notes-file, not both.")
        notes = args.notes
        if args.notes_file is not None:
            notes = _read_text_option(args.notes_file, "Character notes")
        content = _structured_note_content(
            [
                ("Role", args.role),
                ("Goal", args.goal),
                ("Conflict", args.conflict),
                ("Arc", args.arc),
            ],
            notes,
        )
        note = store.add_note(args.slug, args.name, content, "character")
        print(f"Added character {note.id}: {note.title}")
        return 0
    if args.command == "add-location":
        if args.notes is not None and args.notes_file is not None:
            raise StorageError("Use either --notes or --notes-file, not both.")
        notes = args.notes
        if args.notes_file is not None:
            notes = _read_text_option(args.notes_file, "Location notes")
        content = _structured_note_content(
            [
                ("Description", args.description),
                ("Mood", args.mood),
                ("Importance", args.importance),
            ],
            notes,
        )
        note = store.add_note(args.slug, args.name, content, "location")
        print(f"Added location {note.id}: {note.title}")
        return 0
    if args.command == "add-note":
        if args.content and args.content_file is not None:
            raise StorageError("Use either --content or --content-file, not both.")
        content = args.content
        if args.content_file is not None:
            content = _read_text_option(args.content_file, "Note content")
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
                _print_indented(note.content)
        return 0
    if args.command == "update-note":
        if args.content is not None and args.content_file is not None:
            raise StorageError("Use either --content or --content-file, not both.")
        content = args.content
        if args.content_file is not None:
            content = _read_text_option(args.content_file, "Note content")
        note = store.update_note(args.slug, args.id, title=args.title, content=content, kind=args.kind)
        print(f"Updated note {note.id}: {note.title} [{note.kind}]")
        return 0
    if args.command == "delete-note":
        note = store.delete_note(args.slug, args.id)
        print(f"Deleted note {note.id}: {note.title}")
        return 0
    if args.command == "add-progress":
        entry_date = args.date or date.today().isoformat()
        entry = store.add_progress(args.slug, args.words, entry_date, args.note)
        print(f"Logged progress {entry.id}: {entry.date} +{entry.words} words")
        return 0
    if args.command == "list-progress":
        entries = store.list_progress(args.slug)
        if not entries:
            print("No progress entries found.")
            return 0
        for entry in entries:
            line = f"{entry.id}. {entry.date}: +{entry.words} words"
            if entry.note:
                line = f"{line} - {entry.note}"
            print(line)
        return 0
    if args.command == "update-progress":
        entry = store.update_progress(args.slug, args.id, entry_date=args.date, words=args.words, note=args.note)
        print(f"Updated progress {entry.id}: {entry.date} +{entry.words} words")
        return 0
    if args.command == "delete-progress":
        entry = store.delete_progress(args.slug, args.id)
        print(f"Deleted progress {entry.id}: {entry.date} +{entry.words} words")
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
        if args.summary and args.summary_file is not None:
            raise StorageError("Use either --summary or --summary-file, not both.")
        summary = args.summary
        if args.summary_file is not None:
            summary = _read_text_option(args.summary_file, "Chapter summary")
        chapter = store.add_chapter(args.slug, args.title, args.content, args.status, summary)
        print(f"Added chapter {chapter.number}: {chapter.title}")
        return 0
    if args.command == "update-chapter":
        if args.content is not None and args.content_file is not None:
            raise StorageError("Use either --content or --content-file, not both.")
        if args.summary is not None and args.summary_file is not None:
            raise StorageError("Use either --summary or --summary-file, not both.")
        content = args.content
        if args.content_file is not None:
            content = _read_text_option(args.content_file, "Chapter content")
        summary = args.summary
        if args.summary_file is not None:
            summary = _read_text_option(args.summary_file, "Chapter summary")
        chapter = store.update_chapter(
            args.slug,
            args.number,
            title=args.title,
            content=content,
            summary=summary,
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
    if args.command == "add-scene":
        if args.summary and args.summary_file is not None:
            raise StorageError("Use either --summary or --summary-file, not both.")
        summary = args.summary
        if args.summary_file is not None:
            summary = _read_text_option(args.summary_file, "Scene summary")
        scene = store.add_scene(args.slug, args.chapter, args.title, summary, args.status)
        print(f"Added scene {args.chapter}.{scene.number}: {scene.title}")
        return 0
    if args.command == "list-scenes":
        scenes = store.list_scenes(args.slug, args.chapter)
        if not scenes:
            print("No scenes found.")
            return 0
        for scene in scenes:
            print(f"{args.chapter}.{scene.number}. {scene.title} [{scene.status}]")
            if scene.summary:
                print(f"   {scene.summary}")
        return 0
    if args.command == "update-scene":
        if args.summary is not None and args.summary_file is not None:
            raise StorageError("Use either --summary or --summary-file, not both.")
        summary = args.summary
        if args.summary_file is not None:
            summary = _read_text_option(args.summary_file, "Scene summary")
        scene = store.update_scene(
            args.slug,
            args.chapter,
            args.scene,
            title=args.title,
            summary=summary,
            status=args.status,
        )
        print(f"Updated scene {args.chapter}.{scene.number}: {scene.title}")
        return 0
    if args.command == "delete-scene":
        scene = store.delete_scene(args.slug, args.chapter, args.scene)
        print(f"Deleted scene {args.chapter}.{args.scene}: {scene.title}")
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
    if args.command == "restore-backup":
        project = store.restore_backup(args.backup, overwrite=args.force)
        print(f"Restored project: {project.slug}")
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
