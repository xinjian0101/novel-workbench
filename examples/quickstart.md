# Quickstart Example

This example shows the smallest complete flow.

Install directly from GitHub:

```powershell
python -m pip install "git+https://github.com/xinjian0101/novel-workbench.git"
```

Try the built-in sample:

```powershell
novel --workspace workspace sample
novel --workspace workspace focus moon-archive
novel --workspace workspace momentum moon-archive
novel --workspace workspace export-pack moon-archive exports/moon-archive-pack
```

Run a fuller local workflow:

```powershell
novel --workspace workspace init
novel --workspace workspace starter drafts/working-title.md --template three-act
novel --workspace workspace import-markdown working-title drafts/working-title.md
novel --workspace workspace rename working-title first-draft --title "First Draft"
novel --workspace workspace sample
novel --workspace workspace set-metadata moon-archive --genre "science fiction" --audience adult --revision-notes "Lean into the discovery mystery."
novel --workspace workspace move-chapter moon-archive 2 1
novel --workspace workspace delete-chapter moon-archive 2
novel --workspace workspace add-note moon-archive "Underground rain" --kind plot --content "The moon city has weather below the dust."
novel --workspace workspace update-note moon-archive 1 --kind research --content "The lower city has sealed storm drains."
novel --workspace workspace list-notes moon-archive
novel --workspace workspace set-target moon-archive 80000
novel --workspace workspace stats moon-archive
novel --workspace workspace search moon-archive rain
novel --workspace workspace export moon-archive exports/moon-archive.md
novel --workspace workspace export moon-archive exports/moon-archive-frontmatter.md --template frontmatter
novel --workspace workspace export moon-archive exports/moon-archive-progress.md --template progress
novel --workspace workspace export-pack moon-archive exports/moon-archive-pack
novel --workspace workspace backup moon-archive backups
```

Expected statistics:

```text
Chapters: 1
Notes: 1
Words: 8
Target words: 80000
Remaining words: 79992
Progress: 0%
Average chapter words: 8
Characters: 43
Draft: 1 chapters / 8 words
Revising: 0 chapters / 0 words
Done: 0 chapters / 0 words
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
- Characters: 43
- Genre: science fiction
- Audience: adult
- Target words: 80000
- Remaining words: 79992
- Progress: 0%
- Average chapter words: 8
```

Expected report pack files:

```text
moon-archive.md
moon-archive-frontmatter.md
moon-archive-focus.md
moon-archive-momentum.md
moon-archive-board.md
moon-archive-outline.md
moon-archive-progress.md
moon-archive-review.md
moon-archive-revision.md
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

Using a custom export template:

```markdown
# {title} Brief

{synopsis}

{status_summary}

{chapter_table}
```

```powershell
novel --workspace workspace export moon-archive exports/moon-archive-brief.md --template-file templates/brief.md
```
