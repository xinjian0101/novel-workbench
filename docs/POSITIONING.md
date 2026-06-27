# Positioning

Novel Workbench is a local-first command line workspace for long-form fiction. It is not trying to replace every writing app. It exists for writers and developers who want inspectable project files, repeatable exports, and automation-friendly context.

## Why Star It

- You want a plain-file writing system that can live in Git.
- You want Markdown export without putting private drafts into a cloud account.
- You want structured context for AI or editor handoffs.
- You want a small Python CLI that is easy to inspect, extend, and run offline.
- You want a static HTML project snapshot that can be published by GitHub Pages.

## Comparison

| Need | Novel Workbench | Rich writing apps | Notes apps | Static site generators |
|---|---|---|---|---|
| Local plain files | First-class JSON and Markdown workflow | Varies by app | Usually partial | Usually input-only |
| Novel structure | Projects, chapters, scenes, notes, progress | Usually strong | Usually manual | Usually manual |
| Terminal automation | Primary interface | Usually limited | Usually limited | Strong, but not novel-aware |
| AI/editor handoff | Built-in briefs and context JSON | Usually manual | Usually manual | Usually manual |
| Static manuscript demo | Built-in export-site and Pages demo | Usually external | Usually external | Strong, but requires setup |
| Offline by default | Yes | Varies by app | Varies by app | Yes |

## Design Bets

- Keep manuscript data local and easy to back up.
- Prefer durable UTF-8 JSON and Markdown over proprietary project formats.
- Make every export reproducible from command line input.
- Keep the dependency surface small so the tool stays easy to audit.
- Add workflow depth before adding visual complexity.

## Tradeoffs

- No real-time collaboration.
- No hosted account, sync service, or mobile app.
- No WYSIWYG manuscript layout.
- No opaque database optimized for a single desktop application.

These tradeoffs are intentional. Novel Workbench should stay small enough that a writer or developer can understand the files it creates and the commands that change them.

## Best Public Pitch

Novel Workbench is for people who like the privacy of local files, the repeatability of a CLI, and the portability of Markdown.
