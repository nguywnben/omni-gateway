# Omni Gateway

<p align="center">
  <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
  <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
  <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
  <img src="https://img.shields.io/badge/i18n-15%20%E8%AF%AD%E8%A8%80-orange?style=flat-square" alt="15 语言">
</p>

<p align="center">
  <a href="#支持的提供商"><b>🌐 支持的提供商</b></a> •
  <a href="#核心功能"><b>⚡ 核心功能</b></a> •
  <a href="#部署"><b>🐳 Docker 部署</b></a> •
  <a href="#sdk-接入"><b>🔌 SDK 接入</b></a> •
  <a href="../../docs/architecture.md"><b>📖 架构设计</b></a>
</p>

<p align="center">
  <a href="../../README.md">English</a> •
  <a href="README.vi.md">Tiếng Việt</a> •
  <b>中文(简体)</b> •
  <a href="README.zh-TW.md">中文(繁體)</a> •
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

面向编程工具的通用 AI 路由器。Omni Gateway 提供智能自动故障转移、令牌感知上下文清理、使用量可视化和无缝协议转换，让本地 Agent、IDE 助手和自动化脚本可以通过一个稳定的 API 接口调用各种免费与付费的 LLM 资源。

> **项目状态：** 稳定。版本 `1.3.1` 支持 15 种语言的完整本地化控制台，提供多语言管理接口提示及版本更新指南。

## 为什么选择 Omni Gateway

现代编程工作流通常混用各种客户端与模型提供商：OpenAI 兼容工具、Gemini 原生 SDK、Anthropic 格式的智能体、Google 账户以及各种实验性模型路由。Omni Gateway 位于客户端与后端之间，让每个工具继续使用原本熟悉的调用格式，同时在底层完成路由分发、自动重试、请求清洗与响应标准化。

## 核心功能

- **智能自动故障转移：** 按请求预留凭据，均衡并发流量，追踪调用历史以实现公平轮换，并自动绕过近期错误、冷却状态、速率限制与耗尽额度的凭据。
- **令牌感知清理：** 在安全的对话回合边界裁剪过长历史，保留系统提示词、工具定义以及最近上下文。
- **多向格式转换：** 支持 OpenAI Chat Completions & Responses、Gemini 原生及 Anthropic Messages 请求，并在流式与非流式响应间自动转换。
- **凭据全生命周期管理：** 支持 OAuth 账户与 API Key 凭据池，具备健康检查、冷却追踪、防重及自动故障恢复能力。
- **凭据级模型路由隔离：** 为每个凭据维护独立能力清单，避免把请求发送给不支持该模型的账号。
- **流式弹性保障：** 支持标准 SSE、伪流式以及长文本防截断自动续写重试。
- **内置 Web 控制台：** 提供直观的凭据管理、实时日志、配置调整、用量分析与版本检测界面。

## 控制台预览

![Omni Gateway credential pool](../../docs/assets/screenshots/credential-pool.png)

## <a id="支持的提供商"></a>支持的提供商

| 提供商 | 认证方式 | 支持协议 | 自动故障转移 | 流式传输 |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (本地/私有部署)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## <a id="部署"></a>部署

### Docker 部署（推荐）

在服务器上创建持久化存储目录：

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

启动容器：

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

在浏览器打开管理面板：`http://YOUR_SERVER_IP:4283`

首次运行时根据页面提示设置控制台密码。若从远程访问，需输入 `docker logs omni-gateway` 输出中的引导 Token。

## <a id="sdk-接入"></a>SDK 接入

### OpenAI SDK (Python)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "用一句话介绍这个项目。"}],
)
print(response.choices[0].message.content)
```

## 开源协议

Omni Gateway 遵循 [MIT 开源协议](../../LICENSE)。
