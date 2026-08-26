<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Universal AI Router & เกตเวย์รวมศูนย์หลายผู้ให้บริการสำหรับเครื่องมือ AI Coding</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20%E0%B8%A0%E0%B8%B2%E0%B8%A9%E0%B8%B2-orange?style=flat-square" alt="15 ภาษา">
  </p>

  <p>
    <a href="#phu-hai-borikan-thi-rong-rap"><b>🌐 ผู้ให้บริการที่รองรับ</b></a> •
    <a href="#khwam-samart-lak"><b>⚡ ความสามารถหลัก</b></a> •
    <a href="#kan-tidthang"><b>🐳 การติดตั้ง Docker</b></a> •
    <a href="#kan-chueam-tor-sdk"><b>🔌 การตั้งค่า SDK</b></a> •
    <a href="../architecture.md"><b>📖 สถาปัตยกรรม</b></a>
  </p>

  <p>
    <b>ภาษาคอนโซลและเอกสาร:</b><br>
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
</div>

---

เราเตอร์ AI อเนกประสงค์สำหรับเครื่องมือเขียนโค้ด Omni Gateway มอบระบบสลับข้อมูลสำรองอัตโนมัติอัจฉริยะ (smart auto-fallback), การทำความสะอาดคำขอที่คำนึงถึงโทเค็น, การแสดงผลการใช้งานที่โปร่งใส และการแปลงรูปแบบคำขออย่างไร้รอยต่อ เพื่อให้เอเจนต์ในเครื่อง, ส่วนขยาย IDE และสคริปต์อัตโนมัติสามารถใช้ขีดความสามารถของ LLM ทั้งแบบฟรีและพรีเมียมผ่านอินเทอร์เฟซ API ที่เสถียรเพียงหนึ่งเดียว

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## ทำไมต้อง Omni Gateway

เวิร์กโฟลว์การเขียนโค้ดยุคใหม่มักผสมผสานไคลเอนต์และผู้ให้บริการที่หลากหลาย: เครื่องมือที่เข้ากันได้กับ OpenAI, SDK ดั้งเดิมของ Gemini, เอเจนต์สไตล์ Anthropic, ข้อมูลรับรองที่รองรับโดย Google และเส้นทางโมเดลทดลอง Omni Gateway ทำหน้าที่เป็นตัวกลางระหว่างไคลเอนต์เหล่านั้นกับโมเดลแบ็กเอนด์ เพื่อให้แต่ละเครื่องมือสามารถสื่อสารในรูปแบบที่เข้าใจอยู่แล้วได้ต่อไป ในขณะที่เกตเวย์จะจัดการเรื่องการกำหนดเส้นทาง, การลองใหม่ (retry), การทำความสะอาดคำขอ และการปรับการตอบกลับให้เป็นมาตรฐาน

## <a id="khwam-samart-lak"></a>ความสามารถหลัก

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## ตัวอย่างคอนโซล

![พูลข้อมูลรับรอง Omni Gateway](../assets/screenshots/credential-pool.png)

## <a id="phu-hai-borikan-thi-rong-rap"></a>ผู้ให้บริการที่รองรับ

Omni Gateway ปรับคำขออย่างไร้รอยต่อระหว่างผู้ให้บริการ AI ชั้นนำ, รันไทม์ในเครื่อง และจุดปลายทาง OAuth:

| ผู้ให้บริการ | ประเภทการยืนยันตัวตน | โปรโตคอลที่รองรับ | ระบบสลับสำรองอัตโนมัติ | การสตรีม |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | รองรับ OpenAI, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | รองรับ OpenAI | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (ในเครื่อง / โฮสต์เอง)** | ภายในเครื่อง / Base URL | รองรับ OpenAI | ✅ | ✅ |

## สถาปัตยกรรม

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | การเชื่อมต่อ IDE
        |
        v
Omni Gateway
  การยืนยันตัวตน -> การแปลงรูปแบบ -> การทำความสะอาดตามโทเค็น -> การกำหนดเส้นทาง -> ระบบสำรอง -> การสตรีม
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

API สาธารณะยังคงเสถียรในขณะที่อะแดปเตอร์เฉพาะของผู้ให้บริการพัฒนาอยู่เบื้องหลัง Omni Gateway

## โครงสร้างที่เก็บข้อมูล (Repository)

```text
backend/       รูทการประกอบ FastAPI, แกนหลักการกำหนดเส้นทาง, ตัวแปลง, ที่จัดเก็บข้อมูล และการทดสอบ
frontend/      มาร์กอัปคอนโซลการจัดการ, สไตล์, สคริปต์ และแอสเซทของผู้ให้บริการ
deploy/        คำจำกัดความของคอนเทนเนอร์, แมนิเฟสต์แพลตฟอร์ม และสคริปต์ระบบปฏิบัติการ
docs/          บันทึกสถาปัตยกรรมและแอสเซทโครงการที่ได้รับการดูแล
.github/       CI, ระบบอัตโนมัติของการพึ่งพา และเทมเพลตการมีส่วนร่วม
```

ดู [สถาปัตยกรรม](../architecture.md) สำหรับขอบเขตโมดูล, โฟลว์ของคำขอ, ความเป็นเจ้าของสถานะ และข้อจำกัดของรุ่นปัจจุบัน

## <a id="kan-tidthang"></a>การติดตั้ง

Omni Gateway ออกแบบมาสำหรับการติดตั้งใช้งานจริง Docker เป็นแนวทางที่แนะนำสำหรับสภาพแวดล้อม VPS และเซิร์ฟเวอร์เนื่องจากช่วยแยกรันไทม์ในขณะที่ยังคงรักษาข้อมูลรับรองและบันทึกไว้บนโฮสต์

### Docker บน VPS

สร้างไดเรกทอรีโฮสต์แบบถาวรก่อน:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

เริ่มบริการ:

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

รุ่นเดียวกันนี้เผยแพร่ไปยัง GitHub Packages ในชื่อ `ghcr.io/nguywnben/omni-gateway:1.4.0` แท็ก `latest` จะติดตามรุ่นเสถียรใหม่ล่าสุด ส่วน `edge` จะติดตามบิลด์ที่ตรวจสอบแล้วแต่ยังไม่เผยแพร่จาก `main` ตรึงแท็กเวอร์ชันหรือไดเจสต์เมื่อต้องการการติดตั้งที่สามารถทำซ้ำได้อย่างแน่นอน

เปิดแผงควบคุมที่:

```text
http://YOUR_SERVER_IP:4283
```

ในการรันครั้งแรก ให้สร้างรหัสผ่านคอนโซลบนหน้าจอตั้งค่า ไม่มีการกำหนดรหัสผ่านเริ่มต้นมาจากโรงงาน เบราว์เซอร์ระยะไกลต้องป้อนโทเค็นบูตสแตรปที่พิมพ์โดย `docker logs omni-gateway` ด้วย การตั้งค่าบน localhost โดยตรงไม่จำเป็นต้องใช้ กำหนดค่า `SETUP_TOKEN` ก่อนเริ่มต้นเมื่อระบบอัตโนมัติในการติดตั้งต้องการโทเค็นบูตสแตรปที่คงที่

รหัสผ่านที่จัดการโดยแอปพลิเคชันจะถูกจัดเก็บเป็นแฮช scrypt แบบใส่เกลือ (salted), เซสชันแผงควบคุมใช้คุกกี้ HttpOnly และคำขอ SDK สาธารณะจะยืนยันตัวตนด้วยคีย์ API `sk-ogw-` ที่สร้างขึ้น สำหรับการติดตั้งแบบไม่ต้องโต้ตอบ ให้กำหนดค่า `PANEL_PASSWORD` ล่วงหน้าและข้ามหน้าจอตั้งค่าไปได้เลย

คอนเทนเนอร์ `1.4.0` เผยแพร่สำหรับ `linux/amd64` การเผยแพร่ ARM64 ถูกหยุดชั่วคราวโดยเจตนาจนกว่าการพึ่งพาของผู้ให้บริการทุกราย รวมถึงสแต็กการขนส่ง Vertex จะสามารถสร้างและทดสอบภายใต้ข้อตกลงเดียวกันได้

หากไฟร์วอลล์ของเซิร์ฟเวอร์เปิดใช้งานอยู่ ให้อนุญาตพอร์ตเกตเวย์:

```bash
sudo ufw allow 4283/tcp
```

ดูบันทึกการทำงาน:

```bash
sudo docker logs -f omni-gateway
```

อัปเดตเป็นอิมเมจเสถียรล่าสุด:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

จากนั้นเริ่มคอนเทนเนอร์อีกครั้งด้วยคำสั่ง `docker run` เดียวกันข้างต้น ไดเรกทอรี `/opt/omni-gateway` ที่เมานต์ไว้จะรักษาข้อมูลรับรอง, การกำหนดค่า, ข้อมูลการใช้งาน และบันทึกไว้ตลอดการอัปเดตคอนเทนเนอร์

### Docker Compose

สำหรับการติดตั้งตามที่เก็บข้อมูล:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

ไฟล์ compose ที่ให้มาจะดึง `nguywnben/omni-gateway:latest` และใช้ `/opt/omni-gateway` เป็นค่าเริ่มต้นสำหรับข้อมูลโฮสต์แบบถาวร กำหนด `IMAGE=nguywnben/omni-gateway:1.4.0` เพื่อตรึงรุ่นนี้ และกำหนด `DATA_DIR=/custom/path` เมื่อเซิร์ฟเวอร์ใช้ตำแหน่งที่จัดเก็บอื่น

Compose จะส่งต่อ `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, URI การจัดเก็บข้อมูลภายนอก และ `PROXY` จากเชลล์หรือไฟล์ `.env` ที่รูท เว้นว่างไว้เพื่อคงการสร้างคีย์อัตโนมัติ, การตั้งค่าการรันครั้งแรก, ที่จัดเก็บ SQLite ในเครื่อง และเครือข่ายขาออกโดยตรง


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.


### การพัฒนาในเครื่อง (Local Development)

ใช้เวิร์กโฟลว์ Python เมื่อพัฒนาหรือแก้จุดบกพร่องเกตเวย์ในเครื่อง:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

บน Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

เปิดแผงควบคุมที่:

```text
http://127.0.0.1:4283
```

การพัฒนาในเครื่องใช้หน้าจอตั้งค่าการรันครั้งแรกแบบเดียวกับการติดตั้ง Docker

## การกำหนดค่า

Omni Gateway อ่านการกำหนดค่าจากตัวแปรสภาพแวดล้อมก่อน จากนั้นตามด้วยการกำหนดค่าที่บันทึกไว้ และค่าเริ่มต้นตามลำดับ

| ตัวแปร | ค่าเริ่มต้น | วัตถุประสงค์ |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | ที่อยู่ผูก (bind address) |
| `PORT` | `4283` | พอร์ต HTTP |
| `HOST_PORT` | `4283` | พอร์ตฝั่งโฮสต์ที่ใช้โดย Docker Compose เท่านั้น |
| `WORKERS` | `1` | จำนวน worker ที่รองรับสำหรับ 1.x ค่าอื่นจะถูกปฏิเสธจนกว่าการจอง, คูลดาวน์, เซสชัน และการรวบรวมการใช้งานจะได้รับการประสานงานข้ามกระบวนการ |
| `CORS_ORIGINS` | ว่าง | ต้นทางเบราว์เซอร์ที่คั่นด้วยเครื่องหมายจุลภาคที่อนุญาตให้เรียกใช้ API ข้ามต้นทาง เว้นว่างไว้สำหรับการใช้งานคอนโซลต้นทางเดียวกัน |
| `CORS_ORIGIN_REGEX` | ว่าง | Regex ทางเลือกสำหรับต้นทางเบราว์เซอร์แบบไดนามิกที่ได้รับการจัดการ |
| `API_KEY` | สร้างอัตโนมัติ | คีย์ที่ต้องการสำหรับคำขอ API ไคลเอนต์สาธารณะ ต้องขึ้นต้นด้วย `sk-ogw-` |
| `PANEL_PASSWORD` | ว่างจนกว่าจะตั้งค่า | รหัสผ่านสำหรับแผงควบคุมบนเว็บ |
| `SETUP_TOKEN` | สร้างตามกระบวนการ | โทเค็นบูตสแตรปคงที่ทางเลือกที่จำเป็นสำหรับการตั้งค่าระยะไกลครั้งแรก เมื่อละเว้น ให้อ่านโทเค็นที่สร้างขึ้นจากบันทึกของแอปพลิเคชันหรือคอนเทนเนอร์ |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | อายุการใช้งานเซสชันคอนโซลเว็บบนหน่วยวินาที |
| `PANEL_COOKIE_SECURE` | อัตโนมัติ | ตั้งค่า `true` เพื่อกำหนดให้คุกกี้พาเนลใช้เฉพาะ HTTPS เท่านั้น เว้นว่างไว้เพื่อตรวจหา HTTPS ผ่าน `X-Forwarded-Proto` โดยอัตโนมัติ |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | หน้าต่างจำกัดอัตราการเข้าสู่ระบบในหน่วยวินาที |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | ความพยายามเข้าสู่ระบบที่ล้มเหลวสูงสุดที่อนุญาตต่อไคลเอนต์ภายในหน้าต่างจำกัดอัตรา |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | ที่อยู่ไคลเอนต์สูงสุดที่เก็บไว้โดยตัวจำกัดการเข้าสู่ระบบในหน่วยความจำ |
| `MAX_REQUEST_BODY_MB` | `64` | ขนาดเนื้อหาคำขอ HTTP สูงสุดในหน่วย MiB คำขอ SDK ที่มีขนาดเกินขีดจำกัดจะส่งกลับข้อผิดพลาดตามโครงสร้างดั้งเดิมของโปรโตคอล |
| `TRUST_PROXY_HEADERS` | `false` | ยอมรับส่วนหัวการส่งต่อไคลเอนต์/โปรโตคอลจาก reverse proxy ที่เชื่อถือได้ซึ่งเขียนทับส่วนหัวเหล่านั้นเท่านั้น |
| `CREDENTIALS_DIR` | `./backend/data/creds` | ไดเรกทอรีจัดเก็บข้อมูลรับรอง ใน Docker ให้คงอยู่ `/app/backend/data/creds` ด้วยวอลุ่มโฮสต์ |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | ปลายทางแบ็กเอนด์ของ Code Assist |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | ปลายทางแบ็กเอนด์ของ Google Antigravity |
| `PROXY` | ว่าง | พร็อกซี HTTP, HTTPS หรือ SOCKS ทางเลือก |
| `RETRY_429_ENABLED` | `true` | เปิดใช้งานการลองใหม่แบบมีขอบเขตสำหรับการจำกัดอัตราและความล้มเหลวชั่วคราวของอัปสตรีม ชื่อเดิมยังคงอยู่เพื่อความเข้ากันได้ของการกำหนดค่า |
| `RETRY_429_MAX_RETRIES` | `5` | ความพยายามลองใหม่สูงสุดสำหรับความล้มเหลวชั่วคราวของอัปสตรีม |
| `RETRY_429_INTERVAL` | `1` | ความล่าช้าพื้นฐานระหว่างการลองใหม่ชั่วคราวในหน่วยวินาที |
| `AUTO_DISABLE` | `false` | ปิดใช้งานข้อมูลรับรองหลังจากความล้มเหลวร้ายแรง (hard failures) ที่กำหนดค่าไว้ |
| `AUTO_DISABLE_ERROR_CODES` | `403` | รหัสสถานะความล้มเหลวร้ายแรงที่คั่นด้วยเครื่องหมายจุลภาค |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | ว่าง | ผู้ให้บริการที่ต้องการโดยกลยุทธ์ `priority` เช่น `google_antigravity` หรือ `google_ai_studio` |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | ระยะเวลาหมดเวลาการอนุมานของผู้ให้บริการ ซึ่งถูกจำกัดระหว่าง 5 ถึง 900 วินาที |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | ความพยายามดำเนินการต่อสูงสุดสำหรับการสตรีมแบบป้องกันการตัดทอน |
| `TOKEN_COMPRESSION_ENABLED` | `true` | บีบอัดประวัติการสนทนาที่มีขนาดใหญ่เกินไปก่อนการกำหนดเส้นทางไปยังผู้ให้บริการ |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | เกณฑ์โทเค็นอินพุตโดยประมาณที่เปิดใช้งานการบีบอัด |
| `TOKEN_COMPRESSION_TARGET` | `24000` | เป้าหมายโทเค็นอินพุตโดยประมาณหลังจากการบีบอัด ต้องต่ำกว่าเกณฑ์เปิดใช้งาน |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | จำนวนรอบการสนทนาล่าสุดขั้นต่ำของผู้ใช้ที่คงไว้ระหว่างการบีบอัด |
| `COMPATIBILITY_MODE` | `false` | แปลงข้อความระบบสำหรับไคลเอนต์/โมเดลที่ไม่รองรับ |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | รวมฟิลด์การใช้เหตุผล (reasoning) ของโมเดลเมื่อมีให้ใช้งาน |
| `MONGODB_URI` | ว่าง | เปิดใช้งานที่จัดเก็บข้อมูล MongoDB เมื่อตั้งค่า |
| `POSTGRESQL_URI` | ว่าง | เปิดใช้งานที่จัดเก็บข้อมูล PostgreSQL เมื่อตั้งค่า |
| `REDIS_URL` | ว่าง | เปิดใช้งานแคช/สถานะเซสชันที่สำรองด้วย Redis เมื่อตั้งค่า |
| `CODE_ASSIST_CLIENT_ID` | ไคลเอนต์เดสก์ท็อปในตัว | การแทนที่ทางเลือกสำหรับ Client ID OAuth ของ Code Assist |
| `CODE_ASSIST_CLIENT_SECRET` | ไคลเอนต์เดสก์ท็อปในตัว | การแทนที่ทางเลือกสำหรับ Client Secret OAuth ของ Code Assist |
| `ANTIGRAVITY_CLIENT_ID` | ไคลเอนต์เดสก์ท็อปในตัว | การแทนที่ทางเลือกสำหรับ Client ID OAuth ของ Google Antigravity สามารถจัดการได้จากหน้า Providers |
| `ANTIGRAVITY_CLIENT_SECRET` | ไคลเอนต์เดสก์ท็อปในตัว | การแทนที่ทางเลือกสำหรับ Client Secret OAuth ของ Google Antigravity กำหนดค่าผ่าน env หรือหน้า Providers เมื่อไคลเอนต์อัปสตรีมเปลี่ยน |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | การแทนที่ทางเลือกสำหรับปลายทาง Google AI Studio Generative Language API |
| `XAI_API_URL` | `https://api.x.ai/v1` | การแทนที่ทางเลือกสำหรับปลายทาง API ของ SpaceXAI Console สำหรับข้อมูลรับรองคีย์ API สามารถจัดการได้จากหน้า Providers |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | การแทนที่ทางเลือกสำหรับปลายทางการสมัครสมาชิก OAuth ของ Grok Build |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | การแทนที่ทางเลือกสำหรับผู้ออก OAuth ของ Grok Build คอนโซลยอมรับเฉพาะโฮสต์ HTTPS ภายใต้ `x.ai` เท่านั้น |
| `XAI_CLIENT_ID` | ไคลเอนต์สาธารณะในตัว | การแทนที่ทางเลือกสำหรับ Client ID OAuth PKCE ของ Grok Build |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | การแทนที่ทางเลือกสำหรับ HTTP User-Agent ที่ใช้ร่วมกันสำหรับคำขอ Grok Build OAuth และ SpaceXAI Console API |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | การแทนที่ทางเลือกสำหรับปลายทาง OpenAI Platform API สามารถจัดการได้จากหน้า Providers |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | การแทนที่ทางเลือกสำหรับปลายทางการอนุมานและโมเดลบัญชีของ Codex |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | การแทนที่ทางเลือกสำหรับปลายทางการจำกัดอัตราของบัญชี Codex |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | การแทนที่ทางเลือกสำหรับบริการอนุมัติอุปกรณ์ของ Codex |
| `CODEX_CLIENT_ID` | ไคลเอนต์สาธารณะในตัว | การแทนที่ทางเลือกสำหรับ Client ID OAuth อุปกรณ์ของ Codex |
| `CODEX_USER_AGENT` | ค่าที่เข้ากันได้กับ Codex CLI | การแทนที่ทางเลือกสำหรับ User-Agent สำหรับคำขอ Codex |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | การแทนที่ทางเลือกสำหรับปลายทาง Claude Platform และ Claude Code Messages API สามารถจัดการได้จากหน้า Providers |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | การแทนที่ทางเลือกสำหรับปลายทางการอนุญาต PKCE ของ Claude Code คอนโซลยอมรับเฉพาะโฮสต์ Anthropic และ Claude |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | การแทนที่ทางเลือกสำหรับปลายทางโทเค็นของ Claude Code คอนโซลยอมรับเฉพาะโฮสต์ Anthropic และ Claude |
| `CLAUDE_CLIENT_ID` | ไคลเอนต์สาธารณะในตัว | การแทนที่ทางเลือกสำหรับ Client ID OAuth PKCE ของ Claude Code |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | การแทนที่ทางเลือกสำหรับ User-Agent สำหรับคำขอ Claude Code และ Claude Platform |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | การแทนที่ทางเลือกสำหรับโปรโตคอล User-Agent ของ Google Antigravity |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | การแทนที่ทางเลือกสำหรับ userAgent ระดับเพย์โหลดของ Google Antigravity |
| `METRICS_TOKEN` | empty | At least 32 bytes; required with opt-in `PROMETHEUS_EXPORT_ENABLED=true`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | ระดับบันทึกการทำงานของรันไทม์ |
| `LOG_MAX_MB` | `10` | ขนาดไฟล์บันทึกที่ใช้งานสูงสุดก่อนการหมุนเวียน (rotation) |
| `LOG_BACKUP_COUNT` | `3` | จำนวนไฟล์บันทึกที่หมุนเวียนที่คงไว้ |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | ปลายทางไฟล์บันทึก ใน Docker ให้คงอยู่ `/app/backend/data/logs` ด้วยวอลุ่มโฮสต์ |

## <a id="kan-chueam-tor-sdk"></a>พื้นผิว SDK

Omni Gateway ได้รับการออกแบบตามพฤติกรรม URL มาตรฐานของ Python SDK อย่างเป็นทางการ กำหนดค่าแต่ละไคลเอนต์ให้ตรงตามที่แสดงด้านล่าง เกตเวย์ไม่ต้องการคำนำหน้าเส้นทางที่ซ้ำซ้อนซึ่งไม่ได้มาตรฐาน

ตัวอย่างใช้โมเดลเสมือน `omway` กำหนดค่าลำดับการสำรองข้อมูลผู้ให้บริการ-โมเดลในหน้า Models ก่อน หรือแทนที่ด้วย ID โมเดลที่เป็นรูปธรรม

### OpenAI Python SDK

ใช้ `/v1` เป็น base URL ของ OpenAI โดย SDK จะต่อท้าย `/chat/completions` โดยอัตโนมัติ

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "อธิบายที่เก็บข้อมูลนี้ในหนึ่งย่อหน้า"}],
)
```

ไคลเอนต์เดียวกันสามารถใช้ OpenAI Responses API ได้:

```python
response = client.responses.create(
    model="omway",
    instructions="ตอบอย่างกระชับ",
    input="อธิบายที่เก็บข้อมูลนี้ในหนึ่งย่อหน้า",
)

print(response.output_text)
```

ความเข้ากันได้ของ Responses รองรับข้อความ, อินพุตรูปภาพ, non-streaming function tools และการสตรีมข้อความ SSE เครื่องมือในตัวที่โฮสต์โดย OpenAI, ประวัติการตอบกลับที่จัดเก็บไว้ และการเรียกฟังก์ชันแบบสตรีมมิ่งจะถูกปฏิเสธอย่างชัดเจนเนื่องจาก Omni Gateway ไม่ได้เรียกใช้, จัดเก็บ หรือละทิ้งพฤติกรรมเฉพาะของ OpenAI เหล่านั้นอย่างเงียบๆ

### Anthropic Python SDK

ใช้ต้นทางของเกตเวย์เป็น base URL ของ Anthropic โดย SDK จะต่อท้าย `/v1/messages` โดยอัตโนมัติ

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "ร่างข้อความคอมมิตสั้นๆ"}],
)
```

### Google GenAI Python SDK

ใช้ต้นทางของเกตเวย์เป็น base URL ของ Google GenAI โดย SDK จะต่อท้ายเส้นทางโมเดลเริ่มต้น เช่น `/v1beta/models/{model}:generateContent`

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
    contents="เขียนฟังก์ชัน Python สั้นๆ หนึ่งฟังก์ชัน",
    config=types.GenerateContentConfig(
        system_instruction="คุณเป็นผู้ช่วยที่เป็นประโยชน์",
    ),
)
```

### เส้นทางที่รองรับ

Omni Gateway เปิดเผยเส้นทางที่เข้ากันได้กับ SDK โดยไม่ต้องมีเนมสเปซของผลิตภัณฑ์:

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

ความล้มเหลวในการยืนยันตัวตน, การตรวจสอบความถูกต้องของคำขอ, การกำหนดเส้นทาง, อัปสตรีม และข้อผิดพลาดก่อนการสตรีมจะใช้โครงสร้างข้อผิดพลาดดั้งเดิมสำหรับพื้นผิว SDK ที่เลือก ทุกการตอบกลับ HTTP จะรวมส่วนหัว `X-Request-ID` ไคลเอนต์สามารถระบุตัวระบุที่ปลอดภัยในส่วนหัวนั้นเพื่อการเชื่อมโยงแบบครบวงจร (end-to-end) การตอบกลับที่จำกัดอัตราและไม่พร้อมใช้งานชั่วคราวจะคงส่วนหัว `Retry-After` ไว้เมื่ออัปสตรีมระบุให้

## คุณสมบัติโมเดล

หน้า Models จะสร้างโมเดลเสมือน `omway` จากโมเดลที่ค้นพบในข้อมูลรับรองของผู้ให้บริการที่เปิดใช้งาน จัดเรียงสมาชิกตามลำดับความสำคัญเพียงครั้งเดียว จากนั้นใช้ `omway` จาก SDK ที่รองรับ Omni Gateway จะปรับสมดุลข้อมูลรับรองที่สมบูรณ์ซึ่งรองรับโมเดลแรก และดำเนินการต่อไปตามลำดับโมเดลที่กำหนดค่าไว้เมื่อโมเดลนั้นไม่พร้อมใช้งาน ID โมเดลของผู้ให้บริการที่เป็นรูปธรรมยังคงมีให้ใช้งานสำหรับไคลเอนต์ที่ต้องการการเลือกโมเดลแบบกำหนดแน่นอน การบันทึกการเลือกที่ว่างเปล่าจะปิดใช้งาน `omway` โดยไม่ส่งผลกระทบต่อข้อมูลรับรองของผู้ให้บริการ

การค้นพบโมเดลจะคำนึงถึงผู้ให้บริการ: โมเดลที่ใช้ร่วมกันสามารถรองรับโดยผู้ให้บริการหลายราย ในขณะที่โมเดลเฉพาะของผู้ให้บริการจะใช้เฉพาะข้อมูลรับรองที่เข้ากันได้เท่านั้น แต่ละข้อมูลรับรองที่ได้รับการยืนยันจะจัดเก็บแคตตาล็อกผู้ให้บริการของตนเอง และเราเตอร์จะให้ความสำคัญกับการสนับสนุนที่ประกาศไว้ของข้อมูลรับรองมากกว่าการอนุมานผู้ให้บริการทั่วไป การรีเฟรชแคตตาล็อกจะตรวจสอบความพร้อมใช้งานของผู้ให้บริการปัจจุบันอีกครั้ง ตัวเลือกที่ไม่พร้อมใช้งานจะยังคงมองเห็นได้ในการกำหนดค่าจนกว่าจะได้รับการกู้คืนหรือลบออก

เมื่ออัปสตรีมส่งคืน `404` สำหรับโมเดลที่เป็นรูปธรรม Omni Gateway จะบันทึกเส้นทางที่ไม่พร้อมใช้งานสำหรับข้อมูลรับรองและโมเดลนั้นแทนที่จะระงับผู้ให้บริการทั้งหมด เส้นทางดังกล่าวจะถูกหลีกเลี่ยงชั่วคราวในทันทีและยังคงมองเห็นได้ใน **Unavailable Model Routes** จนกว่าจะถูกลบออกหรือข้อมูลรับรองได้รับการตรวจสอบใหม่ ซึ่งจะช่วยป้องกันไม่ให้การสมัครสมาชิกหรือสิทธิ์ตามภูมิภาคของบัญชีหนึ่งส่งผลกระทบต่อบัญชีอื่นที่ผู้ให้บริการรายเดียวกัน หากไม่มีข้อมูลรับรองที่เปิดใช้งานประกาศหรือสามารถอนุมานการสนับสนุนสำหรับโมเดลที่เป็นรูปธรรมที่ร้องขอ เกตเวย์จะส่งกลับข้อผิดพลาดไม่มีข้อมูลรับรองที่เข้ากันได้ที่ชัดเจนแทนที่จะส่งคำขอไปยังผู้ให้บริการแบบสุ่ม

Omni Gateway รู้จักคำนำหน้าและคำต่อท้ายคุณสมบัติในชื่อโมเดล:

- `fake-streaming/{model}` หรือคำนำหน้าการจำลองสตรีมที่กำหนดค่าไว้สำหรับไคลเอนต์ที่ต้องการเอาต์พุต SSE
- `streaming-anti-truncation/{model}` หรือคำนำหน้าป้องกันการตัดทอนที่กำหนดค่าไว้สำหรับการกู้คืนการสตรีมแบบยาว
- คำต่อท้ายการคิด เช่น `-high`, `-medium`, `-low`, `-minimal` และ `-max` สำหรับโมเดลตระกูล Gemini ที่รองรับ
- คำต่อท้ายการค้นหา เช่น `-search` สำหรับโมเดลที่รองรับการอิงข้อมูลด้วย Google Search (grounding)

อะแดปเตอร์ของผู้ให้บริการจะปรับชื่อคุณสมบัติเหล่านี้ให้เป็นมาตรฐานก่อนส่งคำขอไปยังอัปสตรีม

## ความโปร่งใสในการใช้งานและค่าใช้จ่าย

Omni Gateway บันทึกปริมาณคำขอ, อัตราความสำเร็จ, การระบุข้อมูลรับรอง, การใช้โทเค็นที่รายงานโดยผู้ให้บริการ และโทเค็นโดยประมาณที่ถูกตัดออกโดยการบีบอัดบริบทสำหรับแต่ละช่วงเวลาของแดชบอร์ด การประหยัดจากการบีบอัดถูกระบุว่าเป็นค่าประมาณเนื่องจากตัวตัดคำ (tokenizer) และกฎการเรียกเก็บเงินของผู้ให้บริการยังคงมีอำนาจตัดสินขั้นสุดท้าย การกำหนดเส้นทางตามราคาของผู้ให้บริการถูกละเว้นไว้เป็นชั้นนโยบายในอนาคตโดยเจตนา เพื่อให้ API หลักยังคงเสถียรเมื่อมีการเพิ่มผู้ให้บริการมากขึ้น

## เวิร์กโฟลว์ข้อมูลรับรอง

1. เริ่มต้น Omni Gateway
2. เปิด `http://YOUR_SERVER_IP:4283` บน VPS หรือ `http://127.0.0.1:4283` สำหรับการพัฒนาในเครื่อง
3. สร้างรหัสผ่านคอนโซลบนหน้าจอตั้งค่าการรันครั้งแรก สำหรับการตั้งค่าระยะไกล ให้ป้อนโทเค็นบูตสแตรปจากบันทึกของแอปพลิเคชัน หรือกำหนดค่า `PANEL_PASSWORD` ล่วงหน้า
4. เพิ่มบัญชี, คีย์ API หรือการเชื่อมต่อ Ollama จากหน้า Providers
5. ตรวจสอบข้อมูลรับรองและดูสถานะคูลดาวน์/ข้อผิดพลาดในพาเนล
6. ชี้เครื่องมือเขียนโค้ดของคุณไปยังหนึ่งในพื้นผิว API ด้านบน

เมื่อเพิ่มข้อมูลรับรอง Google Antigravity ทาง Google จะเปลี่ยนเส้นทางเบราว์เซอร์ไปที่ `http://localhost:4283/callback` หลังจากลงชื่อเข้าใช้ ในเครื่องโลคัล Omni Gateway จะแสดงหน้าความสำเร็จของ OAuth บน VPS ที่อยู่ `localhost` นั้นเป็นของเครื่องเบราว์เซอร์ของผู้ใช้ ดังนั้นหน้าเว็บอาจโหลดไม่สำเร็จ ให้คัดลอก URL แบบเต็มจากแถบที่อยู่ของเบราว์เซอร์ กลับไปที่หน้า Providers วางลงใน `Callback URL` แล้วคลิก `Save credential`

Google AI Studio ใช้การยืนยันตัวตนด้วยคีย์ API แทน OAuth เพิ่มคีย์จากหน้า Providers แล้ว Omni Gateway จะตรวจสอบความถูกต้องกับแคตตาล็อกโมเดลของ Google จัดเก็บเป็นข้อมูลรับรองของผู้ให้บริการ และกำหนดเส้นทางคำขอ Gemini หรือ Gemma ที่เข้ากันได้ผ่านคีย์นั้น เราเตอร์อัจฉริยะสามารถสลับสำรองระหว่าง AI Studio และ Google Antigravity สำหรับโมเดล Gemini ที่ใช้ร่วมกันได้ ในขณะที่ยังคงรักษาโมเดลเฉพาะของผู้ให้บริการไว้บนข้อมูลรับรองที่เข้ากันได้

การนำเข้าแบบกลุ่มของ Google AI Studio รองรับไฟล์ JSON และไฟล์บีบอัด ZIP ที่มีไฟล์ JSON เอกสาร JSON อาจมีหนึ่งคีย์, อาร์เรย์ `api_keys` หรืออาร์เรย์ของออบเจกต์คีย์:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

ทุกคีย์ที่นำเข้าจะได้รับการตรวจสอบความถูกต้องก่อนจัดเก็บ คีย์ที่ซ้ำกันในการนำเข้าเดียวกันจะถูกข้าม คีย์ที่มีอยู่จะได้รับการตรวจสอบใหม่และอัปเดต และรายการที่ไม่ถูกต้องจะถูกรายงานโดยไม่เปิดเผยค่าของคีย์

Grok Build รองรับข้อมูลรับรอง PKCE OAuth ในขณะที่ SpaceXAI Console รองรับคีย์ API คีย์ SpaceXAI Console จะได้รับการตรวจสอบความถูกต้องกับแคตตาล็อกโมเดลของ Grok Build ก่อนจัดเก็บ สำหรับ Grok Build OAuth นั้น Omni Gateway จะสร้างลิงก์การอนุญาต หลังจากการอนุญาต ให้คัดลอกโค้ดที่แสดงบนหน้าการอนุญาต Grok Build แล้ววางลงในแบบฟอร์ม Grok Build OAuth โทเค็นการเข้าถึงจะได้รับการรีเฟรชโดยอัตโนมัติเมื่อมีรีเฟรชโทเค็น และข้อมูลรับรองทั้งสองประเภทจะแสดงเฉพาะโมเดล Grok Build ที่ประกาศโดยแคตตาล็อกปัจจุบันเท่านั้น หน้า Pool สามารถดึงข้อมูลการใช้เครดิตรายเดือน และการใช้งานรายสัปดาห์ (เมื่อ xAI ระบุให้) สำหรับบัญชี Grok Build OAuth มุมมองการเรียกเก็บเงินระดับบัญชีนี้ไม่สามารถใช้ได้กับคีย์ API ของ SpaceXAI Console

Codex ใช้โฟลว์การอนุญาตอุปกรณ์ของ OpenAI สร้างรหัสอุปกรณ์จากหน้า Providers เปิด URL การยืนยันที่แสดง ป้อนรหัส เสร็จสิ้นการลงชื่อเข้าใช้ และกลับมาตรวจสอบการอนุญาต Omni Gateway จะจัดเก็บแคตตาล็อกโมเดลตามขอบเขตบัญชีที่ Codex ส่งคืน รีเฟรชโทเค็นการเข้าถึง OAuth เมื่อจำเป็น และส่งคำขอที่เข้ากันได้ผ่านการขนส่ง Codex Responses ส่วน OpenAI Platform ใช้การยืนยันตัวตนด้วยคีย์ API คีย์จะได้รับการตรวจสอบผ่านแคตตาล็อกโมเดลบัญชีก่อนเข้าสู่พูล ผลิตภัณฑ์ทั้งสองรองรับการนำเข้า JSON และ ZIP พร้อมการตรวจสอบความถูกต้องและการตัดข้อมูลซ้ำซ้อนเฉพาะผู้ให้บริการ

Claude Code ใช้โฟลว์ Anthropic PKCE OAuth สร้างลิงก์การอนุญาต เสร็จสิ้นการอนุญาต จากนั้นวางรหัสการอนุญาตที่ส่งคืนลงในหน้า Providers ส่วน Claude Platform จะยอมรับคีย์ API ของ Anthropic ผลิตภัณฑ์ทั้งสองจะค้นพบโมเดลที่เปิดเผยต่อแต่ละข้อมูลรับรอง ใช้การขนส่ง Anthropic Messages รีเฟรชโทเค็นการเข้าถึง Claude Code เมื่อเป็นไปได้ และรองรับการนำเข้า JSON หรือ ZIP ที่ผ่านการตรวจสอบแล้ว

การเชื่อมต่อ Ollama ได้รับการกำหนดค่าตามแต่ละจุดปลายทาง และอาจรวมคีย์ API bearer ทางเลือกสำหรับเซิร์ฟเวอร์ที่ได้รับการป้องกันหรือบนคลาวด์ Omni Gateway ค้นพบโมเดลผ่าน `/api/tags` และกำหนดเส้นทางการอนุมานผ่าน `/api/chat` เมื่อ Omni Gateway ทำงานใน Docker คำว่า `localhost` จะหมายถึงตัวคอนเทนเนอร์เอง ให้ใช้ที่อยู่ host-gateway หรือปลายทาง Ollama อื่นที่สามารถเข้าถึงได้ผ่านเครือข่าย

การนำเข้าพูลและการนำเข้าแบบกลุ่มของ Google Antigravity รองรับไฟล์เก็บถาวรสูงสุด 10 MB, ไม่เกิน 500 ไฟล์, ไฟล์ข้อมูลรับรองแต่ละไฟล์สูงสุด 2 MB และข้อมูลที่ไม่ได้บีบอัดสูงสุด 25 MB การนำเข้าผู้ให้บริการ Google AI Studio, OpenAI, Anthropic และ Ollama ใช้ขีดจำกัดที่เข้มงวดกว่าคือ 2 MB ต่อไฟล์ที่นำเข้า, 200 รายการ JSON และข้อมูลที่ไม่ได้บีบอัด 5 MB

หน้า Pool ยังมีเวิร์กโฟลว์การสำรองข้อมูลที่เป็นอิสระจากผู้ให้บริการ `Download ZIP` จะส่งออกพูลข้อมูลรับรองที่ใช้งานอยู่ และ `Import ZIP` จะกู้คืนไฟล์เก็บถาวรนั้นโดยระบุข้อมูลรับรองแต่ละรายการเป็น Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform หรือ Ollama บัญชี OAuth จะรักษาการตัดข้อมูลซ้ำซ้อนของข้อมูลประจำตัวตามขอบเขตของผู้ให้บริการ ในขณะที่คีย์ API จะได้รับการตรวจสอบและตัดข้อมูลซ้ำซ้อนด้วยลายนิ้วมือคีย์ที่ไม่สามารถย้อนกลับได้ตามขอบเขตของผู้ให้บริการ รายการที่ไม่รองรับหรือมีรูปแบบไม่ถูกต้องจะถูกรายงานเป็นรายบุคคลโดยไม่บล็อกข้อมูลรับรองที่ถูกต้องในไฟล์เก็บถาวรเดียวกัน

ข้อมูลรับรอง Google Antigravity ใช้ `google-antigravity-{account_fingerprint}.json` ซึ่งลายนิ้วมือได้มาจากอีเมลบัญชีที่ปรับให้เป็นมาตรฐานโดยไม่เปิดเผยอีเมล ข้อมูลรับรอง Google AI Studio ใช้ `google-ai-studio-{key_fingerprint}.json`, ข้อมูลรับรอง Grok Build OAuth ใช้ `grok-{account_fingerprint}.json`, ข้อมูลรับรอง SpaceXAI Console ใช้ `xai-console-{key_fingerprint}.json`, ข้อมูลรับรอง Codex ใช้ `openai-codex-{account_fingerprint}.json`, ข้อมูลรับรอง OpenAI Platform ใช้ `openai-platform-{key_fingerprint}.json`, ข้อมูลรับรอง Claude Code ใช้ `claude-code-{account_fingerprint}.json`, ข้อมูลรับรอง Claude Platform ใช้ `claude-platform-{key_fingerprint}.json` และการเชื่อมต่อ Ollama ใช้ `ollama-{connection_fingerprint}.json` ข้อมูลรับรองเดิม `provider_*.json` และ `xai-grok-*.json` ยังคงเข้ากันได้และจะถูกส่งออกด้วยชื่อตามแบบแผนมาตรฐาน

ชื่อโหมดข้อมูลรับรอง:

- `code_assist`: พูลข้อมูลรับรอง Code Assist มาตรฐาน
- `provider`: พูลข้อมูลรับรองแบ็กเอนด์ของผู้ให้บริการ

## การจัดเก็บข้อมูล

การติดตั้งแบบอินสแตนซ์เดียวใช้ที่จัดเก็บข้อมูลที่รองรับด้วย SQLite ในไดเรกทอรีข้อมูลที่เมานต์ บน Docker ให้คง `/app/backend/data/creds` และ `/app/backend/data/logs` ที่เมานต์ไว้กับพาธโฮสต์ที่คงทน เช่น `/opt/omni-gateway/creds` และ `/opt/omni-gateway/logs`

MongoDB หรือ PostgreSQL สามารถแทนที่ SQLite ในเครื่องได้ตามความต้องการในการปฏิบัติงานหรือการทดสอบการย้ายข้อมูล:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

สามารถเพิ่ม Redis เพื่อเพิ่มความเร็วของแคช/เซสชัน:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

ที่จัดเก็บข้อมูลภายนอกไม่ได้ทำให้รันไทม์ 1.x สามารถปรับขนาดในแนวนอนได้ (horizontal scaling) ให้รัน worker หนึ่งตัวและแบบจำลอง (replica) หนึ่งชุดจนกว่าการจองข้อมูลรับรองแบบกระจาย, คูลดาวน์, การยกเลิกเซสชัน และการรวบรวมการใช้งานจะได้รับการนำไปใช้งาน กำหนดค่า MongoDB หรือ PostgreSQL อย่างใดอย่างหนึ่งเท่านั้น อย่ากำหนดค่าทั้งสองอย่าง ความล้มเหลวในการเริ่มต้นฐานข้อมูลภายนอกอย่างชัดเจนจะหยุดการเริ่มต้นระบบแทนที่จะเปลี่ยนกลับไปใช้ SQLite อย่างเงียบๆ

การนำเข้าข้อมูลรับรองจากสภาพแวดล้อมมีให้ใช้งานได้จากแผงควบคุม กำหนดค่าหนึ่งในตัวแปรต่อไปนี้เป็น JSON ดิบ หรือใช้ตัวแปร `_B64` ที่ตรงกันสำหรับ JSON ที่เข้ารหัส base64:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

เพย์โหลดสามารถเป็นออบเจกต์ข้อมูลรับรองเดี่ยว, อาร์เรย์ หรือ `{ "credentials": [...] }`

## การพัฒนา

ส่วนนี้สำหรับผู้มีส่วนร่วมและการดีบักในเครื่อง การติดตั้งใช้งานจริงในระบบโปรดักชันควรใช้ Docker พร้อมวอลุ่มโฮสต์แบบถาวร

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

เริ่มบริการหลังจากผ่านการตรวจสอบทั้งหมด:

```bash
python backend/main.py
```

เกณฑ์มาตรฐานในการผลิตคือ Python 3.12 และปัจจุบัน CI ตรวจสอบความถูกต้องของ Python 3.12 และ 3.14 ดู [การมีส่วนร่วม](../../CONTRIBUTING.md) สำหรับเวิร์กโฟลว์ pull-request และความคาดหวังในการตรวจสอบ

## หมายเหตุการติดตั้ง

- ห้ามคอมมิตไฟล์ JSON ข้อมูลรับรองหรือไฟล์ `.env` โดยเด็ดขาด
- ใช้ `API_KEY` โดยเฉพาะสำหรับการรวมเข้ากับไคลเอนต์ และใช้ `PANEL_PASSWORD` แยกต่างหากสำหรับการเข้าถึงคอนโซล
- จำกัดการเข้าถึงวอลุ่มข้อมูลรับรองแบบถาวรหรือฐานข้อมูลภายนอก และเปิดใช้งานการเข้ารหัสระดับแพลตฟอร์มเมื่อไม่มีการใช้งาน (encryption at rest) โทเค็นของผู้ให้บริการจะต้องสามารถเรียกค้นได้โดยเราเตอร์
- วาง Omni Gateway ไว้ด้านหลัง reverse proxy พร้อม TLS เมื่อสามารถเข้าถึงได้จากภายนอก localhost
- กำหนดค่า reverse proxy เพื่อรักษา `Host` และส่งผ่าน `X-Forwarded-Proto` กำหนด `PANEL_COOKIE_SECURE=true` เมื่อรับประกันการยุติ HTTPS
- ตั้งค่า `TRUST_PROXY_HEADERS=true` เฉพาะเมื่อบริการสามารถเข้าถึงได้ผ่านพร็อกซีที่เชื่อถือได้ซึ่งเขียนทับ `X-Forwarded-For` และ `X-Forwarded-Proto` เท่านั้น
- ใช้ `GET /health` สำหรับการตรวจสอบการทำงานของกระบวนการ (liveness) และ `GET /ready` สำหรับการตรวจสอบความพร้อมที่คำนึงถึงที่จัดเก็บข้อมูล (readiness)
- อิมเมจ Docker เริ่มต้นด้วยสิทธิ์ root เพียงนานพอที่จะแก้ไขความเป็นเจ้าของไดเรกทอรีข้อมูลที่เมานต์ไว้ จากนั้นจะเรียกใช้บริการในฐานะผู้ใช้ `gateway` ที่ไม่มีสิทธิ์พิเศษ
- กำหนด `CORS_ORIGINS` เป็นต้นทางที่เชื่อถือได้ชัดเจนเมื่อไคลเอนต์เบราว์เซอร์ต้องการการเข้าถึงข้ามต้นทาง
- สำรองข้อมูล `/opt/omni-gateway` หรือ `DATA_DIR` ที่คุณเลือกเสมอก่อนอัปเกรดหรือย้ายเซิร์ฟเวอร์
- การเผยแพร่อิมเมจ Docker ใช้ข้อมูลลับของที่เก็บข้อมูล `DOCKERHUB_USERNAME` และ `DOCKERHUB_TOKEN` สำหรับ Docker Hub และ `GITHUB_TOKEN` ในตัวสำหรับ GitHub Packages ที่ `ghcr.io/nguywnben/omni-gateway` กำหนดตัวแปรที่เก็บข้อมูลทางเลือก `IMAGE_NAME` เฉพาะเมื่อเผยแพร่ไปยังชื่ออิมเมจ Docker Hub ที่กำหนดเอง
- คงค่า `WORKERS=1` และแบบจำลองแอปพลิเคชันหนึ่งชุดสำหรับซีรีส์ 1.x ที่จัดเก็บข้อมูลภายนอกไม่สามารถทดแทนการประสานงานแบบกระจายได้
- ใช้เส้นทางการจัดการมาตรฐาน `/api/credentials` นามแฝงเบต้า `/api/creds` ถูกลบออกใน 1.0.0 แล้ว
- ปฏิบัติตาม [การอัปเกรดเป็น 1.0](../upgrading-to-1.0.md) ก่อนที่จะย้ายการติดตั้งรุ่นเบต้า
- ปฏิบัติตาม [คู่มือการอัปเดต](../updating.md) เมื่ออัปเกรดอินสแตนซ์ที่ติดตั้งใช้งานหรือย้อนกลับรุ่น
- ปฏิบัติตาม [รายการตรวจสอบการเปิดตัว](../release-checklist.md) ที่ดูแลไว้ก่อนที่จะแท็กหรือโปรโมตอิมเมจ
- เก็บนโยบายการเก็บรักษาบันทึกและการหมุนเวียนข้อมูลรับรองให้สอดคล้องกับขีดจำกัดการใช้งานของคุณ
- หมุนเวียนข้อมูลรับรองทันทีหากที่เก็บข้อมูลหรือเครื่องสแกนแพลตฟอร์มรายงานความลับรั่วไหล
- Render Blueprint ใช้บริการแบบชำระเงินพร้อมดิสก์แบบถาวร บริการฟรีของ Render ใช้ระบบไฟล์ชั่วคราวและเหมาะสำหรับการประเมินแบบใช้แล้วทิ้งเท่านั้น

## ชุมชนและสุขภาพของโครงการ

- อ่าน [การมีส่วนร่วม](../../CONTRIBUTING.md) ก่อนเปิด pull request
- รายงานช่องโหว่ผ่านกระบวนการส่วนตัวใน [นโยบายความปลอดภัย](../../SECURITY.md)
- ตรวจสอบ [บันทึกการเปลี่ยนแปลง](../../CHANGELOG.md) สำหรับการเปลี่ยนแปลงระดับรุ่น
- ปฏิบัติตาม [หลักจรรยาบรรณ](../../CODE_OF_CONDUCT.md) ในทุกพื้นที่ของโครงการ

## การแสดงความขอบคุณ & แรงบันดาลใจ

Omni Gateway ยืนอยู่บนไหล่ของชุมชนเราเตอร์ AI, การวัดระยะไกล และเกตเวย์แบบโอเพนซอร์ส เราขอแสดงความขอบคุณต่อผู้สร้างและผู้ดูแลโครงการเหล่านี้:

| โครงการ | คำอธิบาย | ดาว |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | แรงบันดาลใจสำหรับการจัดการคีย์แบบหลายผู้ให้บริการและการรวม API บนเว็บ | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | ผู้บุกเบิกพร็อกซีหลายรูปแบบและเลเยอร์การแปลงโปรโตคอลสำหรับ AI coding CLI | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | พร็อกซี LLM แบบรวมศูนย์ที่เป็นมาตรฐาน, การกระจายโหลด และการกำหนดเส้นทางสำรอง | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | สถาปัตยกรรมเกตเวย์ AI ความเร็วสูงพิเศษ, กลยุทธ์การกำหนดเส้นทาง และรูปแบบการสำรองที่ยืดหยุ่น | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | แพลตฟอร์มวิศวกรรม LLM แบบโอเพนซอร์ส, การติดตามร่องรอย, การสังเกตการณ์ และการรับข้อมูลเมตริก | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## ใบอนุญาต

Omni Gateway เผยแพร่ภายใต้ [ใบอนุญาต MIT](../../LICENSE)
