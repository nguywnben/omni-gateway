<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Routeur d'IA universel et passerelle multi-fournisseurs unifiée pour outils de développement IA</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#fournisseurs-pris-en-charge"><b>🌐 Fournisseurs pris en charge</b></a> •
    <a href="#fonctionnalites-principales"><b>⚡ Fonctionnalités principales</b></a> •
    <a href="#deploiement"><b>🐳 Déploiement Docker</b></a> •
    <a href="#demarrage-rapide-integration-sdk"><b>🔌 Intégration SDK</b></a> •
    <a href="../architecture.md"><b>📖 Architecture</b></a>
  </p>

  <p>
    <b>Langues de la console et documentation :</b><br>
    <a href="../../README.md">English</a> •
    <a href="README.vi.md">Tiếng Việt</a> •
    <a href="README.zh-CN.md">中文(简体)</a> •
    <a href="README.zh-TW.md">中文(繁體)</a> •
    <a href="README.ja.md">日本語</a> •
    <a href="README.ko.md">한국어</a> •
    <a href="README.es.md">Español</a> •
    <b>Français</b> •
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

Un routeur d'IA universel pour les outils de développement. Omni Gateway fournit un basculement automatique intelligent (smart auto-fallback), un nettoyage de contexte sensible aux tokens, une visibilité d'utilisation et une traduction fluide de formats afin que les agents locaux, assistants d'IDE et scripts d'automatisation puissent exploiter la capacité des LLM gratuits et payants via une interface d'API stable unique.

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Pourquoi Omni Gateway

Les flux de travail de développement modernes associent fréquemment plusieurs clients et fournisseurs : outils compatibles OpenAI, SDK natifs Gemini, agents au style Anthropic, identifiants adossés à Google et routes de modèles expérimentales. Omni Gateway s'intercale entre ces clients et les backends de modèles afin que chaque outil puisse continuer à utiliser son format natif tandis que la passerelle gère le routage, les nouvelles tentatives (retries), le nettoyage des requêtes et la normalisation des réponses.

## <a id="fonctionnalites-principales"></a>Fonctionnalités principales

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## Aperçu de la console

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## <a id="fournisseurs-pris-en-charge"></a>Fournisseurs pris en charge

Omni Gateway adapte les requêtes de manière fluide entre les principaux fournisseurs d'IA, moteurs d'exécution locaux et points de terminaison OAuth :

| Fournisseur | Type d'authentification | Protocoles pris en charge | Basculement automatique | Support du streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | Clé API | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | Clé API | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | Clé API | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | Clé API | Compatible OpenAI, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | Clé API | Compatible OpenAI | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Local / Auto-hébergé)** | Local / Base URL | Compatible OpenAI | ✅ | ✅ |

## Architecture

```text
outils clients
  SDKs OpenAI | SDKs Google GenAI | SDKs Anthropic | Intégrations IDE
        |
        v
Omni Gateway
  authentification -> traduction de format -> nettoyage de tokens -> routage -> basculement -> streaming
        |
        v
adaptateurs fournisseurs
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

L'API publique demeure stable pendant que les adaptateurs spécifiques aux fournisseurs évoluent sous Omni Gateway.

## Structure du dépôt

```text
backend/       Racine de composition FastAPI, cœur de routage, traducteurs, stockage et tests
frontend/      Interface de console d'administration, styles, scripts et ressources graphiques
deploy/        Définitions de conteneurs, manifestes de plateforme et scripts système
docs/          Notes d'architecture et documentation de maintenance du projet
.github/       CI, automatisation des dépendances et modèles de contribution
```

Consultez [Architecture](../architecture.md) pour en savoir plus sur les limites de modules, flux de requêtes, gestion d'état et contraintes de version actuelles.

## <a id="deploiement"></a>Déploiement

Omni Gateway est conçu pour des déploiements réels en production. Docker constitue la méthode recommandée pour les serveurs et VPS, car il maintient le runtime isolé tout en conservant durablement les identifiants et journaux sur l'hôte.

### Docker sur VPS

Créez d'abord les répertoires persistants sur l'hôte :

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Démarrez le service :

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

La même version est également publiée sur GitHub Packages sous `ghcr.io/nguywnben/omni-gateway:1.4.0`. Le tag `latest` suit la version stable la plus récente ; `edge` suit les builds validés mais non publiés de la branche `main`. Figez un tag de version ou un digest spécifique pour garantir des déploiements reproductibles.

Ouvrez le panneau de configuration à l'adresse :

```text
http://IP_DE_VOTRE_SERVEUR:4283
```

Lors de la première exécution, définissez le mot de passe de la console sur l'écran de configuration. Aucun mot de passe par défaut n'est fourni. Un navigateur distant doit également saisir le token d'initialisation (bootstrap token) affiché par `docker logs omni-gateway` ; une configuration directe sur localhost ne l'exige pas. Définissez `SETUP_TOKEN` avant le démarrage si l'automatisation du déploiement requiert un token prédéterminé fixe.

Les mots de passe gérés par l'application sont stockés sous forme de hachages scrypt avec sel, les sessions de la console utilisent des cookies HttpOnly et les requêtes SDK publiques s'authentifient avec la clé API générée au format `sk-ogw-`. Pour un déploiement non interactif, préconfigurez `PANEL_PASSWORD` afin d'ignorer entièrement l'écran de configuration initiale.

Le conteneur `1.4.0` est publié pour l'architecture `linux/amd64`. La publication d'images ARM64 est temporairement suspendue jusqu'à ce que chaque dépendance de fournisseur, y compris la pile de transport Vertex, puisse être compilée et testée selon le même standard.

Si le pare-feu du serveur est activé, autorisez le port de la passerelle :

```bash
sudo ufw allow 4283/tcp
```

Consulter les journaux :

```bash
sudo docker logs -f omni-gateway
```

Mettre à jour vers l'image stable la plus récente :

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Redémarrez ensuite le conteneur avec la même commande `docker run` ci-dessus. Les répertoires montés dans `/opt/omni-gateway` conservent les identifiants, configurations, données d'utilisation et journaux à travers les mises à jour de conteneurs.

### Docker Compose

Pour les déploiements basés sur le dépôt source :

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

Le fichier Compose inclus télécharge `nguywnben/omni-gateway:latest` et utilise `/opt/omni-gateway` par défaut pour les données persistantes de l'hôte. Définissez `IMAGE=nguywnben/omni-gateway:1.4.0` pour figer cette version, et `DATA_DIR=/chemin/personnalise` lorsque le serveur utilise un autre emplacement de stockage.

Compose transmet `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, les URIs de stockage externe et `PROXY` depuis le shell ou un fichier `.env` à la racine. Laissez-les vides pour conserver la génération automatique de clé, la configuration initiale, le stockage local SQLite et la connectivité réseau sortante directe.


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.


### Développement local

Utilisez le flux de travail Python pour développer ou déboguer la passerelle localement :

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

Sur Windows PowerShell :

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Ouvrez le panneau de configuration à l'adresse :

```text
http://127.0.0.1:4283
```

Le développement local utilise le même écran de configuration initiale que le déploiement Docker.

## Configuration

Omni Gateway lit la configuration en priorité depuis les variables d'environnement, puis la configuration enregistrée, puis les valeurs par défaut.

| Variable | Valeur par défaut | Description |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Adresse d'écoute (bind address). |
| `PORT` | `4283` | Port HTTP. |
| `HOST_PORT` | `4283` | Port côté hôte utilisé uniquement par Docker Compose. |
| `WORKERS` | `1` | Nombre de workers pris en charge pour la série 1.x. Toute autre valeur est rejetée jusqu'à ce que les réservations, cooldowns, sessions et agrégations soient coordonnés multi-processus. |
| `CORS_ORIGINS` | vide | Liste séparée par des virgules des origines de navigateur autorisées pour les appels API cross-origin. Laisser vide pour un usage console same-origin. |
| `CORS_ORIGIN_REGEX` | vide | Expression régulière optionnelle pour les origines de navigateur dynamiques gérées. |
| `API_KEY` | générée automatiquement | Clé privilégiée pour les requêtes API client publiques. Doit commencer par `sk-ogw-`. |
| `PANEL_PASSWORD` | vide jusqu'à configuration | Mot de passe pour le panneau de contrôle web. |
| `SETUP_TOKEN` | généré par processus | Token de démarrage fixe optionnel requis pour la configuration initiale distante. Si omis, lire le token dans les logs de l'application ou du conteneur. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Durée de vie de la session de console web en secondes. |
| `PANEL_COOKIE_SECURE` | automatique | Définir à `true` pour forcer les cookies de console uniquement via HTTPS. Laisser vide pour une détection automatique via `X-Forwarded-Proto`. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Fenêtre de limitation de débit de connexion en secondes. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Tentatives de connexion infructueuses autorisées par client pendant la fenêtre de limitation. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Nombre maximal d'adresses clients conservées en mémoire par le limiteur de connexion. |
| `MAX_REQUEST_BODY_MB` | `64` | Taille maximale du corps de requête HTTP en MiB. Les requêtes SDK trop volumineuses renvoient la structure d'erreur native du protocole. |
| `TRUST_PROXY_HEADERS` | `false` | N'accepter les en-têtes de transfert client/protocole que depuis un reverse proxy de confiance qui les écrase. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Répertoire de stockage des identifiants. Dans Docker, persister `/app/backend/data/creds` avec un volume hôte. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Point de terminaison backend de Code Assist. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Point de terminaison backend de Google Antigravity. |
| `PROXY` | vide | Proxy HTTP, HTTPS ou SOCKS optionnel. |
| `RETRY_429_ENABLED` | `true` | Active les nouvelles tentatives limitées pour les limites de débit et pannes temporaires d'upstream. Le nom historique est conservé pour compatibilité. |
| `RETRY_429_MAX_RETRIES` | `5` | Nombre maximal de tentatives pour les pannes temporaires d'upstream. |
| `RETRY_429_INTERVAL` | `1` | Délai de base entre les nouvelles tentatives temporaires en secondes. |
| `AUTO_DISABLE` | `false` | Désactive automatiquement les identifiants après des erreurs critiques configurées. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Liste séparée par des virgules des codes d'état d'erreur critique. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | vide | Fournisseur préféré pour la stratégie `priority`, tel que `google_antigravity` ou `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Délai d'expiration d'inférence du fournisseur, compris entre 5 et 900 secondes. |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Nombre maximal de tentatives de continuation pour le streaming anti-troncature (anti-truncation). |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Compresse l'historique de conversation volumineux avant le routage vers le fournisseur. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Seuil estimé de tokens d'entrée déclenchant la compression de contexte. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Cible estimée de tokens d'entrée après compression. Doit être inférieur au seuil. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Nombre minimal de tours récents de l'utilisateur conservés lors de la compression. |
| `COMPATIBILITY_MODE` | `false` | Convertit les messages système pour les clients/modèles qui ne les prennent pas en charge nativement. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Inclut les champs de raisonnement du modèle (reasoning) lorsqu'ils sont disponibles. |
| `MONGODB_URI` | vide | Active le stockage backend MongoDB lorsqu'il est défini. |
| `POSTGRESQL_URI` | vide | Active le stockage backend PostgreSQL lorsqu'il est défini. |
| `REDIS_URL` | vide | Active le cache / l'état de session adossé à Redis lorsqu'il est défini. |
| `CODE_ASSIST_CLIENT_ID` | intégré | Remplacement optionnel pour le Client ID OAuth de Code Assist. |
| `CODE_ASSIST_CLIENT_SECRET` | intégré | Remplacement optionnel pour le Client Secret OAuth de Code Assist. |
| `ANTIGRAVITY_CLIENT_ID` | intégré | Remplacement optionnel pour le Client ID OAuth de Google Antigravity. Peut également être géré depuis la page Providers. |
| `ANTIGRAVITY_CLIENT_SECRET` | intégré | Remplacement optionnel pour le Client Secret OAuth de Google Antigravity. À configurer via env ou l'interface Providers lors d'un changement upstream. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Remplacement optionnel du point de terminaison Generative Language API de Google AI Studio. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Remplacement optionnel du point de terminaison d'API SpaceXAI Console pour les identifiants par clé API. Gérable depuis la page Providers. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Remplacement optionnel du point de terminaison d'abonnement Grok Build OAuth. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Remplacement optionnel de l'émetteur Grok Build OAuth. Seuls les hôtes HTTPS sous `x.ai` sont acceptés par la console. |
| `XAI_CLIENT_ID` | intégré | Remplacement optionnel pour le Client ID OAuth PKCE de Grok Build. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Remplacement optionnel du User-Agent HTTP partagé pour les requêtes Grok Build OAuth et API SpaceXAI Console. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Remplacement optionnel du point de terminaison d'API OpenAI Platform. Gérable depuis la page Providers. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Remplacement optionnel du point de terminaison d'inférence et de catalogue de modèles de compte Codex. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Remplacement optionnel du point de terminaison de vérification des limites de compte Codex. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Remplacement optionnel du service d'autorisation d'appareils Codex. |
| `CODEX_CLIENT_ID` | intégré | Remplacement optionnel pour le Client ID OAuth d'appareils de Codex. |
| `CODEX_USER_AGENT` | compatible Codex CLI | Remplacement optionnel de User-Agent pour les requêtes Codex. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Remplacement optionnel du point de terminaison Messages API de Claude Platform et Claude Code. Gérable depuis la page Providers. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Remplacement optionnel du point de terminaison d'autorisation PKCE de Claude Code. Seuls les hôtes Anthropic et Claude sont acceptés. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Remplacement optionnel du point de terminaison d'échange de token de Claude Code. Seuls les hôtes Anthropic et Claude sont acceptés. |
| `CLAUDE_CLIENT_ID` | intégré | Remplacement optionnel pour le Client ID OAuth PKCE de Claude Code. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Remplacement optionnel de User-Agent pour les requêtes Claude Code et Claude Platform. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Remplacement optionnel de User-Agent au niveau protocolaire de Google Antigravity. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Remplacement optionnel du champ userAgent au niveau de la charge utile de Google Antigravity. |
| `METRICS_TOKEN` | empty | Optional bearer token required to scrape `GET /metrics`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | Niveau de détail des journaux (log level). |
| `LOG_MAX_MB` | `10` | Taille maximale du fichier de journal actif avant rotation. |
| `LOG_BACKUP_COUNT` | `3` | Nombre de fichiers journaux archivés conservés lors des rotations. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Emplacement du fichier journal. Dans Docker, persister `/app/backend/data/logs` avec un volume hôte. |

## <a id="demarrage-rapide-integration-sdk"></a>Surfaces SDK

Omni Gateway est conçu autour du comportement d'URL standard des SDK Python officiels. Configurez chaque client exactement comme illustré ci-dessous ; la passerelle n'exige aucun préfixe de chemin dupliqué non standard.

Ces exemples utilisent le modèle virtuel `omway`. Configurez son ordre de priorité de basculement fournisseur-modèle sur la page Models au préalable, ou remplacez-le par un ID de modèle concret.

### OpenAI Python SDK

Utilisez `/v1` comme base_url pour OpenAI. Le SDK ajoute automatiquement `/chat/completions`.

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Explique ce dépôt en un seul paragraphe."}],
)
```

Le même client peut utiliser l'API OpenAI Responses :

```python
response = client.responses.create(
    model="omway",
    instructions="Réponds de façon concise.",
    input="Explique ce dépôt en un seul paragraphe.",
)

print(response.output_text)
```

La compatibilité Responses prend en charge le texte, les entrées d'images, les outils de fonction sans streaming et le streaming de texte par SSE. Les outils intégrés hébergés par OpenAI, l'historique persistant de réponses et les appels de fonctions en streaming sont explicitement rejetés car Omni Gateway n'exécute, ne persiste ni ne supprime silencieusement ces comportements spécifiques à OpenAI.

### Anthropic Python SDK

Utilisez l'origine de la passerelle comme base_url pour Anthropic. Le SDK ajoute automatiquement `/v1/messages`.

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Rédige un message de commit court."}],
)
```

### Google GenAI Python SDK

Utilisez l'origine de la passerelle comme base_url pour Google GenAI. Le SDK ajoute automatiquement sa route de modèle par défaut, telle que `/v1beta/models/{model}:generateContent`.

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
    contents="Écris une petite fonction Python.",
    config=types.GenerateContentConfig(
        system_instruction="Tu es un assistant serviable.",
    ),
)
```

### Routes prises en charge

Omni Gateway expose des routes compatibles SDK sans espace de noms dédié aux produits :

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

Les erreurs d'authentification, de validation de requête, de routage, d'upstream et préalables au streaming utilisent la structure d'erreur native du SDK correspondant. Chaque réponse HTTP inclut l'en-tête `X-Request-ID` ; les clients peuvent fournir un identifiant sécurisé dans cet en-tête pour corréler les requêtes de bout en bout. Les réponses limitées en débit ou temporairement indisponibles conservent l'en-tête `Retry-After` lorsqu'il est fourni par l'upstream.

## Fonctionnalités des modèles

La page Models assemble le modèle virtuel `omway` à partir des modèles découverts sur les identifiants de fournisseurs activés. Définissez une fois l'ordre de priorité de ses membres, puis utilisez `omway` depuis n'importe quel SDK pris en charge. Omni Gateway équilibre la charge entre les identifiants sains prenant en charge le premier modèle et continue à travers l'ordre configuré lorsque ce modèle est indisponible. Les ID de modèles spécifiques des fournisseurs restent accessibles pour les clients nécessitant une sélection déterministe. Enregistrer une sélection vide désactive `omway` sans impacter les identifiants des fournisseurs.

La découverte de modèles tient compte du fournisseur : un modèle partagé peut être alimenté par plusieurs fournisseurs, tandis que les modèles propres à un fournisseur n'utilisent que des identifiants compatibles. Chaque identifiant vérifié conserve son propre catalogue de fournisseur, et le routeur accorde la priorité au support explicitement déclaré par l'identifiant plutôt qu'aux déductions génériques. Actualiser le catalogue revérifie la disponibilité actuelle du fournisseur ; les sélections indisponibles restent visibles dans la configuration jusqu'à leur rétablissement ou suppression.

Lorsqu'un upstream renvoie une erreur `404` pour un modèle concret, Omni Gateway enregistre une route indisponible pour cet identifiant et ce modèle au lieu de désactiver l'ensemble du fournisseur. Cette route est immédiatement et temporairement évitée, et demeure visible dans **Routes de modèles indisponibles** jusqu'à ce qu'elle soit supprimée ou que l'identifiant soit revalidé. Cela évite que les restrictions d'abonnement ou régionales d'un compte n'affectent les autres comptes sains du même fournisseur. Si aucun identifiant activé ne déclare ou ne permet de déduire la prise en charge d'un modèle demandé, la passerelle renvoie une erreur explicite d'absence d'identifiant compatible au lieu d'envoyer la requête à un fournisseur aléatoire.

Omni Gateway interprète les préfixes et suffixes de fonctionnalités dans les noms de modèles :

- `fake-streaming/{model}` ou le préfixe de pseudo-streaming configuré pour les clients exigeant obligatoirement une sortie SSE.
- `streaming-anti-truncation/{model}` ou le préfixe anti-troncature configuré pour la récupération automatique lors de longs flux.
- Suffixes de réflexion (thinking) comme `-high`, `-medium`, `-low`, `-minimal` et `-max` pour les modèles compatibles de la famille Gemini.
- Suffixes de recherche comme `-search` pour les modèles prenant en charge l'ancrage Google Search (grounding).

Les adaptateurs de fournisseurs normalisent ces noms de fonctionnalités avant de transmettre les requêtes vers l'upstream.

## Visibilité de l'utilisation et des coûts

Omni Gateway enregistre le volume de requêtes, le taux de réussite, l'attribution par identifiant, l'utilisation de tokens signalée par le fournisseur et l'estimation des tokens économisés par la compression de contexte pour chaque plage temporelle du tableau de bord. Les économies par compression sont indiquées comme des estimations car les tokeniseurs et les règles de facturation des fournisseurs font autorité. Le routage basé sur les prix des fournisseurs est volontairement réservé en tant que future couche de politique afin que l'API centrale demeure stable au fur et à mesure de l'ajout de nouveaux fournisseurs.

## Flux de travail des identifiants

1. Démarrez Omni Gateway.
2. Ouvrez `http://IP_DE_VOTRE_SERVEUR:4283` sur VPS, ou `http://127.0.0.1:4283` en développement local.
3. Créez le mot de passe de console sur l'écran de configuration initiale. Pour une configuration distante, saisissez le bootstrap token depuis les journaux d'application ; ou préconfigurez `PANEL_PASSWORD`.
4. Ajoutez un compte, une clé API ou une connexion Ollama depuis la page Providers.
5. Vérifiez les identifiants et observez l'état des cooldowns/erreurs dans la console.
6. Pointez votre outil de programmation vers l'une des interfaces API décrites ci-dessus.

Lors de l'ajout d'un identifiant Google Antigravity, Google redirige le navigateur vers `http://localhost:4283/callback` après connexion. Sur une machine locale, Omni Gateway affiche une page de succès OAuth. Sur un VPS, cette adresse `localhost` correspondant à la machine du navigateur de l'utilisateur, la page peut ne pas charger ; copiez l'URL complète depuis la barre d'adresse du navigateur, revenez sur la page Providers, collez-la dans `Callback URL` et cliquez sur `Save credential`.

Google AI Studio utilise une authentification par clé API au lieu d'OAuth. Ajoutez une clé depuis la page Providers ; Omni Gateway la valide par rapport au catalogue de modèles de Google, la stocke comme identifiant de fournisseur et route les requêtes Gemini ou Gemma compatibles à travers elle. Le routeur intelligent peut basculer entre AI Studio et Google Antigravity pour les modèles Gemini partagés tout en maintenant les modèles propriétaires sur des identifiants compatibles.

L'importation par lot de Google AI Studio accepte les fichiers JSON et les archives ZIP contenant des fichiers JSON. Un document JSON peut contenir une clé unique, un tableau `api_keys` ou un tableau d'objets de clé :

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Chaque clé importée est validée avant enregistrement. Les clés en double au sein d'un même import sont ignorées, les clés existantes sont revalidées et mises à jour, et les entrées invalides sont signalées sans exposer la valeur brute de la clé.

Grok Build prend en charge les identifiants OAuth PKCE, tandis que SpaceXAI Console prend en charge les clés API. Les clés SpaceXAI Console sont validées par rapport au catalogue de modèles Grok Build avant enregistrement. Pour Grok Build OAuth, Omni Gateway génère un lien d'autorisation ; après autorisation, copiez le code affiché sur la page Grok Build et collez-le dans le formulaire Grok Build OAuth. Les tokens d'accès sont renouvelés automatiquement lorsqu'un refresh token est disponible, et les deux types d'identifiants n'exposent que les modèles Grok Build déclarés par leur catalogue actuel. La page Pool permet de récupérer l'utilisation mensuelle des crédits et, lorsque xAI la fournit, l'utilisation hebdomadaire des comptes Grok Build OAuth. Cette vue de facturation au niveau du compte n'est pas disponible pour les clés API SpaceXAI Console.

Codex utilise le flux d'autorisation d'appareils d'OpenAI. Générez un code d'appareil depuis la page Providers, ouvrez l'URL de vérification affichée, saisissez le code, terminez la connexion et revenez vérifier l'autorisation. Omni Gateway stocke le catalogue de modèles de compte renvoyé par Codex, rafraîchit les tokens d'accès OAuth si nécessaire et achemine les requêtes compatibles via le transport Codex Responses. OpenAI Platform utilise une authentification par clé API ; les clés sont validées via le catalogue de modèles de compte avant d'intégrer le pool. Les deux produits prennent en charge l'importation JSON et ZIP avec validation et déduplication propres à chaque fournisseur.

Claude Code utilise le flux OAuth PKCE d'Anthropic. Générez un lien d'autorisation, complétez l'autorisation, puis collez le code d'autorisation obtenu dans la page Providers. Claude Platform accepte les clés API Anthropic. Les deux produits découvrent les modèles exposés pour chaque identifiant, utilisent le transport Anthropic Messages, rafraîchissent les tokens d'accès Claude Code lorsque possible et prennent en charge l'importation validée en JSON ou ZIP.

Les connexions Ollama sont configurées par point de terminaison et peuvent inclure une clé API Bearer optionnelle pour les serveurs protégés ou dans le cloud. Omni Gateway découvre les modèles via `/api/tags` et achemine l'inférence via `/api/chat`. Quand Omni Gateway s'exécute dans Docker, `localhost` fait référence au conteneur lui-même ; utilisez une adresse host-gateway ou un point de terminaison Ollama accessible sur le réseau.

Les imports du Pool et les imports par lot de Google Antigravity acceptent des archives jusqu'à 10 Mo, au maximum 500 fichiers, 2 Mo par fichier d'identifiant individuel et 25 Mo de données décompressées au total. Les imports de fournisseurs Google AI Studio, OpenAI, Anthropic et Ollama appliquent des limites plus strictes de 2 Mo par fichier importé, 200 entrées JSON et 5 Mo de données décompressées.

La page Pool offre également un flux de sauvegarde indépendant du fournisseur. `Download ZIP` exporte l'intégralité du pool d'identifiants actifs, et `Import ZIP` restaure cette archive en identifiant automatiquement chaque identifiant comme Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform ou Ollama. Les comptes OAuth conservent la déduplication d'identité dans le périmètre du fournisseur, tandis que les clés API sont validées et dédupliquées par une empreinte de hachage irréversible par fournisseur. Les entrées non prises en charge ou malformées sont signalées individuellement sans bloquer les autres identifiants valides de l'archive.

Les identifiants Google Antigravity utilisent `google-antigravity-{account_fingerprint}.json`, où l'empreinte est dérivée de l'e-mail normalisé sans l'exposer. Les identifiants Google AI Studio utilisent `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth utilise `grok-{account_fingerprint}.json`, SpaceXAI Console utilise `xai-console-{key_fingerprint}.json`, Codex utilise `openai-codex-{account_fingerprint}.json`, OpenAI Platform utilise `openai-platform-{key_fingerprint}.json`, Claude Code utilise `claude-code-{account_fingerprint}.json`, Claude Platform utilise `claude-platform-{key_fingerprint}.json` et les connexions Ollama utilisent `ollama-{connection_fingerprint}.json`. Les identifiants historiques `provider_*.json` et `xai-grok-*.json` demeurent compatibles et sont exportés avec des noms canoniques.

Noms des modes d'identifiants :

- `code_assist` : pool d'identifiants standard Code Assist.
- `provider` : pool d'identifiants de backend de fournisseur.

## Stockage

Les déploiements mono-processus utilisent le stockage SQLite dans le répertoire de données monté. Dans Docker, veillez à monter `/app/backend/data/creds` et `/app/backend/data/logs` sur des chemins durables de l'hôte tels que `/opt/omni-gateway/creds` et `/opt/omni-gateway/logs`.

MongoDB ou PostgreSQL peuvent remplacer SQLite local selon les préférences d'exploitation ou les tests de migration :

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

Redis peut être ajouté pour accélérer le cache et les sessions :

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Le stockage externe ne rend pas le runtime 1.x évolutif horizontalement (horizontal scaling). Conservez un seul worker et une seule réplique jusqu'à ce que la réservation distribuée d'identifiants, les cooldowns, l'invalidation de sessions et l'agrégation d'utilisation soient implémentés. Configurez soit MongoDB soit PostgreSQL, jamais les deux à la fois ; un échec d'initialisation de base de données externe arrêtera explicitement le démarrage au lieu de basculer silencieusement sur SQLite.

L'importation d'identifiants depuis les variables d'environnement est disponible depuis la console. Définissez l'une des variables suivantes avec une chaîne JSON brute ou utilisez la variante `_B64` correspondante pour une chaîne JSON encodée en base64 :

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

La charge utile peut être un objet d'identifiant unique, un tableau ou `{ "credentials": [...] }`.

## Développement

Cette section s'adresse aux contributeurs et au débogage local. Les déploiements en production doivent utiliser Docker avec des volumes hôtes persistants.

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

Démarrez le service une fois l'ensemble des vérifications réussies :

```bash
python backend/main.py
```

Le standard de production est Python 3.12, et l'intégration continue vérifie actuellement Python 3.12 et 3.14. Consultez [Contribution](../../CONTRIBUTING.md) pour le cycle de vie des pull requests et les critères de revue de code.

## Notes de déploiement

- Ne committez jamais de fichiers JSON d'identifiants ni de fichiers `.env`.
- Utilisez une `API_KEY` dédiée pour les intégrations clientes et un `PANEL_PASSWORD` distinct pour l'accès à la console.
- Restreignez l'accès au volume d'identifiants ou à la base de données externe et activez le chiffrement au repos (encryption at rest) ; les tokens des fournisseurs doivent pouvoir être relus par le routeur.
- Placez Omni Gateway derrière un reverse proxy avec TLS lorsqu'il est accessible au-delà de localhost.
- Configurez le reverse proxy pour préserver `Host` et transmettre `X-Forwarded-Proto` ; définissez `PANEL_COOKIE_SECURE=true` lorsque la terminaison HTTPS est garantie.
- Ne définissez `TRUST_PROXY_HEADERS=true` que si le service n'est accessible qu'à travers un proxy de confiance qui écrase `X-Forwarded-For` et `X-Forwarded-Proto`.
- Utilisez `GET /health` pour les sondes de vivacité (liveness probe) et `GET /ready` pour les vérifications de disponibilité avec état du stockage (readiness probe).
- L'image Docker ne s'exécute en root que le temps nécessaire pour ajuster les permissions du répertoire de données monté, puis bascule sur l'utilisateur non privilégié `gateway`.
- Définissez `CORS_ORIGINS` avec des origines de confiance explicites lorsque les clients navigateurs requièrent un accès cross-origin.
- Conservez des sauvegardes de `/opt/omni-gateway` ou de votre `DATA_DIR` avant toute mise à niveau ou migration de serveur.
- La publication d'images Docker utilise les secrets de dépôt `DOCKERHUB_USERNAME` et `DOCKERHUB_TOKEN` pour Docker Hub, et le `GITHUB_TOKEN` intégré pour GitHub Packages sous `ghcr.io/nguywnben/omni-gateway`. Ne définissez la variable optionnelle `IMAGE_NAME` que lors de la publication vers un nom d'image Docker Hub personnalisé.
- Conservez `WORKERS=1` et une seule réplique d'application pour toute la série 1.x ; le stockage externe ne remplace pas la coordination distribuée.
- Utilisez les routes de gestion canoniques `/api/credentials`. Les alias `/api/creds` de la phase bêta ont été supprimés en 1.0.0.
- Suivez le guide [Mise à niveau vers 1.0](../upgrading-to-1.0.md) avant de migrer un déploiement bêta.
- Suivez le [guide de mise à jour](../updating.md) lors de la mise à niveau d'une instance déployée ou d'un retour arrière (rollback).
- Suivez la [checklist de release](../release-checklist.md) maintenue avant d'apposer un tag ou de publier une image.
- Alignez les politiques de rétention des journaux et de rotation des identifiants avec vos limites d'utilisation.
- Révoquez et renouvelez immédiatement les identifiants si un analyseur de sécurité détecte une fuite de secrets.
- Le Render Blueprint utilise un service payant doté d'un disque persistant. Les services gratuits de Render utilisent un système de fichiers éphémère et ne conviennent qu'aux évaluations temporaires.

## Communauté et santé du projet

- Lisez le guide de [Contribution](../../CONTRIBUTING.md) avant d'ouvrir une pull request.
- Signalez toute vulnérabilité de sécurité via la procédure privée décrite dans la [Politique de sécurité](../../SECURITY.md).
- Consultez le [Journal des modifications](../../CHANGELOG.md) pour le détail des changements par version.
- Respectez le [Code de conduite](../../CODE_OF_CONDUCT.md) dans tous les espaces du projet.

## Remerciements et inspirations

Omni Gateway s'appuie sur le travail de la communauté open source dans les domaines du routage d'IA, de la télémétrie et des passerelles. Nous exprimons notre profonde gratitude aux créateurs et mainteneurs des projets suivants :

| Projet | Description | Étoiles |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Source d'inspiration pour la gestion multi-fournisseurs de clés et l'agrégation d'API basée sur le web | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Pionnier de la couche de proxy multi-format et de la traduction de protocoles pour CLI de codage IA | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Référence pour le proxy LLM unifié, l'équilibrage de charge et le routage de basculement | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Architecture de passerelle IA ultra-rapide, stratégies de routage et modèles de basculement résilients | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Plateforme d'ingénierie LLM open source, traçage, observabilité et ingestion de métriques | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Licence

Omni Gateway est publié sous la [Licence MIT](../../LICENSE).
