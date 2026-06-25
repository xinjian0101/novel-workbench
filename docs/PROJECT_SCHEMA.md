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
  "chapters": [],
  "created_at": "2026-06-25T12:00:00+00:00",
  "updated_at": "2026-06-25T12:00:00+00:00"
}
```

Required fields:

- `slug`: lowercase letters, numbers, and single hyphens
- `title`: non-empty, 120 characters or fewer
- `synopsis`: string
- `chapters`: array of chapter objects
- `created_at`: ISO timestamp
- `updated_at`: ISO timestamp

The file name should match the project slug.

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

## Validation

Run:

```powershell
novel --workspace workspace doctor
```

The doctor command validates project JSON files, reports corrupt files, checks file-name-to-slug consistency, and checks chapter numbering.
