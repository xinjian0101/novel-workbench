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

## `novel dashboard`

Show a workspace-level progress table for every project.

```powershell
novel --workspace workspace dashboard
```

The table includes slug, title, chapter count, manuscript words, logged words, current writing streak, target words, target progress, and last updated timestamp. Use this command to choose what needs attention before opening a specific project with `plan` or `stats`.

## `novel export-dashboard`

Export the workspace progress dashboard to Markdown.

```powershell
novel --workspace workspace export-dashboard exports/workspace-dashboard.md
```

The report uses the same project summary fields as `dashboard`, but writes a Markdown table that can be committed, shared, or attached to a planning note.

## `novel doctor`

Validate project files in the workspace.

```powershell
novel --workspace workspace doctor
```

The command exits with `0` when the workspace is healthy and `2` when project files are invalid.

For known problems such as JSON syntax errors, invalid UTF-8, missing required fields, invalid values, slug/file mismatches, and non-sequential chapter numbers, the output includes a concise repair hint.

## `novel migrate`

Normalize project files to the current schema.

```powershell
novel --workspace workspace migrate --dry-run
novel --workspace workspace migrate
```

Use `--dry-run` to see which projects would change. A real migration validates each project, writes a pre-migration safety snapshot under `workspace/backups/`, then rewrites the JSON with the current schema fields and `schema_version`.

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

## `novel focus`

Show the next writing focus for a project.

```powershell
novel --workspace workspace focus moon-archive
novel --workspace workspace export moon-archive exports/moon-archive-focus.md --template focus
```

The focus brief includes current progress, target pace when configured, the next unfinished chapter, unfinished scenes in that chapter, recent writing log entries, and revision notes. Use it as the first command before a writing session.

## `novel handoff`

Show an AI/editor handoff brief for a project.

```powershell
novel --workspace workspace handoff moon-archive
novel --workspace workspace export moon-archive exports/moon-archive-handoff.md --template handoff
```

The handoff brief includes a project snapshot, next action, continuity notes, chapter state, recent progress, and a continuation prompt. Use it when moving from the CLI into an AI assistant, editor, or critique workflow.

## `novel context`

Print a machine-readable AI/editor project context JSON document.

```powershell
novel --workspace workspace context moon-archive
```

The context document includes the full project JSON, calculated stats, the next recommended action, chapter state with word counts and scene labels, recent progress, and continuity note previews. Use it when an editor, script, or AI workflow needs structured state instead of a human-readable Markdown handoff.

## `novel momentum`

Show writing momentum and weekly progress for a project.

```powershell
novel --workspace workspace momentum moon-archive
novel --workspace workspace export moon-archive exports/moon-archive-momentum.md --template momentum
```

The report includes manuscript words, logged words, writing days, streaks, target progress, required daily pace when configured, weekly writing totals, and the seven most recent writing log entries. Use it to check whether recent drafting output is keeping pace with the project target.

## `novel board`

Show a chapter status board grouped by draft, revising, and done.

```powershell
novel --workspace workspace board moon-archive
novel --workspace workspace export moon-archive exports/moon-archive-board.md --template board
```

Each chapter row includes word count, summary, and unfinished scene follow-ups when present. Use it when deciding what to draft, revise, or mark complete next.

## `novel outline`

Show a structured project outline with synopsis, metadata, chapter statuses, and chapter summaries.

```powershell
novel --workspace workspace outline moon-archive
```

## `novel plan`

Show a richer planning view with project positioning, progress targets, chapters, scenes, grouped notes, and writing log entries.

```powershell
novel --workspace workspace plan moon-archive
```

Use this when reviewing a project before drafting or revision. `outline` stays focused on chapter structure; `plan` includes the surrounding planning context.

## `novel review`

Show manuscript readiness findings.

```powershell
novel --workspace workspace review moon-archive
novel --workspace workspace export moon-archive exports/moon-archive-review.md --template review
```

The report flags author-facing gaps such as missing synopsis, missing genre or audience, missing target word count, empty chapters, chapters without summaries, unfinished chapters, unfinished scenes, and missing writing logs. Use `doctor` for project-file health and `review` for manuscript readiness.

## `novel revision`

Show a project revision checklist.

```powershell
novel --workspace workspace revision moon-archive
novel --workspace workspace export moon-archive exports/moon-archive-revision.md --template revision
```

The checklist includes a project snapshot, revision notes, chapter checkboxes, unfinished scene follow-ups, and planning notes to review. Use it when moving from drafting into a focused edit pass.

## `novel stats`

Show chapter, note, word, writing log, writing streak, target, deadline, required daily writing pace, average chapter, character, and status counts.

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

## `novel set-deadline`

Set a project target completion date.

```powershell
novel --workspace workspace set-deadline moon-archive 2026-12-31
```

Dates use `YYYY-MM-DD`. When the project also has a target word count, `novel stats` reports the required daily words to reach the target by the deadline.

## `novel clear-deadline`

Clear a project target completion date.

```powershell
novel --workspace workspace clear-deadline moon-archive
```

## `novel add-character`

Add a structured character note.

```powershell
novel --workspace workspace add-character moon-archive "Ada" --role protagonist --goal "Decode the archive signal."
novel --workspace workspace add-character moon-archive "Ada" --conflict "The crew distrusts her." --arc "Learns to ask for help."
novel --workspace workspace add-character moon-archive "Ada" --notes-file notes/ada.md
```

The command stores the entry as a `character` note, so it appears in `list-notes --kind character`, search results, and the `plan` view. Use either `--notes` or `--notes-file`, not both.

## `novel add-location`

Add a structured location note.

```powershell
novel --workspace workspace add-location moon-archive "Archive Vault" --description "A sealed records chamber below the city."
novel --workspace workspace add-location moon-archive "Archive Vault" --mood "quiet dread" --importance "It hides the first relay."
novel --workspace workspace add-location moon-archive "Archive Vault" --notes-file notes/archive-vault.md
```

The command stores the entry as a `location` note, so it appears in `list-notes --kind location`, search results, and the `plan` view. Use either `--notes` or `--notes-file`, not both.

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

## `novel update-progress`

Correct a writing progress entry.

```powershell
novel --workspace workspace update-progress moon-archive 1 --words 1250
novel --workspace workspace update-progress moon-archive 1 --date 2026-06-27 --note "Included evening revisions."
```

Provide at least one of `--date`, `--words`, or `--note`. Dates use `YYYY-MM-DD`; word counts must be greater than zero.

## `novel delete-progress`

Delete a writing progress entry.

```powershell
novel --workspace workspace delete-progress moon-archive 1
```

The command writes a pre-delete safety snapshot under `workspace/backups/` before removing the progress entry.

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
novel --workspace workspace export moon-archive exports/moon-archive-board.md --template board
novel --workspace workspace export moon-archive exports/moon-archive-focus.md --template focus
novel --workspace workspace export moon-archive exports/moon-archive-handoff.md --template handoff
novel --workspace workspace export moon-archive exports/moon-archive-momentum.md --template momentum
novel --workspace workspace export moon-archive exports/moon-archive-outline.md --template outline
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
novel --workspace workspace export moon-archive exports/moon-archive-review.md --template review
novel --workspace workspace export moon-archive exports/moon-archive-revision.md --template revision
```

Templates:

- `default`: plain manuscript Markdown.
- `board`: shareable status board grouped by chapter status, with unfinished scene follow-ups.
- `focus`: shareable writing-session brief with next chapter, target pace, and recent progress.
- `frontmatter`: YAML front matter followed by the default Markdown body.
- `handoff`: shareable AI/editor handoff brief with project context, next action, continuity notes, and a continuation prompt.
- `momentum`: shareable writing momentum report with target pace, weekly totals, and recent progress entries.
- `outline`: shareable outline document with synopsis, metadata, chapter summaries, and scene beats.
- `progress`: shareable project progress report with overview, writing log totals, streaks, target deadline pace, remaining words, status word counts, a chapter table, and progress log entries.
- `review`: shareable manuscript readiness report with findings and strengths.
- `revision`: shareable revision checklist with project notes, chapter checkboxes, and unfinished scene follow-ups.

Custom template files use Python-style named fields. Supported fields are:

`title`, `slug`, `synopsis`, `genre`, `audience`, `revision_notes`, `target_words`, `target_date`, `words`, `logged_words`, `writing_days`, `current_streak_days`, `longest_streak_days`, `remaining_words`, `progress_percent`, `days_until_target_date`, `required_daily_words`, `average_chapter_words`, `average_logged_words`, `best_day_words`, `chapters_markdown`, `focus_brief`, `handoff_brief`, `momentum_report`, `status_board`, `chapter_table`, `status_summary`, `progress_log`, `review_report`, and `revision_checklist`.

Use either `--template` or `--template-file`, not both.
Files passed with `--template-file` must be readable UTF-8 text.

## `novel export-context`

Export a machine-readable AI/editor project context JSON document.

```powershell
novel --workspace workspace export-context moon-archive exports/moon-archive-context.json
```

The exported file uses the same payload as `novel context`, with `format` set to `novel-workbench-project-context` and `format_version` set to `1`.

## `novel export-site`

Export a static HTML project site.

```powershell
novel --workspace workspace export-site moon-archive exports/moon-archive-site
```

The command writes `index.html`, `manuscript.html`, and `context.json`. The index page summarizes project metadata, progress, the next action, chapters, notes, and recent writing. The manuscript page provides a clean reading view. The JSON file matches `novel context`, which makes the site directory useful for GitHub Pages, local review, or AI/editor automation.

## `novel export-pack`

Export every standard project report to one directory.

```powershell
novel --workspace workspace export-pack moon-archive exports/moon-archive-pack
```

The command writes the plain manuscript, YAML-frontmatter manuscript, focus brief, handoff brief, momentum report, status board, outline, progress report, readiness review, and revision checklist. File names use the project slug, for example `moon-archive.md`, `moon-archive-handoff.md`, and `moon-archive-revision.md`.

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
