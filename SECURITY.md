# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| Current `main` branch | Yes |
| Latest published release | Yes |
| Older releases | No |

## Reporting Vulnerabilities

Report suspected vulnerabilities through a [private GitHub security advisory](https://github.com/nguywnben/omni-gateway/security/advisories/new). Do not open a public issue for active secrets, credential exposure, authentication bypasses, or deployment compromise.

Include the affected version or commit, deployment topology, reproduction steps, impact, and any proposed mitigation. Remove real credentials and personal data from evidence. This is a personal open-source project, so response times are best effort; reports are normally acknowledged within 72 hours.

After a fix is available, coordinate public disclosure through the advisory. Credit is provided unless the reporter prefers to remain anonymous.

## Operational Baseline

- Use a unique `PANEL_PASSWORD` for the management console.
- Use a separate `API_KEY` beginning with `sk-ogw-` for client traffic.
- Keep the service behind TLS when exposed outside localhost.
- Preconfigure `PANEL_PASSWORD`, or restrict network access until first-run setup is complete, so an untrusted visitor cannot claim a new public deployment.
- Restrict browser cross-origin access with `CORS_ORIGINS`.
- Trust forwarded headers only when a controlled reverse proxy overwrites them.
- Keep one worker when using local file and SQLite storage.
- Never commit `.env`, credential JSON files, database files, or logs.
- Rotate credentials immediately if GitHub or another scanner reports a public leak.
