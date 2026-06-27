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
    ".env.example",
    "docs/CLI_REFERENCE.md",
    "docs/DISTRIBUTION.md",
    "docs/FAQ.md",
    "docs/GITHUB_LAUNCH.md",
    "docs/LAUNCH_KIT.md",
    "docs/OUTPUT_EXAMPLES.md",
    "docs/PACKAGING.md",
    "docs/POSITIONING.md",
    "docs/PYPI_PUBLISHING.md",
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
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
        "https://github.com/xinjian0101/novel-workbench/discussions/7",
        "https://github.com/xinjian0101/novel-workbench/releases/download/v0.1.1/novel_workbench-0.1.1-py3-none-any.whl",
        "python -m pip install \"git+https://github.com/xinjian0101/novel-workbench.git\"",
        "60-Second Tour",
        "assets/readme-showcase.svg",
        "docs/DISTRIBUTION.md",
        "docs/FAQ.md",
        "docs/OUTPUT_EXAMPLES.md",
        "export-site",
        "docs/LAUNCH_KIT.md",
        "docs/POSITIONING.md",
        "docs/SHOWCASE.md",
        "docs/USE_CASES.md",
    ],
    "docs/DISTRIBUTION.md": [
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
        "https://github.com/xinjian0101/novel-workbench/discussions/7",
        "novel_workbench-0.1.1-py3-none-any.whl",
        "docs/FAQ.md",
        "docs/OUTPUT_EXAMPLES.md",
        "Awesome List Entry",
        "Hacker News Style",
        "GitHub Discussion Announcement",
        "Follow-Up Signals",
    ],
    "docs/GITHUB_LAUNCH.md": [
        "Pages",
        "python scripts/check.py",
        "python scripts/build_pages_demo.py public",
    ],
    "docs/LAUNCH_KIT.md": [
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
        "https://github.com/xinjian0101/novel-workbench/discussions/7",
        "novel_workbench-0.1.1-py3-none-any.whl",
        "docs/FAQ.md",
        "docs/OUTPUT_EXAMPLES.md",
        "Live demo",
        "Launch posts",
        "Star pitch",
        "Submission checklist",
    ],
    "docs/POSITIONING.md": [
        "Why Star It",
        "Comparison",
        "Design Bets",
        "Tradeoffs",
    ],
    "docs/PYPI_PUBLISHING.md": [
        "Package Identity",
        "TestPyPI Dry Run",
        "PyPI Release",
        "Post-Release Updates",
    ],
    "docs/PACKAGING.md": [
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
        "novel_workbench-0.1.1-py3-none-any.whl",
        "docs/PYPI_PUBLISHING.md",
        "python scripts/release_check.py",
    ],
    ".env.example": [
        "NOVEL_WORKBENCH_HOME=workspace",
    ],
    "docs/SHOWCASE.md": [
        "Pages demo",
        "https://github.com/xinjian0101/novel-workbench/discussions/7",
        "docs/FAQ.md",
        "docs/OUTPUT_EXAMPLES.md",
        "assets/social-preview.svg",
        "Demo acceptance checks",
    ],
    "docs/OUTPUT_EXAMPLES.md": [
        "Live HTML Demo",
        "Manuscript Markdown",
        "AI or Editor Handoff",
        "Machine-Readable Context JSON",
        "Progress Report",
        "Report Pack",
        "python scripts/check.py",
    ],
    "docs/FAQ.md": [
        "Does Novel Workbench upload manuscripts?",
        "Where is my writing stored?",
        "How is it different from Scrivener, Ulysses, or Obsidian?",
        "Can I import an existing manuscript?",
        "Can I export to Markdown?",
        "Can I share a static preview?",
        "Is it on PyPI?",
        "novel_workbench-0.1.1-py3-none-any.whl",
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
