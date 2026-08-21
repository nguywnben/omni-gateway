<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Router universal de IA y pasarela multiproveedor unificada para herramientas de desarrollo con IA</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#proveedores-compatibles"><b>🌐 Proveedores compatibles</b></a> •
    <a href="#capacidades-principales"><b>⚡ Capacidades principales</b></a> •
    <a href="#despliegue"><b>🐳 Despliegue Docker</b></a> •
    <a href="#inicio-rapido-integracion-sdk"><b>🔌 Integración SDK</b></a> •
    <a href="../architecture.md"><b>📖 Arquitectura</b></a>
  </p>

  <p>
    <b>Idiomas de la consola y documentación:</b><br>
    <a href="../../README.md">English</a> •
    <a href="README.vi.md">Tiếng Việt</a> •
    <a href="README.zh-CN.md">中文(简体)</a> •
    <a href="README.zh-TW.md">中文(繁體)</a> •
    <a href="README.ja.md">日本語</a> •
    <a href="README.ko.md">한국어</a> •
    <b>Español</b> •
    <a href="README.fr.md">Français</a> •
    <a href="README.de.md">Deutsch</a> •
    <a href="README.it.md">Italiano</a> •
    <a href="README.pt.md">Português</a> •
    <a href="README.ru.md">Русский</a> •
    <a href="README.id.md">Indonesia</a> •
    <a href="README.th.md">ภาษาไทย</a> •
    <a href="README.tr.md">Türkçe</a>
  </p>
</div>

---

Un router de IA universal para herramientas de desarrollo. Omni Gateway ofrece conmutación por error automática inteligente (smart auto-fallback), limpieza de contexto consciente de tokens, visibilidad de uso y traducción de formatos transparente para que los agentes locales, asistentes de IDE y scripts de automatización puedan aprovechar la capacidad de LLM gratuitos y de pago mediante una única interfaz de API estable.

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Por qué elegir Omni Gateway

Los flujos de trabajo de desarrollo modernos a menudo combinan múltiples clientes y proveedores: herramientas compatibles con OpenAI, SDK nativos de Gemini, agentes con estilo de Anthropic, credenciales respaldadas por Google y rutas de modelos experimentales. Omni Gateway se sitúa entre esos clientes y los backends de modelos para que cada herramienta pueda seguir utilizando el formato que ya comprende, mientras la pasarela se encarga del enrutamiento, reintentos, limpieza de solicitudes y normalización de respuestas.

## Capacidades principales

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## Vista previa de la consola

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## Proveedores compatibles

Omni Gateway adapta las solicitudes de forma fluida entre los principales proveedores de IA, entornos locales y endpoints OAuth:

| Proveedor | Tipo de autenticación | Protocolos compatibles | Failover automático | Soporte de streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Local / Autohospedado)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## Arquitectura

```text
herramientas de cliente
  SDKs de OpenAI | SDKs de Google GenAI | SDKs de Anthropic | Integraciones IDE
        |
        v
Omni Gateway
  autenticación -> traducción de formato -> limpieza consciente de tokens -> enrutamiento -> failover -> streaming
        |
        v
adaptadores de proveedores
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

La API pública mantiene su estabilidad mientras los adaptadores específicos de cada proveedor evolucionan continuamente dentro de Omni Gateway.

## Estructura del repositorio

```text
backend/       Raíz de composición de FastAPI, núcleo de enrutamiento, adaptadores, almacenamiento y pruebas
frontend/      Interfaz de consola web, estilos, scripts y activos de logotipos de proveedores
deploy/        Definiciones de contenedores, manifiestos de plataforma y scripts de inicio de SO
docs/          Notas de arquitectura y documentación de mantenimiento del proyecto
.github/       Flujos de CI, automatización de dependencias y plantillas de contribución
```

Consulte [Arquitectura](../architecture.md) para conocer más sobre los límites de módulos, flujos de solicitudes, propiedad de estado y restricciones de la versión actual.

## Despliegue

Omni Gateway está diseñado para entornos de producción reales. Docker es la opción recomendada para VPS y servidores, ya que mantiene el runtime aislado mientras almacena de forma persistente credenciales y registros en el host.

### Docker en VPS

En primer lugar, cree los directorios persistentes en el host:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Inicie el contenedor del servicio:

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

La misma versión también se publica en GitHub Packages: `ghcr.io/nguywnben/omni-gateway:1.4.0`. La etiqueta `latest` sigue el lanzamiento estable más reciente; la etiqueta `edge` sigue compilaciones verificadas pero no publicadas de la rama `main`. Fije etiquetas de versión específicas o digests cuando requiera despliegues reproducibles.

Abra la consola de administración en el navegador:

```text
http://IP_DE_SU_SERVIDOR:4283
```

En la primera ejecución, establezca la contraseña del panel en la pantalla de configuración inicial. El proyecto no incluye contraseñas predeterminadas. El acceso desde navegadores remotos también requiere ingresar el token de inicialización (bootstrap token) mostrado en `docker logs omni-gateway`; el acceso directo desde localhost no lo requerirá. Puede configurar la variable de entorno `SETUP_TOKEN` antes del inicio si la automatización del despliegue necesita un token predeterminado fijo.

Las contraseñas administradas por el sistema se almacenan como hashes scrypt con sal, las sesiones del panel utilizan cookies HttpOnly y las solicitudes de SDK públicas se autentican mediante claves API `sk-ogw-` generadas automáticamente. Para despliegues no interactivos, preconfigure `PANEL_PASSWORD` para omitir la interfaz de configuración inicial.

La imagen `1.4.0` se publica para la arquitectura `linux/amd64`. La publicación de imágenes ARM64 se encuentra en pausa hasta que todas las dependencias de proveedores, incluida la pila de transporte de Vertex, puedan compilarse y probarse bajo el mismo estándar.

Si el firewall de su servidor está habilitado, abra el puerto de la pasarela:

```bash
sudo ufw allow 4283/tcp
```

Ver registros en tiempo real:

```bash
sudo docker logs -f omni-gateway
```

Actualizar a la imagen estable más reciente:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

A continuación, reinicie el contenedor utilizando el mismo comando `docker run` anterior. Los directorios montados en `/opt/omni-gateway` conservarán las credenciales, configuraciones, datos de uso y registros a lo largo de las actualizaciones del contenedor.

### Despliegue con Docker Compose

Para despliegues basados en el repositorio de código fuente:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

El archivo Compose incluido descargará `nguywnben/omni-gateway:latest` de forma predeterminada y utilizará `/opt/omni-gateway` para los datos persistentes del host. Establezca `IMAGE=nguywnben/omni-gateway:1.4.0` para fijar esta versión, y configure `DATA_DIR=/ruta/personalizada` si utiliza otra ubicación de almacenamiento.

Compose transferirá `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, URIs de almacenamiento externo y `PROXY` desde el entorno shell o el archivo `.env` en la raíz. Déjelos vacíos para mantener los comportamientos predeterminados de generación automática de claves, configuración inicial, almacenamiento local SQLite y conectividad de salida directa.


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.


### Desarrollo local

Utilice el flujo de trabajo nativo de Python para desarrollar o depurar la pasarela localmente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

En Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Abra el panel de control en el navegador:

```text
http://127.0.0.1:4283
```

El entorno de desarrollo local utiliza la misma pantalla de configuración inicial que el despliegue con Docker.

## Configuración

Omni Gateway lee la configuración con la siguiente prioridad: variables de entorno > configuración guardada > valores predeterminados.

| Variable de entorno | Valor predeterminado | Descripción |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Dirección de escucha (bind address). |
| `PORT` | `4283` | Puerto HTTP. |
| `HOST_PORT` | `4283` | Puerto del host utilizado únicamente por Docker Compose. |
| `WORKERS` | `1` | Número de workers admitidos para la serie 1.x. Otros valores serán rechazados hasta que la reserva de credenciales, enfriamiento, sesiones y agregación de uso se coordinen entre procesos. |
| `CORS_ORIGINS` | vacío | Lista separada por comas de orígenes de navegador autorizados para llamadas a la API de origen cruzado. Dejar vacío para uso de consola en el mismo origen. |
| `CORS_ORIGIN_REGEX` | vacío | Expresión regular opcional para orígenes de navegador dinámicos. |
| `API_KEY` | generada automáticamente | Clave preferida para solicitudes de API de clientes públicos. Debe comenzar con `sk-ogw-`. |
| `PANEL_PASSWORD` | vacía hasta configuración | Contraseña de acceso al panel de control web. |
| `SETUP_TOKEN` | generado por proceso | Token de inicialización fijo opcional para configuración remota inicial. Si se omite, léalo en los registros de la aplicación o del contenedor. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Tiempo de vida de la sesión del panel de control web en segundos. |
| `PANEL_COOKIE_SECURE` | automático | Establezca en `true` para forzar cookies solo a través de HTTPS. Vacío para autodetección mediante `X-Forwarded-Proto`. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Ventana de límite de tasa de inicio de sesión en segundos. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Intentos máximos de inicio de sesión fallidos permitidos por cliente dentro de la ventana de límite. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Número máximo de direcciones de clientes rastreadas en memoria por el limitador de inicio de sesión. |
| `MAX_REQUEST_BODY_MB` | `64` | Tamaño máximo del cuerpo de solicitud HTTP en MiB. Las solicitudes que excedan el límite devolverán errores con la estructura nativa del protocolo correspondiente. |
| `TRUST_PROXY_HEADERS` | `false` | Acepte encabezados de reenvío de cliente/protocolo solo si provienen de un proxy inverso de confianza que los sobrescriba. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Directorio de almacenamiento de credenciales. En Docker, mantenga `/app/backend/data/creds` persistente mediante volúmenes de host. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Endpoint del backend de Code Assist. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Endpoint del backend de Google Antigravity. |
| `PROXY` | vacío | Proxy HTTP, HTTPS o SOCKS opcional. |
| `RETRY_429_ENABLED` | `true` | Habilita reintentos acotados para límites de tasa y fallos temporales de upstream. El nombre antiguo se mantiene por compatibilidad. |
| `RETRY_429_MAX_RETRIES` | `5` | Número máximo de reintentos para fallos temporales de upstream. |
| `RETRY_429_INTERVAL` | `1` | Intervalo base de retroceso (backoff) entre reintentos temporales en segundos. |
| `AUTO_DISABLE` | `false` | Deshabilita automáticamente credenciales tras errores graves configurados. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Lista separada por comas de códigos de estado de error grave. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | vacío | Proveedor preferido para la estrategia `priority`, por ejemplo `google_antigravity` o `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Tiempo de espera para inferencia del proveedor (5 a 900 segundos). |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Intentos máximos de continuación para la función de streaming contra truncamiento (anti-truncation). |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Comprime historiales de conversación excesivamente largos antes de enrutarlos al proveedor. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Umbral estimado de tokens de entrada para activar la compresión de contexto. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Objetivo de tokens de entrada tras la compresión. Debe ser inferior al umbral de activación. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Número mínimo de turnos de usuario recientes que deben preservarse durante la compresión. |
| `COMPATIBILITY_MODE` | `false` | Convierte mensajes del sistema para clientes/modelos que no los admiten de forma nativa. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Devuelve el proceso de razonamiento del modelo (reasoning) cuando esté disponible. |
| `MONGODB_URI` | vacío | Habilita el backend de almacenamiento MongoDB cuando está configurado. |
| `POSTGRESQL_URI` | vacío | Habilita el backend de almacenamiento PostgreSQL cuando está configurado. |
| `REDIS_URL` | vacío | Habilita caché / estado de sesiones en Redis cuando está configurado. |
| `CODE_ASSIST_CLIENT_ID` | integrado | Anulación opcional del Client ID OAuth de Code Assist. |
| `CODE_ASSIST_CLIENT_SECRET` | integrado | Anulación opcional del Client Secret OAuth de Code Assist. |
| `ANTIGRAVITY_CLIENT_ID` | integrado | Anulación opcional del Client ID OAuth de Google Antigravity (configurable también en la página de Proveedores). |
| `ANTIGRAVITY_CLIENT_SECRET` | integrado | Anulación opcional del Client Secret OAuth de Google Antigravity. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Anulación opcional del endpoint Generative Language API de Google AI Studio. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Anulación opcional del endpoint de API para credenciales de API Key de SpaceXAI Console. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Anulación opcional del endpoint de suscripción Grok Build OAuth. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Anulación opcional del emisor OAuth de Grok Build. La consola solo acepta hosts HTTPS bajo el dominio `x.ai`. |
| `XAI_CLIENT_ID` | integrado | Anulación opcional del Client ID OAuth PKCE de Grok Build. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Anulación opcional del User-Agent HTTP compartido para solicitudes OAuth de Grok Build y API de SpaceXAI Console. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Anulación opcional del endpoint de API de OpenAI Platform (configurable también en la página de Proveedores). |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Anulación opcional del endpoint de inferencia y catálogo de modelos de cuenta de Codex. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Anulación opcional del endpoint de verificación de límites de cuenta de Codex. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Anulación opcional del servicio de autorización de dispositivos de Codex. |
| `CODEX_CLIENT_ID` | integrado | Anulación opcional del Client ID OAuth de dispositivos de Codex. |
| `CODEX_USER_AGENT` | compatible Codex CLI | Anulación opcional de User-Agent para solicitudes de Codex. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Anulación opcional del endpoint de API Messages de Claude Platform y Claude Code. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Anulación opcional del endpoint de autorización PKCE de Claude Code. Solo hosts oficiales de Anthropic y Claude. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Anulación opcional del endpoint de token de Claude Code. Solo hosts oficiales de Anthropic y Claude. |
| `CLAUDE_CLIENT_ID` | integrado | Anulación opcional del Client ID OAuth PKCE de Claude Code. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Anulación opcional de User-Agent para solicitudes de Claude Code y Claude Platform. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Anulación opcional de User-Agent para solicitudes a nivel de protocolo de Google Antigravity. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Anulación opcional del campo userAgent a nivel de carga útil de Google Antigravity. |
| `METRICS_TOKEN` | empty | Optional bearer token required to scrape `GET /metrics`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | Nivel de detalle de los registros (log level). |
| `LOG_MAX_MB` | `10` | Tamaño máximo en MB de un archivo de registro activo antes de rotar. |
| `LOG_BACKUP_COUNT` | `3` | Cantidad de archivos de registro rotados que se conservan. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Ruta del archivo de registro. En Docker, mantenga `/app/backend/data/logs` persistente mediante volúmenes de host. |

## Inicio rápido: Integración SDK

Omni Gateway está diseñado respetando el comportamiento estándar de URL de los SDK oficiales de Python. Configure cada cliente exactamente como se indica a continuación; la pasarela no requiere prefijos de ruta redundantes o no estándar.

Los siguientes ejemplos utilizan el modelo virtual `omway`. Configure su orden de prioridad de fallback en la página de Modelos previamente, o reemplácelo por el ID de un modelo específico de un proveedor.

### OpenAI Python SDK

Utilice `/v1` como Base URL para OpenAI. El SDK agregará automáticamente `/chat/completions` al final.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Explica este repositorio de código en un solo párrafo."}],
)
```

El mismo cliente puede invocar directamente la API OpenAI Responses:

```python
response = client.responses.create(
    model="omway",
    instructions="Responde de manera concisa y clara.",
    input="Explica este repositorio de código en un solo párrafo.",
)

print(response.output_text)
```

La compatibilidad con Responses admite entrada de texto, imágenes, Function Tools sin streaming y streaming de texto por SSE. Las herramientas integradas alojadas por OpenAI, el historial persistente de respuestas y las llamadas a funciones en streaming serán rechazadas explícitamente, ya que Omni Gateway no ejecuta, persiste ni descarta silenciosamente estos comportamientos propietarios de OpenAI.

### Anthropic Python SDK

Utilice el origen de la pasarela como Base URL para Anthropic. El SDK agregará automáticamente `/v1/messages` al final.

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Escribe un mensaje de commit breve."}],
)
```

### Google GenAI Python SDK

Utilice el origen de la pasarela como Base URL para Google GenAI. El SDK agregará automáticamente la ruta predeterminada del modelo, como `/v1beta/models/{model}:generateContent`.

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
    contents="Escribe una función corta en Python.",
    config=types.GenerateContentConfig(
        system_instruction="Eres un asistente útil y competente.",
    ),
)
```

### Endpoints compatibles

Omni Gateway proporciona rutas compatibles con los SDK estándar sin necesidad de prefijos de espacio de nombres adicionales:

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

Los errores de autenticación, validación de solicitudes, enrutamiento, fallos de upstream y errores previos al inicio del streaming utilizan las estructuras de error nativas de cada interfaz de SDK. Todas las respuestas HTTP incluyen el encabezado `X-Request-ID`; los clientes pueden enviar un identificador en este encabezado para rastrear el flujo de solicitudes. Las respuestas con límite de tasa o no disponibles temporalmente conservan el encabezado `Retry-After` de forma transparente cuando el upstream lo proporciona.

## Gestión avanzada de modelos

La página de Modelos construye el modelo virtual `omway` agregando los modelos descubiertos a partir de las credenciales de proveedores habilitadas. Defina una única vez el orden de prioridad de los modelos subyacentes y utilice `omway` desde cualquiera de los SDK compatibles. Omni Gateway balanceará la carga entre las credenciales saludables que admitan el modelo principal y pasará automáticamente al siguiente modelo configurado si el primero deja de estar disponible. Los IDs de modelos físicos de los proveedores siguen estando disponibles para clientes que requieran una selección determinista. Guardar una lista vacía desactivará `omway` sin afectar las credenciales de los proveedores.

El descubrimiento de modelos es consciente de cada proveedor: los modelos compartidos pueden ser atendidos por varios proveedores, mientras que los modelos propietarios solo se enrutan a credenciales compatibles. Cada credencial verificada mantiene su propio catálogo de proveedor, y el router prioriza el soporte declarado explícitamente por la credencial sobre deducciones generales. La actualización del catálogo verifica la disponibilidad en tiempo real con el proveedor; las opciones que dejen de estar disponibles seguirán mostrándose en la configuración hasta que se restablezcan o eliminen manualmente.

Cuando un upstream devuelve un error `404` para un modelo físico específico, Omni Gateway registra una ruta no disponible para esa credencial y modelo en lugar de desactivar todo el proveedor. Dicha ruta se omitirá de forma inmediata y permanecerá visible bajo **Rutas de modelos no disponibles** hasta que se limpie o la credencial sea verificada nuevamente. Esto evita que los límites de suscripción o restricciones regionales de una cuenta afecten a otras cuentas saludables del mismo proveedor. Si ninguna credencial habilitada declara o permite deducir el soporte para un modelo solicitado, la pasarela devolverá un error explícito de falta de credenciales compatibles en lugar de enviar la solicitud a un proveedor al azar.

Omni Gateway interpreta prefijos y sufijos de funciones en los nombres de modelos:

- `fake-streaming/{model}` o el prefijo de pseudo-streaming configurado para clientes que requieren obligatoriamente el formato SSE.
- `streaming-anti-truncation/{model}` o el prefijo de anti-truncamiento configurado para la recuperación automática en generaciones extensas en streaming.
- Sufijos de profundidad de razonamiento (como `-high`, `-medium`, `-low`, `-minimal`, `-max`) para modelos compatibles de la familia Gemini.
- Sufijos de búsqueda como `-search` para modelos compatibles con fundamentación en Google Search (grounding).

Los adaptadores de los proveedores normalizan estos identificadores de funciones antes de enviar las solicitudes al upstream.

## Transparencia de uso y costes

Omni Gateway registra el volumen de solicitudes, tasa de éxito, atribución por credencial, consumo de tokens reportado por el proveedor y el ahorro estimado de tokens logrado mediante la compresión de contexto para cada intervalo de tiempo en la consola. El ahorro por compresión se indica como estimado debido a que los tokenizadores y las reglas de facturación de los proveedores tienen la autoridad definitiva. El enrutamiento dinámico basado en precios de proveedores se ha reservado deliberadamente como una capa de políticas futura para mantener la API central simple y estable a medida que se agreguen más proveedores.

## Flujo de trabajo con credenciales

1. Inicie Omni Gateway.
2. Acceda a `http://IP_DE_SU_SERVIDOR:4283` en un VPS, o a `http://127.0.0.1:4283` en desarrollo local.
3. Cree la contraseña del panel en la pantalla de configuración inicial. Para instalaciones remotas, ingrese el bootstrap token que aparece en los registros; o configure `PANEL_PASSWORD` previamente.
4. Añada cuentas, claves API o conexiones Ollama desde la página de Proveedores.
5. Verifique la validez de las credenciales y supervise los enfriamientos y errores en el panel.
6. Configure sus herramientas de programación para que se conecten a una de las interfaces de API compatibles descritas anteriormente.

Al agregar credenciales de Google Antigravity, Google redirigirá el navegador a `http://localhost:4283/callback` una vez completado el inicio de sesión. En un equipo local, Omni Gateway mostrará directamente la página de éxito de OAuth. En un VPS, dado que ese `localhost` apunta al navegador local del usuario, es posible que la página no cargue; copie la URL completa de la barra de direcciones del navegador, regrese a la página de Proveedores, péguela en el campo `Callback URL` y haga clic en `Guardar credencial`.

Google AI Studio utiliza autenticación mediante API Key en lugar de OAuth. Añada una clave desde la página de Proveedores; Omni Gateway verificará su validez frente al catálogo de modelos de Google, la guardará como credencial de proveedor y enrutará las solicitudes de Gemini o Gemma compatibles a través de ella. El router inteligente puede alternar automáticamente entre AI Studio y Google Antigravity para modelos Gemini compartidos, reservando los modelos propietarios para credenciales compatibles.

La importación masiva de Google AI Studio admite archivos JSON y archivos ZIP que contengan archivos JSON. Los documentos JSON pueden contener una clave única, una lista `api_keys` o una lista de objetos de clave:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Cada clave importada se valida rigurosamente antes de su almacenamiento. Las claves duplicadas dentro del mismo lote se omiten, las claves existentes se vuelven a verificar y actualizar, y los registros inválidos se reportan individualmente sin revelar el texto plano de las claves.

Grok Build admite credenciales OAuth PKCE, mientras que SpaceXAI Console admite claves API. Las claves de SpaceXAI Console se validan frente al catálogo de modelos de Grok Build antes de guardarse. Para Grok Build OAuth, Omni Gateway genera un enlace de autorización; tras completar la autorización, copie el código mostrado en la página de Grok Build y péguelo en el formulario. Los tokens de acceso se renuevan automáticamente cuando existe un refresh token, y ambos tipos de credenciales solo exponen los modelos de Grok Build declarados en sus catálogos actuales. La página del Pool permite consultar el uso mensual de créditos de las cuentas Grok Build OAuth y el uso semanal cuando xAI lo proporciona. Esta vista de facturación a nivel de cuenta no está disponible para claves API de SpaceXAI Console.

Codex utiliza el flujo de autorización de dispositivos de OpenAI. Genere un código de dispositivo en la página de Proveedores, abra la URL de verificación mostrada, ingrese el código, complete el inicio de sesión y regrese para comprobar la autorización. Omni Gateway almacena el catálogo de modelos de cuenta devuelto por Codex, renueva los tokens de acceso OAuth cuando es necesario y reenvía las solicitudes compatibles mediante el transporte Codex Responses. OpenAI Platform utiliza autenticación por API Key; las claves se validan frente al catálogo de modelos antes de integrarse al pool. Ambos productos admiten importación mediante JSON y ZIP con validación y deduplicación específica por proveedor.

Claude Code utiliza el flujo OAuth PKCE de Anthropic. Genere el enlace de autorización, complete el proceso y pegue el código de autorización recibido en la página de Proveedores. Claude Platform acepta claves API de Anthropic. Ambos productos descubren los modelos admitidos para cada credencial, utilizan el transporte Anthropic Messages, renuevan los tokens de acceso de Claude Code cuando es posible y admiten importaciones validadas mediante JSON o ZIP.

Las conexiones Ollama se configuran por endpoint y pueden incluir una Bearer API Key opcional para servidores protegidos o en la nube. Omni Gateway descubre los modelos disponibles a través de `/api/tags` y enruta la inferencia a través de `/api/chat`. Cuando Omni Gateway se ejecuta dentro de Docker, `localhost` apunta al propio contenedor; utilice la dirección de host-gateway o un endpoint de Ollama accesible a través de la red.

La importación completa del Pool y la importación masiva de Google Antigravity admiten archivos comprimidos de hasta 10 MB, con un máximo de 500 archivos, hasta 2 MB por archivo de credencial individual y un total descomprimido de hasta 25 MB. Las importaciones individuales de Google AI Studio, OpenAI, Anthropic y Ollama aplican límites más estrictos: 2 MB por archivo importado, 200 registros JSON y 5 MB de datos descomprimidos.

La página del Pool de Credenciales también ofrece un flujo de respaldo completo independiente del proveedor. `Descargar ZIP` exporta todo el pool de credenciales activas, e `Importar ZIP` restaura dicho archivo identificando automáticamente cada credencial como Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform u Ollama. Las cuentas OAuth conservan la deduplicación de identidad dentro del ámbito del proveedor, mientras que las claves API se validan y deduplican mediante una huella hash irreversible por proveedor. Los elementos no compatibles o con errores de formato se reportan de forma independiente sin interrumpir la importación de las demás credenciales válidas en el archivo comprimido.

Las credenciales de Google Antigravity se almacenan con el formato `google-antigravity-{account_fingerprint}.json`, donde la huella se deriva del correo electrónico normalizado sin exponer el texto plano. Google AI Studio utiliza `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth utiliza `grok-{account_fingerprint}.json`, SpaceXAI Console utiliza `xai-console-{key_fingerprint}.json`, Codex utiliza `openai-codex-{account_fingerprint}.json`, OpenAI Platform utiliza `openai-platform-{key_fingerprint}.json`, Claude Code utiliza `claude-code-{account_fingerprint}.json`, Claude Platform utiliza `claude-platform-{key_fingerprint}.json` y las conexiones Ollama utilizan `ollama-{connection_fingerprint}.json`. Las credenciales antiguas con formato `provider_*.json` y `xai-grok-*.json` mantienen compatibilidad retrospectiva y se exportan con sus nombres normalizados.

Nombres de modo de credencial:

- `code_assist`: pool de credenciales estándar de Code Assist.
- `provider`: pool de credenciales de backend de proveedores generales.

## Almacenamiento de datos

Los despliegues de proceso único utilizan de forma predeterminada el almacenamiento SQLite en el directorio de datos montado. En despliegues con Docker, asegúrese de montar `/app/backend/data/creds` y `/app/backend/data/logs` en rutas persistentes del host como `/opt/omni-gateway/creds` y `/opt/omni-gateway/logs`.

Puede sustituir SQLite por MongoDB o PostgreSQL según las necesidades operativas o pruebas de migración:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

También se puede agregar Redis para acelerar la memoria caché y el estado de las sesiones:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Configurar almacenamiento externo no otorga capacidad de escalado horizontal al runtime 1.x. Mantenga un único worker y una única réplica de la aplicación hasta que se implementen mecanismos distribuidos de reserva de credenciales, enfriamiento, invalidación de sesiones y agregación de uso. Configure únicamente MongoDB o PostgreSQL, nunca ambos simultáneamente; los fallos de inicialización en bases de datos externas detendrán explícitamente el inicio en lugar de recurrir silenciosamente a SQLite.

Se admite la importación de credenciales mediante variables de entorno. Puede realizarse desde la consola o estableciendo una de las siguientes variables con un string JSON sin procesar, o utilizando la variante con sufijo `_B64` codificada en Base64:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

El contenido puede ser un objeto de credencial único, una lista de credenciales o una estructura con `{ "credentials": [...] }`.

## Guía de desarrollo

Esta sección está dirigida a colaboradores del proyecto y depuración local. Los despliegues de producción deben utilizar Docker con volúmenes de host persistentes.

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

Inicie el servicio una vez que se hayan superado todas las comprobaciones:

```bash
python backend/main.py
```

La base estándar para producción es Python 3.12, y las pruebas automáticas en CI cubren Python 3.12 y 3.14. Consulte la [Guía de contribución](../../CONTRIBUTING.md) para conocer el flujo de pull requests y las expectativas de revisión de código.

## Consideraciones de despliegue

- Nunca haga commit de archivos JSON de credenciales ni de archivos `.env`.
- Asigne una `API_KEY` dedicada para las integraciones de clientes y una `PANEL_PASSWORD` independiente para acceder a la consola.
- Restrinja el acceso al volumen de credenciales o base de datos externa y habilite el cifrado en reposo (encryption at rest) en la plataforma; el router debe poder descifrar y leer los tokens de proveedores.
- Ubique siempre Omni Gateway detrás de un proxy inverso con TLS cuando esté expuesto más allá de localhost.
- Configure el proxy inverso para conservar el encabezado `Host` y reenviar `X-Forwarded-Proto`; establezca `PANEL_COOKIE_SECURE=true` cuando la terminación HTTPS esté garantizada.
- Establezca `TRUST_PROXY_HEADERS=true` únicamente si el servicio solo es accesible a través de un proxy de confianza que sobrescriba `X-Forwarded-For` y `X-Forwarded-Proto`.
- Utilice `GET /health` para sondeos de vitalidad (liveness probe) y `GET /ready` para sondeos de disponibilidad con comprobación de almacenamiento (readiness probe).
- La imagen Docker solo opera como root brevemente al inicio para ajustar los permisos del directorio de datos montado, y luego pasa a ejecutarse bajo el usuario sin privilegios `gateway`.
- Defina `CORS_ORIGINS` con los orígenes confiables específicos cuando los clientes web requieran acceso cross-origin.
- Realice siempre una copia de seguridad de `/opt/omni-gateway` o de su `DATA_DIR` configurado antes de actualizar o migrar de servidor.
- El flujo de publicación de imágenes Docker utiliza los secretos de repositorio `DOCKERHUB_USERNAME` y `DOCKERHUB_TOKEN` para Docker Hub, y el `GITHUB_TOKEN` integrado para GitHub Packages en `ghcr.io/nguywnben/omni-gateway`. Configure la variable opcional `IMAGE_NAME` solo si publica con un nombre de imagen de Docker Hub personalizado.
- Mantenga `WORKERS=1` y una sola réplica de aplicación para toda la serie 1.x; el almacenamiento externo no sustituye a la coordinación distribuida.
- Utilice las rutas canónicas de administración `/api/credentials`. Las rutas con alias `/api/creds` de la fase beta fueron eliminadas en 1.0.0.
- Consulte la [Guía de actualización a 1.0](../upgrading-to-1.0.md) antes de migrar un despliegue de la versión beta.
- Siga la [Guía de actualización](../updating.md) al actualizar una instancia en ejecución o al revertir a una versión previa.
- Siga la [Lista de verificación de lanzamiento](../release-checklist.md) antes de crear etiquetas o publicar imágenes.
- Establezca políticas adecuadas de retención de registros y rotación de credenciales según sus cuotas de uso.
- Revoque y renueve inmediatamente las credenciales si los analizadores de seguridad del repositorio o de la nube detectan una fuga de secretos.
- El manifiesto de Render Blueprint utiliza servicios de pago con disco persistente. Los servicios gratuitos de Render emplean un sistema de archivos efímero y solo son aptos para pruebas temporales.

## Comunidad y salud del proyecto

- Lea la [Guía de contribución](../../CONTRIBUTING.md) antes de enviar un pull request.
- Reporte vulnerabilidades de seguridad a través del canal privado indicado en la [Política de seguridad](../../SECURITY.md).
- Revise el [Registro de cambios](../../CHANGELOG.md) para conocer las novedades de cada versión.
- Respete el [Código de conducta](../../CODE_OF_CONDUCT.md) en todos los espacios del proyecto.

## Agradecimientos e inspiración

Omni Gateway se apoya en el trabajo de la comunidad de código abierto dedicada a enrutamiento de IA, telemetría y pasarelas. Expresamos nuestro sincero agradecimiento a los creadores y mantenedores de los siguientes proyectos:

| Proyecto | Descripción | Estrellas |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Inspiración arquitectónica en la gestión de claves multiproveedor y agregación de API vía web | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Pionero en la capa de proxy multiprotocolo y conversión de formatos para CLIs de programación con IA | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Referente de la industria en proxy LLM unificado, balanceo de carga y enrutamiento con tolerancia a fallos | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Arquitectura de pasarela de IA ultrarrápida, estrategias de enrutamiento y modos de alta resiliencia | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Plataforma de ingeniería de LLM de código abierto, rastreo de llamadas, observabilidad y métricas | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Licencia

Omni Gateway se distribuye bajo la [Licencia MIT](../../LICENSE).
