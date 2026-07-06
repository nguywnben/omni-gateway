# Security Policy

## Supported Version

Security fixes target the current `main` branch.

## Reporting Vulnerabilities

Please report suspected vulnerabilities privately through GitHub security advisories or by contacting the repository owner. Do not open a public issue for active secrets, credential exposure, authentication bypasses, or deployment compromise.

## Operational Baseline

- Use a unique `PANEL_PASSWORD` for the management console.
- Use a separate `API_KEY` beginning with `sk-ogw-` for client traffic.
- Keep the service behind TLS when exposed outside localhost.
- Restrict browser cross-origin access with `CORS_ORIGINS`.
- Never commit `.env`, credential JSON files, database files, or logs.
- Rotate credentials immediately if GitHub or another scanner reports a public leak.

