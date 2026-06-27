from __future__ import annotations

import sys
from pathlib import Path


REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "MANIFEST.in",
    ".devcontainer/devcontainer.json",
    "CHANGELOG.md",
    "ROADMAP.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    ".env.example",
    "docs/CLI_REFERENCE.md",
    "docs/CODESPACES.md",
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
    ".github/CODEOWNERS",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/question.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/pull_request_template.md",
    "docs/MAINTAINER_GUIDE.md",
    "scripts/build_pages_demo.py",
    "scripts/demo.py",
    "scripts/verify_public_links.py",
]

REQUIRED_TEXT = {
    "README.md": [
        "https://xinjian0101.github.io/novel-workbench/",
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
        "https://github.com/xinjian0101/novel-workbench/discussions/7",
        "https://github.com/xinjian0101/novel-workbench/releases/download/v0.1.1/novel_workbench-0.1.1-py3-none-any.whl",
        "https://img.shields.io/github/stars/xinjian0101/novel-workbench?label=stars",
        "https://img.shields.io/badge/open-Codespaces-181717.svg",
        "https://codespaces.new/xinjian0101/novel-workbench?quickstart=1",
        "topics-writing%20%7C%20novel%20%7C%20local--first%20%7C%20cli",
        "python -m pip install \"git+https://github.com/xinjian0101/novel-workbench.git\"",
        "At a Glance",
        "Fastest try path",
        "Cloud try path",
        "Shareable proof",
        "Star fit",
        "60-Second Tour",
        "novel --workspace workspace tour --output-dir exports",
        "novel templates",
        "novel pitch",
        "assets/readme-showcase.svg",
        "assets/terminal-demo.svg",
        "docs/DISTRIBUTION.md",
        "docs/EVALUATION.md",
        "docs/EDITOR_WORKFLOWS.md",
        "docs/FAQ.md",
        "docs/FIRST_PR.md",
        "docs/CODESPACES.md",
        "docs/MAINTAINER_GUIDE.md",
        "docs/OUTPUT_EXAMPLES.md",
        "novel templates",
        "novel pitch",
        "three-act|hero-journey|mystery|romance|sci-fi|thriller",
        "export-site",
        "--theme classic|editorial|focus",
        "--base-url https://example.com/site",
        "docs/LAUNCH_KIT.md",
        "docs/POSITIONING.md",
        "docs/SHOWCASE.md",
        "docs/USE_CASES.md",
        "near-term examples",
        "static-site polish",
    ],
    "ROADMAP.md": [
        "Near Term",
        "Medium Term",
        "Later",
        "Non-Goals",
        "static-site theme options",
        "editor workflow recipes",
        "import validation messages",
        "docs/PYPI_PUBLISHING.md",
        "contribution-ready issues",
        "Hosted AI generation",
        "Background network calls",
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
        ".devcontainer/devcontainer.json",
        "docs/CODESPACES.md",
        "python scripts/check.py",
        "python scripts/build_pages_demo.py public",
        "python scripts/verify_public_links.py",
        "python scripts/verify_public_links.py --min-stars 10000",
        "sitemap.xml",
        "robots.txt",
        ".github/CODEOWNERS",
        "docs/MAINTAINER_GUIDE.md",
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
        "docs/CODESPACES.md",
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
        "sitemap.xml",
        "robots.txt",
    ],
    ".env.example": [
        "NOVEL_WORKBENCH_HOME=workspace",
    ],
    "MANIFEST.in": [
        "include .github/CODEOWNERS",
        "recursive-include .devcontainer *.json",
        "recursive-include .github *.md *.yml",
    ],
    ".devcontainer/devcontainer.json": [
        "mcr.microsoft.com/devcontainers/python:1-3.12-bullseye",
        "python -m pip install --upgrade pip && python -m pip install -e '.[dev]'",
        "ms-python.python",
    ],
    "docs/CODESPACES.md": [
        "Codespaces Quick Start",
        "python -m pip install -e '.[dev]'",
        "novel --workspace workspace tour --output-dir exports",
        "python scripts/check.py",
        "python scripts/launch_audit.py",
        "Do not commit generated `workspace/`, `exports/`, `backups/`, `.env`, or private manuscript files.",
    ],
    "docs/SHOWCASE.md": [
        "Pages demo",
        "https://github.com/xinjian0101/novel-workbench/discussions/7",
        "docs/FAQ.md",
        "docs/OUTPUT_EXAMPLES.md",
        "assets/terminal-demo.svg",
        "assets/social-preview.svg",
        "Try Novel Workbench",
        "moon-archive-pitch.md",
        "scene summaries",
        "Open Graph",
        "Twitter summary metadata",
        "sitemap.xml",
        "robots.txt",
        "Codespaces quick start",
        "novel --workspace workspace tour --output-dir exports",
        "Demo acceptance checks",
    ],
    "docs/OUTPUT_EXAMPLES.md": [
        "Launch Post Snippets",
        "Live HTML Demo",
        "novel templates",
        "Pitch brief",
        "moon-archive-pitch.md",
        "romance",
        "sci-fi",
        "thriller",
        "novel --workspace workspace tour --output-dir exports",
        "Manuscript Markdown",
        "AI or Editor Handoff",
        "Machine-Readable Context JSON",
        "Progress Report",
        "Report Pack",
        "https://xinjian0101.github.io/novel-workbench/",
        "https://github.com/xinjian0101/novel-workbench/releases/tag/v0.1.1",
        "sitemap.xml",
        "robots.txt",
        "python scripts/check.py",
    ],
    "scripts/demo.py": [
        "pitch",
        "moon-archive-pitch.md",
        "--template",
        "pitch",
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
        "novel templates",
        "novel starter",
        "novel pitch",
        "romance",
        "sci-fi",
        "thriller",
        "AI or Editor Handoff",
        "docs/EDITOR_WORKFLOWS.md",
        "Static Project Demo",
        "--theme editorial",
        "scene summaries",
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
        "docs/CODESPACES.md",
        "docs/MAINTAINER_GUIDE.md",
        "Current contributor entry points",
    ],
    "docs/MAINTAINER_GUIDE.md": [
        "Maintainer Guide",
        ".github/CODEOWNERS",
        "@xinjian0101",
        "python scripts/check.py",
        "python scripts/release_check.py",
        "python scripts/launch_audit.py",
        "python scripts/build_pages_demo.py public",
        "python scripts/verify_public_links.py",
        "python scripts/verify_public_links.py --min-stars 10000",
        "Do not mark a milestone complete unless the verifier passes against the live GitHub repository.",
        "good first issue",
        "help wanted",
        "roadmap",
        "question",
        "export-site --base-url",
        "no account requirement, telemetry, background network calls, or cloud dependency",
    ],
    "docs/FIRST_PR.md": [
        "First Pull Request Guide",
        "Choose a Small Issue",
        "docs/EDITOR_WORKFLOWS.md",
        "docs/CODESPACES.md",
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
