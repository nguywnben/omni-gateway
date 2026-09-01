"""Driver-boundary tests for the fenced Redis coordination store."""

from __future__ import annotations

import sys
import unittest
from collections import defaultdict, deque
from hashlib import sha256
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import (
    CasRequest,
    CoordinationCorruptError,
    CoordinationReconciliationRequiredError,
    CoordinationUnavailableError,
    EpochState,
    InvalidationRequest,
    QuotaCommitRequest,
    QuotaReservationRequest,
)
from core.redis_state_store import SCRIPT_SOURCES, RedisStateStore
from core.state_store import BaseStateStore
from core.state_store import RedisStateStore as CompatibilityRedisStateStore

EPOCH_READY = [b"1", b"ok", b"1", b"ready"]
NOSCRIPT_THEN_RELOAD = object()


class FakeRegisteredScript:
    def __init__(self, client: FakeRedisClient, source: str) -> None:
        self.client = client
        self.source = source
        self.name = source.splitlines()[0].removeprefix("-- omni:").removesuffix(":v1")

    async def __call__(self, *, keys: list[str], args: list[object]) -> object:
        self.client.script_calls.append((self.name, keys, args))
        response = self.client.script_replies[self.name].popleft()
        if response is NOSCRIPT_THEN_RELOAD:
            # redis-py's registered Script owns this bounded EVALSHA -> SCRIPT LOAD -> retry.
            self.client.script_loads += 1
            response = self.client.script_replies[self.name].popleft()
        if isinstance(response, BaseException):
            raise response
        return response


class FakeRedisClient:
    def __init__(self) -> None:
        self.registered: dict[str, FakeRegisteredScript] = {}
        self.script_replies: defaultdict[str, deque[object]] = defaultdict(deque)
        self.script_calls: list[tuple[str, list[str], list[object]]] = []
        self.script_loads = 0
        self.aclose_calls = 0
        self.command_calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
        self.command_replies: defaultdict[str, deque[object]] = defaultdict(deque)

    def register_script(self, source: str) -> FakeRegisteredScript:
        script = FakeRegisteredScript(self, source)
        self.registered[script.name] = script
        return script

    async def get(self, *args: object, **kwargs: object) -> object:
        return await self._command("get", *args, **kwargs)

    async def set(self, *args: object, **kwargs: object) -> object:
        return await self._command("set", *args, **kwargs)

    async def delete(self, *args: object, **kwargs: object) -> object:
        return await self._command("delete", *args, **kwargs)

    async def _command(self, name: str, *args: object, **kwargs: object) -> object:
        self.command_calls.append((name, args, kwargs))
        replies = self.command_replies[name]
        response = replies.popleft() if replies else None
        if isinstance(response, BaseException):
            raise response
        return response

    async def aclose(self) -> None:
        self.aclose_calls += 1


class ScriptRegistrationFailureClient(FakeRedisClient):
    def register_script(self, source: str) -> FakeRegisteredScript:
        raise RuntimeError("registration failed with redis://user:secret@example.invalid/0")


class FakeRedisModule:
    def __init__(self, client: FakeRedisClient | None = None) -> None:
        self.client = client or FakeRedisClient()
        self.calls: list[tuple[str, dict[str, object]]] = []
        self.error: BaseException | None = None

    def from_url(self, url: str, **kwargs: object) -> FakeRedisClient:
        self.calls.append((url, kwargs))
        if self.error is not None:
            raise self.error
        return self.client


class RedisStateStoreTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.client = FakeRedisClient()
        self.redis = FakeRedisModule(self.client)
        self.store = RedisStateStore(
            "redis://alice:super-secret@redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=self.redis,
        )

    def queue(self, script: str, *replies: object) -> None:
        self.client.script_replies[script].extend(replies)

    async def test_client_is_lazy_binary_safe_and_url_is_secret(self) -> None:
        self.assertEqual(self.redis.calls, [])
        rendered = repr(self.store)
        self.assertNotIn("alice", rendered)
        self.assertNotIn("super-secret", rendered)
        self.queue("epoch_read", EPOCH_READY)
        epoch = await self.store.read_epoch()
        self.assertEqual((epoch.epoch, epoch.state), (1, EpochState.READY))
        self.assertEqual(len(self.redis.calls), 1)
        _url, options = self.redis.calls[0]
        self.assertIs(options["decode_responses"], False)

    async def test_invalid_namespace_and_inputs_fail_before_client_access(self) -> None:
        with self.assertRaises(ValueError):
            RedisStateStore(
                "redis://alice:super-secret@redis.example/0",
                deployment_namespace="Prod West",
                _redis_module_for_testing=self.redis,
            )
        with self.assertRaises(ValueError):
            await self.store.advance_epoch(True, "advance")
        with self.assertRaises(ValueError):
            await self.store.read_invalidation_generation("\n")
        with self.assertRaises(ValueError):
            await self.store.set("key", float("nan"))
        self.assertEqual(self.redis.calls, [])

    def test_invalid_redis_url_fails_without_disclosing_it(self) -> None:
        with self.assertRaisesRegex(ValueError, "Redis URL is invalid") as caught:
            RedisStateStore(
                "https://alice:super-secret@example.invalid/0",
                deployment_namespace="prod-west",
                _redis_module_for_testing=self.redis,
            )
        self.assertNotIn("alice", str(caught.exception))
        self.assertNotIn("super-secret", str(caught.exception))

    async def test_close_is_idempotent_and_use_after_close_never_creates_client(self) -> None:
        await self.store.close()
        await self.store.close()
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_epoch()
        self.assertEqual(self.redis.calls, [])

        second = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=self.redis,
        )
        self.queue("epoch_read", EPOCH_READY)
        await second.read_epoch()
        await second.close()
        await second.close()
        self.assertEqual(self.client.aclose_calls, 1)

    async def test_all_keys_share_one_tag_and_hide_logical_names(self) -> None:
        self.queue("epoch_read", EPOCH_READY)
        self.queue("cas", [b"1", b"applied", b"1", b"0"])
        self.queue("invalidation_read", [b"1", b"ok", b""])
        await self.store.read_epoch()
        await self.store.compare_and_set(
            CasRequest("raw-customer-session", 0, b"\x00\xffpayload", 4.25, 1, "raw-cas-op")
        )
        await self.store.read_invalidation_generation("raw-auth-scope")

        keys = [key for _name, call_keys, _args in self.client.script_calls for key in call_keys]
        tags = {key[key.index("{") + 1 : key.index("}")] for key in keys}
        self.assertEqual(len(tags), 1)
        rendered_keys = " ".join(keys)
        self.assertNotIn("prod-west", rendered_keys)
        self.assertNotIn("raw-customer-session", rendered_keys)
        self.assertNotIn("raw-auth-scope", rendered_keys)
        cas_args = self.client.script_calls[1][2]
        self.assertIn(b"\x00\xffpayload", cas_args)

    async def test_key_layout_is_deterministic_across_instances(self) -> None:
        other_client = FakeRedisClient()
        other = RedisStateStore(
            "redis://elsewhere/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=FakeRedisModule(other_client),
        )
        self.queue("epoch_read", EPOCH_READY)
        other_client.script_replies["epoch_read"].append(EPOCH_READY)
        await self.store.read_epoch()
        await other.read_epoch()
        self.assertEqual(self.client.script_calls[0][1], other_client.script_calls[0][1])

        expected_tag = sha256(b"prod-west").hexdigest()
        self.assertIn(f"{{{expected_tag}}}", self.client.script_calls[0][1][0])

    async def test_partial_lazy_initialization_closes_the_created_client(self) -> None:
        client = ScriptRegistrationFailureClient()
        store = RedisStateStore(
            "redis://alice:super-secret@redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        with self.assertRaises(CoordinationUnavailableError) as caught:
            await store.read_epoch()

        self.assertEqual(client.aclose_calls, 1)
        self.assertNotIn("alice", str(caught.exception))
        self.assertNotIn("super-secret", str(caught.exception))

    async def test_exact_epoch_keys_and_args_and_registered_script_reload_boundary(self) -> None:
        self.queue("epoch_advance", NOSCRIPT_THEN_RELOAD, [b"1", b"ok", b"2", b"reconciling"])
        epoch = await self.store.advance_epoch(1, "advance-1")
        self.assertEqual((epoch.epoch, epoch.state), (2, EpochState.RECONCILING))
        self.assertEqual(self.client.script_loads, 1)
        self.assertEqual(len(self.client.script_calls), 1)
        name, keys, args = self.client.script_calls[0]
        self.assertEqual(name, "epoch_advance")
        self.assertEqual(len(keys), 3)
        self.assertEqual(args[:3], [b"1", b"advance-1", b"2592000000"])
        self.assertEqual(args[-1], b"100000")

    async def test_cas_keys_and_args_are_exact_and_replay_result_is_strict(self) -> None:
        self.queue("cas", [b"1", b"applied", b"7", b"1"])
        request = CasRequest("opaque-key", 6, b"\x00value\xff", 2.5, 3, "cas-op")
        result = await self.store.compare_and_set(request)
        self.assertEqual((result.applied, result.revision, result.idempotent), (True, 7, True))
        name, keys, args = self.client.script_calls[0]
        self.assertEqual((name, len(keys)), ("cas", 4))
        self.assertEqual(args[:5], [b"6", b"\x00value\xff", b"2500", b"3", b"cas-op"])
        self.assertEqual(len(args[5]), 64)
        self.assertEqual(args[6], b"100000")

    async def test_numeric_ttl_forms_have_identical_replay_fingerprints(self) -> None:
        self.queue("cas", [b"1", b"applied", b"1", b"0"], [b"1", b"applied", b"1", b"1"])
        await self.store.compare_and_set(CasRequest("key", 0, b"value", 1, 1, "cas-op"))
        await self.store.compare_and_set(CasRequest("key", 0, b"value", 1.0, 1, "cas-op"))

        cas_fingerprints = [call[2][5] for call in self.client.script_calls]
        self.assertEqual(cas_fingerprints[0], cas_fingerprints[1])

        self.client.script_calls.clear()
        self.queue(
            "invalidation",
            [b"1", b"applied", b"1", b"0"],
            [b"1", b"applied", b"1", b"1"],
        )
        await self.store.invalidate(InvalidationRequest("scope", 1, "invalidate-op", 1))
        await self.store.invalidate(InvalidationRequest("scope", 1, "invalidate-op", 1.0))

        invalidation_fingerprints = [call[2][3] for call in self.client.script_calls]
        self.assertEqual(invalidation_fingerprints[0], invalidation_fingerprints[1])

    async def test_invalidation_args_and_stale_reconciling_outcomes(self) -> None:
        self.queue(
            "invalidation",
            [b"1", b"not_applied", b"", b"0"],
            [b"1", b"applied", b"4", b"1"],
        )
        stale = await self.store.invalidate(InvalidationRequest("scope", 1, "op-1", 2.0))
        replay = await self.store.invalidate(InvalidationRequest("scope", 2, "op-2", 3.0))
        self.assertEqual((stale.applied, stale.generation), (False, None))
        self.assertEqual((replay.applied, replay.generation, replay.idempotent), (True, 4, True))
        _name, keys, args = self.client.script_calls[1]
        self.assertEqual(len(keys), 4)
        self.assertEqual(args[:3], [b"2", b"op-2", b"3000"])
        self.assertEqual(len(args[3]), 64)
        self.assertEqual(args[4], b"100000")

    async def test_reconciliation_status_raises_typed_error(self) -> None:
        self.queue("cas", [b"1", b"reconciliation_required", b"", b"0"])
        with self.assertRaises(CoordinationReconciliationRequiredError):
            await self.store.compare_and_set(CasRequest("key", 0, b"value", 1, 1, "op"))

    async def test_corrupt_unknown_and_bool_or_float_like_replies_fail_closed(self) -> None:
        corrupt_replies = (
            [b"2", b"ok", b"1", b"ready"],
            [b"1", b"unknown", b"1", b"ready"],
            [b"1", b"ok", b"1.0", b"ready"],
            [b"1", b"ok", True, b"ready"],
            ["1", b"ok", b"1", b"ready"],
        )
        for reply in corrupt_replies:
            with self.subTest(reply=reply):
                client = FakeRedisClient()
                client.script_replies["epoch_read"].append(reply)
                store = RedisStateStore(
                    "redis://redis.example/0",
                    deployment_namespace="prod-west",
                    _redis_module_for_testing=FakeRedisModule(client),
                )
                with self.assertRaises(CoordinationCorruptError):
                    await store.read_epoch()

    async def test_connection_and_protocol_failures_are_secret_free(self) -> None:
        self.redis.error = ConnectionError(
            "cannot connect redis://alice:super-secret@redis.example/0"
        )
        with self.assertRaises(CoordinationUnavailableError) as caught:
            await self.store.read_epoch()
        self.assertNotIn("alice", str(caught.exception))
        self.assertNotIn("super-secret", str(caught.exception))

        client = FakeRedisClient()
        client.script_replies["epoch_read"].append(RuntimeError("protocol leaked-secret"))
        store = RedisStateStore(
            "redis://bob:hidden@redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        with self.assertRaises(CoordinationUnavailableError) as script_caught:
            await store.read_epoch()
        self.assertNotIn("leaked-secret", str(script_caught.exception))

        corrupt_client = FakeRedisClient()
        corrupt_client.script_replies["epoch_read"].append(
            RuntimeError("WRONGTYPE key contained secret-value")
        )
        corrupt_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=FakeRedisModule(corrupt_client),
        )
        with self.assertRaises(CoordinationCorruptError) as corrupt_caught:
            await corrupt_store.read_epoch()
        self.assertNotIn("secret-value", str(corrupt_caught.exception))

        wrongtype_client = FakeRedisClient()
        wrongtype_client.command_replies["get"].append(
            RuntimeError("WRONGTYPE key contained another-secret-value")
        )
        wrongtype_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=FakeRedisModule(wrongtype_client),
        )
        with self.assertRaises(CoordinationCorruptError) as wrongtype_caught:
            await wrongtype_store.get("key")
        self.assertNotIn("another-secret-value", str(wrongtype_caught.exception))

    async def test_generic_transport_is_hashed_bounded_and_lock_release_is_token_safe(self) -> None:
        self.client.command_replies["set"].append(True)
        self.client.script_replies["lock_release"].append([b"1", b"ok", b"1"])
        acquired = await self.store.acquire_lock("raw-lock-name", 1.5)
        await self.store.release_lock("raw-lock-name")
        self.assertTrue(acquired)
        _command, (redis_key, token), options = self.client.command_calls[0]
        self.assertNotIn("raw-lock-name", redis_key)
        self.assertEqual(options, {"nx": True, "px": 1500})
        _name, keys, args = self.client.script_calls[0]
        self.assertEqual(keys, [redis_key])
        self.assertEqual(args, [token])

    async def test_generic_get_set_delete_and_increment_preserve_binary_values(self) -> None:
        self.client.command_replies["set"].append(True)
        self.client.command_replies["get"].append(b"\x00binary\xff")
        self.client.command_replies["delete"].append(1)
        self.client.script_replies["increment"].append([b"1", b"ok", b"6"])

        await self.store.set("raw-generic-key", b"\x00binary\xff", ttl_seconds=2.25)
        value = await self.store.get("raw-generic-key")
        incremented = await self.store.increment("raw-generic-key", 5, ttl_seconds=3)
        await self.store.delete("raw-generic-key")

        self.assertEqual(value, b"\x00binary\xff")
        self.assertEqual(incremented, 6)
        command_keys = [args[0] for _name, args, _kwargs in self.client.command_calls]
        script_key = self.client.script_calls[0][1][0]
        self.assertTrue(all(key == script_key for key in command_keys))
        self.assertNotIn("raw-generic-key", script_key)
        self.assertEqual(self.client.script_calls[0][2], [b"5", b"3000"])

    async def test_quota_methods_fail_closed_until_task_four(self) -> None:
        reserve = QuotaReservationRequest(
            "reservation",
            "key",
            1.0,
            1.0,
            1,
            0.1,
            1,
            1,
            None,
            None,
            0.0,
            0.0,
            1.0,
            1.0,
        )
        commit = QuotaCommitRequest("reservation", 1.0, 1, 0.1, True)
        for operation in (
            self.store.reserve_quota(reserve),
            self.store.commit_quota(commit),
            self.store.release_quota("reservation", now=1.0),
        ):
            with self.assertRaisesRegex(
                CoordinationUnavailableError, "not available until Task 4/HA activation"
            ):
                await operation
        self.assertEqual(self.redis.calls, [])

    def test_scripts_are_fixed_cluster_safe_and_bounded(self) -> None:
        self.assertEqual(
            set(SCRIPT_SOURCES),
            {
                "epoch_read",
                "epoch_advance",
                "epoch_ready",
                "cas",
                "invalidation",
                "invalidation_read",
                "increment",
                "lock_release",
            },
        )
        for name, source in SCRIPT_SOURCES.items():
            with self.subTest(name=name):
                upper = source.upper()
                self.assertNotIn("REDIS.CALL('KEYS'", upper)
                self.assertNotIn('REDIS.CALL("KEYS"', upper)
                self.assertNotIn("REDIS.CALL('SCAN'", upper)
                self.assertNotIn('REDIS.CALL("SCAN"', upper)
                self.assertNotIn("WHILE ", upper)
                if "ZRANGEBYSCORE" in upper:
                    self.assertIn("LIMIT', 0, 257", source)
                    self.assertIn("#due > 256", source)
                    self.assertIn("redis.call('ZCARD'", source)
                    self.assertLess(
                        source.index("local due = redis.call('ZRANGEBYSCORE'"),
                        source.index("redis.call('HDEL'"),
                    )

        cas_source = SCRIPT_SOURCES["cas"]
        self.assertIn("redis.call('PTTL', KEYS[2])", cas_source)
        self.assertIn("#record[3] > 16384", cas_source)

        for name in ("epoch_advance", "epoch_ready", "cas", "invalidation"):
            with self.subTest(name=name):
                self.assertIn(
                    "not valid_integer(replay_expiry)",
                    SCRIPT_SOURCES[name],
                    "A corrupt ZSCORE must fail closed before tonumber().",
                )

    def test_compatibility_reexport_and_virtual_subclass(self) -> None:
        self.assertIs(CompatibilityRedisStateStore, RedisStateStore)
        self.assertTrue(issubclass(RedisStateStore, BaseStateStore))
        self.assertIsInstance(self.store, BaseStateStore)


if __name__ == "__main__":
    unittest.main()
