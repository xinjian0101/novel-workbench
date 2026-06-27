# Output Examples

Use these examples to see what Novel Workbench produces before installing it.

## Launch Post Snippets

Use these compact snippets in posts, README comparisons, forum replies, and issue answers.

Manuscript export:

```text
Markdown manuscript export:
# Moon Archive
## Chapter 1: Descent
They opened the hatch and heard rain below.
```

AI/editor handoff:

```text
Handoff brief:
- Continue Chapter 1: Descent [draft] - 8 words
- Includes project snapshot, continuity notes, recent progress, and a continuation prompt.
```

Context JSON:

```text
Context JSON:
{"format":"novel-workbench-project-context","project":{"slug":"moon-archive"},"next_action":{"kind":"continue_chapter"}}
```

Static site export:

```text
Static site export:
index.html
manuscript.html
context.json
Demo: https://xinjian0101.github.io/novel-workbench/
Release: https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1
```

## Live HTML Demo

The GitHub Pages demo is generated with the same static export path available to users:

- Demo: https://xinjian0101.github.io/novel-workbench/
- Build command: `python scripts/build_pages_demo.py public`
- User command: `novel --workspace workspace export-site moon-archive exports/moon-archive-site`

The generated directory contains:

```text
index.html
manuscript.html
context.json
```

## Manuscript Markdown

Command:

```powershell
novel --workspace workspace export moon-archive exports\moon-archive.md
```

Output shape:

```markdown
# Moon Archive

A historian finds a city under the lunar dust.

## Chapter 1: Descent

They opened the hatch and heard rain below.
```

## AI or Editor Handoff

Command:

```powershell
novel --workspace workspace handoff moon-archive
```

Output shape:

```markdown
# Moon Archive Handoff

## Project Snapshot

- Slug: `moon-archive`
- Synopsis: A historian finds a city under the lunar dust.
- Genre: science fiction
- Audience: adult
- Manuscript words: 8
- Logged words: 1250
- Target words: 80000
- Remaining words: 79992

## Next Action

- Continue Chapter 1: Descent [draft] - 8 words

## Prompt

Continue Chapter 1: Descent. Preserve the synopsis, continuity notes, current chapter status, and recent progress.
```

## Machine-Readable Context JSON

Command:

```powershell
novel --workspace workspace export-context moon-archive exports\moon-archive-context.json
```

Output shape:

```json
{
  "format": "novel-workbench-project-context",
  "format_version": 1,
  "project": {
    "slug": "moon-archive",
    "title": "Moon Archive"
  },
  "stats": {
    "words": 8,
    "logged_words": 1250,
    "target_words": 80000
  },
  "next_action": {
    "kind": "continue_chapter",
    "chapter_number": 1,
    "chapter_title": "Descent"
  }
}
```

## Progress Report

Command:

```powershell
novel --workspace workspace export moon-archive exports\moon-archive-progress.md --template progress
```

Output shape:

```markdown
# Moon Archive Progress

## Overview

- Chapters: 1
- Notes: 3
- Words: 8
- Target words: 80000
- Remaining words: 79992
- Progress: 0%

## Recent Progress

| Date | Words | Note |
|---|---:|---|
| 2026-06-26 | 1250 | Included evening revisions. |
```

## Report Pack

Command:

```powershell
novel --workspace workspace export-pack moon-archive exports\moon-archive-pack
```

Output files:

```text
moon-archive.md
moon-archive-frontmatter.md
moon-archive-focus.md
moon-archive-handoff.md
moon-archive-momentum.md
moon-archive-board.md
moon-archive-outline.md
moon-archive-progress.md
moon-archive-review.md
moon-archive-revision.md
```

## Reproduce Locally

Run the bundled demo script:

```powershell
python scripts/demo.py
```

Run the full quality gate:

```powershell
python scripts/check.py
```
