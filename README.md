# Omni Gateway

A universal AI router for coding tools. Omni Gateway provides smart auto-fallback, token compression, and seamless format translation so local agents, IDE assistants, and automation scripts can use free and premium LLM capacity through one stable API surface.

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
  Code Assist | provider backend | Vertex route
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

On first run, open the control panel and create the console password on the setup screen. No default password is shipped.

### Docker

```bash
docker run -d \
  --name router \
  -p 7861:7861 \
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
| `HOST` | `0.0.0.0` | Bind address. |
| `PORT` | `7861` | HTTP port. |
| `CORS_ORIGINS` | empty | Comma-separated browser origins allowed to call the API cross-origin. Leave empty for same-origin console usage. |
| `CORS_ORIGIN_REGEX` | empty | Optional regex for managed dynamic browser origins. |
| `API_KEY` | generated automatically | Preferred key for public client API requests. Must start with `sk-ogw-`. |
| `API_PASSWORD` | empty until setup | Password for API requests. |
| `PANEL_PASSWORD` | empty until setup | Password for the web control panel. |
| `PASSWORD` | empty until setup | Shared fallback password for API and panel. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Web console session lifetime in seconds. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Login rate-limit window in seconds. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Failed login attempts allowed per client within the rate-limit window. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Local credential storage directory. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist backend endpoint. |
| `API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Provider backend endpoint. |
| `PROXY` | empty | Optional HTTP, HTTPS, or SOCKS proxy. |
| `RETRY_429_ENABLED` | `true` | Retry rate-limited requests. |
| `RETRY_429_MAX_RETRIES` | `5` | Maximum rate-limit retry attempts. |
| `RETRY_429_INTERVAL` | `1` | Delay between retries in seconds. |
| `AUTO_DISABLE` | `false` | Disable credentials after configured hard failures. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Comma-separated hard-failure status codes. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Maximum continuation attempts for anti-truncation streaming. |
| `COMPATIBILITY_MODE` | `false` | Converts system messages for clients/models that reject them. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Include model reasoning fields when available. |
| `MONGODB_URI` | empty | Enables MongoDB storage when set. |
| `POSTGRESQL_URI` | empty | Enables PostgreSQL storage when set. |
| `REDIS_URL` | empty | Enables Redis-backed caches/session state when set. |
| `CODE_ASSIST_CLIENT_ID` | default desktop client | Optional override for the Code Assist OAuth flow. |
| `CODE_ASSIST_CLIENT_SECRET` | empty | Required when using the Code Assist OAuth flow with a custom client. |
| `ANTIGRAVITY_CLIENT_ID` | default desktop client | Optional override for the Antigravity OAuth flow. |
| `ANTIGRAVITY_CLIENT_SECRET` | empty | Required when using the Antigravity OAuth flow with a custom client. |
| `CLIENT_ID` | empty | Optional legacy-compatible fallback for provider OAuth override. |
| `CLIENT_SECRET` | empty | Optional legacy-compatible fallback for provider OAuth override. |
| `USER_AGENT` | `router/cli/...` | Optional upstream user-agent override. |

## API Surfaces

### OpenAI-Compatible Chat

```bash
curl http://127.0.0.1:7861/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
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
curl "http://127.0.0.1:7861/v1/models/gemini-2.5-flash:generateContent?key=$API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [
      {"role": "user", "parts": [{"text": "Write a small Python function."}]}
    ]
  }'
```

### Anthropic Messages

```bash
curl http://127.0.0.1:7861/v1/messages \
  -H "x-api-key: $API_KEY" \
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

### Normalized Client Routes

Omni Gateway exposes provider-compatible routes without a product namespace:

- `POST /v1/chat/completions`
- `POST /v1/messages`
- `GET /v1/models`
- `GET /v1beta/models`
- `POST /v1/models/{model}:generateContent`
- `POST /v1beta/models/{model}:generateContent`
- `POST /v1/models/{model}:streamGenerateContent`
- `POST /v1beta/models/{model}:streamGenerateContent`
- `POST /v1/models/{model}:countTokens`
- `POST /v1beta/models/{model}:countTokens`
- `POST /vertex/v1/chat/completions`
- `POST /vertex/v1/models/{model}:generateContent`

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
3. Create the console password on the first-run setup screen, or sign in with `PANEL_PASSWORD` when it is preconfigured.
4. Add credentials through OAuth or upload existing credential JSON files.
5. Verify credentials and watch cooldown/error state in the panel.
6. Point your coding tool to one of the API surfaces above.

Credential mode names:

- `code_assist`: standard Code Assist credential pool.
- `provider`: provider backend credential pool.

## Storage

Omni Gateway works out of the box with local SQLite-style storage under the project data directories. For distributed deployments, configure a shared backend:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=core
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/core
```

Redis can be added for cache/session acceleration:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Environment credential import is available from the control panel. Set one of the following variables to raw JSON or use the matching `_B64` variant for base64-encoded JSON:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
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
- Use a dedicated `API_KEY` for client integrations and a separate `PANEL_PASSWORD` for console access.
- Put Omni Gateway behind TLS when reachable outside localhost.
- Set `CORS_ORIGINS` to explicit trusted origins when browser clients need cross-origin access.
- Docker image publishing uses the `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets. Set the optional `IMAGE_NAME` repository variable only when publishing to a custom Docker Hub image name.
- Use MongoDB/PostgreSQL for multi-instance deployments.
- Keep log retention and credential rotation policies aligned with your usage limits.
- Rotate credentials immediately if a repository or platform scanner reports a leaked secret.

## License

Omni Gateway is released under the [MIT License](LICENSE).
