<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>AI コーディングツール向けユニバーサル AI ルーター & 統合マルチプロバイダーゲートウェイ</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#対応プロバイダー"><b>🌐 対応プロバイダー</b></a> •
    <a href="#主要機能"><b>⚡ 主要機能</b></a> •
    <a href="#デプロイ"><b>🐳 Docker デプロイ</b></a> •
    <a href="#クイックスタート-sdk-連携"><b>🔌 SDK 連携</b></a> •
    <a href="../architecture.md"><b>📖 アーキテクチャ</b></a>
  </p>

  <p>
    <b>コンソール & ドキュメント言語:</b><br>
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
</div>

---

コーディングツールのためのユニバーサル AI ルーター。Omni Gateway は、スマートな自動フォールバック、トークン対応のコンテキストクリーンアップ、利用状況の可視化、シームレスなフォーマット変換を提供し、ローカルエージェント、IDE アシスタント、自動化スクリプトが単一の安定した API インターフェースを通じて無料および有料の LLM 処理能力を活用できるようにします。

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Omni Gateway を選ぶ理由

現代のコーディングワークフローでは、OpenAI 互換ツール、Gemini ネイティブ SDK、Anthropic スタイルのエージェント、Google 認証情報、実験的なモデルルートなど、複数のクライアントとプロバイダーが混在することがよくあります。Omni Gateway はこれらのクライアントとモデルバックエンドの間に位置し、ゲートウェイがルーティング、リトライ、リクエストのクリーンアップ、レスポンスの正規化を処理する間、各ツールがネイティブフォーマットで通信し続けられるようにします。

## 主要機能

- スマートな自動フォールバック: リクエストごとに認証情報を予約し、同時トラフィックを分散し、公正なローテーションのためにすべての試行を追跡し、最近のエラー、クールダウン、レート制限、容量枯渇を自動的に回避します。
- トークン対応のクリーンアップ: ペイロードを正規化し、システム指示、ツール定義、直近のコンテキストを完全に保持しながら、安全なターン境界でのみ過大な会話プレフィックスをトリミングします。
- フォーマット変換: OpenAI Chat Completions および Responses、Gemini ネイティブおよび Anthropic Messages を受け入れ、通常モードおよびストリーミングモードの両方でフォーマット間を相互に変換します。
- 認証情報のオーケストレーション: ヘルス状態、クールダウン追跡、検証、重複排除、プロバイダー対応フォールバックを備えた OAuth アカウントおよびプロバイダー API キーを管理します。
- 認証情報レベルのモデルルーティング: 認証情報ごとに個別の機能カタログを維持し、あるアカウントの権限が、選択されたモデルを公開していない別のアカウントに誤ってリクエストを送信するのを防ぎます。
- ルートヘルスログ: 認証情報スコープでモデル未検出（404）レスポンスを記録し、影響を受けるルートをモデルページから復旧できるように表示します。
- ストリーミング耐障害性: SSE ストリーミング、ストリーム出力を必須とするクライアント向け疑似ストリーミング（pseudo-streaming）、および長文生成時の途切れ防止リトライをサポートします。
- コントロールパネル: 認証情報の管理、ログの閲覧、システム設定、利用状況の確認、バージョン情報の参照が可能な Web コンソールが付属しています。

## コンソールプレビュー

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## 対応プロバイダー

Omni Gateway は、主要な AI プロバイダー、ローカルランタイム、OAuth エンドポイント間でリクエストをシームレスに適応させます:

| プロバイダー | 認証タイプ | サポートプロトコル | 自動フェイルオーバー | ストリーミング |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | API Key | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | API Key | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | API Key | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | API Key | OpenAI 互換, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | API Key | OpenAI 互換 | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (ローカル / セルフホスト)** | ローカル / Base URL | OpenAI 互換 | ✅ | ✅ |

## アーキテクチャ

```text
クライアントツール
  OpenAI SDK | Google GenAI SDK | Anthropic SDK | IDE 連携プラグイン
        |
        v
Omni Gateway
  認証 -> フォーマット変換 -> トークン対応クリーンアップ -> ルーティング -> フォールバック -> ストリーミング
        |
        v
プロバイダーアダプター
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

Omni Gateway バックエンドアダプターが進化し続ける中でも、外部向けのパブリック API コントラクトは安定性を維持します。

## リポジトリ構成

```text
backend/       FastAPI 構成ルート、ルーティングコア、プロトコル変換、ストレージ、テスト
frontend/      管理コンソール UI、スタイル、スクリプト、プロバイダーアイコンアセット
deploy/        コンテナ定義、プラットフォームマニフェスト、OS 起動スクリプト
docs/          アーキテクチャ設計書およびプロジェクト保守ドキュメント
.github/       CI ワークフロー、依存関係自動化、コントリビューションテンプレート
```

モジュール境界、リクエスト処理フロー、状態の所有権、現行リリースの制約については、[アーキテクチャ](../architecture.md)を参照してください。

## デプロイ

Omni Gateway は本番環境向けに設計されています。VPS やサーバー環境では、ランタイムを隔離しつつホスト上で認証情報とログを永続化できる Docker の使用を推奨します。

### VPS での Docker デプロイ

まず、ホストサーバー上に永続化ディレクトリを作成します:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

サービスコンテナを起動します:

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

同一リリースは GitHub Packages にも公開されています: `ghcr.io/nguywnben/omni-gateway:1.4.0`。`latest` タグは最新の安定版リリースを追跡し、`edge` タグは検証済みだが未リリースの `main` ブランチビルドを追跡します。環境の再現性が必要な場合は、特定のバージョンタグまたはダイジェストを固定してください。

ブラウザでコントロールパネルを開きます:

```text
http://サーバーのIPアドレス:4283
```

初回起動時は、初期設定画面でコントロールパネルのパスワードを設定します。デフォルトのパスワードは用意されていません。リモートブラウザからアクセスする場合は、`docker logs omni-gateway` に表示されるブートストラップトークン（bootstrap token）を入力する必要があります（localhost からの直接アクセス時は不要です）。自動デプロイを行う場合は、起動前に `SETUP_TOKEN` 環境変数を事前設定できます。

システム管理パスワードはソルト付き scrypt ハッシュで安全に保存され、コンソールセッションには HttpOnly Cookie が使用され、公開 SDK リクエストは自動生成される `sk-ogw-` API キーで認証されます。非対話型デプロイの場合は、`PANEL_PASSWORD` を事前設定することで初期設定画面を完全にスキップできます。

`1.4.0` イメージは `linux/amd64` 向けにビルド・公開されています。Vertex トランスポートスタックを含むすべてのプロバイダー依存関係が同一基準でビルドおよびテスト可能になるまで、ARM64 イメージの公開は保留されています。

サーバーのファイアウォールが有効な場合は、ゲートウェイポートを開放してください:

```bash
sudo ufw allow 4283/tcp
```

リアルタイムログの確認:

```bash
sudo docker logs -f omni-gateway
```

最新の安定版へのアップデート:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

その後、上記の同じ `docker run` コマンドでコンテナを再起動します。マウントされた `/opt/omni-gateway` ディレクトリにより、コンテナのアップデートをまたいで認証情報、設定、利用状況データ、ログが保持されます。

### Docker Compose デプロイ

ソースコードリポジトリベースのデプロイを行う場合:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

付属の Compose ファイルはデフォルトで `nguywnben/omni-gateway:latest` をプルし、ホストデータの永続化に `/opt/omni-gateway` を使用します。このリリースを固定するには `IMAGE=nguywnben/omni-gateway:1.4.0` を設定し、別の保存先を使用する場合は `DATA_DIR=/カスタムパス` を設定します。

Compose はシェル環境変数またはルートの `.env` ファイルから `API_KEY`、`PANEL_PASSWORD`、`SETUP_TOKEN`、外部ストレージ URI、`PROXY` を渡します。自動キー生成、初回セットアップ、ローカル SQLite ストレージ、直接アウトバウンド通信のデフォルト動作を維持する場合は、これらを空のままにしてください。


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.


### ローカル開発

ローカルでゲートウェイを開発またはデバッグする場合は、Python ネイティブのワークフローを使用します:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Windows PowerShell 環境:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

ブラウザでコントロールパネルを開きます:

```text
http://127.0.0.1:4283
```

ローカル開発環境でも、Docker デプロイと同じ初回実行セットアップ画面が使用されます。

## 設定

Omni Gateway は、環境変数 > 保存された設定 > デフォルト値の優先順位で設定を読み込みます。

| 環境変数 | デフォルト値 | 説明 |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | バインドアドレス。 |
| `PORT` | `4283` | HTTP ポート。 |
| `HOST_PORT` | `4283` | ホスト側ポート（Docker Compose 専用）。 |
| `WORKERS` | `1` | 1.x 系でサポートされるワーカー数。プロセス間での予約、クールダウン、セッション、利用状況集計が実装されるまで、他の値は拒否されます。 |
| `CORS_ORIGINS` | 空 | クロスオリジン API 呼び出しを許可するブラウザオリジンのカンマ区切りリスト。同一オリジンのコンソールアクセスの場合は空のままにします。 |
| `CORS_ORIGIN_REGEX` | 空 | 動的ブラウザオリジンを照合するためのオプションの正規表現。 |
| `API_KEY` | 自動生成 | パブリッククライアント API リクエスト用の優先キー。`sk-ogw-` で始まる必要があります。 |
| `PANEL_PASSWORD` | セットアップ前は空 | Web コントロールパネルのアクセスパスワード。 |
| `SETUP_TOKEN` | プロセスごとに生成 | リモート初回セットアップ用のオプションの固定ブートストラップトークン。省略時はログから取得します。 |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Web コントロールパネルセッションの有効期間（秒）。 |
| `PANEL_COOKIE_SECURE` | 自動判定 | `true` に設定すると Cookie の送信を HTTPS に強制します。空の場合は `X-Forwarded-Proto` から自動検出します。 |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | ログインレート制限ウィンドウ（秒）。 |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | ウィンドウ期間内に単一クライアントに許可される最大ログイン失敗回数。 |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | メモリ内ログイン制限機能が追跡する最大クライアントアドレス数。 |
| `MAX_REQUEST_BODY_MB` | `64` | 最大 HTTP リクエストボディサイズ（MiB）。超過したリクエストにはプロトコル固有のエラーが返されます。 |
| `TRUST_PROXY_HEADERS` | `false` | 転送ヘッダーを上書きする信頼できるリバースプロキシ配下にある場合のみ有効にします。 |
| `CREDENTIALS_DIR` | `./backend/data/creds` | 認証情報の保存ディレクトリ。Docker では `/app/backend/data/creds` をホストにマウントします。 |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Code Assist バックエンドエンドポイント。 |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Google Antigravity バックエンドエンドポイント。 |
| `PROXY` | 空 | オプションの HTTP、HTTPS、または SOCKS プロキシ。 |
| `RETRY_429_ENABLED` | `true` | レート制限および一時的なアップストリームエラーに対する有界リトライを有効化。既存設定との互換性のために旧名を維持。 |
| `RETRY_429_MAX_RETRIES` | `5` | 一時的なアップストリームエラーに対する最大リトライ回数。 |
| `RETRY_429_INTERVAL` | `1` | 一時的リトライの基本バックオフ間隔（秒）。 |
| `AUTO_DISABLE` | `false` | 設定された重大なエラーの発生時に認証情報を自動無効化。 |
| `AUTO_DISABLE_ERROR_CODES` | `403` | 重大なエラーとみなすステータスコードのカンマ区切りリスト。 |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | 空 | `priority` ポリシーで優先されるプロバイダー（例: `google_antigravity`、`google_ai_studio`）。 |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | プロバイダー推論タイムアウト（5〜900 秒）。 |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | ストリーミング途切れ防止機能の最大継続リトライ回数。 |
| `TOKEN_COMPRESSION_ENABLED` | `true` | プロバイダーへのルーティング前に長大な会話履歴を圧縮。 |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | コンテキスト圧縮を開始する推定入力トークンしきい値。 |
| `TOKEN_COMPRESSION_TARGET` | `24000` | 圧縮後の目標推定入力トークン数。しきい値未満にする必要があります。 |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | 圧縮時に必ず保持する最新のユーザーターン最小数。 |
| `COMPATIBILITY_MODE` | `false` | システムメッセージをサポートしないクライアント/モデル向けに自動変換。 |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | 利用可能な場合にモデルの思考プロセス（reasoning）を返却。 |
| `MONGODB_URI` | 空 | 設定時に MongoDB ストレージバックエンドを有効化。 |
| `POSTGRESQL_URI` | 空 | 設定時に PostgreSQL ストレージバックエンドを有効化。 |
| `REDIS_URL` | 空 | 設定時に Redis キャッシュ / セッション状態を有効化。 |
| `CODE_ASSIST_CLIENT_ID` | 組み込みデスクトップ | Code Assist OAuth Client ID のオプションの上書き。 |
| `CODE_ASSIST_CLIENT_SECRET` | 組み込みデスクトップ | Code Assist OAuth Client Secret のオプションの上書き。 |
| `ANTIGRAVITY_CLIENT_ID` | 組み込みデスクトップ | Google Antigravity OAuth Client ID のオプションの上書き（プロバイダー画面でも設定可能）。 |
| `ANTIGRAVITY_CLIENT_SECRET` | 組み込みデスクトップ | Google Antigravity OAuth Client Secret のオプションの上書き。 |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Google AI Studio Generative Language API エンドポイントのオプションの上書き。 |
| `XAI_API_URL` | `https://api.x.ai/v1` | SpaceXAI Console API キー認証用エンドポイントのオプションの上書き（プロバイダー画面でも設定可能）。 |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Grok Build OAuth サブスクリプションエンドポイントのオプションの上書き。 |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Grok Build OAuth Issuer のオプションの上書き。コンソールは `x.ai` ドメイン配下の HTTPS ホストのみを受け入れます。 |
| `XAI_CLIENT_ID` | 組み込みパブリック | Grok Build PKCE OAuth Client ID のオプションの上書き。 |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Grok Build OAuth および SpaceXAI Console API リクエスト共通の HTTP User-Agent のオプションの上書き。 |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | OpenAI Platform API エンドポイントのオプションの上書き（プロバイダー画面でも設定可能）。 |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Codex 推論およびアカウントモデルリストエンドポイントのオプションの上書き。 |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Codex アカウントレート制限確認エンドポイントのオプションの上書き。 |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Codex デバイス認可サービスのオプションの上書き。 |
| `CODEX_CLIENT_ID` | 組み込みパブリック | Codex デバイス OAuth Client ID のオプションの上書き。 |
| `CODEX_USER_AGENT` | Codex CLI 互換 | Codex リクエスト用のオプションの User-Agent 上書き。 |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Claude Platform および Claude Code Messages API エンドポイントのオプションの上書き（プロバイダー画面でも設定可能）。 |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Claude Code PKCE 認可エンドポイントのオプションの上書き。Anthropic / Claude 公式ホストのみ受付。 |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Claude Code トークンエンドポイントのオプションの上書き。Anthropic / Claude 公式ホストのみ受付。 |
| `CLAUDE_CLIENT_ID` | 組み込みパブリック | Claude Code PKCE OAuth Client ID のオプションの上書き。 |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Claude Code および Claude Platform リクエスト用のオプションの User-Agent 上書き。 |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Google Antigravity プロトコルレベルリクエスト用のオプションの User-Agent 上書き。 |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Google Antigravity ペイロード層 userAgent フィールドのオプションの上書き。 |
| `METRICS_TOKEN` | empty | Optional bearer token required to scrape `GET /metrics`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | 実行時のログレベル。 |
| `LOG_MAX_MB` | `10` | ログファイルがローテーションされるまでの最大サイズ（MB）。 |
| `LOG_BACKUP_COUNT` | `3` | 保持するローテーションログファイルの世代数。 |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | ファイルログの出力先パス。Docker では `/app/backend/data/logs` をホストにマウントします。 |

## クイックスタート SDK 連携

Omni Gateway は、公式 Python SDK の標準 URL 動作に合わせて設計されています。ゲートウェイには非標準の重複パスプレフィックスは不要ですので、以下のようにクライアントを設定してください。

以下の例では仮想モデル `omway` を使用しています。事前にモデル管理画面でフォールバック優先順位を設定するか、特定のプロバイダーモデル ID に置き換えてください。

### OpenAI Python SDK

OpenAI のベース URL に `/v1` を指定します。SDK は自動的に `/chat/completions` を末尾に追加します。

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "このリポジトリについて1段落で説明してください。"}],
)
```

同一クライアントで OpenAI Responses API を呼び出すこともできます:

```python
response = client.responses.create(
    model="omway",
    instructions="簡潔に回答してください。",
    input="このリポジトリについて1段落で説明してください。",
)

print(response.output_text)
```

Responses 互換レイヤーは、テキスト入力、画像入力、非ストリーミング Function Tool、および SSE テキストストリーミングをサポートします。OpenAI ホスト型の組み込みツール、永続化されたレスポンス履歴、ストリーミング関数呼び出しについては、Omni Gateway がこれらの OpenAI 独自仕様を実行、永続化、または暗黙的に破棄しないため、明確にエラーを返して拒否します。

### Anthropic Python SDK

Anthropic のベース URL にはゲートウェイのオリジンを直接指定します。SDK は自動的に `/v1/messages` を末尾に追加します。

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "簡潔なコミットメッセージを作成してください。"}],
)
```

### Google GenAI Python SDK

Google GenAI のベース URL にはゲートウェイのオリジンを直接指定します。SDK は自動的に `/v1beta/models/{model}:generateContent` などのデフォルトモデルルートを追加します。

```python
from google import genai
from google.genai import types

client = genai.Client(http_options={"base_url": "http://127.0.0.1:4283"}, api_key="sk-ogw-...")

response = client.models.generate_content(
    model="omway",
    contents="短い Python 関数を書いてください。",
    config=types.GenerateContentConfig(system_instruction="あなたは有能なアシスタントです。"),
)
```

### 対応エンドポイント一覧

Omni Gateway は、余分な製品名前空間プレフィックスなしで標準の SDK 互換ルートを提供します:

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

認証エラー、リクエスト検証エラー、ルーティングエラー、アップストリームエラー、ストリーミング開始前の失敗は、すべて対応する SDK インターフェースのネイティブエラー構造でラップされます。すべての HTTP レスポンスには `X-Request-ID` ヘッダーが含まれ、クライアントはこのヘッダーに識別子を渡すことでリクエストフローの追跡が可能です。アップストリームからレート制限または一時的な利用不可が返された場合、ゲートウェイは `Retry-After` ヘッダーをそのまま透過的に保持します。

## モデル機能と高度な制御

コンソールの「モデル」ページでは、有効なプロバイダー認証情報から検出されたモデルを集約して仮想モデル `omway` を構築します。各基礎モデルの優先順位を一度設定すれば、サポートされている任意の SDK から `omway` を利用できます。Omni Gateway は第 1 順位のモデルをサポートする健全な認証情報間で負荷分散を行い、そのモデルが利用不可になった場合は設定順に従って自動的にフォールバックを試行します。特定のモデルを決定論的に指定する必要があるクライアントのために、プロバイダー固有のモデル ID もそのまま利用可能です。空のリストを保存すると、プロバイダー認証情報に影響を与えることなく `omway` を無効化できます。

モデル検出はプロバイダー認識型です。共通モデルは複数のプロバイダーでサポートされ、固有モデルは互換性のある認証情報でのみ処理されます。検証済みの各認証情報は独自のプロバイダーカタログを保持し、ルーターは一般的なプロバイダーの推測よりも認証情報が明示的に宣言したサポートを優先します。カタログを更新するとプロバイダーの現在の可用性が再取得され、利用不可となった項目も復旧または削除されるまで設定内に表示され続けます。

特定のモデルに対してアップストリームが `404` を返した場合、Omni Gateway はプロバイダー全体を無効化するのではなく、その認証情報とモデルのスコープで利用不可ルートを記録します。そのルートは直ちに一時的に回避され、クリアされるか認証情報が再検証されるまで**利用不可モデルルート**一覧に表示されます。これにより、単一アカウントのサブスクリプション権限やリージョン制限が同じプロバイダー配下の他の健全なアカウントに影響を与えるのを防ぎます。有効な認証情報のいずれも要求されたモデルを宣言または推測できない場合、ゲートウェイは不適切なプロバイダーにランダムに転送することなく、互換性のある認証情報が存在しない旨のエラーを明確に返します。

Omni Gateway は、モデル名に含まれる機能プレフィックスおよびサフィックスを解釈します:

- `fake-streaming/{model}` または設定された疑似ストリーミングプレフィックス（SSE 形式を必須とするクライアント用）。
- `streaming-anti-truncation/{model}` または設定された途切れ防止プレフィックス（長文ストリーミング生成時の自動復旧用）。
- 思考深度サフィックス（`-high`、`-medium`、`-low`、`-minimal`、`-max` など、サポートされている Gemini 系モデル用）。
- 検索グラウンディングサフィックス（`-search` など、Google Search グラウンディング対応モデル用）。

プロバイダーアダプターは、アップストリームにリクエストを送信する前にこれらの機能識別子を自動的に正規化します。

## 利用状況とコストの透明性

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## 認証情報の設定ワークフロー

1. Omni Gateway を起動します。
2. VPS では `http://サーバーのIP:4283`、ローカル開発では `http://127.0.0.1:4283` にアクセスします。
3. 初回起動画面でコントロールパネルのパスワードを作成します。リモートデプロイの場合はログのブートストラップトークンを入力するか、事前に `PANEL_PASSWORD` を設定しておきます。
4. 「プロバイダー」ページでアカウント、API キー、または Ollama 接続を追加します。
5. 認証情報の有効性を検証し、パネル内でクールダウンやエラー状態を監視します。
6. コーディングツールを上記のサポートされている API インターフェースのいずれかに接続します。

Google Antigravity 認証情報を追加する際、ログイン完了後に Google はブラウザを `http://localhost:4283/callback` にリダイレクトします。ローカルマシンでは OAuth 成功画面が直接表示されます。VPS の場合、その `localhost` はユーザーのローカルブラウザを指すためページが開かないことがあります。ブラウザのアドレスバーから URL 全体をコピーし、プロバイダー画面に戻って `Callback URL` 欄に貼り付け、`認証情報を保存` をクリックしてください。

Google AI Studio は OAuth ではなく API キー認証を使用します。プロバイダー画面でキーを追加すると、Omni Gateway は Google のモデルカタログと照合して検証し、プロバイダー認証情報として保存して、互換性のある Gemini または Gemma リクエストをルーティングします。スマートルーターは、共通の Gemini モデルについて AI Studio と Google Antigravity 間で自動フェイルオーバーを行い、固有モデルは互換性のある認証情報にのみ送信します。

Google AI Studio の一括インポートは、JSON ファイルおよび JSON ファイルを含む ZIP アーカイブをサポートしています。JSON ドキュメントには単一のキー、`api_keys` 配列、またはキーオブジェクトの配列を含めることができます:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

インポートされた各キーは保存前に厳格に検証されます。同一バッチ内の重複キーはスキップされ、既存のキーは再検証されて更新され、無効なレコードはキーの平文を漏洩することなく個別に報告されます。

Grok Build は PKCE OAuth 認証情報をサポートし、SpaceXAI Console は API キーをサポートします。SpaceXAI Console キーは保存前に Grok Build モデルカタログと照合して検証されます。Grok Build OAuth の場合、Omni Gateway は認可リンクを生成します。認可完了後、認可画面に表示されたコードをコピーしてフォームに貼り付けてください。リフレッシュトークンが存在する場合はアクセストークンが自動更新され、両方の認証情報タイプともに現在のカタログで宣言された Grok Build モデルのみを公開します。プール画面では、Grok Build OAuth アカウントの月間クレジット消費量、および xAI から提供されている場合は週間使用量を確認できます。このアカウントレベルの請求ビューは SpaceXAI Console API キーでは利用できません。

Codex は OpenAI デバイス認可フローを使用します。プロバイダー画面でデバイスコードを生成し、表示された検証 URL を開き、コードを入力してログインを完了した後、認可状態を確認します。Omni Gateway は Codex が返したアカウントスコープのモデルカタログを保存し、必要に応じて OAuth アクセストークンを更新し、Codex Responses トランスポートを通じて互換リクエストを転送します。OpenAI Platform は API キー認証を使用し、キーはアカウントモデルカタログを通じて検証された後にプールへ追加されます。両製品ともに JSON および ZIP インポートをサポートし、プロバイダー固有の検証と重複排除が行われます。

Claude Code は Anthropic の PKCE OAuth フローを使用します。認可リンクを生成して認可を完了し、取得した認可コードをプロバイダー画面に貼り付けます。Claude Platform は Anthropic API キーを受け入れます。両製品ともに認証情報ごとにサポートされているモデルを検出し、Anthropic Messages トランスポートを使用し、可能な場合は Claude Code アクセストークンを自動更新し、検証付きの JSON / ZIP インポートをサポートします。

Ollama 接続はエンドポイントごとに設定され、保護されたサーバーやクラウドサーバー向けのオプションの Bearer API キーを含めることができます。Omni Gateway は `/api/tags` を通じてモデルを検出し、`/api/chat` を介して推論をルーティングします。Omni Gateway が Docker 内で動作している場合、`localhost` はコンテナ自身を指します。ホストゲートウェイアドレスまたはネットワーク経由でアクセス可能な Ollama エンドポイントを使用してください。

プール全体のインポートおよび Google Antigravity の一括インポートは、最大 10 MB のアーカイブ、最大 500 ファイル、単一認証情報ファイル最大 2 MB、解凍後合計最大 25 MB をサポートします。Google AI Studio、OpenAI、Anthropic、Ollama の個別プロバイダーインポートには、ファイルあたり最大 2 MB、最大 200 件の JSON レコード、解凍後最大 5 MB という厳格な制限が適用されます。

「認証情報プール」ページでは、プロバイダーに依存しない完全なバックアップワークフローも提供されています。`ZIP をダウンロード` でアクティブな全認証情報をエクスポートし、`ZIP をインポート` で各認証情報（Google Antigravity、Google AI Studio、Grok Build、SpaceXAI Console、Codex、OpenAI Platform、Claude Code、Claude Platform、Ollama）を自動認識して復元します。OAuth アカウントはプロバイダーのスコープ内で同一性を維持して重複排除され、API キーは不可逆ハッシュフィンガープリントによって検証・重複排除されます。サポートされていない項目やフォーマットエラーのある項目は個別に報告され、アーカイブ内の他の有効な認証情報のインポートを妨げません。

Google Antigravity 認証情報は `google-antigravity-{account_fingerprint}.json` の形式で保存され、フィンガープリントは平文を漏洩することなく正規化されたメールアドレスから生成されます。Google AI Studio は `google-ai-studio-{key_fingerprint}.json`、Grok Build OAuth は `grok-{account_fingerprint}.json`、SpaceXAI Console は `xai-console-{key_fingerprint}.json`、Codex は `openai-codex-{account_fingerprint}.json`、OpenAI Platform は `openai-platform-{key_fingerprint}.json`、Claude Code は `claude-code-{account_fingerprint}.json`、Claude Platform は `claude-platform-{key_fingerprint}.json`、Ollama 接続は `ollama-{connection_fingerprint}.json` を使用します。レガシーな `provider_*.json` および `xai-grok-*.json` 認証情報との下位互換性も維持されており、エクスポート時には標準名に正規化されます。

認証情報モード名:

- `code_assist`: 標準の Code Assist 認証情報プール。
- `provider`: 汎用プロバイダーバックエンド認証情報プール。

## データストレージ

単一プロセスデプロイでは、マウントされたデータディレクトリ内の SQLite ストレージがデフォルトで使用されます。Docker デプロイでは、`/app/backend/data/creds` および `/app/backend/data/logs` を必ずホスト側の永続化パス（`/opt/omni-gateway/creds`、`/opt/omni-gateway/logs` など）にマウントしてください。

運用要件や移行テストに応じて、ローカル SQLite を MongoDB または PostgreSQL に置き換えることができます:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

キャッシュおよびセッション状態の高速化のために Redis を追加することも可能です:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

外部ストレージを設定しても、1.x ランタイムが水平スケーリング可能になるわけではありません。プロセス間での分散予約、クールダウン管理、セッション無効化、利用状況集計が実装されるまでは、単一ワーカーかつ単一レプリカで運用してください。MongoDB と PostgreSQL はどちらか一方のみを設定してください。外部データベースの初期化に失敗した場合、ゲートウェイは SQLite へ暗黙的にフォールバックすることなく起動を明示的に停止します。

環境変数経由での認証情報のインポートもサポートされています。コントロールパネルから操作するか、以下のいずれかの変数に生の JSON 文字列を設定するか、Base64 エンコードされた `_B64` サフィックス付きの変数を使用します:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

ペイロードには単一の認証情報オブジェクト、配列、または `{ "credentials": [...] }` 構造を使用できます。

## 開発ガイド

本セクションはプロジェクト貢献者およびローカルデバッグ向けです。本番環境のデプロイには、永続化ホストボリュームを備えた Docker を使用してください。

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

すべてのチェックを通過後、サービスを起動します:

```bash
python backend/main.py
```

本番稼働のベースラインは Python 3.12 であり、CI 自動テストは Python 3.12 および 3.14 をカバーしています。Pull Request の提出手順とコードレビュー基準については、[貢献ガイド](../../CONTRIBUTING.md)を参照してください。

## デプロイ時の注意事項

- 認証情報を含む JSON ファイルや `.env` ファイルは絶対にコミットしないでください。
- クライアント連携用には専用の `API_KEY` を、コンソールアクセス用には個別の `PANEL_PASSWORD` を設定してください。
- 永続化された認証情報ボリュームや外部データベースへのアクセスを厳格に制限し、プラットフォームレベルで保存時暗号化（encryption at rest）を有効にしてください。ルーターはプロバイダートークンを復号して読み取れる必要があります。
- サービスを localhost 以外に公開する場合は、必ず TLS が有効なリバースプロキシの背後に Omni Gateway を配置してください。
- リバースプロキシが `Host` ヘッダーを保持し、`X-Forwarded-Proto` を渡すように設定してください。HTTPS 終端が保証されている場合は `PANEL_COOKIE_SECURE=true` を設定します。
- `X-Forwarded-For` および `X-Forwarded-Proto` を上書きする信頼できるプロキシ経由でのみアクセス可能な場合にのみ、`TRUST_PROXY_HEADERS=true` を設定してください。
- プロセス生存確認（liveness）には `GET /health` を、ストレージ層を含む準備完了確認（readiness）には `GET /ready` を使用してください。
- Docker イメージは起動初期にマウントされたデータディレクトリの所有権を修正する間のみ root 権限で動作し、その後は非特権ユーザー `gateway` に降格して実行されます。
- ブラウザクライアントからクロスオリジンアクセスが必要な場合は、`CORS_ORIGINS` に信頼できるオリジンを明示的に指定してください。
- アップグレードやサーバー移行の前には、必ず `/opt/omni-gateway` または指定の `DATA_DIR` ディレクトリをバックアップしてください。
- Docker イメージの公開では、Docker Hub 用にリポジトリシークレット `DOCKERHUB_USERNAME` と `DOCKERHUB_TOKEN` を使用し、GitHub Packages（`ghcr.io/nguywnben/omni-gateway`）用に組み込みの `GITHUB_TOKEN` を使用します。カスタムの Docker Hub イメージ名に公開する場合のみ、オプションの `IMAGE_NAME` 変数を設定してください。
- 1.x 系では `WORKERS=1` および単一のアプリケーションレプリカを維持してください。外部ストレージは分散オーケストレーションの代替にはなりません。
- 標準的な正規管理ルート `/api/credentials` を使用してください。ベータ版の別名 `/api/creds` は 1.0.0 で完全に削除されました。
- ベータ版のデプロイを移行する前に、[1.0 へのアップグレードガイド](../upgrading-to-1.0.md)を確認してください。
- 既存のインスタンスをアップグレードまたはロールバックする際は、[アップデートガイド](../updating.md)を参照してください。
- タグ付けやイメージのリリース前に、整備されている[リリースチェックリスト](../release-checklist.md)を順に確認してください。
- 利用制限やクォータに合わせて、適切なログ保持ポリシーと認証情報ローテーションポリシーを策定してください。
- リポジトリやクラウドプラットフォームのスキャンによってシークレットの漏洩が検出された場合は、直ちにその認証情報を失効・ローテーションしてください。
- Render デプロイマニフェストは永続ディスクを備えた有料サービスを使用します。Render の無料サービスはエフェメラルなファイルシステムを使用するため、一時的な試用目的にのみ適しています。

## コミュニティと健全性

- Pull Request を作成する前に[貢献ガイド](../../CONTRIBUTING.md)をお読みください。
- セキュリティ脆弱性の報告は、[セキュリティポリシー](../../SECURITY.md)に記載された非公開の手順に従ってください。
- 各リリースの変更内容については[変更履歴](../../CHANGELOG.md)をご確認ください。
- 本プロジェクトのすべての活動において[行動規範](../../CODE_OF_CONDUCT.md)を遵守してください。

## 謝辞 & インスピレーション

Omni Gateway は、オープンソースの AI ルーティング、オブザーバビリティ、ゲートウェイコミュニティの成果の上に築かれています。以下のプロジェクトの創設者およびメンテナーに深く感謝いたします:

| プロジェクト | 説明 | Stars |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | マルチプロバイダーのキー管理および Web ベース API 集約のアーキテクチャインスピレーション | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | AI コーディング CLI 向けマルチプロトコルプロキシおよびフォーマット変換レイヤーの先駆的実装 | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | 業界標準の統合 LLM プロキシ、ロードバランシング、フォールバックルーティング | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | 超高速 AI ゲートウェイアーキテクチャ、ルーティング戦略、高耐障害性フォールバック | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | オープンソース LLM エンジニアリングプラットフォーム、トレース、可観測性、メトリクス収集 | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## ライセンス

Omni Gateway は [MIT ライセンス](../../LICENSE) のもとで公開されています。
