# External high-availability evidence runbook

This runbook is the only supported path for producing the external Redis/PostgreSQL evidence
required by ADR-008. The evidence candidate is isolated from production activation. A successful
run is eligible for review only; it cannot add itself to the production activation allowlist.

## Safety boundary

- Use a clean committed tree and Docker Desktop with the Linux engine available.
- Use only immutable image IDs or `name@sha256:...` references.
- Keep the generated candidate and report directory. They contain synthetic metadata only.
- Do not point the harness at a production Redis, PostgreSQL, credential directory, or network.
- A failed or interrupted run remains failed and is cleaned automatically from its create-only,
  authenticated project scope. Preserve its incomplete output and captured logs for diagnosis;
  never edit a manifest or reuse its output directory.

## Preflight and candidate freeze

From the repository root in PowerShell, select exact local images. Replace the two placeholder
references with images already pulled and verified for this run.

```powershell
$w4cRoot = (Get-Location).Path
$w4cCandidateDir = Join-Path $w4cRoot "temp\w4c-candidate"
New-Item -ItemType Directory -Path $w4cCandidateDir | Out-Null

$w4cRevision = git rev-parse HEAD
docker build --pull --file deploy/Dockerfile --build-arg REVISION=$w4cRevision `
  --tag omni-gateway:w4c-candidate .
$w4cProductionImage = docker image inspect omni-gateway:w4c-candidate --format '{{.Id}}'
$w4cLauncherDigest = .\.venv\Scripts\python.exe -c `
  "from pathlib import Path; from tools.ha_topology_evidence.candidate import launcher_digest; print(launcher_digest(Path.cwd()))"

docker build --file deploy/evidence/Dockerfile `
  --build-arg PRODUCTION_IMAGE=omni-gateway:w4c-candidate `
  --build-arg PRODUCTION_IMAGE_ID=$w4cProductionImage `
  --build-arg EVIDENCE_LAUNCHER_DIGEST=$w4cLauncherDigest `
  --tag omni-gateway:w4c-evidence .
$w4cEvidenceImage = docker image inspect omni-gateway:w4c-evidence --format '{{.Id}}'
$w4cRedisImage = '<redis-image@sha256:digest>'
$w4cPostgresImage = '<postgres-image@sha256:digest>'

.\.venv\Scripts\python.exe -m tools.ha_topology_evidence.candidate `
  --repository $w4cRoot `
  --production-image $w4cProductionImage `
  --evidence-image $w4cEvidenceImage `
  --redis-image $w4cRedisImage `
  --postgresql-image $w4cPostgresImage `
  --output (Join-Path $w4cCandidateDir 'candidate.json')

$w4cProject = 'w4c-' + ([guid]::NewGuid().ToString('N').Substring(0,12))

.\.venv\Scripts\python.exe -m tools.ha_topology_evidence preflight `
  --candidate (Join-Path $w4cCandidateDir 'candidate.json') `
  --repository $w4cRoot `
  --project $w4cProject `
  --evidence-image $w4cEvidenceImage
```

Candidate creation fails if the source tree is dirty, the revision is not exact, either application
image is not pinned, or the frozen workload differs from the W4-C profile. The production image,
evidence derivative image, and launcher package digest are all frozen into the same candidate.

Preflight validates Docker/Compose, the clean Git tree, all image identities, the evidence launcher
label, the rendered Compose model, project-name isolation, empty project ownership, and at least
10 GiB of free disk. Before either application replica starts, the evidence image also recomputes
the digest of its installed launcher package and compares it with `candidate.json`; a matching
label on mismatched launcher code is insufficient.

## Run and verify

Create a new parent directory but do not create the report directory itself. The writer is
create-only so interrupted output cannot be mistaken for a complete report.

```powershell
$w4cEvidenceParent = Join-Path $w4cRoot 'docs\evidence'
$w4cOutput = Join-Path $w4cEvidenceParent ('pending-' + $w4cProject)

$w4cRun = .\.venv\Scripts\python.exe -m tools.ha_topology_evidence run `
  --candidate (Join-Path $w4cCandidateDir 'candidate.json') `
  --repository $w4cRoot `
  --project $w4cProject `
  --evidence-image $w4cEvidenceImage `
  --output $w4cOutput
$w4cRunResult = $w4cRun | ConvertFrom-Json
$w4cManifestDigest = $w4cRunResult.manifest_digest
$w4cCleanupScope = $w4cRunResult.cleanup_scope
$w4cCleanupKey = $w4cRunResult.cleanup_key

.\.venv\Scripts\python.exe -m tools.ha_topology_evidence verify `
  --candidate (Join-Path $w4cCandidateDir 'candidate.json') `
  --manifest (Join-Path $w4cOutput 'manifest.json') `
  --expected-manifest-digest $w4cManifestDigest
```

The run uses synthetic provider data and seeds at least one valid record in every copy-required
durable family (including both credential modes, identity/role/policy/schema, audit, trace, usage,
and a settled hard-budget reservation). It then exercises the exact frozen inventory: resumable
durable migration, interrupted bootstrap, alternating one/two-replica performance, both application
losses, Redis per-path/both-path/restart/standby-promotion failures, stale epoch, partial namespace,
PostgreSQL outage, unknown upstream outcome, a cross-replica duplicate delivery with one provider
execution and one durable usage commit, drain/reconcile/mark-ready, and a one-process
standalone rollback using the same PostgreSQL history. The topology enables the exact-response
cache and positively demonstrates a real miss, a real hit, and a post-epoch miss against the
fixture's upstream-attempt counter. Every admission probe has a globally unique sample identity,
is included in the artifacts, and is counted by the durable-conservation oracle. Correctness
scenarios have an individual 120-second timeout;
the entire bootstrap, matrix, report, and verification path is bounded by 45 minutes.

The completed report archives the exact canonical `candidate.json` alongside the event, sample,
scenario, and summary artifacts. Verification recomputes every artifact hash, requires that
archived candidate to equal the independently supplied candidate, and rejects missing, duplicate, skipped, unavailable,
interrupted, unexercised, unsafe, source/image-mismatched, secret-bearing, or performance-regressed
evidence. The acceptance limits are p95 no greater than 1.20 times baseline and successful
throughput no lower than 0.85 times baseline for each alternating pair, with zero correctness
failure counters.
The summary binds the exact Redis/PostgreSQL image IDs and records the observed Redis 8 and
PostgreSQL 17 server patch versions; a valid-looking but candidate-mismatched dependency image is
rejected during offline verification.
The three alternating performance pairs use the immutable seed tuple stored in `candidate.json`;
the seed drives a deterministic replica schedule and is therefore covered by the candidate digest.
The verifier requires the exact 28,704 HTTP deliveries, unique delivery digests, the exact single
two-delivery operation replay, and exact challenged-operation/fault-milestone
count for every scenario; a truncated or padded artifact cannot satisfy the frozen workload merely
by retaining successful aggregate counters.
Redis/PostgreSQL recovery results also contain monotonic timestamps for fault observation,
dependency restoration, reconciliation start/completion, `mark-ready`, and sustained readiness;
verification rejects missing, out-of-order, or slower-than-60-second recovery clocks.

## Post-approval production-gate rerun

The first verified candidate is only an activation predecessor. After its immutable artifacts are
reviewed, ADR-009 may compile that predecessor identifier into
`SUPPORTED_HA_ACTIVATION_RECORDS` and raise the production policy ceiling to exactly two replicas.
Build that reviewed revision as a new production image, create a new candidate/output/project, and
freeze the predecessor explicitly:

```powershell
$w4cApprovedRecord = '<act_identifier_from_the_first_verified_manifest>'

.\.venv\Scripts\python.exe -m tools.ha_topology_evidence.candidate `
  --repository $w4cRoot `
  --production-image $w4cActivatedProductionImage `
  --evidence-image $w4cActivatedEvidenceImage `
  --redis-image $w4cRedisImage `
  --postgresql-image $w4cPostgresImage `
  --activation-record $w4cApprovedRecord `
  --output (Join-Path $w4cActivatedCandidateDir 'candidate.json')
```

The activated candidate has its own digest and identifier, but its lifecycle and operator must
verify the predecessor through the production allowlist. The evidence wrapper no longer derives a
two-replica policy in this mode: `HaRuntimePolicy.from_environment` must accept the exact two-replica
topology itself. Therefore an empty/mismatched allowlist or an unchanged one-replica policy aborts
startup. Run the entire matrix and offline verifier again; a partial rerun is not activation
evidence, and any subsequent material source/configuration change invalidates both results.

## Failure diagnosis

The launcher attempts authenticated cleanup on every ordinary failure, timeout, cancellation, and
keyboard interruption. Capture live logs in a second terminal while the run is active when deeper
diagnostics are required:

```powershell
docker ps -a --filter "label=com.docker.compose.project=$w4cProject"
docker ps -aq --filter "label=com.docker.compose.project=$w4cProject" |
  ForEach-Object { docker logs --tail 500 $_ }
docker volume ls --filter "label=com.docker.compose.project=$w4cProject"
```

Application logs and incomplete output are diagnostic only and never acceptance evidence. Fix the
production owner, commit it, freeze a new candidate, and rerun the invalidated matrix from scratch.

## Bounded cleanup

Before creating Docker resources, `run` verifies that the project label is empty and writes a
create-only signed scope plus a separate 32-byte cleanup key outside the report directory. Cleanup
authenticates that scope, snapshots matching resources once, then removes only those exact IDs and
names; it does not trust or reread the report manifest.

```powershell
.\.venv\Scripts\python.exe -m tools.ha_topology_evidence cleanup `
  --scope $w4cCleanupScope `
  --cleanup-key $w4cCleanupKey
```

Successful cleanup removes the generated cleanup key and scope. Never use a wildcard project,
container, volume, or network selector.
