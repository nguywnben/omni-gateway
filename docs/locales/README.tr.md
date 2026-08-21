<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Yapay Zeka Kodlama Araçları İçin Evrensel AI Yönlendirici ve Birleşik Çok Sağlayıcılı Ağ Geçidi</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20dil-orange?style=flat-square" alt="15 Dil">
  </p>

  <p>
    <a href="#desteklenen-saglayicilar"><b>🌐 Desteklenen Sağlayıcılar</b></a> •
    <a href="#temel-yetenekler"><b>⚡ Temel Yetenekler</b></a> •
    <a href="#dagitim"><b>🐳 Docker Dağıtımı</b></a> •
    <a href="#sdk-arayuzleri"><b>🔌 SDK Kurulumu</b></a> •
    <a href="../architecture.md"><b>📖 Mimari</b></a>
  </p>

  <p>
    <b>Konsol ve Dokümantasyon Dilleri:</b><br>
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
    <a href="README.th.md">ภาษาไทย</a> •
    <b>Türkçe</b>
  </p>
</div>

---

Kodlama araçları için evrensel bir yapay zeka yönlendiricisi. Omni Gateway; akıllı otomatik yük devretme (auto-fallback), belirteç (token) duyarlı istek temizleme, kullanım görünürlüğü ve kusursuz format dönüşümü sağlayarak yerel ajanların, IDE asistanlarının ve otomasyon betiklerinin tek bir kararlı API yüzeyi üzerinden ücretsiz ve premium LLM kapasitesini kullanmasına olanak tanır.

> **Proje durumu:** Kararlı. Sürüm `1.3.1`, 15 dilde yerelleştirilmiş konsolu tamamlar, yerel ayarlara duyarlı yönetim API mesajları ve sürüme duyarlı güncelleme rehberliği ekler; `1.0.0` ile oluşturulan kararlı SDK rotalarını, kurallı yönetim rotalarını, yapılandırma adlarını ve tek örnekli çalışma zamanı sözleşmesini korur.

## Neden Omni Gateway

Modern kodlama iş akışları genellikle istemcileri ve sağlayıcıları bir arada kullanır: OpenAI uyumlu araçlar, Gemini yerel SDK'ları, Anthropic tarzı ajanlar, Google destekli kimlik bilgileri ve deneysel model rotaları. Omni Gateway, bu istemciler ile model arka uçları arasında yer alır; böylece her araç zaten anladığı formatta konuşmaya devam ederken ağ geçidi yönlendirme, yeniden denemeler, istek temizleme ve yanıt normalleştirmesini üstlenir.

## <a id="temel-yetenekler"></a>Temel Yetenekler

- Akıllı otomatik yük devretme: istek başına kimlik bilgilerini rezerve eder, eşzamanlı trafiği dağıtır, adil rotasyon için her denemeyi izler ve son hataları, bekleme sürelerini (cooldown), hız sınırlarını (rate limit) ve tükenen kapasiteleri otomatik olarak atlatır.
- Belirteç duyarlı temizleme: yükleri normalleştirir ve sistem talimatlarını, araç tanımlarını ve son bağlamı korurken yalnızca aşırı büyük konuşma öneklerini güvenli tur sınırlarında kırpar.
- Format dönüştürme: OpenAI Chat Completions ve Responses, Gemini yerel istekleri ve Anthropic Messages formatlarını kabul eder; ardından istekleri ve akış yanıtlarını formatlar arasında sorunsuz şekilde dönüştürür.
- Kimlik bilgisi orkestrasyonu: OAuth hesaplarını ve sağlayıcı API anahtarlarını sağlık durumu, bekleme süresi takibi, doğrulama, tekilleştirme ve sağlayıcıya duyarlı yük devretme ile yönetir.
- Kimlik bilgisi düzeyinde model yönlendirmesi: her kimlik bilgisi için ayrı bir yetenek kataloğu tutar, böylece bir hesabın yetkisi, seçilen modeli sunmayan başka bir hesaba istek gönderemez.
- Rota sağlık belleği: kimlik bilgisi kapsamında model bulunamadı (model-not-found) yanıtlarını kaydeder ve Models sayfasından kurtarma için etkilenen rotaları gösterir.
- Akış esnekliği: SSE akışını, akış çıktısı gerektiren istemciler için sözde akışı (pseudo-streaming) ve uzun üretimler için kesilmeyi önleyici (anti-truncation) yeniden denemeleri destekler.
- Kontrol paneli: kimlik bilgileri, günlükler, yapılandırma, kullanım ve sürüm bilgileri için bir web konsolu ile birlikte gelir.

## Konsol Önizlemesi

![Omni Gateway kimlik bilgisi havuzu](../assets/screenshots/credential-pool.png)

## <a id="desteklenen-saglayicilar"></a>Desteklenen Sağlayıcılar

Omni Gateway, önde gelen yapay zeka sağlayıcıları, yerel çalışma zamanı motorları ve OAuth uç noktaları arasında istekleri sorunsuz şekilde uyarlar:

| Sağlayıcı | Kimlik Doğrulama | Desteklenen Protokoller | Otomatik Yük Devretme | Akış (Streaming) |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Uyumlu, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Uyumlu | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Yerel / Kendi Sunucunuzda)** | Yerel / Base URL | OpenAI Uyumlu | ✅ | ✅ |

## Mimari

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | IDE entegrasyonları
        |
        v
Omni Gateway
  kimlik doğrulama -> format dönüştürme -> belirteç duyarlı temizleme -> yönlendirme -> yük devretme -> akış
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

Genel API kararlı kalırken sağlayıcıya özel adaptörler Omni Gateway arkasında gelişmeye devam eder.

## Depo Yapısı

```text
backend/       FastAPI bileşim kökü, yönlendirme çekirdeği, dönüştürücüler, depolama ve testler
frontend/      Yönetim konsolu işaretlemesi, stilleri, betikleri ve sağlayıcı varlıkları
deploy/        Konteyner tanımları, platform bildirimleri ve işletim sistemi betikleri
docs/          Mimari notları ve bakımı yapılan proje belgeleri
.github/       CI, bağımlılık otomasyonu ve katkı şablonları
```

Modül sınırları, istek akışı, durum sahipliği ve mevcut sürüm kısıtlamaları için [Mimari](../architecture.md) belgesine bakın.

## <a id="dagitim"></a>Dağıtım

Omni Gateway gerçek dağıtımlar için tasarlanmıştır. Docker, ana makinede kimlik bilgilerini ve günlükleri korurken çalışma zamanını yalıttığı için VPS ve sunucu ortamları için önerilen yoldur.

### VPS Üzerinde Docker

Önce kalıcı ana makine dizinlerini oluşturun:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Hizmeti başlatın:

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

Aynı sürüm GitHub Packages üzerinde `ghcr.io/nguywnben/omni-gateway:1.3.1` olarak da yayınlanır. `latest` etiketi en yeni kararlı sürümü izler; `edge`, `main` dalındaki doğrulanmış ancak yayınlanmamış derlemeleri izler. Tekrarlanabilir dağıtım önemli olduğunda belirli bir sürüm etiketini veya özetini (digest) sabitleyin.

Kontrol panelini şu adresten açın:

```text
http://SUNUCU_IP_ADRESINIZ:4283
```

İlk çalıştırmada, kurulum ekranında konsol şifresini oluşturun. Varsayılan bir şifre tanımlı gelmez. Uzak bir tarayıcı, `docker logs omni-gateway` tarafından yazdırılan bootstrap belirtecini de girmelidir; doğrudan localhost kurulumu bunu gerektirmez. Dağıtım otomasyonu kararlı bir bootstrap belirteci gerektirdiğinde başlatmadan önce `SETUP_TOKEN` değişkenini ayarlayın.

Uygulama tarafından yönetilen şifreler tuzlanmış scrypt karmaları (salted hashes) olarak saklanır, kontrol paneli oturumları HttpOnly çerezleri kullanır ve genel SDK istekleri oluşturulan `sk-ogw-` API anahtarıyla kimlik doğrulaması yapar. Etkileşimsiz bir dağıtım için `PANEL_PASSWORD` değişkenini önceden yapılandırın ve kurulum ekranını tamamen atlayın.

`1.3.1` konteyneri `linux/amd64` için yayınlanmıştır. Vertex aktarım yığını dahil tüm sağlayıcı bağımlılıkları aynı sözleşmeyle derlenip test edilene kadar ARM64 yayını kasıtlı olarak duraklatılmıştır.

Sunucu güvenlik duvarı etkinse ağ geçidi bağlantı noktasına izin verin:

```bash
sudo ufw allow 4283/tcp
```

Günlükleri görüntüleyin:

```bash
sudo docker logs -f omni-gateway
```

En yeni kararlı imaja güncelleyin:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Ardından konteyneri yukarıdaki aynı `docker run` komutuyla tekrar başlatın. Bağlanan `/opt/omni-gateway` dizinleri; kimlik bilgilerini, yapılandırmayı, kullanım verilerini ve günlükleri konteyner güncellemeleri boyunca korur.

### Docker Compose

Depo tabanlı dağıtımlar için:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

Birlikte gelen compose dosyası `nguywnben/omni-gateway:latest` imajını çeker ve kalıcı ana makine verileri için varsayılan olarak `/opt/omni-gateway` kullanır. Bu sürümü sabitlemek için `IMAGE=nguywnben/omni-gateway:1.3.1` olarak ayarlayın ve sunucu farklı bir depolama konumu kullandığında `DATA_DIR=/ozel/yol` olarak ayarlayın.

Compose; `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, harici depolama URI'leri ve `PROXY` değişkenlerini kabuktan veya kök dizindeki `.env` dosyasından iletir. Otomatik anahtar oluşturma, ilk çalıştırma kurulumu, yerel SQLite depolaması ve doğrudan giden ağ bağlantısını korumak için bunları boş bırakın.

### Yerel Geliştirme

Ağ geçidini yerel ortamda geliştirirken veya hata ayıklarken Python iş akışını kullanın:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Windows PowerShell üzerinde:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Kontrol panelini şu adresten açın:

```text
http://127.0.0.1:4283
```

Yerel geliştirme, Docker dağıtımıyla aynı ilk çalıştırma kurulum ekranını kullanır.

## Yapılandırma

Omni Gateway, yapılandırmayı önce ortam değişkenlerinden, ardından kaydedilmiş yapılandırmadan ve son olarak varsayılan değerlerden okur.

| Değişken | Varsayılan | Amaç |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Bağlanma adresi (bind address). |
| `PORT` | `4283` | HTTP bağlantı noktası. |
| `HOST_PORT` | `4283` | Yalnızca Docker Compose tarafından kullanılan ana makine tarafı bağlantı noktası. |
| `WORKERS` | `1` | 1.x serisi için desteklenen çalışan sayısı. Rezervasyonlar, bekleme süreleri, oturumlar ve kullanım toplama süreçler arasında koordine edilene kadar diğer değerler reddedilir. |
| `CORS_ORIGINS` | boş | API'yi kaynaklar arası (cross-origin) çağırmasına izin verilen virgülle ayrılmış tarayıcı kaynakları. Aynı kaynak konsol kullanımı için boş bırakın. |
| `CORS_ORIGIN_REGEX` | boş | Yönetilen dinamik tarayıcı kaynakları için isteğe bağlı regex. |
| `API_KEY` | otomatik üretilir | Genel istemci API istekleri için tercih edilen anahtar. `sk-ogw-` ile başlamalıdır. |
| `PANEL_PASSWORD` | kuruluma kadar boş | Web kontrol paneli şifresi. |
| `SETUP_TOKEN` | süreç başına üretilir | Uzaktan ilk çalıştırma kurulumu için gerekli isteğe bağlı sabit bootstrap belirteci. Atlandığında, oluşturulan belirteci uygulama veya konteyner günlüklerinden okuyun. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Saniye cinsinden web konsolu oturum ömrü. |
| `PANEL_COOKIE_SECURE` | otomatik | Yalnızca HTTPS panel çerezleri gerektirmek için `true` yapın. HTTPS'yi `X-Forwarded-Proto` üzerinden algılamak için boş bırakın. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Saniye cinsinden giriş hız sınırlama penceresi. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Hız sınırlama penceresi içinde istemci başına izin verilen maksimum başarısız giriş denemesi. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Bellek içi giriş sınırlayıcısı tarafından tutulan maksimum istemci adresi. |
| `MAX_REQUEST_BODY_MB` | `64` | MiB cinsinden maksimum HTTP istek gövdesi boyutu. Aşırı büyük SDK istekleri yerel protokol hata zarfını döndürür. |
| `TRUST_PROXY_HEADERS` | `false` | İstemci/protokol yönlendirme başlıklarını yalnızca bunların üzerine yazan güvenilir bir ters proxy'den kabul edin. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Kimlik bilgisi depolama dizini. Docker'da `/app/backend/data/creds` dizinini bir ana makine birimiyle kalıcı hale getirin. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist arka uç uç noktası. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Google Antigravity arka uç uç noktası. |
| `PROXY` | boş | İsteğe bağlı HTTP, HTTPS veya SOCKS proxy. |
| `RETRY_429_ENABLED` | `true` | Hız sınırları ve geçici yukarı akış (upstream) hataları için sınırlı yeniden denemeleri etkinleştirin. Eski ad yapılandırma uyumluluğu için korunmuştur. |
| `RETRY_429_MAX_RETRIES` | `5` | Geçici yukarı akış hataları için maksimum yeniden deneme sayısı. |
| `RETRY_429_INTERVAL` | `1` | Saniye cinsinden geçici yeniden denemeler arasındaki temel gecikme. |
| `AUTO_DISABLE` | `false` | Yapılandırılmış kritik hatalardan (hard failures) sonra kimlik bilgilerini devre dışı bırakın. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Virgülle ayrılmış kritik hata durum kodları. |
| `ROUTING_STRATEGY` | `balanced` | Kimlik bilgisi seçim politikası: `balanced` (dengeli) veya `priority` (öncelikli). |
| `PREFERRED_PROVIDER` | boş | `priority` stratejisi tarafından tercih edilen sağlayıcı, örneğin `google_antigravity` veya `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Sağlayıcı çıkarım zaman aşımı, 5 ile 900 saniye arasında sınırlandırılmıştır. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Kesilmeyi önleyici akış için maksimum devam denemesi. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Sağlayıcı yönlendirmesinden önce aşırı büyük konuşma geçmişini sıkıştırın. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Sıkıştırmayı etkinleştiren tahmini giriş belirteci eşiği. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Sıkıştırma sonrası tahmini hedef giriş belirteci sayısı. Eşikten düşük olmalıdır. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Sıkıştırma sırasında korunan minimum son kullanıcı konuşma turu sayısı. |
| `COMPATIBILITY_MODE` | `false` | Sistem mesajlarını reddeden istemciler/modeller için dönüştürür. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Mevcut olduğunda model akıl yürütme (reasoning) alanlarını dahil edin. |
| `MONGODB_URI` | boş | Ayarlandığında MongoDB depolamasını etkinleştirir. |
| `POSTGRESQL_URI` | boş | Ayarlandığında PostgreSQL depolamasını etkinleştirir. |
| `REDIS_URL` | boş | Ayarlandığında Redis destekli önbellekleri/oturum durumunu etkinleştirir. |
| `CODE_ASSIST_CLIENT_ID` | yerleşik masaüstü istemcisi | Code Assist OAuth Client ID için isteğe bağlı geçersiz kılma. |
| `CODE_ASSIST_CLIENT_SECRET` | yerleşik masaüstü istemcisi | Code Assist OAuth Client Secret için isteğe bağlı geçersiz kılma. |
| `ANTIGRAVITY_CLIENT_ID` | yerleşik masaüstü istemcisi | Google Antigravity OAuth Client ID için isteğe bağlı geçersiz kılma. Providers sayfasından da yönetilebilir. |
| `ANTIGRAVITY_CLIENT_SECRET` | yerleşik masaüstü istemcisi | Google Antigravity OAuth Client Secret için isteğe bağlı geçersiz kılma. Yukarı akış istemcisi değiştiğinde ortam değişkeni veya Providers sayfası üzerinden yapılandırın. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Google AI Studio Generative Language API uç noktası için isteğe bağlı geçersiz kılma. |
| `XAI_API_URL` | `https://api.x.ai/v1` | API anahtarı kimlik bilgileri için SpaceXAI Console API uç noktası geçersiz kılması. Providers sayfasından da yönetilebilir. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Grok Build OAuth abonelik uç noktası için isteğe bağlı geçersiz kılma. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Grok Build OAuth sağlayıcısı (issuer) için isteğe bağlı geçersiz kılma. Konsol tarafından yalnızca `x.ai` altındaki HTTPS ana makineleri kabul edilir. |
| `XAI_CLIENT_ID` | yerleşik genel istemci | Grok Build PKCE OAuth Client ID için isteğe bağlı geçersiz kılma. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Grok Build OAuth ve SpaceXAI Console API istekleri için paylaşılan ortak HTTP User-Agent geçersiz kılması. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | OpenAI Platform API uç noktası için isteğe bağlı geçersiz kılma. Providers sayfasından da yönetilebilir. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Codex çıkarım ve hesap-model uç noktası için isteğe bağlı geçersiz kılma. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Codex hesap hız sınırı uç noktası için isteğe bağlı geçersiz kılma. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Codex cihaz yetkilendirme hizmeti için isteğe bağlı geçersiz kılma. |
| `CODEX_CLIENT_ID` | yerleşik genel istemci | Codex cihazı OAuth Client ID için isteğe bağlı geçersiz kılma. |
| `CODEX_USER_AGENT` | Codex CLI uyumlu değer | Codex istekleri için isteğe bağlı User-Agent geçersiz kılması. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Claude Platform ve Claude Code Messages API uç noktası için isteğe bağlı geçersiz kılma. Providers sayfasından da yönetilebilir. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Claude Code PKCE yetkilendirme uç noktası için isteğe bağlı geçersiz kılma. Konsol tarafından yalnızca Anthropic ve Claude ana makineleri kabul edilir. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Claude Code belirteç uç noktası için isteğe bağlı geçersiz kılma. Konsol tarafından yalnızca Anthropic ve Claude ana makineleri kabul edilir. |
| `CLAUDE_CLIENT_ID` | yerleşik genel istemci | Claude Code PKCE OAuth Client ID için isteğe bağlı geçersiz kılma. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Claude Code ve Claude Platform istekleri için isteğe bağlı User-Agent geçersiz kılması. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Google Antigravity protokolü User-Agent geçersiz kılması. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Google Antigravity yük düzeyi userAgent geçersiz kılması. |
| `LOG_LEVEL` | `info` | Çalışma zamanı günlük seviyesi. |
| `LOG_MAX_MB` | `10` | Döndürmeden (rotation) önceki maksimum aktif günlük dosyası boyutu. |
| `LOG_BACKUP_COUNT` | `3` | Saklanan döndürülmüş günlük dosyası sayısı. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Dosya günlüğü hedefi. Docker'da `/app/backend/data/logs` dizinini bir ana makine birimiyle kalıcı hale getirin. |

## <a id="sdk-arayuzleri"></a>SDK Yüzeyleri

Omni Gateway, resmi Python SDK'larının standart URL davranışı etrafında tasarlanmıştır. Her istemciyi tam olarak aşağıda gösterildiği gibi yapılandırın; ağ geçidi standart olmayan yinelenen yol önekleri gerektirmez.

Örnekler sanal model `omway` kullanır. Önce Models sayfasında sıralı sağlayıcı-model yük devretmesini yapılandırın veya somut bir model kimliğiyle değiştirin.

### OpenAI Python SDK

OpenAI temel URL'si olarak `/v1` kullanın. SDK sonuna `/chat/completions` ekler.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Bu depoyu bir paragrafta açıklayın."}],
)
```

Aynı istemci OpenAI Responses API'sini de kullanabilir:

```python
response = client.responses.create(
    model="omway",
    instructions="Kısa ve öz olun.",
    input="Bu depoyu bir paragrafta açıklayın.",
)

print(response.output_text)
```

Responses uyumluluğu; metin, görüntü girişleri, akışsız fonksiyon araçları (non-streaming function tools) ve SSE metin akışını destekler. OpenAI tarafından barındırılan yerleşik araçlar, saklanan yanıt geçmişi ve akışlı fonksiyon çağrıları açıkça reddedilir; çünkü Omni Gateway bu OpenAI'ye özgü davranışları yürütmez, kalıcı kılmaz veya sessizce göz ardı etmez.

### Anthropic Python SDK

Anthropic temel URL'si olarak ağ geçidi kaynağını (origin) kullanın. SDK sonuna `/v1/messages` ekler.

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Kısa bir commit mesajı taslağı hazırlayın."}],
)
```

### Google GenAI Python SDK

Google GenAI temel URL'si olarak ağ geçidi kaynağını kullanın. SDK varsayılan model rotasını ekler, örneğin `/v1beta/models/{model}:generateContent`.

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
    contents="Küçük bir Python fonksiyonu yazın.",
    config=types.GenerateContentConfig(
        system_instruction="Yardımsever bir asistansınız.",
    ),
)
```

### Desteklenen Rotalar

Omni Gateway, ürün ad alanı olmadan SDK uyumlu rotalar sunar:

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

Kimlik doğrulama, istek doğrulama, yönlendirme, yukarı akış ve akış öncesi hatalar, seçilen SDK yüzeyi için yerel hata zarfını kullanır. Her HTTP yanıtı `X-Request-ID` içerir; istemciler uçtan uca ilişkilendirme için bu başlıkta güvenli bir tanımlayıcı sağlayabilir. Hız sınırlı ve geçici olarak kullanılamayan yanıtlar, yukarı akış sağladığında `Retry-After` başlığını korur.

## Model Özellikleri

Models sayfası, etkin sağlayıcı kimlik bilgileri genelinde keşfedilen modellerden sanal `omway` modelini oluşturur. Üyelerini bir kez öncelik sırasına göre düzenleyin, ardından desteklenen herhangi bir SDK'dan `omway` kullanın. Omni Gateway, ilk modeli destekleyen sağlıklı kimlik bilgilerini dengeler ve bu model kullanılamadığında yapılandırılmış model sırası üzerinden devam eder. Belirli sağlayıcı model kimlikleri, deterministik model seçimine ihtiyaç duyan istemciler için kullanılabilir olmaya devam eder. Boş bir seçimi kaydetmek, sağlayıcı kimlik bilgilerini etkilemeden `omway` modelini devre dışı bırakır.

Model keşfi sağlayıcıya duyarlıdır: paylaşılan bir model birden fazla sağlayıcı tarafından desteklenebilirken, sağlayıcıya özgü modeller yalnızca uyumlu kimlik bilgilerini kullanır. Doğrulanan her kimlik bilgisi kendi sağlayıcı kataloğunu saklar ve yönlendirici, bildirilen kimlik bilgisi desteğine genel sağlayıcı çıkarımına göre öncelik verir. Kataloğu yenilemek, mevcut sağlayıcı kullanılabilirliğini yeniden kontrol eder; kullanılamayan seçimler geri yüklenene veya kaldırılana kadar yapılandırmada görünür kalır.

Bir yukarı akış somut bir model için `404` döndürdüğünde Omni Gateway, tüm sağlayıcıyı devre dışı bırakmak yerine söz konusu kimlik bilgisi ve model için kullanılamayan bir rota kaydeder. Rota hemen geçici olarak atlatılır ve kaldırılana veya kimlik bilgisi yeniden doğrulanana kadar **Unavailable Model Routes** altında görünür kalır. Bu, bir hesabın aboneliğinin veya bölgesel yetkisinin aynı sağlayıcıdaki diğer hesapları etkilemesini önler. Etkinleştirilmiş hiçbir kimlik bilgisi istenen somut model için destek bildirmez veya çıkaramazsa ağ geçidi, isteği rastgele bir sağlayıcıya göndermek yerine net bir uyumlu kimlik bilgisi yok hatası döndürür.

Omni Gateway, model adlarındaki özellik öneklerini ve soneklerini tanır:

- SSE çıktısı gerektiren istemciler için `fake-streaming/{model}` veya yapılandırılmış sözde akış öneki.
- Uzun biçimli akış kurtarma için `streaming-anti-truncation/{model}` veya yapılandırılmış kesilmeyi önleme öneki.
- Desteklenen Gemini ailesi modelleri için `-high`, `-medium`, `-low`, `-minimal` ve `-max` gibi düşünme (thinking) sonekleri.
- Google Search doğrulaması (grounding) destekleyen modeller için `-search` gibi arama sonekleri.

Sağlayıcı adaptörleri, yukarı akış isteklerini göndermeden önce bu özellik adlarını normalleştirir.

## Kullanım ve Maliyet Görünürlüğü

Omni Gateway; her pano zaman aralığı için istek hacmini, başarı oranını, kimlik bilgisi ilişkilendirmesini, sağlayıcı tarafından bildirilen belirteç kullanımını ve bağlam sıkıştırmasıyla kaldırılan tahmini belirteçleri kaydeder. Sağlayıcı belirteçleyicileri (tokenizers) ve faturalandırma kuralları nihai otorite olmaya devam ettiğinden sıkıştırma tasarrufları tahmin olarak etiketlenir. Sağlayıcı fiyat tabanlı yönlendirme, daha fazla sağlayıcı eklendikçe çekirdek API'nin kararlı kalması amacıyla gelecekteki bir politika katmanı olarak bırakılmıştır.

## Kimlik Bilgisi İş Akışı

1. Omni Gateway'i başlatın.
2. VPS üzerinde `http://SUNUCU_IP_ADRESINIZ:4283` veya yerel geliştirme için `http://127.0.0.1:4283` adresini açın.
3. İlk çalıştırma kurulum ekranında konsol şifresini oluşturun. Uzaktan kurulum için uygulama günlüklerindeki bootstrap belirtecini girin; alternatif olarak `PANEL_PASSWORD` değişkenini önceden yapılandırın.
4. Providers sayfasından bir hesap, API anahtarı veya Ollama bağlantısı ekleyin.
5. Kimlik bilgilerini doğrulayın ve paneldeki bekleme süresi/hata durumunu izleyin.
6. Kodlama aracınızı yukarıdaki API yüzeylerinden birine yönlendirin.

Bir Google Antigravity kimlik bilgisi eklerken, oturum açtıktan sonra Google tarayıcıyı `http://localhost:4283/callback` adresine yönlendirir. Yerel bir makinede Omni Gateway bir OAuth başarı sayfası gösterir. Bir VPS'de bu `localhost` adresi kullanıcının tarayıcı makinesine ait olduğundan sayfa yüklenmeyebilir; tarayıcı adres çubuğundaki tam URL'yi kopyalayın, Providers sayfasına dönün, `Callback URL` alanına yapıştırın ve `Save credential` butonuna tıklayın.

Google AI Studio, OAuth yerine API anahtarı kimlik doğrulaması kullanır. Providers sayfasından bir anahtar ekleyin; Omni Gateway bunu Google'ın model kataloğuna karşı doğrular, bir sağlayıcı kimlik bilgisi olarak saklar ve uyumlu Gemini veya Gemma isteklerini bu anahtar üzerinden yönlendirir. Akıllı yönlendirici, paylaşılan Gemini modelleri için AI Studio ile Google Antigravity arasında yük devretme yapabilirken sağlayıcıya özgü modelleri uyumlu kimlik bilgilerinde tutar.

Google AI Studio toplu içe aktarma, JSON dosyalarını ve JSON dosyaları içeren ZIP arşivlerini kabul eder. Bir JSON belgesi tek bir anahtar, bir `api_keys` dizisi veya anahtar nesneleri dizisi içerebilir:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

İçe aktarılan her anahtar saklanmadan önce doğrulanır. Aynı içe aktarma içindeki yinelenen anahtarlar atlanır, mevcut anahtarlar yeniden doğrulanır ve güncellenir; geçersiz girişler anahtar değeri açığa çıkarılmadan raporlanır.

Grok Build, PKCE OAuth kimlik bilgilerini desteklerken SpaceXAI Console, API anahtarlarını destekler. SpaceXAI Console anahtarları saklanmadan önce Grok Build model kataloğuna karşı doğrulanır. Grok Build OAuth için Omni Gateway bir yetkilendirme bağlantısı oluşturur; yetkilendirmeden sonra Grok Build yetkilendirme sayfasında görüntülenen kodu kopyalayın ve Grok Build OAuth formuna yapıştırın. Erişim belirteçleri bir yenileme belirteci (refresh token) mevcut olduğunda otomatik olarak yenilenir ve her iki kimlik bilgisi türü de yalnızca mevcut katalogları tarafından bildirilen Grok Build modellerini sunar. Pool sayfası, Grok Build OAuth hesapları için aylık kredi kullanımını ve xAI sağladığında haftalık kullanımı alabilir. Bu hesap düzeyinde faturalandırma görünümü SpaceXAI Console API anahtarları için kullanılamaz.

Codex, OpenAI'nin cihaz yetkilendirme akışını kullanır. Providers sayfasından bir cihaz kodu oluşturun, görüntülenen doğrulama URL'sini açın, kodu girin, oturum açmayı tamamlayın ve yetkilendirmeyi kontrol etmek için geri dönün. Omni Gateway, Codex tarafından döndürülen hesap kapsamlı model kataloğunu saklar, gerektiğinde OAuth erişim belirteçlerini yeniler ve uyumlu istekleri Codex Responses aktarımı üzerinden gönderir. OpenAI Platform, API anahtarı kimlik doğrulaması kullanır; anahtarlar havuza girmeden önce hesap model kataloğu üzerinden doğrulanır. Her iki ürün de sağlayıcıya özel doğrulama ve tekilleştirme ile JSON ve ZIP içe aktarmayı destekler.

Claude Code, Anthropic'in PKCE OAuth akışını kullanır. Bir yetkilendirme bağlantısı oluşturun, yetkilendirmeyi tamamlayın, ardından döndürülen yetkilendirme kodunu Providers sayfasına yapıştırın. Claude Platform, Anthropic API anahtarlarını kabul eder. Her iki ürün de her kimlik bilgisine sunulan modelleri keşfeder, Anthropic Messages aktarımını kullanır, mümkün olduğunda Claude Code erişim belirteçlerini yeniler ve doğrulanmış JSON veya ZIP içe aktarmayı destekler.

Ollama bağlantıları uç nokta başına yapılandırılır ve korumalı veya bulut sunucuları için isteğe bağlı bir bearer API anahtarı içerebilir. Omni Gateway modelleri `/api/tags` üzerinden keşfeder ve çıkarımı `/api/chat` üzerinden yönlendirir. Omni Gateway Docker'da çalıştığında `localhost` konteynerin kendisini ifade eder; bir host-gateway adresi veya ağ üzerinden erişilebilen başka bir Ollama uç noktası kullanın.

Pool içe aktarmaları ve Google Antigravity toplu içe aktarmaları 10 MB'a kadar arşivleri, en fazla 500 dosyayı, 2 MB'a kadar bireysel kimlik bilgisi dosyalarını ve en fazla 25 MB sıkıştırılmamış veriyi kabul eder. Google AI Studio, OpenAI, Anthropic ve Ollama sağlayıcı içe aktarmaları içe aktarılan dosya başına 2 MB, 200 JSON girişi ve 5 MB sıkıştırılmamış veri gibi daha katı sınırlar kullanır.

Pool sayfası ayrıca sağlayıcıdan bağımsız bir yedekleme iş akışı sunar. `Download ZIP` aktif kimlik bilgisi havuzunu dışa aktarır ve `Import ZIP`, her kimlik bilgisini Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform veya Ollama olarak tanımlayarak bu arşivi geri yükler. OAuth hesapları sağlayıcı kapsamlı kimlik tekilleştirmesini korurken API anahtarları sağlayıcı kapsamlı, geri döndürülemez bir anahtar parmak iziyle (fingerprint) doğrulanır ve tekilleştirilir. Desteklenmeyen veya hatalı biçimlendirilmiş girişler, aynı arşivdeki geçerli kimlik bilgilerini engellemeden tek tek raporlanır.

Google Antigravity kimlik bilgileri `google-antigravity-{account_fingerprint}.json` kullanır; burada parmak izi, açığa çıkarılmadan normalleştirilmiş hesap e-postasından türetilir. Google AI Studio kimlik bilgileri `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth kimlik bilgileri `grok-{account_fingerprint}.json`, SpaceXAI Console kimlik bilgileri `xai-console-{key_fingerprint}.json`, Codex kimlik bilgileri `openai-codex-{account_fingerprint}.json`, OpenAI Platform kimlik bilgileri `openai-platform-{key_fingerprint}.json`, Claude Code kimlik bilgileri `claude-code-{account_fingerprint}.json`, Claude Platform kimlik bilgileri `claude-platform-{key_fingerprint}.json` ve Ollama bağlantıları `ollama-{connection_fingerprint}.json` kullanır. Eski `provider_*.json` ve `xai-grok-*.json` kimlik bilgileri uyumlu kalmaya devam eder ve kurallı adlarla dışa aktarılır.

Kimlik bilgisi modu adları:

- `code_assist`: standart Code Assist kimlik bilgisi havuzu.
- `provider`: sağlayıcı arka uç kimlik bilgisi havuzu.

## Depolama

Tek örnekli dağıtımlar, bağlı veri dizininde SQLite destekli depolama kullanır. Docker'da `/app/backend/data/creds` ve `/app/backend/data/logs` dizinlerini `/opt/omni-gateway/creds` ve `/opt/omni-gateway/logs` gibi dayanıklı ana makine yollarına bağlı tutun.

Operasyonel tercih veya geçiş testi için MongoDB veya PostgreSQL yerel SQLite'ın yerini alabilir:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

Önbellek/oturum hızlandırması için Redis eklenebilir:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Harici depolama, 1.x çalışma zamanını yatay olarak ölçeklenebilir yapmaz. Dağıtılmış kimlik bilgisi rezervasyonları, bekleme süreleri, oturum geçersiz kılma ve kullanım toplama uygulanana kadar tek bir çalışan ve tek bir kopya (replica) çalıştırın. MongoDB veya PostgreSQL'den yalnızca birini yapılandırın, ikisini birden değil; açık bir harici veritabanı başlatma hatası, sessizce SQLite'a geri dönmek yerine başlatmayı durdurur.

Ortam kimlik bilgisi içe aktarma özelliği kontrol panelinden kullanılabilir. Aşağıdaki değişkenlerden birini ham JSON olarak ayarlayın veya base64 kodlu JSON için eşleşen `_B64` varyantını kullanın:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

Yük; tek bir kimlik bilgisi nesnesi, bir dizi veya `{ "credentials": [...] }` olabilir.

## Geliştirme

Bu bölüm katkıda bulunanlar ve yerel hata ayıklama içindir. Üretim dağıtımları kalıcı ana makine birimleriyle Docker kullanmalıdır.

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

Kontroller geçtikten sonra hizmeti başlatın:

```bash
python backend/main.py
```

Üretim temeli Python 3.12'dir ve CI şu anda Python 3.12 ve 3.14'ü doğrulamaktadır. Pull request iş akışı ve inceleme beklentileri için [Katkıda Bulunma](../../CONTRIBUTING.md) belgesine bakın.

## Dağıtım Notları

- Kimlik bilgisi JSON dosyalarını veya `.env` dosyasını asla commit etmeyin.
- İstemci entegrasyonları için özel bir `API_KEY` ve konsol erişimi için ayrı bir `PANEL_PASSWORD` kullanın.
- Kalıcı kimlik bilgisi birimine veya harici veritabanına erişimi kısıtlayın ve platform düzeyinde beklemede şifrelemeyi (encryption at rest) etkinleştirin; sağlayıcı belirteçleri yönlendirici tarafından alınabilir kalmalıdır.
- Localhost dışından erişilebildiğinde Omni Gateway'i TLS özellikli bir ters proxy'nin arkasına yerleştirin.
- Ters proxy'yi `Host` başlığını koruyacak ve `X-Forwarded-Proto` başlığını iletecek şekilde yapılandırın; HTTPS sonlandırması garanti edildiğinde `PANEL_COOKIE_SECURE=true` ayarlayın.
- `TRUST_PROXY_HEADERS=true` ayarını yalnızca hizmete `X-Forwarded-For` ve `X-Forwarded-Proto` başlıklarının üzerine yazan güvenilir bir proxy aracılığıyla erişildiğinde etkinleştirin.
- Süreç canlılığı için `GET /health` ve depolamaya duyarlı hazırlık kontrolleri için `GET /ready` kullanın.
- Docker imajı, yalnızca bağlı veri dizini sahipliğini onaracak kadar kök (root) kullanıcı olarak başlar, ardından hizmeti ayrıcalıksız `gateway` kullanıcısı olarak çalıştırır.
- Tarayıcı istemcileri kaynaklar arası erişime ihtiyaç duyduğunda `CORS_ORIGINS` değişkenini açıkça güvenilir kaynaklara ayarlayın.
- Sunucuları yükseltmeden veya taşımadan önce `/opt/omni-gateway` veya seçtiğiniz `DATA_DIR` dizinini mutlaka yedekleyin.
- Docker imaj yayını; Docker Hub için `DOCKERHUB_USERNAME` ve `DOCKERHUB_TOKEN` depo sırlarını, `ghcr.io/nguywnben/omni-gateway` adresindeki GitHub Packages için yerleşik `GITHUB_TOKEN` kullanır. İsteğe bağlı `IMAGE_NAME` depo değişkenini yalnızca özel bir Docker Hub imaj adına yayınlarken ayarlayın.
- 1.x serisi için `WORKERS=1` ve tek bir uygulama kopyası tutun; harici depolama dağıtılmış koordinasyonun yerine geçmez.
- Kurallı `/api/credentials` yönetim rotalarını kullanın. Beta `/api/creds` takma adları 1.0.0 sürümünde kaldırılmıştır.
- Bir beta dağıtımını taşımadan önce [1.0'a Yükseltme](../upgrading-to-1.0.md) kılavuzunu izleyin.
- Dağıtılmış bir örneği yükseltirken veya bir sürümü geri alırken [güncelleme kılavuzunu](../updating.md) izleyin.
- Bir imajı etiketlemeden veya yükseltmeden önce bakımı yapılan [sürüm kontrol listesini](../release-checklist.md) izleyin.
- Günlük saklama ve kimlik bilgisi rotasyon politikalarını kullanım sınırlarınızla uyumlu tutun.
- Bir depo veya platform tarayıcısı sızdırılmış bir sır bildirirse kimlik bilgilerini derhal değiştirin.
- Render Blueprint, kalıcı diske sahip ücretli bir hizmet kullanır. Render ücretsiz hizmetleri geçici dosya sistemleri kullanır ve yalnızca tek kullanımlık değerlendirmeler için uygundur.

## Topluluk ve Proje Sağlığı

- Bir pull request açmadan önce [Katkıda Bulunma](../../CONTRIBUTING.md) kılavuzunu okuyun.
- Güvenlik açıklarını [Güvenlik Politikası](../../SECURITY.md) içindeki özel süreç aracılığıyla bildirin.
- Sürüm düzeyindeki değişiklikler için [Değişiklik Günlüğü](../../CHANGELOG.md) belgesini inceleyin.
- Tüm proje alanlarında [Davranış Kuralları](../../CODE_OF_CONDUCT.md) ilkelerine uyun.

## Teşekkürler & İlham Kaynakları

Omni Gateway, açık kaynaklı yapay zeka yönlendirme, telemetri ve ağ geçidi topluluğunun omuzlarında yükselmektedir. Bu projelerin yaratıcılarına ve yöneticilerine şükranlarımızı sunarız:

| Proje | Açıklama | Yıldız |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Çok sağlayıcılı anahtar yönetimi ve web tabanlı API toplama ilhamı | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | AI kodlama CLI'ları için öncü çok formatlı proxy ve protokol dönüştürme katmanı | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Standart belirleyen birleşik LLM proxy'si, yük dengeleme ve yük devretme yönlendirmesi | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Ultra hızlı AI ağ geçidi mimarisi, yönlendirme stratejileri ve dayanıklı yük devretme kalıpları | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Açık kaynaklı LLM mühendislik platformu, izleme (tracing), gözlemlenebilirlik ve metrik alımı | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Lisans

Omni Gateway, [MIT Lisansı](../../LICENSE) altında yayınlanmıştır.
