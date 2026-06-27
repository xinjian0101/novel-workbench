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
    "docs/EVALUATION.md",
    "docs/EDITOR_WORKFLOWS.md",
    "docs/FAQ.md",
    "docs/FIRST_PR.md",
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
    "assets/terminal-demo.svg",
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
        "https://img.shields.io/github/stars/xinjian0101/novel-workbench?label=stars",
        "topics-writing%20%7C%20novel%20%7C%20local--first%20%7C%20cli",
        "python -m pip install \"git+https://github.com/xinjian0101/novel-workbench.git\"",
        "At a Glance",
        "Fastest try path",
        "Shareable proof",
        "Star fit",
        "60-Second Tour",
        "novel --workspace workspace tour --output-dir exports",
        "assets/readme-showcase.svg",
        "assets/terminal-demo.svg",
        "docs/DISTRIBUTION.md",
        "docs/EVALUATION.md",
        "docs/EDITOR_WORKFLOWS.md",
        "docs/FAQ.md",
        "docs/FIRST_PR.md",
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
        "novel --workspace workspace tour --output-dir exports",
        "docs/FAQ.md",
        "docs/OUTPUT_EXAMPLES.md",
        "docs/EDITOR_WORKFLOWS.md",
        "docs/EVALUATION.md",
        "Short output snippets",
        "Editor workflow recipes",
        "Awesome List Entry",
        "Hacker News Style",
        "GitHub Discussion Announcement",
        "Follow-Up Signals",
    ],
    "docs/GITHUB_LAUNCH.md": [
        "Pages",
        "good first issue",
        "help wanted",
        "novel --workspace workspace tour --output-dir exports",
        "python scripts/check.py",
        "python scripts/build_pages_demo.py public",
    ],
    "docs/LAUNCH_KIT.md": [
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
        "https://github.com/xinjian0101/novel-workbench/discussions/7",
        "novel_workbench-0.1.1-py3-none-any.whl",
        "novel --workspace workspace tour --output-dir exports",
        "docs/FAQ.md",
        "docs/OUTPUT_EXAMPLES.md",
        "docs/EDITOR_WORKFLOWS.md",
        "docs/EVALUATION.md",
        "Live demo",
        "Launch posts",
        "assets/terminal-demo.svg",
        "good first issue",
        "help wanted",
        "docs/FIRST_PR.md",
        "Star pitch",
        "README first screen includes stars, topics, local-first proof, fastest try path, and evaluation guide links.",
        "Submission checklist",
    ],
    "docs/POSITIONING.md": [
        "Why Star It",
        "Comparison",
        "Design Bets",
        "Tradeoffs",
    ],
    "docs/EVALUATION.md": [
        "Two-Minute Fit Check",
        "Fastest Proof",
        "Star Signals",
        "Share Targets",
        "Contribution Fit",
        "novel --workspace workspace tour --output-dir exports",
        "no account, server, database, telemetry, or background network calls",
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
        "assets/terminal-demo.svg",
        "assets/social-preview.svg",
        "Try Novel Workbench",
        "novel --workspace workspace tour --output-dir exports",
        "Demo acceptance checks",
    ],
    "docs/OUTPUT_EXAMPLES.md": [
        "Launch Post Snippets",
        "Live HTML Demo",
        "novel --workspace workspace tour --output-dir exports",
        "Manuscript Markdown",
        "AI or Editor Handoff",
        "Machine-Readable Context JSON",
        "Progress Report",
        "Report Pack",
        "https://xinjian0101.github.io/novel-workbench/",
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
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
        "docs/EDITOR_WORKFLOWS.md",
        "Static Project Demo",
        "Not a Fit",
    ],
    "docs/EDITOR_WORKFLOWS.md": [
        "VS Code Draft Loop",
        "Obsidian or Markdown Vault",
        "AI or Human Editor Handoff",
        "Git Review Workflow",
        "python scripts/check.py",
        "novel --workspace workspace export-pack",
    ],
    "docs/COMMUNITY.md": [
        "Current Contributor Entry Points",
        "docs/EDITOR_WORKFLOWS.md",
        "docs/FIRST_PR.md",
        "https://github.com/xinjian0101/novel-workbench/issues/8",
        "https://github.com/xinjian0101/novel-workbench/issues/9",
        "good first issue",
        "help wanted",
    ],
    "CONTRIBUTING.md": [
        "docs/FIRST_PR.md",
        "python scripts/check.py",
        "Current contributor entry points",
    ],
    "docs/FIRST_PR.md": [
        "First Pull Request Guide",
        "Choose a Small Issue",
        "docs/EDITOR_WORKFLOWS.md",
        "python scripts/check.py",
        "Closes #9",
        "Do not add account requirements, telemetry, background network calls, or cloud services.",
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
        "docs/FIRST_PR.md",
        "python scripts/check.py",
        "Existing project JSON files remain readable",
    ],
}

FORBIDDEN_TEXT = {
    "README.md": [
        "https://github.com/xinjian0101/novel-workbench/issues/10",
    ],
    "docs/COMMUNITY.md": [
        "https://github.com/xinjian0101/novel-workbench/issues/10",
    ],
    "docs/FIRST_PR.md": [
        "https://github.com/xinjian0101/novel-workbench/issues/10",
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
    for relative, snippets in FORBIDDEN_TEXT.items():
        path = root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for snippet in snippets:
            if snippet in text:
                messages.append(f"FORBIDDEN text: {relative} contains {snippet}")
                ok = False
                continue
            messages.append(f"OK absent: {relative} omits {snippet}")
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
