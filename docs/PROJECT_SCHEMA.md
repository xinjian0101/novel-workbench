# Project File Schema

Novel Workbench stores each project as a UTF-8 JSON file:

```text
workspace/projects/<slug>.json
```

## Project Object

```json
{
  "slug": "moon-archive",
  "title": "Moon Archive",
  "synopsis": "A historian finds a city under the lunar dust.",
  "genre": "science fiction",
  "audience": "adult",
  "revision_notes": "Tighten the midpoint.",
  "target_words": 80000,
  "chapters": [],
  "notes": [],
  "created_at": "2026-06-25T12:00:00+00:00",
  "updated_at": "2026-06-25T12:00:00+00:00"
}
```

Required fields:

- `slug`: lowercase letters, numbers, and single hyphens
- `title`: non-empty, 120 characters or fewer
- `synopsis`: string
- `genre`: string, 240 characters or fewer
- `audience`: string, 240 characters or fewer
- `revision_notes`: string
- `target_words`: positive integer or `null`
- `chapters`: array of chapter objects
- `notes`: array of note objects
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

The file name should match the project slug.

Older project files without `genre`, `audience`, `revision_notes`, `target_words`, or `notes` still load. Novel Workbench treats missing text metadata as empty strings, missing `target_words` as `null`, and missing `notes` as an empty list.

## Chapter Object

```json
{
  "number": 1,
  "title": "Signal",
  "content": "The first signal arrived.",
  "status": "draft",
  "created_at": "2026-06-25T12:00:00+00:00",
  "updated_at": "2026-06-25T12:00:00+00:00"
}
```

Required fields:

- `number`: one-based chapter number
- `title`: non-empty, 120 characters or fewer
- `content`: string
- `status`: `draft`, `revising`, or `done`
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

Chapter numbers should be sequential starting at `1`.

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

## Validation

Run:

```powershell
novel --workspace workspace doctor
```

The doctor command validates project JSON files, reports JSON syntax line and column numbers, flags invalid UTF-8, missing required fields, invalid slugs, empty or oversized titles, invalid statuses, invalid note kinds, duplicate note ids, invalid target word counts, file-name-to-slug mismatches, and chapter numbering problems, then prints repair hints for known failures.

Backup files use the same schema as project files. `novel restore-backup` validates a backup before restoring it into `workspace/projects/`.
