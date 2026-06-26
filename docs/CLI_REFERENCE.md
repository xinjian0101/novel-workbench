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

For known problems such as corrupt JSON, slug/file mismatches, and non-sequential chapter numbers, the output includes a concise repair hint.

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
```

## `novel rename`

Rename a project slug and optionally update its title.

```powershell
novel --workspace workspace rename first-novel second-novel
novel --workspace workspace rename first-novel second-novel --title "Second Novel"
```

The command rewrites the project JSON under the new slug, preserves chapters and progress metadata, and refuses to overwrite an existing project.

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

## `novel stats`

Show chapter, note, word, target, progress, character, and status counts.

```powershell
novel --workspace workspace stats moon-archive
```

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

## `novel list-notes`

List project notes, optionally filtered by kind.

```powershell
novel --workspace workspace list-notes moon-archive
novel --workspace workspace list-notes moon-archive --kind character
```

## `novel delete-note`

Delete a project note by id.

```powershell
novel --workspace workspace delete-note moon-archive 1
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
```

## `novel update-chapter`

Update an existing chapter.

```powershell
novel --workspace workspace update-chapter moon-archive 1 --status revising
novel --workspace workspace update-chapter moon-archive 1 --content-file chapter-1.md
```

Use either `--content` or `--content-file`, not both.

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

The command removes the selected chapter and closes numbering gaps.

## `novel export`

Export a project to Markdown.

```powershell
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
```

Templates:

- `default`: plain manuscript Markdown.
- `frontmatter`: YAML front matter followed by the default Markdown body.
- `progress`: shareable project progress report with overview, status counts, and a chapter table.

## `novel backup`

Copy the project JSON file to a backup directory.

```powershell
novel --workspace workspace backup moon-archive backups
```
