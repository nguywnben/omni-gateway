<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>面向 AI 程式設計工具的通用 AI 路由器與多供應商統一閘道</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#支援的供應商"><b>🌐 支援的供應商</b></a> •
    <a href="#核心能力"><b>⚡ 核心能力</b></a> •
    <a href="#部署"><b>🐳 Docker 部署</b></a> •
    <a href="#快速上手-sdk-接入"><b>🔌 SDK 接入</b></a> •
    <a href="../architecture.md"><b>📖 架構設計</b></a>
  </p>

  <p>
    <b>控制台與文檔語言：</b><br>
    <a href="../../README.md">English</a> •
    <a href="README.vi.md">Tiếng Việt</a> •
    <a href="README.zh-CN.md">中文(简体)</a> •
    <b>中文(繁體)</b> •
    <a href="README.ja.md">日本語</a> •
    <a href="README.ko.md">한국어</a> •
    <a href="README.es.md">Español</a> •
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

面向程式設計工具的通用 AI 路由器。Omni Gateway 提供智慧自動容錯移轉、權杖感知上下文清理、使用量視覺化與無縫格式轉換，讓本地 Agent、IDE 助手與自動化腳本能透過單一穩定的 API 介面調用各類免費與付費的 LLM 算力。

> **專案狀態：** 穩定。版本 `1.4.0` 完善了支援 15 種語言的在地化控制台，新增感知語系環境的管理 API 提示訊息與版本更新指南，並保留了自 `1.0.0` 確立的穩定 SDK 路由、規範管理路由、配置命名與單實例執行契約。

## 為什麼選擇 Omni Gateway

現代程式設計工作流通常混合使用多種客戶端與模型供應商：OpenAI 相容工具、Gemini 原生 SDK、Anthropic 風格的 Agent、Google 憑證以及實驗性模型路由。Omni Gateway 位於這些客戶端與模型後端之間，讓每個工具能繼續使用其原生協定，同時由閘道統一處理請求路由、重試、請求清理與回應格式標準化。

## 核心能力

- 智慧自動容錯移轉：按請求預留憑證，均衡並發流量，追蹤每次調用以實現公平輪詢，並自動避開近期故障、冷卻期、速率限制及額度耗盡的憑證。
- 權杖感知清理：規範化請求負載，僅在安全的對話輪次邊界處修剪過長的歷史前綴，同時完整保留系統指令、工具定義與最近上下文。
- 格式協定轉換：接收 OpenAI Chat Completions 與 Responses、Gemini 原生請求及 Anthropic Messages，並在不同格式與串流回應之間雙向轉譯。
- 憑證生命週期協調：管理 OAuth 帳戶與供應商 API 金鑰，提供健康狀態檢查、冷卻追蹤、有效性驗證、去重與供應商感知容錯移轉。
- 憑證級模型路由：為每個憑證維護獨立的能力目錄，防止某個帳戶的模型權限將請求誤發至不支援該模型的其他帳戶。
- 路由健康記憶：在憑證層級記錄模型未找到（404）回應，並在模型管理頁面展示受影響的路由以便復原。
- 串流傳輸彈性：支援 SSE 串流傳輸、為強制要求串流輸出的客戶端提供偽串流（pseudo-streaming），並為長文本生成提供防截斷重試。
- Web 控制面板：自帶 Web 控制台，用於憑證管理、日誌檢視、系統配置、使用量統計與版本資訊檢視。

## 控制台預覽

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## 支持的供应商

Omni Gateway 在主流 AI 供應商、本地執行階段與 OAuth 端點之間無縫適配請求：

| 供應商 | 認證類型 | 支援的協定 | 自動容錯移轉 | 串流傳輸 |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI 相容, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI 相容 | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (本地 / 自託管)** | 本地 / Base URL | OpenAI 相容 | ✅ | ✅ |

## 架構設計

```text
客戶端工具
  OpenAI SDK | Google GenAI SDK | Anthropic SDK | IDE 整合外掛
        |
        v
Omni Gateway
  身分認證 -> 格式協定轉換 -> 權杖感知清理 -> 路由分發 -> 容錯移轉 -> 串流輸出
        |
        v
供應商適配器
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

在 Omni Gateway 後端適配器持續演進的同時，對外的公共 API 契約保持絕對穩定。

## 程式庫目錄結構

```text
backend/       FastAPI 組合根、路由核心、協定轉換器、儲存層與測試用例
frontend/      管理控制台頁面結構、樣式、腳本及供應商圖示資產
deploy/        容器定義、平台部署清單與作業系統啟動腳本
docs/          架構設計說明與專案維護文檔
.github/       CI 流水線、依賴自動化與貢獻範本
```

詳見[架構設計](../architecture.md)，瞭解模組邊界、請求處理流程、狀態歸屬與目前版本的發布約束。

## 部署

Omni Gateway 專為生產環境部署而設計。Docker 是 VPS 與伺服器環境的建議方案，既能保證執行階段隔離，又能在宿主機持久化儲存憑證與日誌。

### 在 VPS 上使用 Docker 部署

首先在宿主機建立持久化目錄：

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

啟動服務容器：

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

同一版本亦已發布至 GitHub Packages：`ghcr.io/nguywnben/omni-gateway:1.4.0`。`latest` 標籤追蹤最新的穩定版本；`edge` 標籤追蹤經測試但尚未正式發布的 `main` 分支組建。在需要環境可重現的場景下，建議固定具體版本號或映像檔摘要。

開啟瀏覽器造訪控制台：

```text
http://你的伺服器IP:4283
```

首次執行時，在初始化頁面設定控制台密碼。專案未內建任何預設密碼。透過遠端瀏覽器造訪時，還必須輸入 `docker logs omni-gateway` 輸出的引導權杖（bootstrap token）；直接在本機 localhost 造訪則無需輸入。若需自動化部署，可在啟動前預先設定 `SETUP_TOKEN` 環境變數。

系統管理的密碼均以加鹽 scrypt 雜湊安全儲存，控制台工作階段使用 HttpOnly Cookie，公共 SDK 請求則使用自動產生的 `sk-ogw-` API 金鑰進行鑑權。如需非互動式部署，可預先配置 `PANEL_PASSWORD` 直接略過初始化引導介面。

`1.4.0` 映像檔針對 `linux/amd64` 平台建置發布。ARM64 映像檔發布暫緩，直到包括 Vertex 傳輸堆疊在內的所有供應商依賴均能在同一標準下建置並通過測試。

若伺服器啟用了防火牆，請放行閘道連接埠：

```bash
sudo ufw allow 4283/tcp
```

檢視即時日誌：

```bash
sudo docker logs -f omni-gateway
```

更新至最新穩定版本：

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

隨後使用上方相同的 `docker run` 指令重新啟動容器。掛載的 `/opt/omni-gateway` 目錄將在容器更新期間完整保留憑證、配置、使用量資料與日誌。

### Docker Compose 部署

適用於基於原始碼倉庫的部署方式：

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

隨附的 Compose 檔案預設拉取 `nguywnben/omni-gateway:latest` 並使用 `/opt/omni-gateway` 儲存宿主機資料。可透過設定 `IMAGE=nguywnben/omni-gateway:1.4.0` 來鎖定該版本，或設定 `DATA_DIR=/自訂路徑` 使用不同的儲存路徑。

Compose 會從 Shell 環境變數或根目錄 `.env` 檔案傳遞 `API_KEY`、`PANEL_PASSWORD`、`SETUP_TOKEN`、外部儲存 URI 與 `PROXY`。留空即可保持自動產生金鑰、首次引導配置、本地 SQLite 儲存與直接網路出站的預設行為。


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.

### 本地開發

在本地進行開發或偵錯閘道時，請使用 Python 原生工作流：

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Windows PowerShell 環境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

在瀏覽器開啟控制面板：

```text
http://127.0.0.1:4283
```

本地開發環境與 Docker 部署採用相同的首次執行初始化設定頁面。

## 配置項

Omni Gateway 讀取配置的優先順序為：環境變數 > 已儲存配置 > 預設值。

| 環境變數 | 預設值 | 用途說明 |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | 繫結監聽位址。 |
| `PORT` | `4283` | HTTP 連接埠。 |
| `HOST_PORT` | `4283` | 宿主機連接埠，僅供 Docker Compose 使用。 |
| `WORKERS` | `1` | 1.x 系列支援的 Worker 數量。在跨行程的憑證預留、冷卻、工作階段與使用量聚合實現前，其他數值會被拒絕。 |
| `CORS_ORIGINS` | 空 | 允許跨來源調用 API 的瀏覽器 Origin 列表（逗號分隔）。同來源控制台造訪請保持為空。 |
| `CORS_ORIGIN_REGEX` | 空 | 用於比對動態瀏覽器 Origin 的可選正規表示式。 |
| `API_KEY` | 自動產生 | 供公共客戶端 API 請求使用的偏好金鑰。必須以 `sk-ogw-` 開頭。 |
| `PANEL_PASSWORD` | 引導前為空 | Web 控制面板的造訪密碼。 |
| `SETUP_TOKEN` | 行程隨機產生 | 用於遠端首次初始化設定的可選固定引導權杖。省略時可從應用或容器日誌中取得產生的權杖。 |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Web 控制台工作階段有效時間（秒）。 |
| `PANEL_COOKIE_SECURE` | 自動偵測 | 設為 `true` 強制僅在 HTTPS 下傳輸 Cookie。留空時透過 `X-Forwarded-Proto` 自動偵測。 |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | 登入頻率限制時間窗口（秒）。 |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | 限制窗口期內單一客戶端允許的最大失敗登入嘗試次數。 |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | 記憶體中登入頻率限制器追蹤的最大客戶端位址數量。 |
| `MAX_REQUEST_BODY_MB` | `64` | 最大 HTTP 請求主體大小（MiB）。超出限制的 SDK 請求將回傳對應協定的原生錯誤封包。 |
| `TRUST_PROXY_HEADERS` | `false` | 僅在下游存在受信任的反向代理且會覆寫轉發標頭時才接收客戶端與協定轉發標頭。 |
| `CREDENTIALS_DIR` | `./backend/data/creds` | 憑證儲存目錄。在 Docker 中需將 `/app/backend/data/creds` 掛載至宿主機磁碟區。 |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist 後端服務位址。 |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Google Antigravity 後端服務位址。 |
| `PROXY` | 空 | 可選的 HTTP、HTTPS 或 SOCKS 代理。 |
| `RETRY_429_ENABLED` | `true` | 對速率限制和上游暫時性故障啟用有限次重試。保留舊名稱以相容既有配置。 |
| `RETRY_429_MAX_RETRIES` | `5` | 上游暫時性故障的最大重試次數。 |
| `RETRY_429_INTERVAL` | `1` | 暫時性重試的基礎退避間隔（秒）。 |
| `AUTO_DISABLE` | `false` | 在發生配置的嚴重錯誤後自動停用對應憑證。 |
| `AUTO_DISABLE_ERROR_CODES` | `403` | 逗號分隔的嚴重錯誤狀態碼列表。 |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | 空 | `priority` 策略優先選用的供應商，例如 `google_antigravity` 或 `google_ai_studio`。 |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | 供應商推論逾時時間，限制在 5 到 900 秒之間。 |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | 防截斷串流傳輸的最大續寫重試次數。 |
| `TOKEN_COMPRESSION_ENABLED` | `true` | 在路由至供應商前壓縮超長對話歷史。 |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | 觸發上下文壓縮的預估輸入權杖閾值。 |
| `TOKEN_COMPRESSION_TARGET` | `24000` | 壓縮後的預估輸入權杖目標值。必須低於觸發閾值。 |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | 壓縮過程中必須保留的最近使用者輪次最少數。 |
| `COMPATIBILITY_MODE` | `false` | 為不相容系統訊息的客戶端/模型自動轉換 System 訊息。 |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | 在可用時回傳模型的思考推理過程（reasoning）。 |
| `MONGODB_URI` | 空 | 設定後啟用 MongoDB 儲存後端。 |
| `POSTGRESQL_URI` | 空 | 設定後啟用 PostgreSQL 儲存後端。 |
| `REDIS_URL` | 空 | 設定後啟用 Redis 快取與工作階段狀態加速。 |
| `CODE_ASSIST_CLIENT_ID` | 內建桌面客戶端 | Code Assist OAuth Client ID 的可選覆蓋值。 |
| `CODE_ASSIST_CLIENT_SECRET` | 內建桌面客戶端 | Code Assist OAuth Client Secret 的可選覆蓋值。 |
| `ANTIGRAVITY_CLIENT_ID` | 內建桌面客戶端 | Google Antigravity OAuth Client ID 的可選覆蓋值，亦可在供應商頁面配置。 |
| `ANTIGRAVITY_CLIENT_SECRET` | 內建桌面客戶端 | Google Antigravity OAuth Client Secret 的可選覆蓋值，上游變更時可透過環境變數或供應商頁面調整。 |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Google AI Studio Generative Language API 的可選服務位址覆蓋值。 |
| `XAI_API_URL` | `https://api.x.ai/v1` | SpaceXAI Console API 金鑰憑證的可選 API 服務位址覆蓋值，亦可在供應商頁面配置。 |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Grok Build OAuth 訂閱端點的可選服務位址覆蓋值。 |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Grok Build OAuth Issuer 的可選覆蓋值。控制台僅接受 `x.ai` 網域下的 HTTPS 主機。 |
| `XAI_CLIENT_ID` | 內建公開客戶端 | Grok Build PKCE OAuth Client ID 的可選覆蓋值。 |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Grok Build OAuth 與 SpaceXAI Console API 請求共用的可選 HTTP User-Agent 覆蓋值。 |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | OpenAI Platform API 的可選服務位址覆蓋值，亦可在供應商頁面配置。 |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Codex 推論與帳戶模型列表端點的可選覆蓋值。 |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Codex 帳戶速率限制查詢端點的可選覆蓋值。 |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Codex 裝置授權服務的可選服務位址覆蓋值。 |
| `CODEX_CLIENT_ID` | 內建公開客戶端 | Codex 裝置 OAuth Client ID 的可選覆蓋值。 |
| `CODEX_USER_AGENT` | Codex CLI 相容值 | Codex 請求的可選 User-Agent 覆蓋值。 |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Claude Platform 與 Claude Code Messages API 的可選服務位址覆蓋值，亦可在供應商頁面配置。 |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Claude Code PKCE 授權端點的可選覆蓋值。控制台僅接受 Anthropic 與 Claude 官方主機。 |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Claude Code Token 端點的可選覆蓋值。控制台僅接受 Anthropic 與 Claude 官方主機。 |
| `CLAUDE_CLIENT_ID` | 內建公開客戶端 | Claude Code PKCE OAuth Client ID 的可選覆蓋值。 |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Claude Code 與 Claude Platform 請求的可選 User-Agent 覆蓋值。 |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Google Antigravity 協定層級請求的可選 User-Agent 覆蓋值。 |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Google Antigravity 負載層 userAgent 的可選覆蓋值。 |
| `METRICS_TOKEN` | empty | At least 32 bytes; required with opt-in `PROMETHEUS_EXPORT_ENABLED=true`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | 執行階段日誌記錄層級。 |
| `LOG_MAX_MB` | `10` | 單一活動日誌檔案在輪替前的最大體積（MB）。 |
| `LOG_BACKUP_COUNT` | `3` | 保留的歷史輪替日誌檔案數量。 |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | 檔案日誌輸出路徑。在 Docker 中需將 `/app/backend/data/logs` 掛載至宿主機磁碟區。 |

## 快速上手 SDK 接入

Omni Gateway 嚴格按照官方 Python SDK 的標準 URL 行為進行設計。請完全參照下文方式配置客戶端，閘道無需任何非標準的重複路徑前綴。

範例中使用虛擬模型 `omway`。請先在控制台的「模型」頁面配置其優先順序回退模型鏈，或者直接將其替換為具體的供應商模型 ID。

### OpenAI Python SDK

將 OpenAI 的 Base URL 設定為 `/v1`，SDK 會自動在末尾追加 `/chat/completions`。

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway", messages=[{"role": "user", "content": "用一段話解釋這個程式庫。"}]
)
```

同一客戶端亦可以直接調用 OpenAI Responses API：

```python
response = client.responses.create(
    model="omway", instructions="請簡明扼要。", input="用一段話解釋這個程式庫。"
)

print(response.output_text)
```

Responses 相容層支援文字輸入、圖片輸入、非串流 Function Tool 以及 SSE 文字串流傳輸。對於 OpenAI 託管的內建工具、持久化回應歷史以及串流函式調用，閘道會明確回傳錯誤拒絕請求，因為 Omni Gateway 不會執行、持久化或隱含捨棄這些 OpenAI 特有的專有行為。

### Anthropic Python SDK

將 Anthropic 的 Base URL 直接指向閘道根位址，SDK 會自動在末尾追加 `/v1/messages`。

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "撰寫一條 Git 提交訊息。"}],
)
```

### Google GenAI Python SDK

將 Google GenAI 的 Base URL 直接指向閘道根位址，SDK 會自動追加預設模型路由，例如 `/v1beta/models/{model}:generateContent`。

```python
from google import genai
from google.genai import types

client = genai.Client(http_options={"base_url": "http://127.0.0.1:4283"}, api_key="sk-ogw-...")

response = client.models.generate_content(
    model="omway",
    contents="寫一個簡短的 Python 函式。",
    config=types.GenerateContentConfig(system_instruction="你是一個得力的程式設計助手。"),
)
```

### 支援的路由列表

Omni Gateway 提供標準 SDK 相容路由，無需額外的產品命名空間前綴：

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

身分認證、請求校驗、路由選擇、上游調用及串流啟動前的失敗均使用對應 SDK 介面的原生錯誤格式包裹。每個 HTTP 回應均包含 `X-Request-ID` 請求標識；客戶端可在該請求標頭傳入安全標識以進行全鏈路追蹤。當上游回傳速率限制或暫時無法使用時，閘道將原樣保留並透傳 `Retry-After` 標頭。

## 模型特性與高級控制

控制台「模型」頁面透過已啟用的各供應商憑證中探索到的模型，聚合建構出虛擬模型 `omway`。只需設定一次各底層模型的優先順序順序，即可在任意支援的 SDK 中使用 `omway`。Omni Gateway 會在支援第一順位模型的健康憑證之間進行負載平衡；當該模型無法使用時，自動依次降級嘗試後續配置的模型。具體的供應商物理模型 ID 依然保留可用，以滿足需要確定性指定模型的客戶端需求。儲存空列表即可停用 `omway`，這不會影響任何供應商憑證。

模型探索機制具備供應商感知能力：通用模型可由多個供應商共同支援，而專有模型僅由相容的憑證承接。每個已驗證的憑證獨立儲存其專屬的供應商目錄，路由器優先採用憑證明確宣告支援的模型，而非通用的供應商類型推斷。重新整理目錄將重新拉取目前供應商的即時可用性；無法使用的配置項將保持可見，直到其復原或被手動移除。

當上游對某個物理模型回傳 `404` 時，Omni Gateway 會在該憑證與模型作用域內記錄無法使用路由，而非直接停用整個供應商。該路由將立即被暫時避開，並在**無法使用模型路由**列表中保持可見，直到被手動清除或該憑證重新校驗通過。這避免了因單一帳戶的訂閱權限或地域限制而影響同一供應商下的其他健康帳戶。若啟用的憑證均未宣告或推斷支援所請求的模型，閘道將回傳明確的無相容憑證錯誤，而不是將請求隨機發往不符合的供應商。

Omni Gateway 支援在模型名稱中解析特性前綴與後綴：

- `fake-streaming/{model}` 或配置的偽串流前綴，適用於強制要求 SSE 輸出的客戶端。
- `streaming-anti-truncation/{model}` 或配置的防截斷前綴，用於長文本串流生成的自動續寫復原。
- 思考深度後綴（如 `-high`、`-medium`、`-low`、`-minimal`、`-max`），適用於支援該特性的 Gemini 系列模型。
- 連網搜尋後綴（如 `-search`），適用於支援 Google Search 搜尋接地的模型。

供應商適配器會在向上游發送請求前自動將這些特性標識規範化。

## 使用量與成本透明度

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## 憑證配置工作流程

1. 啟動 Omni Gateway。
2. 在 VPS 上造訪 `http://你的伺服器IP:4283`，或在本地開發時造訪 `http://127.0.0.1:4283`。
3. 在首次執行頁面建立控制台密碼。遠端部署需輸入應用日誌中的引導權杖；或者預先配置 `PANEL_PASSWORD`。
4. 在「供應商」頁面新增帳戶、API 金鑰或 Ollama 連線。
5. 驗證憑證有效性，並在面板中監控冷卻時間與錯誤狀態。
6. 將你的程式設計工具連接至上述支援的 API 介面之一。

新增 Google Antigravity 憑證時，Google 會在登入完成後將瀏覽器重新導向至 `http://localhost:4283/callback`。在本地機器上，Omni Gateway 會直接展示 OAuth 授權成功頁面。在 VPS 上，由於該 `localhost` 指向使用者的本地瀏覽器機器，頁面可能無法開啟；只需複製瀏覽器網址列中的完整 URL，返回「供應商」頁面貼至 `Callback URL` 框中，點擊 `儲存憑證` 即可。

Google AI Studio 使用 API 金鑰認證而非 OAuth。在「供應商」頁面新增金鑰後，Omni Gateway 將對照 Google 模型目錄驗證其有效性，儲存為供應商憑證，並將相容的 Gemini 或 Gemma 請求路由至該憑證。智慧路由器可以在共用的 Gemini 模型上於 AI Studio 與 Google Antigravity 之間自動容錯移轉，同時保證專有模型僅由相容憑證承接。

Google AI Studio 批次匯入支援 JSON 檔案及包含 JSON 檔案的 ZIP 壓縮檔。JSON 檔案可包含單條金鑰、`api_keys` 陣列或金鑰物件陣列：

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

每個匯入的金鑰在入庫前均經過嚴格校驗。同批次內的重複金鑰將被略過，已存在的金鑰將重新校驗並更新，無效記錄將直接報錯且不會洩漏金鑰明文。

Grok Build 支援 PKCE OAuth 憑證，而 SpaceXAI Console 支援 API 金鑰。SpaceXAI Console 金鑰在儲存前會對照 Grok Build 模型目錄進行驗證。對於 Grok Build OAuth，Omni Gateway 會產生授權連結；授權完成後，複製授權頁面展示的授權碼並貼至表單中。當存在 Refresh Token 時系統會自動重新整理存取權杖，且兩種憑證類型均僅暴露其目前目錄宣告的 Grok Build 模型。在「憑證池」頁面，可查詢 Grok Build OAuth 帳戶的月度額度消耗情況，以及 xAI 提供時的週度使用量。該帳戶級帳單檢視不支援 SpaceXAI Console API 金鑰。

Codex 使用 OpenAI 裝置授權流程。在「供應商」頁面產生裝置代碼，開啟展示的驗證網址，輸入代碼完成登入，然後返回檢查授權狀態。Omni Gateway 將儲存 Codex 回傳的帳戶級模型目錄，在需要時自動重新整理 OAuth 存取權杖，並透過 Codex Responses 傳輸協定轉發相容請求。OpenAI Platform 使用 API 金鑰認證；金鑰在入池前均透過帳戶模型目錄進行有效性校驗。兩款產品均支援 JSON 與 ZIP 匯入，並具備供應商特定的校驗與去重能力。

Claude Code 使用 Anthropic 的 PKCE OAuth 流程。產生授權連結，完成授權後將回傳的授權碼貼回「供應商」頁面。Claude Platform 接收 Anthropic API 金鑰。兩款產品均可探索每個憑證支援的模型列表，使用 Anthropic Messages 傳輸協定，在可能時自動重新整理 Claude Code 存取權杖，並支援帶校驗的 JSON 或 ZIP 匯入。

Ollama 連線按端點配置，並可包含用於受保護或雲端伺服器的可選 Bearer API 金鑰。Omni Gateway 透過 `/api/tags` 探索可用模型，並透過 `/api/chat` 執行推論路由。當 Omni Gateway 執行在 Docker 中時，`localhost` 指向容器本身；請使用宿主機閘道位址或網路可達的其他 Ollama 端點。

憑證池完整匯入與 Google Antigravity 批次匯入支援最大 10 MB 的壓縮檔、最多 500 個檔案、單一憑證檔案最大 2 MB 以及解壓縮後最大 25 MB 的資料量。Google AI Studio、OpenAI、Anthropic 與 Ollama 供應商單項匯入採用更嚴格的限制：單一匯入檔案最大 2 MB、最多 200 條 JSON 記錄、解壓縮後最大 5 MB。

「憑證池」頁面亦提供獨立於供應商的完整備份工作流程。`下載 ZIP` 可匯出目前活躍的完整憑證池，`匯入 ZIP` 透過自動識別憑證類型（Google Antigravity、Google AI Studio、Grok Build、SpaceXAI Console、Codex、OpenAI Platform、Claude Code、Claude Platform 或 Ollama）完成還原。OAuth 帳戶保留基於供應商作用域的身分去重，API 金鑰則透過供應商作用域的不可逆雜湊指紋進行驗證與去重。不支援或格式錯誤的項目將單獨報錯，不會中斷壓縮檔內其他有效憑證的匯入。

Google Antigravity 憑證命名為 `google-antigravity-{account_fingerprint}.json`，指紋衍生自規範化的帳戶電子郵件且不洩漏明文。Google AI Studio 憑證命名為 `google-ai-studio-{key_fingerprint}.json`，Grok Build OAuth 憑證命名為 `grok-{account_fingerprint}.json`，SpaceXAI Console 憑證命名為 `xai-console-{key_fingerprint}.json`，Codex 憑證命名為 `openai-codex-{account_fingerprint}.json`，OpenAI Platform 憑證命名為 `openai-platform-{key_fingerprint}.json`，Claude Code 憑證命名為 `claude-code-{account_fingerprint}.json`，Claude Platform 憑證命名為 `claude-platform-{key_fingerprint}.json`，Ollama 連線命名為 `ollama-{connection_fingerprint}.json`。舊版 `provider_*.json` 與 `xai-grok-*.json` 憑證保持向下相容，並在匯出時自動轉換為標準規範名稱。

憑證模式名稱：

- `code_assist`：標準 Code Assist 憑證池。
- `provider`：通用供應商後端憑證池。

## 資料儲存

單實例部署預設使用掛載資料目錄中的 SQLite 儲存。在 Docker 部署中，請務必將 `/app/backend/data/creds` 與 `/app/backend/data/logs` 掛載到宿主機的持久化路徑（如 `/opt/omni-gateway/creds` 與 `/opt/omni-gateway/logs`）。

可根據維運需求或遷移測試需要，使用 MongoDB 或 PostgreSQL 替代本地 SQLite：

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

亦可新增 Redis 以加速快取與工作階段狀態管理：

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

配置外部儲存並不會使 1.x 執行階段具備水平擴展能力。在實現跨行程分散式憑證預留、冷卻管理、工作階段失效與使用量聚合之前，請保持單 Worker 與單複本執行。MongoDB 與 PostgreSQL 僅能二選一，不可同時配置；若外部資料庫初始化失敗，閘道將明確終止啟動，而不會靜默降級回退到 SQLite。

支援透過環境變數匯入憑證。可在控制台操作，或將以下變數之一設定為原始 JSON 字串，亦可使用帶 `_B64` 後綴的 Base64 編碼字串：

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

負載內容可以是單一憑證物件、憑證陣列或 `{ "credentials": [...] }` 結構。

## 開發指南

本節面向專案貢獻者及本地偵錯。生產環境部署請使用帶有持久化宿主機磁碟區的 Docker 方案。

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

所有程式碼檢查均通過後啟動服務：

```bash
python backend/main.py
```

生產執行基準為 Python 3.12，CI 自動化測試涵蓋 Python 3.12 與 3.14。有關 Pull Request 提交流程與程式碼審查標準，請參閱[貢獻指南](../../CONTRIBUTING.md)。

## 部署注意事項

- 切勿提交包含憑證的 JSON 檔案或 `.env` 檔案。
- 為客戶端整合配置專用的 `API_KEY`，並為控制台造訪設定獨立的 `PANEL_PASSWORD`。
- 嚴格限制對持久化憑證資料磁碟區或外部資料庫的造訪權限，並在平台層啟用靜態落盤加密；路由器必須能夠解密讀取供應商權杖。
- 當服務暴露於非 localhost 環境時，務必將 Omni Gateway 置於配置了 TLS 的反向代理之後。
- 配置反向代理保留 `Host` 請求標頭並傳遞 `X-Forwarded-Proto`；在確認全程 HTTPS 終止時設定 `PANEL_COOKIE_SECURE=true`。
- 僅當服務完全僅經由會改寫 `X-Forwarded-For` 與 `X-Forwarded-Proto` 的受信任代理造訪時，才設定 `TRUST_PROXY_HEADERS=true`。
- 使用 `GET /health` 進行行程存活探針檢查，使用 `GET /ready` 進行包含儲存層感知的整備探針檢查。
- Docker 映像檔僅在啟動初期以 root 權限修復掛載資料目錄的權限歸屬，隨後降權切換至無特權的 `gateway` 使用者執行。
- 當瀏覽器客戶端需要跨來源造訪時，請將 `CORS_ORIGINS` 明確設定為受信任的來源。
- 在升級版本或遷移伺服器前，請務必備份 `/opt/omni-gateway` 或自訂的 `DATA_DIR` 目錄。
- Docker 映像檔發布使用倉庫密鑰 `DOCKERHUB_USERNAME` 與 `DOCKERHUB_TOKEN` 推送至 Docker Hub，並使用內建的 `GITHUB_TOKEN` 推送至 GitHub Packages（`ghcr.io/nguywnben/omni-gateway`）。僅在發布到自訂 Docker Hub 映像檔名稱時才設定可選的 `IMAGE_NAME` 變數。
- 在 1.x 系列版本中，請保持 `WORKERS=1` 與單應用複本；外部儲存無法替代分散式協同機制。
- 請使用標準規範的 `/api/credentials` 管理路由。Beta 階段的 `/api/creds` 別名已在 1.0.0 中徹底移除。
- 在遷移 Beta 版本部署前，請先查閱[升級至 1.0 指南](../upgrading-to-1.0.md)。
- 升級現有執行實例或復原版本時，請參考[更新指南](../updating.md)。
- 在打 Tag 或發布映像檔前，請對照維護的[發布核對清單](../release-checklist.md)逐項確認。
- 請根據實際用量配額合理制定日誌保留與憑證輪替策略。
- 一旦程式碼倉庫或雲端平台安全掃描警示憑證洩漏，請立即撤銷並輪換該憑證。
- Render 部署清單使用的是帶有持久化硬碟的付費服務。Render 的免費服務使用暫時檔案系統，僅適合一次性測試體驗。

## 社群與專案健康度

- 在提交 Pull Request 前請閱讀[貢獻指南](../../CONTRIBUTING.md)。
- 回報安全漏洞請透過[安全政策](../../SECURITY.md)中註明的私密管道提交。
- 檢視[更新日誌](../../CHANGELOG.md)瞭解各版本的詳細變更。
- 在參與本專案的所有相關活動中均須遵守[行為準則](../../CODE_OF_CONDUCT.md)。

## 致謝與靈感來源

Omni Gateway 站在開源 AI 路由、可觀測性與閘道社群的堅實肩膀之上。我們向以下專案的創作者與維護者致以由衷的敬意與感謝：

| 專案 | 專案描述 | Stars |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | 多供應商金鑰管理與基於 Web 的 API 聚合架構靈感來源 | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | 面向 AI 程式設計 CLI 的開創性多協定代理與格式轉換層 | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | 行業標竿級的統一 LLM 代理、負載平衡與容錯移轉路由 | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | 極速 AI 閘道架構設計、路由策略及高彈性容災模式 | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | 開源 LLM 工程化平台、調用追蹤、系統可觀測性與指標採集 | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## 開源授權

Omni Gateway 基於 [MIT 開源授權](../../LICENSE) 發布。
