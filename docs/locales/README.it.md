<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Router IA universale e gateway multi-provider unificato per strumenti di sviluppo IA</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20lingue-orange?style=flat-square" alt="15 Lingue">
  </p>

  <p>
    <a href="#provider-supportati"><b>🌐 Provider supportati</b></a> •
    <a href="#funzionalita-principali"><b>⚡ Funzionalità principali</b></a> •
    <a href="#distribuzione"><b>🐳 Distribuzione Docker</b></a> •
    <a href="#guida-rapida-integrazione-sdk"><b>🔌 Integrazione SDK</b></a> •
    <a href="../architecture.md"><b>📖 Architettura</b></a>
  </p>

  <p>
    <b>Lingue della console e documentazione:</b><br>
    <a href="../../README.md">English</a> •
    <a href="README.vi.md">Tiếng Việt</a> •
    <a href="README.zh-CN.md">中文(简体)</a> •
    <a href="README.zh-TW.md">中文(繁體)</a> •
    <a href="README.ja.md">日本語</a> •
    <a href="README.ko.md">한국어</a> •
    <a href="README.es.md">Español</a> •
    <a href="README.fr.md">Français</a> •
    <a href="README.de.md">Deutsch</a> •
    <b>Italiano</b> •
    <a href="README.pt.md">Português</a> •
    <a href="README.ru.md">Русский</a> •
    <a href="README.id.md">Indonesia</a> •
    <a href="README.th.md">ภาษาไทย</a> •
    <a href="README.tr.md">Türkçe</a>
  </p>
</div>

---

Un router IA universale per strumenti di programmazione. Omni Gateway offre failover automatico intelligente (smart auto-fallback), pulizia del contesto sensibile ai token, visibilità sull'utilizzo e conversione fluida dei formati, consentendo ad agenti locali, assistenti IDE e script di automazione di sfruttare la capacità di LLM gratuiti e a pagamento tramite un'unica interfaccia API stabile.

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Perché scegliere Omni Gateway

I moderni flussi di lavoro di sviluppo combinano spesso molteplici client e provider: strumenti compatibili con OpenAI, SDK nativi Gemini, agenti in stile Anthropic, credenziali basate su Google e route di modelli sperimentali. Omni Gateway si posiziona tra tali client e i backend dei modelli, consentendo a ciascuno strumento di comunicare nel formato nativo mentre il gateway gestisce routing, tentativi di ripetizione (retry), pulizia delle richieste e normalizzazione delle risposte.

## <a id="funzionalita-principali"></a>Funzionalità principali

- **Failover automatico intelligente (Smart auto-fallback):** Prenota le credenziali per singola richiesta, distribuisce il traffico concorrente, traccia ogni tentativo per una rotazione equa ed evita automaticamente errori recenti, periodi di raffreddamento (cooldown), limiti di frequenza e quote esaurite.
- **Pulizia sensibile ai token (Token-aware cleanup):** Normalizza i payload e riduce solo i prefissi di conversazione troppo lunghi ai confini sicuri dei turni di dialogo, preservando intatte le istruzioni di sistema, le definizioni dei tool e il contesto recente.
- **Conversione dei formati:** Accetta OpenAI Chat Completions e Responses, richieste native Gemini e Anthropic Messages, traducendo fluidamente tra i formati sia in modalità standard sia in streaming.
- **Orchestrazione delle credenziali:** Gestisce account OAuth e chiavi API dei provider con stato di salute, monitoraggio del cooldown, convalida, deduplicazione e failover intelligente per ciascun provider.
- **Routing dei modelli per singola credenziale:** Mantiene un catalogo di funzionalità dedicato per ciascuna credenziale, impedendo che i permessi di un account inoltrino erroneamente richieste a un altro account privo del modello selezionato.
- **Memoria di salute dei percorsi (Route health memory):** Registra gli errori di modello non trovato (404) a livello di credenziale e mostra i percorsi interessati per il ripristino dalla pagina Modelli.
- **Resilienza dello streaming:** Supporta SSE streaming, pseudo-streaming per client con requisiti di streaming obbligatori e meccanismi di continuazione anti-troncamento (anti-truncation) per generazioni di testo estese.
- **Pannello di controllo:** Include una console web per gestire le credenziali, consultare i log, configurare il sistema, monitorare l'utilizzo e verificare le informazioni sulle versioni.

## Anteprima della console

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## <a id="provider-supportati"></a>Provider supportati

Omni Gateway instrada le richieste in modo trasparente tra i principali provider di IA, runtime locali ed endpoint OAuth:

| Provider | Tipo di autenticazione | Protocolli supportati | Failover automatico | Supporto streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | Compatibile OpenAI, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | Compatibile OpenAI | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Locale / Self-hosted)** | Locale / Base URL | Compatibile OpenAI | ✅ | ✅ |

## Architettura

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | Integrazioni IDE
        |
        v
Omni Gateway
  autenticazione -> conversione formato -> pulizia token -> routing -> failover -> streaming
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

L'API pubblica mantiene la sua stabilità mentre gli adapter specifici per provider evolvono continuamente all'interno di Omni Gateway.

## Struttura del repository

```text
backend/       Radice di composizione FastAPI, core di routing, adapter, persistenza e test
frontend/      Interfaccia console web, stili, script e asset grafici dei provider
deploy/        Definizioni container, manifest di piattaforma e script del sistema operativo
docs/          Note di architettura e documentazione di manutenzione del progetto
.github/       Flussi CI, automazione delle dipendenze e modelli per i contributi
```

Consultare [Architettura](../architecture.md) per i confini dei moduli, il flusso delle richieste, la gestione dello stato e i vincoli attuali di rilascio.

## <a id="distribuzione"></a>Distribuzione

Omni Gateway è progettato per ambienti di produzione reali. Docker è la soluzione consigliata per ambienti VPS e server poiché mantiene il runtime isolato preservando credenziali e log sull'host.

### Docker su VPS

Creare innanzitutto le directory persistenti sull'host:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Avviare il servizio:

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

La stessa release è pubblicata su GitHub Packages come `ghcr.io/nguywnben/omni-gateway:1.4.0`. Il tag `latest` segue la versione stabile più recente; `edge` segue le build verificate ma non rilasciate dal ramo `main`. Fissare un tag di versione specifico o il digest quando è richiesta la riproducibilità.

Aprire il pannello di controllo all'indirizzo:

```text
http://IP_DEL_VOSTRO_SERVER:4283
```

Al primo avvio, creare la password della console nella schermata di configurazione. Non è presente alcuna password predefinita. L'accesso da browser remoto richiede inoltre l'inserimento del bootstrap token mostrato in `docker logs omni-gateway`; la configurazione diretta da localhost non lo richiede. È possibile impostare la variabile `SETUP_TOKEN` prima dell'avvio per l'automazione del deployment.

Le password gestite dall'applicazione sono memorizzate come hash scrypt con salt, le sessioni della console usano cookie HttpOnly e le richieste SDK pubbliche si autenticano tramite chiavi API `sk-ogw-` generate automaticamente. Per distribuzioni non interattive, preconfigurare `PANEL_PASSWORD` per ignorare la schermata iniziale.

Il container `1.4.0` è rilasciato per architettura `linux/amd64`. La pubblicazione ARM64 è temporaneamente sospesa fino a quando tutte le dipendenze dei provider, incluso lo stack di trasporto Vertex, non saranno compilate e testate con gli stessi standard.

Se il firewall del server è attivo, consentire la porta del gateway:

```bash
sudo ufw allow 4283/tcp
```

Visualizzare i log:

```bash
sudo docker logs -f omni-gateway
```

Aggiornare all'immagine stabile più recente:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Riavviare quindi il container con lo stesso comando `docker run` precedente. Le directory montate in `/opt/omni-gateway` manterranno credenziali, configurazioni, dati di utilizzo e log durante gli aggiornamenti del container.

### Docker Compose

Per distribuzioni basate su repository:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

Il file compose incluso scarica `nguywnben/omni-gateway:latest` e utilizza `/opt/omni-gateway` come predefinito per i dati persistenti. Impostare `IMAGE=nguywnben/omni-gateway:1.4.0` per bloccare la versione, e `DATA_DIR=/percorso/personalizzato` se il server usa una cartella differente.

Compose inoltra `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, URI di storage esterno e `PROXY` dalla shell o dal file `.env` principale. Lasciarli vuoti per mantenere generazione automatica delle chiavi, configurazione al primo avvio, storage SQLite locale e connettività diretta in uscita.


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.

### Sviluppo locale

Utilizzare il flusso di lavoro Python per sviluppare o eseguire il debug del gateway in locale:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Su Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Aprire il pannello di controllo all'indirizzo:

```text
http://127.0.0.1:4283
```

L'ambiente di sviluppo locale utilizza la stessa schermata di configurazione iniziale al primo avvio della distribuzione Docker.

## Configurazione

Omni Gateway assegna priorità alle variabili d'ambiente, seguite dalla configurazione salvata e infine dai valori predefiniti.

| Variabile d'ambiente | Valore predefinito | Descrizione |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Indirizzo di ascolto (bind address). |
| `PORT` | `4283` | Porta HTTP. |
| `HOST_PORT` | `4283` | Porta host utilizzata esclusivamente da Docker Compose. |
| `WORKERS` | `1` | Numero di worker supportati per la serie 1.x. Altri valori saranno rifiutati finché prenotazione credenziali, cooldown, sessioni e aggregazione d'uso non saranno coordinati multi-processo. |
| `CORS_ORIGINS` | vuoto | Elenco separato da virgole di origini browser autorizzate a chiamate API cross-origin. Lasciare vuoto per l'uso della console sulla stessa origine. |
| `CORS_ORIGIN_REGEX` | vuoto | Espressione regolare opzionale per origini browser dinamiche. |
| `API_KEY` | autogenerata | Chiave preferita per richieste API client pubbliche. Deve iniziare con `sk-ogw-`. |
| `PANEL_PASSWORD` | vuoto fino a setup | Password per l'accesso al pannello di controllo web. |
| `SETUP_TOKEN` | generato per processo | Token di avvio fisso opzionale per configurazione remota iniziale. Se omesso, leggerlo dai log dell'applicazione o del container. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Durata della sessione della console web in secondi. |
| `PANEL_COOKIE_SECURE` | auto | Impostare su `true` per forzare cookie solo su HTTPS. Lasciare vuoto per rilevamento automatico tramite `X-Forwarded-Proto`. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Finestra del limitatore di frequenza di login in secondi. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Tentativi massimi di login falliti consentiti per client nella finestra di limitazione. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Numero massimo di indirizzi client tracciati in memoria dal limitatore di login. |
| `MAX_REQUEST_BODY_MB` | `64` | Dimensione massima del corpo della richiesta HTTP in MiB. Le richieste che superano il limite restituiranno strutture di errore conformi al rispettivo protocollo. |
| `TRUST_PROXY_HEADERS` | `false` | Accetta gli header di inoltro client/protocollo solo da un reverse proxy affidabile che li sovrascrive. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Directory di archiviazione delle credenziali. In Docker, rendere persistente `/app/backend/data/creds` tramite volumi host. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Endpoint backend di Code Assist. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Endpoint backend di Google Antigravity. |
| `PROXY` | vuoto | Proxy HTTP, HTTPS o SOCKS opzionale. |
| `RETRY_429_ENABLED` | `true` | Abilita tentativi limitati per rate limit ed errori temporanei upstream. Nome storico mantenuto per compatibilità. |
| `RETRY_429_MAX_RETRIES` | `5` | Numero massimo di tentativi per errori temporanei dell'upstream. |
| `RETRY_429_INTERVAL` | `1` | Ritardo base tra i tentativi temporanei in secondi. |
| `AUTO_DISABLE` | `false` | Disabilita automaticamente le credenziali dopo errori gravi configurati. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Elenco separato da virgole dei codici di stato di errore grave. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | vuoto | Provider preferito per la strategia `priority`, ad esempio `google_antigravity` o `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Timeout per la risposta di inferenza del provider (da 5 a 900 secondi). |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Tentativi massimi di continuazione per la funzione di streaming anti-troncamento. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Comprime la cronologia di conversazioni troppo ampie prima dell'inoltro al provider. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Soglia stimata di token in input per attivare la compressione del contesto. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Obiettivo stimato di token in input dopo la compressione. Deve essere inferiore alla soglia di attivazione. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Numero minimo di turni recenti dell'utente da preservare durante la compressione. |
| `COMPATIBILITY_MODE` | `false` | Converte i messaggi di sistema per client/modelli che non li supportano nativamente. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Restituisce il processo di ragionamento del modello (reasoning) quando disponibile. |
| `MONGODB_URI` | vuoto | Abilita il backend di archiviazione MongoDB quando configurato. |
| `POSTGRESQL_URI` | vuoto | Abilita il backend di archiviazione PostgreSQL quando configurato. |
| `REDIS_URL` | vuoto | Abilita la cache / stato di sessione Redis quando configurato. |
| `CODE_ASSIST_CLIENT_ID` | integrato | Override opzionale per il Client ID OAuth di Code Assist. |
| `CODE_ASSIST_CLIENT_SECRET` | integrato | Override opzionale per il Client Secret OAuth di Code Assist. |
| `ANTIGRAVITY_CLIENT_ID` | integrato | Override opzionale per il Client ID OAuth di Google Antigravity. Gestibile anche dalla pagina Provider. |
| `ANTIGRAVITY_CLIENT_SECRET` | integrato | Override opzionale per il Client Secret OAuth di Google Antigravity. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Override opzionale per l'endpoint Generative Language API di Google AI Studio. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Override opzionale per l'endpoint API SpaceXAI Console per credenziali API key. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Override opzionale per l'endpoint di abbonamento Grok Build OAuth. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Override opzionale per l'emittente OAuth di Grok Build. La console accetta solo host HTTPS del dominio `x.ai`. |
| `XAI_CLIENT_ID` | integrato | Override opzionale per il Client ID OAuth PKCE di Grok Build. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Override opzionale per l'User-Agent HTTP condiviso per richieste Grok Build OAuth e API SpaceXAI Console. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Override opzionale per l'endpoint API OpenAI Platform. Gestibile anche dalla pagina Provider. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Override opzionale per l'endpoint di inferenza e catalogo modelli account di Codex. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Override opzionale per l'endpoint di verifica limiti account Codex. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Override opzionale per il servizio di autorizzazione dispositivi di Codex. |
| `CODEX_CLIENT_ID` | integrato | Override opzionale per il Client ID OAuth dispositivi di Codex. |
| `CODEX_USER_AGENT` | compatibile Codex CLI | Override opzionale per l'User-Agent delle richieste Codex. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Override opzionale per l'endpoint API Messages di Claude Platform e Claude Code. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Override opzionale per l'endpoint di autorizzazione PKCE di Claude Code. Solo host Anthropic e Claude. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Override opzionale per l'endpoint token di Claude Code. Solo host Anthropic e Claude. |
| `CLAUDE_CLIENT_ID` | integrato | Override opzionale per il Client ID OAuth PKCE di Claude Code. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Override opzionale per l'User-Agent per richieste Claude Code e Claude Platform. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Override opzionale per l'User-Agent a livello di protocollo Google Antigravity. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Override opzionale per il campo userAgent a livello di payload Google Antigravity. |
| `METRICS_TOKEN` | empty | Optional bearer token required to scrape `GET /metrics`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | Livello di dettaglio dei log (log level). |
| `LOG_MAX_MB` | `10` | Dimensione massima in MB del file di log attivo prima della rotazione. |
| `LOG_BACKUP_COUNT` | `3` | Numero di file di log archiviati dopo la rotazione da conservare. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Percorso del file di log. In Docker, rendere persistente `/app/backend/data/logs` tramite volumi host. |

## <a id="guida-rapida-integrazione-sdk"></a>Guida rapida: Integrazione SDK

Omni Gateway è progettato seguendo il comportamento standard degli URL degli SDK ufficiali Python. Configurare ciascun client esattamente come indicato di seguito; il gateway non richiede prefissi di percorso ridondanti o non standard.

I seguenti esempi utilizzano il modello virtuale `omway`. Configurare preventivamente l'ordine di priorità di fallback modello-provider nella pagina Modelli, oppure sostituirlo con l'ID di un modello specifico.

### OpenAI Python SDK

Utilizzare `/v1` come Base URL per OpenAI. L'SDK aggiungerà automaticamente `/chat/completions`.

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway",
    messages=[
        {"role": "user", "content": "Spiega questo repository di codice in un singolo paragrafo."}
    ],
)
```

Lo stesso client può invocare direttamente l'API OpenAI Responses:

```python
response = client.responses.create(
    model="omway",
    instructions="Rispondi in modo conciso e chiaro.",
    input="Spiega questo repository di codice in un singolo paragrafo.",
)

print(response.output_text)
```

La compatibilità con Responses supporta testo, input di immagini, Function Tools non-streaming e streaming di testo via SSE. Gli strumenti integrati ospitati da OpenAI, la cronologia persistente delle risposte e le chiamate di funzione in streaming saranno rifiutati esplicitamente, poiché Omni Gateway non esegue, memorizza né ignora silenziosamente tali funzionalità proprietarie di OpenAI.

### Anthropic Python SDK

Utilizzare l'origine del gateway come Base URL per Anthropic. L'SDK aggiungerà automaticamente `/v1/messages`.

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Scrivi un messaggio di commit breve."}],
)
```

### Google GenAI Python SDK

Utilizzare l'origine del gateway come Base URL per Google GenAI. L'SDK aggiungerà automaticamente il percorso predefinito del modello, come `/v1beta/models/{model}:generateContent`.

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
    contents="Scrivi una breve funzione in Python.",
    config=types.GenerateContentConfig(
        system_instruction="Sei un assistente utile e competente.",
    ),
)
```

### Endpoint supportati

Omni Gateway fornisce percorsi compatibili con gli SDK standard senza la necessità di prefissi di namespace dedicati:

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

Errori di autenticazione, convalida delle richieste, routing, fallimenti upstream ed errori precedenti all'avvio dello streaming utilizzano le strutture di errore native di ciascuna interfaccia SDK. Tutte le risposte HTTP includono l'header `X-Request-ID`; i client possono inviare un identificatore per tracciare il flusso delle richieste. Le risposte soggette a rate limit o temporaneamente non disponibili conservano l'header `Retry-After` fornito dall'upstream.

## Gestione avanzata dei modelli

La pagina Modelli costruisce il modello virtuale `omway` aggregando i modelli rilevati dalle credenziali dei provider attivi. È sufficiente ordinare le priorità dei modelli una sola volta e richiamare `omway` da qualsiasi SDK supportato. Omni Gateway bilancerà il carico tra le credenziali integre che supportano il modello primario e passerà automaticamente al modello successivo qualora il primo risulti non disponibile. Gli ID specifici dei modelli fisici rimangono accessibili per i client che necessitano di selezioni deterministiche. Il salvataggio di un elenco vuoto disattiva `omway` senza intaccare le credenziali dei provider.

Il rilevamento dei modelli è specifico per ciascun provider: i modelli condivisi possono essere serviti da più provider, mentre i modelli proprietari vengono instradati solo verso credenziali compatibili. Ogni credenziale verificata mantiene il proprio catalogo di provider e il router privilegia il supporto dichiarato esplicitamente dalla credenziale rispetto a deduzioni generiche. L'aggiornamento del catalogo verifica la disponibilità effettiva presso il provider; le opzioni non più disponibili rimangono visibili nella configurazione fino al loro ripristino o alla rimozione manuale.

Quando un upstream restituisce un errore `404` per uno specifico modello fisico, Omni Gateway registra un percorso non disponibile per tale credenziale e modello, anziché disattivare l'intero provider. Quel percorso viene escluso immediatamente ed è visibile sotto **Percorsi modello non disponibili** fino alla cancellazione o alla nuova verifica della credenziale. In questo modo si evita che i limiti di abbonamento o le restrizioni geografiche di un account influiscano sugli altri account dello stesso provider. Se nessuna credenziale abilitata dichiara o deduce il supporto per il modello richiesto, il gateway restituirà un errore esplicito di assenza di credenziali compatibili anziché inviare la richiesta a un provider casuale.

Omni Gateway riconosce prefissi e suffissi di funzionalità nei nomi dei modelli:

- `fake-streaming/{model}` o il prefisso di pseudo-streaming configurato per i client che richiedono obbligatoriamente il formato SSE.
- `streaming-anti-truncation/{model}` o il prefisso di anti-troncamento configurato per il ripristino automatico dello streaming in testi lunghi.
- Suffissi di profondità di ragionamento (come `-high`, `-medium`, `-low`, `-minimal`, `-max`) per i modelli compatibili della famiglia Gemini.
- Suffissi di ricerca come `-search` per i modelli che supportano il grounding con Google Search.

Gli adapter dei provider normalizzano tali identificatori di funzionalità prima di inoltrare la richiesta all'upstream.

## Trasparenza su utilizzo e costi

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## Flusso di lavoro per le credenziali

1. Avviare Omni Gateway.
2. Accedere a `http://IP_DEL_VOSTRO_SERVER:4283` su VPS, oppure `http://127.0.0.1:4283` in locale.
3. Creare la password della console nella schermata di configurazione iniziale. Per installazioni remote, inserire il bootstrap token mostrato nei log; oppure preconfigurare `PANEL_PASSWORD`.
4. Aggiungere account, chiavi API o connessioni Ollama dalla pagina Provider.
5. Verificare la validità delle credenziali e monitorare cooldown ed errori nel pannello.
6. Indirizzare i propri strumenti di sviluppo verso una delle interfacce API sopra descritte.

Quando si aggiungono credenziali Google Antigravity, Google reindirizzerà il browser a `http://localhost:4283/callback` dopo l'autenticazione. In locale, Omni Gateway mostrerà direttamente la pagina di conferma OAuth. Su un VPS, poiché `localhost` fa riferimento alla macchina locale dell'utente, la pagina potrebbe non caricarsi; copiare l'intero URL dalla barra degli indirizzi del browser, tornare alla pagina Provider, incollarlo nel campo `Callback URL` e premere `Salva credenziale`.

Google AI Studio utilizza l'autenticazione tramite chiave API anziché OAuth. Aggiungere una chiave dalla pagina Provider; Omni Gateway ne verificherà la validità rispetto al catalogo modelli di Google, la salverà come credenziale del provider e vi instraderà le richieste compatibili di Gemini o Gemma. Il router intelligente effettua il failover automatico tra AI Studio e Google Antigravity per i modelli Gemini condivisi, mantenendo i modelli proprietari sulle rispettive credenziali.

L'importazione massiva di Google AI Studio accetta file JSON e archivi ZIP contenenti file JSON. I documenti JSON possono contenere una singola chiave, un array `api_keys` o una lista di oggetti chiave:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Ogni chiave importata viene convalidata prima del salvataggio. Le chiavi duplicate all'interno dello stesso lotto vengono ignorate, le chiavi esistenti vengono verificate nuovamente e aggiornate, e le voci non valide vengono segnalate senza mostrare il testo in chiaro della chiave.

Grok Build supporta credenziali OAuth PKCE, mentre SpaceXAI Console supporta chiavi API. Le chiavi SpaceXAI Console vengono convalidate rispetto al catalogo modelli di Grok Build prima di essere memorizzate. Per Grok Build OAuth, Omni Gateway genera un link di autorizzazione; completata l'autorizzazione, copiare il codice mostrato nella pagina di Grok Build e incollarlo nel form. I token di accesso vengono rinnovati automaticamente in presenza di un refresh token, ed entrambi i tipi di credenziali espongono solo i modelli Grok Build dichiarati nei rispettivi cataloghi correnti. La pagina Pool consente di consultare l'utilizzo mensile dei crediti e l'utilizzo settimanale (quando fornito da xAI) per gli account Grok Build OAuth. Questa visualizzazione di fatturazione a livello di account non è disponibile per le API key di SpaceXAI Console.

Codex adotta il flusso di autorizzazione dispositivi di OpenAI. Generare un codice dispositivo dalla pagina Provider, aprire l'URL di verifica mostrato, digitare il codice, completare il login e tornare per verificare l'autorizzazione. Omni Gateway memorizza il catalogo modelli associato all'account restituito da Codex, rinnova i token di accesso OAuth quando necessario e inoltra le richieste compatibili tramite il trasporto Codex Responses. OpenAI Platform utilizza l'autenticazione tramite API Key; le chiavi sono convalidate tramite il catalogo modelli dell'account prima di essere inserite nel pool. Entrambi i prodotti supportano importazioni JSON e ZIP con convalida e deduplicazione specifiche per provider.

Claude Code adotta il flusso OAuth PKCE di Anthropic. Generare il link di autorizzazione, completare il flusso e incollare il codice di autorizzazione ottenuto nella pagina Provider. Claude Platform accetta chiavi API Anthropic. Entrambi i prodotti rilevano i modelli supportati per ciascuna credenziale, utilizzano il trasporto Anthropic Messages, rinnovano i token di accesso di Claude Code quando possibile e supportano importazioni convalidate da file JSON o ZIP.

Le connessioni Ollama sono configurate per singolo endpoint e possono includere una Bearer API Key facoltativa per istanze protette o cloud. Omni Gateway rileva i modelli disponibili tramite `/api/tags` e instrada l'inferenza tramite `/api/chat`. Quando Omni Gateway è in esecuzione all'interno di Docker, `localhost` fa riferimento al container stesso; utilizzare l'indirizzo host-gateway o un endpoint Ollama accessibile via rete.

L'importazione completa del Pool e l'importazione massiva di Google Antigravity accettano archivi fino a 10 MB, per un massimo di 500 file, fino a 2 MB per singolo file di credenziale e fino a 25 MB totali non compressi. Le importazioni dedicate per Google AI Studio, OpenAI, Anthropic e Ollama adottano limiti più restrittivi: 2 MB per file importato, 200 voci JSON e 5 MB di dati non compressi.

La pagina Credential Pool offre inoltre un flusso di backup indipendente dal provider. `Scarica ZIP` esporta l'intero pool di credenziali attive, e `Importa ZIP` ripristina l'archivio identificando automaticamente ciascuna credenziale come Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform o Ollama. Gli account OAuth mantengono la deduplicazione dell'identità all'interno dell'ambito del provider, mentre le chiavi API sono convalidate e deduplicate tramite fingerprint hash irreversibili per provider. Le voci non supportate o con errori di formato vengono segnalate individualmente senza interrompere le altre credenziali valide contenute nell'archivio.

Le credenziali Google Antigravity utilizzano il formato `google-antigravity-{account_fingerprint}.json`, dove il fingerprint è derivato dall'email dell'account normalizzata senza esporre l'email in chiaro. Google AI Studio utilizza `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth utilizza `grok-{account_fingerprint}.json`, SpaceXAI Console utilizza `xai-console-{key_fingerprint}.json`, Codex utilizza `openai-codex-{account_fingerprint}.json`, OpenAI Platform utilizza `openai-platform-{key_fingerprint}.json`, Claude Code utilizza `claude-code-{account_fingerprint}.json`, Claude Platform utilizza `claude-platform-{key_fingerprint}.json` e le connessioni Ollama utilizzano `ollama-{connection_fingerprint}.json`. Le vecchie credenziali conformi a `provider_*.json` e `xai-grok-*.json` rimangono retrocompatibili e vengono esportate con i nomi normalizzati.

Nomi delle modalità credenziali (Credential mode names):

- `code_assist`: pool di credenziali Code Assist standard.
- `provider`: pool di credenziali backend per provider generici.

## Archiviazione dei dati

Le distribuzioni a singolo processo utilizzano per impostazione predefinita lo storage SQLite nella directory dati montata. Su Docker, montare sempre `/app/backend/data/creds` e `/app/backend/data/logs` su percorsi host persistenti quali `/opt/omni-gateway/creds` e `/opt/omni-gateway/logs`.

MongoDB o PostgreSQL possono sostituire l'istanza SQLite locale in base a esigenze operative o test di migrazione:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

È possibile aggiungere Redis per accelerare caching e stato delle sessioni:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

L'archiviazione esterna non rende il runtime 1.x scalabile orizzontalmente. Mantenere un unico worker e una singola replica dell'applicazione fino al rilascio di meccanismi distribuiti per prenotazione credenziali, cooldown, invalidazione sessioni e aggregazione d'uso. Configurare esclusivamente MongoDB o PostgreSQL, mai entrambi contemporaneamente; eventuali errori di inizializzazione dei database esterni arresteranno esplicitamente l'avvio anziché ripiegare silenziosamente su SQLite.

È supportata l'importazione di credenziali tramite variabili d'ambiente direttamente dalla console. Impostare una delle seguenti variabili con una stringa JSON non elaborata o utilizzare la variante con suffisso `_B64` codificata in Base64:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

Il payload può essere un singolo oggetto credenziale, un array o `{ "credentials": [...] }`.

## Guida allo sviluppo

Questa sezione è destinata a contributori e al debug locale. Le installazioni di produzione devono utilizzare Docker con volumi host persistenti.

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

Avviare il servizio una volta superati tutti i controlli:

```bash
python backend/main.py
```

La piattaforma di riferimento per la produzione è Python 3.12, e la CI convalida sia Python 3.12 sia 3.14. Consultare [Contribuire](../../CONTRIBUTING.md) per le linee guida sulle pull request e le aspettative di revisione del codice.

## Note di distribuzione

- Non committare mai file JSON contenenti credenziali né file `.env`.
- Utilizzare una `API_KEY` dedicata per le integrazioni client e una `PANEL_PASSWORD` distinta per l'accesso alla console.
- Limitare i permessi di accesso al volume persistente delle credenziali o al database esterno e attivare la cifratura a riposo (encryption at rest) sulla piattaforma; il router deve poter decifrare e leggere i token dei provider.
- Posizionare Omni Gateway dietro un reverse proxy con TLS attivo quando esposto al di fuori di localhost.
- Configurare il reverse proxy in modo da preservare l'header `Host` e inoltrare `X-Forwarded-Proto`; impostare `PANEL_COOKIE_SECURE=true` una volta garantita la terminazione HTTPS.
- Impostare `TRUST_PROXY_HEADERS=true` unicamente se il servizio è accessibile esclusivamente tramite un proxy fidato che sovrascrive `X-Forwarded-For` e `X-Forwarded-Proto`.
- Utilizzare `GET /health` per i controlli di attività (liveness probe) e `GET /ready` per i controlli di disponibilità con verifica dello storage (readiness probe).
- L'immagine Docker opera come root solo temporaneamente all'avvio per correggere i permessi della cartella dati montata, passando poi all'utente non privilegiato `gateway`.
- Configurare `CORS_ORIGINS` con le origini attendibili esplicite qualora i client web necessitino di accesso cross-origin.
- Eseguire sempre un backup di `/opt/omni-gateway` o della directory `DATA_DIR` configurata prima di aggiornare o migrare il server.
- Il flusso di pubblicazione delle immagini Docker utilizza i secret di repository `DOCKERHUB_USERNAME` e `DOCKERHUB_TOKEN` per Docker Hub, e il `GITHUB_TOKEN` integrato per GitHub Packages su `ghcr.io/nguywnben/omni-gateway`. Impostare la variabile opzionale `IMAGE_NAME` solo se si pubblica con un nome immagine Docker Hub personalizzato.
- Mantenere `WORKERS=1` e una singola replica dell'applicazione per l'intera serie 1.x; lo storage esterno non sostituisce il coordinamento distribuito.
- Utilizzare i percorsi canonici di gestione `/api/credentials`. Le route con alias `/api/creds` della fase beta sono state rimosse a partire dalla 1.0.0.
- Consultare la guida [Aggiornamento a 1.0](../upgrading-to-1.0.md) prima di migrare una distribuzione beta.
- Seguire la [guida all'aggiornamento](../updating.md) durante l'aggiornamento di un'istanza attiva o il ripristino di una versione precedente.
- Seguire la [checklist di rilascio](../release-checklist.md) prima di applicare tag o pubblicare immagini.
- Definire politiche di conservazione dei log e di rotazione delle credenziali adeguate alle proprie quote di utilizzo.
- Revocare e rinnovare immediatamente le credenziali qualora scanner di sicurezza o piattaforme cloud rilevino token esposti.
- Il template Render Blueprint impiega un servizio a pagamento con disco persistente. I piani gratuiti di Render utilizzano file system effimeri e sono idonei solo a test temporanei.

## Community e stato del progetto

- Consultare [Contribuire](../../CONTRIBUTING.md) prima di aprire una pull request.
- Segnalare vulnerabilità di sicurezza tramite il canale privato descritto nell'[Informativa sulla sicurezza](../../SECURITY.md).
- Consultare il [Registro delle modifiche](../../CHANGELOG.md) per l'elenco delle novità di ciascuna versione.
- Rispettare il [Codice di condotta](../../CODE_OF_CONDUCT.md) in tutti gli spazi del progetto.

## Ringraziamenti e ispirazione

Omni Gateway poggia sul lavoro della comunità open source nell'ambito di AI routing, telemetria e gateway. Esprimiamo la nostra più profonda gratitudine ai creatori e manutentori dei seguenti progetti:

| Progetto | Descrizione | Stelle |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Ispirazione per la gestione chiavi multi-provider e l'aggregazione API via console web | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Pioniere nel livello di proxy multi-protocollo e conversione di formati per CLI di coding con IA | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Punto di riferimento nei proxy LLM unificati, bilanciamento del carico e routing con tolleranza d'errore | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Architettura AI gateway ad altissime prestazioni, strategie di routing e modalità di failover avanzate | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Piattaforma open source di LLM engineering, tracciamento delle chiamate, osservabilità e metriche | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Licenza

Omni Gateway è distribuito sotto [Licenza MIT](../../LICENSE).
