<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Universal AI Router & Gateway Multi-Penyedia Terpadu untuk Alat AI Coding</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20bahasa-orange?style=flat-square" alt="15 Bahasa">
  </p>

  <p>
    <a href="#penyedia-yang-didukung"><b>🌐 Penyedia yang Didukung</b></a> •
    <a href="#kemampuan-utama"><b>⚡ Kemampuan Utama</b></a> •
    <a href="#penerapan"><b>🐳 Penerapan Docker</b></a> •
    <a href="#antarmuka-sdk"><b>🔌 Penyiapan SDK</b></a> •
    <a href="../architecture.md"><b>📖 Arsitektur</b></a>
  </p>

  <p>
    <b>Bahasa Konsol & Dokumentasi:</b><br>
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
    <b>Indonesia</b> •
    <a href="README.th.md">ภาษาไทย</a> •
    <a href="README.tr.md">Türkçe</a>
  </p>
</div>

---

Router AI universal untuk alat pemrograman. Omni Gateway menyediakan auto-fallback cerdas, pembersihan permintaan sadar token, visibilitas penggunaan, dan penerjemahan format mulus sehingga agen lokal, asisten IDE, dan skrip otomatisasi dapat menggunakan kapasitas LLM gratis dan premium melalui satu permukaan API yang stabil.

> **Status proyek:** Stabil. Versi `1.3.1` melengkapi konsol yang dilokalkan dalam 15 bahasa, menambahkan pesan API manajemen yang sadar lokal dan panduan pembaruan berbasis rilis, serta mempertahankan rute SDK yang stabil, rute manajemen kanonikal, nama konfigurasi, dan kontrak runtime instans tunggal yang ditetapkan pada `1.0.0`.

## Mengapa Omni Gateway

Alur kerja coding modern sering menggabungkan berbagai klien dan penyedia: alat yang kompatibel dengan OpenAI, SDK native Gemini, agen gaya Anthropic, kredensial berbasis Google, dan rute model eksperimental. Omni Gateway berada di antara klien-klien tersebut dan backend model sehingga setiap alat dapat terus berbicara dalam format yang sudah dipahaminya, sementara gateway menangani perutean, percobaan ulang (retry), pembersihan permintaan, dan normalisasi respons.

## Kemampuan Utama

- Auto-fallback cerdas: mereservasi kredensial per permintaan, menyebarkan lalu lintas bersamaan, melacak setiap percobaan untuk rotasi yang adil, dan merutekan pengalihan dari kegagalan terkini, cooldown, batas laju (rate limit), dan kapasitas yang habis.
- Pembersihan sadar token: menormalkan muatan (payload) dan hanya memangkas awalan percakapan yang terlalu besar pada batas giliran yang aman sambil mempertahankan instruksi sistem, definisi alat, dan konteks terkini.
- Penerjemahan format: menerima OpenAI Chat Completions dan Responses, permintaan native Gemini, dan Anthropic Messages, lalu menerjemahkan permintaan serta respons streaming lintas format.
- Orkestrasi kredensial: mengelola akun OAuth dan kunci API penyedia dengan status kesehatan, pelacakan cooldown, verifikasi, deduplikasi, dan fallback berbasis penyedia.
- Perutean model tingkat kredensial: memelihara katalog kemampuan terpisah untuk setiap kredensial, sehingga hak akses satu akun tidak dapat mengirim permintaan ke akun lain yang tidak mengekspos model yang dipilih.
- Memori kesehatan rute: mencatat respons model-tidak-ditemukan pada cakupan kredensial dan menampilkan rute yang terpengaruh untuk pemulihan dari halaman Models.
- Ketahanan streaming: mendukung SSE streaming, pseudo-streaming untuk klien yang memerlukan output streaming, dan percobaan ulang anti-pemotongan (anti-truncation) untuk generasi panjang.
- Panel kontrol: dilengkapi dengan konsol web untuk kredensial, log, konfigurasi, penggunaan, dan informasi versi.

## Pratinjau Konsol

![Pool kredensial Omni Gateway](../assets/screenshots/credential-pool.png)

## Penyedia yang Didukung

Omni Gateway mengadaptasi permintaan secara mulus di seluruh penyedia AI terkemuka, mesin runtime lokal, dan endpoint OAuth:

| Penyedia | Tipe Autentikasi | Protokol yang Didukung | Auto-Failover | Streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | Kompatibel OpenAI, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | Kompatibel OpenAI | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Lokal / Self-hosted)** | Lokal / Base URL | Kompatibel OpenAI | ✅ | ✅ |

## Arsitektur

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | Integrasi IDE
        |
        v
Omni Gateway
  autentikasi -> penerjemahan format -> pembersihan sadar token -> perutean -> fallback -> streaming
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

API publik tetap stabil sementara adaptor khusus penyedia berkembang di balik Omni Gateway.

## Struktur Repositori

```text
backend/       FastAPI composition root, inti perutean, penerjemah, penyimpanan, dan pengujian
frontend/      Markup konsol manajemen, gaya, skrip, dan aset penyedia
deploy/        Definisi kontainer, manifes platform, dan skrip sistem operasi
docs/          Catatan arsitektur dan aset proyek yang dipelihara
.github/       CI, otomatisasi dependensi, dan template kontribusi
```

Lihat [Arsitektur](../architecture.md) untuk batasan modul, alur permintaan, kepemilikan status, dan batasan rilis saat ini.

## Penerapan

Omni Gateway ditujukan untuk penerapan nyata. Docker adalah jalur yang direkomendasikan untuk lingkungan VPS dan server karena menjaga runtime tetap terisolasi sambil mempertahankan kredensial dan log pada host.

### Docker pada VPS

Buat direktori host persisten terlebih dahulu:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Mulai layanan:

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

Rilis yang sama dipublikasikan ke GitHub Packages sebagai `ghcr.io/nguywnben/omni-gateway:1.3.1`. Tag `latest` melacak rilis stabil terbaru; `edge` melacak build terverifikasi tetapi belum dirilis dari `main`. Sematkan tag versi atau digest saat penerapan yang dapat direproduksi diperlukan.

Buka panel kontrol di:

```text
http://IP_SERVER_ANDA:4283
```

Pada peluncuran pertama, buat kata sandi konsol di layar pengaturan. Tidak ada kata sandi default yang disertakan. Peramban jarak jauh juga harus memasukkan bootstrap token yang dicetak oleh `docker logs omni-gateway`; pengaturan langsung di localhost tidak memerlukannya. Tetapkan `SETUP_TOKEN` sebelum startup saat otomatisasi penerapan memerlukan bootstrap token yang stabil.

Kata sandi yang dikelola oleh aplikasi disimpan sebagai hash scrypt bergaram (salted), sesi panel kontrol menggunakan cookie HttpOnly, dan permintaan SDK publik mengautentikasi dengan kunci API `sk-ogw-` yang dihasilkan. Untuk penerapan non-interaktif, konfigurasikan `PANEL_PASSWORD` sebelumnya dan lewati layar pengaturan sepenuhnya.

Kontainer `1.3.1` dipublikasikan untuk `linux/amd64`. Publikasi ARM64 sengaja dijeda hingga setiap dependensi penyedia, termasuk tumpukan transportasi Vertex, dapat dibangun dan diuji dengan kontrak yang sama.

Jika firewall server aktif, izinkan port gateway:

```bash
sudo ufw allow 4283/tcp
```

Lihat log:

```bash
sudo docker logs -f omni-gateway
```

Perbarui ke image stabil terbaru:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Kemudian mulai kontainer lagi dengan perintah `docker run` yang sama di atas. Direktori `/opt/omni-gateway` yang dipasang mempertahankan kredensial, konfigurasi, data penggunaan, dan log di seluruh pembaruan kontainer.

### Docker Compose

Untuk penerapan berbasis repositori:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

File compose yang disertakan menarik `nguywnben/omni-gateway:latest` dan menggunakan `/opt/omni-gateway` secara default untuk data host persisten. Tetapkan `IMAGE=nguywnben/omni-gateway:1.3.1` untuk menyematkan rilis ini, dan tetapkan `DATA_DIR=/jalur/kustom` saat server menggunakan lokasi penyimpanan yang berbeda.

Compose meneruskan `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, URI penyimpanan eksternal, dan `PROXY` dari shell atau file `.env` root. Biarkan kosong untuk mempertahankan pembuatan kunci otomatis, penyiapan pertama kali, penyimpanan SQLite lokal, dan jaringan keluar langsung.

### Pengembangan Lokal

Gunakan alur kerja Python saat mengembangkan atau men-debug gateway secara lokal:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Pada Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Buka panel kontrol di:

```text
http://127.0.0.1:4283
```

Pengembangan lokal menggunakan layar penyiapan pertama kali yang sama dengan penerapan Docker.

## Konfigurasi

Omni Gateway membaca konfigurasi dari variabel lingkungan terlebih dahulu, kemudian konfigurasi yang disimpan, lalu nilai default.

| Variabel | Default | Tujuan |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Alamat ikat (bind address). |
| `PORT` | `4283` | Port HTTP. |
| `HOST_PORT` | `4283` | Port sisi host yang hanya digunakan oleh Docker Compose. |
| `WORKERS` | `1` | Jumlah worker yang didukung untuk seri 1.x. Nilai lain ditolak hingga reservasi, cooldown, sesi, dan agregasi penggunaan dikoordinasikan lintas proses. |
| `CORS_ORIGINS` | kosong | Asal (origin) peramban yang dipisahkan koma yang diizinkan memanggil API lintas-asal (cross-origin). Biarkan kosong untuk penggunaan konsol origin yang sama. |
| `CORS_ORIGIN_REGEX` | kosong | Regex opsional untuk origin peramban dinamis yang dikelola. |
| `API_KEY` | dibuat otomatis | Kunci pilihan untuk permintaan API klien publik. Harus dimulai dengan `sk-ogw-`. |
| `PANEL_PASSWORD` | kosong hingga disiapkan | Kata sandi untuk panel kontrol web. |
| `SETUP_TOKEN` | dibuat per proses | Bootstrap token tetap opsional yang diperlukan untuk pengaturan jarak jauh pertama kali. Jika diabaikan, baca token yang dibuat dari log aplikasi atau kontainer. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Masa berlaku sesi konsol web dalam detik. |
| `PANEL_COOKIE_SECURE` | otomatis | Tetapkan `true` untuk mewajibkan cookie panel hanya melalui HTTPS. Biarkan kosong untuk mendeteksi HTTPS melalui `X-Forwarded-Proto`. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Jendela pembatasan laju login dalam detik. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Percobaan login gagal maksimum yang diizinkan per klien dalam jendela pembatasan laju. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Alamat klien maksimum yang disimpan oleh pembatas login dalam memori. |
| `MAX_REQUEST_BODY_MB` | `64` | Ukuran tubuh permintaan HTTP maksimum dalam MiB. Permintaan SDK yang terlalu besar mengembalikan amplop kesalahan protokol native. |
| `TRUST_PROXY_HEADERS` | `false` | Hanya terima header penerusan klien/protokol dari reverse proxy tepercaya yang menimpanya. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Direktori penyimpanan kredensial. Di Docker, pertahankan `/app/backend/data/creds` dengan volume host. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Endpoint backend Code Assist. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Endpoint backend Google Antigravity. |
| `PROXY` | kosong | Proksi HTTP, HTTPS, atau SOCKS opsional. |
| `RETRY_429_ENABLED` | `true` | Aktifkan percobaan ulang terbatas untuk batas laju dan kegagalan sementara upstream. Nama lama dipertahankan untuk kompatibilitas konfigurasi. |
| `RETRY_429_MAX_RETRIES` | `5` | Upaya percobaan ulang maksimum untuk kegagalan sementara upstream. |
| `RETRY_429_INTERVAL` | `1` | Penundaan dasar antar percobaan ulang sementara dalam detik. |
| `AUTO_DISABLE` | `false` | Nonaktifkan kredensial setelah kegagalan berat (hard failure) yang dikonfigurasi. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Kode status kegagalan berat yang dipisahkan koma. |
| `ROUTING_STRATEGY` | `balanced` | Kebijakan pemilihan kredensial: `balanced` atau `priority`. |
| `PREFERRED_PROVIDER` | kosong | Penyedia yang disukai oleh strategi `priority`, seperti `google_antigravity` atau `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Batas waktu inferensi penyedia, dibatasi antara 5 dan 900 detik. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Upaya kelanjutan maksimum untuk streaming anti-pemotongan. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Kompres riwayat percakapan yang terlalu besar sebelum perutean ke penyedia. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Ambang perkiraan token input yang mengaktifkan kompresi. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Target perkiraan token input setelah kompresi. Harus lebih rendah dari ambang batas. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Jumlah minimum giliran pengguna terkini yang dipertahankan selama kompresi. |
| `COMPATIBILITY_MODE` | `false` | Mengonversi pesan sistem untuk klien/model yang menolaknya. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Sertakan bidang penalaran (reasoning) model jika tersedia. |
| `MONGODB_URI` | kosong | Mengaktifkan penyimpanan MongoDB saat disetel. |
| `POSTGRESQL_URI` | kosong | Mengaktifkan penyimpanan PostgreSQL saat disetel. |
| `REDIS_URL` | kosong | Mengaktifkan cache/status sesi berbasis Redis saat disetel. |
| `CODE_ASSIST_CLIENT_ID` | klien desktop bawaan | Penimpaan opsional untuk Client ID OAuth Code Assist. |
| `CODE_ASSIST_CLIENT_SECRET` | klien desktop bawaan | Penimpaan opsional untuk Client Secret OAuth Code Assist. |
| `ANTIGRAVITY_CLIENT_ID` | klien desktop bawaan | Penimpaan opsional untuk Client ID OAuth Google Antigravity. Juga dapat dikelola dari halaman Providers. |
| `ANTIGRAVITY_CLIENT_SECRET` | klien desktop bawaan | Penimpaan opsional untuk Client Secret OAuth Google Antigravity. Konfigurasikan melalui env atau halaman Providers saat klien upstream berubah. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Penimpaan opsional untuk endpoint Google AI Studio Generative Language API. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Penimpaan opsional untuk endpoint API SpaceXAI Console untuk kredensial kunci API. Juga dapat dikelola dari halaman Providers. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Penimpaan opsional untuk endpoint langganan OAuth Grok Build. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Penimpaan opsional untuk penerbit OAuth Grok Build. Hanya host HTTPS di bawah `x.ai` yang diterima oleh konsol. |
| `XAI_CLIENT_ID` | klien publik bawaan | Penimpaan opsional untuk Client ID OAuth PKCE Grok Build. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Penimpaan opsional HTTP User-Agent bersama untuk permintaan Grok Build OAuth dan SpaceXAI Console API. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Penimpaan opsional untuk endpoint OpenAI Platform API. Juga dapat dikelola dari halaman Providers. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Penimpaan opsional untuk endpoint inferensi dan model akun Codex. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Penimpaan opsional untuk endpoint batas laju akun Codex. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Penimpaan opsional untuk layanan otorisasi perangkat Codex. |
| `CODEX_CLIENT_ID` | klien publik bawaan | Penimpaan opsional untuk Client ID OAuth perangkat Codex. |
| `CODEX_USER_AGENT` | nilai kompatibel Codex CLI | Penimpaan opsional User-Agent untuk permintaan Codex. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Penimpaan opsional untuk endpoint Claude Platform dan Claude Code Messages API. Juga dapat dikelola dari halaman Providers. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Penimpaan opsional untuk endpoint otorisasi PKCE Claude Code. Hanya host Anthropic dan Claude yang diterima oleh konsol. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Penimpaan opsional untuk endpoint token Claude Code. Hanya host Anthropic dan Claude yang diterima oleh konsol. |
| `CLAUDE_CLIENT_ID` | klien publik bawaan | Penimpaan opsional untuk Client ID OAuth PKCE Claude Code. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Penimpaan opsional User-Agent untuk permintaan Claude Code dan Claude Platform. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Penimpaan opsional protokol User-Agent Google Antigravity. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Penimpaan opsional userAgent tingkat payload Google Antigravity. |
| `LOG_LEVEL` | `info` | Tingkat log runtime. |
| `LOG_MAX_MB` | `10` | Ukuran file log aktif maksimum sebelum rotasi. |
| `LOG_BACKUP_COUNT` | `3` | Jumlah file log terotasi yang dipertahankan. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Tujuan file log. Di Docker, pertahankan `/app/backend/data/logs` dengan volume host. |

## Antarmuka SDK

Omni Gateway dirancang berdasarkan perilaku URL standar dari Python SDK resmi. Konfigurasikan setiap klien persis seperti yang ditunjukkan di bawah ini; gateway tidak memerlukan awalan jalur duplikat non-standar.

Contoh-contoh ini menggunakan model virtual `omway`. Konfigurasikan urutan fallback penyedia-model pada halaman Models terlebih dahulu, atau ganti dengan ID model konkret.

### OpenAI Python SDK

Gunakan `/v1` sebagai base URL OpenAI. SDK akan menambahkan `/chat/completions`.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Jelaskan repositori ini dalam satu paragraf."}],
)
```

Klien yang sama dapat menggunakan OpenAI Responses API:

```python
response = client.responses.create(
    model="omway",
    instructions="Jadilah ringkas.",
    input="Jelaskan repositori ini dalam satu paragraf.",
)

print(response.output_text)
```

Kompatibilitas Responses mendukung teks, input gambar, non-streaming function tools, dan SSE text streaming. Alat bawaan yang dihosting OpenAI, riwayat respons tersimpan, dan streaming function calls ditolak secara eksplisit karena Omni Gateway tidak mengeksekusi, mempertahankan, atau secara diam-diam membuang perilaku khusus OpenAI tersebut.

### Anthropic Python SDK

Gunakan origin gateway sebagai base URL Anthropic. SDK akan menambahkan `/v1/messages`.

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Draf pesan komit."}],
)
```

### Google GenAI Python SDK

Gunakan origin gateway sebagai base URL Google GenAI. SDK akan menambahkan rute model defaultnya, seperti `/v1beta/models/{model}:generateContent`.

```python
from google import genai
from google.genai import types

client = genai.Client(
    http_options={
        "base_url": "http://127.0.0.1:4283",
    },
    api_key="sk-ogw-..."
)

response = client.models.generate_content(
    model="omway",
    contents="Tulis sebuah fungsi Python kecil.",
    config=types.GenerateContentConfig(
        system_instruction="Anda adalah asisten yang membantu.",
    ),
)
```

### Rute yang Didukung

Omni Gateway mengekspos rute yang kompatibel dengan SDK tanpa namespace produk:

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

Kegagalan autentikasi, validasi permintaan, perutean, upstream, dan pra-streaming menggunakan amplop kesalahan native untuk antarmuka SDK yang dipilih. Setiap respons HTTP menyertakan `X-Request-ID`; klien dapat memberikan pengidentifikasi aman dalam header tersebut untuk korelasi menyeluruh (end-to-end). Respons yang dibatasi laju atau sementara tidak tersedia mempertahankan `Retry-After` ketika upstream menyediakannya.

## Fitur Model

Halaman Models membangun model virtual `omway` dari model yang ditemukan di seluruh kredensial penyedia yang diaktifkan. Atur anggotanya dalam urutan prioritas satu kali, lalu gunakan `omway` dari SDK yang didukung. Omni Gateway menyeimbangkan kredensial sehat yang mendukung model pertama dan melanjutkan melalui urutan model yang dikonfigurasi saat model tersebut tidak tersedia. ID model penyedia konkret tetap tersedia untuk klien yang memerlukan pemilihan model deterministik. Menyimpan pilihan kosong akan menonaktifkan `omway` tanpa memengaruhi kredensial penyedia.

Penemuan model berbasis penyedia: model bersama dapat didukung oleh beberapa penyedia, sementara model khusus penyedia hanya menggunakan kredensial yang kompatibel. Setiap kredensial terverifikasi menyimpan katalog penyedianya sendiri, dan router memberikan prioritas dukungan kredensial yang dinyatakan di atas inferensi penyedia umum. Menyegarkan katalog akan memeriksa ulang ketersediaan penyedia saat ini; pilihan yang tidak tersedia tetap terlihat dalam konfigurasi sampai dipulihkan atau dihapus.

Ketika upstream mengembalikan `404` untuk model konkret, Omni Gateway mencatat rute yang tidak tersedia untuk kredensial dan model tersebut alih-alih menekan seluruh penyedia. Rute tersebut langsung dihindari untuk sementara dan tetap terlihat di bawah **Unavailable Model Routes** sampai dihapus atau kredensial divalidasi ulang. Ini mencegah langganan atau hak regional satu akun memengaruhi akun lain di penyedia yang sama. Jika tidak ada kredensial yang diaktifkan menyatakan atau dapat menyimpulkan dukungan untuk model konkret yang diminta, gateway mengembalikan kesalahan kredensial-tidak-kompatibel yang jelas alih-alih mengirim permintaan ke penyedia acak.

Omni Gateway mengenali awalan dan akhiran fitur dalam nama model:

- `fake-streaming/{model}` atau awalan pseudo-streaming yang dikonfigurasi untuk klien yang memerlukan output SSE.
- `streaming-anti-truncation/{model}` atau awalan anti-pemotongan yang dikonfigurasi untuk pemulihan streaming bentuk panjang.
- Akhiran pemikiran seperti `-high`, `-medium`, `-low`, `-minimal`, dan `-max` untuk model keluarga Gemini yang didukung.
- Akhiran pencarian seperti `-search` untuk model yang mendukung grounding Google Search.

Adaptor penyedia menormalkan nama fitur ini sebelum mengirim permintaan ke upstream.

## Penggunaan dan Visibilitas Biaya

Omni Gateway mencatat volume permintaan, tingkat keberhasilan, atribusi kredensial, penggunaan token yang dilaporkan penyedia, dan perkiraan token yang dihapus oleh kompresi konteks untuk setiap rentang waktu dasbor. Penghematan kompresi diberi label sebagai perkiraan karena tokenizer penyedia dan aturan penagihan tetap bersifat otoritatif. Perutean berbasis harga penyedia sengaja dibiarkan sebagai lapisan kebijakan masa depan sehingga API inti tetap stabil seiring bertambahnya penyedia.

## Alur Kerja Kredensial

1. Mulai Omni Gateway.
2. Buka `http://IP_SERVER_ANDA:4283` di VPS, atau `http://127.0.0.1:4283` untuk pengembangan lokal.
3. Buat kata sandi konsol pada layar penyiapan pertama kali. Untuk penyiapan jarak jauh, masukkan bootstrap token dari log aplikasi; atau konfigurasikan `PANEL_PASSWORD` sebelumnya.
4. Tambahkan akun, kunci API, atau koneksi Ollama dari halaman Providers.
5. Verifikasi kredensial dan pantau status cooldown/kesalahan di panel.
6. Arahkan alat coding Anda ke salah satu antarmuka API di atas.

Saat menambahkan kredensial Google Antigravity, Google mengarahkan peramban ke `http://localhost:4283/callback` setelah masuk. Pada mesin lokal, Omni Gateway menampilkan halaman keberhasilan OAuth. Pada VPS, alamat `localhost` tersebut milik mesin peramban pengguna, sehingga halaman mungkin tidak dapat dimuat; salin URL lengkap dari bilah alamat peramban, kembali ke halaman Providers, tempel ke `Callback URL`, dan klik `Save credential`.

Google AI Studio menggunakan autentikasi kunci API alih-alih OAuth. Tambahkan kunci dari halaman Providers; Omni Gateway memvalidasinya terhadap katalog model Google, menyimpannya sebagai kredensial penyedia, dan merutekan permintaan Gemini atau Gemma yang kompatibel melaluinya. Router cerdas dapat melakukan fallback antara AI Studio dan Google Antigravity untuk model Gemini bersama sambil mempertahankan model khusus penyedia pada kredensial yang kompatibel.

Impor massal Google AI Studio menerima file JSON dan arsip ZIP yang berisi file JSON. Dokumen JSON dapat berisi satu kunci, larik `api_keys`, atau larik objek kunci:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Setiap kunci yang diimpor divalidasi sebelum disimpan. Kunci duplikat dalam impor yang sama dilewati, kunci yang ada divalidasi ulang dan diperbarui, dan entri yang tidak valid dilaporkan tanpa mengekspos nilai kunci.

Grok Build mendukung kredensial PKCE OAuth, sedangkan SpaceXAI Console mendukung kunci API. Kunci SpaceXAI Console divalidasi terhadap katalog model Grok Build sebelum disimpan. Untuk Grok Build OAuth, Omni Gateway menghasilkan tautan otorisasi; setelah otorisasi, salin kode yang ditampilkan pada halaman otorisasi Grok Build dan tempelkan ke dalam formulir Grok Build OAuth. Token akses diperbarui secara otomatis saat refresh token tersedia, dan kedua jenis kredensial hanya mengekspos model Grok Build yang dinyatakan oleh katalog saat ini. Halaman Pool dapat mengambil penggunaan kredit bulanan dan, ketika xAI menyediakannya, penggunaan mingguan untuk akun Grok Build OAuth. Tampilan penagihan tingkat akun ini tidak tersedia untuk kunci API SpaceXAI Console.

Codex menggunakan alur otorisasi perangkat OpenAI. Hasilkan kode perangkat dari halaman Providers, buka URL verifikasi yang ditampilkan, masukkan kode, selesaikan proses masuk, dan kembali untuk memeriksa otorisasi. Omni Gateway menyimpan katalog model cakupan akun yang dikembalikan oleh Codex, menyegarkan token akses OAuth saat diperlukan, dan mengirim permintaan yang kompatibel melalui transportasi Codex Responses. OpenAI Platform menggunakan autentikasi kunci API; kunci divalidasi melalui katalog model akun sebelum memasuki pool. Kedua produk mendukung impor JSON dan ZIP dengan validasi khusus penyedia dan deduplikasi.

Claude Code menggunakan alur Anthropic PKCE OAuth. Buat tautan otorisasi, selesaikan otorisasi, lalu tempelkan kode otorisasi yang dikembalikan ke halaman Providers. Claude Platform menerima kunci API Anthropic. Kedua produk menemukan model yang diekspos ke setiap kredensial, menggunakan transportasi Anthropic Messages, menyegarkan token akses Claude Code jika memungkinkan, dan mendukung impor JSON atau ZIP yang divalidasi.

Koneksi Ollama dikonfigurasi per endpoint dan dapat menyertakan kunci API pembawa (bearer) opsional untuk server yang dilindungi atau di cloud. Omni Gateway menemukan model melalui `/api/tags` dan merutekan inferensi melalui `/api/chat`. Saat Omni Gateway berjalan di Docker, `localhost` mengacu pada kontainer itu sendiri; gunakan alamat host-gateway atau endpoint Ollama lain yang dapat dijangkau jaringan.

Impor Pool dan impor massal Google Antigravity menerima arsip hingga 10 MB, paling banyak 500 file, file kredensial individual hingga 2 MB, dan paling banyak 25 MB data yang tidak dikompresi. Impor penyedia Google AI Studio, OpenAI, Anthropic, dan Ollama menggunakan batas yang lebih ketat yaitu 2 MB per file yang diimpor, 200 entri JSON, dan 5 MB data yang tidak dikompresi.

Halaman Pool juga menyediakan alur kerja pencadangan independen penyedia. `Download ZIP` mengekspor pool kredensial yang aktif, dan `Import ZIP` memulihkan arsip tersebut dengan mengidentifikasi setiap kredensial sebagai Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform, atau Ollama. Akun OAuth mempertahankan deduplikasi identitas cakupan penyedia, sementara kunci API divalidasi dan dideduplikasi oleh sidik jari (fingerprint) kunci cakupan penyedia yang tidak dapat dibalik. Entri yang tidak didukung atau salah bentuk dilaporkan secara individual tanpa memblokir kredensial yang valid dalam arsip yang sama.

Kredensial Google Antigravity menggunakan `google-antigravity-{account_fingerprint}.json`, di mana sidik jari diturunkan dari email akun yang dinormalisasi tanpa mengeksposnya. Kredensial Google AI Studio menggunakan `google-ai-studio-{key_fingerprint}.json`, kredensial Grok Build OAuth menggunakan `grok-{account_fingerprint}.json`, kredensial SpaceXAI Console menggunakan `xai-console-{key_fingerprint}.json`, kredensial Codex menggunakan `openai-codex-{account_fingerprint}.json`, kredensial OpenAI Platform menggunakan `openai-platform-{key_fingerprint}.json`, kredensial Claude Code menggunakan `claude-code-{account_fingerprint}.json`, kredensial Claude Platform menggunakan `claude-platform-{key_fingerprint}.json`, dan koneksi Ollama menggunakan `ollama-{connection_fingerprint}.json`. Kredensial lama `provider_*.json` dan `xai-grok-*.json` tetap kompatibel dan diekspor dengan nama kanonikal.

Nama mode kredensial:

- `code_assist`: pool kredensial Code Assist standar.
- `provider`: pool kredensial backend penyedia.

## Penyimpanan

Penerapan instans tunggal menggunakan penyimpanan berbasis SQLite di direktori data yang dipasang. Di Docker, pertahankan `/app/backend/data/creds` dan `/app/backend/data/logs` yang dipasang ke jalur host yang tahan lama seperti `/opt/omni-gateway/creds` dan `/opt/omni-gateway/logs`.

MongoDB atau PostgreSQL dapat menggantikan SQLite lokal untuk preferensi operasional atau pengujian migrasi:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

Redis dapat ditambahkan untuk akselerasi cache/sesi:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Penyimpanan eksternal tidak membuat runtime 1.x dapat diskalakan secara horizontal. Jalankan satu worker dan satu replika hingga reservasi kredensial terdistribusi, cooldown, pembatalan sesi, dan agregasi penggunaan diimplementasikan. Konfigurasikan salah satu antara MongoDB atau PostgreSQL, jangan keduanya; kegagalan inisialisasi database eksternal eksplisit akan menghentikan startup alih-alih secara diam-diam kembali ke SQLite.

Impor kredensial lingkungan tersedia dari panel kontrol. Tetapkan salah satu variabel berikut ke JSON mentah atau gunakan varian `_B64` yang cocok untuk JSON yang dikodekan base64:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

Muatan dapat berupa objek kredensial tunggal, larik, atau `{ "credentials": [...] }`.

## Pengembangan

Bagian ini ditujukan bagi kontributor dan debugging lokal. Penerapan produksi harus menggunakan Docker dengan volume host persisten.

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

Mulai layanan setelah pemeriksaan berhasil:

```bash
python backend/main.py
```

Garis dasar produksi adalah Python 3.12, dan CI saat ini memverifikasi Python 3.12 dan 3.14. Lihat [Berkontribusi](../../CONTRIBUTING.md) untuk alur kerja pull-request dan ekspektasi tinjauan.

## Catatan Penerapan

- Jangan pernah melakukan komit file JSON kredensial atau `.env`.
- Gunakan `API_KEY` khusus untuk integrasi klien dan `PANEL_PASSWORD` terpisah untuk akses konsol.
- Batasi akses ke volume kredensial persisten atau database eksternal dan aktifkan enkripsi tingkat platform saat istirahat (at rest); token penyedia harus tetap dapat diambil oleh router.
- Tempatkan Omni Gateway di belakang reverse proxy dengan TLS ketika dapat dijangkau di luar localhost.
- Konfigurasikan reverse proxy untuk mempertahankan `Host` dan meneruskan `X-Forwarded-Proto`; tetapkan `PANEL_COOKIE_SECURE=true` ketika terminasi HTTPS terjamin.
- Tetapkan `TRUST_PROXY_HEADERS=true` hanya jika layanan dapat dijangkau secara eksklusif melalui proxy tepercaya yang menggantikan `X-Forwarded-For` dan `X-Forwarded-Proto`.
- Gunakan `GET /health` untuk pemeriksaan keaktifan proses (liveness) dan `GET /ready` untuk pemeriksaan kesiapan sadar penyimpanan (readiness).
- Image Docker dimulai sebagai root hanya cukup lama untuk memperbaiki kepemilikan direktori data yang dipasang, kemudian menjalankan layanan sebagai pengguna `gateway` yang tidak memiliki hak istimewa.
- Tetapkan `CORS_ORIGINS` ke asal tepercaya eksplisit saat klien peramban memerlukan akses lintas-asal.
- Pastikan `/opt/omni-gateway` atau `DATA_DIR` pilihan Anda dicadangkan sebelum meningkatkan atau memindahkan server.
- Penerbitan image Docker menggunakan rahasia repositori `DOCKERHUB_USERNAME` dan `DOCKERHUB_TOKEN` untuk Docker Hub, dan `GITHUB_TOKEN` bawaan untuk GitHub Packages di `ghcr.io/nguywnben/omni-gateway`. Tetapkan variabel repositori opsional `IMAGE_NAME` hanya saat memublikasikan ke nama image Docker Hub kustom.
- Pertahankan `WORKERS=1` dan satu replika aplikasi untuk seri 1.x; penyimpanan eksternal bukan pengganti koordinasi terdistribusi.
- Gunakan rute manajemen kanonikal `/api/credentials`. Alias beta `/api/creds` telah dihapus pada 1.0.0.
- Ikuti [Meningkatkan ke 1.0](../upgrading-to-1.0.md) sebelum memigrasikan penerapan beta.
- Ikuti [panduan pembaruan](../updating.md) saat meningkatkan instans yang diterapkan atau mengembalikan (rollback) rilis.
- Ikuti [daftar periksa rilis](../release-checklist.md) yang dipelihara sebelum menandai (tag) atau mempromosikan image.
- Jaga agar kebijakan retensi log dan rotasi kredensial selaras dengan batas penggunaan Anda.
- Segera rotasi kredensial jika repositori atau pemindai platform melaporkan rahasia yang bocor.
- Render Blueprint menggunakan layanan berbayar dengan disk persisten. Layanan gratis Render menggunakan sistem file fana dan hanya cocok untuk evaluasi sekali pakai.

## Komunitas dan Kesehatan Proyek

- Baca [Berkontribusi](../../CONTRIBUTING.md) sebelum membuka pull request.
- Laporkan kerentanan melalui proses pribadi di [Kebijakan Keamanan](../../SECURITY.md).
- Tinjau [Catatan Perubahan](../../CHANGELOG.md) untuk perubahan tingkat rilis.
- Ikuti [Kode Etik](../../CODE_OF_CONDUCT.md) di semua ruang proyek.

## Ucapan Terima Kasih & Inspirasi

Omni Gateway berdiri di atas pundak komunitas perutean AI sumber terbuka, telemetri, dan gateway. Kami mengucapkan terima kasih kepada para pencipta dan pengelola proyek-proyek ini:

| Proyek | Deskripsi | Bintang |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Inspirasi untuk manajemen kunci multi-penyedia dan agregasi API berbasis web | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Memelopori proxy multi-format dan lapisan penerjemahan protokol untuk CLI AI coding | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Proxy LLM terpadu penetap standar, penyeimbangan beban, dan perutean fallback | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Arsitektur gateway AI ultra-cepat, strategi perutean, dan pola fallback tangguh | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Platform rekayasa LLM sumber terbuka, penelusuran, observabilitas, dan penyerapan metrik | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Lisensi

Omni Gateway dirilis di bawah [Lisensi MIT](../../LICENSE).
