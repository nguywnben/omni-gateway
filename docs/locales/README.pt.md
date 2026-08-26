<div align="center">
  <h1>
    <img src="../../frontend/assets/logo.png" alt="Omni Gateway Logo" width="48" height="48" style="vertical-align: middle;" /> <span style="vertical-align: middle;">Omni Gateway</span>
  </h1>
  <p><b>Roteador universal de IA e gateway multiprovedor unificado para ferramentas de código com IA</b></p>

  <p>
    <a href="https://github.com/nguywnben/omni-gateway/releases"><img src="https://img.shields.io/github/v/release/nguywnben/omni-gateway?style=flat-square&color=blue" alt="Release"></a>
    <a href="https://github.com/nguywnben/omni-gateway/blob/main/LICENSE"><img src="https://img.shields.io/github/license/nguywnben/omni-gateway?style=flat-square&color=green" alt="License"></a>
    <a href="https://github.com/nguywnben/omni-gateway/actions"><img src="https://img.shields.io/github/actions/workflow/status/nguywnben/omni-gateway/ci.yml?branch=main&style=flat-square&label=CI" alt="CI Status"></a>
    <a href="https://hub.docker.com/r/nguywnben/omni-gateway"><img src="https://img.shields.io/docker/pulls/nguywnben/omni-gateway?style=flat-square&logo=docker" alt="Docker Pulls"></a>
    <img src="https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.12 | 3.14">
    <img src="https://img.shields.io/badge/i18n-15%20languages-orange?style=flat-square" alt="15 Languages">
  </p>

  <p>
    <a href="#provedores-suportados"><b>🌐 Provedores suportados</b></a> •
    <a href="#recursos-principais"><b>⚡ Recursos principais</b></a> •
    <a href="#implantacao"><b>🐳 Implantação Docker</b></a> •
    <a href="#inicio-rapido-integracao-sdk"><b>🔌 Integração SDK</b></a> •
    <a href="../architecture.md"><b>📖 Arquitetura</b></a>
  </p>

  <p>
    <b>Idiomas do Console e Documentação:</b><br>
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
    <b>Português</b> •
    <a href="README.ru.md">Русский</a> •
    <a href="README.id.md">Indonesia</a> •
    <a href="README.th.md">ภาษาไทย</a> •
    <a href="README.tr.md">Türkçe</a>
  </p>
</div>

---

Um roteador de IA universal para ferramentas de código. O Omni Gateway oferece failover automático inteligente (smart auto-fallback), limpeza de contexto com reconhecimento de tokens, visibilidade de uso e tradução contínua de formatos para que agentes locais, assistentes de IDE e scripts de automação possam aproveitar capacidades LLM gratuitas e pagas através de uma única interface estável de API.

> **Project status:** Stable. Version `1.4.0` adds enterprise governance and FinOps: virtual API keys with budgets and rate limits, a per-call USD cost ledger backed by a maintained pricing table, optional guardrails and response caching, three new routing strategies, a Prometheus metrics endpoint, Langfuse trace export, and a Helm chart — while preserving the stable SDK routes, canonical management routes, configuration names, and single-instance runtime contract established in `1.0.0`.

## Por que o Omni Gateway

Fluxos de trabalho de desenvolvimento modernos costumam misturar múltiplos clientes e provedores: ferramentas compatíveis com OpenAI, SDKs nativos do Gemini, agentes no estilo Anthropic, credenciais respaldadas pelo Google e rotas de modelos experimentais. O Omni Gateway atua entre esses clientes e os backends dos modelos, permitindo que cada ferramenta continue se comunicando no formato que já compreende, enquanto o gateway gerencia roteamento, novas tentativas (retries), limpeza de solicitações e normalização de respostas.

## <a id="recursos-principais"></a>Recursos principais

- **Failover automático inteligente (Smart auto-fallback):** Reserva credenciais por solicitação, distribui o tráfego concorrente, registra cada tentativa para rotação justa e contorna automaticamente falhas recentes, períodos de espera (cooldowns), limites de taxa e limites de cota esgotados.
- **Limpeza com reconhecimento de tokens:** Normaliza payloads e apara apenas prefixos de conversas excessivamente longos em limites seguros de turnos, preservando instruções de sistema, definições de ferramentas e contexto recente.
- **Tradução de formatos:** Aceita OpenAI Chat Completions e Responses, solicitações nativas do Gemini e Anthropic Messages, traduzindo requisições e streaming de respostas perfeitamente entre todos os formatos.
- **Orquestração de credenciais:** Gerencia contas OAuth e chaves de API com status de integridade, rastreamento de cooldown, validação, desduplicação e failover inteligente por provedor.
- **Roteamento de modelos em nível de credencial:** Mantém um catálogo de capacidades separado para cada credencial, evitando que uma permissão de conta envie requisições para outra conta que não ofereça o modelo selecionado.
- **Memória de integridade de rotas:** Registra respostas de modelo não encontrado no escopo da credencial e exibe as rotas afetadas para recuperação na página Models.
- **Resiliência em streaming:** Suporta streaming SSE, pseudo-streaming para clientes que exigem fluxo obrigatório de dados e tentativas contra truncamento (anti-truncation) para gerações longas.
- **Painel de controle:** Acompanha console web para gerenciar credenciais, registros de log, configurações, métricas de uso e informações sobre versões.

## Prévia do Console

![Omni Gateway credential pool](../assets/screenshots/credential-pool.png)

## <a id="provedores-suportados"></a>Provedores suportados

O Omni Gateway adapta requisições de forma transparente entre os principais provedores de IA, runtimes locais e endpoints OAuth:

| Provedor | Tipo de Autenticação | Protocolos Suportados | Auto-Failover | Suporte a Streaming |
| :--- | :---: | :---: | :---: | :---: |
| <img src="../../frontend/assets/providers/google-antigravity-logo.png" width="18" height="18" valign="middle" /> **Google Antigravity** | OAuth (Google) | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/google-ai-studio-logo.png" width="18" height="18" valign="middle" /> **Google AI Studio** | Chave de API | Gemini Native, OpenAI, Anthropic | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-code-logo.png" width="18" height="18" valign="middle" /> **Claude Code** | OAuth (Anthropic) | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/claude-platform-logo.png" width="18" height="18" valign="middle" /> **Claude Platform** | Chave de API | Anthropic Messages, OpenAI, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/codex-logo.png" width="18" height="18" valign="middle" /> **Codex** | OAuth (OpenAI) | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/openai-platform-logo.png" width="18" height="18" valign="middle" /> **OpenAI Platform** | Chave de API | OpenAI Completions & Responses | ✅ | ✅ |
| <img src="../../frontend/assets/providers/grok-build-logo.png" width="18" height="18" valign="middle" /> **Grok Build** | Chave de API | Compatível com OpenAI, Anthropic, Gemini | ✅ | ✅ |
| <img src="../../frontend/assets/providers/spacexai-console-logo.png" width="18" height="18" valign="middle" /> **SpaceXAI Console** | Chave de API | Compatível com OpenAI | ✅ | ✅ |
| <img src="../../frontend/assets/providers/ollama-logo.png" width="18" height="18" valign="middle" /> **Ollama (Local / Auto-hospedado)** | Local / URL Base | Compatível com OpenAI | ✅ | ✅ |

## Arquitetura

```text
client tools
  OpenAI SDKs | Google GenAI SDKs | Anthropic SDKs | Integrações de IDE
        |
        v
Omni Gateway
  autenticação -> tradução de formatos -> limpeza consciente de tokens -> roteamento -> failover -> streaming
        |
        v
provider adapters
  Google Antigravity | Google AI Studio | Grok Build | SpaceXAI Console | Codex | OpenAI Platform | Claude Code | Claude Platform | Ollama
```

A API pública permanece estável enquanto os adaptadores específicos de cada provedor evoluem sob o Omni Gateway.

## Estrutura do Repositório

```text
backend/       Raiz de composição FastAPI, núcleo de roteamento, tradutores, armazenamento e testes
frontend/      Marcação do console administrativo, estilos, scripts e recursos visuais dos provedores
deploy/        Definições de contêineres, manifestos de plataformas e scripts do sistema operacional
docs/          Notas de arquitetura e documentação de manutenção do projeto
.github/       CI, automação de dependências e modelos de contribuição
```

Consulte [Arquitetura](../architecture.md) para saber mais sobre limites de módulos, fluxo de requisições, controle de estado e restrições da versão atual.

## <a id="implantacao"></a>Implantação

O Omni Gateway foi projetado para ambientes de produção reais. O Docker é a abordagem recomendada para ambientes VPS e servidores, pois mantém o runtime isolado e persiste credenciais e registros no host com segurança.

### Docker em uma VPS

Crie primeiro os diretórios persistentes no host:

```bash
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
```

Inicie o serviço:

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

A mesma versão é publicada no GitHub Packages como `ghcr.io/nguywnben/omni-gateway:1.4.0`. A tag `latest` aponta para a versão estável mais recente; `edge` aponta para compilações verificadas, mas não lançadas, da branch `main`. Fixe uma tag de versão ou digest para implantações reproduzíveis.

Abra o painel de controle em:

```text
http://IP_DO_SEU_SERVIDOR:4283
```

Na primeira execução, crie a senha do console na tela de configuração inicial. Nenhuma senha padrão é fornecida de fábrica. Um navegador remoto também deve inserir o token de inicialização (bootstrap token) exibido em `docker logs omni-gateway`; a configuração direta no localhost dispensa o token. Defina `SETUP_TOKEN` antes de iniciar caso a automação de deploy exija um token fixo.

Senhas gerenciadas pela aplicação são salvas como hashes scrypt com salt, sessões do painel usam cookies HttpOnly e requisições públicas de SDKs autenticam com a chave de API gerada no formato `sk-ogw-`. Para deploys não interativos, configure previamente `PANEL_PASSWORD` para ignorar a tela de configuração inicial.

O contêiner `1.4.0` foi lançado para a arquitetura `linux/amd64`. A publicação ARM64 está temporariamente em pausa até que todas as dependências de provedores, incluindo a pilha de transporte Vertex, possam ser compiladas e testadas com o mesmo padrão.

Se o firewall do servidor estiver ativo, libere a porta do gateway:

```bash
sudo ufw allow 4283/tcp
```

Visualizar logs:

```bash
sudo docker logs -f omni-gateway
```

Atualizar para a imagem estável mais recente:

```bash
sudo docker pull nguywnben/omni-gateway:latest
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Em seguida, inicie o contêiner novamente com o mesmo comando `docker run` acima. Os diretórios montados em `/opt/omni-gateway` preservam credenciais, configurações, dados de uso e logs entre atualizações de contêiner.

### Docker Compose

Para implantações baseadas no repositório:

```bash
git clone https://github.com/nguywnben/omni-gateway.git
cd omni-gateway
sudo mkdir -p /opt/omni-gateway/creds /opt/omni-gateway/logs
docker compose -f deploy/docker-compose.yml up -d
```

O arquivo compose incluso obtém `nguywnben/omni-gateway:latest` e usa `/opt/omni-gateway` por padrão para dados persistentes do host. Defina `IMAGE=nguywnben/omni-gateway:1.4.0` para fixar esta versão e defina `DATA_DIR=/caminho/personalizado` se o servidor usar outro local de armazenamento.

O Compose repassa `API_KEY`, `PANEL_PASSWORD`, `SETUP_TOKEN`, URIs de armazenamento externo e `PROXY` do shell ou de um arquivo `.env` na raiz. Deixe-os vazios para manter a geração automática de chave, a configuração no primeiro uso, o banco de dados SQLite local e conexões diretas de rede.


### Kubernetes (Helm)

A Helm chart is provided at `deploy/helm/omni-gateway` with a persistent volume for credentials and the usage ledger, liveness/readiness probes, optional Ingress, and an optional Prometheus ServiceMonitor wired to `/metrics`:

```bash
helm install omni-gateway deploy/helm/omni-gateway \
  --set secrets.panelPassword=change-me
```

The chart deploys exactly one replica with a `Recreate` strategy because the 1.x runtime holds routing and rate-limit state in process memory. Do not scale the Deployment horizontally.

### Desenvolvimento Local

Utilize o fluxo de desenvolvimento em Python ao criar recursos ou depurar o gateway localmente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
cp .env.example .env
python backend/main.py
```

No Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --require-hashes -r requirements.lock
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python backend/main.py
```

Abra o painel de controle em:

```text
http://127.0.0.1:4283
```

O ambiente de desenvolvimento local utiliza a mesma tela de configuração inicial do deploy Docker.

## Configuração

O Omni Gateway lê as configurações primeiro a partir de variáveis de ambiente, depois das configurações salvas e, por fim, dos valores padrão.

| Variável | Padrão | Finalidade |
| --- | --- | --- |
| `HOST` | `0.0.0.0` | Endereço de escuta (bind address). |
| `PORT` | `4283` | Porta HTTP. |
| `HOST_PORT` | `4283` | Porta do lado do host usada apenas pelo Docker Compose. |
| `WORKERS` | `1` | Quantidade de workers suportada para a série 1.x. Outros valores são rejeitados até que reservas, cooldowns, sessões e agregação de métricas sejam coordenados entre processos. |
| `CORS_ORIGINS` | vazio | Lista separada por vírgulas de origens de navegador autorizadas para chamadas de API cross-origin. Deixe vazio para uso no mesmo domínio (same-origin). |
| `CORS_ORIGIN_REGEX` | vazio | Expressão regular opcional para origens dinâmicas gerenciadas no navegador. |
| `API_KEY` | gerada automaticamente | Chave principal para requisições públicas de clientes da API. Deve iniciar com `sk-ogw-`. |
| `PANEL_PASSWORD` | vazio até configuração | Senha para o painel de controle web. |
| `SETUP_TOKEN` | gerado por processo | Token de inicialização fixo opcional para configuração remota no primeiro uso. Quando omitido, leia o token gerado nos logs da aplicação ou contêiner. |
| `PANEL_SESSION_TTL_SECONDS` | `86400` | Duração da sessão do console web em segundos. |
| `PANEL_COOKIE_SECURE` | automático | Defina como `true` para exigir cookies seguros apenas via HTTPS. Deixe vazio para detectar HTTPS via `X-Forwarded-Proto`. |
| `PANEL_LOGIN_WINDOW_SECONDS` | `300` | Janela de limitação de taxa de login em segundos. |
| `PANEL_LOGIN_MAX_ATTEMPTS` | `10` | Tentativas de login falhas permitidas por cliente dentro da janela de taxa. |
| `PANEL_LOGIN_MAX_TRACKED_CLIENTS` | `10000` | Limite de endereços de clientes retidos pelo limitador de login em memória. |
| `MAX_REQUEST_BODY_MB` | `64` | Tamanho máximo do corpo da requisição HTTP em MiB. Requisições de SDK que excederem o limite retornam o envelope de erro nativo do protocolo. |
| `TRUST_PROXY_HEADERS` | `false` | Aceitar headers de encaminhamento de cliente/protocolo apenas de um proxy reverso confiável que os sobrescreva. |
| `CREDENTIALS_DIR` | `./backend/data/creds` | Diretório de armazenamento de credenciais. No Docker, mantenha `/app/backend/data/creds` persistido com volume host. |
| `CODE_ASSIST_ENDPOINT` | `https://cloudcode-pa.googleapis.com` | Endpoint backend do Code Assist. |
| `ANTIGRAVITY_API_URL` | `https://daily-cloudcode-pa.googleapis.com` | Endpoint backend do Google Antigravity. |
| `PROXY` | vazio | Proxy HTTP, HTTPS ou SOCKS opcional. |
| `RETRY_429_ENABLED` | `true` | Ativa tentativas limitadas para limites de taxa e falhas temporárias no upstream. Nome legado mantido por compatibilidade. |
| `RETRY_429_MAX_RETRIES` | `5` | Número máximo de novas tentativas para falhas transitórias no upstream. |
| `RETRY_429_INTERVAL` | `1` | Intervalo base entre tentativas transitórias em segundos. |
| `AUTO_DISABLE` | `false` | Desativa credenciais após falhas graves configuradas. |
| `AUTO_DISABLE_ERROR_CODES` | `403` | Lista de códigos de status de falha grave separados por vírgula. |
| `ROUTING_STRATEGY` | `balanced` | Credential selection policy: `balanced`, `priority`, `weighted`, `least_latency`, or `lowest_cost`. |
| `PREFERRED_PROVIDER` | vazio | Provedor preferido pela estratégia `priority`, como `google_antigravity` ou `google_ai_studio`. |
| `UPSTREAM_TIMEOUT_SECONDS` | `300` | Tempo limite de inferência do provedor, limitado entre 5 e 900 segundos. |
| `RESPONSE_CACHE_ENABLED` | `false` | Cache deterministic (temperature 0) non-streaming responses in memory. |
| `RESPONSE_CACHE_TTL_SECONDS` | `300` | Response cache entry lifetime in seconds. |
| `RESPONSE_CACHE_MAX_ENTRIES` | `1000` | Maximum responses held by the in-memory cache. |
| `GUARDRAILS_ENABLED` | `false` | Enable the pre-call guardrails pipeline. |
| `GUARDRAILS_PII_MASKING_ENABLED` | `true` | Mask emails, card numbers, and API keys in outbound request text. |
| `GUARDRAILS_INJECTION_DETECTION_ENABLED` | `true` | Reject prompt-injection attempts with HTTP 400. |
| `GUARDRAILS_BLOCKED_KEYWORDS` | empty | Comma-separated case-insensitive keywords that block a request. |
| `ANTI_TRUNCATION_MAX_ATTEMPTS` | `3` | Tentativas máximas de continuação para o streaming anti-truncamento. |
| `TOKEN_COMPRESSION_ENABLED` | `true` | Comprime histórico de conversa excessivo antes de rotear ao provedor. |
| `TOKEN_COMPRESSION_THRESHOLD` | `32000` | Limite estimado de tokens de entrada para acionar a compressão. |
| `TOKEN_COMPRESSION_TARGET` | `24000` | Meta de tokens de entrada após a compressão. Deve ser menor que o limite. |
| `TOKEN_COMPRESSION_MIN_RECENT_TURNS` | `4` | Número mínimo de turnos recentes do usuário mantidos durante a compressão. |
| `COMPATIBILITY_MODE` | `false` | Converte mensagens de sistema para clientes/modelos que não as suportam. |
| `RETURN_THOUGHTS_TO_FRONTEND` | `true` | Retorna campos de raciocínio (reasoning) do modelo quando disponíveis. |
| `MONGODB_URI` | vazio | Habilita armazenamento no MongoDB quando configurado. |
| `POSTGRESQL_URI` | vazio | Habilita armazenamento no PostgreSQL quando configurado. |
| `REDIS_URL` | vazio | Habilita cache / estado de sessão no Redis quando configurado. |
| `CODE_ASSIST_CLIENT_ID` | cliente desktop integrado | Substituição opcional do Client ID OAuth do Code Assist. |
| `CODE_ASSIST_CLIENT_SECRET` | cliente desktop integrado | Substituição opcional do Client Secret OAuth do Code Assist. |
| `ANTIGRAVITY_CLIENT_ID` | cliente desktop integrado | Substituição opcional do Client ID OAuth do Google Antigravity. Gerenciável na página Providers. |
| `ANTIGRAVITY_CLIENT_SECRET` | cliente desktop integrado | Substituição opcional do Client Secret OAuth do Google Antigravity. Configurável via env ou na página Providers. |
| `GOOGLE_AI_STUDIO_API_URL` | `https://generativelanguage.googleapis.com` | Substituição opcional do endpoint Generative Language API do Google AI Studio. |
| `XAI_API_URL` | `https://api.x.ai/v1` | Substituição opcional do endpoint SpaceXAI Console API para chaves de API. Gerenciável na página Providers. |
| `XAI_OAUTH_API_URL` | `https://cli-chat-proxy.grok.com/v1` | Substituição opcional do endpoint de assinatura OAuth do Grok Build. |
| `XAI_OAUTH_ISSUER` | `https://auth.x.ai` | Substituição opcional do emissor OAuth do Grok Build. Somente hosts HTTPS em `x.ai` são aceitos. |
| `XAI_CLIENT_ID` | cliente público integrado | Substituição opcional do Client ID OAuth PKCE do Grok Build. |
| `XAI_USER_AGENT` | `grok-cli/omni-gateway` | Substituição opcional do HTTP User-Agent compartilhado para requisições Grok Build OAuth e SpaceXAI Console API. |
| `OPENAI_API_URL` | `https://api.openai.com/v1` | Substituição opcional do endpoint de API da OpenAI Platform. Gerenciável na página Providers. |
| `CODEX_API_URL` | `https://chatgpt.com/backend-api/codex` | Substituição opcional do endpoint de inferência e catálogo de modelos de conta do Codex. |
| `CODEX_USAGE_URL` | `https://chatgpt.com/backend-api/wham/usage` | Substituição opcional do endpoint de limites de taxa de conta do Codex. |
| `CODEX_AUTH_BASE` | `https://auth.openai.com` | Substituição opcional do serviço de autorização de dispositivos do Codex. |
| `CODEX_CLIENT_ID` | cliente público integrado | Substituição opcional do Client ID OAuth de dispositivo do Codex. |
| `CODEX_USER_AGENT` | valor compatível com Codex CLI | Substituição opcional do User-Agent para requisições do Codex. |
| `ANTHROPIC_API_URL` | `https://api.anthropic.com/v1` | Substituição opcional do endpoint Messages API da Claude Platform e Claude Code. Gerenciável na página Providers. |
| `CLAUDE_OAUTH_AUTHORIZE_URL` | `https://claude.ai/oauth/authorize` | Substituição opcional do endpoint de autorização PKCE do Claude Code. Apenas hosts Anthropic e Claude são aceitos. |
| `CLAUDE_OAUTH_TOKEN_URL` | `https://api.anthropic.com/v1/oauth/token` | Substituição opcional do endpoint de token do Claude Code. Apenas hosts Anthropic e Claude são aceitos. |
| `CLAUDE_CLIENT_ID` | cliente público integrado | Substituição opcional do Client ID OAuth PKCE do Claude Code. |
| `CLAUDE_USER_AGENT` | `claude-cli/omni-gateway` | Substituição opcional do User-Agent para requisições Claude Code e Claude Platform. |
| `ANTIGRAVITY_USER_AGENT` | `antigravity/cli/1.0.1 windows/amd64` | Substituição opcional do User-Agent de protocolo do Google Antigravity. |
| `ANTIGRAVITY_PAYLOAD_USER_AGENT` | `antigravity` | Substituição opcional do campo userAgent em nível de payload do Google Antigravity. |
| `METRICS_TOKEN` | empty | At least 32 bytes; required with opt-in `PROMETHEUS_EXPORT_ENABLED=true`. |
| `LANGFUSE_PUBLIC_KEY` | empty | Enables Langfuse trace export together with the secret key. |
| `LANGFUSE_SECRET_KEY` | empty | Langfuse secret key for trace export. |
| `LANGFUSE_HOST` | `https://cloud.langfuse.com` | Langfuse ingestion endpoint. |
| `LOG_LEVEL` | `info` | Nível de detalhamento dos logs. |
| `LOG_MAX_MB` | `10` | Tamanho máximo do arquivo de log ativo antes da rotação. |
| `LOG_BACKUP_COUNT` | `3` | Quantidade de arquivos de log rotacionados a serem mantidos. |
| `LOG_FILE` | `./backend/data/logs/omni-gateway.log` | Destino do arquivo de log. No Docker, mantenha `/app/backend/data/logs` persistido com volume host. |

## <a id="inicio-rapido-integracao-sdk"></a>Interfaces SDK

O Omni Gateway é projetado respeitando o comportamento padrão de URL dos SDKs oficiais em Python. Configure cada cliente exatamente como demonstrado abaixo; o gateway não requer prefixos duplicados ou fora do padrão.

Os exemplos usam o modelo virtual `omway`. Configure a ordem de prioridade de fallback na página Models previamente ou substitua por um ID de modelo concreto.

### OpenAI Python SDK

Use `/v1` como base URL para OpenAI. O SDK anexa `/chat/completions` automaticamente.

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:4283/v1", api_key="sk-ogw-...")

response = client.chat.completions.create(
    model="omway",
    messages=[{"role": "user", "content": "Explique este repositório em um parágrafo."}],
)
```

O mesmo cliente também pode utilizar a OpenAI Responses API:

```python
response = client.responses.create(
    model="omway",
    instructions="Seja conciso.",
    input="Explique este repositório em um parágrafo.",
)

print(response.output_text)
```

A compatibilidade com Responses oferece suporte a entradas de texto e imagem, ferramentas de função sem streaming e streaming de texto via SSE. Ferramentas internas hospedadas pela OpenAI, histórico persistido de respostas e chamadas de ferramentas em streaming são rejeitadas explicitamente porque o Omni Gateway não executa, persiste ou descarta silenciosamente esses comportamentos proprietários da OpenAI.

### Anthropic Python SDK

Use a origem do gateway como URL base para a Anthropic. O SDK anexa `/v1/messages` automaticamente.

```python
from anthropic import Anthropic

client = Anthropic(base_url="http://127.0.0.1:4283", api_key="sk-ogw-...")

response = client.messages.create(
    model="omway",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Escreva uma mensagem de commit concisa."}],
)
```

### Google GenAI Python SDK

Use a origem do gateway como URL base para Google GenAI. O SDK anexa a rota padrão do modelo, como `/v1beta/models/{model}:generateContent`.

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
    contents="Escreva uma função simples em Python.",
    config=types.GenerateContentConfig(
        system_instruction="Você é um assistente prestativo.",
    ),
)
```

### Rotas Suportadas

O Omni Gateway expõe rotas compatíveis com SDKs sem a necessidade de prefixos de produtos:

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

Falhas de autenticação, validação de requisições, roteamento, problemas no upstream e erros pré-streaming utilizam o envelope nativo de erros da interface SDK selecionada. Todas as respostas HTTP incluem o cabeçalho `X-Request-ID`; clientes podem enviar um identificador seguro para correlação ponta a ponta. Respostas com limitação de taxa ou indisponibilidade temporária preservam o cabeçalho `Retry-After` quando informado pelo upstream.

## Recursos dos Modelos

A página Models cria o modelo virtual `omway` a partir dos modelos descobertos em credenciais habilitadas dos provedores. Organize seus membros em ordem de prioridade uma única vez e utilize `omway` a partir de qualquer SDK suportado. O Omni Gateway realiza balanceamento entre credenciais saudáveis que suportam o modelo principal e avança na ordem configurada quando o modelo estiver indisponível. Identificadores de modelos concretos permanecem disponíveis para clientes que requerem seleção determinística. Salvar uma seleção vazia desativa `omway` sem impactar as credenciais dos provedores.

A descoberta de modelos é orientada ao provedor: um modelo compartilhado pode ser atendido por múltiplos provedores, enquanto modelos específicos usam apenas credenciais compatíveis. Cada credencial verificada armazena seu próprio catálogo e o roteador prioriza o suporte formalmente declarado da credencial sobre suposições genéricas. Atualizar o catálogo checa a disponibilidade atual do provedor; seleções indisponíveis permanecem na configuração até serem restauradas ou removidas.

Quando um upstream retorna erro `404` para um modelo específico, o Omni Gateway registra uma rota indisponível para essa credencial e modelo em vez de desativar o provedor por inteiro. A rota é evitada temporariamente de imediato e segue listada sob **Unavailable Model Routes** até ser removida ou a credencial revalidada. Isso evita que planos ou restrições regionais de uma conta afetem outras contas no mesmo provedor. Se nenhuma credencial habilitada suportar o modelo solicitado, o gateway retorna um erro claro de ausência de credencial compatível em vez de enviar a requisição a um provedor aleatório.

O Omni Gateway reconhece prefixos e sufixos especiais nos nomes de modelos:

- `fake-streaming/{model}` ou o prefixo de pseudo-streaming configurado para clientes que exigem resposta em SSE.
- `streaming-anti-truncation/{model}` ou o prefixo anti-truncamento configurado para recuperação automática em streaming de respostas longas.
- Sufixos de raciocínio (thinking) como `-high`, `-medium`, `-low`, `-minimal` e `-max` para modelos compatíveis da família Gemini.
- Sufixos de pesquisa como `-search` para modelos com suporte a dados ancorados no Google Search (grounding).

Os adaptadores dos provedores normalizam essas variações antes de encaminhar a requisição ao serviço de origem.

## Uso e Transparência de Custos

Omni Gateway records request volume, success rate, credential attribution, provider-reported token usage, estimated context-compression savings, and an estimated USD cost per call computed from a maintained model pricing table. Override or extend prices by placing a `model_pricing.json` file in the credentials directory; prices are USD per one million tokens. Aggregates are available on the dashboard, per virtual key through the `/api/virtual-keys` management API, and for monitoring systems through the Prometheus `/metrics` endpoint. Compression savings and costs are labeled as estimates because provider tokenizers and billing rules remain authoritative.

Virtual API keys let one gateway serve multiple clients under separate limits. Each key carries optional daily and monthly USD budgets enforced from the cost ledger, requests-per-minute and tokens-per-minute sliding windows, an expiry timestamp, and a model allowlist with glob patterns. Keys are stored as SHA-256 hashes; the plaintext secret is shown exactly once at creation time.

## Fluxo de Trabalho com Credenciais

1. Inicie o Omni Gateway.
2. Abra `http://IP_DO_SEU_SERVIDOR:4283` na VPS ou `http://127.0.0.1:4283` no ambiente de desenvolvimento local.
3. Defina a senha do painel na tela de configuração inicial. Para configuração remota, forneça o bootstrap token dos logs da aplicação ou defina previamente `PANEL_PASSWORD`.
4. Adicione uma conta, chave de API ou conexão Ollama através da página Providers.
5. Valide as credenciais e acompanhe os estados de cooldown e erros no painel.
6. Aponte sua ferramenta de desenvolvimento para uma das interfaces de API descritas acima.

Ao cadastrar credenciais do Google Antigravity, o Google redireciona o navegador para `http://localhost:4283/callback` após o login. Em um computador local, o Omni Gateway exibe a tela de sucesso de autenticação OAuth. Em uma VPS, o endereço `localhost` aponta para o dispositivo do navegador local, o que pode impedir o carregamento da página; copie a URL completa da barra de endereços do navegador, acesse a página Providers, cole em `Callback URL` e clique em `Save credential`.

O Google AI Studio adota autenticação via chave de API em vez de OAuth. Cadastre uma chave na página Providers; o Omni Gateway validará sua conformidade com o catálogo do Google, salvará o registro como credencial e roteará requisições Gemini ou Gemma compatíveis. O roteador inteligente alterna entre AI Studio e Google Antigravity para modelos Gemini compartilhados, mantendo modelos específicos nas credenciais correspondentes.

A importação em lote do Google AI Studio aceita arquivos JSON e arquivos ZIP contendo JSON. O documento JSON pode conter uma única chave, uma lista `api_keys` ou uma lista de objetos de chave:

```json
{
  "provider": "google_ai_studio",
  "api_keys": [
    "YOUR_FIRST_API_KEY",
    "YOUR_SECOND_API_KEY"
  ]
}
```

Cada chave importada é validada antes de ser armazenada. Chaves duplicadas no mesmo lote são desconsideradas, chaves existentes são revalidadas e atualizadas e entradas inválidas são informadas sem expor o valor da chave.

O Grok Build suporta autenticação OAuth PKCE, enquanto o SpaceXAI Console aceita chaves de API. Chaves do SpaceXAI Console são validadas contra o catálogo do Grok Build antes de serem salvas. Para o Grok Build OAuth, o gateway gera um link de autorização; ao concluir, copie o código exibido na página do Grok Build e cole no formulário do console. Tokens de acesso são renovados automaticamente quando um refresh token estiver disponível, e ambos os tipos de credencial expõem somente os modelos declarados em seus catálogos. A página Pool permite consultar o consumo mensal e semanal (se fornecido pela xAI) para contas Grok Build OAuth. Esse detalhamento em nível de conta não se aplica a chaves de API do SpaceXAI Console.

O Codex utiliza o fluxo de autorização de dispositivos da OpenAI. Gere o código de dispositivo na página Providers, acesse a URL indicada, insira o código, conclua a autenticação e retorne para checar a autorização. O Omni Gateway persiste o catálogo de modelos retornado pelo Codex, renova tokens OAuth conforme necessário e envia requisições compatíveis via transporte Codex Responses. A OpenAI Platform utiliza autenticação por chave de API; as chaves são validadas no catálogo da conta antes de ingressarem no pool. Ambos os produtos suportam importação de arquivos JSON e ZIP com validação e desduplicação específicas por provedor.

O Claude Code emprega o fluxo OAuth PKCE da Anthropic. Gere o link de autorização, conclua a autenticação e insira o código retornado na página Providers. A Claude Platform aceita chaves de API da Anthropic. Ambos identificam os modelos acessíveis para cada credencial, utilizam o transporte Anthropic Messages, renovam tokens do Claude Code quando aplicável e suportam importação validada via JSON ou ZIP.

Conexões Ollama são configuradas individualmente por endpoint e aceitam chave bearer opcional para servidores protegidos ou em nuvem. O gateway lista modelos via `/api/tags` e roteia inferências via `/api/chat`. Ao executar o Omni Gateway no Docker, `localhost` refere-se ao contêiner; utilize o endereço do host-gateway ou outro endpoint acessível na rede.

As importações do Pool e do Google Antigravity suportam arquivos compactados de até 10 MB, no máximo 500 arquivos, arquivos individuais de até 2 MB e até 25 MB de dados descompactados. As importações de Google AI Studio, OpenAI, Anthropic e Ollama seguem limites mais restritos: 2 MB por arquivo importado, 200 entradas JSON e 5 MB de dados descompactados.

A página Pool oferece ainda um fluxo de backup universal entre provedores. `Download ZIP` exporta todo o pool ativo e `Import ZIP` restaura o pacote reconhecendo automaticamente cada registro como Google Antigravity, Google AI Studio, Grok Build, SpaceXAI Console, Codex, OpenAI Platform, Claude Code, Claude Platform ou Ollama. Contas OAuth preservam o controle de identidade sem duplicidade por provedor, enquanto chaves de API são validadas e desduplicadas por um fingerprint irreversível. Entradas não suportadas ou inválidas são reportadas isoladamente sem afetar as credenciais válidas do pacote.

Credenciais do Google Antigravity utilizam o padrão `google-antigravity-{account_fingerprint}.json`, onde o fingerprint é gerado com base no e-mail normalizado sem expô-lo. O Google AI Studio adota `google-ai-studio-{key_fingerprint}.json`, Grok Build OAuth adota `grok-{account_fingerprint}.json`, SpaceXAI Console adota `xai-console-{key_fingerprint}.json`, Codex adota `openai-codex-{account_fingerprint}.json`, OpenAI Platform adota `openai-platform-{key_fingerprint}.json`, Claude Code adota `claude-code-{account_fingerprint}.json`, Claude Platform adota `claude-platform-{key_fingerprint}.json` e conexões Ollama adotam `ollama-{connection_fingerprint}.json`. Credenciais legadas nos formatos `provider_*.json` e `xai-grok-*.json` continuam suportadas e são salvas com a nomenclatura canônica.

Nomes dos modos de credencial (Credential mode names):

- `code_assist`: pool padrão de credenciais do Code Assist.
- `provider`: pool de credenciais de backend de provedores.

## Armazenamento

Instâncias em processo único utilizam SQLite no diretório de dados montado. No Docker, mantenha os diretórios `/app/backend/data/creds` e `/app/backend/data/logs` montados em diretórios persistentes do host, como `/opt/omni-gateway/creds` e `/opt/omni-gateway/logs`.

MongoDB ou PostgreSQL podem substituir o SQLite local conforme necessidades operacionais ou testes de migração:

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=omni_gateway
```

```bash
POSTGRESQL_URI=postgresql://user:password@localhost:5432/omni_gateway
```

O Redis pode ser integrado para otimizar cache e controle de sessões:

```bash
REDIS_URL=redis://127.0.0.1:6379/0
```

Bancos de dados externos não tornam a versão 1.x escalável horizontalmente. Mantenha um único worker e uma única réplica até que o controle distribuído de reservas, cooldowns, invalidação de sessões e agregação de dados seja introduzido. Configure apenas um banco: MongoDB ou PostgreSQL; falhas de inicialização com bancos externos interrompem o boot em vez de retornar silenciosamente ao SQLite.

A importação de credenciais via ambiente pode ser acionada pelo console. Atribua o JSON bruto a uma das variáveis abaixo ou utilize o sufixo `_B64` para conteúdo codificado em base64:

```bash
CODE_ASSIST_CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
CREDENTIALS_JSON='{"token":"...","refresh_token":"...","client_id":"...","client_secret":"...","project_id":"..."}'
```

O payload pode conter um único objeto de credencial, uma lista de objetos ou a estrutura `{ "credentials": [...] }`.

## Desenvolvimento

Esta seção é destinada a contribuidores e testes locais. Ambientes de produção devem priorizar o Docker com volumes persistentes.

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

Inicie o serviço após a validação bem-sucedida de todas as etapas:

```bash
python backend/main.py
```

A base oficial de produção é o Python 3.12, com pipelines de CI validando compilações em Python 3.12 e 3.14. Consulte o guia de [Contribuição](../../CONTRIBUTING.md) para detalhes sobre fluxo de pull requests e diretrizes de revisão.

## Notas de Implantação

- Nunca versione arquivos JSON com credenciais ou arquivos `.env`.
- Use uma `API_KEY` dedicada para integrações e uma `PANEL_PASSWORD` distinta para a área administrativa.
- Restrinja o acesso ao volume de credenciais ou banco de dados externo e ative criptografia em repouso (encryption at rest); o gateway precisa ler os tokens em texto puro.
- Posicione o Omni Gateway atrás de um reverse proxy com TLS ativo quando acessível fora do ambiente localhost.
- Configure o proxy para manter o header `Host` e repassar `X-Forwarded-Proto`; ative `PANEL_COOKIE_SECURE=true` ao operar com terminação HTTPS.
- Só habilite `TRUST_PROXY_HEADERS=true` se o serviço estiver estritamente atrás de um proxy confiável que reescreva `X-Forwarded-For` e `X-Forwarded-Proto`.
- Use `GET /health` para checagem de integridade (liveness) e `GET /ready` para checagem de prontidão com armazenamento (readiness).
- A imagem Docker inicia com privilégios de root apenas para ajustar permissões no volume montado, transferindo a execução ao usuário não privilegiado `gateway`.
- Defina `CORS_ORIGINS` com origens confiáveis caso clientes de navegador precisem de acesso cross-origin.
- Mantenha backups de `/opt/omni-gateway` ou da pasta `DATA_DIR` antes de atualizações ou migrações de servidor.
- O pipeline de publicação de imagens Docker utiliza os secrets `DOCKERHUB_USERNAME` e `DOCKERHUB_TOKEN` para o Docker Hub, além do `GITHUB_TOKEN` para o GitHub Packages em `ghcr.io/nguywnben/omni-gateway`. Utilize a variável opcional `IMAGE_NAME` apenas para imagens personalizadas no Docker Hub.
- Mantenha `WORKERS=1` e uma única réplica para toda a série 1.x; armazenamento externo não substitui mecanismos de coordenação distribuída.
- Utilize as rotas canônicas de gerenciamento `/api/credentials`. Os aliases beta `/api/creds` foram removidos na versão 1.0.0.
- Consulte o guia [Migrando para a versão 1.0](../upgrading-to-1.0.md) antes de atualizar instâncias beta.
- Siga as instruções de [Atualização](../updating.md) para atualizar uma instância em produção ou reverter versões.
- Siga o [checklist de lançamento](../release-checklist.md) mantido antes de gerar tags ou publicar imagens.
- Alinhe o período de retenção de logs e rotação de credenciais com as cotas contratadas junto aos provedores.
- Revogue e atualize credenciais caso detectores automáticos de segurança apontem vazamento de segredos.
- O Blueprint da Render exige um serviço pago com disco persistente. Serviços gratuitos utilizam armazenamento temporário e destinam-se apenas a testes breves.

## Comunidade e Saúde do Projeto

- Consulte o guia de [Contribuição](../../CONTRIBUTING.md) antes de submeter um pull request.
- Comunique vulnerabilidades de segurança de maneira privada pelo processo da [Política de Segurança](../../SECURITY.md).
- Acompanhe o [Histórico de Alterações](../../CHANGELOG.md) para detalhes de mudanças em cada versão.
- Respeite o [Código de Conduta](../../CODE_OF_CONDUCT.md) em todos os canais oficiais do projeto.

## Agradecimentos e Inspirações

O Omni Gateway baseia-se nas inovações da comunidade open-source de roteamento de IA, telemetria e gateways. Agradecemos profundamente aos idealizadores e mantenedores dos projetos:

| Projeto | Descrição | Estrelas |
| :--- | :--- | :---: |
| [**songquanpeng / one-api**](https://github.com/songquanpeng/one-api) | Referência em agregação web de APIs e gestão centralizada de chaves multiprovedor | [![Stars](https://img.shields.io/github/stars/songquanpeng/one-api?style=flat-square&color=yellow)](https://github.com/songquanpeng/one-api) |
| [**router-for-me / CLIProxyAPI**](https://github.com/router-for-me/CLIProxyAPI) | Pioneiro na camada de tradução e roteamento de protocolos entre múltiplos formatos para ferramentas CLI de IA | [![Stars](https://img.shields.io/github/stars/router-for-me/CLIProxyAPI?style=flat-square&color=yellow)](https://github.com/router-for-me/CLIProxyAPI) |
| [**BerriAI / litellm**](https://github.com/BerriAI/litellm) | Grande referência em proxy LLM unificado, balanceamento de carga e estratégias de failover | [![Stars](https://img.shields.io/github/stars/BerriAI/litellm?style=flat-square&color=yellow)](https://github.com/BerriAI/litellm) |
| [**Portkey-AI / gateway**](https://github.com/Portkey-AI/gateway) | Arquitetura ultra veloz para gateways de IA com suporte a estratégias flexíveis de roteamento | [![Stars](https://img.shields.io/github/stars/Portkey-AI/gateway?style=flat-square&color=yellow)](https://github.com/Portkey-AI/gateway) |
| [**langfuse / langfuse**](https://github.com/langfuse/langfuse) | Plataforma open-source completa para engenharia de LLMs, rastreabilidade e observabilidade | [![Stars](https://img.shields.io/github/stars/langfuse/langfuse?style=flat-square&color=yellow)](https://github.com/langfuse/langfuse) |

## Licença

O Omni Gateway é distribuído sob a licença [MIT](../../LICENSE).
