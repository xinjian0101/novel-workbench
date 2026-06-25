# Security Policy

Novel Workbench is local-first. It does not send manuscripts, metadata, or usage events to external services.

## Reporting a Vulnerability

Open a private security advisory if the repository is hosted on GitHub, or contact the maintainers through the project's published security contact.

Please include:

- affected version or commit
- operating system and Python version
- reproduction steps
- expected and actual behavior
- impact assessment

Do not include private manuscripts or secrets in reports.

## Security Expectations

- No telemetry without explicit design approval.
- No real credentials in examples or tests.
- No automatic network access for core commands.
- Local manuscript data should remain outside Git by default.
