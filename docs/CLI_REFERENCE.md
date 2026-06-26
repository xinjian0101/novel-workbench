# CLI Reference

All commands accept `--workspace <dir>`. If omitted, Novel Workbench uses `NOVEL_WORKBENCH_HOME`, then `./workspace`.

## `novel init`

Create the workspace directory structure.

```powershell
novel --workspace workspace init
```

## `novel list`

List projects in the workspace.

```powershell
novel --workspace workspace list
```

## `novel doctor`

Validate project files in the workspace.

```powershell
novel --workspace workspace doctor
```

The command exits with `0` when the workspace is healthy and `2` when project files are invalid.

For known problems such as JSON syntax errors, invalid UTF-8, missing required fields, invalid values, slug/file mismatches, and non-sequential chapter numbers, the output includes a concise repair hint.

## `novel completion`

Print a completion script for bash, zsh, or PowerShell.

```powershell
novel completion powershell
novel completion bash
novel completion zsh
```

See [SHELL_COMPLETION.md](SHELL_COMPLETION.md) for setup steps and the current completion scope.

## `novel sample`

Create a ready-to-explore sample project.

```powershell
novel --workspace workspace sample
novel --workspace workspace sample --slug my-demo
```

## `novel starter`

Write an importable Markdown manuscript template.

```powershell
novel --workspace workspace starter drafts/working-title.md
novel --workspace workspace starter drafts/working-title.md --template mystery
novel --workspace workspace starter drafts/working-title.md --force
novel --workspace workspace import-markdown working-title drafts/working-title.md
```

The generated file starts with a project title, synopsis prompt, and three chapter headings that match the `import-markdown` format.

Templates:

- `three-act`: opening image, inciting incident, and first choice. This is the default.
- `hero-journey`: ordinary world, call to adventure, and crossing the threshold.
- `mystery`: the body, first suspect, and false pattern.

## `novel create`

Create an empty project.

```powershell
novel --workspace workspace create first-novel "First Novel" --synopsis "A concise premise."
novel --workspace workspace create moon-archive "Moon Archive" --genre "science fiction" --audience adult
```

## `novel rename`

Rename a project slug and optionally update its title.

```powershell
novel --workspace workspace rename first-novel second-novel
novel --workspace workspace rename first-novel second-novel --title "Second Novel"
```

The command writes a pre-rename safety snapshot under `workspace/backups/`, rewrites the project JSON under the new slug, preserves chapters and progress metadata, and refuses to overwrite an existing project.

## `novel import-markdown`

Create a project from a Markdown manuscript.

```powershell
novel --workspace workspace import-markdown moon-archive manuscript.md
```

Expected input format:

```markdown
# Moon Archive

A historian finds a city under the lunar dust.

## Chapter 1: Signal

The first signal arrived.
```

## `novel show`

Show project metadata and chapter outline.

```powershell
novel --workspace workspace show moon-archive
```

## `novel outline`

Show a structured project outline with synopsis, metadata, chapter statuses, and chapter summaries.

```powershell
novel --workspace workspace outline moon-archive
```

## `novel stats`

Show chapter, note, word, writing log, target, remaining word, average chapter, character, and status counts.

```powershell
novel --workspace workspace stats moon-archive
```

## `novel set-metadata`

Set optional project positioning and revision metadata.

```powershell
novel --workspace workspace set-metadata moon-archive --genre "science fiction"
novel --workspace workspace set-metadata moon-archive --audience adult --revision-notes "Tighten the midpoint."
novel --workspace workspace set-metadata moon-archive --revision-notes-file notes/revision.md
```

Use either `--revision-notes` or `--revision-notes-file`, not both. Provide at least one metadata field.
Files passed with `--revision-notes-file` must be readable UTF-8 text.

## `novel set-target`

Set a project target word count.

```powershell
novel --workspace workspace set-target moon-archive 80000
```

## `novel clear-target`

Clear a project target word count.

```powershell
novel --workspace workspace clear-target moon-archive
```

## `novel add-note`

Add a planning note to a project.

```powershell
novel --workspace workspace add-note moon-archive "Ada" --kind character --content "Engineer protagonist."
novel --workspace workspace add-note moon-archive "Research" --kind research --content-file notes/research.md
```

Kinds:

- `general`
- `character`
- `location`
- `plot`
- `research`

Use either `--content` or `--content-file`, not both.
Files passed with `--content-file` must be readable UTF-8 text.

## `novel list-notes`

List project notes, optionally filtered by kind.

```powershell
novel --workspace workspace list-notes moon-archive
novel --workspace workspace list-notes moon-archive --kind character
```

## `novel update-note`

Update a project note title, kind, or content.

```powershell
novel --workspace workspace update-note moon-archive 1 --title "Ada Byron"
novel --workspace workspace update-note moon-archive 1 --kind research --content-file notes/research.md
```

Use either `--content` or `--content-file`, not both. Provide at least one field to update.
Files passed with `--content-file` must be readable UTF-8 text.

## `novel delete-note`

Delete a project note by id.

```powershell
novel --workspace workspace delete-note moon-archive 1
```

The command writes a pre-delete safety snapshot under `workspace/backups/` before removing the note.

## `novel add-progress`

Log words written on a specific date.

```powershell
novel --workspace workspace add-progress moon-archive 1200
novel --workspace workspace add-progress moon-archive 1200 --date 2026-06-26 --note "Drafted the descent sequence."
```

Dates use `YYYY-MM-DD`. If `--date` is omitted, the command uses the current local date.

## `novel list-progress`

List writing progress entries sorted by date.

```powershell
novel --workspace workspace list-progress moon-archive
```

## `novel search`

Search chapter titles, manuscript content, note titles, note content, and note kinds.

```powershell
novel --workspace workspace search moon-archive signal
```

## `novel add-chapter`

Append a chapter.

```powershell
novel --workspace workspace add-chapter moon-archive "Signal" --content "The first signal arrived."
novel --workspace workspace add-chapter moon-archive "Signal" --summary "The first signal disrupts the archive shift."
novel --workspace workspace add-chapter moon-archive "Signal" --summary-file outlines/signal.md
```

Use either `--summary` or `--summary-file`, not both. Files passed with `--summary-file` must be readable UTF-8 text.

## `novel update-chapter`

Update an existing chapter.

```powershell
novel --workspace workspace update-chapter moon-archive 1 --status revising
novel --workspace workspace update-chapter moon-archive 1 --content-file chapter-1.md
novel --workspace workspace update-chapter moon-archive 1 --summary "The opening clue now points below the city."
```

Use either `--content` or `--content-file`, not both.
Files passed with `--content-file` must be readable UTF-8 text.
Use either `--summary` or `--summary-file`, not both.
Files passed with `--summary-file` must be readable UTF-8 text.

## `novel move-chapter`

Move a chapter to a new position and renumber the project.

```powershell
novel --workspace workspace move-chapter moon-archive 2 1
```

The command preserves chapter content and status, then rewrites chapter numbers so they stay sequential.

## `novel delete-chapter`

Delete a chapter and renumber the remaining chapters.

```powershell
novel --workspace workspace delete-chapter moon-archive 2
```

The command writes a pre-delete safety snapshot under `workspace/backups/`, removes the selected chapter, and closes numbering gaps.

## `novel add-scene`

Add a scene outline to a chapter.

```powershell
novel --workspace workspace add-scene moon-archive 1 "Signal discovered"
novel --workspace workspace add-scene moon-archive 1 "Signal discovered" --summary "The crew finds the first active relay."
novel --workspace workspace add-scene moon-archive 1 "Signal discovered" --summary-file scenes/signal.md --status revising
```

Use either `--summary` or `--summary-file`, not both. Files passed with `--summary-file` must be readable UTF-8 text.

## `novel list-scenes`

List scene outlines for a chapter.

```powershell
novel --workspace workspace list-scenes moon-archive 1
```

## `novel update-scene`

Update a scene title, summary, or status.

```powershell
novel --workspace workspace update-scene moon-archive 1 1 --title "Signal decoded"
novel --workspace workspace update-scene moon-archive 1 1 --summary "The clue points below the archive."
novel --workspace workspace update-scene moon-archive 1 1 --status done
```

Use either `--summary` or `--summary-file`, not both. Provide at least one field to update.

## `novel delete-scene`

Delete a scene outline and renumber the remaining scenes in that chapter.

```powershell
novel --workspace workspace delete-scene moon-archive 1 2
```

The command writes a pre-delete safety snapshot under `workspace/backups/`, removes the selected scene, and closes scene numbering gaps inside the chapter.

## `novel export`

Export a project to Markdown.

```powershell
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-brief.md --template-file templates/brief.md
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
```

Templates:

- `default`: plain manuscript Markdown.
- `frontmatter`: YAML front matter followed by the default Markdown body.
- `progress`: shareable project progress report with overview, writing log totals, remaining words, status word counts, a chapter table, and progress log entries.

Custom template files use Python-style named fields. Supported fields are:

`title`, `slug`, `synopsis`, `genre`, `audience`, `revision_notes`, `target_words`, `words`, `logged_words`, `writing_days`, `remaining_words`, `progress_percent`, `average_chapter_words`, `average_logged_words`, `best_day_words`, `chapters_markdown`, `chapter_table`, `status_summary`, and `progress_log`.

Use either `--template` or `--template-file`, not both.
Files passed with `--template-file` must be readable UTF-8 text.

## `novel backup`

Copy the project JSON file to a backup directory.

```powershell
novel --workspace workspace backup moon-archive backups
```

Rename, chapter deletion, and note deletion also create automatic safety snapshots under `workspace/backups/`. Use `backup` when you want an explicit copy in another directory.

## `novel restore-backup`

Restore a project JSON file from a backup.

```powershell
novel --workspace workspace restore-backup backups/moon-archive-20260626T120000000000Z.json
novel --workspace workspace restore-backup backups/moon-archive-20260626T120000000000Z.json --force
```

The command validates the backup file before writing it into `workspace/projects/`. If a project with the same slug already exists, the command refuses to overwrite it unless `--force` is passed. Forced restores create a pre-restore safety snapshot under `workspace/backups/`.
