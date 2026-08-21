# Omni Gateway

<p align="center">
  <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
  <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
  <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
  <img src="https://img.shields.io/badge/i18n-15%EA%B0%9C%20%EC%96%B8%EC%96%B4-orange?style=flat-square" alt="15개 언어">
</p>

<p align="center">
  <a href="#지원-제공자"><b>🌐 지원 제공자</b></a> •
  <a href="#핵심-기능"><b>⚡ 핵심 기능</b></a> •
  <a href="#배포"><b>🐳 Docker 배포</b></a> •
  <a href="#sdk-연동"><b>🔌 SDK 연동</b></a> •
  <a href="../../docs/architecture.md"><b>📖 아키텍처</b></a>
</p>

<p align="center">
  <a href="../../README.md">English</a> •
  <a href="README.vi.md">Tiếng Việt</a> •
  <a href="README.zh-CN.md">中文(简体)</a> •
  <a href="README.zh-TW.md">中文(繁體)</a> •
  <a href="README.ja.md">日本語</a> •
  <b>한국어</b> •
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

코딩 도구를 위한 유니버설 AI 라우터. Omni Gateway는 스마트 자동 장애 조치(Failover), 토큰 인식 컨텍스트 정리, 사용량 가시화 및 원활한 프로토콜 변환을 제공하여 로컬 에이전트, IDE 어시스턴트, 자동화 스크립트가 단일 안정 API 엔드포인트를 통해 다양한 무료 및 유료 LLM 용량을 활용할 수 있도록 지원합니다.

> **프로젝트 상태:** 안정 버전. `1.3.1` 버전은 15개 언어로 완벽히 현지화된 관리 콘솔과 릴리스 인식 업데이트 안내를 제공합니다.

## 핵심 기능

- **스마트 자동 장애 조치 (Auto-fallback):** 요청별로 자격 증명을 예약하고, 동시 트래픽을 분산하며, 오류 발생 시 자동으로 우회합니다.
- **토큰 인식 컨텍스트 정리:** 안전한 대화 턴 경계에서만 긴 기록을 정리하며 시스템 지침과 최근 컨텍스트를 완벽하게 보존합니다.
- **다방향 프로토콜 변환:** OpenAI Chat Completions & Responses, Gemini Native, Anthropic Messages 간의 상호 변환 및 스트리밍을 지원합니다.
- **자격 증명 풀 오케스트레이션:** OAuth 계정과 API 키를 통합 관리하며 상태 추적, 중복 제거 및 장애 복구를 수행합니다.
- **웹 관리 콘솔:** 자격 증명 관리, 실시간 로그 모니터링, 토큰 분석 등을 지원하는 직관적인 대시보드 내장.

## <a id="지원-제공자"></a>지원 제공자

| 제공자 | 인증 방식 | 지원 프로토콜 | 자동 장애 조치 | 스트리밍 |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (로컬/자체 호스팅)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## <a id="배포"></a>배포

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

브라우저에서 `http://YOUR_SERVER_IP:4283`으로 접속하여 초기 비밀번호를 설정하세요.

## 라이선스

Omni Gateway는 [MIT 라이선스](../../LICENSE)에 따라 배포됩니다.
