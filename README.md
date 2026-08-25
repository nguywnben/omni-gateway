<div align="center">
  <h1>
    <img src="frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Universal AI Router & Unified Multi-Provider Gateway for AI Coding Tools</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#supported-providers"><b>🌐 Supported Providers</b></a> •
    <a href="#core-capabilities"><b>⚡ Capabilities</b></a> •
    <a href="#deployment"><b>🐳 Docker Deployment</b></a> •
    <a href="#quick-start-sdk-integration"><b>🔌 SDK Setup</b></a> •
    <a href="docs/architecture.md"><b>📖 Architecture</b></a>
  </p>

  <p>
    <b>Console & Documentation Languages:</b><br>
    <b>English</b> •
    <a href="docs/locales/README.vi.md">Tiếng Việt</a> •
    <a href="docs/locales/README.zh-CN.md">中文(简体)</a> •
    <a href="docs/locales/README.zh-TW.md">中文(繁體)</a> •
    <a href="docs/locales/README.ja.md">日本語</a> •
    <a href="docs/locales/README.ko.md">한국어</a> •
    <a href="docs/locales/README.es.md">Español</a> •
    <a href="docs/locales/README.fr.md">Français</a> •
    <a href="docs/locales/README.de.md">Deutsch</a> •
    <a href="docs/locales/README.it.md">Italiano</a> •
    <a href="docs/locales/README.pt.md">Português</a> •
    <a href="docs/locales/README.ru.md">Русский</a> •
    <a href="docs/locales/README.id.md">Indonesia</a> •
    <a href="docs/locales/README.th.md">ภาษาไทย</a> •
    <a href="docs/locales/README.tr.md">Türkçe</a>
  </p>
</div>

---

A universal AI router for coding tools. Omni Gateway provides smart auto-fallback, token-aware request cleanup, usage visibility, and seamless format translation so local agents, IDE assistants, and automation scripts can use free and premium LLM capacity through one stable API surface.

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Why Omni Gateway

Modern coding workflows often mix clients and providers: OpenAI-compatible tools, Gemini-native SDKs, Anthropic-style agents, Google-backed credentials, and experimental model routes. Omni Gateway sits between those clients and model backends so each tool can keep speaking the format it already understands while the gateway handles routing, retries, request cleanup, and response normalization.

## Core Capabilities

- Smart auto-fallback: reserves credentials per request, spreads concurrent traffic, tracks every attempt for fair rotation, and routes around recent failures, cooldowns, rate limits, and exhausted capacity.
- Token-aware cleanup: normalizes payloads and trims only oversized conversation prefixes at safe turn boundaries while preserving system instructions, tool definitions, and recent context.
- Format translation: accepts OpenAI Chat Completions and Responses, Gemini native requests, and Anthropic Messages, then translates requests and streaming responses across formats.
- Credential orchestration: manages OAuth accounts and provider API keys with health state, cooldown tracking, verification, deduplication, and provider-aware fallback.
- Credential-level model routing: keeps a separate capability catalog for each credential, so one account's entitlement cannot send a request to another account that does not expose the selected model.
- Route health memory: records model-not-found responses at credential scope and exposes the affected routes for recovery from the Models page.
- Streaming resilience: supports SSE streaming, pseudo-streaming for clients that require streamed output, and anti-truncation retries for long generations.
- Routing strategies: balanced, provider priority, weighted random, least latency, and lowest cost credential selection.
- Virtual API keys: scoped client keys with daily and monthly USD budgets, per-minute request and token limits, expiry, and model allowlists.
- Cost ledger: estimated USD cost per call from a maintained model pricing table, aggregated on the dashboard and in Prometheus metrics.
- Guardrails: optional pre-call prompt-injection blocking, keyword filtering, and PII masking before requests leave the gateway.
- Response caching: optional exact-match caching of deterministic requests to reduce latency and provider spend.
- Observability: Prometheus `/metrics` endpoint and optional Langfuse trace export alongside the built-in usage dashboard.
- Control panel: ships with a web console for credentials, logs, configuration, usage, and version information.

## Console Preview

![Omni Gateway credential pool](docs/assets/screenshots/credential-pool.png)

## Supported Providers

Omni Gateway adapts requests seamlessly across leading AI providers, local runtime engines, and OAuth endpoints:

| Provider | Auth Type | Supported Protocols | Auto-Failover | Streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Local / Self-hosted)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

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
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
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
  nguywnben/omni-gateway:1.4.0
```

The same release is published to GitHub Packages as `ghcr.io/nguywnben/omni-gateway:1.4.0`. The `latest` tag tracks the newest stable release; `edge` tracks verified but unreleased builds from `main`. Pin a version tag or digest when reproducible deployment matters.

Open the control panel at:

```text
http://YOUR_SERVER_IP:4283
```

On first run, create the console password on the setup screen. No default password is shipped. A remote browser must also enter the bootstrap token printed by `docker logs omni-gateway`; direct localhost setup does not require it. Set `SETUP_TOKEN` before startup when deployment automation needs a stable bootstrap token.

Passwords managed by the application are stored as salted scrypt hashes, control-panel sessions use HttpOnly cookies, and public SDK requests authenticate with the generated `sk-ogw-` API key. For a non-interactive deployment, preconfigure `PANEL_PASSWORD` and skip the setup screen entirely.

The `1.4.0` container is published for `linux/amd64`. ARM64 publication is intentionally paused until every provider dependency, including the Vertex transport stack, can be built and tested with the same contract.

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

The included compose file pulls `nguywnben/omni-gateway:latest` and uses `/opt/omni-gateway` by default for persistent host data. Set `IMAGE=nguywnben/omni-gateway:1.4.0` to pin this release, and set `DATA_DIR=/custom/path` when the server uses a different storage location.

Compose forwards `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, external storage URIs, and `PROXY` from the shell or a root `.env` file. Leave them empty to retain automatic key generation, first-run setup, local SQLite storage, and direct outbound networking.

### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.

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
| `RETRY_429_ENABLED` | `true` | Enable bounded retries for rate limits and transient upstream failures. The legacy name is retained for configuration compatibility. |
| `RETRY_429_MAX_RETRIES` | `5` | Maximum retry attempts for transient upstream failures. |
| `RETRY_429_INTERVAL` | `1` | Base delay between transient retries in seconds. |
| `AUTO_DISABLE` | `false` | Disable credentials after configured hard failures. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Comma-separated hard-failure status codes. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | empty | Provider preferred by the `priority` strategy, such as `google_antigravity` or `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Provider inference timeout, bounded between 5 and 900 seconds. |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
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
| `XAI_API_URL` | `https://api.x.ai/v1` | Optional SpaceXAI Console API endpoint override for API-key credentials. It can also be managed from the Providers page. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Optional Grok Build OAuth subscription endpoint override. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Optional Grok Build OAuth issuer override. Only HTTPS hosts under `x.ai` are accepted by the console. |
| `XAI_CLIENT_ID` | bundled public client | Optional override for the Grok Build PKCE OAuth client ID. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Optional shared HTTP User-Agent override for Grok Build OAuth and SpaceXAI Console API requests. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Optional OpenAI Platform API endpoint override. It can also be managed from the Providers page. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Optional Codex inference and account-model endpoint override. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Optional Codex account rate-limit endpoint override. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Optional Codex device-authorization service override. |
| `CODEX_CLIENT_ID` | bundled public client | Optional override for the Codex device OAuth client ID. |
| `CODEX_USER_AGENT` | Codex CLI-compatible value | Optional User-Agent override for Codex requests. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Optional Claude Platform and Claude Code Messages API endpoint override. It can also be managed from the Providers page. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Optional Claude Code PKCE authorization endpoint override. Only Anthropic and Claude hosts are accepted by the console. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Optional Claude Code token endpoint override. Only Anthropic and Claude hosts are accepted by the console. |
| `CLAUDE_CLIENT_ID` | bundled public client | Optional override for the Claude Code PKCE OAuth client ID. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Optional User-Agent override for Claude Code and Claude Platform requests. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Optional Google Antigravity protocol User-Agent override. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Optional payload-level Google Antigravity userAgent override. |
| `METRICS_TOKEN` | empty | Optional bearer token required to scrape `GET /metrics`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
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

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

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

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

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
    api_key="sk-ogw-...",
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

Model discovery is provider-aware: a shared model can be backed by multiple providers, while provider-specific models only use compatible credentials. Each verified credential stores its own provider catalog, and the router gives declared credential support priority over generic provider inference. Refreshing the catalog rechecks current provider availability; unavailable selections remain visible in the configuration until they are restored or removed.

When an upstream returns `404` for a concrete model, Omni Gateway records an unavailable route for that credential and model rather than suppressing the entire provider. The route is temporarily avoided immediately and remains visible under **Unavailable Model Routes** until it is removed or the credential is revalidated. This prevents one account's subscription or regional entitlement from affecting other accounts at the same provider. If no enabled credential declares or can infer support for a requested concrete model, the gateway returns a clear no-compatible-credential error instead of sending the request to a random provider.

Omni Gateway recognizes feature prefixes and suffixes in model names:

- `fake-streaming/{model}` or the configured pseudo-streaming prefix for clients that require SSE output.
- `streaming-anti-truncation/{model}` or the configured anti-truncation prefix for long-form streaming recovery.
- Thinking suffixes such as `-high`, `-medium`, `-low`, `-minimal`, and `-max` for supported Gemini-family models.
- Search suffixes such as `-search` for models that support Google Search grounding.

Provider adapters normalize these feature names before sending upstream requests.

## Usage and Cost Visibility

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## Credential Workflow

1. Start Omni Gateway.
2. Open `http://YOUR_SERVER_IP:4283` on a VPS, or `http://127.0.0.1:4283` for local development.
3. Create the console password on the first-run setup screen. For remote setup, enter the bootstrap token from the application logs; alternatively preconfigure `PANEL_PASSWORD`.
4. Add an account, API key, or Ollama connection from the Providers page.
5. Verify credentials and watch cooldown/error state in the panel.
6. Point your coding tool to one of the API surfaces above.

When adding a Google Antigravity credential, Google redirects the browser to `http://localhost:4283/callback` after sign-in. On a local machine, Omni Gateway shows an OAuth success page. On a VPS, that `localhost` address belongs to the user's browser machine, so the page may not load; copy the full URL from the browser address bar, return to the Providers page, paste it into `Callback URL`, and click `Save credential`.

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

Grok Build supports PKCE OAuth credentials, while SpaceXAI Console supports API keys. SpaceXAI Console keys are validated against the Grok Build model catalog before storage. For Grok Build OAuth, Omni Gateway generates an authorization link; after authorization, copy the code displayed on the Grok Build authorization page and paste it into the Grok Build OAuth form. Access tokens are refreshed automatically when a refresh token is available, and both credential types expose only the Grok Build models declared by their current catalog. The Pool page can retrieve monthly credit usage and, when xAI provides it, weekly usage for Grok Build OAuth accounts. This account-level billing view is not available for SpaceXAI Console API keys.

Codex uses OpenAI's device authorization flow. Generate a device code from the Providers page, open the displayed verification URL, enter the code, finish sign-in, and return to check authorization. Omni Gateway stores the account-scoped model catalog returned by Codex, refreshes OAuth access tokens when needed, and sends compatible requests through the Codex Responses transport. OpenAI Platform uses API-key authentication; keys are validated through the account model catalog before entering the pool. Both products support JSON and ZIP import with provider-specific validation and deduplication.

Claude Code uses Anthropic's PKCE OAuth flow. Generate an authorization link, finish authorization, then paste the returned authorization code into the Providers page. Claude Platform accepts Anthropic API keys. Both products discover the models exposed to each credential, use the Anthropic Messages transport, refresh Claude Code access tokens when possible, and support validated JSON or ZIP import.

Ollama connections are configured per endpoint and may include an optional bearer API key for protected or cloud servers. Omni Gateway discovers models through `/api/tags` and routes inference through `/api/chat`. When Omni Gateway runs in Docker, `localhost` refers to the container itself; use a host-gateway address or another network-reachable Ollama endpoint.

Pool imports and Google Antigravity batch imports accept archives up to 10 MB, at most 500 files, individual credential files up to 2 MB, and at most 25 MB of uncompressed data. Google AI Studio, OpenAI, Anthropic, and Ollama provider imports use stricter limits of 2 MB per imported file, 200 JSON entries, and 5 MB of uncompressed data.

The Pool page also provides a provider-independent backup workflow. `Download ZIP` exports the active credential pool, and `Import ZIP` restores that archive by identifying each credential as Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform, or Ollama. OAuth accounts retain provider-scoped identity deduplication, while API keys are validated and deduplicated by a provider-scoped, non-reversible key fingerprint. Unsupported or malformed entries are reported individually without blocking valid credentials in the same archive.

Google Antigravity credentials use `google-antigravity-{account_fingerprint}.json`, where the fingerprint is derived from the normalized account email without exposing it. Google AI Studio credentials use `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth credentials use `grok-{account_fingerprint}.json`, SpaceXAI Console credentials use `xai-console-{key_fingerprint}.json`, Codex credentials use `openai-codex-{account_fingerprint}.json`, OpenAI Platform credentials use `openai-platform-{key_fingerprint}.json`, Claude Code credentials use `claude-code-{account_fingerprint}.json`, Claude Platform credentials use `claude-platform-{key_fingerprint}.json`, and Ollama connections use `ollama-{connection_fingerprint}.json`. Legacy `provider_*.json` and `xai-grok-*.json` credentials remain compatible and are exported with canonical names.

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
- Use `GET /metrics` for Prometheus scraping; set `METRICS_TOKEN` to require bearer authentication outside trusted networks.
- The Docker image starts as root only long enough to repair mounted data-directory ownership, then runs the service as the unprivileged `gateway` user.
- Set `CORS_ORIGINS` to explicit trusted origins when browser clients need cross-origin access.
- Keep `/opt/omni-gateway` or your chosen `DATA_DIR` backed up before upgrading or moving servers.
- Docker image publishing uses the `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets for Docker Hub, and the built-in `GITHUB_TOKEN` for GitHub Packages at `ghcr.io/nguywnben/omni-gateway`. Set the optional `IMAGE_NAME` repository variable only when publishing to a custom Docker Hub image name.
- Keep `WORKERS=1` and one application replica for the 1.x series; external storage is not a substitute for distributed coordination.
- Use the canonical `/api/credentials` management routes. The beta `/api/creds` aliases were removed in 1.0.0.
- Follow [Upgrading to 1.0](docs/upgrading-to-1.0.md) before migrating a beta deployment.
- Follow the [update guide](docs/updating.md) when upgrading a deployed instance or rolling back a release.
- Follow the maintained [release checklist](docs/release-checklist.md) before tagging or promoting an image.
- Keep log retention and credential rotation policies aligned with your usage limits.
- Rotate credentials immediately if a repository or platform scanner reports a leaked secret.
- The Render Blueprint uses a paid service with a persistent disk. Render free services use ephemeral filesystems and are suitable only for disposable evaluation.

## Community and Project Health

- Read [Contributing](CONTRIBUTING.md) before opening a pull request.
- Report vulnerabilities through the private process in [Security Policy](SECURITY.md).
- Review [Changelog](CHANGELOG.md) for release-level changes.
- Follow the [Code of Conduct](CODE_OF_CONDUCT.md) in all project spaces.

## Acknowledgements & Inspirations

Omni Gateway stands on the shoulders of the open-source AI routing, telemetry, and gateway community. We express our gratitude to the creators and maintainers of these projects:

| Project | Description | Stars |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Inspiration for multi-provider key management and web-based API aggregation | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Pioneering multi-format proxy and protocol translation layer for AI coding CLIs | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Standard-setting unified LLM proxy, load balancing, and fallback routing | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Ultra-fast AI gateway architecture, routing strategies, and resilient fallback patterns | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Open-source LLM engineering platform, tracing, observability, and metrics ingestion | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## License

Omni Gateway is released under the [MIT License](LICENSE).
