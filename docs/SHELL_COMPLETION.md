# Shell Completion

Novel Workbench ships a dependency-free `novel completion` command that prints static completion scripts for installed command names.

## Why This Approach

The standard Python `argparse` module does not generate shell completion scripts by itself. The most common argparse completion package is `argcomplete`, which officially focuses on bash and zsh, with other shells such as PowerShell handled outside the core support path. Novel Workbench keeps completion built in so bash, zsh, and PowerShell users can use the same installed `novel` command without adding a runtime dependency.

The generated scripts complete top-level commands such as `create`, `outline`, `plan`, `add-character`, `add-location`, `add-scene`, `add-progress`, `set-deadline`, `stats`, `export`, `backup`, and `restore-backup`. They do not yet complete project slugs, file paths, or option values.

## Bash

For the current shell session:

```bash
eval "$(novel completion bash)"
```

To enable completion for new shells, add the same line to `~/.bashrc`.

## Zsh

For the current shell session:

```zsh
eval "$(novel completion zsh)"
```

To enable completion for new shells, add the same line to `~/.zshrc`.

If completion is not active in your zsh setup, initialize completion before registering Novel Workbench:

```zsh
autoload -Uz compinit
compinit
eval "$(novel completion zsh)"
```

## PowerShell

For the current shell session:

```powershell
novel completion powershell | Invoke-Expression
```

To enable completion for new shells, add the same line to your PowerShell profile:

```powershell
notepad $PROFILE
```

Then add:

```powershell
novel completion powershell | Invoke-Expression
```

Restart PowerShell after saving the profile.

## Updating Completions

When Novel Workbench adds commands, update your shell by starting a new session or re-running the command for your shell.
