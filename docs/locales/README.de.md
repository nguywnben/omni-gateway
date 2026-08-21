# Omni Gateway

<p align="center">
  <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
  <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
  <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
  <img src="https://img.shields.io/badge/i18n-15%20Sprachen-orange?style=flat-square" alt="15 Sprachen">
</p>

<p align="center">
  <a href="#unterstutzte-anbieter"><b>🌐 Anbieter</b></a> •
  <a href="#kernfunktionen"><b>⚡ Kernfunktionen</b></a> •
  <a href="#bereitstellung"><b>🐳 Docker-Bereitstellung</b></a> •
  <a href="#sdk-integration"><b>🔌 SDK-Integration</b></a> •
  <a href="../../docs/architecture.md"><b>📖 Architektur</b></a>
</p>

<p align="center">
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

---

Ein universeller KI-Router für Entwickler-Tools. Omni Gateway bietet intelligentes Auto-Failover, tokenbewusste Kontextbereinigung, Nutzungsübersicht und nahtlose Protokollübersetzung für die Nutzung von LLMs über eine einheitliche API-Schnittstelle.

> **Status:** Stabil. Version `1.3.1` bietet eine in 15 Sprachen lokalisierte Web-Konsole.

## <a id="unterstutzte-anbieter"></a>Unterstützte Anbieter

| Anbieter | Authentifizierung | Protokolle | Auto-Failover | Streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API-Schlüssel | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API-Schlüssel | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API-Schlüssel | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API-Schlüssel | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API-Schlüssel | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Lokal / Self-hosted)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## <a id="bereitstellung"></a>Docker-Bereitstellung

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs

sudo docker run -d \
  --name omni-gateway \
  --pull always \
  --restart unless-stopped \
  -p 4283:4283 \
  -v /opt/omni-gateway/creds:/app/backend/data/creds \
  -v /opt/omni-gateway/logs:/app/backend/data/logs \
  nguywnben/omni-gateway:1.3.1
```

Öffnen Sie `http://IHRE_SERVER_IP:4283` im Browser.

## Lizenz

Omni Gateway ist unter der [MIT-Lizenz](../../LICENSE) veröffentlicht.
