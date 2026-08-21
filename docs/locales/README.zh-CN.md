<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>面向 AI 编程工具的通用 AI 路由器与多供应商统一网关</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#支持的供应商"><b>🌐 支持的供应商</b></a> •
    <a href="#核心能力"><b>⚡ 核心能力</b></a> •
    <a href="#部署"><b>🐳 Docker 部署</b></a> •
    <a href="#快速上手-sdk-接入"><b>🔌 SDK 接入</b></a> •
    <a href="../architecture.md"><b>📖 架构设计</b></a>
  </p>

  <p>
    <b>控制台与文档语言：</b><br>
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
</div>

---

面向编程工具的通用 AI 路由器。Omni Gateway 提供智能自动故障转移、令牌感知上下文清理、使用量可视化和无缝格式转换，让本地 Agent、IDE 助手和自动化脚本可以通过一个稳定的 API 接口调用各种免费与付费的 LLM 算力。

> **项目状态：** 稳定。版本 `1.3.1` 完善了支持 15 种语言的本地化控制台，新增感知语言环境的管理 API 提示信息和版本更新指南，并保留了从 `1.0.0` 确立的稳定 SDK 路由、规范管理路由、配置命名和单实例运行契约。

## 为什么选择 Omni Gateway

现代编程工作流通常混合使用多种客户端与模型供应商：OpenAI 兼容工具、Gemini 原生 SDK、Anthropic 风格的 Agent、Google 凭据以及实验性模型路由。Omni Gateway 位于这些客户端与模型后端之间，让每个工具继续使用其原生协议，同时由网关统一处理请求路由、重试、上下文清理和响应格式标准化。

## 核心能力

- 智能自动故障转移：按请求预留凭据，均衡并发流量，追踪每次调用以实现公平轮询，并自动绕过近期故障、冷却期、速率限制及额度耗尽的凭据。
- 令牌感知清理：规范化请求负载，仅在安全的对话轮次边界处修剪过长的历史前缀，同时完整保留系统指令、工具定义和最近上下文。
- 格式协议转换：接收 OpenAI Chat Completions 与 Responses、Gemini 原生请求及 Anthropic Messages，并在不同格式与流式响应之间双向转译。
- 凭据生命周期编排：管理 OAuth 账户与供应商 API 密钥，提供健康状态检查、冷却追踪、有效性校验、去重和供应商感知故障转移。
- 凭据级模型路由：为每个凭据维护独立的能力目录，防止某个账户的模型权限将请求误发到不支持该模型的其他账户。
- 路由健康记忆：在凭据级别记录模型未找到（404）响应，并在模型管理页面展示受影响的路由以便恢复。
- 流式传输弹性：支持 SSE 流式传输、为强制要求流式输出的客户端提供伪流式（pseudo-streaming），并为长文本生成提供防截断重试。
- Web 控制面板：自带 Web 控制台，用于凭据管理、日志查看、系统配置、使用量统计和版本信息查看。

## 控制台预览

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## 支持的供应商

Omni Gateway 在主流 AI 供应商、本地运行时和 OAuth 终端之间无缝适配请求：

| 供应商 | 认证类型 | 支持的协议 | 自动故障转移 | 流式传输 |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI 兼容, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI 兼容 | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (本地 / 自托管)** | 本地 / Base URL | OpenAI 兼容 | ✅ | ✅ |

## 架构设计

```text
客户端工具
  OpenAI SDK | Google GenAI SDK | Anthropic SDK | IDE 集成插件
        |
        v
Omni Gateway
  身份认证 -> 格式协议转换 -> 令牌感知清理 -> 路由分发 -> 故障转移 -> 流式输出
        |
        v
供应商适配器
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

在 Omni Gateway 后端适配器持续演进的同时，对外的公共 API 契约保持绝对稳定。

## 代码仓库结构

```text
backend/       FastAPI 组合根、路由核心、协议转换器、存储层与测试用例
frontend/      管理控制台页面结构、样式、脚本及供应商图标资产
deploy/        容器定义、平台部署清单与操作系统启动脚本
docs/          架构设计说明与项目维护文档
.github/       CI 流水线、依赖自动化与贡献模板
```

详见[架构设计](../architecture.md)，了解模块边界、请求处理流程、状态归属与当前版本的发布约束。

## 部署

Omni Gateway 为生产部署而设计。Docker 是 VPS 和服务器环境的推荐方案，既能保证运行时隔离，又能在宿主机持久化保存凭据和日志。

### 在 VPS 上使用 Docker 部署

首先在宿主机创建持久化目录：

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

启动服务容器：

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

同一版本也已发布至 GitHub Packages：`ghcr.io/nguywnben/omni-gateway:1.3.1`。`latest` 标签跟踪最新的稳定版本；`edge` 标签跟踪经测试但尚未正式发布的 `main` 分支构建。在需要环境可复现的场景下，建议固定具体版本号或镜像摘要。

打开浏览器访问控制台：

```text
http://你的服务器IP:4283
```

首次运行时，在初始化页面设置控制台密码。项目未内置任何默认密码。通过远程浏览器访问时，还必须输入 `docker logs omni-gateway` 输出的引导令牌（bootstrap token）；直接在本地 localhost 访问则无需输入。若需自动化部署，可在启动前预先设置 `SETUP_TOKEN` 环境变量。

系统管理的密码均以加盐 scrypt 哈希安全存储，控制台会话使用 HttpOnly Cookie，公共 SDK 请求则使用自动生成的 `sk-ogw-` API 密钥进行鉴权。如需非交互式部署，可预先配置 `PANEL_PASSWORD` 直接跳过初始化引导界面。

`1.3.1` 镜像针对 `linux/amd64` 平台构建发布。ARM64 镜像发布暂缓，直到包括 Vertex 传输栈在内的所有供应商依赖均能在同一标准下构建并通过测试。

若服务器启用了防火墙，请放行网关端口：

```bash
sudo ufw allow 4283/tcp
```

查看实时日志：

```bash
sudo docker logs -f omni-gateway
```

更新到最新稳定版本：

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

随后使用上方相同的 `docker run` 命令重新启动容器。挂载的 `/opt/omni-gateway` 目录将在容器更新期间完整保留凭据、配置、使用量数据和日志。

### Docker Compose 部署

适用于基于源码仓库的部署方式：

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

附带的 Compose 文件默认拉取 `nguywnben/omni-gateway:latest` 并使用 `/opt/omni-gateway` 存储宿主机数据。可通过设置 `IMAGE=nguywnben/omni-gateway:1.3.1` 来锁定该版本，或设置 `DATA_DIR=/自定义路径` 使用不同的存储路径。

Compose 会从 Shell 环境变量或根目录 `.env` 文件传递 `API_KEY`、`PANEL_PASSWORD`、`SETUP_TOKEN`、外部存储 URI 和 `PROXY`。留空即可保持自动生成密钥、首次引导配置、本地 SQLite 存储和直接网络出站的默认行为。

### 本地开发

在本地进行开发或调试网关时，请使用 Python 原生工作流：

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Windows PowerShell 环境：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

在浏览器打开控制面板：

```text
http://127.0.0.1:4283
```

本地开发环境与 Docker 部署采用相同的首次运行初始化设置页面。

## 配置项

Omni Gateway 读取配置的优先级为：环境变量 > 已保存配置 > 默认值。

| 环境变量 | 默认值 | 用途说明 |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | 绑定监听地址。 |
| `PORT` | `4283` | HTTP 端口。 |
| `HOST_PORT` | `4283` | 宿主机端口，仅供 Docker Compose 使用。 |
| `WORKERS` | `1` | 1.x 系列支持的 Worker 数量。在跨进程的凭据预留、冷却、会话和使用量聚合实现前，其他数值会被拒绝。 |
| `CORS_ORIGINS` | 空 | 允许跨域调用 API 的浏览器 Origin 列表（逗号分隔）。同源控制台访问请保持为空。 |
| `CORS_ORIGIN_REGEX` | 空 | 用于匹配动态浏览器 Origin 的可选正则表达式。 |
| `API_KEY` | 自动生成 | 供公共客户端 API 请求使用的首选密钥。必须以 `sk-ogw-` 开头。 |
| `PANEL_PASSWORD` | 引导前为空 | Web 控制面板的访问密码。 |
| `SETUP_TOKEN` | 进程随机生成 | 用于远程首次初始化设置的可选固定引导令牌。省略时可从应用或容器日志中获取生成的令牌。 |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Web 控制台会话有效期（秒）。 |
| `PANEL_COOKIE_SECURE` | 自动检测 | 设为 `true` 强制仅在 HTTPS 下传输 Cookie。留空时通过 `X-Forwarded-Proto` 自动检测。 |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | 登录频率限制时间窗口（秒）。 |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | 限制窗口期内单个客户端允许的最大失败登录尝试次数。 |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | 内存中登录频率限制器追踪的最大客户端地址数量。 |
| `MAX_REQUEST_BODY_MB` | `64` | 最大 HTTP 请求体大小（MiB）。超出限制的 SDK 请求将返回对应协议的原生错误包。 |
| `TRUST_PROXY_HEADERS` | `false` | 仅在下游存在可信的反向代理且会覆写转发头时才接收客户端与协议转发头。 |
| `CREDENTIALS_DIR` | `./backend/data/creds` | 凭据存储目录。在 Docker 中需将 `/app/backend/data/creds` 挂载至宿主机卷。 |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist 后端服务地址。 |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Google Antigravity 后端服务地址。 |
| `PROXY` | 空 | 可选的 HTTP、HTTPS 或 SOCKS 代理。 |
| `RETRY_429_ENABLED` | `true` | 对速率限制和上游临时故障启用有界重试。保留旧名称以兼容既有配置。 |
| `RETRY_429_MAX_RETRIES` | `5` | 上游临时故障的最大重试次数。 |
| `RETRY_429_INTERVAL` | `1` | 临时重试的基础退避间隔（秒）。 |
| `AUTO_DISABLE` | `false` | 在发生配置的严重错误后自动禁用对应凭据。 |
| `AUTO_DISABLE_ERROR_CODES` | `403` | 逗号分隔的严重错误状态码列表。 |
| `ROUTING_STRATEGY` | `balanced` | 凭据选择策略：`balanced`（均衡）或 `priority`（优先级）。 |
| `PREFERRED_PROVIDER` | 空 | `priority` 策略优先选用的供应商，例如 `google_antigravity` 或 `google_ai_studio`。 |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | 供应商推理超时时间，限制在 5 到 900 秒之间。 |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | 防截断流式传输的最大续写重试次数。 |
| `TOKEN_COMPRESSION_ENABLED` | `true` | 在路由至供应商前压缩超长对话历史。 |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | 触发上下文压缩的预估输入令牌阈值。 |
| `TOKEN_COMPRESSION_TARGET` | `24000` | 压缩后的预估输入令牌目标值。必须低于触发阈值。 |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | 压缩过程中必须保留的最近用户轮次最少数。 |
| `COMPATIBILITY_MODE` | `false` | 为不兼容系统消息的客户端/模型自动转换 System 消息。 |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | 在可用时返回模型的思考推理过程（reasoning）。 |
| `MONGODB_URI` | 空 | 设置后启用 MongoDB 存储后端。 |
| `POSTGRESQL_URI` | 空 | 设置后启用 PostgreSQL 存储后端。 |
| `REDIS_URL` | 空 | 设置后启用 Redis 缓存与会话状态加速。 |
| `CODE_ASSIST_CLIENT_ID` | 内置桌面客户端 | Code Assist OAuth Client ID 的可选覆盖值。 |
| `CODE_ASSIST_CLIENT_SECRET` | 内置桌面客户端 | Code Assist OAuth Client Secret 的可选覆盖值。 |
| `ANTIGRAVITY_CLIENT_ID` | 内置桌面客户端 | Google Antigravity OAuth Client ID 的可选覆盖值，也可在供应商页面配置。 |
| `ANTIGRAVITY_CLIENT_SECRET` | 内置桌面客户端 | Google Antigravity OAuth Client Secret 的可选覆盖值，上游变更时可通过环境变量或供应商页面调整。 |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Google AI Studio Generative Language API 的可选服务地址覆盖值。 |
| `XAI_API_URL` | `https://api.x.ai/v1` | SpaceXAI Console API 密钥凭据的可选 API 服务地址覆盖值，也可在供应商页面配置。 |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Grok Build OAuth 订阅端点的可选服务地址覆盖值。 |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Grok Build OAuth Issuer 的可选覆盖值。控制台仅接受 `x.ai` 域名下的 HTTPS 主机。 |
| `XAI_CLIENT_ID` | 内置公开客户端 | Grok Build PKCE OAuth Client ID 的可选覆盖值。 |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Grok Build OAuth 与 SpaceXAI Console API 请求共享的可选 HTTP User-Agent 覆盖值。 |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | OpenAI Platform API 的可选服务地址覆盖值，也可在供应商页面配置。 |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Codex 推理与账户模型列表端点的可选覆盖值。 |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Codex 账户速率限制查询端点的可选覆盖值。 |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Codex 设备授权服务的可选服务地址覆盖值。 |
| `CODEX_CLIENT_ID` | 内置公开客户端 | Codex 设备 OAuth Client ID 的可选覆盖值。 |
| `CODEX_USER_AGENT` | Codex CLI 兼容值 | Codex 请求的可选 User-Agent 覆盖值。 |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Claude Platform 与 Claude Code Messages API 的可选服务地址覆盖值，也可在供应商页面配置。 |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Claude Code PKCE 授权端点的可选覆盖值。控制台仅接受 Anthropic 和 Claude 官方主机。 |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Claude Code Token 端点的可选覆盖值。控制台仅接受 Anthropic 和 Claude 官方主机。 |
| `CLAUDE_CLIENT_ID` | 内置公开客户端 | Claude Code PKCE OAuth Client ID 的可选覆盖值。 |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Claude Code 与 Claude Platform 请求的可选 User-Agent 覆盖值。 |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Google Antigravity 协议级请求的可选 User-Agent 覆盖值。 |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Google Antigravity 载荷层 userAgent 的可选覆盖值。 |
| `LOG_LEVEL` | `info` | 运行时日志记录级别。 |
| `LOG_MAX_MB` | `10` | 单个活动日志文件在轮转前的最大体积（MB）。 |
| `LOG_BACKUP_COUNT` | `3` | 保留的历史轮转日志文件数量。 |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | 文件日志输出路径。在 Docker 中需将 `/app/backend/data/logs` 挂载至宿主机卷。 |

## SDK 接入

Omni Gateway 严格按照官方 Python SDK 的标准 URL 行为进行设计。请完全参照下文方式配置客户端，网关无需任何非标准的重复路径前缀。

示例中使用虚拟模型 `omway`。请先在控制台的“模型”页面配置其优先级回退模型链，或者直接将其替换为具体的供应商模型 ID。

### OpenAI Python SDK

将 OpenAI 的 Base URL 设置为 `/v1`，SDK 会自动在末尾追加 `/chat/completions`。

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "用一段话解释这个代码仓库。"}]
)
```

同一客户端也可以直接调用 OpenAI Responses API：

```python
response = client.responses.create(
    model="omway",
    instructions="请简明扼要。",
    input="用一段话解释这个代码仓库。"
)

print(response.output_text)
```

Responses 兼容层支持文本输入、图片输入、非流式 Function Tool 以及 SSE 文本流式传输。对于 OpenAI 托管的内置工具、持久化响应历史以及流式函数调用，网关会明确返回错误拒绝请求，因为 Omni Gateway 不会执行、持久化或隐式丢弃这些 OpenAI 特有的专有行为。

### Anthropic Python SDK

将 Anthropic 的 Base URL 直接指向网关根地址，SDK 会自动在末尾追加 `/v1/messages`。

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "撰写一条 Git 提交信息。"}]
)
```

### Google GenAI Python SDK

将 Google GenAI 的 Base URL 直接指向网关根地址，SDK 会自动追加默认模型路由，例如 `/v1beta/models/{model}:generateContent`。

```python
from google import genai
from google.genai import types

client = genai.Client(
    http_options={
        "base_url": "http://127.0.0.1:4283"
    },
    api_key="sk-ogw-..."
)

response = client.models.generate_content(
    model="omway",
    contents="写一个简短的 Python 函数。",
    config=types.GenerateContentConfig(
        system_instruction="你是一个得力的编程助手。"
    )
)
```

### 支持的路由列表

Omni Gateway 提供标准 SDK 兼容路由，无需额外的产品命名空间前缀：

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

身份认证、请求校验、路由选择、上游调用及流式启动前的失败均使用对应 SDK 接口的原生错误格式包裹。每个 HTTP 响应均包含 `X-Request-ID` 请求标识；客户端可在该请求头传入安全标识以进行全链路追踪。当上游返回速率限制或暂时不可用时，网关将原样保留并透传 `Retry-After` 头。

## 模型特性与高级控制

控制台“模型”页面通过已启用的各供应商凭据中发现的模型，聚合构建出虚拟模型 `omway`。只需设置一次各底层模型的优先级顺序，即可在任意支持的 SDK 中使用 `omway`。Omni Gateway 会在支持第一顺位模型的健康凭据之间进行负载均衡；当该模型不可用时，自动依次降级尝试后续配置的模型。具体的供应商物理模型 ID 依然保留可用，以满足需要确定性指定模型的客户端需求。保存空列表即可停用 `omway`，这不会影响任何供应商凭据。

模型发现机制具备供应商感知能力：通用模型可由多个供应商共同支持，而专有模型仅由兼容的凭据承接。每个已验证的凭据独立保存其专属的供应商目录，路由器优先采用凭据显式声明支持的模型，而非通用的供应商类型推断。刷新目录将重新拉取当前供应商的实时可用性；不可用的配置项将保持可见，直到其恢复或被手动移除。

当上游对某个物理模型返回 `404` 时，Omni Gateway 会在该凭据和模型作用域内记录不可用路由，而非直接禁用整个供应商。该路由将立即被临时避开，并在**不可用模型路由**列表中保持可见，直到被手动清除或该凭据重新校验通过。这避免了因单个账户的订阅权限或地域限制而影响同一供应商下的其他健康账户。若启用的凭据均未声明或推断支持所请求的模型，网关将返回明确的无兼容凭据错误，而不是将请求随机发往不匹配的供应商。

Omni Gateway 支持在模型名称中解析特性前缀与后缀：

- `fake-streaming/{model}` 或配置的伪流式前缀，适用于强制要求 SSE 输出的客户端。
- `streaming-anti-truncation/{model}` 或配置的防截断前缀，用于长文本流式生成的自动续写恢复。
- 思考深度后缀（如 `-high`、`-medium`、`-low`、`-minimal`、`-max`），适用于支持该特性的 Gemini 系列模型。
- 联网搜索后缀（如 `-search`），适用于支持 Google Search 搜索接地的模型。

供应商适配器会在向上游发送请求前自动将这些特性标识规范化。

## 使用量与成本透明度

Omni Gateway 在控制台各时间跨度内记录请求量、成功率、凭据归属、供应商上报的 Token 使用量，以及上下文压缩所节省的预估 Token 数量。压缩节省量标为预估值，因为供应商的分词器（Tokenizer）和计费规则具有最终权威。基于供应商价格的动态路由被特意留作未来的策略层，以确保核心 API 在接入更多供应商时保持极简与稳定。

## 凭据配置工作流

1. 启动 Omni Gateway。
2. 在 VPS 上访问 `http://你的服务器IP:4283`，或在本地开发时访问 `http://127.0.0.1:4283`。
3. 在首次运行页面创建控制台密码。远程部署需输入应用日志中的引导令牌；或者预先配置 `PANEL_PASSWORD`。
4. 在“供应商”页面添加账户、API 密钥或 Ollama 连接。
5. 验证凭据有效性，并在面板中监控冷却时间与错误状态。
6. 将你的编程工具连接至上述支持的 API 接口之一。

添加 Google Antigravity 凭据时，Google 会在登录完成后将浏览器重定向至 `http://localhost:4283/callback`。在本地机器上，Omni Gateway 会直接展示 OAuth 授权成功页面。在 VPS 上，由于该 `localhost` 指向用户的本地浏览器机器，页面可能无法打开；只需复制浏览器地址栏中的完整 URL，返回“供应商”页面粘贴至 `Callback URL` 框中，点击 `保存凭据` 即可。

Google AI Studio 使用 API 密钥认证而非 OAuth。在“供应商”页面添加密钥后，Omni Gateway 将对照 Google 模型目录验证其有效性，保存为供应商凭据，并将兼容的 Gemini 或 Gemma 请求路由至该凭据。智能路由器可以在共享的 Gemini 模型上于 AI Studio 与 Google Antigravity 之间自动故障转移，同时保证专有模型仅由兼容凭据承接。

Google AI Studio 批量导入支持 JSON 文件及包含 JSON 文件的 ZIP 压缩包。JSON 文件可包含单条密钥、`api_keys` 数组或密钥对象数组：

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

每个导入的密钥在入库前均经过严格校验。同批次内的重复密钥将被跳过，已存在的密钥将重新校验并更新，无效记录将直接报错且不会泄露密钥明文。

Grok Build 支持 PKCE OAuth 凭据，而 SpaceXAI Console 支持 API 密钥。SpaceXAI Console 密钥在保存前会对照 Grok Build 模型目录进行验证。对于 Grok Build OAuth，Omni Gateway 会生成授权链接；授权完成后，复制授权页面展示的授权码并粘贴至表单中。当存在 Refresh Token 时系统会自动刷新访问令牌，且两种凭据类型均仅暴露其当前目录声明的 Grok Build 模型。在“凭据池”页面，可查询 Grok Build OAuth 账户的月度额度消耗情况，以及 xAI 提供时的周度使用量。该账户级账单视图不支持 SpaceXAI Console API 密钥。

Codex 使用 OpenAI 设备授权流程。在“供应商”页面生成设备代码，打开展示的验证网址，输入代码完成登录，然后返回检查授权状态。Omni Gateway 将保存 Codex 返回的账户级模型目录，在需要时自动刷新 OAuth 访问令牌，并通过 Codex Responses 传输协议转发兼容请求。OpenAI Platform 使用 API 密钥认证；密钥在入池前均通过账户模型目录进行有效性校验。两款产品均支持 JSON 和 ZIP 导入，并具备供应商特定的校验与去重能力。

Claude Code 使用 Anthropic 的 PKCE OAuth 流程。生成授权链接，完成授权后将返回的授权码粘贴回“供应商”页面。Claude Platform 接收 Anthropic API 密钥。两款产品均可发现每个凭据支持的模型列表，使用 Anthropic Messages 传输协议，在可能时自动刷新 Claude Code 访问令牌，并支持带校验的 JSON 或 ZIP 导入。

Ollama 连接按端点配置，并可包含用于受保护或云端服务器的可选 Bearer API 密钥。Omni Gateway 通过 `/api/tags` 发现可用模型，并通过 `/api/chat` 执行推理路由。当 Omni Gateway 运行在 Docker 中时，`localhost` 指向容器本身；请使用宿主机网关地址或网络可达的其他 Ollama 端点。

凭据池完整导入与 Google Antigravity 批量导入支持最大 10 MB 的压缩包、最多 500 个文件、单个凭据文件最大 2 MB 以及解压后最大 25 MB 的数据量。Google AI Studio、OpenAI、Anthropic 和 Ollama 供应商单项导入采用更严格的限制：单个导入文件最大 2 MB、最多 200 条 JSON 记录、解压后最大 5 MB。

“凭据池”页面还提供独立于供应商的完整备份工作流。`下载 ZIP` 可导出当前活跃的完整凭据池，`导入 ZIP` 通过自动识别凭据类型（Google Antigravity、Google AI Studio、Grok Build、SpaceXAI Console、Codex、OpenAI Platform、Claude Code、Claude Platform 或 Ollama）完成还原。OAuth 账户保留基于供应商作用域的身份去重，API 密钥则通过供应商作用域的不可逆哈希指纹进行验证与去重。不支持或格式错误的条目将单独报错，不会阻断压缩包内其他有效凭据的导入。

Google Antigravity 凭据命名为 `google-antigravity-{account_fingerprint}.json`，指纹派生自规范化的账户邮箱且不泄露明文。Google AI Studio 凭据命名为 `google-ai-studio-{key_fingerprint}.json`，Grok Build OAuth 凭据命名为 `grok-{account_fingerprint}.json`，SpaceXAI Console 凭据命名为 `xai-console-{key_fingerprint}.json`，Codex 凭据命名为 `openai-codex-{account_fingerprint}.json`，OpenAI Platform 凭据命名为 `openai-platform-{key_fingerprint}.json`，Claude Code 凭据命名为 `claude-code-{account_fingerprint}.json`，Claude Platform 凭据命名为 `claude-platform-{key_fingerprint}.json`，Ollama 连接命名为 `ollama-{connection_fingerprint}.json`。旧版 `provider_*.json` 和 `xai-grok-*.json` 凭据保持向下兼容，并在导出时自动转换为标准规范名称。

凭据模式名称：

- `code_assist`：标准 Code Assist 凭据池。
- `provider`：通用供应商后端凭据池。

## 数据存储

单实例部署默认使用挂载数据目录中的 SQLite 存储。在 Docker 部署中，请务必将 `/app/backend/data/creds` 和 `/app/backend/data/logs` 挂载到宿主机的持久化路径（如 `/opt/omni-gateway/creds` 和 `/opt/omni-gateway/logs`）。

可根据运维需求或迁移测试需要，使用 MongoDB 或 PostgreSQL 替代本地 SQLite：

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

亦可添加 Redis 以加速缓存与会话状态管理：

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

配置外部存储并不会使 1.x 运行时具备水平扩展能力。在实现跨进程分布式凭据预留、冷却管理、会话失效和使用量聚合之前，请保持单 Worker 与单副本运行。MongoDB 与 PostgreSQL 仅能二选一，不可同时配置；若外部数据库初始化失败，网关将明确终止启动，而不会静默降级回退到 SQLite。

支持通过环境变量导入凭据。可在控制台操作，或将以下变量之一设置为原始 JSON 字符串，亦可使用带 `_B64` 后缀的 Base64 编码字符串：

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

负载内容可以是单个凭据对象、凭据数组或 `{ "credentials": [...] }` 结构。

## 开发指南

本节面向项目贡献者及本地调试。生产环境部署请使用带有持久化宿主机卷的 Docker 方案。

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

所有代码检查均通过后启动服务：

```bash
python backend/main.py
```

生产运行基线为 Python 3.12，CI 自动化测试覆盖 Python 3.12 和 3.14。有关 Pull Request 提交流程与代码评审标准，请参阅[贡献指南](../../CONTRIBUTING.md)。

## 部署注意事项

- 切勿提交包含凭据的 JSON 文件或 `.env` 文件。
- 为客户端集成配置专用的 `API_KEY`，并为控制台访问设置独立的 `PANEL_PASSWORD`。
- 严格限制对持久化凭据数据卷或外部数据库的访问权限，并在平台层启用静态落盘加密；路由器必须能够解密读取供应商令牌。
- 当服务暴露于非 localhost 环境时，务必将 Omni Gateway 置于配置了 TLS 的反向代理之后。
- 配置反向代理保留 `Host` 请求头并传递 `X-Forwarded-Proto`；在确认全程 HTTPS 终止时设置 `PANEL_COOKIE_SECURE=true`。
- 仅当服务完全仅经由会重写 `X-Forwarded-For` 和 `X-Forwarded-Proto` 的可信代理访问时，才设置 `TRUST_PROXY_HEADERS=true`。
- 使用 `GET /health` 进行进程存活探针检查，使用 `GET /ready` 进行包含存储层感知的就绪探针检查。
- Docker 镜像仅在启动初期以 root 权限修复挂载数据目录的权限归属，随后降权切换至无特权的 `gateway` 用户运行。
- 当浏览器客户端需要跨域访问时，请将 `CORS_ORIGINS` 显式设置为受信任的来源。
- 在升级版本或迁移服务器前，请务必备份 `/opt/omni-gateway` 或自定义的 `DATA_DIR` 目录。
- Docker 镜像发布使用仓库机密 `DOCKERHUB_USERNAME` 与 `DOCKERHUB_TOKEN` 推送至 Docker Hub，并使用内置的 `GITHUB_TOKEN` 推送至 GitHub Packages（`ghcr.io/nguywnben/omni-gateway`）。仅在发布到自定义 Docker Hub 镜像名称时才设置可选的 `IMAGE_NAME` 变量。
- 在 1.x 系列版本中，请保持 `WORKERS=1` 和单应用副本；外部存储无法替代分布式协同机制。
- 请使用标准规范的 `/api/credentials` 管理路由。Beta 阶段的 `/api/creds` 别名已在 1.0.0 中彻底移除。
- 在迁移 Beta 版本部署前，请先查阅[升级至 1.0 指南](../upgrading-to-1.0.md)。
- 升级现有运行实例或回滚版本时，请参考[更新指南](../updating.md)。
- 在打 Tag 或发布镜像前，请对照维护的[发布核对清单](../release-checklist.md)逐项确认。
- 请根据实际用量配额合理制定日志保留与凭据轮转策略。
- 一旦代码仓库或云平台安全扫描告警凭据泄漏，请立即吊销并轮换该凭据。
- Render 部署清单使用的是带有持久化硬盘的付费服务。Render 的免费服务使用临时文件系统，仅适合一次性测试体验。

## 社区与项目健康度

- 在提交 Pull Request 前请阅读[贡献指南](../../CONTRIBUTING.md)。
- 报告安全漏洞请通过[安全政策](../../SECURITY.md)中注明的私密渠道提交。
- 查看[更新日志](../../CHANGELOG.md)了解各版本的详细变更。
- 在参与本项目的所有相关活动中均须遵守[行为准则](../../CODE_OF_CONDUCT.md)。

## 致谢与灵感来源

Omni Gateway 站在开源 AI 路由、可观测性与网关社区的坚实肩膀之上。我们向以下项目的创作者与维护者致以由衷的敬意与感谢：

| 项目 | 项目描述 | Stars |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | 多供应商密钥管理与基于 Web 的 API 聚合架构灵感来源 | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | 面向 AI 编程 CLI 的开创性多协议代理与格式转换层 | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | 行业标杆级的统一 LLM 代理、负载均衡与故障转移路由 | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | 极速 AI 网关架构设计、路由策略及高弹性容灾模式 | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | 开源 LLM 工程化平台、调用追踪、系统可观测性与指标采集 | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## 开源许可证

Omni Gateway 基于 [MIT 开源许可证](../../LICENSE) 发布。
