# Showcase

Use this page as the source of truth for visual and demo assets.

## Live surfaces

- Repository: https://github.com/xinjian0101/novel-workbench
- Pages demo: https://xinjian0101.github.io/novel-workbench/
- README showcase: `assets/readme-showcase.svg`
- Social preview source: `assets/social-preview.svg`

## What the demo proves

- The CLI can create a sample project.
- The project can be enriched with metadata, notes, progress, and a target word count.
- The project can be exported as Markdown reports, AI/editor context JSON, and a static HTML site.
- GitHub Pages can publish a working static project dashboard.

## Visual asset usage

Use `assets/readme-showcase.svg` inside README and docs.

Use `assets/social-preview.svg` when setting a GitHub social preview image or preparing launch graphics. If a platform requires PNG, export the SVG from a browser or design tool at 1280 by 640 pixels.

## Demo proof commands

```powershell
python scripts/build_pages_demo.py public
python scripts/launch_audit.py
python scripts/check.py
```

## Demo acceptance checks

- `public/index.html` contains `Moon Archive`.
- `public/manuscript.html` contains `They opened the hatch`.
- `public/context.json` contains `"slug": "moon-archive"`.
- The published Pages URL returns HTTP 200.
