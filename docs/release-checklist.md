# Release Checklist

Use this checklist when preparing a tagged Omni Gateway release.

## Automated Gates

- Run `ruff check backend` and `ruff format --check backend`.
- Run `python -m compileall -q backend`.
- Run `python -m backend.tests`.
- Run `node --check` for every file under `frontend/js`.
- Run `yamllint --strict .github deploy .yamllint.yml`.
- Run `python -m pip_audit --local --progress-spinner off`.
- Regenerate `requirements.lock` and confirm that `git diff --exit-code requirements.lock` is clean.
- Confirm the CI container smoke test builds the image and completes setup, login, management API, and invalid-key checks.
- Confirm public authentication, validation, upstream, and pre-stream errors match the OpenAI, Anthropic, and Google GenAI envelopes.
- Confirm every public response includes a bounded `X-Request-ID`.
- Confirm oversized fixed-length and chunked requests return `413` in the selected SDK envelope.

## Manual Provider Checks

- Add one Google Antigravity credential through OAuth and complete a message test.
- Add one Google AI Studio key and complete a message test.
- Add one Grok credential through OAuth and complete a message test.
- Add one xAI Console key and complete a message test.
- Refresh the model catalog and route `omway` through at least one compatible model from every configured provider type.
- Configure two credentials from the same provider with different model catalogs; confirm a fixed model uses only compatible credentials and that one credential's model-not-found response does not disable the route for the other credential.
- Remove one entry from **Unavailable Model Routes**, revalidate its credential, and confirm the route becomes eligible again without changing unrelated provider routes.
- Send one non-streaming and one streaming request through each supported SDK surface.
- Confirm token usage, provider attribution, fallback, cooldown, and context-compression metrics update.
- Export the pool, restore it into a clean disposable instance, and verify deduplication results.
- Exercise the console in a real browser at desktop and mobile widths; verify every page, modal, form, navigation action, and empty/error state without console errors or horizontal page overflow.

## Deployment Checks

- Test the exact `linux/amd64` image on a clean host with persistent credential and log mounts.
- Confirm remote first-run setup rejects a missing token and accepts the token shown in container logs.
- Put the service behind TLS and verify secure cookies and forwarded-header configuration.
- Back up the persistent data directory before upgrading an existing instance.
- Record the previous image digest for rollback.
- Confirm the version tag publishes `latest` and semantic-version tags, while a default-branch build publishes `edge` without moving `latest`.
- When upgrading a beta deployment, perform the documented [1.0 upgrade](upgrading-to-1.0.md) against a copy of the existing data.

## Release Steps

1. Move completed entries from `Unreleased` to the target version in `CHANGELOG.md`.
2. Confirm `DEFAULT_APPLICATION_VERSION` matches the release tag.
3. Rebase on `origin/main` and rerun every automated gate.
4. Tag the verified commit with an annotated `vX.Y.Z` tag.
5. Let GitHub Actions publish the container and verify its digest.
6. Confirm GitHub Actions created the release from the matching changelog section before announcing it.
7. Pull the published image by digest, rerun liveness/readiness and SDK smoke checks, and record the digest in the release notes or deployment record.
