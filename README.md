# Omni Gateway

A universal AI router for coding tools. Omni Gateway provides smart auto-fallback, token-aware request cleanup, usage visibility, and seamless format translation so local agents, IDE assistants, and automation scripts can use free and premium LLM capacity through one stable API surface.

> **Project status:** Stable. Version `1.0.0` establishes the supported SDK routes, canonical management routes, configuration names, and single-instance runtime contract. Future compatibility changes follow Semantic Versioning.

## Why Omni Gateway

Modern coding workflows often mix clients and providers: OpenAI-compatible tools, Gemini-native SDKs, Anthropic-style agents, Google-backed credentials, and experimental model routes. Omni Gateway sits between those clients and model backends so each tool can keep speaking the format it already understands while the gateway handles routing, retries, request cleanup, and response normalization.

## Core Capabilities

- Smart auto-fallback: reserves credentials per request, spreads concurrent traffic, tracks every attempt for fair rotation, and routes around recent failures, cooldowns, rate limits, and exhausted capacity.
- Token-aware cleanup: normalizes payloads and trims only oversized conversation prefixes at safe turn boundaries while preserving system instructions, tool definitions, and recent context.
- Format translation: accepts OpenAI Chat Completions and Responses, Gemini native requests, and Anthropic Messages, then translates requests and streaming responses across formats.
- Credential orchestration: manages OAuth accounts and provider API keys with health state, cooldown tracking, verification, deduplication, and provider-aware fallback.
- Streaming resilience: supports SSE streaming, pseudo-streaming for clients that require streamed output, and anti-truncation retries for long generations.
- Control panel: ships with a web console for credentials, logs, configuration, usage, and version information.

## Console Preview

![Omni Gateway credential pool](docs/assets/screenshots/credential-pool.png)

## Architecture

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | IDE integrations
        |
        v
Omni Gateway
  authentication -> format translation -> token-aware cleanup -> routing -> fallback -> streaming
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok | xAI Console | Code Assist | Vertex-compatible route
```

The public API stays stable while provider-specific adapters evolve behind Omni Gateway.

## Repository Structure

```text
backend/       FastAPI composition root, routing core, translators, storage, and tests
frontend/      Management console markup, styles, scripts, and provider assets
deploy/        Container definitions, platform manifests, and operating-system scripts
docs/          Architecture notes and maintained project assets
.github/       CI, dependency automation, and contribution templates
```

See [Architecture](docs/architecture.md) for module boundaries, request flow, state ownership, and current release constraints.

## Deployment

Omni Gateway is intended for real deployments. Docker is the recommended path for VPS and server environments because it keeps the runtime isolated while preserving credentials and logs on the host.

### Docker on a VPS

Create persistent host directories first:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Start the service:

```bash
sudo docker run -d \
  --name omni-gateway \
  --pull always \
  --restart unless-stopped \
  -p 4283:4283 \
  -v /opt/omni-gateway/creds:/app/backend/data/creds \
  -v /opt/omni-gateway/logs:/app/backend/data/logs \
  nguywnben/omni-gateway:1.0.0
```

The same release is published to GitHub Packages as `ghcr.io/nguywnben/omni-gateway:1.0.0`. The `latest` tag tracks the newest stable release; `edge` tracks verified but unreleased builds from `main`. Pin a version tag or digest when reproducible deployment matters.

Open the control panel at:

```text
http://YOUR_SERVER_IP:4283
```

On first run, create the console password on the setup screen. No default password is shipped. A remote browser must also enter the bootstrap token printed by `docker logs omni-gateway`; direct localhost setup does not require it. Set `SETUP_TOKEN` before startup when deployment automation needs a stable bootstrap token.

Passwords managed by the application are stored as salted scrypt hashes, control-panel sessions use HttpOnly cookies, and public SDK requests authenticate with the generated `sk-ogw-` API key. For a non-interactive deployment, preconfigure `PANEL_PASSWORD` and skip the setup screen entirely.

The `1.0.0` container is published for `linux/amd64`. ARM64 publication is intentionally paused until every provider dependency, including the Vertex transport stack, can be built and tested with the same contract.

If the server firewall is enabled, allow the gateway port:

```bash
sudo ufw allow 4283/tcp
```

View logs:

```bash
sudo docker logs -f omni-gateway
```

Update to the newest stable image:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Then start the container again with the same `docker run` command above. The mounted `/opt/omni-gateway` directories preserve credentials, configuration, usage data, and logs across container updates.

### Docker Compose

For repository-based deployments:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

The included compose file pulls `nguywnben/omni-gateway:latest` and uses `/opt/omni-gateway` by default for persistent host data. Set `IMAGE=nguywnben/omni-gateway:1.0.0` to pin this release, and set `DATA_DIR=/custom/path` when the server uses a different storage location.

Compose forwards `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, external storage URIs, and `PROXY` from the shell or a root `.env` file. Leave them empty to retain automatic key generation, first-run setup, local SQLite storage, and direct outbound networking.

### Local Development

Use the Python workflow when developing or debugging the gateway locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Open the control panel at:

```text
http://127.0.0.1:4283
```

Local development uses the same first-run setup screen as the Docker deployment.

## Configuration

Omni Gateway reads configuration from environment variables first, then stored configuration, then defaults.

| Variable | Default | Purpose |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Bind address. |
| `PORT` | `4283` | HTTP port. |
| `HOST_PORT` | `4283` | Host-side port used only by Docker Compose. |
| `WORKERS` | `1` | Supported worker count for 1.x. Other values are rejected until reservations, cooldowns, sessions, and usage aggregation are coordinated across processes. |
| `CORS_ORIGINS` | empty | Comma-separated browser origins allowed to call the API cross-origin. Leave empty for same-origin console usage. |
| `CORS_ORIGIN_REGEX` | empty | Optional regex for managed dynamic browser origins. |
| `API_KEY` | generated automatically | Preferred key for public client API requests. Must start with `sk-ogw-`. |
| `PANEL_PASSWORD` | empty until setup | Password for the web control panel. |
| `SETUP_TOKEN` | generated per process | Optional fixed bootstrap token required for remote first-run setup. When omitted, read the generated token from application or container logs. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Web console session lifetime in seconds. |
| `PANEL_COOKIE_SECURE` | automatic | Set `true` to require HTTPS-only panel cookies. Leave empty to detect HTTPS through `X-Forwarded-Proto`. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Login rate-limit window in seconds. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Failed login attempts allowed per client within the rate-limit window. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Maximum client addresses retained by the in-memory login limiter. |
| `MAX_REQUEST_BODY_MB` | `64` | Maximum HTTP request body size in MiB. Oversized SDK requests return the native protocol error envelope. |
| `TRUST_PROXY_HEADERS` | `false` | Accept client/protocol forwarding headers only from a trusted reverse proxy that overwrites them. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Credential storage directory. In Docker, persist `/app/backend/data/creds` with a host volume. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist backend endpoint. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Google Antigravity backend endpoint. |
| `PROXY` | empty | Optional HTTP, HTTPS, or SOCKS proxy. |
| `RETRY_429_ENABLED` | `true` | Retry rate-limited requests. |
| `RETRY_429_MAX_RETRIES` | `5` | Maximum rate-limit retry attempts. |
| `RETRY_429_INTERVAL` | `1` | Delay between retries in seconds. |
| `AUTO_DISABLE` | `false` | Disable credentials after configured hard failures. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Comma-separated hard-failure status codes. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced` or `priority`. |
| `PREFERRED_PROVIDER` | empty | Provider preferred by the `priority` strategy, such as `google_antigravity` or `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Provider inference timeout, bounded between 5 and 900 seconds. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Maximum continuation attempts for anti-truncation streaming. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Compress oversized conversation history before provider routing. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Estimated input-token threshold that activates compression. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Estimated input-token target after compression. Must be lower than the threshold. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Minimum number of recent user turns retained during compression. |
| `COMPATIBILITY_MODE` | `false` | Converts system messages for clients/models that reject them. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Include model reasoning fields when available. |
| `MONGODB_URI` | empty | Enables MongoDB storage when set. |
| `POSTGRESQL_URI` | empty | Enables PostgreSQL storage when set. |
| `REDIS_URL` | empty | Enables Redis-backed caches/session state when set. |
| `CODE_ASSIST_CLIENT_ID` | bundled desktop client | Optional override for the Code Assist OAuth client ID. |
| `CODE_ASSIST_CLIENT_SECRET` | bundled desktop client | Optional override for the Code Assist OAuth client secret. |
| `ANTIGRAVITY_CLIENT_ID` | bundled desktop client | Optional override for the Google Antigravity OAuth client ID. It can also be managed from the Providers page. |
| `ANTIGRAVITY_CLIENT_SECRET` | bundled desktop client | Optional override for the Google Antigravity OAuth client secret. Configure it through env or the Providers page when the upstream client changes. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Optional Google AI Studio Generative Language API endpoint override. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Optional xAI inference and model-catalog endpoint override. It can also be managed from the Providers page. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Optional xAI OAuth issuer override. Only HTTPS hosts under `x.ai` are accepted by the console. |
| `XAI_CLIENT_ID` | bundled public client | Optional override for the xAI PKCE OAuth client ID. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Optional xAI OAuth and API transport User-Agent override. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Optional Google Antigravity protocol User-Agent override. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Optional payload-level Google Antigravity userAgent override. |
| `LOG_LEVEL` | `info` | Runtime log level. |
| `LOG_MAX_MB` | `10` | Maximum active log file size before rotation. |
| `LOG_BACKUP_COUNT` | `3` | Number of rotated log files retained. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | File log destination. In Docker, persist `/app/backend/data/logs` with a host volume. |

## SDK Surfaces

Omni Gateway is designed around the standard URL behavior of the official Python SDKs. Configure each client exactly as shown below; the gateway does not require non-standard duplicated path prefixes.

The examples use the virtual model `omway`. Configure its ordered provider-model fallback on the Models page first, or replace it with a concrete model ID.

### OpenAI Python SDK

Use `/v1` as the OpenAI base URL. The SDK appends `/chat/completions`.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Explain this repository in one paragraph."}],
)
```

The same client can use the OpenAI Responses API:

```python
response = client.responses.create(
    model="omway",
    instructions="Be concise.",
    input="Explain this repository in one paragraph.",
)

print(response.output_text)
```

Responses compatibility supports text, image inputs, non-streaming function tools, and SSE text streaming. OpenAI-hosted built-in tools, stored response history, and streaming function calls are rejected explicitly because Omni Gateway does not execute, persist, or silently discard those OpenAI-specific behaviors.

### Anthropic Python SDK

Use the gateway origin as the Anthropic base URL. The SDK appends `/v1/messages`.

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="omway",
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
    model="omway",
    contents="Write a small Python function.",
    config=types.GenerateContentConfig(
        system_instruction="You are a helpful assistant.",
    ),
)
```

### Supported Routes

Omni Gateway exposes SDK-compatible routes without a product namespace:

- `POST /v1/chat/completions`
- `POST /v1/responses`
- `POST /v1/messages`
- `GET /v1/models`
- `GET /v1beta/models`
- `POST /v1beta/models/{model}:generateContent`
- `POST /v1beta/models/{model}:streamGenerateContent`
- `POST /v1beta/models/{model}:countTokens`
- `POST /vertex/v1/chat/completions`
- `POST /vertex/v1/models/{model}:generateContent`

Authentication, request-validation, routing, upstream, and pre-stream failures use the native error envelope for the selected SDK surface. Every HTTP response includes `X-Request-ID`; clients may supply a safe identifier in that header for end-to-end correlation. Rate-limited and temporarily unavailable responses preserve `Retry-After` when the upstream provides it.

## Model Features

The Models page builds the virtual model `omway` from models discovered across enabled provider credentials. Arrange its members in priority order once, then use `omway` from any supported SDK. Omni Gateway balances healthy credentials that support the first model and continues through the configured model order when that model is unavailable. Concrete provider model IDs remain available for clients that need deterministic model selection. Saving an empty selection disables `omway` without affecting provider credentials.

Model discovery is provider-aware: a shared model can be backed by multiple providers, while provider-specific models only use compatible credentials. Refreshing the catalog rechecks current provider availability; unavailable selections remain visible in the configuration until they are restored or removed.

Omni Gateway recognizes feature prefixes and suffixes in model names:

- `fake-streaming/{model}` or the configured pseudo-streaming prefix for clients that require SSE output.
- `streaming-anti-truncation/{model}` or the configured anti-truncation prefix for long-form streaming recovery.
- Thinking suffixes such as `-high`, `-medium`, `-low`, `-minimal`, and `-max` for supported Gemini-family models.
- Search suffixes such as `-search` for models that support Google Search grounding.

Provider adapters normalize these feature names before sending upstream requests.

## Usage and Cost Visibility

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, and estimated tokens removed by context compression for each dashboard time range. Compression savings are labeled as estimates because provider tokenizers and billing rules remain authoritative. Provider price-based routing is intentionally left as a future policy layer so the core API remains stable as more providers are added.

## Credential Workflow

1. Start Omni Gateway.
2. Open `http://YOUR_SERVER_IP:4283` on a VPS, or `http://127.0.0.1:4283` for local development.
3. Create the console password on the first-run setup screen. For remote setup, enter the bootstrap token from the application logs; alternatively preconfigure `PANEL_PASSWORD`.
4. Add a Google Antigravity account, Google AI Studio API key, xAI OAuth account, or xAI API key from the Providers page.
5. Verify credentials and watch cooldown/error state in the panel.
6. Point your coding tool to one of the API surfaces above.

When adding Google Antigravity credentials, Google redirects the browser to `http://localhost:4283/callback` after sign-in. On a local machine, Omni Gateway shows an OAuth success page. On a VPS, that `localhost` address belongs to the user's browser machine, so the page may not load; copy the full URL from the browser address bar, return to the Providers page, paste it into `Callback URL`, and click `Save credentials`.

Google AI Studio uses API-key authentication instead of OAuth. Add a key from the Providers page; Omni Gateway validates it against Google's model catalog, stores it as a provider credential, and routes compatible Gemini or Gemma requests through it. The smart router can fall back between AI Studio and Google Antigravity for shared Gemini models while keeping provider-specific models on compatible credentials.

Google AI Studio batch import accepts JSON files and ZIP archives containing JSON files. A JSON document may contain one key, an `api_keys` array, or an array of key objects:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Every imported key is validated before storage. Duplicate keys within the same import are skipped, existing keys are revalidated and updated, and invalid entries are reported without exposing the key value.

Grok supports PKCE OAuth credentials, while xAI Console supports API keys. xAI Console keys are validated against the xAI model catalog before storage. For Grok OAuth, Omni Gateway generates an authorization link that redirects to `http://127.0.0.1:56121/callback`; after authorization, copy the complete callback URL from the browser and paste it into the Grok OAuth form. Access tokens are refreshed automatically when a refresh token is available, and both credential types expose only the Grok models declared by their current catalog.

Pool and Google Antigravity imports accept archives up to 10 MB, at most 500 files, individual credential files up to 2 MB, and at most 25 MB of uncompressed data. Google AI Studio uses stricter limits of 2 MB per upload, 200 JSON entries, and 5 MB of uncompressed data.

The Pool page also provides a provider-independent backup workflow. `Download ZIP` exports the active credential pool, and `Import ZIP` restores that archive by identifying each credential as Google Antigravity, Google AI Studio, Grok, or xAI Console. OAuth accounts retain provider-scoped email-and-expiry deduplication, while API keys are validated and deduplicated by a provider-scoped, non-reversible key fingerprint. Unsupported or malformed entries are reported individually without blocking valid credentials in the same archive.

Google Antigravity credentials use `google-antigravity-{account_fingerprint}.json`, where the fingerprint is derived from the normalized account email without exposing it. Google AI Studio credentials use `google-ai-studio-{key_fingerprint}.json`, Grok OAuth credentials use `grok-{account_fingerprint}.json`, and xAI Console credentials use `xai-console-{key_fingerprint}.json`. Legacy `provider_*.json` and `xai-grok-*.json` credentials remain compatible and are exported with canonical names.

Credential mode names:

- `code_assist`: standard Code Assist credential pool.
- `provider`: provider backend credential pool.

## Storage

Single-instance deployments use SQLite-backed storage in the mounted data directory. On Docker, keep `/app/backend/data/creds` and `/app/backend/data/logs` mounted to durable host paths such as `/opt/omni-gateway/creds` and `/opt/omni-gateway/logs`.

MongoDB or PostgreSQL can replace local SQLite for operational preference or migration testing:

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

External storage does not make the 1.x runtime horizontally scalable. Run one worker and one replica until distributed credential reservations, cooldowns, session invalidation, and usage aggregation are implemented. Configure either MongoDB or PostgreSQL, not both; an explicit external-database initialization failure stops startup rather than silently falling back to SQLite.

Environment credential import is available from the control panel. Set one of the following variables to raw JSON or use the matching `_B64` variant for base64-encoded JSON:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

The payload can be a single credential object, an array, or `{ "credentials": [...] }`.

## Development

This section is for contributors and local debugging. Production deployments should use Docker with persistent host volumes.

```bash
python -m pip install --require-hashes -r requirements.lock
python -m pip install -r requirements-dev.txt
ruff check backend
ruff format --check backend
python -m compileall -q backend
python -m backend.tests
for script in frontend/js/*.js; do node --check "$script"; done
yamllint --strict .github deploy .yamllint.yml
python -m pip_audit --local --progress-spinner off
```

Start the service after the checks pass:

```bash
python backend/main.py
```

The production baseline is Python 3.12, and CI currently verifies Python 3.12 and 3.14. See [Contributing](CONTRIBUTING.md) for the pull-request workflow and review expectations.

## Deployment Notes

- Never commit credential JSON files or `.env`.
- Use a dedicated `API_KEY` for client integrations and a separate `PANEL_PASSWORD` for console access.
- Restrict access to the persistent credential volume or external database and enable platform-level encryption at rest; provider tokens must remain retrievable by the router.
- Put Omni Gateway behind a reverse proxy with TLS when reachable outside localhost.
- Configure the reverse proxy to preserve `Host` and pass `X-Forwarded-Proto`; set `PANEL_COOKIE_SECURE=true` when HTTPS termination is guaranteed.
- Set `TRUST_PROXY_HEADERS=true` only when the service is reachable exclusively through a trusted proxy that replaces `X-Forwarded-For` and `X-Forwarded-Proto`.
- Use `GET /health` for process liveness and `GET /ready` for storage-aware readiness checks.
- The Docker image starts as root only long enough to repair mounted data-directory ownership, then runs the service as the unprivileged `gateway` user.
- Set `CORS_ORIGINS` to explicit trusted origins when browser clients need cross-origin access.
- Keep `/opt/omni-gateway` or your chosen `DATA_DIR` backed up before upgrading or moving servers.
- Docker image publishing uses the `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets for Docker Hub, and the built-in `GITHUB_TOKEN` for GitHub Packages at `ghcr.io/nguywnben/omni-gateway`. Set the optional `IMAGE_NAME` repository variable only when publishing to a custom Docker Hub image name.
- Keep `WORKERS=1` and one application replica for the 1.x series; external storage is not a substitute for distributed coordination.
- Use the canonical `/api/credentials` management routes. The beta `/api/creds` aliases were removed in 1.0.0.
- Follow [Upgrading to 1.0](docs/upgrading-to-1.0.md) before migrating a beta deployment.
- Follow the maintained [release checklist](docs/release-checklist.md) before tagging or promoting an image.
- Keep log retention and credential rotation policies aligned with your usage limits.
- Rotate credentials immediately if a repository or platform scanner reports a leaked secret.
- The Render Blueprint uses a paid service with a persistent disk. Render free services use ephemeral filesystems and are suitable only for disposable evaluation.

## Community and Project Health

- Read [Contributing](CONTRIBUTING.md) before opening a pull request.
- Report vulnerabilities through the private process in [Security Policy](SECURITY.md).
- Review [Changelog](CHANGELOG.md) for release-level changes.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md) in all project spaces.

## License

Omni Gateway is released under the [MIT License](LICENSE).
