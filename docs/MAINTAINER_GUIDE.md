# Maintainer Guide

Use this guide to keep Novel Workbench easy to trust, review, and hand off.

## Review Routing

- `.github/CODEOWNERS` routes repository-wide review ownership to `@xinjian0101`.
- Keep pull requests small enough to review against one issue, one command, or one documentation surface.
- Ask contributors to run `python scripts/check.py` before review.

## Issue Triage

- `good first issue`: scoped work that a new contributor can finish without private project context.
- `help wanted`: work where maintainers welcome outside implementation or workflow design.
- `roadmap`: planned product direction that still needs public discussion.
- `question`: setup, workflow, or documentation questions that may become docs.
- `area:cli`, `area:docs`, and `area:import-export`: primary ownership areas for follow-up.

## Release Gates

Run these commands before tagging or publishing a public release:

```powershell
python scripts/check.py
python scripts/release_check.py
python scripts/launch_audit.py
python scripts/build_pages_demo.py public
python scripts/verify_public_links.py
```

For milestone checks, verify the public star target explicitly:

```powershell
python scripts/verify_public_links.py --min-stars 10000
```

Do not mark a milestone complete unless the verifier passes against the live GitHub repository.

## Public Surface Checks

- README first screen should keep the live demo, release link, star badge, fastest try path, and evaluation links visible.
- The Pages demo should include `index.html`, `manuscript.html`, `context.json`, `social-card.svg`, `sitemap.xml`, `robots.txt`, and `feed.xml`.
- Static site exports with a public URL should use `export-site --base-url`.
- Launch materials should point to `docs/LAUNCH_KIT.md`, `docs/SHOWCASE.md`, and `docs/FIRST_PR.md`.

## Data Safety

- Never commit private manuscript text, `.env`, tokens, local workspaces, exports, backups, or generated scratch output.
- Keep the local-first promise intact: no account requirement, telemetry, background network calls, or cloud dependency without public design discussion.
- If a bug report includes private writing, ask for a minimal redacted reproduction before continuing.

## Maintenance Loop

1. Triage new issues into labels and a next action.
2. Convert repeated questions into `docs/FAQ.md` or workflow docs.
3. Keep `docs/COMMUNITY.md` current with active contributor entry points.
4. Run `python scripts/launch_audit.py` after changing launch, README, community, or distribution material.
5. Run `python scripts/check.py` before merging.
