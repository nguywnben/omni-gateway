# Omni Gateway

A universal AI router for coding tools. Omni Gateway provides smart auto-fallback, token compression, and seamless format translation so local agents, IDE assistants, and automation scripts can use free and premium LLM capacity through one stable API surface.

Repository: https://github.com/nguywnben/omni-gateway

## Why Omni Gateway

Modern coding workflows often mix clients and providers: OpenAI-compatible tools, Gemini-native SDKs, Anthropic-style agents, Google-backed credentials, and experimental model routes. Omni Gateway sits between those clients and model backends so each tool can keep speaking the format it already understands while the gateway handles routing, retries, request cleanup, and response normalization.

## Core Capabilities

- Smart auto-fallback: rotates credentials, retries transient failures, and routes around cooldowns, rate limits, and exhausted capacity.
- Token compression: normalizes payloads, removes incompatible fields, trims avoidable overhead, and keeps long coding sessions within practical context limits.
- Format translation: accepts OpenAI chat completions, Gemini native requests, and Anthropic Messages, then translates requests and streaming responses across formats.
- Credential orchestration: manages multiple OAuth credential pools with health state, cooldown tracking, bulk upload, verification, and quota visibility.
- Streaming resilience: supports SSE streaming, pseudo-streaming for clients that require streamed output, and anti-truncation retries for long generations.
- Control panel: ships with a local web console for credentials, logs, configuration, usage, and version information.

## Architecture

```text
client tools
  OpenAI SDKs | Gemini SDKs | Anthropic-compatible agents | IDE integrations
        |
        v
Omni Gateway
  auth -> format translation -> token cleanup -> routing -> fallback -> streaming
        |
        v
provider adapters
  Code Assist | Omni backend | Vertex route
```

The public API stays stable while provider-specific adapters can evolve behind the gateway.

## Repository Structure

```text
backend/     FastAPI entrypoint, routing core, format translators, storage, auth
frontend/    Management console HTML, CSS, and JavaScript
deploy/      Docker, platform manifests, and install/start scripts
```

## Quick Start

### Local Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python backend/main.py
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python backend/main.py
```

Open the control panel at:

```text
http://127.0.0.1:7861
```

The default API/control-panel password is `pwd`. Change it before exposing the service.

### Docker

```bash
docker run -d \
  --name omni-gateway \
  -p 7861:7861 \
  -e OGW_API_PASSWORD=change-me \
  -e OGW_PANEL_PASSWORD=change-me-too \
  -v "$(pwd)/backend/data/creds:/app/backend/data/creds" \
  nguywnben/omni-gateway:latest
```

### Docker Compose

```bash
docker compose -f deploy/docker-compose.yml up -d
```

The included compose file starts Omni Gateway with a persistent `backend/data/creds` volume.

## Configuration

Omni Gateway reads configuration from environment variables first, then stored configuration, then defaults.

| Variable | Default | Purpose |
| --- | --- | --- |
| `OGW_HOST` | `0.0.0.0` | Bind address. |
| `OGW_PORT` | `7861` | HTTP port. |
| `OGW_API_PASSWORD` | `pwd` via fallback | Password for API requests. |
| `OGW_PANEL_PASSWORD` | `pwd` via fallback | Password for the web control panel. |
| `OGW_PASSWORD` | `pwd` | Shared fallback password for API and panel. |
| `OGW_CREDENTIALS_DIR` | `./backend/data/creds` | Local credential storage directory. |
| `OGW_CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist backend endpoint. |
| `OGW_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Omni backend endpoint. |
| `OGW_PROXY` | empty | Optional HTTP, HTTPS, or SOCKS proxy. |
| `OGW_RETRY_429_ENABLED` | `true` | Retry rate-limited requests. |
| `OGW_RETRY_429_MAX_RETRIES` | `5` | Maximum rate-limit retry attempts. |
| `OGW_RETRY_429_INTERVAL` | `1` | Delay between retries in seconds. |
| `OGW_AUTO_DISABLE` | `false` | Disable credentials after configured hard failures. |
| `OGW_AUTO_DISABLE_ERROR_CODES` | `403` | Comma-separated hard-failure status codes. |
| `OGW_ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Maximum continuation attempts for anti-truncation streaming. |
| `OGW_COMPATIBILITY_MODE` | `false` | Converts system messages for clients/models that reject them. |
| `OGW_RETURN_THOUGHTS_TO_FRONTEND` | `true` | Include model reasoning fields when available. |
| `OGW_MONGODB_URI` | empty | Enables MongoDB storage when set. |
| `OGW_POSTGRESQL_URI` | empty | Enables PostgreSQL storage when set. |
| `OGW_REDIS_URL` | empty | Enables Redis-backed caches/session state when set. |
| `OGW_CODE_ASSIST_CLIENT_ID` | empty | Required for Code Assist OAuth flow. |
| `OGW_CODE_ASSIST_CLIENT_SECRET` | empty | Required for Code Assist OAuth flow. |
| `OGW_CLIENT_ID` | empty | Required for Omni OAuth flow. |
| `OGW_CLIENT_SECRET` | empty | Required for Omni OAuth flow. |
| `OGW_USER_AGENT` | `omni-gateway/cli/...` | Optional upstream user-agent override. |

## API Surfaces

### OpenAI-Compatible Chat

```bash
curl http://127.0.0.1:7861/ogw/v1/chat/completions \
  -H "Authorization: Bearer $OGW_API_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash",
    "messages": [
      {"role": "user", "content": "Explain this repository in one paragraph."}
    ],
    "stream": true
  }'
```

### Gemini Native

```bash
curl "http://127.0.0.1:7861/ogw/v1/models/gemini-2.5-flash:generateContent?key=$OGW_API_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {"role": "user", "parts": [{"text": "Write a small Python function."}]}
    ]
  }'
```

### Anthropic Messages

```bash
curl http://127.0.0.1:7861/ogw/v1/messages \
  -H "x-api-key: $OGW_API_PASSWORD" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-2.5-flash",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Draft a commit message."}
    ]
  }'
```

### Namespaced Omni Routes

Omni Gateway exposes namespaced routes for explicit Omni backend usage:

- `POST /ogw/v1/chat/completions`
- `POST /ogw/v1/messages`
- `GET /ogw/v1/models`
- `POST /ogw/v1/models/{model}:generateContent`
- `POST /ogw/v1/models/{model}:streamGenerateContent`
- `POST /ogw/v1/models/{model}:countTokens`

## Model Features

Omni Gateway recognizes feature prefixes and suffixes in model names:

- `fake-streaming/{model}` or the configured pseudo-streaming prefix for clients that require SSE output.
- `streaming-anti-truncation/{model}` or the configured anti-truncation prefix for long-form streaming recovery.
- Thinking suffixes such as `-high`, `-medium`, `-low`, `-minimal`, and `-max` for supported Gemini-family models.
- Search suffixes such as `-search` for models that support Google Search grounding.

Provider adapters normalize these feature names before sending upstream requests.

## Credential Workflow

1. Start Omni Gateway.
2. Open `http://127.0.0.1:7861`.
3. Sign in to the control panel with `OGW_PANEL_PASSWORD`.
4. Add credentials through OAuth or upload existing credential JSON files.
5. Verify credentials and watch cooldown/error state in the panel.
6. Point your coding tool to one of the API surfaces above.

Credential mode names:

- `code_assist`: standard Code Assist credential pool.
- `omni`: Omni backend credential pool.

## Storage

Omni Gateway works out of the box with local SQLite-style storage under the project data directories. For distributed deployments, configure a shared backend:

```bash
OGW_MONGODB_URI=mongodb://localhost:27017
OGW_MONGODB_DATABASE=omni_gateway
```

```bash
OGW_POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

Redis can be added for cache/session acceleration:

```bash
OGW_REDIS_URL=redis://127.0.0.1:6379/0
```

Environment credential import is available from the control panel. Set one of the following variables to raw JSON or use the matching `_B64` variant for base64-encoded JSON:

```bash
OGW_CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
OGW_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

The payload can be a single credential object, an array, or `{ "credentials": [...] }`.

## Development

```bash
pip install -r requirements.txt
python -m compileall backend
python backend/main.py
```

Useful checks:

```bash
rg -n -i "legacy-string" .
git status --short
```

## Deployment Notes

- Never commit credential JSON files or `.env`.
- Use separate `OGW_API_PASSWORD` and `OGW_PANEL_PASSWORD` for exposed deployments.
- Put Omni Gateway behind TLS when reachable outside localhost.
- Use MongoDB/PostgreSQL for multi-instance deployments.
- Keep log retention and credential rotation policies aligned with your usage limits.

## License

This repository uses the license declared in [LICENSE](LICENSE). Review it before using Omni Gateway in any environment beyond personal development.
