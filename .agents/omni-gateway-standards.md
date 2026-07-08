# Omni Gateway Project Standards

These rules define the shared quality bar for Omni Gateway. Apply them when editing frontend UI, backend responses, logs, documentation, deployment files, and internal configuration.

## Product Definition

Omni Gateway is a universal AI router for coding tools. It provides smart auto-fallback, token-aware request cleanup, usage visibility, and seamless format translation so OpenAI, Anthropic, Google GenAI, and provider-native clients can share one stable routing layer.

Google Antigravity is the first supported provider workflow. It must be presented as one provider inside Omni Gateway, not as the whole product. Use `Google Antigravity` in provider introductions, OAuth setup, advanced settings, and documentation; use `Antigravity` only in compact cards, badges, and space-constrained labels.

## Brand and Architecture Boundaries

- Use `Omni Gateway` for user-facing product identity in the UI, README, docs, page titles, and high-level logs.
- Keep SDK-compatible API surfaces generic and namespace-free: `/v1`, `/v1beta`, and provider-compatible routes only.
- Preserve the `sk-ogw-` API key prefix. It is the only intentional brand marker inside runtime security tokens.
- Avoid legacy project names, URLs, credits, or fork references.
- Use port `4283` as the default Omni Gateway development and deployment port unless a platform requires another value.

## Writing Style

- Use clear, natural, professional English.
- Prefer concise sentences over verbose explanations.
- Use sentence case for labels, buttons, status messages, placeholders, and helper text.
- Use Title Case for page titles, card titles, modal titles, and major section headings.
- Do not expose internal keys such as `status_no_creds`, `AUTO_DISABLE`, or `CODE_ASSIST_CLIENT_ID` as visible UI text. Explain their meaning in normal language.
- Use punctuation according to context. Full sentences should end with punctuation; short labels and button text usually should not.
- Avoid awkward plural forms such as `credential(s)` or `file(s)`. Use wording that reads naturally, such as `credential files` or explicit singular/plural logic.
- Avoid excessive `successfully`. Prefer direct outcomes: `Configuration saved.`, `API key regenerated.`, `Credentials imported.`
- Error messages should state what failed, why when known, and what the user can do next when useful.

## UI Design Language

- Maintain a hyper-minimal, developer-first console using Google Sans.
- Use high contrast, hairline borders, restrained spacing, and quiet neutral surfaces.
- Use `var(--radius)` for standard component radius. Do not reintroduce pill radius globally unless the component is intentionally pill-shaped.
- Disabled and readonly inputs must use `background: var(--bg-subtle);` with readable text color.
- Do not use heavy shadows, decorative effects, slow animations, or floating marketing-style cards.
- Keep information modals structured: first section for summary/context, later sections for details. Avoid raw API responses in user-facing modals unless they are explicitly needed for troubleshooting.
- Confirmation modals may stay simpler, but their body text must remain natural and readable.
- Do not place raw JSON or long text where it can overflow horizontally. Wrap, scroll vertically, or use structured detail blocks.

## Backend Responses and Logs

- Backend response messages must be grammatically complete and sanitized.
- Logs should be useful to an operator and written in a consistent tone.
- Do not log secrets, access tokens, refresh tokens, passwords, or full API keys.
- Prefer `credential`, `credential file`, `provider credential`, and `Code Assist credential` consistently.
- Use `Project ID`, `API key`, `base URL`, `OAuth`, `User-Agent`, and `Google GenAI` consistently.
- Preserve upstream error details only when they are needed for debugging and do not expose local secrets.

## SDK and Route Standards

- OpenAI SDK: base URL should be origin plus `/v1`; the SDK appends `/chat/completions`.
- Anthropic SDK: base URL should be the origin; the SDK appends `/v1/messages`.
- Google GenAI SDK: base URL should be the origin; the SDK appends its standard `/v1beta` model routes.
- Do not add custom branded prefixes to public SDK routes.
- Frontend copy should describe SDK initialization, not low-level HTTP request construction, unless a screen is specifically about raw endpoints.

## Configuration and Deployment

- Keep `.env.example` safe, complete, and copy-paste ready.
- Use placeholders for private values. Public/bundled provider client settings may be shown when they are required for normal operation.
- Treat Omni Gateway as a real deployment project, not a demo. Docker/VPS instructions should be production-first, use restart policies, and persist credentials/logs in durable host paths such as `/opt/omni-gateway`.
- OAuth provider flows must account for VPS deployments. Google Antigravity should redirect to `localhost:4283/callback`, which works on local machines and intentionally lands on the user's browser machine when the console runs on a VPS. The UI must keep a clear manual callback URL path for that server scenario.
- Deployment service names, container names, default directories, and metadata should use `omni-gateway`.
- Default MongoDB database names should use `omni_gateway`.
- Docker Hub secrets should be named `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.

## Review Checklist

- Does every visible string read naturally in English?
- Are headings, labels, buttons, toasts, modals, docs, logs, and API messages using the same product vocabulary?
- Are UI texts free of raw internal variable names and old generated translation keys?
- Are technical routes generic while the presentation still clearly says Omni Gateway?
- Are errors actionable, sanitized, and grammatically complete?
- Are design tokens and modal structures consistent with the console's minimal design language?
