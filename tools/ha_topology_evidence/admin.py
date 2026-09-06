"""Evidence-only construction of real HA lifecycle and operator owners."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Mapping

from .contract import CandidateTopology, CandidateVerifier, EvidenceVerificationError

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.ha_activation import verify_ha_activation_record  # noqa: E402
from core.ha_coordination_binding import CoordinationBindingManager  # noqa: E402
from core.ha_operator import HaRuntimeOperator  # noqa: E402
from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode  # noqa: E402


def experimental_policy(
    environment: Mapping[str, str],
    candidate: CandidateTopology,
    *,
    replica_count: int,
) -> HaRuntimePolicy:
    """Build a frozen policy, using the production activation gate after approval."""

    if not isinstance(environment, Mapping):
        raise EvidenceVerificationError("Candidate environment is invalid.")
    verifier = CandidateVerifier.exact(candidate, replica_count=replica_count)
    if not verifier(candidate.candidate_id):
        raise EvidenceVerificationError("Candidate topology is not exact.")
    selected = dict(environment)
    selected["OMNI_REPLICA_COUNT"] = str(replica_count)
    topology_verifier = None
    if candidate.activation_record is None:

        def topology_verifier(mode: RuntimeMode, replicas: int) -> bool:
            return (
                mode is RuntimeMode.COORDINATED
                and replicas == replica_count
                and verifier(candidate.candidate_id)
            )

    policy = HaRuntimePolicy.from_environment(
        selected,
        topology_verifier=topology_verifier,
    )
    if (
        policy.mode is not RuntimeMode.COORDINATED
        or policy.workers != candidate.workers_per_replica
        or policy.durable_backend != "postgresql"
        or policy.replicas != replica_count
    ):
        raise EvidenceVerificationError("Candidate runtime policy is incompatible.")
    return policy


class CandidateAdmin:
    """Inject the exact candidate verifier into existing production owners."""

    def __init__(
        self,
        policy: HaRuntimePolicy,
        storage: object,
        store: object,
        verifier: CandidateVerifier,
    ) -> None:
        if (
            not verifier(verifier.candidate.candidate_id)
            or policy.mode is not RuntimeMode.COORDINATED
            or policy.workers != verifier.workers_per_replica
            or policy.replicas != verifier.replica_count
            or policy.durable_backend != "postgresql"
        ):
            raise EvidenceVerificationError("Candidate verifier does not match observed topology.")
        activation_record = verifier.candidate.activation_record
        activation_verifier = verifier
        if activation_record is not None:
            if not verify_ha_activation_record(activation_record):
                raise EvidenceVerificationError(
                    "Candidate predecessor activation record is not approved."
                )
            activation_verifier = verify_ha_activation_record
        else:
            activation_record = verifier.candidate.candidate_id
        self.policy = policy
        self.verifier = verifier
        self.activation_record = activation_record
        self.bindings = CoordinationBindingManager(
            storage,
            store,
            activation_verifier=activation_verifier,
        )
        self.operator = HaRuntimeOperator(
            policy,
            storage,
            store,
            activation_verifier=activation_verifier,
        )

    async def bootstrap(self, migration_plan_id: str, *, apply: bool = False):
        return await self.bindings.bootstrap(
            self.policy,
            activation_record=self.activation_record,
            migration_plan_id=migration_plan_id,
            apply=apply,
        )
