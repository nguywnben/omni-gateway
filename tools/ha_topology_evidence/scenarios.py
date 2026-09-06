"""Closed external scenario inventory and host-side Docker/fault controller."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final, Mapping
from urllib.parse import urlsplit

from .contract import REQUIRED_SCENARIOS, EvidenceVerificationError
from .fixture import FaultAction


@dataclass(frozen=True, slots=True)
class ScenarioSpec:
    scenario_id: str
    fault_action: FaultAction | None
    requires_fault_milestone: bool
    requires_oracle: bool = True


_ACTIONS: Final = {
    "redis-app-a-interruption": FaultAction.REDIS_APP_A_BLOCK,
    "redis-app-b-interruption": FaultAction.REDIS_APP_B_BLOCK,
    "redis-both-paths-interruption": FaultAction.REDIS_ALL_BLOCK,
    "redis-standby-promotion": FaultAction.REDIS_PROMOTE_STANDBY,
    "postgresql-outage": FaultAction.POSTGRES_ALL_BLOCK,
    "cancellation-unknown-outcome": FaultAction.PROVIDER_DROP_NEXT,
}
SCENARIO_SPECS: Final = tuple(
    ScenarioSpec(
        scenario,
        _ACTIONS.get(scenario),
        scenario not in {"coordinated-baseline", "coordinated-target"},
    )
    for scenario in REQUIRED_SCENARIOS
)


class ComposeAction(StrEnum):
    CONFIG = "config"
    UP = "up"
    STOP = "stop"
    START = "start"
    KILL = "kill"
    PS = "ps"
    LOGS = "logs"
    DOWN = "down"
    RECREATE = "recreate"


_PROJECT = re.compile(r"w4c-[0-9a-f]{12}")
_IMMUTABLE_IMAGE = re.compile(r"(?:[a-z0-9][a-z0-9./:_-]*@)?sha256:[0-9a-f]{64}")
_SERVICES: Final = frozenset(
    {"app-a", "app-b", "redis-primary", "redis-standby", "postgres", "fixture"}
)


def require_loopback_http_url(value: str, *, allow_path: bool = False) -> str:
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except (TypeError, ValueError) as exc:
        raise EvidenceVerificationError("Evidence endpoint is invalid.") from exc
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.username is not None
        or parsed.password is not None
        or port is None
        or parsed.query
        or parsed.fragment
        or (not allow_path and parsed.path not in {"", "/"})
    ):
        raise EvidenceVerificationError("Evidence endpoint must be an exact loopback HTTP URL.")
    return value.rstrip("/")


def require_immutable_image_reference(reference: str, resolved_id: str) -> str:
    if (
        not isinstance(reference, str)
        or not _IMMUTABLE_IMAGE.fullmatch(reference)
        or not isinstance(resolved_id, str)
        or not re.fullmatch(r"sha256:[0-9a-f]{64}", resolved_id)
        or reference.rsplit("@", 1)[-1] != resolved_id
    ):
        raise EvidenceVerificationError("Evidence image reference is not immutable.")
    return reference


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def loopback_opener(*handlers) -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect(), *handlers)


class HostController:
    """Own only fixed Compose/service/fault actions; never invokes a shell."""

    def __init__(
        self,
        compose_file: Path | tuple[Path, ...],
        project: str,
        fixture_url: str,
        *,
        compose_environment: Mapping[str, str] | None = None,
        control_token: str | None = None,
    ) -> None:
        compose_files = (compose_file,) if isinstance(compose_file, Path) else compose_file
        if (
            not isinstance(compose_files, tuple)
            or not compose_files
            or any(not path.is_absolute() or not path.is_file() for path in compose_files)
        ):
            raise EvidenceVerificationError("Compose evidence file is invalid.")
        if not _PROJECT.fullmatch(project):
            raise EvidenceVerificationError("Evidence project name is invalid.")
        fixture_url = require_loopback_http_url(fixture_url)
        self.compose_files = compose_files
        self.compose_file = compose_files[0]
        self.project = project
        self.fixture_url = fixture_url
        if control_token is not None and (
            not isinstance(control_token, str) or not 32 <= len(control_token) <= 128
        ):
            raise EvidenceVerificationError("Fixture control token is invalid.")
        self.control_token = control_token
        self.compose_environment = (
            None if compose_environment is None else {**os.environ, **dict(compose_environment)}
        )

    def compose(
        self,
        action: ComposeAction,
        services: tuple[str, ...] = (),
        *,
        timeout_seconds: int = 120,
    ) -> subprocess.CompletedProcess[str]:
        if type(action) is not ComposeAction or any(
            service not in _SERVICES for service in services
        ):
            raise EvidenceVerificationError("Compose action is invalid.")
        if type(timeout_seconds) is not int or not 1 <= timeout_seconds <= 2700:
            raise EvidenceVerificationError("Compose timeout is invalid.")
        arguments = ["docker", "compose"]
        for path in self.compose_files:
            arguments.extend(("-f", str(path)))
        arguments.extend(
            ("-p", self.project, "up" if action is ComposeAction.RECREATE else action.value)
        )
        if action in {ComposeAction.UP, ComposeAction.RECREATE}:
            arguments.extend(["-d", "--wait"])
            if action is ComposeAction.RECREATE:
                arguments.append("--force-recreate")
        elif action is ComposeAction.KILL:
            arguments.extend(["--signal", "SIGKILL"])
        elif action is ComposeAction.DOWN:
            arguments.extend(["--remove-orphans"])
        arguments.extend(services)
        return subprocess.run(
            arguments,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
            env=self.compose_environment,
        )

    def fault(self, action: FaultAction) -> dict[str, object]:
        if type(action) is not FaultAction:
            raise EvidenceVerificationError("Fixture fault action is invalid.")
        if self.control_token is None:
            raise EvidenceVerificationError("Fixture fault authorization is unavailable.")
        request = urllib.request.Request(
            f"{self.fixture_url}/actions/{action.value}",
            method="POST",
            data=b"",
            headers={"Content-Length": "0", "X-Evidence-Control": self.control_token},
        )
        try:
            with loopback_opener().open(request, timeout=5.0) as response:
                raw = response.read(65_537)
                if len(raw) > 65_536:
                    raise EvidenceVerificationError("Fixture fault acknowledgement is oversized.")
                payload = json.loads(raw)
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise EvidenceVerificationError("Fixture fault action was not observed.") from exc
        if not isinstance(payload, dict) or payload.get("action") != action.value:
            raise EvidenceVerificationError("Fixture fault acknowledgement is invalid.")
        return payload

    def fixture_state(self) -> dict[str, object]:
        try:
            with loopback_opener().open(f"{self.fixture_url}/state", timeout=5.0) as response:
                raw = response.read(65_537)
                if len(raw) > 65_536:
                    raise EvidenceVerificationError("Fixture state acknowledgement is oversized.")
                payload = json.loads(raw)
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise EvidenceVerificationError("Fixture state is unavailable.") from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != 1:
            raise EvidenceVerificationError("Fixture state acknowledgement is invalid.")
        return payload

    def container_ids(self) -> tuple[str, ...]:
        raw = _run_read_only(
            [
                "docker",
                "ps",
                "-aq",
                "--filter",
                f"label=com.docker.compose.project={self.project}",
            ]
        )
        values = tuple(sorted(line for line in raw.splitlines() if line))
        if any(not re.fullmatch(r"[0-9a-f]{12,64}", value) for value in values):
            raise EvidenceVerificationError("Evidence container identity is invalid.")
        return values

    def project_resources(self) -> ProjectResources:
        volumes = _labeled_names("volume", self.project)
        networks = _labeled_names("network", self.project)
        return ProjectResources(self.project, self.container_ids(), volumes, networks)

    @staticmethod
    def wait_http(
        url: str,
        *,
        expected_status: int = 200,
        timeout_seconds: int = 60,
    ) -> int:
        require_loopback_http_url(url, allow_path=True)
        deadline = time.monotonic() + timeout_seconds
        last_status = 0
        while time.monotonic() < deadline:
            try:
                with loopback_opener().open(url, timeout=2.0) as response:
                    last_status = response.status
            except urllib.error.HTTPError as exc:
                last_status = exc.code
            except (OSError, urllib.error.URLError):
                last_status = 0
            if last_status == expected_status:
                return last_status
            time.sleep(0.25)
        raise EvidenceVerificationError("Evidence HTTP probe did not reach the expected state.")

    @staticmethod
    def now_ns() -> int:
        return time.monotonic_ns()


@dataclass(frozen=True, slots=True)
class PreflightResult:
    docker_server_version: str
    compose_version: str
    source_revision: str
    source_tree_digest: str
    production_image_id: str
    evidence_image_id: str
    redis_image_id: str
    postgresql_image_id: str
    free_disk_bytes: int

    def safe_summary(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "docker_server_version": self.docker_server_version,
            "compose_version": self.compose_version,
            "source_revision": self.source_revision,
            "source_tree_digest": self.source_tree_digest,
            "production_image_id": self.production_image_id,
            "evidence_image_id": self.evidence_image_id,
            "redis_image_id": self.redis_image_id,
            "postgresql_image_id": self.postgresql_image_id,
            "free_disk_bytes": self.free_disk_bytes,
        }


@dataclass(frozen=True, slots=True)
class ProjectResources:
    project: str
    containers: tuple[str, ...]
    volumes: tuple[str, ...]
    networks: tuple[str, ...]

    def __post_init__(self) -> None:
        if not _PROJECT.fullmatch(self.project):
            raise EvidenceVerificationError("Evidence project identity is invalid.")
        if any(not re.fullmatch(r"[0-9a-f]{12,64}", value) for value in self.containers):
            raise EvidenceVerificationError("Evidence container inventory is invalid.")
        expected_prefix = self.project + "_"
        if any(
            not isinstance(value, str) or not value.startswith(expected_prefix)
            for value in (*self.volumes, *self.networks)
        ):
            raise EvidenceVerificationError("Evidence resource inventory is invalid.")

    def safe_summary(self) -> dict[str, object]:
        return {
            "project": self.project,
            "containers": list(self.containers),
            "volumes": list(self.volumes),
            "networks": list(self.networks),
        }

    @classmethod
    def from_dict(cls, value: object) -> ProjectResources:
        if not isinstance(value, dict) or set(value) != {
            "project",
            "containers",
            "volumes",
            "networks",
        }:
            raise EvidenceVerificationError("Evidence resource inventory schema is invalid.")
        try:
            return cls(
                value["project"],
                tuple(value["containers"]),
                tuple(value["volumes"]),
                tuple(value["networks"]),
            )
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Evidence resource inventory is invalid.") from exc


@dataclass(frozen=True, slots=True)
class CleanupScope:
    """Create-only authorization for one isolated Compose project namespace."""

    project: str
    nonce: str
    signature: str
    schema_version: int = 1

    def __post_init__(self) -> None:
        if (
            self.schema_version != 1
            or not _PROJECT.fullmatch(self.project)
            or not re.fullmatch(r"[0-9a-f]{32}", self.nonce)
            or not re.fullmatch(r"[0-9a-f]{64}", self.signature)
        ):
            raise EvidenceVerificationError("Evidence cleanup scope is invalid.")

    def unsigned_payload(self) -> bytes:
        return json.dumps(
            {
                "schema_version": self.schema_version,
                "project": self.project,
                "nonce": self.nonce,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "project": self.project,
            "nonce": self.nonce,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, value: object) -> CleanupScope:
        if not isinstance(value, dict) or set(value) != {
            "schema_version",
            "project",
            "nonce",
            "signature",
        }:
            raise EvidenceVerificationError("Evidence cleanup scope schema is invalid.")
        try:
            return cls(**value)
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Evidence cleanup scope is invalid.") from exc


def _labeled_names(kind: str, project: str) -> tuple[str, ...]:
    if kind not in {"volume", "network"} or not _PROJECT.fullmatch(project):
        raise EvidenceVerificationError("Evidence resource query is invalid.")
    raw = _run_read_only(
        [
            "docker",
            kind,
            "ls",
            "--format",
            "{{.Name}}",
            "--filter",
            f"label=com.docker.compose.project={project}",
        ]
    )
    return tuple(sorted(line for line in raw.splitlines() if line))


def _project_resources(project: str) -> ProjectResources:
    current_containers = _run_read_only(
        ["docker", "ps", "-aq", "--filter", f"label=com.docker.compose.project={project}"]
    )
    containers = tuple(sorted(line for line in current_containers.splitlines() if line))
    return ProjectResources(
        project,
        containers,
        _labeled_names("volume", project),
        _labeled_names("network", project),
    )


def create_cleanup_scope(project: str, key: bytes) -> CleanupScope:
    """Issue a scope only when the project label owns no pre-existing resources."""

    if not isinstance(key, bytes) or len(key) != 32:
        raise EvidenceVerificationError("Evidence cleanup key is invalid.")
    existing = _project_resources(project)
    if existing.containers or existing.volumes or existing.networks:
        raise EvidenceVerificationError("Evidence project already owns Docker resources.")
    provisional = CleanupScope(project, secrets.token_hex(16), "0" * 64)
    signature = hmac.digest(
        key,
        b"omni-ha-cleanup-scope-v1\x00" + provisional.unsigned_payload(),
        hashlib.sha256,
    ).hex()
    return CleanupScope(project, provisional.nonce, signature)


def verify_cleanup_scope(scope: CleanupScope, key: bytes) -> bool:
    if type(scope) is not CleanupScope or not isinstance(key, bytes) or len(key) != 32:
        return False
    expected = hmac.digest(
        key,
        b"omni-ha-cleanup-scope-v1\x00" + scope.unsigned_payload(),
        hashlib.sha256,
    ).hex()
    return hmac.compare_digest(scope.signature, expected)


def cleanup_project_resources(scope: CleanupScope, key: bytes) -> ProjectResources:
    """Snapshot once, then remove only those exact authenticated project resources."""

    if not verify_cleanup_scope(scope, key):
        raise EvidenceVerificationError("Evidence cleanup authorization is invalid.")
    recorded = _project_resources(scope.project)
    containers = recorded.containers
    volumes = recorded.volumes
    networks = recorded.networks
    commands = (
        (["docker", "rm", "-f", *containers] if containers else None),
        (["docker", "volume", "rm", *volumes] if volumes else None),
        (["docker", "network", "rm", *networks] if networks else None),
    )
    for command in commands:
        if command is None:
            continue
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
                shell=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise EvidenceVerificationError("Bounded evidence cleanup failed.") from exc
    return recorded


def _run_read_only(arguments: list[str], *, cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(
            arguments,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise EvidenceVerificationError("External evidence preflight command failed.") from exc
    return result.stdout.strip()


def _image_id(reference: str) -> str:
    raw = _run_read_only(["docker", "image", "inspect", reference, "--format", "{{.Id}}"])
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", raw):
        raise EvidenceVerificationError("Docker image identity is invalid.")
    return raw


def source_tree_digest(repository: Path, revision: str) -> str:
    if not repository.is_absolute() or not repository.is_dir():
        raise EvidenceVerificationError("Source repository is invalid.")
    if _run_read_only(["git", "status", "--porcelain"], cwd=repository):
        raise EvidenceVerificationError("Source tree must be committed and clean before preflight.")
    actual_revision = _run_read_only(["git", "rev-parse", "HEAD"], cwd=repository)
    if actual_revision != revision:
        raise EvidenceVerificationError("Source revision does not match the candidate.")
    tree = _run_read_only(["git", "ls-tree", "-r", "--full-tree", revision], cwd=repository)
    return hashlib.sha256(b"omni-ha-source-tree-v1\x00" + tree.encode("utf-8")).hexdigest()


def run_preflight(
    candidate,
    *,
    repository: Path,
    controller: HostController,
    evidence_image: str,
    minimum_free_disk_bytes: int = 10 * 1024**3,
) -> PreflightResult:
    from .contract import CandidateTopology

    if type(candidate) is not CandidateTopology:
        raise EvidenceVerificationError("Candidate is invalid.")
    docker_version = _run_read_only(["docker", "version", "--format", "{{.Server.Version}}"])
    compose_version = _run_read_only(["docker", "compose", "version", "--short"])
    tree_digest = source_tree_digest(repository, candidate.source_revision)
    if tree_digest != candidate.source_tree_digest:
        raise EvidenceVerificationError("Source tree digest does not match the candidate.")
    production_id = _image_id(candidate.production_image)
    production_revision = _run_read_only(
        [
            "docker",
            "image",
            "inspect",
            candidate.production_image,
            "--format",
            '{{ index .Config.Labels "org.opencontainers.image.revision" }}',
        ]
    )
    if production_revision != candidate.source_revision:
        raise EvidenceVerificationError("Production image revision does not match the source.")
    evidence_id = _image_id(evidence_image)
    require_immutable_image_reference(evidence_image, evidence_id)
    if evidence_id != _image_id(candidate.evidence_image):
        raise EvidenceVerificationError("Evidence image does not match the frozen candidate.")
    launcher_label = _run_read_only(
        [
            "docker",
            "image",
            "inspect",
            evidence_image,
            "--format",
            '{{ index .Config.Labels "com.omni-gateway.evidence.launcher-digest" }}',
        ]
    )
    if launcher_label != candidate.evidence_launcher_digest:
        raise EvidenceVerificationError("Evidence image launcher digest does not match.")
    production_label = _run_read_only(
        [
            "docker",
            "image",
            "inspect",
            evidence_image,
            "--format",
            '{{ index .Config.Labels "com.omni-gateway.evidence.production-image" }}',
        ]
    )
    if production_label != candidate.production_image:
        raise EvidenceVerificationError("Evidence image production base does not match.")
    redis_id = _image_id(candidate.redis_primary_image)
    postgres_id = _image_id(candidate.postgresql_image)
    controller.compose(ComposeAction.CONFIG, timeout_seconds=30)
    existing = _run_read_only(
        [
            "docker",
            "ps",
            "-aq",
            "--filter",
            f"label=com.docker.compose.project={controller.project}",
        ]
    )
    if (
        existing
        or _labeled_names("volume", controller.project)
        or _labeled_names("network", controller.project)
    ):
        raise EvidenceVerificationError("Evidence project already owns Docker resources.")
    free = shutil.disk_usage(repository).free
    if free < minimum_free_disk_bytes:
        raise EvidenceVerificationError("Evidence host has insufficient free disk space.")
    return PreflightResult(
        docker_version,
        compose_version,
        candidate.source_revision,
        tree_digest,
        production_id,
        evidence_id,
        redis_id,
        postgres_id,
        free,
    )
