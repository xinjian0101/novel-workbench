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

Show chapter, word, target, progress, character, and status counts.

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

## `novel search`

Search chapter titles and manuscript content.

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

## `novel export`

Export a project to Markdown.

```powershell
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
```

Templates:

- `default`: plain manuscript Markdown.
- `frontmatter`: YAML front matter followed by the default Markdown body.

## `novel backup`

Copy the project JSON file to a backup directory.

```powershell
novel --workspace workspace backup moon-archive backups
```
