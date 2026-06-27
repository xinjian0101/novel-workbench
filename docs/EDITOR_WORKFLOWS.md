# Editor Workflows

Use these recipes when Novel Workbench is the project system and another editor is the drafting surface. The CLI keeps project state structured; the editor handles prose.

## VS Code Draft Loop

Use this when chapters live in a local workspace and the manuscript is reviewed in VS Code.

```powershell
novel --workspace workspace sample
novel --workspace workspace focus moon-archive
novel --workspace workspace export moon-archive exports/moon-archive.md
code exports/moon-archive.md
```

After editing or reviewing the exported manuscript, keep structured state current:

```powershell
novel --workspace workspace update-chapter moon-archive 1 --content-file drafts/chapter-1.md
novel --workspace workspace add-progress moon-archive 1200 --note "Drafted the next scene."
novel --workspace workspace review moon-archive
```

## Obsidian or Markdown Vault

Use this when planning notes, exported reports, and manuscript snapshots belong in a Markdown vault.

```powershell
novel --workspace workspace export-pack moon-archive vault/novels/moon-archive
novel --workspace workspace export-dashboard vault/novels/dashboard.md
novel --workspace workspace export-context moon-archive vault/novels/moon-archive/context.json
```

Commit the exported pack or sync it with the vault tool you already trust. Keep `workspace/projects/*.json` private if the manuscript is not ready to share.

## AI or Human Editor Handoff

Use this when a collaborator needs context without receiving the whole workspace.

```powershell
novel --workspace workspace handoff moon-archive > handoff/moon-archive.md
novel --workspace workspace export-context moon-archive handoff/moon-archive-context.json
novel --workspace workspace export moon-archive handoff/moon-archive-revision.md --template revision
```

Send the Markdown handoff for readable context and the JSON file when another tool needs structured project state. The handoff includes the next action, continuity notes, recent progress, and a continuation prompt.

## Git Review Workflow

Use this when manuscript progress should be reviewable as plain files.

```powershell
novel --workspace workspace doctor
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
git diff -- workspace exports
```

Before opening a pull request or sharing a branch, run:

```powershell
python scripts/check.py
```

This verifies tests, packaging, the Pages demo, launch readiness, and the bundled demo workflow.

## What to Keep Out of Git

- Private drafts that should not be public.
- `.env` files.
- Temporary `workspace/`, `exports/`, and `backups/` directories unless they are intentionally shared examples.
- Generated files that do not help reviewers understand the change.

Use `.gitignore`, `novel backup`, and explicit export directories to keep the boundary clear.
