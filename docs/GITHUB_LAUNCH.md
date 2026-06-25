# GitHub Launch Checklist

Use this checklist before making the repository public or announcing it.

## Repository Settings

- Description: `Local-first CLI workspace for writing, organizing, searching, and exporting novels.`
- Topics: `writing`, `novel`, `markdown`, `cli`, `local-first`, `author-tools`, `python`
- Website: leave blank unless a real project page exists.
- Visibility: public only after CI passes on GitHub.
- Features: enable Issues and Discussions if maintainers can respond.
- Dependabot: enabled for GitHub Actions through `.github/dependabot.yml`.

## README Review

- The first screen explains what the tool does.
- The terminal demo matches `python scripts/demo.py`.
- Quick Start works on a clean checkout.
- No temporary or example-only GitHub URLs remain.
- Security and contribution links resolve.

## Release Prep

1. Run:

   ```powershell
   python scripts/check.py
   ```

2. Tag the first release as `v0.1.0`.
3. Use `docs/RELEASE_TEMPLATE.md` and the `0.1.0` section from `CHANGELOG.md` as release notes.
4. Attach the source distribution and wheel only if you intend to distribute artifacts through GitHub Releases.

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
