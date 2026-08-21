# Omni Gateway

<p align="center">
  <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
  <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
  <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
  <img src="https://img.shields.io/badge/i18n-15%20%E8%AA%9E%E8%A8%80-orange?style=flat-square" alt="15 語言">
</p>

<p align="center">
  <a href="#支援的供應商"><b>🌐 支援的供應商</b></a> •
  <a href="#核心功能"><b>⚡ 核心功能</b></a> •
  <a href="#部署"><b>🐳 Docker 部署</b></a> •
  <a href="#sdk-整合"><b>🔌 SDK 整合</b></a> •
  <a href="../../docs/architecture.md"><b>📖 架構說明</b></a>
</p>

<p align="center">
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

---

適用於程式開發工具的通用 AI 路由器。Omni Gateway 提供智慧自動容錯移轉、權杖感知對話清理、用量可見性與無縫通訊協定轉換，讓本機 Agent、IDE 助理與自動化腳本能透過單一穩定 API 介面調用各類免費與付費 LLM 資源。

> **專案狀態：** 穩定。版本 `1.3.1` 完整支援 15 種語言在地化管理主控台，並提供多語系管理訊息與版本升級指引。

## 為什麼選擇 Omni Gateway

現代程式開發流程通常結合多種客戶端與模型供應商：相容 OpenAI 的工具、Gemini 原生 SDK、Anthropic 格式的 Agent、Google 認證帳戶與實驗性模型路由。Omni Gateway 介於兩者之間，讓各工具維持原生調用方式，同時由閘道自動處理負載調度、重試、請求清理與回應標準化。

## 核心功能

- **智慧自動容錯移轉：** 針對每個請求預先保留憑證，平攤並行流量，記錄調用歷史以公平輪替，自動避開近期錯誤、冷卻時間、速率限制與用盡額度的憑證。
- **權杖感知清理：** 於對話輪次安全邊界裁剪超長歷史，完整保留系統提示詞、工具定義與最近上下文。
- **多向格式轉換：** 支援 OpenAI Chat Completions & Responses、Gemini 原生與 Anthropic Messages，並於各協定串流/非串流間自動轉換。
- **憑證集區全生命週期管理：** 支援 OAuth 帳戶與 API 金鑰集區，具備健康度監控、冷卻追蹤、除重與自動還原能力。
- **憑證層級模型路由隔離：** 為每個憑證維護獨立能力清單，避免請求轉發至不支援該模型的帳號。
- **串流彈性保障：** 支援標準 SSE、偽串流以及長文本防截斷自動續寫機制。
- **整合式 Web 主控台：** 提供直覺的憑證管理、即時日誌、系統設定、用量分析與版本檢測介面。

## 主控台預覽

![Omni Gateway credential pool](../../docs/assets/screenshots/credential-pool.png)

## <a id="支援的供應商"></a>支援的供應商

| 供應商 | 驗證方式 | 支援通訊協定 | 自動容錯移轉 | 支援串流 |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (本機/自託管)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## <a id="部署"></a>部署

### Docker 部署（推薦）

於伺服器上建立持久化目錄：

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

啟動容器：

```bash
sudo docker run -d \
  --name omni-gateway \
  --pull always \
  --restart unless-stopped \
  -p 4283:4283 \
  -v /opt/omni-gateway/creds:/app/backend/data/creds \
  -v /opt/omni-gateway/logs:/app/backend/data/logs \
  nguywnben/omni-gateway:1.3.1
```

開啟瀏覽器進入主控台：`http://YOUR_SERVER_IP:4283`

首次啟動時請依畫面指示設定主控台密碼。若為遠端伺服器，請輸入 `docker logs omni-gateway` 所產生的引導 Token。

## 授權條款

Omni Gateway 採用 [MIT 授權條款](../../LICENSE)。
