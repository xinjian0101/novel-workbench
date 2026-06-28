# Evaluation Guide

Use this page when deciding whether Novel Workbench is worth trying, starring, sharing, or contributing to.

## Two-Minute Fit Check

Novel Workbench is a good fit if you want:

- A local-first writing workspace with no account, server, database, telemetry, or background network calls.
- Plain UTF-8 JSON project files that can live in Git, backups, or a private folder.
- Markdown manuscript exports, AI/editor context JSON, and a static HTML project site from the same source data.
- A small Python CLI that can be audited, scripted, and run offline.

It is not the right fit if you need:

- Rich WYSIWYG editing, page layout, or print production.
- Real-time collaboration, cloud sync, comments, or mobile apps.
- A hosted AI writing service.
- A replacement for a mature commercial writing suite.

## Fastest Proof

Install from GitHub and run the tour:

```powershell
python -m pip install "git+https://github.com/xinjian0101/novel-workbench.git"
novel --workspace workspace tour --output-dir exports
```

For a one-word first run after installation:

```powershell
novel try
```

Then inspect:

- `workspace/projects/moon-archive.json` for the local project file.
- `exports/moon-archive/context.json` for AI/editor handoff context.
- `exports/moon-archive/site/index.html` for the static project dashboard.
- `exports/moon-archive/pack/` for Markdown reports.

## Star Signals

Star the repository if any of these are useful to you:

- You want more local-first writing tools that keep drafts in user-controlled files.
- You use Markdown, Git, or command line workflows for long-form writing.
- You want AI/editor handoff context without uploading a manuscript to a hosted app.
- You want a simple static project demo that can publish through GitHub Pages.
- You want to track a small Python CLI that is intentionally easy to audit and extend.

## Share Targets

The clearest places to share Novel Workbench are:

- Local-first software communities.
- Python CLI and developer tool lists.
- Markdown, plain-text, and Git writing workflow communities.
- Author tool, indie writer, and writing process discussions.
- AI-assisted writing workflow threads where local context export matters.

Use [docs/DISTRIBUTION.md](DISTRIBUTION.md) for copy-paste launch text.

## Contribution Fit

Good first contributions improve one of these surfaces:

- Install and first-run clarity.
- Import/export examples.
- Editor workflow recipes.
- Static site output polish.
- CLI validation, error messages, and tests.

Start with [docs/FIRST_PR.md](FIRST_PR.md) and keep the local-first boundary intact: no accounts, telemetry, cloud services, or background network calls.
