# Omni Gateway

<p align="center">
  <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
  <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
  <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
  <img src="https://img.shields.io/badge/i18n-15%20ng%C3%B4n%20ng%E1%BB%AF-orange?style=flat-square" alt="15 Ngôn ngữ">
</p>

<p align="center">
  <a href="#nha-cung-cap-ho-tro"><b>🌐 Nhà cung cấp</b></a> •
  <a href="#tinh-nang-chinh"><b>⚡ Tính năng</b></a> •
  <a href="#trien-khai"><b>🐳 Triển khai Docker</b></a> •
  <a href="#tich-hop-sdk"><b>🔌 Tích hợp SDK</b></a> •
  <a href="../../docs/architecture.md"><b>📖 Kiến trúc</b></a>
</p>

<p align="center">
  <a href="../../README.md">English</a> •
  <b>Tiếng Việt</b> •
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
  <a href="README.tr.md">Türkçe</a>
</p>

---

Một router AI vạn năng dành cho các công cụ lập trình (coding tools). Omni Gateway cung cấp khả năng tự động chuyển đổi dự phòng thông minh (auto-fallback), dọn dẹp ngữ cảnh thông minh theo token, minh bạch hóa mức độ sử dụng và chuyển đổi định dạng giao thức liền mạch — giúp các AI agent cục bộ, trợ lý IDE và script tự động hóa tận dụng tối đa năng lực LLM miễn phí lẫn trả phí thông qua một giao diện API duy nhất.

> **Trạng thái dự án:** Ổn định. Phiên bản `1.3.1` hoàn thiện console đa ngôn ngữ trên 15 thứ tiếng, hỗ trợ thông báo quản lý nhận biết ngôn ngữ và hướng dẫn cập nhật mượt mà.

## Tại sao nên dùng Omni Gateway

Quy trình lập trình hiện đại thường kết hợp nhiều client và provider: công cụ chuẩn OpenAI, SDK Gemini native, agent theo định dạng Anthropic, tài khoản Google và các định tuyến mô hình thử nghiệm. Omni Gateway đứng ở giữa, cho phép mỗi công cụ tiếp tục giao tiếp theo đúng định dạng vốn có, trong khi gateway tự động đảm nhận việc điều phối tải, thử lại, tối ưu ngữ cảnh và chuẩn hóa phản hồi.

## Tính năng chính

- **Chuyển đổi dự phòng thông minh (Auto-fallback):** Đặt chỗ trước thông tin xác thực cho từng request, phân phối lưu lượng đồng thời, ghi nhận lượt dùng để xoay vòng công bằng và tự né các lỗi tạm thời, thời gian chờ (cooldown), giới hạn tần suất (rate limits) hoặc tài khoản cạn hạn mức.
- **Tối ưu hóa token:** Chuẩn hóa payload và chỉ cắt tỉa các lượt hội thoại quá dài ở ranh giới an toàn, giữ nguyên toàn bộ system prompt, định nghĩa tool và ngữ cảnh gần nhất.
- **Chuyển đổi định dạng đa chiều:** Nhận request theo chuẩn OpenAI Chat Completions & Responses, Gemini native và Anthropic Messages, sau đó biên dịch mượt mà giữa các định dạng (bao gồm cả streaming).
- **Điều phối thông tin xác thực đa năng:** Quản lý tài khoản OAuth và API key với theo dõi sức khỏe, kiểm tra hợp lệ, chống trùng lặp và chuyển vùng dự phòng thông minh.
- **Định tuyến mô hình theo từng tài khoản:** Duy trì danh mục mô hình riêng cho từng credential để không gửi nhầm yêu cầu đến tài khoản không hỗ trợ mô hình đó.
- **Khả năng phục hồi streaming:** Hỗ trợ SSE streaming, pseudo-streaming cho client bắt buộc stream, và cơ chế tiếp tục sinh văn bản chống bị ngắt quãng giữa chừng (anti-truncation).
- **Bảng điều khiển web (Console):** Tích hợp giao diện quản lý credential, xem log thời gian thực, cấu hình hệ thống, thống kê token và kiểm tra phiên bản.

## Giao diện Console

![Omni Gateway credential pool](../../docs/assets/screenshots/credential-pool.png)

## <a id="nha-cung-cap-ho-tro"></a>Nhà cung cấp hỗ trợ

Omni Gateway thích ứng linh hoạt giữa các nhà cung cấp AI hàng đầu, runtime cục bộ và tài khoản OAuth:

| Nhà cung cấp | Loại xác thực | Giao thức hỗ trợ | Tự động Failover | Hỗ trợ Streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Self-hosted)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## <a id="trien-khai"></a>Triển khai

### Chạy bằng Docker trên VPS

Tạo thư mục lưu trữ dữ liệu bền vững trên máy chủ:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Khởi chạy container:

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

Mở trình duyệt truy cập bảng điều khiển tại: `http://IP_CUA_SERVER:4283`

Khi khởi chạy lần đầu tiên, hãy đặt mật khẩu quản trị trên màn hình thiết lập. Nếu truy cập từ xa, hãy nhập mã bootstrap token được hiển thị trong lệnh `docker logs omni-gateway`.

## <a id="tich-hop-sdk"></a>Tích hợp SDK

Omni Gateway hỗ trợ định tuyến theo chuẩn SDK chính thức mà không cần thay đổi code phức tạp.

### OpenAI SDK (Python)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:4283/v1",
    api_key="sk-ogw-..."
)

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Giải thích dự án này trong một đoạn ngắn."}],
)
print(response.choices[0].message.content)
```

### Anthropic SDK (Python)

```python
from anthropic import Anthropic

client = Anthropic(
    base_url="http://127.0.0.1:4283",
    api_key="sk-ogw-..."
)

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Viết giúp tôi commit message."}],
)
print(response.content[0].text)
```

### Google GenAI SDK (Python)

```python
from google import genai

client = genai.Client(
    http_options={"base_url": "http://127.0.0.1:4283"},
    api_key="sk-ogw-..."
)

response = client.models.generate_content(
    model="omway",
    contents="Viết một hàm Python tính giai thừa.",
)
print(response.text)
```

## Giấy phép

Omni Gateway được phát hành dưới [Giấy phép MIT](../../LICENSE).
