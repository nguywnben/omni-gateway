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
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | IDE integrations
        |
        v
Omni Gateway
  authentication -> format translation -> token cleanup -> routing -> fallback -> streaming
        |
        v
provider adapters
  Code Assist | Antigravity | Vertex-compatible route
```

The public API stays stable while provider-specific adapters evolve behind Omni Gateway.

## Repository Structure

```text
backend/     FastAPI entry point, routing core, format translators, storage, authentication
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
http://127.0.0.1:4283
```

On first run, open the control panel and create the console password on the setup screen. No default password is shipped.

### Docker

```bash
docker run -d \
  --name omni-gateway \
  -p 4283:4283 \
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
| `PORT` | `4283` | HTTP port. |
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
| `CODE_ASSIST_CLIENT_ID` | bundled desktop client | Optional override for the Code Assist OAuth client ID. |
| `CODE_ASSIST_CLIENT_SECRET` | bundled desktop client | Optional override for the Code Assist OAuth client secret. |
| `ANTIGRAVITY_CLIENT_ID` | bundled desktop client | Optional override for the Antigravity OAuth client ID. It can also be managed from the Providers page. |
| `ANTIGRAVITY_CLIENT_SECRET` | bundled desktop client | Optional override for the Antigravity OAuth client secret. Configure it through env or the Providers page when the upstream client changes. |
| `CLIENT_ID` | empty | Optional legacy-compatible fallback for provider OAuth override. |
| `CLIENT_SECRET` | empty | Optional legacy-compatible fallback for provider OAuth override. |
| `ANTIGRAVITY_API_URL` / `API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Optional Antigravity upstream endpoint override. |
| `USER_AGENT` / `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Optional Antigravity protocol user-agent override. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Optional payload-level Antigravity userAgent override. |

## SDK Surfaces

Omni Gateway is designed around the standard URL behavior of the official Python SDKs. Configure each client exactly as shown below; the gateway does not require non-standard duplicated path prefixes.

### OpenAI Python SDK

Use `/v1` as the OpenAI base URL. The SDK appends `/chat/completions`.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[{"role": "user", "content": "Explain this repository in one paragraph."}],
)
```

### Anthropic Python SDK

Use the gateway origin as the Anthropic base URL. The SDK appends `/v1/messages`.

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="gemini-2.5-flash",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Draft a commit message."}],
)
```

### Google GenAI Python SDK

Use the gateway origin as the Google GenAI base URL. The SDK appends its default model route, such as `/v1beta/models/{model}:generateContent`.

```python
from google import genai
from google.genai import types

client = genai.Client(
    http_options={
        "base_url": "http://127.0.0.1:4283",
    },
    api_key="sk-ogw-..."
)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Write a small Python function.",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful assistant.",
    ),
)
```

### Supported Routes

Omni Gateway exposes SDK-compatible routes without a product namespace:

- `POST /v1/chat/completions`
- `POST /v1/messages`
- `GET /v1/models`
- `GET /v1beta/models`
- `POST /v1beta/models/{model}:generateContent`
- `POST /v1beta/models/{model}:streamGenerateContent`
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
2. Open `http://127.0.0.1:4283`.
3. Create the console password on the first-run setup screen, or sign in with `PANEL_PASSWORD` when it is preconfigured.
4. Add credentials through OAuth or upload existing credential JSON files.
5. Verify credentials and watch cooldown/error state in the panel.
6. Point your coding tool to one of the API surfaces above.

Credential mode names:

- `code_assist`: standard Code Assist credential pool.
- `provider`: provider backend credential pool.

## Storage

Omni Gateway works out of the box with SQLite-backed local storage under the project data directories. For distributed deployments, configure a shared backend:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
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
