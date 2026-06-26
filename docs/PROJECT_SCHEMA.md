# Project File Schema

Novel Workbench stores each project as a UTF-8 JSON file:

```text
workspace/projects/<slug>.json
```

## Project Object

```json
{
  "schema_version": 1,
  "slug": "moon-archive",
  "title": "Moon Archive",
  "synopsis": "A historian finds a city under the lunar dust.",
  "genre": "science fiction",
  "audience": "adult",
  "revision_notes": "Tighten the midpoint.",
  "target_words": 80000,
  "target_date": "2026-12-31",
  "chapters": [],
  "notes": [],
  "progress": [],
  "created_at": "2026-06-25T12:00:00+00:00",
  "updated_at": "2026-06-25T12:00:00+00:00"
}
```

Required fields:

- `slug`: lowercase letters, numbers, and single hyphens
- `schema_version`: project schema version written by Novel Workbench
- `title`: non-empty, 120 characters or fewer
- `synopsis`: string
- `genre`: string, 240 characters or fewer
- `audience`: string, 240 characters or fewer
- `revision_notes`: string
- `target_words`: positive integer or `null`
- `target_date`: date in `YYYY-MM-DD` format or `null`
- `chapters`: array of chapter objects
- `notes`: array of note objects
- `progress`: array of progress entry objects
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

The file name should match the project slug.

Older project files without `schema_version`, `genre`, `audience`, `revision_notes`, `target_words`, `target_date`, `notes`, or `progress` still load. Novel Workbench treats missing `schema_version` as legacy version `0`, missing text metadata as empty strings, missing `target_words` or `target_date` as `null`, and missing `notes` or `progress` as an empty list.

Run `novel --workspace workspace migrate` to rewrite legacy project files using the current schema. The command creates a safety snapshot before writing each migrated project.

## Chapter Object

```json
{
  "number": 1,
  "title": "Signal",
  "content": "The first signal arrived.",
  "summary": "The signal disrupts the archive shift.",
  "status": "draft",
  "scenes": [],
  "created_at": "2026-06-25T12:00:00+00:00",
  "updated_at": "2026-06-25T12:00:00+00:00"
}
```

Required fields:

- `number`: one-based chapter number
- `title`: non-empty, 120 characters or fewer
- `content`: string
- `summary`: string
- `status`: `draft`, `revising`, or `done`
- `scenes`: array of scene objects
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

Chapter numbers should be sequential starting at `1`.

Older chapter objects without `summary` or `scenes` still load. Novel Workbench treats missing chapter summaries as empty strings and missing scenes as an empty list.

## Scene Object

```json
{
  "number": 1,
  "title": "Signal discovered",
  "summary": "The crew finds the first active relay.",
  "status": "draft",
  "created_at": "2026-06-25T12:00:00+00:00",
  "updated_at": "2026-06-25T12:00:00+00:00"
}
```

Required fields:

- `number`: one-based scene number within the chapter
- `title`: non-empty, 120 characters or fewer
- `summary`: string
- `status`: `draft`, `revising`, or `done`
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

Scene numbers should be sequential starting at `1` within each chapter.

## Note Object

```json
{
  "id": 1,
  "title": "Ada",
  "content": "Engineer protagonist.",
  "kind": "character",
  "created_at": "2026-06-25T12:00:00+00:00",
  "updated_at": "2026-06-25T12:00:00+00:00"
}
```

Required fields:

- `id`: one-based note id unique within the project
- `title`: non-empty, 120 characters or fewer
- `content`: string
- `kind`: `general`, `character`, `location`, `plot`, or `research`
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

## Progress Entry Object

```json
{
  "id": 1,
  "date": "2026-06-26",
  "words": 1200,
  "note": "Drafted the descent sequence.",
  "created_at": "2026-06-26T12:00:00+00:00",
  "updated_at": "2026-06-26T12:00:00+00:00"
}
```

Required fields:

- `id`: one-based progress id unique within the project
- `date`: writing date in `YYYY-MM-DD` format
- `words`: positive integer
- `note`: string
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

## Validation

Run:

```powershell
novel --workspace workspace doctor
```

The doctor command validates project JSON files, reports JSON syntax line and column numbers, flags invalid UTF-8, missing required fields, invalid slugs, empty or oversized titles, invalid statuses, invalid note kinds, duplicate note ids, invalid progress dates or word counts, invalid target word counts or dates, file-name-to-slug mismatches, chapter numbering problems, and scene numbering problems, then prints repair hints for known failures.

Backup files use the same schema as project files. `novel restore-backup` validates a backup before restoring it into `workspace/projects/`.
