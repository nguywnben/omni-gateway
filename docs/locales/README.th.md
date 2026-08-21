# Omni Gateway

<p align="center">
  <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
  <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
  <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
  <img src="https://img.shields.io/badge/i18n-15%20%E0%B8%A0%E0%B8%B2%E0%B8%A9%E0%B8%B2-orange?style=flat-square" alt="15 ภาษา">
</p>

<p align="center">
  <a href="#phu-hai-borikan-thi-rong-rap"><b>🌐 ผู้ให้บริการที่รองรับ</b></a> •
  <a href="#khwam-samart-lak"><b>⚡ ความสามารถหลัก</b></a> •
  <a href="#kan-tidthang"><b>🐳 การติดตั้ง Docker</b></a> •
  <a href="#kan-chueam-tor-sdk"><b>🔌 การเชื่อมต่อ SDK</b></a> •
  <a href="../../docs/architecture.md"><b>📖 สถาปัตยกรรม</b></a>
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
  <a href="README.de.md">Deutsch</a> •
  <a href="README.it.md">Italiano</a> •
  <a href="README.pt.md">Português</a> •
  <a href="README.ru.md">Русский</a> •
  <a href="README.id.md">Indonesia</a> •
  <b>ภาษาไทย</b> •
  <a href="README.tr.md">Türkçe</a>
</p>

---

เราเตอร์ AI อเนกประสงค์สำหรับเครื่องมือเขียนโค้ด Omni Gateway มอบระบบสลับข้อมูลสำรองอัตโนมัติอัจฉริยะ (auto-fallback), การตัดแต่งบริบทตามโทเค็น, การแสดงผลการใช้งาน และการแปลงโปรโตคอลอย่างไร้รอยต่อ

> **สถานะ:** เสถียร เวอร์ชัน `1.3.1` รองรับคอนโซลการจัดการ 15 ภาษา

## <a id="phu-hai-borikan-thi-rong-rap"></a>ผู้ให้บริการที่รองรับ

| ผู้ให้บริการ | การยืนยันตัวตน | โปรโตคอลที่รองรับ | สลับสำรองอัตโนมัติ | สตรีมมิ่ง |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (โฮสต์เอง)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## <a id="kan-tidthang"></a>การติดตั้งด้วย Docker

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

เปิด `http://YOUR_SERVER_IP:4283` ในเบราว์เซอร์ของคุณ

## ใบอนุญาต

Omni Gateway เผยแพร่ภายใต้ [ใบอนุญาต MIT](../../LICENSE)
