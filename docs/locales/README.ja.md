# Omni Gateway

<p align="center">
  <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
  <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
  <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
  <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
  <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
  <img src="https://img.shields.io/badge/i18n-15%20%E8%A8%80%E8%AA%9E-orange?style=flat-square" alt="15 言語">
</p>

<p align="center">
  <a href="#対応プロバイダー"><b>🌐 対応プロバイダー</b></a> •
  <a href="#主要機能"><b>⚡ 主要機能</b></a> •
  <a href="#デプロイ"><b>🐳 Docker デプロイ</b></a> •
  <a href="#sdk-連携"><b>🔌 SDK 連携</b></a> •
  <a href="../../docs/architecture.md"><b>📖 アーキテクチャ</b></a>
</p>

<p align="center">
  <a href="../../README.md">English</a> •
  <a href="README.vi.md">Tiếng Việt</a> •
  <a href="README.zh-CN.md">中文(简体)</a> •
  <a href="README.zh-TW.md">中文(繁體)</a> •
  <b>日本語</b> •
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

コーディングツールのためのユニバーサル AI ルーター。Omni Gateway は、スマート自動フェイルオーバー、トークンを考慮したリクエストクリーンアップ、利用状況の可視化、シームレスなプロトコル変換を提供し、ローカルエージェント、IDE アシスタント、自動化スクリプトが単一の安定した API エンドポイントを介して無料および有料の LLM リソースを活用できるようにします。

> **ステータス:** 安定版。バージョン `1.3.1` では、15 言語に対応した管理コンソールと多言語 API メッセージをサポートしています。

## 主な機能

- **スマート自動フェイルオーバー:** リクエストごとに認証情報を予約し、並行トラフィックを分散。レート制限、一時的な障害、クォータ枯渇を自動的に回避します。
- **トークン最適化クリーンアップ:** 会話の安全な区切りで履歴をトリミングし、システムプロンプトや最新の文脈を保持します。
- **マルチプロトコル変換:** OpenAI Chat Completions & Responses、Gemini ネイティブ、Anthropic Messages 間の相互変換（ストリーミング対応）を行います。
- **認証情報プール管理:** OAuth アカウントと API キーを集中管理し、ヘルスチェックや重複排除を行います。
- **Web 管理コンソール:** 認証情報、リアルタイムログ、設定、使用量分析を直感的に操作できるダッシュボードを内蔵。

## <a id="対応プロバイダー"></a>対応プロバイダー

| プロバイダー | 認証方式 | 対応プロトコル | 自動フェイルオーバー | ストリーミング |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI Compatible, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI Compatible | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (ローカル/自己ホスト)** | Local / Base URL | OpenAI Compatible | ✅ | ✅ |

## <a id="デプロイ"></a>Docker デプロイ

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

ブラウザで `http://YOUR_SERVER_IP:4283` にアクセスし、画面の指示に従ってパスワードを設定してください。

## ライセンス

Omni Gateway は [MIT ライセンス](../../LICENSE) の下で公開されています。
