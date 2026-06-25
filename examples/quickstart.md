# Quickstart Example

This example shows the smallest complete flow.

```powershell
novel --workspace workspace init
novel --workspace workspace create moon-archive "Moon Archive" --synopsis "A historian finds a city under the lunar dust."
novel --workspace workspace add-chapter moon-archive "Signal" --content "The first signal arrived at 03:17."
novel --workspace workspace stats moon-archive
novel --workspace workspace search moon-archive signal
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace backup moon-archive backups
```

Expected statistics:

```text
Chapters: 1
Words: 7
Characters: 34
Draft: 1
Revising: 0
Done: 0
```

Expected export:

```markdown
# Moon Archive

A historian finds a city under the lunar dust.

## Chapter 1: Signal

The first signal arrived at 03:17.
```

Importing from Markdown:

```powershell
novel --workspace workspace import-markdown imported-book path/to/manuscript.md
```
