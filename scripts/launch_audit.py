from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "docs/CLI_REFERENCE.md",
    "docs/GITHUB_LAUNCH.md",
    "docs/LAUNCH_KIT.md",
    "docs/PACKAGING.md",
    "docs/SHOWCASE.md",
    "docs/USE_CASES.md",
    "examples/quickstart.md",
    "assets/readme-showcase.svg",
    "assets/social-preview.svg",
    ".github/workflows/ci.yml",
    ".github/workflows/pages.yml",
    ".github/workflows/release.yml",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/question.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/pull_request_template.md",
    "scripts/build_pages_demo.py",
]

REQUIRED_TEXT = {
    "README.md": [
        "https://xinjian0101.github.io/novel-workbench/",
        "python -m pip install \"git+https://github.com/xinjian0101/novel-workbench.git\"",
        "60-Second Tour",
        "assets/readme-showcase.svg",
        "export-site",
        "docs/LAUNCH_KIT.md",
        "docs/SHOWCASE.md",
        "docs/USE_CASES.md",
    ],
    "docs/GITHUB_LAUNCH.md": [
        "Pages",
        "python scripts/check.py",
        "python scripts/build_pages_demo.py public",
    ],
    "docs/LAUNCH_KIT.md": [
        "Live demo",
        "Launch posts",
        "Submission checklist",
    ],
    "docs/SHOWCASE.md": [
        "Pages demo",
        "assets/social-preview.svg",
        "Demo acceptance checks",
    ],
    "docs/USE_CASES.md": [
        "Author Drafting Workspace",
        "AI or Editor Handoff",
        "Static Project Demo",
        "Not a Fit",
    ],
    "pyproject.toml": [
        "Live Demo",
        "Documentation",
        "Source",
    ],
    ".github/ISSUE_TEMPLATE/bug_report.yml": [
        "Steps to reproduce",
        "This report does not include private manuscript text",
    ],
    ".github/ISSUE_TEMPLATE/feature_request.yml": [
        "Writing workflow",
        "This keeps manuscripts in local user-controlled files",
    ],
    ".github/ISSUE_TEMPLATE/question.yml": [
        "GitHub Discussions",
        "Static site demo",
    ],
    ".github/pull_request_template.md": [
        "python scripts/check.py",
        "Existing project JSON files remain readable",
    ],
}


def audit(root: Path) -> tuple[bool, list[str]]:
    messages: list[str] = []
    ok = True
    for relative in REQUIRED_FILES:
        path = root / relative
        if path.exists():
            messages.append(f"OK file: {relative}")
            continue
        messages.append(f"MISSING file: {relative}")
        ok = False

    for relative, snippets in REQUIRED_TEXT.items():
        path = root / relative
        if not path.exists():
            messages.append(f"MISSING text source: {relative}")
            ok = False
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet in text:
                messages.append(f"OK text: {relative} contains {snippet}")
                continue
            messages.append(f"MISSING text: {relative} lacks {snippet}")
            ok = False
    return ok, messages


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0]).resolve() if args else Path(__file__).resolve().parents[1]
    ok, messages = audit(root)
    print("Launch readiness: PASS" if ok else "Launch readiness: FAIL")
    for message in messages:
        print(f"- {message}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
