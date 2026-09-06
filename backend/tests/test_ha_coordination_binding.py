from __future__ import annotations

import base64
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import CoordinationUninitializedError
from core.durable_migration import AuthoritySide, MigrationPhase
from core.ha_coordination_binding import (
    CoordinationBinding,
    CoordinationBindingManager,
    HaBindingError,
)
from core.ha_runtime_policy import HaRuntimePolicy
from core.state_store import InMemoryStateStore

from backend.tests.durable_migration_fixtures import (
    PLAN_ID,
    MemoryMigrationCheckpoints,
    completed_migration_checkpoint,
)


class _Storage:
    def __init__(self) -> None:
        self.config: dict[str, object] = {}
        self.fail_next_write = False
        self.checkpoints = MemoryMigrationCheckpoints(completed_migration_checkpoint())

    async def get_config(self, key: str, default=None):
        return self.config.get(key, default)

    async def set_config(self, key: str, value: object) -> bool:
        if self.fail_next_write:
            self.fail_next_write = False
            return False
        self.config[key] = value
        return True

    async def create_migration_checkpoint_repository(self):
        return self.checkpoints


class _ExplicitNamespaceStore(InMemoryStateStore):
    def __init__(self, *, initialized: bool) -> None:
        super().__init__()
        self.initialized = initialized
        self.initialize_calls = 0

    async def read_epoch(self):
        if not self.initialized:
            raise CoordinationUninitializedError("Coordination namespace is uninitialized.")
        return await super().read_epoch()

    async def initialize_epoch(self):
        self.initialize_calls += 1
        self.initialized = True
        return await super().read_epoch()


def policy() -> HaRuntimePolicy:
    return HaRuntimePolicy.from_environment(
        {
            "OMNI_RUNTIME_MODE": "coordinated",
            "WORKERS": "1",
            "OMNI_REPLICA_COUNT": "1",
            "POSTGRESQL_URI": "postgresql://database/omni",
            "REDIS_URL": "redis://redis/0",
            "OMNI_COORDINATION_NAMESPACE": "production-east",
            "OMNI_DEPLOYMENT_ID": "gateway-east-01",
            "OMNI_COORDINATION_KEY": base64.urlsafe_b64encode(b"k" * 32).decode("ascii"),
            "OMNI_COORDINATION_EPOCH": "1",
        }
    )


class CoordinationBindingManagerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.storage = _Storage()
        self.store = InMemoryStateStore()
        self.manager = CoordinationBindingManager(self.storage, self.store)

    async def test_verify_requires_matching_durable_and_coordination_records(self) -> None:
        expected = CoordinationBinding.for_policy(
            policy(), "act_" + ("a" * 32), completed_migration_checkpoint()
        )
        self.storage.config[self.manager.DURABLE_KEY] = expected.to_dict()
        await self.store.set(self.manager.STORE_KEY, expected.to_dict())

        verified = await self.manager.verify(policy())

        self.assertEqual(verified, expected)
        self.assertNotIn("production-east", repr(verified))
        self.assertNotIn("k" * 32, repr(verified))

    async def test_shared_binding_accepts_canonical_json_transport(self) -> None:
        expected = CoordinationBinding.for_policy(
            policy(), "act_" + ("a" * 32), completed_migration_checkpoint()
        )
        self.storage.config[self.manager.DURABLE_KEY] = expected.to_dict()
        await self.store.set(
            self.manager.STORE_KEY,
            json.dumps(expected.to_dict(), separators=(",", ":"), sort_keys=True),
        )

        self.assertEqual(await self.manager.verify(policy()), expected)

    async def test_missing_or_mismatched_records_fail_with_safe_codes(self) -> None:
        expected = CoordinationBinding.for_policy(
            policy(), "act_" + ("a" * 32), completed_migration_checkpoint()
        )
        cases = []
        cases.append(({}, None, "durable_binding_missing"))
        cases.append(({self.manager.DURABLE_KEY: expected.to_dict()}, None, "namespace_missing"))
        mismatched = expected.to_dict()
        mismatched["fencing_epoch"] = 2
        cases.append(
            (
                {self.manager.DURABLE_KEY: expected.to_dict()},
                mismatched,
                "binding_mismatch",
            )
        )

        for durable, shared, code in cases:
            with self.subTest(code=code):
                storage = _Storage()
                storage.config.update(durable)
                store = InMemoryStateStore()
                if shared is not None:
                    await store.set(self.manager.STORE_KEY, shared)
                manager = CoordinationBindingManager(storage, store)
                with self.assertRaises(HaBindingError) as raised:
                    await manager.verify(policy())
                self.assertEqual(raised.exception.code, code)

    async def test_bootstrap_is_dry_run_first_and_closed_by_default(self) -> None:
        plan = await self.manager.bootstrap(
            policy(),
            activation_record="act_" + ("a" * 32),
            migration_plan_id=PLAN_ID,
            apply=False,
        )
        self.assertFalse(plan.applied)
        self.assertTrue(plan.prerequisite.eligible)
        self.assertIsNone(await self.store.get(self.manager.STORE_KEY))

        with self.assertRaises(HaBindingError) as raised:
            await self.manager.bootstrap(
                policy(),
                activation_record="act_" + ("a" * 32),
                migration_plan_id=PLAN_ID,
                apply=True,
            )
        self.assertEqual(raised.exception.code, "activation_gate_closed")

    async def test_dry_run_reports_missing_and_ineligible_migration_without_writing(self) -> None:
        self.storage.checkpoints.records.clear()
        missing = await self.manager.bootstrap(
            policy(),
            activation_record="act_" + ("a" * 32),
            migration_plan_id=PLAN_ID,
            apply=False,
        )
        self.assertIsNone(missing.binding)
        self.assertEqual(missing.prerequisite.code, "migration_checkpoint_missing")

        checkpoint = completed_migration_checkpoint()
        checkpoint = replace(
            checkpoint,
            phase=MigrationPhase.VERIFYING,
            authority=AuthoritySide.SOURCE,
            families=tuple(
                replace(item, verified=False) if index == 0 else item
                for index, item in enumerate(checkpoint.families)
            ),
        )
        self.storage.checkpoints.records[PLAN_ID] = checkpoint
        ineligible = await self.manager.bootstrap(
            policy(),
            activation_record="act_" + ("a" * 32),
            migration_plan_id=PLAN_ID,
            apply=False,
        )
        self.assertFalse(ineligible.prerequisite.eligible)
        self.assertEqual(
            ineligible.prerequisite.mismatched_families,
            (checkpoint.families[0].family.value,),
        )
        self.assertIsNone(await self.store.get(self.manager.STORE_KEY))

    async def test_verify_rejects_checkpoint_changed_after_binding(self) -> None:
        manager = CoordinationBindingManager(
            self.storage,
            self.store,
            activation_verifier=lambda _record: True,
        )
        await manager.bootstrap(
            policy(),
            activation_record="act_" + ("f" * 32),
            migration_plan_id=PLAN_ID,
            apply=True,
        )
        self.storage.checkpoints.records[PLAN_ID] = replace(
            completed_migration_checkpoint(), revision=5
        )

        with self.assertRaises(HaBindingError) as raised:
            await manager.verify(policy())

        self.assertEqual(raised.exception.code, "migration_checkpoint_mismatch")

    async def test_partial_bootstrap_resumes_without_overwriting_shared_marker(self) -> None:
        manager = CoordinationBindingManager(
            self.storage,
            self.store,
            activation_verifier=lambda _record: True,
        )
        self.storage.fail_next_write = True
        with self.assertRaises(HaBindingError) as raised:
            await manager.bootstrap(
                policy(),
                activation_record="act_" + ("b" * 32),
                migration_plan_id=PLAN_ID,
                apply=True,
            )
        self.assertEqual(raised.exception.code, "durable_write_failed")
        marker = await self.store.get(manager.STORE_KEY)
        self.assertIsNotNone(marker)

        result = await manager.bootstrap(
            policy(),
            activation_record="act_" + ("b" * 32),
            migration_plan_id=PLAN_ID,
            apply=True,
        )
        self.assertTrue(result.applied)
        self.assertEqual(await manager.verify(policy()), result.binding)
        self.assertEqual(await self.store.get(manager.STORE_KEY), marker)

    async def test_bootstrap_alone_initializes_a_fresh_epoch_namespace(self) -> None:
        store = _ExplicitNamespaceStore(initialized=False)
        manager = CoordinationBindingManager(
            self.storage,
            store,
            activation_verifier=lambda _record: True,
        )

        result = await manager.bootstrap(
            policy(),
            activation_record="act_" + ("c" * 32),
            migration_plan_id=PLAN_ID,
            apply=True,
        )

        self.assertTrue(result.applied)
        self.assertEqual(store.initialize_calls, 1)
        self.assertEqual(await manager.verify(policy()), result.binding)

    async def test_existing_durable_binding_never_bootstraps_a_lost_epoch_namespace(self) -> None:
        expected = CoordinationBinding.for_policy(
            policy(), "act_" + ("d" * 32), completed_migration_checkpoint()
        )
        self.storage.config[self.manager.DURABLE_KEY] = expected.to_dict()
        store = _ExplicitNamespaceStore(initialized=False)
        await store.set(self.manager.STORE_KEY, expected.to_dict())
        manager = CoordinationBindingManager(
            self.storage,
            store,
            activation_verifier=lambda _record: True,
        )

        with self.assertRaises(HaBindingError) as raised:
            await manager.bootstrap(
                policy(),
                activation_record=expected.activation_record,
                migration_plan_id=PLAN_ID,
                apply=True,
            )

        self.assertEqual(raised.exception.code, "epoch_namespace_missing")
        self.assertEqual(store.initialize_calls, 0)

    async def test_verify_reports_lost_epoch_namespace_without_reinitializing(self) -> None:
        expected = CoordinationBinding.for_policy(
            policy(), "act_" + ("e" * 32), completed_migration_checkpoint()
        )
        self.storage.config[self.manager.DURABLE_KEY] = expected.to_dict()
        store = _ExplicitNamespaceStore(initialized=False)
        await store.set(self.manager.STORE_KEY, expected.to_dict())
        manager = CoordinationBindingManager(self.storage, store)

        with self.assertRaises(HaBindingError) as raised:
            await manager.verify(policy())

        self.assertEqual(raised.exception.code, "epoch_namespace_missing")
        self.assertEqual(store.initialize_calls, 0)


if __name__ == "__main__":
    unittest.main()
