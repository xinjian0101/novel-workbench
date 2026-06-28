# GitHub Launch Checklist

Use this checklist before making the repository public or announcing it.

## Repository Settings

- Description: `Local-first CLI workspace for writing, organizing, searching, and exporting novels.`
- Topics: `writing`, `novel`, `novel-writing`, `creative-writing`, `writing-tools`, `fiction`, `markdown`, `cli`, `local-first`, `author-tools`, `python`, `static-site`
- Website: use the GitHub Pages URL after the `Pages` workflow publishes successfully.
- Visibility: public only after CI passes on GitHub.
- Features: enable Issues and Discussions if maintainers can respond.
- Dependabot: enabled for GitHub Actions through `.github/dependabot.yml`.
- Pages: enable GitHub Actions as the Pages source so `.github/workflows/pages.yml` can publish the generated demo site.
- Codespaces: `.devcontainer/devcontainer.json` should install `.[dev]` so new contributors can run the tour and checks without local Python setup.
- Community intake: issue forms and the pull request template should stay focused on reproducible bugs, author workflows, and the local-first project model.
- Maintainer trust: `.github/CODEOWNERS` and `docs/MAINTAINER_GUIDE.md` should describe review routing, release gates, public link checks, and milestone verification.

## README Review

- The first screen explains what the tool does.
- The README links to concrete author, archive, AI handoff, and static demo use cases.
- The README includes a direct star-worthy positioning section.
- The README links to the distribution copy for public sharing.
- The install command points to the real GitHub repository.
- PyPI publishing is documented as a post-release maintainer action, not claimed as already complete.
- The one-command 60-second tour works after installing from GitHub: `novel --workspace workspace tour --output-dir exports`.
- The Codespaces quick start links to `docs/CODESPACES.md` and runs the same one-command tour.
- The terminal demo matches `python scripts/demo.py`.
- The Pages demo builds with `python scripts/build_pages_demo.py public`.
- The showcase assets in `docs/SHOWCASE.md` render in the README and social preview.
- The issue forms and pull request template make first contributions easy to scope.
- The repository has open contributor entry points, including `good first issue` and `help wanted` issues.
- Quick Start works on a clean checkout.
- No temporary or example-only GitHub URLs remain.
- Security and contribution links resolve.

## Release Prep

1. Run:

   ```powershell
   python scripts/check.py
   python scripts/release_check.py
   python scripts/build_pages_demo.py public
   python scripts/launch_audit.py
   python scripts/verify_github_metadata.py
   python scripts/verify_public_links.py
   ```

2. Tag the next release as `vX.Y.Z`.
3. Use `docs/RELEASE_TEMPLATE.md` and the matching version section from `CHANGELOG.md` as release notes.
4. Push the tag to let the Release workflow build, verify, and attach the source distribution and wheel.
5. Confirm the `Pages` workflow publishes `index.html`, `manuscript.html`, `context.json`, `social-card.svg`, `sitemap.xml`, `robots.txt`, `feed.xml`, `llms.txt`, and `site.webmanifest`.
6. Run `python scripts/verify_github_metadata.py` after publish to confirm the public repository description, homepage, release, topics, and star count from GitHub's API.
7. Run `python scripts/verify_public_links.py` after publish to confirm the repository, Pages demo, badges, release wheel, and reported star count resolve from a clean public path.
8. When auditing a star-count milestone, run `python scripts/verify_github_metadata.py --min-stars 10000` and `python scripts/verify_public_links.py --min-stars 10000`; rely on command results instead of estimating from README badges by eye.
9. Do not mark a milestone complete unless the live GitHub verifiers pass.

## Social Preview

Suggested preview copy:

```text
Novel Workbench
Local-first novel writing from the terminal.
Markdown in, Markdown out. No cloud account required.
```

## Launch Risks

- A real star count cannot be guaranteed by repository contents alone.
- Package URLs currently point to `https://github.com/xinjian0101/novel-workbench`.
- Do not commit local `workspace/`, `exports/`, `backups/`, `.demo-workspace/`, or `.env` files.
