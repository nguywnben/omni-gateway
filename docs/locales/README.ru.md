<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Универсальный AI-маршрутизатор и единый мультипровайдерный шлюз для AI-инструментов разработки</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#podderzhivaemye-provaydery"><b>🌐 Поддерживаемые провайдеры</b></a> •
    <a href="#osnovnye-vozmozhnosti"><b>⚡ Основные возможности</b></a> •
    <a href="#razvertyvanie"><b>🐳 Развертывание Docker</b></a> •
    <a href="#bystryy-start-integraciya-sdk"><b>🔌 Интеграция SDK</b></a> •
    <a href="../architecture.md"><b>📖 Архитектура</b></a>
  </p>

  <p>
    <b>Языки консоли и документации:</b><br>
    <a href="../../README.md">English</a> •
    <a href="README.vi.md">Tiếng Việt</a> •
    <a href="README.zh-CN.md">中文(简体)</a> •
    <a href="README.zh-TW.md">中文(繁體)</a> •
    <a href="README.ja.md">日本語</a> •
    <a href="README.ko.md">한국어</a> •
    <a href="README.es.md">Español</a> •
    <a href="README.fr.md">Français</a> •
    <a href="README.de.md">Deutsch</a> •
    <a href="README.it.md">Italiano</a> •
    <a href="README.pt.md">Português</a> •
    <b>Русский</b> •
    <a href="README.id.md">Indonesia</a> •
    <a href="README.th.md">ภาษาไทย</a> •
    <a href="README.tr.md">Türkçe</a>
  </p>
</div>

---

Универсальный AI-маршрутизатор для инструментов разработки. Omni Gateway обеспечивает интеллектуальное автоматическое переключение при сбоях (smart auto-fallback), очистку контекста с учетом токенов, прозрачность использования и бесшовную трансляцию форматов, позволяя локальным агентам, IDE-ассистентам и скриптам автоматизации задействовать бесплатные и платные мощности LLM через единый стабильный API-интерфейс.

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Почему Omni Gateway

Современные рабочие процессы разработки часто объединяют множество клиентов и провайдеров: OpenAI-совместимые инструменты, нативные SDK Gemini, агенты в стиле Anthropic, учетные записи Google и экспериментальные маршруты моделей. Omni Gateway выступает связующим звеном между этими клиентами и бэкендами моделей, позволяя каждому инструменту взаимодействовать в привычном ему формате, в то время как шлюз берет на себя маршрутизацию, повторные попытки (retries), очистку запросов и нормализацию ответов.

## <a id="osnovnye-vozmozhnosti"></a>Основные возможности

- **Интеллектуальный автоматический failover (Smart auto-fallback):** Резервирует учетные данные под каждый запрос, распределяет параллельный трафик, фиксирует каждую попытку для справедливой ротации и автоматически обходит недавние сбои, периоды ожидания (cooldowns), лимиты частоты запросов и исчерпанные квоты.
- **Очистка с учетом токенов (Token-aware cleanup):** Нормализует тело запроса и аккуратно обрезает только избыточно длинные префиксы диалога по безопасным границам реплик, сохраняя нетронутыми системные инструкции, описания инструментов и актуальный контекст.
- **Трансляция форматов:** Принимает OpenAI Chat Completions и Responses, нативные запросы Gemini и Anthropic Messages, бесшовно преобразуя запросы и потоковые ответы между всеми форматами.
- **Оркестрация учетных данных:** Управляет аккаунтами OAuth и API-ключами провайдеров с отслеживанием состояния работоспособности, кулдаунов, валидацией, дедупликацией и интеллектуальным переключением по провайдерам.
- **Маршрутизация моделей на уровне учетных данных:** Ведет отдельный каталог возможностей для каждой учетной записи, исключая отправку запроса на аккаунт, который не поддерживает выбранную модель.
- **Память работоспособности маршрутов:** Фиксирует ответы «модель не найдена» в области действия конкретной учетной записи и отображает проблемные маршруты для восстановления на странице Models.
- **Отказоустойчивость потоковой передачи:** Поддерживает SSE-стриминг, псевдостриминг для клиентов с обязательным требованием потока данных и механизм повторных попыток против обрыва ответа (anti-truncation) при длинных генерациях.
- **Панель управления (Control Panel):** Включает веб-консоль для управления учетными данными, просмотра журналов, настройки конфигурации, мониторинга использования и информации о версиях.

## Интерфейс консоли

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## <a id="podderzhivaemye-provaydery"></a>Поддерживаемые провайдеры

Omni Gateway прозрачно адаптирует запросы между ведущими AI-провайдерами, локальными средами выполнения и эндпоинтами OAuth:

| Провайдер | Тип аутентификации | Поддерживаемые протоколы | Авто-Failover | Поддержка стриминга |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API-ключ | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API-ключ | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API-ключ | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API-ключ | Совместим с OpenAI, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API-ключ | Совместим с OpenAI | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Локально / Self-hosted)** | Локально / Base URL | Совместим с OpenAI | ✅ | ✅ |

## Архитектура

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | Интеграции IDE
        |
        v
Omni Gateway
  аутентификация -> трансляция форматов -> очистка с учетом токенов -> маршрутизация -> failover -> стриминг
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

Публичный API остается стабильным, в то время как специализированные адаптеры провайдеров развиваются внутри Omni Gateway.

## Структура репозитория

```text
backend/       Корень композиции FastAPI, ядро маршрутизации, трансляторы, хранилище и тесты
frontend/      Разметка консоли управления, стили, скрипты и визуальные ресурсы провайдеров
deploy/        Определения контейнеров, манифесты платформ и скрипты операционной системы
docs/          Заметки по архитектуре и документация проекта
.github/       CI, автоматизация зависимостей и шаблоны для участников
```

Подробнее о границах модулей, потоках запросов, владении состоянием и ограничениях текущего релиза см. в документе [Архитектура](../architecture.md).

## <a id="razvertyvanie"></a>Развертывание

Omni Gateway рассчитан на реальные производственные окружения. Docker является рекомендуемым способом для VPS и серверов, так как он изолирует среду выполнения и надежно сохраняет учетные данные и журналы на хосте.

### Docker на VPS

Сначала создайте постоянные каталоги на хосте:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Запустите сервис:

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

Этот же релиз опубликован в GitHub Packages как `ghcr.io/nguywnben/omni-gateway:1.4.0`. Тег `latest` указывает на последний стабильный релиз; `edge` указывает на проверенные, но еще не выпущенные сборки из ветки `main`. Для повторяемости развертывания фиксируйте конкретный тег версии или дайджест.

Откройте панель управления по адресу:

```text
http://IP_ВАШЕГО_СЕРВЕРА:4283
```

При первом запуске создайте пароль консоли на экране первоначальной настройки. Пароль по умолчанию отсутствует. При удаленном доступе через браузер также потребуется ввести bootstrap-токен, отображаемый в выводе `docker logs omni-gateway`; при локальной настройке через localhost токен не требуется. Передайте переменную `SETUP_TOKEN` перед запуском, если автоматизации развертывания требуется фиксированный bootstrap-токен.

Пароли, управляемые приложением, хранятся в виде salted scrypt-хэшей, сессии панели используют HttpOnly cookie, а публичные запросы SDK аутентифицируются по сгенерированному API-ключу формата `sk-ogw-`. Для неинтерактивного развертывания предварительно задайте `PANEL_PASSWORD`, чтобы полностью пропустить экран настройки.

Контейнер `1.4.0` собран для архитектуры `linux/amd64`. Публикация для ARM64 временно отложена до тех пор, пока все зависимости провайдеров, включая транспортный стек Vertex, не будут полностью собраны и протестированы по единым стандартам.

Если на сервере включен брандмауэр, откройте порт шлюза:

```bash
sudo ufw allow 4283/tcp
```

Просмотр журналов:

```bash
sudo docker logs -f omni-gateway
```

Обновление до актуального стабильного образа:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Затем перезапустите контейнер той же командой `docker run`, приведенной выше. Примонтированные каталоги `/opt/omni-gateway` сохраняют учетные данные, конфигурацию, данные об использовании и логи между обновлениями контейнера.

### Docker Compose

Для развертывания из исходного кода репозитория:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

Прилагаемый compose-файл загружает `nguywnben/omni-gateway:latest` и по умолчанию использует `/opt/omni-gateway` для хранения данных на хосте. Укажите `IMAGE=nguywnben/omni-gateway:1.4.0`, чтобы зафиксировать эту версию, и задайте `DATA_DIR=/vash/put`, если на сервере используется другое расположение.

Compose передает переменные `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, URI внешнего хранилища и `PROXY` из оболочки или корневого файла `.env`. Оставьте их пустыми для автоматической генерации ключей, настройки при первом запуске, локального хранилища SQLite и прямого сетевого подключения.


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.


### Локальная разработка

Используйте рабочий процесс Python для локальной разработки или отладки шлюза:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

В Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Откройте панель управления по адресу:

```text
http://127.0.0.1:4283
```

Локальная среда разработки использует тот же экран первоначальной настройки, что и при развертывании в Docker.

## Конфигурация

Omni Gateway считывает конфигурацию в следующем порядке приоритета: переменные окружения, сохраненные настройки, значения по умолчанию.

| Переменная | По умолчанию | Назначение |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Адрес прослушивания (bind address). |
| `PORT` | `4283` | HTTP-порт. |
| `HOST_PORT` | `4283` | Порт на стороне хоста, используемый только в Docker Compose. |
| `WORKERS` | `1` | Поддерживаемое количество воркеров для ветки 1.x. Другие значения отклоняются до реализации межпроцессной координации резервирования, кулдаунов, сессий и агрегации использования. |
| `CORS_ORIGINS` | пусто | Список разрешенных источников браузера (origins) через запятую для cross-origin вызовов API. Оставьте пустым для работы с консолью из того же источника. |
| `CORS_ORIGIN_REGEX` | пусто | Необязательное регулярное выражение для динамически управляемых источников браузера. |
| `API_KEY` | генерируется автоматически | Основной ключ для публичных клиентских API-запросов. Должен начинаться с `sk-ogw-`. |
| `PANEL_PASSWORD` | пусто до настройки | Пароль для веб-панели управления. |
| `SETUP_TOKEN` | генерируется на процесс | Необязательный фиксированный bootstrap-токен для удаленной первичной настройки. Если не задан, считывайте сгенерированный токен из логов приложения или контейнера. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Время жизни сессии веб-консоли в секундах. |
| `PANEL_COOKIE_SECURE` | автоматически | Установите `true` для принудительного использования cookie панели только по HTTPS. Оставьте пустым для автоопределения HTTPS через `X-Forwarded-Proto`. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Окно ограничения частоты попыток входа в секундах. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Максимальное количество неудачных попыток входа на клиента в пределах окна. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Максимальное число клиентских адресов, отслеживаемых ограничителем входа в памяти. |
| `MAX_REQUEST_BODY_MB` | `64` | Максимальный размер тела HTTP-запроса в МиБ. Запросы SDK, превышающие лимит, возвращают нативную структуру ошибок соответствующего протокола. |
| `TRUST_PROXY_HEADERS` | `false` | Принимать заголовки переадресации клиента/протокола только от доверенного обратного прокси, который перезаписывает их. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Каталог хранения учетных данных. В Docker монтируйте `/app/backend/data/creds` как том хоста. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Бэкенд-эндпоинт Code Assist. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Бэкенд-эндпоинт Google Antigravity. |
| `PROXY` | пусто | Необязательный прокси HTTP, HTTPS или SOCKS. |
| `RETRY_429_ENABLED` | `true` | Включить ограниченные повторные попытки при превышении лимитов и временных сбоях апстрима. Устаревшее имя сохранено для совместимости. |
| `RETRY_429_MAX_RETRIES` | `5` | Максимальное количество повторных попыток при временных ошибках апстрима. |
| `RETRY_429_INTERVAL` | `1` | Базовая задержка между повторными попытками в секундах. |
| `AUTO_DISABLE` | `false` | Отключать учетные данные после критических ошибок из списка. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Список статус-кодов критических ошибок через запятую. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | пусто | Предпочитаемый провайдер для стратегии `priority`, например `google_antigravity` или `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Таймаут генерации ответа провайдером, в диапазоне от 5 до 900 секунд. |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Максимальное количество попыток продолжения генерации для предотвращения обрыва стриминга. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Сжимать избыточную историю диалога перед отправкой провайдеру. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Оценочный порог входных токенов для активации сжатия. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Целевой объем входных токенов после сжатия. Должен быть меньше порога активации. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Минимальное количество последних реплик пользователя, сохраняемых при сжатии. |
| `COMPATIBILITY_MODE` | `false` | Преобразовывать системные сообщения для клиентов/моделей, которые их не поддерживают. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Возвращать блоки рассуждений модели (reasoning), если они доступны. |
| `MONGODB_URI` | пусто | Включает хранилище MongoDB при указании. |
| `POSTGRESQL_URI` | пусто | Включает хранилище PostgreSQL при указании. |
| `REDIS_URL` | пусто | Включает кэширование и сессии на базе Redis при указании. |
| `CODE_ASSIST_CLIENT_ID` | встроенный desktop-клиент | Необязательное переопределение Client ID OAuth для Code Assist. |
| `CODE_ASSIST_CLIENT_SECRET` | встроенный desktop-клиент | Необязательное переопределение Client Secret OAuth для Code Assist. |
| `ANTIGRAVITY_CLIENT_ID` | встроенный desktop-клиент | Необязательное переопределение Client ID OAuth для Google Antigravity. Можно настроить на странице Providers. |
| `ANTIGRAVITY_CLIENT_SECRET` | встроенный desktop-клиент | Необязательное переопределение Client Secret OAuth для Google Antigravity. Настраивается через env или страницу Providers. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Необязательное переопределение эндпоинта Generative Language API в Google AI Studio. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Необязательное переопределение эндпоинта SpaceXAI Console API для API-ключей. Можно настроить на странице Providers. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Необязательное переопределение эндпоинта подписки Grok Build OAuth. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Необязательное переопределение эмитента Grok Build OAuth. Консоль принимает только HTTPS-хосты домена `x.ai`. |
| `XAI_CLIENT_ID` | встроенный публичный клиент | Необязательное переопределение Client ID для Grok Build PKCE OAuth. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Необязательное общее переопределение HTTP User-Agent для запросов Grok Build OAuth и SpaceXAI Console API. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Необязательное переопределение эндпоинта OpenAI Platform API. Можно настроить на странице Providers. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Необязательное переопределение эндпоинта инференса и каталога моделей аккаунта Codex. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Необязательное переопределение эндпоинта проверки лимитов частоты аккаунта Codex. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Необязательное переопределение службы авторизации устройств Codex. |
| `CODEX_CLIENT_ID` | встроенный публичный клиент | Необязательное переопределение Client ID для OAuth-авторизации устройств Codex. |
| `CODEX_USER_AGENT` | значение, совместимое с Codex CLI | Необязательное переопределение User-Agent для запросов Codex. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Необязательное переопределение эндпоинта Messages API для Claude Platform и Claude Code. Настраивается через Providers. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Необязательное переопределение эндпоинта авторизации PKCE для Claude Code. Допустимы только хосты Anthropic и Claude. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Необязательное переопределение эндпоинта получения токена Claude Code. Допустимы только хосты Anthropic и Claude. |
| `CLAUDE_CLIENT_ID` | встроенный публичный клиент | Необязательное переопределение Client ID для Claude Code PKCE OAuth. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Необязательное переопределение User-Agent для запросов Claude Code и Claude Platform. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Необязательное переопределение протокольного User-Agent для Google Antigravity. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Необязательное переопределение поля userAgent на уровне payload для Google Antigravity. |
| `METRICS_TOKEN` | empty | At least 32 bytes; required with opt-in `PROMETHEUS_EXPORT_ENABLED=true`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | Уровень детализации журналов (log level). |
| `LOG_MAX_MB` | `10` | Максимальный размер активного файла журнала перед ротацией. |
| `LOG_BACKUP_COUNT` | `3` | Количество сохраняемых архивных файлов журнала. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Путь к файлу журнала. В Docker монтируйте `/app/backend/data/logs` как том хоста. |

## <a id="bystryy-start-integraciya-sdk"></a>Интерфейсы SDK

Omni Gateway спроектирован с учетом стандартного поведения URL официальных SDK Python. Настраивайте каждый клиент строго по приведенным инструкциям; шлюз не требует нестандартных дублирующихся префиксов путей.

В примерах используется виртуальная модель `omway`. Предварительно настройте приоритеты резервных моделей на странице Models или укажите конкретный идентификатор модели.

### OpenAI Python SDK

Используйте `/v1` в качестве базового URL для OpenAI. SDK автоматически добавит `/chat/completions`.

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Объясни назначение этого репозитория в одном абзаце."}],
)
```

Тот же клиент может использовать OpenAI Responses API:

```python
response = client.responses.create(
    model="omway",
    instructions="Отвечай кратко и емко.",
    input="Объясни назначение этого репозитория в одном абзаце.",
)

print(response.output_text)
```

Совместимость с Responses поддерживает текст, изображения на входе, нестриминговые function tools и SSE-стриминг текста. Встроенные облачные инструменты OpenAI, сохранение истории ответов и потоковые вызовы функций явно отклоняются, поскольку Omni Gateway не исполняет, не сохраняет и не отбрасывает скрытно эти проприетарные механизмы OpenAI.

### Anthropic Python SDK

Используйте адрес шлюза как базовый URL для Anthropic. SDK автоматически добавит `/v1/messages`.

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Составь краткое сообщение коммита."}],
)
```

### Google GenAI Python SDK

Используйте адрес шлюза как базовый URL для Google GenAI. SDK автоматически добавит маршрут модели по умолчанию, например `/v1beta/models/{model}:generateContent`.

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
    contents="Напиши небольшую функцию на Python.",
    config=types.GenerateContentConfig(
        system_instruction="Ты — полезный ассистент.",
    ),
)
```

### Поддерживаемые маршруты

Omni Gateway предоставляет маршруты, совместимые с популярными SDK, без префиксов продуктов:

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

Ошибки аутентификации, валидации запросов, маршрутизации, апстрима и сбои до старта потока возвращаются в нативном формате ошибок выбранного интерфейса SDK. Каждый HTTP-ответ содержит заголовок `X-Request-ID`; клиенты могут передавать безопасный идентификатор в этом заголовке для сквозного отслеживания запросов. Ответы с ограничением частоты запросов или временной недоступностью сохраняют заголовок `Retry-After`, если он предоставлен апстримом.

## Возможности моделей

Страница Models формирует виртуальную модель `omway` на основе моделей, обнаруженных среди активных учетных записей провайдеров. Расставьте входящие модели по приоритету один раз и используйте `omway` в любом поддерживаемом SDK. Omni Gateway распределяет нагрузку между работоспособными аккаунтами с поддержкой первой модели и переходит к следующим по списку в случае недоступности. Прямые ID моделей провайдеров остаются доступными для клиентов, которым требуется детерминированный выбор. Сохранение пустого списка отключает `omway` без влияния на учетные данные провайдеров.

Обнаружение моделей учитывает специфику провайдеров: общая модель может обслуживаться несколькими провайдерами, тогда как уникальные модели используют только совместимые учетные данные. Каждый проверенный аккаунт сохраняет свой собственный каталог, и маршрутизатор отдает приоритет явно заявленной поддержке учетной записи, а не общим предположениям о возможностях провайдера. Обновление каталога повторно проверяет текущую доступность моделей; недоступные позиции остаются в конфигурации до их восстановления или удаления.

Когда апстрим возвращает ошибку `404` для конкретной модели, Omni Gateway фиксирует недоступный маршрут для данной учетной записи и модели вместо отключения провайдера целиком. Этот маршрут временно исключается из ротации и отображается в разделе **Unavailable Model Routes** до его удаления или перепроверки учетных данных. Это предотвращает влияние региональных ограничений или уровней подписки одного аккаунта на другие аккаунты того же провайдера. Если ни одна активная учетная запись не поддерживает запрошенную модель, шлюз возвращает понятную ошибку отсутствия совместимых учетных данных вместо отправки запроса случайному провайдеру.

Omni Gateway распознает префиксы и суффиксы возможностей в названиях моделей:

- `fake-streaming/{model}` или настроенный префикс псевдостриминга для клиентов, требующих обязательный вывод SSE.
- `streaming-anti-truncation/{model}` или настроенный префикс anti-truncation для автоматического восстановления стриминга при длинных ответах.
- Суффиксы рассуждений (thinking), такие как `-high`, `-medium`, `-low`, `-minimal` и `-max` для поддерживаемых моделей семейства Gemini.
- Суффиксы поиска, такие как `-search` для моделей с поддержкой поиска через Google Search (grounding).

Адаптеры провайдеров нормализуют эти модификаторы имен перед отправкой запроса апстриму.

## Использование и Прозрачность расходов

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## Работа с учетными данными

1. Запустите Omni Gateway.
2. Откройте `http://IP_ВАШЕГО_СЕРВЕРА:4283` на VPS или `http://127.0.0.1:4283` при локальной разработке.
3. Создайте пароль панели управления на экране первичной настройки. При удаленной настройке введите bootstrap-токен из логов приложения или задайте `PANEL_PASSWORD`.
4. Добавьте аккаунт, API-ключ или подключение Ollama на странице Providers.
5. Проверьте учетные данные и отслеживайте статусы кулдаунов и ошибок в панели.
6. Направьте ваш инструмент разработки на один из описанных выше API-интерфейсов.

При добавлении учетных данных Google Antigravity сервис Google перенаправляет браузер на `http://localhost:4283/callback` после входа. На локальной машине Omni Gateway покажет страницу успешной авторизации OAuth. На VPS адрес `localhost` относится к компьютеру с браузером пользователя, поэтому страница может не открыться; скопируйте полный URL из адресной строки браузера, вернитесь на страницу Providers, вставьте его в поле `Callback URL` и нажмите `Save credential`.

Google AI Studio использует аутентификацию по API-ключам вместо OAuth. Добавьте ключ на странице Providers; Omni Gateway проверит его по каталогу моделей Google, сохранит как учетные данные провайдера и будет маршрутизировать через него совместимые запросы Gemini или Gemma. Интеллектуальный маршрутизатор может переключаться между AI Studio и Google Antigravity для общих моделей Gemini, сохраняя специфичные модели на совместимых аккаунтах.

Пакетный импорт для Google AI Studio принимает файлы JSON и ZIP-архивы с JSON. JSON-документ может содержать один ключ, массив `api_keys` или массив объектов ключей:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Каждый импортируемый ключ проходит валидацию перед сохранением. Дубликаты внутри одного импорта пропускаются, существующие ключи проверяются повторно и обновляются, а некорректные записи фиксируются без раскрытия значений ключей.

Grok Build поддерживает учетные данные PKCE OAuth, а SpaceXAI Console — API-ключи. Ключи SpaceXAI Console проверяются по каталогу моделей Grok Build перед сохранением. Для Grok Build OAuth шлюз генерирует ссылку авторизации; после подтверждения скопируйте код со страницы Grok Build и вставьте его в форму Grok Build OAuth. Токены доступа обновляются автоматически при наличии refresh-токена, и оба типа учетных данных предоставляют только модели Grok Build, заявленные в их текущем каталоге. Страница Pool позволяет запрашивать ежемесячный расход кредитов и еженедельный расход (если предоставляется xAI) для аккаунтов Grok Build OAuth. Этот просмотр биллинга на уровне аккаунта недоступен для API-ключей SpaceXAI Console.

Codex использует протокол авторизации устройств OpenAI. Сгенерируйте код устройства на странице Providers, перейдите по отображаемому URL, введите код, завершите вход и вернитесь для проверки авторизации. Omni Gateway сохраняет каталог моделей аккаунта, возвращенный Codex, обновляет токены OAuth по мере необходимости и направляет совместимые запросы через транспорт Codex Responses. OpenAI Platform использует API-ключи; ключи проверяются через каталог моделей аккаунта перед добавлением в пул. Оба сервиса поддерживают импорт JSON и ZIP с проверкой и дедупликацией для каждого провайдера.

Claude Code использует протокол Anthropic PKCE OAuth. Сгенерируйте ссылку авторизации, завершите процесс в браузере и вставьте полученный код авторизации на странице Providers. Claude Platform принимает API-ключи Anthropic. Оба варианта определяют доступные модели для каждой учетной записи, используют транспорт Anthropic Messages, обновляют токены Claude Code при возможности и поддерживают проверенный импорт JSON или ZIP.

Подключения к Ollama настраиваются индивидуально для каждого эндпоинта и могут содержать необязательный Bearer API-ключ для защищенных или облачных серверов. Omni Gateway опрашивает модели через `/api/tags` и маршрутизирует генерацию через `/api/chat`. При работе Omni Gateway в Docker `localhost` указывает на сам контейнер; используйте адрес host-gateway или сетевой эндпоинт Ollama.

Импорт пула и пакетный импорт Google Antigravity принимают архивы размером до 10 МБ, содержащие не более 500 файлов, файлы отдельных учетных данных до 2 МБ и суммарный объем распакованных данных до 25 МБ. Для импорта Google AI Studio, OpenAI, Anthropic и Ollama действуют более строгие ограничения: 2 МБ на файл, 200 записей JSON и до 5 МБ распакованных данных.

Страница Pool также предоставляет механизм резервного копирования, независимый от провайдеров. `Download ZIP` экспортирует весь активный пул учетных данных, а `Import ZIP` восстанавливает этот архив, автоматически определяя каждую запись как Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform или Ollama. Аккаунты OAuth сохраняют дедупликацию по идентификаторам провайдера, а API-ключи проверяются и дедуплицируются с помощью необратимого хэш-отпечатка. Неподдерживаемые или некорректные записи регистрируются отдельно, не блокируя валидные данные в том же архиве.

Учетные данные Google Antigravity сохраняются в формате `google-antigravity-{account_fingerprint}.json`, где отпечаток вычисляется из нормализованного email аккаунта без его раскрытия. Google AI Studio использует `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth — `grok-{account_fingerprint}.json`, SpaceXAI Console — `xai-console-{key_fingerprint}.json`, Codex — `openai-codex-{account_fingerprint}.json`, OpenAI Platform — `openai-platform-{key_fingerprint}.json`, Claude Code — `claude-code-{account_fingerprint}.json`, Claude Platform — `claude-platform-{key_fingerprint}.json`, а подключения Ollama — `ollama-{connection_fingerprint}.json`. Устаревшие файлы `provider_*.json` и `xai-grok-*.json` остаются совместимыми и экспортируются с каноническими именами.

Названия режимов учетных данных (Credential mode names):

- `code_assist`: стандартный пул учетных данных Code Assist.
- `provider`: пул учетных данных бэкенда провайдеров.

## Хранилище

Развертывание в виде одного процесса использует базу данных SQLite в примонтированном каталоге данных. В Docker обязательно монтируйте `/app/backend/data/creds` и `/app/backend/data/logs` к постоянным путям хоста, таким как `/opt/omni-gateway/creds` и `/opt/omni-gateway/logs`.

MongoDB или PostgreSQL могут заменить локальный SQLite в зависимости от эксплуатационных требований или для тестирования миграции:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

Для ускорения кэширования и сессий можно подключить Redis:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Внешнее хранилище не делает среду выполнения 1.x горизонтально масштабируемой. Запускайте один воркер и одну реплику до реализации распределенного резервирования учетных данных, кулдаунов, инвалидации сессий и агрегации использования. Настраивайте либо MongoDB, либо PostgreSQL, но не оба одновременно; ошибка инициализации внешней базы данных остановит запуск вместо скрытого отката к SQLite.

Импорт учетных данных из переменных окружения доступен из панели управления. Укажите одну из следующих переменных с необработанной строкой JSON или используйте соответствующий вариант `_B64` для base64-кодированного JSON:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

Тело может представлять собой один объект учетных данных, массив или структуру вида `{ "credentials": [...] }`.

## Разработка

Этот раздел предназначен для контрибьюторов и локальной отладки. Для производственных сред следует использовать Docker с постоянными томами хоста.

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

Запустите сервис после успешного прохождения всех проверок:

```bash
python backend/main.py
```

Базовой версией для продакшена является Python 3.12, а CI в настоящее время проверяет совместимость с Python 3.12 и 3.14. Ознакомьтесь с [Руководством для контрибьюторов](../../CONTRIBUTING.md) относительно рабочего процесса pull request и требований к ревью кода.

## Примечания по развертыванию

- Никогда не фиксируйте в коммитах JSON-файлы с учетными данными или файлы `.env`.
- Используйте выделенный `API_KEY` для интеграции с клиентами и отдельный `PANEL_PASSWORD` для доступа к веб-консоли.
- Ограничьте доступ к постоянному тому учетных данных или внешней базе данных и включите шифрование данных на уровне платформы (encryption at rest); шлюз должен иметь возможность считывать токены провайдеров.
- Размещайте Omni Gateway за обратным прокси-сервером с поддержкой TLS при доступе за пределами localhost.
- Настройте обратный прокси для сохранения заголовка `Host` и передачи `X-Forwarded-Proto`; укажите `PANEL_COOKIE_SECURE=true`, если гарантирована терминация HTTPS.
- Устанавливайте `TRUST_PROXY_HEADERS=true` только тогда, когда сервис доступен исключительно через доверенный прокси, перезаписывающий `X-Forwarded-For` и `X-Forwarded-Proto`.
- Используйте `GET /health` для проверки жизнеспособности процесса (liveness) и `GET /ready` для проверки готовности с учетом хранилища (readiness).
- Docker-образ запускается с правами root лишь на время исправления прав доступа к примонтированному каталогу данных, а затем запускает сервис от имени непривилегированного пользователя `gateway`.
- Задайте `CORS_ORIGINS` с точным списком доверенных источников, если клиентам браузера требуется cross-origin доступ.
- Обязательно делайте резервную копию каталога `/opt/omni-gateway` или выбранного `DATA_DIR` перед обновлением или переносом на другой сервер.
- Публикация Docker-образов использует секреты репозитория `DOCKERHUB_USERNAME` и `DOCKERHUB_TOKEN` для Docker Hub, а также встроенный `GITHUB_TOKEN` для GitHub Packages по адресу `ghcr.io/nguywnben/omni-gateway`. Задавайте переменную `IMAGE_NAME` только при публикации под пользовательским именем образа.
- Сохраняйте `WORKERS=1` и одну реплику приложения для всей линейки версий 1.x; внешнее хранилище не заменяет распределенную координацию.
- Используйте канонические маршруты управления `/api/credentials`. Бета-алиасы `/api/creds` были удалены в версии 1.0.0.
- Следуйте руководству [Обновление до 1.0](../upgrading-to-1.0.md) перед миграцией бета-развертываний.
- Следуйте [руководству по обновлению](../updating.md) при повышении версии работающего инстанса или откате на предыдущую версию.
- Выполняйте пункты [чек-листа релиза](../release-checklist.md) перед присвоением тега или публикацией образа.
- Согласуйте политики хранения логов и ротации учетных данных с вашими лимитами использования.
- Немедленно отзывайте и обновляйте учетные данные, если сканеры репозитория или платформы зафиксировали утечку секрета.
- Render Blueprint использует платный тариф с постоянным диском. Бесплатные сервисы Render используют временную файловую систему и подходят только для ознакомительного тестирования.

## Сообщество и Состояние проекта

- Прочтите [Руководство по участию](../../CONTRIBUTING.md) перед открытием pull request.
- Сообщайте об уязвимостях через конфиденциальный процесс в [Политике безопасности](../../SECURITY.md).
- Ознакомьтесь с [Историей изменений](../../CHANGELOG.md) для информации об изменениях в конкретных релизах.
- Соблюдайте [Кодекс поведения](../../CODE_OF_CONDUCT.md) во всех пространствах проекта.

## Благодарности и Вдохновение

Omni Gateway создан благодаря наработкам сообщества разработчиков открытого исходного кода в области AI-маршрутизации, телеметрии и шлюзов. Мы выражаем искреннюю благодарность создателям и мейнтейнерам следующих проектов:

| Проект | Описание | Звезды |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Вдохновение для мультипровайдерного управления ключами и веб-агрегации API | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Первопроходец в области мультиформатного проксирования и трансляции протоколов для AI-инструментов разработки | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Эталон в области унифицированного LLM-проксирования, балансировки нагрузки и отказоустойчивой маршрутизации | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Сверхбыстрая архитектура AI-шлюза, гибкие стратегии маршрутизации и надежные шаблоны failover | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Open-source платформа для LLM-инжиниринга, трассировки, мониторинга и сбора метрик | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Лицензия

Omni Gateway распространяется под [Лицензией MIT](../../LICENSE).
