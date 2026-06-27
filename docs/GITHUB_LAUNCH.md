# GitHub Launch Checklist

Use this checklist before making the repository public or announcing it.

## Repository Settings

- Description: `Local-first CLI workspace for writing, organizing, searching, and exporting novels.`
- Topics: `writing`, `novel`, `markdown`, `cli`, `local-first`, `author-tools`, `python`
- Website: use the GitHub Pages URL after the `Pages` workflow publishes successfully.
- Visibility: public only after CI passes on GitHub.
- Features: enable Issues and Discussions if maintainers can respond.
- Dependabot: enabled for GitHub Actions through `.github/dependabot.yml`.
- Pages: enable GitHub Actions as the Pages source so `.github/workflows/pages.yml` can publish the generated demo site.
- Community intake: issue forms and the pull request template should stay focused on reproducible bugs, author workflows, and the local-first project model.

## README Review

- The first screen explains what the tool does.
- The README links to concrete author, archive, AI handoff, and static demo use cases.
- The install command points to the real GitHub repository.
- The 60-second tour works after installing from GitHub.
- The terminal demo matches `python scripts/demo.py`.
- The Pages demo builds with `python scripts/build_pages_demo.py public`.
- The showcase assets in `docs/SHOWCASE.md` render in the README and social preview.
- The issue forms and pull request template make first contributions easy to scope.
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
   ```

2. Tag the first release as `v0.1.0`.
3. Use `docs/RELEASE_TEMPLATE.md` and the `0.1.0` section from `CHANGELOG.md` as release notes.
4. Push the tag to let the Release workflow build, verify, and attach the source distribution and wheel.
5. Confirm the `Pages` workflow publishes `index.html`, `manuscript.html`, and `context.json`.

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
