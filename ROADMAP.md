# Roadmap

Novel Workbench is built around a small local core. Planned work is grouped by user value rather than implementation size.

## Near Term

- Improve first-run examples with more realistic project fixtures and export screenshots.
- Add static-site theme options while keeping the generated site dependency-free.
- Expand editor workflow recipes for VS Code, Obsidian, plain Markdown folders, and Git review.
- Add more import validation messages for malformed Markdown manuscripts.
- Publish the package to PyPI after the maintainer completes the manual release checklist in [docs/PYPI_PUBLISHING.md](docs/PYPI_PUBLISHING.md).

## Medium Term

- Add reusable export presets for agent handoff, editorial review, and public progress updates.
- Add a small compatibility test corpus for legacy project JSON files.
- Add optional shell-completion refresh checks for new CLI commands.
- Improve static demo polish with richer progress and scene summaries.
- Create more contribution-ready issues for docs, examples, and validation improvements.

## Later

- Plugin hooks for custom exporters.
- Optional TUI interface.
- Optional encrypted local workspace.
- Optional local search index for very large workspaces.
- Import helpers for common manuscript folder layouts.

## Non-Goals

- Cloud sync by default.
- Manuscript telemetry.
- Mandatory account creation.
- Proprietary storage formats.
- Hosted AI generation.
- Background network calls.
