<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Universeller KI-Router & einheitliches Multi-Provider-Gateway für KI-Coding-Tools</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#unterstuetzte-anbieter"><b>🌐 Unterstützte Anbieter</b></a> •
    <a href="#kernfunktionen"><b>⚡ Kernfunktionen</b></a> •
    <a href="#bereitstellung"><b>🐳 Docker-Bereitstellung</b></a> •
    <a href="#schnellstart-sdk-integration"><b>🔌 SDK-Integration</b></a> •
    <a href="../architecture.md"><b>📖 Architektur</b></a>
  </p>

  <p>
    <b>Konsolen- & Dokumentationssprachen:</b><br>
    <a href="../../README.md">English</a> •
    <a href="README.vi.md">Tiếng Việt</a> •
    <a href="README.zh-CN.md">中文(简体)</a> •
    <a href="README.zh-TW.md">中文(繁體)</a> •
    <a href="README.ja.md">日本語</a> •
    <a href="README.ko.md">한국어</a> •
    <a href="README.es.md">Español</a> •
    <a href="README.fr.md">Français</a> •
    <b>Deutsch</b> •
    <a href="README.it.md">Italiano</a> •
    <a href="README.pt.md">Português</a> •
    <a href="README.ru.md">Русский</a> •
    <a href="README.id.md">Indonesia</a> •
    <a href="README.th.md">ภาษาไทย</a> •
    <a href="README.tr.md">Türkçe</a>
  </p>
</div>

---

Ein universeller KI-Router für Coding-Tools. Omni Gateway bietet intelligentes Auto-Fallback, tokenbewusste Kontextbereinigung, Nutzungstransparenz und nahtlose Formatübersetzung, sodass lokale Agenten, IDE-Assistenten und Automatisierungsskripte kostenlose und kostenpflichtige LLM-Kapazitäten über eine einzige stabile API-Schnittstelle nutzen können.

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Warum Omni Gateway

Moderne Entwicklungs-Workflows kombinieren oft mehrere Clients und Anbieter: OpenAI-kompatible Tools, native Gemini-SDKs, Agenten im Anthropic-Stil, Google-gestützte Anmeldedaten und experimentelle Modellrouten. Omni Gateway positioniert sich zwischen diesen Clients und den Modell-Backends, sodass jedes Tool das Format beibehalten kann, das es bereits versteht, während das Gateway Routing, Wiederholungsversuche, Anfragebereinigung und Antwortnormalisierung übernimmt.

## <a id="kernfunktionen"></a>Kernfunktionen

- **Intelligentes Auto-Fallback (Smart Auto-Fallback):** Reserviert Anmeldedaten pro Anfrage, verteilt gleichzeitigen Datenverkehr, erfasst jeden Versuch für eine faire Rotation und umgeht automatisch kürzliche Fehler, Abkühlzeiten (Cooldowns), Ratenbegrenzungen und erschöpfte Kontingente.
- **Tokenbewusste Bereinigung (Token-Aware Cleanup):** Normalisiert Payloads und schneidet nur überlange Konversationspräfixe an sicheren Dialoggrenzen ab, während Systemanweisungen, Tool-Definitionen und der jüngste Kontext vollständig erhalten bleiben.
- **Formatübersetzung:** Akzeptiert OpenAI Chat Completions und Responses, native Gemini-Anfragen sowie Anthropic Messages und übersetzt Anfragen und Streaming-Antworten nahtlos zwischen allen Formaten.
- **Orchestrierung von Anmeldedaten:** Verwaltet OAuth-Konten und Anbieter-API-Schlüssel mit Zustandsüberwachung, Cooldown-Tracking, Validierung, Deduplizierung und anbieterspezifischem Fallback.
- **Modell-Routing auf Anmeldedatenebene:** Führt einen separaten Funktionskatalog für jeden Anmeldedatensatz, sodass die Berechtigung eines Kontos keine Anfrage an ein anderes Konto senden kann, das das ausgewählte Modell nicht unterstützt.
- **Routen-Gesundheitsspeicher (Route Health Memory):** Speichert „Modell nicht gefunden“-Antworten auf Anmeldedatenebene und zeigt betroffene Routen zur Wiederherstellung auf der Models-Seite an.
- **Streaming-Ausfallsicherheit:** Unterstützt SSE-Streaming, Pseudo-Streaming für Clients, die zwingend Stream-Ausgaben erfordern, und Anti-Truncation-Wiederholungen für lange Textgenerierungen.
- **Steuerungskonsole (Control Panel):** Bietet eine browserbasierte Konsole zur Verwaltung von Anmeldedaten, Protokollen, Konfigurationen, Nutzungsstatistiken und Versionsinformationen.

## Konsolen-Vorschau

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## <a id="unterstuetzte-anbieter"></a>Unterstützte Anbieter

Omni Gateway passt Anfragen nahtlos an führende KI-Anbieter, lokale Laufzeitumgebungen und OAuth-Endpunkte an:

| Anbieter | Authentifizierungsart | Unterstützte Protokolle | Auto-Failover | Streaming-Unterstützung |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API-Schlüssel | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API-Schlüssel | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API-Schlüssel | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API-Schlüssel | OpenAI-kompatibel, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API-Schlüssel | OpenAI-kompatibel | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Lokal / Self-hosted)** | Lokal / Basis-URL | OpenAI-kompatibel | ✅ | ✅ |

## Architektur

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | IDE-Integrationen
        |
        v
Omni Gateway
  Authentifizierung -> Formatübersetzung -> tokenbewusste Bereinigung -> Routing -> Fallback -> Streaming
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

Die öffentliche API bleibt stabil, während sich die anbieterspezifischen Adapter unter Omni Gateway kontinuierlich weiterentwickeln.

## Repository-Struktur

```text
backend/       FastAPI-Kompositions-Root, Routing-Kern, Übersetzer, Speicher und Tests
frontend/      Verwaltungskonsolen-Markup, Styles, Skripte und Anbieter-Grafiken
deploy/        Container-Definitionen, Plattform-Manifeste und Betriebssystem-Skripte
docs/          Architekturhinweise und gepflegte Projektdokumentation
.github/       CI, Abhängigkeitsautomatisierung und Vorlagen für Beiträge
```

Siehe [Architektur](../architecture.md) für Modulgrenzen, Anfragefluss, Zustandsverwaltung und aktuelle Release-Vorgaben.

## <a id="bereitstellung"></a>Bereitstellung

Omni Gateway ist für reale Produktivumgebungen konzipiert. Docker ist der empfohlene Weg für VPS- und Serverumgebungen, da es die Laufzeitumgebung isoliert und Anmeldedaten sowie Protokolle dauerhaft auf dem Host sichert.

### Docker auf einem VPS

Erstellen Sie zunächst persistente Host-Verzeichnisse:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Starten Sie den Dienst:

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

Derselbe Release wird auch auf GitHub Packages als `ghcr.io/nguywnben/omni-gateway:1.4.0` veröffentlicht. Der Tag `latest` verweist auf den neuesten stabilen Release; `edge` verweist auf verifizierte, unveröffentlichte Builds aus dem Branch `main`. Pinnen Sie einen Versions-Tag oder Digest für reproduzierbare Deployments.

Öffnen Sie das Control Panel unter:

```text
http://IHRE_SERVER_IP:4283
```

Erstellen Sie beim ersten Start das Konsolenpasswort im Setup-Bildschirm. Ein Standardpasswort ist nicht vorkonfiguriert. Bei Remote-Zugriff über einen Browser muss zudem das Bootstrap-Token eingegeben werden, das in `docker logs omni-gateway` ausgegeben wird; bei direktem Localhost-Setup entfällt diese Abfrage. Setzen Sie `SETUP_TOKEN` vor dem Start, wenn Bereitstellungsautomatisierungen ein festes Token benötigen.

Vom Gateway verwaltete Passwörter werden als gesalzene scrypt-Hashes gespeichert, Konsolensitzungen nutzen HttpOnly-Cookies und öffentliche SDK-Anfragen authentifizieren sich mit dem generierten `sk-ogw-`-API-Schlüssel. Für nicht-interaktive Bereitstellungen konfigurieren Sie `PANEL_PASSWORD` vor, um den Setup-Bildschirm vollständig zu überspringen.

Der Container `1.4.0` ist für `linux/amd64` veröffentlicht. Die ARM64-Veröffentlichung ist vorübergehend pausiert, bis alle Anbieter-Abhängigkeiten, einschließlich des Vertex-Transport-Stacks, nach denselben Standards gebaut und getestet werden können.

Falls die Server-Firewall aktiv ist, geben Sie den Gateway-Port frei:

```bash
sudo ufw allow 4283/tcp
```

Logs anzeigen:

```bash
sudo docker logs -f omni-gateway
```

Auf das neueste stabile Image aktualisieren:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Starten Sie den Container anschließend mit demselben obigen `docker run`-Befehl neu. Die gemounteten Verzeichnisse `/opt/omni-gateway` behalten Anmeldedaten, Konfiguration, Nutzungsdaten und Logs über Container-Updates hinweg bei.

### Docker Compose

Für repositorybasierte Bereitstellungen:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

Die enthaltene Compose-Datei zieht `nguywnben/omni-gateway:latest` und verwendet standardmäßig `/opt/omni-gateway` für persistente Host-Daten. Setzen Sie `IMAGE=nguywnben/omni-gateway:1.4.0`, um diese Version festzulegen, und setzen Sie `DATA_DIR=/benutzerdefinierter/pfad`, wenn der Server einen anderen Speicherort nutzt.

Compose leitet `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, externe Speicher-URIs und `PROXY` aus der Shell oder einer Stammverzeichnis-`.env`-Datei weiter. Lassen Sie diese leer, um automatische Schlüsselerzeugung, Erst-Setup, lokalen SQLite-Speicher und direkte Netzwerkverbindungen beizubehalten.


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.


### Lokale Entwicklung

Nutzen Sie den Python-Workflow bei lokaler Entwicklung oder Fehlersuche:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Unter Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Öffnen Sie das Control Panel unter:

```text
http://127.0.0.1:4283
```

Die lokale Entwicklungsumgebung nutzt denselben Einrichtungsbildschirm wie das Docker-Deployment.

## Konfiguration

Omni Gateway liest Konfigurationen vorrangig aus Umgebungsvariablen, danach aus gespeicherten Einstellungen und schließlich aus Standardwerten.

| Umgebungsvariable | Standardwert | Zweck |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Bind-Adresse. |
| `PORT` | `4283` | HTTP-Port. |
| `HOST_PORT` | `4283` | Host-seitiger Port, der nur von Docker Compose verwendet wird. |
| `WORKERS` | `1` | Unterstützte Worker-Anzahl für die 1.x-Serie. Andere Werte werden abgewiesen, bis Reservierungen, Cooldowns, Sitzungen und Nutzungsdaten prozessübergreifend koordiniert werden. |
| `CORS_ORIGINS` | leer | Kommagetrennte Browser-Origins für zulässige Cross-Origin-API-Aufrufe. Leer lassen für Same-Origin-Konsolennutzung. |
| `CORS_ORIGIN_REGEX` | leer | Optionaler regulärer Ausdruck für dynamisch verwaltete Browser-Origins. |
| `API_KEY` | automatisch generiert | Bevorzugter Schlüssel für öffentliche Client-API-Anfragen. Muss mit `sk-ogw-` beginnen. |
| `PANEL_PASSWORD` | leer bis zur Einrichtung | Passwort für das Web-Control-Panel. |
| `SETUP_TOKEN` | pro Prozess generiert | Optionales festes Bootstrap-Token für die Remote-Ersteinrichtung. Wenn weggelassen, Token aus den Anwendungs- oder Container-Logs lesen. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Lebensdauer von Webkonsolen-Sitzungen in Sekunden. |
| `PANEL_COOKIE_SECURE` | automatisch | Auf `true` setzen, um reine HTTPS-Panel-Cookies zu erzwingen. Leer lassen, um HTTPS über `X-Forwarded-Proto` zu erkennen. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Zeitfenster für Login-Ratenbegrenzung in Sekunden. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Maximal zulässige fehlgeschlagene Login-Versuche pro Client innerhalb des Zeitfensters. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Maximale Anzahl an Client-Adressen, die im In-Memory-Login-Limiter gespeichert werden. |
| `MAX_REQUEST_BODY_MB` | `64` | Maximale HTTP-Request-Body-Größe in MiB. Zu große SDK-Anfragen geben die native Protokoll-Fehlerstruktur zurück. |
| `TRUST_PROXY_HEADERS` | `false` | Client-/Protokoll-Forwarding-Header nur von einem vertrauenswürdigen Reverse-Proxy akzeptieren, der diese überschreibt. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Verzeichnis für Anmeldedaten. In Docker `/app/backend/data/creds` als Host-Volume mounten. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Backend-Endpunkt für Code Assist. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Backend-Endpunkt für Google Antigravity. |
| `PROXY` | leer | Optionaler HTTP-, HTTPS- oder SOCKS-Proxy. |
| `RETRY_429_ENABLED` | `true` | Aktiviert begrenzte Wiederholungsversuche bei Ratenbegrenzungen und vorübergehenden Upstream-Fehlern. Legacy-Name aus Kompatibilitätsgründen beibehalten. |
| `RETRY_429_MAX_RETRIES` | `5` | Maximale Anzahl an Wiederholungsversuchen bei vorübergehenden Upstream-Fehlern. |
| `RETRY_429_INTERVAL` | `1` | Basisverzögerung zwischen vorübergehenden Wiederholungsversuchen in Sekunden. |
| `AUTO_DISABLE` | `false` | Deaktiviert Anmeldedaten nach konfigurierten schwerwiegenden Fehlern. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Kommagetrennte Statuscodes für schwerwiegende Fehler. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | leer | Bevorzugter Anbieter bei `priority`-Strategie, z. B. `google_antigravity` oder `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Timeout für Anbieter-Inferenz, begrenzt zwischen 5 und 900 Sekunden. |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Maximale Fortsetzungsversuche für Anti-Truncation-Streaming. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Komprimiert überlange Konversationshistorien vor dem Routing an den Anbieter. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Geschätzter Eingabe-Token-Schwellenwert zur Aktivierung der Komprimierung. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Geschätztes Eingabe-Token-Ziel nach der Komprimierung. Muss niedriger als der Schwellenwert sein. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Mindestanzahl jüngster Benutzer-Interaktionen, die bei der Komprimierung erhalten bleiben. |
| `COMPATIBILITY_MODE` | `false` | Wandelt Systemnachrichten für Clients/Modelle um, die diese nicht unterstützen. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Gibt Modell-Denkprozesse (Reasoning) zurück, wenn verfügbar. |
| `MONGODB_URI` | leer | Aktiviert MongoDB-Speicher, wenn gesetzt. |
| `POSTGRESQL_URI` | leer | Aktiviert PostgreSQL-Speicher, wenn gesetzt. |
| `REDIS_URL` | leer | Aktiviert Redis-basiertes Caching / Sitzungszustand, wenn gesetzt. |
| `CODE_ASSIST_CLIENT_ID` | integrierter Desktop-Client | Optionales Überschreiben der Code Assist OAuth Client-ID. |
| `CODE_ASSIST_CLIENT_SECRET` | integrierter Desktop-Client | Optionales Überschreiben des Code Assist OAuth Client-Secrets. |
| `ANTIGRAVITY_CLIENT_ID` | integrierter Desktop-Client | Optionales Überschreiben der Google Antigravity OAuth Client-ID. Auch über die Providers-Seite verwaltbar. |
| `ANTIGRAVITY_CLIENT_SECRET` | integrierter Desktop-Client | Optionales Überschreiben des Google Antigravity OAuth Client-Secrets. Über Env oder Providers-Seite konfigurierbar. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Optionales Überschreiben des Generative Language API-Endpunkts von Google AI Studio. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Optionales Überschreiben des SpaceXAI Console API-Endpunkts für API-Schlüssel. Über die Providers-Seite verwaltbar. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Optionales Überschreiben des Grok Build OAuth-Abonnement-Endpunkts. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Optionales Überschreiben des Grok Build OAuth-Ausstellers. Nur HTTPS-Hosts unter `x.ai` werden akzeptiert. |
| `XAI_CLIENT_ID` | integrierter öffentlicher Client | Optionales Überschreiben der Grok Build PKCE OAuth Client-ID. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Optionales gemeinsames HTTP-User-Agent-Überschreiben für Grok Build OAuth- und SpaceXAI Console API-Anfragen. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Optionales Überschreiben des OpenAI Platform API-Endpunkts. Auch über die Providers-Seite verwaltbar. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Optionales Überschreiben des Codex Inferenz- und Kontomodell-Endpunkts. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Optionales Überschreiben des Codex Konto-Ratenbegrenzungs-Endpunkts. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Optionales Überschreiben des Codex Geräteautorisierungsdienstes. |
| `CODEX_CLIENT_ID` | integrierter öffentlicher Client | Optionales Überschreiben der Codex Geräte-OAuth-Client-ID. |
| `CODEX_USER_AGENT` | Codex CLI-kompatibler Wert | Optionales User-Agent-Überschreiben für Codex-Anfragen. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Optionales Überschreiben des Messages API-Endpunkts von Claude Platform und Claude Code. Über Providers verwaltbar. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Optionales Überschreiben des Claude Code PKCE-Autorisierungsendpunkts. Nur Anthropic- und Claude-Hosts erlaubt. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Optionales Überschreiben des Claude Code Token-Endpunkts. Nur Anthropic- und Claude-Hosts erlaubt. |
| `CLAUDE_CLIENT_ID` | integrierter öffentlicher Client | Optionales Überschreiben der Claude Code PKCE OAuth Client-ID. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Optionales User-Agent-Überschreiben für Claude Code- und Claude Platform-Anfragen. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Optionales User-Agent-Überschreiben für das Google Antigravity Protokoll. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Optionales User-Agent-Überschreiben auf Payload-Ebene für Google Antigravity. |
| `METRICS_TOKEN` | empty | Optional bearer token required to scrape `GET /metrics`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | Protokollierungsgrad (Log-Level). |
| `LOG_MAX_MB` | `10` | Maximale Dateigröße des aktiven Logs vor der Rotation. |
| `LOG_BACKUP_COUNT` | `3` | Anzahl der aufbewahrten rotierten Protokolldateien. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Pfad zur Protokolldatei. In Docker `/app/backend/data/logs` als Host-Volume mounten. |

## <a id="schnellstart-sdk-integration"></a>SDK-Schnittstellen

Omni Gateway orientiert sich am standardmäßigen URL-Verhalten der offiziellen Python-SDKs. Konfigurieren Sie jeden Client genau wie unten dargestellt; das Gateway erfordert keine unüblichen doppelten Pfadpräfixe.

Die folgenden Beispiele verwenden das virtuelle Modell `omway`. Konfigurieren Sie dessen geordnete Fallback-Reihenfolge zuerst auf der Models-Seite oder ersetzen Sie es durch eine konkrete Modell-ID.

### OpenAI Python SDK

Verwenden Sie `/v1` als Basis-URL für OpenAI. Das SDK hängt automatisch `/chat/completions` an.

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Erkläre dieses Repository in einem Absatz."}],
)
```

Derselbe Client kann auch die OpenAI Responses API verwenden:

```python
response = client.responses.create(
    model="omway",
    instructions="Fasse dich kurz.",
    input="Erkläre dieses Repository in einem Absatz.",
)

print(response.output_text)
```

Die Responses-Kompatibilität unterstützt Text, Bildeingaben, nicht-streamende Function-Tools und SSE-Text-Streaming. Von OpenAI gehostete integrierte Tools, gespeicherte Antworthistorien und streamende Funktionsaufrufe werden explizit abgelehnt, da Omni Gateway diese OpenAI-spezifischen Verhaltensweisen weder ausführt, speichert noch stillschweigend verwirft.

### Anthropic Python SDK

Verwenden Sie den Gateway-Origin als Basis-URL für Anthropic. Das SDK hängt automatisch `/v1/messages` an.

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Entwirf eine prägnante Commit-Nachricht."}],
)
```

### Google GenAI Python SDK

Verwenden Sie den Gateway-Origin als Basis-URL für Google GenAI. Das SDK hängt automatisch die Standard-Modellroute an, z. B. `/v1beta/models/{model}:generateContent`.

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
    contents="Schreibe eine kleine Python-Funktion.",
    config=types.GenerateContentConfig(
        system_instruction="Du bist ein hilfreicher Assistent.",
    ),
)
```

### Unterstützte Routen

Omni Gateway stellt SDK-kompatible Routen ohne produktbezogene Namespaces bereit:

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

Fehler bei Authentifizierung, Anfragevalidierung, Routing, Upstream-Aufrufen sowie Fehler vor dem Stream-Start verwenden die native Fehlerstruktur der jeweiligen SDK-Schnittstelle. Jede HTTP-Antwort enthält den Header `X-Request-ID`; Clients können eine sichere Kennung übergeben, um Anfragen durchgängig zu verfolgen. Ratenbegrenzte oder temporär nicht verfügbare Antworten behalten den Header `Retry-After` bei, wenn der Upstream-Anbieter ihn bereitstellt.

## Modellfunktionen

Die Seite Models erstellt das virtuelle Modell `omway` aus den Modellen, die über aktivierte Anmeldedaten ermittelt wurden. Ordnen Sie die Modellmitglieder einmalig nach Priorität und verwenden Sie anschließend `omway` in jedem unterstützten SDK. Omni Gateway verteilt die Last auf gesunde Anmeldedaten, die das erste Modell unterstützen, und probiert bei Nichtverfügbarkeit die konfigurierte Reihenfolge durch. Konkrete Modell-IDs der Anbieter bleiben für deterministische Modellauswahlen verfügbar. Das Speichern einer leeren Liste deaktiviert `omway`, ohne die Anmeldedaten der Anbieter zu beeinträchtigen.

Die Modellerkennung erfolgt anbietersensitiv: Ein geteiltes Modell kann von mehreren Anbietern unterstützt werden, während anbieterspezifische Modelle nur kompatible Anmeldedaten nutzen. Jeder verifizierte Anmeldedatensatz speichert seinen eigenen Anbieterkatalog, und der Router bevorzugt explizit deklarierte Unterstützung vor allgemeinen Anbieterannahmen. Das Aktualisieren des Katalogs prüft die aktuelle Anbieterverfügbarkeit erneut; nicht verfügbare Auswahlen bleiben in der Konfiguration sichtbar, bis sie wiederhergestellt oder gelöscht werden.

Gibt ein Upstream einen `404`-Fehler für ein konkretes Modell zurück, registriert Omni Gateway eine nicht verfügbare Route für diesen Anmeldedatensatz und dieses Modell, anstatt den gesamten Anbieter zu deaktivieren. Diese Route wird sofort temporär umgangen und bleibt unter **Unavailable Model Routes** sichtbar, bis sie gelöscht oder der Anmeldedatensatz neu validiert wird. Dadurch wird verhindert, dass konto- oder regionsspezifische Einschränkungen andere Konten desselben Anbieters beeinträchtigen. Falls kein aktivierter Anmeldedatensatz das angeforderte Modell unterstützt, gibt das Gateway einen klaren Fehler zurück, anstatt die Anfrage an einen beliebigen Anbieter zu leiten.

Omni Gateway erkennt Funktionspräfixe und -suffixe in Modellnamen:

- `fake-streaming/{model}` oder das konfigurierte Pseudo-Streaming-Präfix für Clients, die zwingend SSE-Ausgaben benötigen.
- `streaming-anti-truncation/{model}` oder das konfigurierte Anti-Truncation-Präfix zur automatischen Wiederherstellung bei langen Streaming-Generierungen.
- Thinking-Suffixe wie `-high`, `-medium`, `-low`, `-minimal` und `-max` für unterstützte Modelle der Gemini-Familie.
- Such-Suffixe wie `-search` für Modelle mit Google Search Grounding-Unterstützung.

Anbieter-Adapter normalisieren diese Funktionsnamen vor dem Weiterleiten an Upstream-Dienste.

## Nutzung und Kostentransparenz

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## Workflow für Anmeldedaten

1. Starten Sie Omni Gateway.
2. Öffnen Sie `http://IHRE_SERVER_IP:4283` auf einem VPS oder `http://127.0.0.1:4283` bei lokaler Entwicklung.
3. Erstellen Sie das Konsolenpasswort im Ersteinrichtungs-Bildschirm. Geben Sie bei Remote-Setup das Bootstrap-Token aus den Logs ein oder konfigurieren Sie `PANEL_PASSWORD` vor.
4. Fügen Sie Konten, API-Schlüssel oder Ollama-Verbindungen auf der Seite Providers hinzu.
5. Verifizieren Sie Anmeldedaten und überwachen Sie Cooldown- und Fehlerzustände in der Konsole.
6. Richten Sie Ihr Entwicklungs-Tool auf eine der oben genannten API-Schnittstellen aus.

Beim Hinzufügen von Google Antigravity-Anmeldedaten leitet Google den Browser nach dem Login zu `http://localhost:4283/callback` weiter. Auf einem lokalen Rechner zeigt Omni Gateway eine OAuth-Erfolgsseite an. Auf einem VPS gehört diese `localhost`-Adresse zum Browser-Rechner des Nutzers, sodass die Seite eventuell nicht lädt; kopieren Sie die vollständige URL aus der Adressleiste des Browsers, kehren Sie zur Seite Providers zurück, fügen Sie sie in `Callback URL` ein und klicken Sie auf `Save credential`.

Google AI Studio nutzt API-Schlüssel-Authentifizierung anstelle von OAuth. Fügen Sie einen Schlüssel über die Seite Providers hinzu; Omni Gateway validiert ihn anhand des Modellkatalogs von Google, speichert ihn als Anbieter-Anmeldedatensatz und leitet kompatible Gemini- oder Gemma-Anfragen darüber weiter. Der intelligente Router kann bei gemeinsamen Gemini-Modellen zwischen AI Studio und Google Antigravity wechseln, während modellspezifische Anfragen auf kompatiblen Zugängen verbleiben.

Der Google AI Studio-Batch-Import akzeptiert JSON-Dateien und ZIP-Archive, die JSON-Dateien enthalten. Ein JSON-Dokument kann einen einzelnen Schlüssel, ein `api_keys`-Array oder ein Array von Schlüsselobjekten enthalten:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Jeder importierte Schlüssel wird vor dem Speichern validiert. Duplikate innerhalb desselben Imports werden übersprungen, bestehende Schlüssel neu validiert und aktualisiert und ungültige Einträge gemeldet, ohne den Schlüsselwert preiszugeben.

Grok Build unterstützt PKCE-OAuth-Anmeldedaten, während SpaceXAI Console API-Schlüssel unterstützt. Schlüssel der SpaceXAI Console werden vor dem Speichern anhand des Grok Build-Modellkatalogs validiert. Für Grok Build OAuth generiert Omni Gateway einen Autorisierungslink; kopieren Sie nach der Autorisierung den auf der Seite angezeigten Code und fügen Sie ihn in das Grok Build-Formular ein. Zugriffstokens werden automatisch aktualisiert, wenn ein Refresh-Token vorhanden ist, und beide Anmeldedatentypen zeigen nur die Modelle an, die in ihrem aktuellen Katalog deklariert sind. Die Pool-Seite kann monatliche Guthabennutzung und wöchentliche Nutzung (sofern von xAI bereitgestellt) für Grok Build OAuth-Konten abrufen. Diese Abrechnungsansicht auf Kontoebene ist für SpaceXAI Console API-Schlüssel nicht verfügbar.

Codex verwendet den Geräteautorisierungs-Flow von OpenAI. Generieren Sie einen Gerätecode auf der Seite Providers, öffnen Sie die angezeigte Verifizierungs-URL, geben Sie den Code ein, schließen Sie die Anmeldung ab und prüfen Sie die Autorisierung. Omni Gateway speichert den von Codex zurückgegebenen kontospezifischen Modellkatalog, aktualisiert OAuth-Tokens bei Bedarf und sendet kompatible Anfragen über den Codex Responses-Transport. OpenAI Platform nutzt API-Schlüssel-Authentifizierung; Schlüssel werden vor der Aufnahme in den Pool über den Kontomodellkatalog validiert. Beide Produkte unterstützen JSON- und ZIP-Importe mit anbieterspezifischer Validierung und Deduplizierung.

Claude Code verwendet den PKCE-OAuth-Flow von Anthropic. Generieren Sie einen Autorisierungslink, schließen Sie die Autorisierung ab und fügen Sie den erhaltenen Code auf der Seite Providers ein. Claude Platform akzeptiert Anthropic-API-Schlüssel. Beide Produkte erkennen die für die Anmeldedaten verfügbaren Modelle, nutzen den Anthropic Messages-Transport, aktualisieren Tokens von Claude Code, wenn möglich, und unterstützen validierte JSON- oder ZIP-Importe.

Ollama-Verbindungen werden pro Endpunkt konfiguriert und können einen optionalen Bearer-API-Schlüssel für geschützte oder Cloud-Server enthalten. Omni Gateway erkennt Modelle über `/api/tags` und leitet Inferenzen über `/api/chat`. Wenn Omni Gateway in Docker läuft, bezieht sich `localhost` auf den Container selbst; verwenden Sie eine Host-Gateway-Adresse oder einen netzwerkweit erreichbaren Ollama-Endpunkt.

Pool-Importe und Google Antigravity-Batch-Importe akzeptieren Archive bis zu 10 MB, maximal 500 Dateien, einzelne Anmeldedateien bis zu 2 MB und maximal 25 MB unkomprimierte Daten. Für Google AI Studio, OpenAI, Anthropic und Ollama gelten strengere Limits: 2 MB pro Datei, 200 JSON-Einträge und 5 MB unkomprimierte Daten.

Die Pool-Seite bietet zudem einen anbieterunabhängigen Backup-Workflow. `Download ZIP` exportiert den gesamten aktiven Anmeldedaten-Pool, und `Import ZIP` stellt dieses Archiv wieder her, indem jeder Anmeldedatensatz automatisch als Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform oder Ollama identifiziert wird. OAuth-Konten behalten ihre anbieterbezogene Identitäts-Deduplizierung bei, während API-Schlüssel über einen nicht umkehrbaren Fingerprint dedupliziert werden. Nicht unterstützte oder fehlerhafte Einträge werden einzeln gemeldet, ohne gültige Daten im selben Archiv zu blockieren.

Google Antigravity-Anmeldedaten verwenden das Format `google-antigravity-{account_fingerprint}.json`, wobei der Fingerprint aus der normalisierten E-Mail-Adresse abgeleitet wird, ohne diese preiszugeben. Google AI Studio verwendet `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth `grok-{account_fingerprint}.json`, SpaceXAI Console `xai-console-{key_fingerprint}.json`, Codex `openai-codex-{account_fingerprint}.json`, OpenAI Platform `openai-platform-{key_fingerprint}.json`, Claude Code `claude-code-{account_fingerprint}.json`, Claude Platform `claude-platform-{key_fingerprint}.json` und Ollama `ollama-{connection_fingerprint}.json`. Legacy-Dateien wie `provider_*.json` und `xai-grok-*.json` bleiben kompatibel und werden mit kanonischen Namen exportiert.

Bezeichnungen der Anmeldemodi (Credential mode names):

- `code_assist`: Standard-Anmeldedatenpool für Code Assist.
- `provider`: Anmeldedatenpool für Anbieter-Backends.

## Speicherung

Single-Process-Bereitstellungen nutzen eine SQLite-basierte Speicherung im gemounteten Datenverzeichnis. Binden Sie unter Docker `/app/backend/data/creds` und `/app/backend/data/logs` stets an persistente Host-Pfade wie `/opt/omni-gateway/creds` und `/opt/omni-gateway/logs`.

MongoDB oder PostgreSQL können lokales SQLite nach betrieblichen Anforderungen oder für Migrationstests ersetzen:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

Redis kann zur Beschleunigung von Cache und Sitzungen hinzugefügt werden:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Externer Speicher macht die 1.x-Laufzeitumgebung nicht horizontal skalierbar. Betreiben Sie nur einen Worker und ein Replikat, bis verteilte Anmeldereservierungen, Cooldowns, Sitzungsinvalidierungen und Nutzungsaggregationen vollständig implementiert sind. Konfigurieren Sie entweder MongoDB oder PostgreSQL, nicht beides; ein Initialisierungsfehler externer Datenbanken stoppt den Startvorgang, anstatt stillschweigend auf SQLite zurückzufallen.

Der Import von Anmeldedaten über Umgebungsvariablen ist über die Konsole verfügbar. Setzen Sie eine der folgenden Variablen auf einen rohen JSON-String oder nutzen Sie die entsprechende `_B64`-Variante für base64-codiertes JSON:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

Die Payload kann ein einzelnes Anmeldeobjekt, ein Array oder `{ "credentials": [...] }` sein.

## Entwicklung

Dieser Abschnitt richtet sich an Mitwirkende und die lokale Fehlersuche. Produktionsbereitstellungen sollten Docker mit persistenten Host-Volumes nutzen.

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

Starten Sie den Dienst, nachdem alle Prüfungen erfolgreich bestanden wurden:

```bash
python backend/main.py
```

Die Produktions-Baseline ist Python 3.12, und CI verifiziert derzeit Python 3.12 und 3.14. Siehe [Beitragende Richtlinien](../../CONTRIBUTING.md) für den Pull-Request-Workflow und Review-Erwartungen.

## Hinweise zur Bereitstellung

- Committen Sie niemals JSON-Dateien mit Anmeldedaten oder `.env`-Dateien.
- Verwenden Sie einen dedizierten `API_KEY` für Client-Integrationen und ein separates `PANEL_PASSWORD` für den Konsolenzugriff.
- Beschränken Sie den Zugriff auf persistente Anmelde-Volumes oder externe Datenbanken und aktivieren Sie Verschlüsselung im Ruhezustand (Encryption at rest); das Gateway muss Tokens der Anbieter im Klartext lesen können.
- Platzieren Sie Omni Gateway hinter einem Reverse-Proxy mit TLS, wenn es außerhalb von localhost erreichbar ist.
- Konfigurieren Sie den Reverse-Proxy so, dass er `Host` beibehält und `X-Forwarded-Proto` weiterleitet; setzen Sie `PANEL_COOKIE_SECURE=true`, wenn HTTPS-Terminierung gewährleistet ist.
- Setzen Sie `TRUST_PROXY_HEADERS=true` nur, wenn der Dienst ausschließlich über einen vertrauenswürdigen Proxy erreichbar ist, der `X-Forwarded-For` und `X-Forwarded-Proto` überschreibt.
- Verwenden Sie `GET /health` für Liveness- und `GET /ready` für speicherbezogene Readiness-Prüfungen.
- Das Docker-Image startet nur kurzzeitig mit Root-Rechten, um Dateiberechtigungen im gemounteten Verzeichnis zu korrigieren, und führt den Dienst dann als unprivilegierter Benutzer `gateway` aus.
- Setzen Sie `CORS_ORIGINS` auf explizite vertrauenswürdige Origins, wenn Browser-Clients Cross-Origin-Zugriff benötigen.
- Sichern Sie stets `/opt/omni-gateway` oder Ihr gewähltes `DATA_DIR` vor Upgrades oder Serverumzügen.
- Die Docker-Image-Veröffentlichung nutzt die Repository-Secrets `DOCKERHUB_USERNAME` und `DOCKERHUB_TOKEN` für Docker Hub sowie das integrierte `GITHUB_TOKEN` für GitHub Packages unter `ghcr.io/nguywnben/omni-gateway`. Setzen Sie die optionale Variable `IMAGE_NAME` nur bei Veröffentlichung unter einem benutzerdefinierten Image-Namen.
- Behalten Sie `WORKERS=1` und ein einzelnes Anwendungsreplikat für die 1.x-Serie bei; externer Speicher ersetzt keine verteilte Koordination.
- Verwenden Sie die kanonischen Verwaltungsrouten `/api/credentials`. Die Beta-Aliase `/api/creds` wurden in Version 1.0.0 entfernt.
- Befolgen Sie die Anleitung [Upgrade auf 1.0](../upgrading-to-1.0.md), bevor Sie eine Beta-Bereitstellung migrieren.
- Befolgen Sie den [Update-Leitfaden](../updating.md), wenn Sie eine Instanz aktualisieren oder auf eine frühere Version zurücksetzen.
- Arbeiten Sie die gepflegte [Release-Checkliste](../release-checklist.md) ab, bevor Sie ein Image taggen oder freigeben.
- Stimmen Sie Log-Aufbewahrung und Anmelderotation auf Ihre Nutzungslimits ab.
- Tauschen Sie Anmeldedaten unverzüglich aus, falls ein Secret-Scanner einen geleakten Schlüssel meldet.
- Das Render-Blueprint nutzt einen kostenpflichtigen Dienst mit persistenter Festplatte. Kostenlose Render-Dienste nutzen flüchtige Dateisysteme und eignen sich nur für kurzzeitige Tests.

## Community und Projektzustand

- Lesen Sie [Beitragen](../../CONTRIBUTING.md), bevor Sie einen Pull Request öffnen.
- Melden Sie Sicherheitslücken über das vertrauliche Verfahren in der [Sicherheitsrichtlinie](../../SECURITY.md).
- Konsultieren Sie das [Änderungsprotokoll](../../CHANGELOG.md) für versionsspezifische Änderungen.
- Befolgen Sie den [Verhaltenskodex](../../CODE_OF_CONDUCT.md) in allen Projektbereichen.

## Danksagungen & Inspirationen

Omni Gateway baut auf der Arbeit der Open-Source-Community für KI-Routing, Telemetrie und Gateways auf. Wir bedanken uns herzlich bei den Entwicklern und Betreuern folgender Projekte:

| Projekt | Beschreibung | Sterne |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Inspiration für Multi-Provider-Schlüsselverwaltung und webbasierte API-Aggregation | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Wegweisende Multi-Format-Proxy- und Protokollübersetzungsschicht für KI-Coding-CLIs | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Maßstabsetzender LLM-Proxy mit Lastverteilung und Fallback-Routing | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Ultraschnelle KI-Gateway-Architektur, Routing-Strategien und ausfallsichere Fallback-Muster | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Open-Source-LLM-Engineering-Plattform, Tracing, Observability und Metrikerfassung | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Lizenz

Omni Gateway ist unter der [MIT-Lizenz](../../LICENSE) lizenziert.