"""Evidence-only lifecycle injection around the original Omni Gateway ASGI application."""

from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import Any, Mapping

from .admin import experimental_policy
from .candidate import verify_launcher_package
from .contract import CandidateTopology, CandidateVerifier, EvidenceVerificationError, load_json

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.ha_activation import verify_ha_activation_record  # noqa: E402
from core.ha_runtime import (  # noqa: E402
    HaRuntimeLifecycle,
    close_ha_runtime,
    get_runtime_lifecycle,
    set_runtime_lifecycle,
)
from core.http_server import configure_hypercorn  # noqa: E402
from core.storage_adapter import get_storage_adapter  # noqa: E402

LifespanFactory = Callable[[Any], AsyncIterator[None]]


@asynccontextmanager
async def candidate_lifespan(
    application: Any,
    *,
    candidate: CandidateTopology,
    verifier: CandidateVerifier,
    environment: Mapping[str, str],
    replica_count: int,
    original_lifespan: Callable[[Any], Any] | None = None,
    storage_factory: Callable[[], Awaitable[Any]] = get_storage_adapter,
) -> AsyncIterator[None]:
    """Start one injected lifecycle; the original lifespan owns every other service and shutdown."""

    if not verifier(candidate.candidate_id) or verifier.replica_count != replica_count:
        raise EvidenceVerificationError(
            "Candidate verifier does not match the application replica."
        )
    if get_runtime_lifecycle() is not None:
        raise EvidenceVerificationError("A runtime lifecycle is already installed.")
    policy = experimental_policy(environment, candidate, replica_count=replica_count)
    storage = await storage_factory()
    activation_verifier = verifier
    if candidate.activation_record is not None:
        if not verify_ha_activation_record(candidate.activation_record):
            raise EvidenceVerificationError(
                "Candidate predecessor activation record is not approved."
            )
        activation_verifier = verify_ha_activation_record
    lifecycle = HaRuntimeLifecycle(
        policy=policy,
        activation_verifier=activation_verifier,
    )
    await lifecycle.start(storage=storage)
    set_runtime_lifecycle(lifecycle)
    if original_lifespan is None:
        from main import lifespan as original_lifespan

    try:
        async with original_lifespan(application):
            if get_runtime_lifecycle() is not lifecycle:
                raise EvidenceVerificationError(
                    "Original startup replaced the candidate lifecycle."
                )
            yield
    finally:
        # The original lifespan normally owns this close. Cover only startup failure boundaries;
        # never close the same lifecycle twice.
        if get_runtime_lifecycle() is lifecycle:
            await close_ha_runtime()


class EvidenceApplication:
    """ASGI lifespan wrapper that delegates every HTTP/WebSocket request to the original app."""

    def __init__(self, application: Any, lifespan_factory: Callable[[Any], Any]) -> None:
        self.application = application
        self._lifespan_factory = lifespan_factory

    async def __call__(self, scope: dict[str, object], receive: Any, send: Any) -> None:
        if scope.get("type") != "lifespan":
            await self.application(scope, receive, send)
            return
        started = False
        try:
            message = await receive()
            if message.get("type") != "lifespan.startup":
                raise EvidenceVerificationError("ASGI lifespan startup message is invalid.")
            async with self._lifespan_factory(self.application):
                started = True
                await send({"type": "lifespan.startup.complete"})
                message = await receive()
                if message.get("type") != "lifespan.shutdown":
                    raise EvidenceVerificationError("ASGI lifespan shutdown message is invalid.")
            await send({"type": "lifespan.shutdown.complete"})
        except BaseException as exc:
            kind = "lifespan.shutdown.failed" if started else "lifespan.startup.failed"
            await send({"type": kind, "message": type(exc).__name__})
            raise


def build_candidate_application(
    application: Any,
    *,
    candidate: CandidateTopology,
    verifier: CandidateVerifier,
    environment: Mapping[str, str],
    replica_count: int,
    original_lifespan: Callable[[Any], Any] | None = None,
    storage_factory: Callable[[], Awaitable[Any]] = get_storage_adapter,
) -> EvidenceApplication:
    """Wrap the original ASGI app without replacing its routes, middleware, or repositories."""

    factory = partial(
        candidate_lifespan,
        candidate=candidate,
        verifier=verifier,
        environment=environment,
        replica_count=replica_count,
        original_lifespan=original_lifespan,
        storage_factory=storage_factory,
    )
    return EvidenceApplication(application, factory)


def serve_candidate_application() -> None:
    """Load a frozen candidate and run the original app through its evidence-only lifespan."""

    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    from main import app as production_application
    from main import lifespan as production_lifespan

    candidate_path = Path(os.environ.get("OMNI_EVIDENCE_CANDIDATE_FILE", ""))
    if not candidate_path.is_absolute() or not candidate_path.is_file():
        raise EvidenceVerificationError("Candidate file is unavailable.")
    candidate = CandidateTopology.from_dict(load_json(candidate_path))
    verify_launcher_package(candidate, Path(__file__).resolve().parents[2])
    environment = dict(os.environ)
    verifier = CandidateVerifier.from_environment(candidate, environment)
    if not verifier(candidate.candidate_id):
        raise EvidenceVerificationError("Observed container topology does not match the candidate.")
    application = build_candidate_application(
        production_application,
        candidate=candidate,
        verifier=verifier,
        environment=environment,
        replica_count=verifier.replica_count,
        original_lifespan=production_lifespan,
    )
    config = Config()
    config.bind = ["0.0.0.0:4283"]
    config.workers = 1
    config.accesslog = "-"
    config.errorlog = "-"
    config.loglevel = "INFO"
    configure_hypercorn(config)
    asyncio.run(serve(application, config))


if __name__ == "__main__":
    serve_candidate_application()
