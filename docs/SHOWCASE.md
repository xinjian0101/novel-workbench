# Showcase

Use this page as the source of truth for visual and demo assets.

## Live surfaces

- Repository: https://github.com/xinjian0101/novel-workbench
- Pages demo: https://xinjian0101.github.io/novel-workbench/
- Launch announcement: https://github.com/xinjian0101/novel-workbench/discussions/7
- README showcase: `assets/readme-showcase.svg`
- Terminal demo: `assets/terminal-demo.svg`
- Social preview source: `assets/social-preview.svg`
- Output examples: `docs/OUTPUT_EXAMPLES.md`
- Use-case guide: `docs/USE_CASES.md`
- FAQ: `docs/FAQ.md`
- Positioning guide: `docs/POSITIONING.md`
- Distribution guide: `docs/DISTRIBUTION.md`
- PyPI publishing prep: `docs/PYPI_PUBLISHING.md`

## What the demo proves

- The CLI can create a sample project.
- The project can be enriched with metadata, notes, progress, and a target word count.
- The project can be exported as Markdown reports, AI/editor context JSON, and a static HTML site.
- The Pages demo includes chapter-level scene summaries, so readers can inspect story planning depth before opening the manuscript view.
- The exported HTML includes description, Open Graph, and Twitter summary metadata for cleaner social link previews.
- The Pages demo publishes `social-card.svg`, `sitemap.xml`, and `robots.txt` so public crawlers and social platforms can discover the dashboard, manuscript, context JSON, and preview image.
- The Codespaces quick start gives reviewers a disposable environment for running the same tour without local setup.
- GitHub Pages can publish a working static project dashboard.
- The static site includes a "Try Novel Workbench" callout with the install command and `novel --workspace workspace tour --output-dir exports`.
- The output examples show generated Markdown, handoff, context JSON, static site, and report-pack shapes.
- The bundled terminal demo prints a project pitch and writes `moon-archive-pitch.md`, so launch reviewers can inspect share copy from one command.
- The README and use-case guide explain who should try or star the project.
- The FAQ answers privacy, install, import, export, and package-index questions.
- The GitHub Discussion announcement provides a public launch thread for questions and sharing.
- The positioning guide explains the comparison with rich writing apps, notes apps, and static site generators.
- The distribution guide provides channel-specific copy for external sharing.
- The PyPI publishing guide documents the next install-channel milestone without claiming it is complete.

## Visual asset usage

Use `assets/readme-showcase.svg` inside README and docs.

Use `assets/terminal-demo.svg` when a launch surface needs a compact command-flow preview.

Use `assets/social-preview.svg` when setting a GitHub social preview image or preparing launch graphics. If a platform requires PNG, export the SVG from a browser or design tool at 1280 by 640 pixels.

## Demo proof commands

```powershell
python scripts/build_pages_demo.py public
python scripts/launch_audit.py
python scripts/check.py
```

## Demo acceptance checks

- `public/index.html` contains `Moon Archive`.
- `public/index.html` contains `Try Novel Workbench`.
- `public/index.html` contains `novel --workspace workspace tour --output-dir exports`.
- `public/manuscript.html` contains `They opened the hatch`.
- `public/context.json` contains `"slug": "moon-archive"`.
- `public/social-card.svg` contains `Novel Workbench Share Card`.
- `public/sitemap.xml` contains `https://xinjian0101.github.io/novel-workbench/index.html`.
- `public/sitemap.xml` contains `https://xinjian0101.github.io/novel-workbench/social-card.svg`.
- `public/robots.txt` contains `Sitemap: https://xinjian0101.github.io/novel-workbench/sitemap.xml`.
- The published Pages URL returns HTTP 200.
