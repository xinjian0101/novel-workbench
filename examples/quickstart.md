# Quickstart Example

This example shows the smallest complete flow.

```powershell
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
novel --workspace workspace search moon-archive rain
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
novel --workspace workspace backup moon-archive backups
```

Expected statistics:

```text
Chapters: 1
Notes: 1
Words: 8
Target words: 80000
Progress: 0%
Characters: 43
Draft: 1
Revising: 0
Done: 0
```

Expected export:

```markdown
# Moon Archive

A historian finds a city under the lunar dust.

## Chapter 1: Descent

They opened the hatch and heard rain below.
```

Expected progress report:

```markdown
# Moon Archive Progress

## Overview

- Chapters: 1
- Notes: 1
- Words: 8
- Target words: 80000
- Progress: 0%
```

Importing from Markdown:

```powershell
novel --workspace workspace import-markdown imported-book path/to/manuscript.md
```

Generating a starter manuscript:

```powershell
novel --workspace workspace starter drafts/working-title.md
novel --workspace workspace starter drafts/mystery.md --template mystery
novel --workspace workspace import-markdown working-title drafts/working-title.md
novel --workspace workspace rename working-title first-draft --title "First Draft"
```
