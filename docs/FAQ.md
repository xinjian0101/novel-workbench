# FAQ

## Does Novel Workbench upload manuscripts?

No. Novel Workbench is a local command line tool. It stores projects as UTF-8 JSON files in your workspace and writes exports to paths you choose. It has no account system, server, database, telemetry, or background network calls.

## Where is my writing stored?

By default, projects live under `./workspace/projects/`. Set `NOVEL_WORKBENCH_HOME` if you want a fixed workspace path:

```powershell
$env:NOVEL_WORKBENCH_HOME = "C:\writing\novel-workbench"
```

You can also pass `--workspace <dir>` to any command.

## How is it different from Scrivener, Ulysses, or Obsidian?

Novel Workbench is not a full-screen prose editor or a notes graph. It is a small local CLI for writers who want structured project files, repeatable exports, progress tracking, and handoff briefs that fit Git, Markdown, static sites, or automation.

Use the richer writing app when you want a polished visual editor. Use Novel Workbench when you want plain files, scriptable workflows, and an inspectable project format.

## Can I import an existing manuscript?

Yes. Use Markdown with a project title and chapter headings:

```powershell
novel --workspace workspace import-markdown my-novel drafts\my-novel.md
```

The importer accepts UTF-8 Markdown and creates a structured project with chapters.

## Can I export to Markdown?

Yes. The default export writes a clean manuscript:

```powershell
novel --workspace workspace export my-novel exports\my-novel.md
```

Other export templates can produce focus briefs, handoff briefs, momentum reports, outlines, progress reports, review findings, revision checklists, and YAML front matter.

## Can I share a static preview?

Yes. `export-site` writes `index.html`, `manuscript.html`, `context.json`, and `social-card.svg`:

```powershell
novel --workspace workspace export-site my-novel exports\my-novel-site
```

The live repository demo uses the same static-site path: https://xinjian0101.github.io/novel-workbench/

Use `--base-url` when exporting for a public URL to add absolute preview metadata, RSS discovery metadata, `sitemap.xml`, `robots.txt`, `feed.xml`, `llms.txt`, and `site.webmanifest` for crawlers, subscribers, AI coding tools, and browser save/install flows.

## Does it work without installing runtime dependencies?

Yes. The package has no runtime dependencies. Development and release checks use development tools listed in `pyproject.toml`.

## What Python versions are supported?

Python 3.10 or newer.

## Is it on PyPI?

Not yet. The repository has a verified wheel and source distribution in GitHub Releases, and PyPI publishing is documented in `docs/PYPI_PUBLISHING.md` as a maintainer-controlled manual action.

Install from GitHub Releases:

```powershell
python -m pip install "https://github.com/xinjian0101/novel-workbench/releases/download/v0.1.1/novel_workbench-0.1.1-py3-none-any.whl"
```

## Is this ready for real writing projects?

The local project format, import/export flow, backup/restore commands, workspace doctor, migration command, tests, CI, Pages demo, and release package checks are in place. Keep normal backups of important manuscripts and review exports before sharing them publicly.
