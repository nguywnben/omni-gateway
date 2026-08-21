<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" />
    Omni Gateway
  </h1>
  <p><b>AI 코딩 도구를 위한 범용 AI 라우터 및 통합 멀티 프로바이더 게이트웨이</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#지원하는-제공자"><b>🌐 지원 제공자</b></a> •
    <a href="#핵심-기능"><b>⚡ 핵심 기능</b></a> •
    <a href="#배포"><b>🐳 Docker 배포</b></a> •
    <a href="#빠른-시작-sdk-연동"><b>🔌 SDK 연동</b></a> •
    <a href="../architecture.md"><b>📖 아키텍처</b></a>
  </p>

  <p>
    <b>콘솔 및 문서 언어:</b><br>
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
</div>

---

코딩 도구를 위한 범용 AI 라우터입니다. Omni Gateway는 스마트 자동 장애 조치(auto-fallback), 토큰 인식 컨텍스트 정리, 사용량 가시성 및 원활한 포맷 변환을 제공하여 로컬 에이전트, IDE 어시스턴트 및 자동화 스크립트가 단일 안정적인 API 인터페이스를 통해 무료 및 유료 LLM 용량을 활용할 수 있도록 합니다.

> **프로젝트 상태:** 안정됨. 버전 `1.3.1`에서는 15개 언어 현지화 콘솔을 완성하고, 로케일 인식 관리 API 메시지 및 릴리스 인식 업데이트 가이드를 추가했으며, `1.0.0`에서 확립된 안정적인 SDK 라우트, 표준 관리 라우트, 설정 이름 및 단일 인스턴스 런타임 계약을 유지합니다.

## Omni Gateway를 선택하는 이유

현대 코딩 워크플로는 OpenAI 호환 도구, Gemini 네이티브 SDK, Anthropic 스타일 에이전트, Google 지원 자격 증명 및 실험적 모델 라우트 등 여러 클라이언트와 제공자를 혼합하여 사용하는 경우가 많습니다. Omni Gateway는 이러한 클라이언트와 모델 백엔드 사이에 위치하여 각 도구가 기본 이해 형식을 그대로 유지하면서 게이트웨이가 라우팅, 재시도, 요청 정리 및 응답 정규화를 처리하도록 합니다.

## 핵심 기능

- 스마트 자동 장애 조치: 요청별로 자격 증명을 예약하고, 동시 트래픽을 분산하며, 공정한 라운드로빈을 위해 모든 시도를 추적하고, 최근 오류, 쿨다운, 요청 속도 제한(rate limits) 및 소진된 용량을 자동으로 우회합니다.
- 토큰 인식 정리: 페이로드를 정규화하고 안전한 턴 경계에서만 과도한 대화 접두사를 잘라내며 시스템 지침, 도구 정의 및 최근 컨텍스트를 온전히 보존합니다.
- 포맷 변환: OpenAI Chat Completions 및 Responses, Gemini 네이티브 요청 및 Anthropic Messages를 수신하고 일반 및 스트리밍 모드 모두에서 포맷 간 양방향 변환을 수행합니다.
- 자격 증명 오케스트레이션: 상태 확인, 쿨다운 추적, 유효성 검사, 중복 제거 및 제공자 인식 장애 조치를 통해 OAuth 계정 및 제공자 API 키를 관리합니다.
- 자격 증명 수준 모델 라우팅: 자격 증명마다 별도의 기능 카탈로그를 유지하여 한 계정의 권한이 선택된 모델을 지원하지 않는 다른 계정으로 요청을 잘못 보내지 않도록 방지합니다.
- 라우트 헬스 메모리: 자격 증명 범위에서 모델 미발견(404) 응답을 기록하고 영향을 받는 라우트를 모델 페이지에서 복구할 수 있도록 표시합니다.
- 스트리밍 복원력: SSE 스트리밍, 스트림 출력이 필수인 클라이언트를 위한 의사 스트리밍(pseudo-streaming), 긴 생성 시 끊김 방지(anti-truncation) 재시도를 지원합니다.
- 제어판: 자격 증명 관리, 로그 확인, 시스템 설정, 사용량 모니터링 및 버전 정보를 확인할 수 있는 웹 콘솔이 포함되어 있습니다.

## 콘솔 미리보기

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## 지원하는 제공자

Omni Gateway는 주요 AI 제공자, 로컬 런타임 및 OAuth 엔드포인트 간에 요청을 원활하게 조정합니다:

| 제공자 | 인증 유형 | 지원 프로토콜 | 자동 장애 조치 | 스트리밍 |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI 호환, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI 호환 | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (로컬 / 자체 호스팅)** | 로컬 / Base URL | OpenAI 호환 | ✅ | ✅ |

## 아키텍처

```text
클라이언트 도구
  OpenAI SDK | Google GenAI SDK | Anthropic SDK | IDE 통합 플러그인
        |
        v
Omni Gateway
  인증 -> 포맷 변환 -> 토큰 인식 정리 -> 라우팅 -> 장애 조치 -> 스트리밍
        |
        v
제공자 어댑터
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

Omni Gateway 백엔드 어댑터가 지속적으로 발전하는 동안에도 외부에 노출되는 공개 API 계약은 변함없이 안정적으로 유지됩니다.

## 저장소 구조

```text
backend/       FastAPI 컴포지션 루트, 라우팅 코어, 프로토콜 변환기, 스토리지 및 테스트
frontend/      관리 콘솔 UI 구조, 스타일, 스크립트 및 제공자 아이콘 에셋
deploy/        컨테이너 정의, 플랫폼 배포 매니페스트 및 OS 시작 스크립트
docs/          아키텍처 설계 문서 및 프로젝트 유지 관리 가이드
.github/       CI 워크플로, 의존성 자동화 및 기여 템플릿
```

모듈 경계, 요청 처리 흐름, 상태 소유권 및 현재 릴리스 제약 조건에 대한 자세한 내용은 [아키텍처](../architecture.md) 문서를 참조하세요.

## 배포

Omni Gateway는 실제 프로덕션 환경을 위해 설계되었습니다. VPS 및 서버 환경에서는 런타임을 격리하면서 호스트에 자격 증명과 로그를 영구 보관할 수 있는 Docker 사용을 권장합니다.

### VPS에서 Docker로 배포

먼저 호스트 서버에 영구 보관용 디렉터리를 생성합니다:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

서비스 컨테이너를 시작합니다:

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

동일한 릴리스가 GitHub Packages(`ghcr.io/nguywnben/omni-gateway:1.3.1`)에도 게시됩니다. `latest` 태그는 최신 안정 릴리스를 추적하고, `edge` 태그는 검증되었으나 아직 릴리스되지 않은 `main` 브랜치 빌드를 추적합니다. 재현 가능한 환경이 필요한 경우 특정 버전 태그나 다이제스트를 고정하세요.

브라우저에서 제어판에 접속합니다:

```text
http://서버_IP_주소:4283
```

최초 실행 시 초기 설정 화면에서 제어판 비밀번호를 생성합니다. 프로젝트에는 기본 비밀번호가 내장되어 있지 않습니다. 원격 브라우저 접속 시에는 `docker logs omni-gateway`에 출력되는 부트스트랩 토큰(bootstrap token)도 입력해야 합니다(localhost 직접 접속 시에는 불필요). 자동화 배포가 필요한 경우 시작 전에 `SETUP_TOKEN` 환경 변수를 미리 설정할 수 있습니다.

시스템이 관리하는 비밀번호는 솔트가 적용된 scrypt 해시로 안전하게 저장되며, 콘솔 세션은 HttpOnly 쿠키를 사용하고, 공개 SDK 요청은 자동 생성된 `sk-ogw-` API 키로 인증됩니다. 비대화형 배포의 경우 `PANEL_PASSWORD`를 미리 구성하여 초기 설정 화면을 건너뛸 수 있습니다.

`1.3.1` 이미지는 `linux/amd64`용으로 빌드 및 게시되었습니다. Vertex 전송 스택을 포함한 모든 제공자 의존성이 동일한 기준에서 빌드 및 테스트될 때까지 ARM64 이미지 게시는 보류됩니다.

서버 방화벽이 활성화되어 있다면 게이트웨이 포트를 허용합니다:

```bash
sudo ufw allow 4283/tcp
```

실시간 로그 확인:

```bash
sudo docker logs -f omni-gateway
```

최신 안정 버전으로 업데이트:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

그런 다음 위의 동일한 `docker run` 명령어로 컨테이너를 다시 시작합니다. 마운트된 `/opt/omni-gateway` 디렉터리는 컨테이너 업데이트 간에 자격 증명, 설정, 사용량 데이터 및 로그를 온전히 보존합니다.

### Docker Compose 배포

소스 코드 저장소 기반 배포의 경우:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

동봉된 Compose 파일은 기본적으로 `nguywnben/omni-gateway:latest`를 가져오고 호스트 데이터 영구 보관을 위해 `/opt/omni-gateway`를 사용합니다. 이 릴리스를 고정하려면 `IMAGE=nguywnben/omni-gateway:1.3.1`을 설정하고, 다른 저장 위치를 사용하는 경우 `DATA_DIR=/사용자_정의_경로`를 지정하세요.

Compose는 셸 환경 변수 또는 루트 `.env` 파일에서 `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, 외부 스토리지 URI 및 `PROXY`를 전달합니다. 자동 키 생성, 최초 설정, 로컬 SQLite 스토리지 및 직접 아웃바운드 연결의 기본 동작을 유지하려면 이 값들을 비워 두세요.

### 로컬 개발

로컬에서 게이트웨이를 개발하거나 디버깅할 때는 Python 네이티브 워크플로를 사용합니다:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Windows PowerShell 환경:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

브라우저에서 제어판을 엽니다:

```text
http://127.0.0.1:4283
```

로컬 개발 환경도 Docker 배포와 동일한 최초 실행 설정 화면을 사용합니다.

## 설정

Omni Gateway는 환경 변수 > 저장된 설정 > 기본값 순서의 우선순위로 설정을 읽어옵니다.

| 환경 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | 바인드 주소. |
| `PORT` | `4283` | HTTP 포트. |
| `HOST_PORT` | `4283` | Docker Compose에서만 사용하는 호스트 포트. |
| `WORKERS` | `1` | 1.x 시리즈에서 지원되는 워커 수. 프로세스 간 자격 증명 예약, 쿨다운, 세션 및 사용량 집계가 구현되기 전까지 다른 값은 거부됩니다. |
| `CORS_ORIGINS` | 비어 있음 | 크로스 오리진 API 호출을 허용할 브라우저 오리진 목록(쉼표 구분). 동일 오리진 콘솔 접속 시 비워 둡니다. |
| `CORS_ORIGIN_REGEX` | 비어 있음 | 동적 브라우저 오리진을 일치시키기 위한 선택적 정규식. |
| `API_KEY` | 자동 생성 | 공개 클라이언트 API 요청용 기본 키. 반드시 `sk-ogw-`로 시작해야 합니다. |
| `PANEL_PASSWORD` | 설정 전까지 비어 있음 | 웹 제어판 접속 비밀번호. |
| `SETUP_TOKEN` | 프로세스별 생성 | 원격 최초 설정을 위한 선택적 고정 부트스트랩 토큰. 생략 시 로그에서 생성된 토큰을 확인합니다. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | 웹 제어판 세션 유효 기간(초). |
| `PANEL_COOKIE_SECURE` | 자동 감지 | `true`로 설정 시 쿠키를 HTTPS로만 전송하도록 강제합니다. 비워 두면 `X-Forwarded-Proto`를 통해 자동 감지합니다. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | 로그인 속도 제한 윈도우(초). |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | 윈도우 내 단일 클라이언트에 허용되는 최대 로그인 실패 횟수. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | 메모리 내 로그인 제한기가 추적하는 최대 클라이언트 주소 수. |
| `MAX_REQUEST_BODY_MB` | `64` | 최대 HTTP 요청 본문 크기(MiB). 초과하는 SDK 요청은 해당 프로토콜의 표준 에러 구조를 반환합니다. |
| `TRUST_PROXY_HEADERS` | `false` | 전달 헤더를 덮어쓰는 신뢰할 수 있는 역방향 프록시 뒤에 있을 때만 활성화합니다. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | 자격 증명 저장 디렉터리. Docker에서는 `/app/backend/data/creds`를 호스트 볼륨에 마운트합니다. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist 백엔드 엔드포인트. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Google Antigravity 백엔드 엔드포인트. |
| `PROXY` | 비어 있음 | 선택적 HTTP, HTTPS 또는 SOCKS 프록시. |
| `RETRY_429_ENABLED` | `true` | 요청 제한 및 일시적 업스트림 오류에 대한 유계 재시도 활성화. 기존 설정 호환성을 위해 이전 이름을 유지합니다. |
| `RETRY_429_MAX_RETRIES` | `5` | 일시적 업스트림 오류에 대한 최대 재시도 횟수. |
| `RETRY_429_INTERVAL` | `1` | 일시적 재시도의 기본 백오프 간격(초). |
| `AUTO_DISABLE` | `false` | 구성된 치명적 오류 발생 시 해당 자격 증명을 자동으로 비활성화. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | 치명적 오류로 간주할 상태 코드 목록(쉼표 구분). |
| `ROUTING_STRATEGY` | `balanced` | 자격 증명 선택 정책: `balanced`(균등) 또는 `priority`(우선순위). |
| `PREFERRED_PROVIDER` | 비어 있음 | `priority` 정책에서 우선 선택할 제공자(예: `google_antigravity`, `google_ai_studio`). |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | 제공자 추론 타임아웃(5~900초). |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | 스트리밍 끊김 방지 기능의 최대 연속 재시도 횟수. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | 제공자로 라우팅하기 전에 과도한 대화 기록을 압축. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | 컨텍스트 압축을 트리거할 예상 입력 토큰 임계값. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | 압축 후 목표 예상 입력 토큰 수. 트리거 임계값보다 낮아야 합니다. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | 압축 시 반드시 보존할 최소 최근 사용자 턴 수. |
| `COMPATIBILITY_MODE` | `false` | 시스템 메시지를 지원하지 않는 클라이언트/모델을 위해 자동 변환. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | 사용 가능한 경우 모델의 추론 과정(reasoning)을 반환. |
| `MONGODB_URI` | 비어 있음 | 설정 시 MongoDB 스토리지 백엔드를 활성화. |
| `POSTGRESQL_URI` | 비어 있음 | 설정 시 PostgreSQL 스토리지 백엔드를 활성화. |
| `REDIS_URL` | 비어 있음 | 설정 시 Redis 캐시 / 세션 상태 가속을 활성화. |
| `CODE_ASSIST_CLIENT_ID` | 내장 데스크톱 | Code Assist OAuth Client ID에 대한 선택적 재정의. |
| `CODE_ASSIST_CLIENT_SECRET` | 내장 데스크톱 | Code Assist OAuth Client Secret에 대한 선택적 재정의. |
| `ANTIGRAVITY_CLIENT_ID` | 내장 데스크톱 | Google Antigravity OAuth Client ID에 대한 선택적 재정의(제공자 페이지에서도 구성 가능). |
| `ANTIGRAVITY_CLIENT_SECRET` | 내장 데스크톱 | Google Antigravity OAuth Client Secret에 대한 선택적 재정의. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Google AI Studio Generative Language API 엔드포인트에 대한 선택적 재정의. |
| `XAI_API_URL` | `https://api.x.ai/v1` | SpaceXAI Console API 키 인증용 엔드포인트에 대한 선택적 재정의(제공자 페이지에서도 구성 가능). |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Grok Build OAuth 구독 엔드포인트에 대한 선택적 재정의. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Grok Build OAuth Issuer에 대한 선택적 재정의. 콘솔은 `x.ai` 도메인의 HTTPS 호스트만 허용합니다. |
| `XAI_CLIENT_ID` | 내장 공개 클라이언트 | Grok Build PKCE OAuth Client ID에 대한 선택적 재정의. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Grok Build OAuth 및 SpaceXAI Console API 요청에 공통 적용할 선택적 HTTP User-Agent 재정의. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | OpenAI Platform API 엔드포인트에 대한 선택적 재정의(제공자 페이지에서도 구성 가능). |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Codex 추론 및 계정 모델 목록 엔드포인트에 대한 선택적 재정의. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Codex 계정 요청 제한 확인 엔드포인트에 대한 선택적 재정의. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Codex 디바이스 인증 서비스에 대한 선택적 재정의. |
| `CODEX_CLIENT_ID` | 내장 공개 클라이언트 | Codex 디바이스 OAuth Client ID에 대한 선택적 재정의. |
| `CODEX_USER_AGENT` | Codex CLI 호환값 | Codex 요청을 위한 선택적 User-Agent 재정의. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Claude Platform 및 Claude Code Messages API 엔드포인트에 대한 선택적 재정의(제공자 페이지에서도 구성 가능). |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Claude Code PKCE 인증 엔드포인트에 대한 선택적 재정의. Anthropic / Claude 공식 호스트만 허용. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Claude Code 토큰 엔드포인트에 대한 선택적 재정의. Anthropic / Claude 공식 호스트만 허용. |
| `CLAUDE_CLIENT_ID` | 내장 공개 클라이언트 | Claude Code PKCE OAuth Client ID에 대한 선택적 재정의. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Claude Code 및 Claude Platform 요청을 위한 선택적 User-Agent 재정의. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Google Antigravity 프로토콜 레벨 요청을 위한 선택적 User-Agent 재정의. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Google Antigravity 페이로드 레벨 userAgent 필드에 대한 선택적 재정의. |
| `LOG_LEVEL` | `info` | 런타임 로그 레벨. |
| `LOG_MAX_MB` | `10` | 로그 파일이 로테이션되기 전 최대 크기(MB). |
| `LOG_BACKUP_COUNT` | `3` | 보관할 로테이션 로그 파일 개수. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | 파일 로그 출력 경로. Docker에서는 `/app/backend/data/logs`를 호스트 볼륨에 마운트합니다. |

## 빠른 시작 SDK 연동

Omni Gateway는 공식 Python SDK의 표준 URL 동작에 맞춰 설계되었습니다. 게이트웨이에는 비표준 중복 경로 접두사가 필요하지 않으므로 아래와 같이 클라이언트를 구성하세요.

아래 예제에서는 가상 모델 `omway`를 사용합니다. 모델 페이지에서 대체 우선순위를 미리 구성하거나 특정 제공자 모델 ID로 교체하세요.

### OpenAI Python SDK

OpenAI의 Base URL로 `/v1`을 설정합니다. SDK가 자동으로 끝에 `/chat/completions`를 추가합니다.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "이 코드 저장소를 한 단락으로 설명해 주세요."}]
)
```

동일한 클라이언트로 OpenAI Responses API를 직접 호출할 수도 있습니다:

```python
response = client.responses.create(
    model="omway",
    instructions="간결하게 답변해 주세요.",
    input="이 코드 저장소를 한 단락으로 설명해 주세요."
)

print(response.output_text)
```

Responses 호환성 계층은 텍스트 입력, 이미지 입력, 비스트리밍 Function Tool 및 SSE 텍스트 스트리밍을 지원합니다. OpenAI 호스팅 내장 도구, 영구 보관 응답 이력 및 스트리밍 함수 호출의 경우 Omni Gateway가 이러한 OpenAI 고유 동작을 실행, 영구 보관 또는 묵시적으로 삭제하지 않으므로 명확하게 에러를 반환하여 거부합니다.

### Anthropic Python SDK

Anthropic의 Base URL로 게이트웨이 오리진을 직접 지정합니다. SDK가 자동으로 끝에 `/v1/messages`를 추가합니다.

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "간결한 커밋 메시지를 작성해 주세요."}]
)
```

### Google GenAI Python SDK

Google GenAI의 Base URL로 게이트웨이 오리진을 직접 지정합니다. SDK가 `/v1beta/models/{model}:generateContent`와 같은 기본 모델 라우트를 자동으로 추가합니다.

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
    contents="간단한 Python 함수를 작성해 주세요.",
    config=types.GenerateContentConfig(
        system_instruction="당신은 유능한 코딩 어시스턴트입니다."
    )
)
```

### 지원 엔드포인트 목록

Omni Gateway는 별도의 제품 네임스페이스 접두사 없이 표준 SDK 호환 라우트를 제공합니다:

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

인증 오류, 요청 검증 오류, 라우팅 오류, 업스트림 오류 및 스트리밍 시작 전 실패는 모두 해당 SDK 인터페이스의 기본 에러 구조로 래핑됩니다. 모든 HTTP 응답에는 `X-Request-ID` 헤더가 포함되며, 클라이언트는 이 헤더에 식별자를 전달하여 요청 흐름을 추적할 수 있습니다. 업스트림에서 속도 제한 또는 일시적 사용 불가를 반환할 경우 게이트웨이는 `Retry-After` 헤더를 그대로 투명하게 보존합니다.

## 모델 기능 및 고급 제어

콘솔의 '모델' 페이지에서는 활성화된 제공자 자격 증명에서 발견된 모델을 집계하여 가상 모델 `omway`를 구성합니다. 각 기본 모델의 우선순위를 한 번만 설정하면 지원되는 모든 SDK에서 `omway`를 사용할 수 있습니다. Omni Gateway는 1순위 모델을 지원하는 정상 자격 증명 간에 부하를 분산하며, 해당 모델을 사용할 수 없게 되면 설정된 순서에 따라 자동으로 대체 시도합니다. 특정 모델을 결정론적으로 지정해야 하는 클라이언트를 위해 제공자 고유의 물리적 모델 ID도 계속 사용할 수 있습니다. 빈 목록을 저장하면 제공자 자격 증명에 영향을 주지 않고 `omway`를 비활성화할 수 있습니다.

모델 발견 메커니즘은 제공자 인식형입니다. 범용 모델은 여러 제공자가 함께 지원할 수 있지만, 전용 모델은 호환 가능한 자격 증명으로만 처리됩니다. 검증된 각 자격 증명은 독립된 자체 제공자 카탈로그를 유지하며, 라우터는 일반적인 제공자 추론보다 자격 증명이 명시적으로 선언한 지원을 우선시합니다. 카탈로그를 새로 고치면 현재 제공자의 실시간 가용성을 다시 확인하며, 사용할 수 없게 된 항목도 복구되거나 수동으로 제거될 때까지 구성 내에 계속 표시됩니다.

특정 물리적 모델에 대해 업스트림이 `404`를 반환하는 경우, Omni Gateway는 제공자 전체를 비활성화하는 대신 해당 자격 증명 및 모델 범위에 사용할 수 없는 라우트를 기록합니다. 해당 라우트는 즉시 일시적으로 우회되며, 지워지거나 자격 증명이 다시 검증될 때까지 **사용할 수 없는 모델 라우트** 목록에 계속 표시됩니다. 이를 통해 단일 계정의 구독 권한이나 지역 제한이 동일한 제공자 아래의 다른 정상 계정에 영향을 미치지 않도록 방지합니다. 활성화된 자격 증명 중 어느 것도 요청된 모델을 선언하거나 추론하지 못하는 경우, 게이트웨이는 일치하지 않는 제공자에게 무작위로 전달하지 않고 명확한 호환 자격 증명 없음 오류를 반환합니다.

Omni Gateway는 모델 이름에 포함된 기능 접두사 및 접미사를 해석합니다:

- `fake-streaming/{model}` 또는 구성된 의사 스트리밍 접두사(SSE 형식을 필수로 요구하는 클라이언트용).
- `streaming-anti-truncation/{model}` 또는 구성된 끊김 방지 접두사(긴 텍스트 스트리밍 생성 시 자동 이어쓰기 복구용).
- 사고 깊이 접미사(`-high`, `-medium`, `-low`, `-minimal`, `-max` 등 지원되는 Gemini 계열 모델용).
- 검색 접지 접미사(`-search` 등 Google Search 접지 지원 모델용).

제공자 어댑터는 업스트림으로 요청을 보내기 전에 이러한 기능 식별자를 자동으로 정규화합니다.

## 사용량 및 비용 투명성

Omni Gateway는 콘솔의 각 기간에 걸쳐 요청 트래픽, 성공률, 자격 증명별 귀속, 제공자가 보고한 토큰 사용량 및 컨텍스트 압축을 통해 절약된 예상 토큰 수를 기록합니다. 토크나이저 및 과금 규칙은 제공자 측에 최종 권한이 있으므로 압축 절약량은 예상치로 표시됩니다. 제공자 가격 기반의 동적 라우팅은 더 많은 제공자가 추가되더라도 핵심 API의 안정성을 유지하기 위해 향후 정책 계층으로 의도적으로 분리되어 있습니다.

## 자격 증명 설정 워크플로

1. Omni Gateway를 시작합니다.
2. VPS에서는 `http://서버_IP:4283`에 접속하거나 로컬 개발 시 `http://127.0.0.1:4283`에 접속합니다.
3. 최초 실행 화면에서 제어판 비밀번호를 생성합니다. 원격 배포 시 앱 로그의 부트스트랩 토큰을 입력하거나 사전에 `PANEL_PASSWORD`를 구성합니다.
4. '제공자' 페이지에서 계정, API 키 또는 Ollama 연결을 추가합니다.
5. 자격 증명 유효성을 검증하고 패널에서 쿨다운 및 오류 상태를 모니터링합니다.
6. 코딩 도구를 위의 지원되는 API 인터페이스 중 하나에 연결합니다.

Google Antigravity 자격 증명을 추가할 때 Google은 로그인 완료 후 브라우저를 `http://localhost:4283/callback`으로 리디렉션합니다. 로컬 머신에서는 Omni Gateway가 OAuth 성공 화면을 직접 표시합니다. VPS의 경우 해당 `localhost`가 사용자의 로컬 브라우저 머신을 가리키므로 페이지가 열리지 않을 수 있습니다. 브라우저 주소 표시줄에서 전체 URL을 복사하여 제공자 페이지로 돌아와 `Callback URL` 상자에 붙여넣고 `자격 증명 저장`을 클릭하세요.

Google AI Studio는 OAuth 대신 API 키 인증을 사용합니다. 제공자 페이지에서 키를 추가하면 Omni Gateway가 Google 모델 카탈로그와 대조하여 유효성을 검증하고 제공자 자격 증명으로 저장한 후 호환되는 Gemini 또는 Gemma 요청을 라우팅합니다. 스마트 라우터는 공유 Gemini 모델에 대해 AI Studio와 Google Antigravity 간에 자동 장애 조치를 수행하며 전용 모델은 호환 자격 증명에서만 처리되도록 보장합니다.

Google AI Studio 일괄 가져오기는 JSON 파일 및 JSON 파일이 포함된 ZIP 압축 파일을 지원합니다. JSON 문서는 단일 키, `api_keys` 배열 또는 키 객체 배열을 포함할 수 있습니다:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

가져온 각 키는 저장 전에 엄격하게 검증됩니다. 동일 배치 내의 중복 키는 건너뛰고, 기존 키는 재검증되어 업데이트되며, 유효하지 않은 항목은 키 평문을 노출하지 않고 개별 보고됩니다.

Grok Build는 PKCE OAuth 자격 증명을 지원하고 SpaceXAI Console은 API 키를 지원합니다. SpaceXAI Console 키는 저장 전에 Grok Build 모델 카탈로그와 대조하여 유효성을 검증합니다. Grok Build OAuth의 경우 Omni Gateway가 인증 링크를 생성합니다. 인증 완료 후 인증 페이지에 표시된 코드를 복사하여 양식에 붙여넣으세요. 리프레시 토큰이 있는 경우 액세스 토큰이 자동으로 갱신되며, 두 자격 증명 유형 모두 현재 카탈로그에서 선언된 Grok Build 모델만 노출합니다. 풀 페이지에서는 Grok Build OAuth 계정의 월간 크레딧 사용량과 xAI에서 제공하는 경우 주간 사용량을 확인할 수 있습니다. 이 계정 수준 청구 뷰는 SpaceXAI Console API 키에서는 지원되지 않습니다.

Codex는 OpenAI 디바이스 인증 플로우를 사용합니다. 제공자 페이지에서 디바이스 코드를 생성하고 표시된 확인 URL을 열어 코드를 입력하고 로그인을 완료한 후 인증 상태를 확인합니다. Omni Gateway는 Codex가 반환한 계정 범위의 모델 카탈로그를 저장하고 필요 시 OAuth 액세스 토큰을 갱신하며 Codex Responses 전송 프로토콜을 통해 호환 요청을 전달합니다. OpenAI Platform은 API 키 인증을 사용하며 키는 계정 모델 카탈로그를 통해 유효성이 검증된 후 풀에 추가됩니다. 두 제품 모두 제공자별 검증 및 중복 제거 기능을 갖춘 JSON 및 ZIP 가져오기를 지원합니다.

Claude Code는 Anthropic의 PKCE OAuth 플로우를 사용합니다. 인증 링크를 생성하고 인증을 완료한 후 반환된 인증 코드를 제공자 페이지에 붙여넣습니다. Claude Platform은 Anthropic API 키를 수락합니다. 두 제품 모두 각 자격 증명별로 지원되는 모델 목록을 검색하고 Anthropic Messages 전송 프로토콜을 사용하며 가능한 경우 Claude Code 액세스 토큰을 자동 갱신하고 검증된 JSON 또는 ZIP 가져오기를 지원합니다.

Ollama 연결은 엔드포인트별로 구성되며 보안 서버 또는 클라우드 서버를 위한 선택적 Bearer API 키를 포함할 수 있습니다. Omni Gateway는 `/api/tags`를 통해 가용 모델을 검색하고 `/api/chat`을 통해 추론 라우팅을 수행합니다. Omni Gateway가 Docker 내에서 실행 중인 경우 `localhost`는 컨테이너 자체를 가리킵니다. 호스트 게이트웨이 주소 또는 네트워크로 접근 가능한 다른 Ollama 엔드포인트를 사용하세요.

풀 전체 가져오기 및 Google Antigravity 일괄 가져오기는 최대 10MB 압축 파일, 최대 500개 파일, 개별 자격 증명 파일 최대 2MB 및 압축 해제 후 최대 25MB의 데이터를 지원합니다. Google AI Studio, OpenAI, Anthropic 및 Ollama 개별 제공자 가져오기에는 파일당 최대 2MB, 최대 200개 JSON 항목, 압축 해제 후 최대 5MB의 더 엄격한 제한이 적용됩니다.

'자격 증명 풀' 페이지는 제공자 독립적인 전체 백업 워크플로도 제공합니다. `ZIP 다운로드`로 활성 상태의 전체 자격 증명 풀을 내보내고, `ZIP 가져오기`를 통해 각 자격 증명 유형(Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform 또는 Ollama)을 자동 인식하여 복원합니다. OAuth 계정은 제공자 범위 내에서 동일성을 유지하여 중복 제거되고, API 키는 제공자 범위의 비가역 해시 핑거프린트를 통해 검증 및 중복 제거됩니다. 지원되지 않거나 형식이 잘못된 항목은 개별적으로 보고되어 압축 파일 내 다른 유효한 자격 증명의 가져오기를 방해하지 않습니다.

Google Antigravity 자격 증명은 `google-antigravity-{account_fingerprint}.json` 형식으로 저장되며 핑거프린트는 평문을 노출하지 않고 정규화된 계정 이메일에서 파생됩니다. Google AI Studio는 `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth는 `grok-{account_fingerprint}.json`, SpaceXAI Console은 `xai-console-{key_fingerprint}.json`, Codex는 `openai-codex-{account_fingerprint}.json`, OpenAI Platform은 `openai-platform-{key_fingerprint}.json`, Claude Code는 `claude-code-{account_fingerprint}.json`, Claude Platform은 `claude-platform-{key_fingerprint}.json`, Ollama 연결은 `ollama-{connection_fingerprint}.json`을 사용합니다. 레거시 `provider_*.json` 및 `xai-grok-*.json` 자격 증명과의 하위 호환성도 유지되며 내보내기 시 표준 이름으로 자동 정규화됩니다.

자격 증명 모드 이름:

- `code_assist`: 표준 Code Assist 자격 증명 풀.
- `provider`: 범용 제공자 백엔드 자격 증명 풀.

## 데이터 스토리지

단일 프로세스 배포는 마운트된 데이터 디렉터리의 SQLite 스토리지를 기본으로 사용합니다. Docker 배포 시에는 `/app/backend/data/creds` 및 `/app/backend/data/logs`를 호스트의 영구 경로(`/opt/omni-gateway/creds`, `/opt/omni-gateway/logs` 등)에 반드시 마운트하세요.

운영 요구 사항이나 마이그레이션 테스트에 따라 로컬 SQLite 대신 MongoDB 또는 PostgreSQL을 사용할 수 있습니다:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

캐시 및 세션 상태 가속을 위해 Redis를 추가할 수도 있습니다:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

외부 스토리지를 구성하더라도 1.x 런타임이 수평 확장이 가능해지는 것은 아닙니다. 프로세스 간 분산 자격 증명 예약, 쿨다운 관리, 세션 무효화 및 사용량 집계가 구현되기 전까지는 단일 워커 및 단일 복제본으로 운영하세요. MongoDB와 PostgreSQL 중 하나만 구성해야 하며 둘 다 구성할 수 없습니다. 외부 데이터베이스 초기화에 실패할 경우 게이트웨이는 SQLite로 자동 대체되지 않고 시작을 명시적으로 중단합니다.

환경 변수를 통한 자격 증명 가져오기도 지원됩니다. 제어판에서 작업하거나 다음 변수 중 하나에 원본 JSON 문자열을 설정하거나 Base64로 인코딩된 `_B64` 접미사 변수를 사용합니다:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

페이로드 내용은 단일 자격 증명 객체, 배열 또는 `{ "credentials": [...] }` 구조일 수 있습니다.

## 개발 가이드

이 섹션은 프로젝트 기여자 및 로컬 디버깅을 위한 것입니다. 프로덕션 배포는 영구 호스트 볼륨이 있는 Docker를 사용하세요.

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

모든 코드 검사가 통과한 후 서비스를 시작합니다:

```bash
python backend/main.py
```

프로덕션 실행 기준은 Python 3.12이며 CI 자동화 테스트는 Python 3.12 및 3.14를 포함합니다. Pull Request 제출 절차 및 코드 리뷰 기준은 [기여 가이드](../../CONTRIBUTING.md)를 참조하세요.

## 배포 시 주의사항

- 자격 증명이 포함된 JSON 파일이나 `.env` 파일은 절대 커밋하지 마세요.
- 클라이언트 연동용 전용 `API_KEY`와 콘솔 접속용 개별 `PANEL_PASSWORD`를 각각 구성하세요.
- 영구 자격 증명 데이터 볼륨이나 외부 데이터베이스에 대한 접근 권한을 엄격히 제한하고 플랫폼 계층에서 저장 시 암호화(encryption at rest)를 활성화하세요. 라우터는 제공자 토큰을 복호화하여 읽을 수 있어야 합니다.
- 서비스를 localhost 외부로 노출할 때는 반드시 TLS가 구성된 역방향 프록시 뒤에 Omni Gateway를 배치하세요.
- 역방향 프록시가 `Host` 요청 헤더를 유지하고 `X-Forwarded-Proto`를 전달하도록 구성하세요. 완전한 HTTPS 종료가 보장된 경우 `PANEL_COOKIE_SECURE=true`를 설정합니다.
- `X-Forwarded-For` 및 `X-Forwarded-Proto`를 덮어쓰는 신뢰할 수 있는 프록시를 통해서만 서비스에 접근할 수 있는 경우에만 `TRUST_PROXY_HEADERS=true`를 설정하세요.
- 프로세스 생존 확인에는 `GET /health`를 사용하고 스토리지 계층을 포함한 준비 상태 확인에는 `GET /ready`를 사용하세요.
- Docker 이미지는 시작 초기에 마운트된 데이터 디렉터리의 소유권을 수정하는 동안에만 root 권한으로 실행되며 이후 권한이 없는 `gateway` 사용자로 전환하여 실행됩니다.
- 브라우저 클라이언트에서 크로스 오리진 접근이 필요한 경우 `CORS_ORIGINS`에 신뢰할 수 있는 오리진을 명시적으로 설정하세요.
- 업그레이드나 서버 이전 전에는 항상 `/opt/omni-gateway` 또는 지정된 `DATA_DIR` 디렉터리를 백업하세요.
- Docker 이미지 게시는 Docker Hub용 저장소 시크릿 `DOCKERHUB_USERNAME` 및 `DOCKERHUB_TOKEN`을 사용하고 GitHub Packages(`ghcr.io/nguywnben/omni-gateway`)용 기본 제공 `GITHUB_TOKEN`을 사용합니다. 사용자 정의 Docker Hub 이미지 이름으로 게시할 때만 선택적 `IMAGE_NAME` 변수를 설정하세요.
- 1.x 시리즈 버전에서는 `WORKERS=1` 및 단일 애플리케이션 복제본을 유지하세요. 외부 스토리지가 분산 조율 메커니즘을 대체할 수는 없습니다.
- 표준 규격의 `/api/credentials` 관리 라우트를 사용하세요. 베타 버전의 `/api/creds` 별칭은 1.0.0에서 완전히 제거되었습니다.
- 베타 배포를 마이그레이션하기 전에 [1.0 업그레이드 가이드](../upgrading-to-1.0.md)를 확인하세요.
- 기존 실행 인스턴스를 업그레이드하거나 롤백할 때는 [업데이트 가이드](../updating.md)를 참조하세요.
- 태그를 지정하거나 이미지를 릴리스하기 전에 관리되는 [릴리스 체크리스트](../release-checklist.md)를 순서대로 확인하세요.
- 실제 사용량 쿼터에 맞춰 로그 보존 및 자격 증명 로테이션 정책을 적절히 수립하세요.
- 코드 저장소나 클라우드 플랫폼 보안 검색에서 자격 증명 유출이 감지되면 즉시 해당 자격 증명을 해지하고 교체하세요.
- Render 배포 매니페스트는 영구 디스크가 포함된 유료 서비스를 사용합니다. Render의 무료 서비스는 휘발성 파일 시스템을 사용하므로 일회성 테스트 용도로만 적합합니다.

## 커뮤니티 및 프로젝트 건전성

- Pull Request를 제출하기 전에 [기여 가이드](../../CONTRIBUTING.md)를 읽어주세요.
- 보안 취약점 보고는 [보안 정책](../../SECURITY.md)에 명시된 비공개 절차를 통해 제출해 주세요.
- 각 릴리스의 세부 변경 사항은 [변경 로그](../../CHANGELOG.md)를 참조하세요.
- 본 프로젝트의 모든 관련 활동에서 [행동 강령](../../CODE_OF_CONDUCT.md)을 준수해야 합니다.

## 감사의 글 & 영감의 원천

Omni Gateway는 오픈 소스 AI 라우팅, 관측 가능성 및 게이트웨이 커뮤니티의 탄탄한 토대 위에 구축되었습니다. 다음 프로젝트의 창립자 및 유지 관리자분들께 깊은 존경과 감사를 표합니다:

| 프로젝트 | 프로젝트 설명 | Stars |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | 멀티 프로바이더 키 관리 및 웹 기반 API 집계 아키텍처의 영감 원천 | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | AI 코딩 CLI를 위한 선구적인 다중 프로토콜 프록시 및 포맷 변환 계층 | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | 업계 표준의 통합 LLM 프록시, 로드 밸런싱 및 장애 조치 라우팅 | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | 초고속 AI 게이트웨이 아키텍처, 라우팅 전략 및 고탄력 장애 대응 모드 | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | 오픈 소스 LLM 엔지니어링 플랫폼, 호출 추적, 시스템 관측 가능성 및 지표 수집 | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## 오픈 소스 라이선스

Omni Gateway는 [MIT 오픈 소스 라이선스](../../LICENSE)에 따라 배포됩니다.
