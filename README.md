# Novel Workbench

[![CI](https://github.com/xinjian0101/novel-workbench/actions/workflows/ci.yml/badge.svg)](https://github.com/xinjian0101/novel-workbench/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Novel Workbench is a fast, local-first command line workspace for writing long-form fiction. It gives authors a simple way to create projects, draft chapters, track progress, and export a clean Markdown manuscript without signing up for a cloud service.

```text
$ novel sample
Created sample project: moon-archive (2 chapters)

$ novel stats moon-archive
Chapters: 2
Notes: 0
Words: 15
Target words: 80000
Progress: 0%
Characters: 77
Draft: 2
Revising: 0
Done: 0

$ novel search moon-archive signal
1. Signal [draft]
   The first signal arrived at 03:17.
```

## Why It Exists

Most writing apps are either too heavy for developers and terminal users, or too cloud-dependent for private drafts. Novel Workbench keeps the core workflow plain:

- one command line tool
- one local workspace directory
- UTF-8 JSON project files
- Markdown export that can go into Git, editors, static sites, or publishing tools

## Features

- Create and list novel projects
- Create a sample project for instant exploration
- Generate an importable starter manuscript template
- Rename project slugs and titles without losing chapters
- Add chapters with draft, revising, and done statuses
- Move chapters and keep numbering consistent
- Delete chapters and automatically close numbering gaps
- Update chapter title, content, and status
- Track project notes for characters, locations, plot, research, and general planning
- Show project outlines
- Report chapter, word, character, and status counts
- Track target word count progress
- Search across chapter titles and manuscript content
- Import a Markdown manuscript into a structured project
- Export manuscripts to Markdown
- Export with optional YAML front matter for publishing tools
- Export shareable progress reports with chapter and status tables
- Back up project JSON before risky edits
- Validate workspace health before releases or migrations, with repair hints
- Print shell completion scripts for bash, zsh, and PowerShell
- Run fully offline with no account, server, database, or telemetry

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

novel --workspace workspace init
novel --workspace workspace starter drafts/working-title.md --template three-act
novel --workspace workspace import-markdown working-title drafts/working-title.md
novel --workspace workspace rename working-title first-draft --title "First Draft"
novel --workspace workspace sample
novel --workspace workspace move-chapter moon-archive 2 1
novel --workspace workspace delete-chapter moon-archive 2
novel --workspace workspace add-note moon-archive "Underground rain" --kind plot --content "The moon city has weather below the dust."
novel --workspace workspace list-notes moon-archive
novel --workspace workspace set-target moon-archive 80000
novel --workspace workspace stats moon-archive
novel --workspace workspace doctor
novel --workspace workspace search moon-archive rain
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
novel --workspace workspace backup moon-archive backups
```

Run the bundled demo:

```powershell
python scripts/demo.py
```

## Commands

```text
novel init
novel list
novel doctor
novel completion bash|zsh|powershell
novel sample [--slug moon-archive]
novel starter <output.md> [--template three-act|hero-journey|mystery] [--force]
novel create <slug> <title> [--synopsis "..."]
novel rename <slug> <new-slug> [--title "..."]
novel import-markdown <slug> <input.md>
novel show <slug>
novel stats <slug>
novel set-target <slug> <words>
novel clear-target <slug>
novel add-note <slug> <title> [--kind general|character|location|plot|research] [--content "..."] [--content-file path]
novel list-notes <slug> [--kind general|character|location|plot|research]
novel delete-note <slug> <id>
novel search <slug> <query>
novel add-chapter <slug> <title> [--content "..."] [--status draft|revising|done]
novel update-chapter <slug> <number> [--title "..."] [--content "..."] [--content-file path] [--status draft|revising|done]
novel move-chapter <slug> <number> <new-number>
novel delete-chapter <slug> <number>
novel export <slug> <output.md> [--template default|frontmatter|progress]
novel backup <slug> <output-dir>
```

Use `--workspace <dir>` with any command to choose the workspace directory. If omitted, the tool uses `NOVEL_WORKBENCH_HOME`, then falls back to `./workspace`.

See [docs/CLI_REFERENCE.md](docs/CLI_REFERENCE.md) for command details and examples. Shell completion setup lives in [docs/SHELL_COMPLETION.md](docs/SHELL_COMPLETION.md). Project file details live in [docs/PROJECT_SCHEMA.md](docs/PROJECT_SCHEMA.md).

## Data Layout

```text
workspace/
  projects/
    first-novel.json
exports/
  first-novel.md
backups/
  first-novel-2026-06-25T120000Z0000.json
```

Project files are JSON so they can be reviewed, versioned, backed up, and migrated without a proprietary database.

## Markdown Import Format

```markdown
# Project Title

Optional synopsis.

## Chapter 1: Opening

Chapter text.

## Chapter 2: The Turn

More chapter text.
```

## Development

Install development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run checks:

```powershell
python scripts/check.py
```

Architecture notes live in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Configuration

Copy `.env.example` if you want a fixed local workspace setting:

```powershell
Copy-Item .env.example .env
```

Supported variables:

- `NOVEL_WORKBENCH_HOME`: default workspace directory for `novel`.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned improvements. The current project intentionally starts with a small, reliable local core before adding richer writing workflows.

## GitHub Launch

Use [docs/GITHUB_LAUNCH.md](docs/GITHUB_LAUNCH.md) before publishing the repository. It covers repository description, topics, release notes, CI, and README checks.

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), then open a focused issue or pull request.

Community and issue labels are described in [docs/COMMUNITY.md](docs/COMMUNITY.md).

## Security

Novel Workbench is local-first and does not transmit manuscripts. Report security concerns through [SECURITY.md](SECURITY.md).

## License

MIT. See [LICENSE](LICENSE).
