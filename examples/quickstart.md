# Quickstart Example

This example shows the smallest complete flow.

```powershell
novel --workspace workspace init
novel --workspace workspace starter drafts/working-title.md --template three-act
novel --workspace workspace import-markdown working-title drafts/working-title.md
novel --workspace workspace rename working-title first-draft --title "First Draft"
novel --workspace workspace sample
novel --workspace workspace set-target moon-archive 80000
novel --workspace workspace stats moon-archive
novel --workspace workspace search moon-archive signal
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
novel --workspace workspace backup moon-archive backups
```

Expected statistics:

```text
Chapters: 2
Words: 15
Target words: 80000
Progress: 0%
Characters: 77
Draft: 2
Revising: 0
Done: 0
```

Expected export:

```markdown
# Moon Archive

A historian finds a city under the lunar dust.

## Chapter 1: Signal

The first signal arrived at 03:17.

## Chapter 2: Descent

They opened the hatch and heard rain below.
```

Expected progress report:

```markdown
# Moon Archive Progress

## Overview

- Chapters: 2
- Words: 15
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
