# Architecture

Novel Workbench is intentionally small and local-first.

## Boundaries

- CLI parsing lives in `src/novel_workbench/cli.py`.
- Project persistence and validation live in `src/novel_workbench/storage.py`.
- Data shapes live in `src/novel_workbench/models.py`.
- Tests cover storage behavior, CLI flows, validation errors, the demo script, and the Pages demo builder.

## Data Model

Projects are stored as UTF-8 JSON files under:

```text
workspace/projects/<slug>.json
```

Each project contains:

- `slug`
- `title`
- `synopsis`
- `genre`
- `audience`
- `revision_notes`
- `target_words`
- `chapters`
- `notes`
- `created_at`
- `updated_at`

Each chapter contains:

- `number`
- `title`
- `content`
- `status`
- `created_at`
- `updated_at`

Valid statuses are `draft`, `revising`, and `done`.

See [PROJECT_SCHEMA.md](PROJECT_SCHEMA.md) for the file-level schema and validation expectations.

## Design Choices

- No database: writers can inspect, back up, and version project files directly.
- No network calls: manuscripts stay local by default.
- No runtime dependencies: installation and maintenance stay simple.
- Markdown import/export: manuscripts stay portable.
- Static site export keeps project sharing dependency-free and suitable for GitHub Pages.
- Custom export templates use explicit named fields and Python's built-in formatter.

## Compatibility

The Markdown parser accepts UTF-8 files with or without a BOM. This matters on Windows because some editors write BOM-prefixed UTF-8 files.

## Future Extension Points

- Import formats can be added beside `parse_markdown_chapters`.
- Workspace health checks can inspect project JSON files before destructive operations.
- Optional UI layers should call the storage API rather than duplicate persistence rules.
