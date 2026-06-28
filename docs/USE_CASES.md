# Use Cases

Novel Workbench is built for writers and tool builders who want durable local files instead of a hosted writing account.

For comparison notes and project tradeoffs, see [docs/POSITIONING.md](POSITIONING.md).

For copy-paste editor recipes, see [docs/EDITOR_WORKFLOWS.md](EDITOR_WORKFLOWS.md).

## Author Drafting Workspace

Use Novel Workbench when a novel needs structure before it needs a full writing suite.

- Create a project with chapters, scenes, character notes, location notes, and research notes.
- Discover built-in structures with `novel templates`, then start from importable manuscript templates with `novel starter` for `three-act`, `hero-journey`, `mystery`, `romance`, `sci-fi`, and `thriller` drafts.
- Track daily word-count progress and deadline pace.
- Generate a shareable `novel pitch` brief before posting a project, asking for beta readers, or handing the draft to an editor.
- Export a `novel social-card` SVG when a launch post or project update needs a preview image.
- Export `novel launch-copy` when you need social, community, awesome-list, and follow-up text from the same project data.
- Export a `novel share-kit` bundle when you need pitch copy, static preview files, and report-pack assets in one directory.
- Export Markdown when the draft is ready for an editor, static site, or publishing pipeline.

Useful commands:

```powershell
novel --workspace workspace sample
novel --workspace workspace focus moon-archive
novel --workspace workspace momentum moon-archive
novel --workspace workspace export moon-archive exports/moon-archive.md
```

## Local-First Manuscript Archive

Use Novel Workbench when manuscript data should stay private, reviewable, and easy to back up.

- Store projects as UTF-8 JSON files in a local workspace.
- Keep exported manuscripts and reports as plain Markdown.
- Use backup and restore commands before destructive edits.

Useful commands:

```powershell
novel --workspace workspace backup moon-archive backups
novel --workspace workspace doctor
novel --workspace workspace migrate --dry-run
novel --workspace workspace restore-backup backups/moon-archive-20260626T120000000000Z.json --force
```

## AI or Editor Handoff

Use Novel Workbench when a collaborator or AI tool needs context without receiving a full messy workspace.

- Generate a focused continuation brief.
- Export machine-readable project context JSON.
- Share revision checklists and progress reports.

Useful commands:

```powershell
novel --workspace workspace handoff moon-archive
novel --workspace workspace context moon-archive
novel --workspace workspace revision moon-archive
novel --workspace workspace export-context moon-archive exports/moon-archive-context.json
```

For VS Code, Markdown vault, AI handoff, and Git review flows, see [docs/EDITOR_WORKFLOWS.md](EDITOR_WORKFLOWS.md).

## Static Project Demo

Use Novel Workbench when a project needs a lightweight public or private HTML snapshot.

- Export a static dashboard, manuscript page, and context JSON.
- Publish with GitHub Pages or any static file host.
- Use the bundled Pages demo as an example launch surface.

Useful commands:

```powershell
novel --workspace workspace export-site moon-archive exports/moon-archive-site
novel --workspace workspace export-site moon-archive exports/moon-archive-site --theme editorial
python scripts/build_pages_demo.py public
python scripts/launch_audit.py
```

The exported index includes project metadata, progress, chapter summaries, scene summaries, notes, and recent writing so reviewers can scan the plan before opening the manuscript view.

## Good Fit

- Authors who like Git, Markdown, terminals, and local files.
- Developers building personal writing systems.
- AI-assisted writing workflows that need structured project context.
- Small teams that want inspectable project files instead of a proprietary database.

## Not a Fit

- Real-time collaborative editing.
- Mobile-first drafting.
- Cloud sync, user accounts, or hosted manuscript storage.
- Rich WYSIWYG manuscript layout.
