"""Driver-boundary tests for the fenced Redis coordination store."""

from __future__ import annotations

import asyncio
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


class StatefulRegisteredScript:
    """A bounded driver harness that models public Redis-script semantics, not replies."""

    def __init__(self, client: StatefulRedisClient, source: str) -> None:
        self.client = client
        self.source = source
        self.name = source.splitlines()[0].removeprefix("-- omni:").removesuffix(":v1")
        assert SCRIPT_SOURCES[self.name] == source

    async def __call__(self, *, keys: list[str], args: list[object]) -> object:
        self.client.script_calls.append((self.name, keys, args))
        return self.client.run_script(self.name, keys, args)


class StatefulRedisClient(FakeRedisClient):
    """Small deterministic driver model for Task 3's public transition sequence."""

    _KEY_COUNTS = {
        "epoch_read": (1, 0),
        "epoch_advance": (3, 4),
        "epoch_ready": (3, 4),
        "cas": (4, 7),
        "invalidation": (4, 5),
        "invalidation_read": (1, 0),
        "increment": (1, 2),
        "lock_release": (1, 1),
    }

    def __init__(self) -> None:
        super().__init__()
        self.now_ms = 1_000_000
        self.epoch = (1, b"ready")
        self.cas: dict[str, tuple[int, bytes, int]] = {}
        self.generations: dict[str, int] = {}
        self.replays: defaultdict[str, dict[bytes, tuple[bytes, list[bytes], int]]] = defaultdict(
            dict
        )
        self.values: dict[str, tuple[bytes, int | None]] = {}

    def register_script(self, source: str) -> StatefulRegisteredScript:
        script = StatefulRegisteredScript(self, source)
        self.registered[script.name] = script  # type: ignore[assignment]
        return script

    def advance(self, milliseconds: int) -> None:
        self.now_ms += milliseconds

    def _expired(self, expires_at: int | None) -> bool:
        return expires_at is not None and expires_at <= self.now_ms

    def _replay(self, name: str, operation_id: bytes, fingerprint: bytes) -> list[bytes] | None:
        entries = self.replays[name]
        due = [
            identifier
            for identifier, (_fingerprint, _result, expiry) in entries.items()
            if expiry <= self.now_ms
        ]
        if len(due) > 256:
            return [b"1", b"reconciliation_required", b"", b"0"]
        for identifier in due:
            del entries[identifier]
        saved = entries.get(operation_id)
        if saved is None:
            return None
        saved_fingerprint, result, _expiry = saved
        if saved_fingerprint == fingerprint:
            replay = list(result)
            if len(replay) == 4 and replay[1] in {b"applied", b"not_applied"}:
                replay[3] = b"1"
            return replay
        return [b"1", b"not_applied", b"", b"0"]

    def _remember(
        self,
        name: str,
        operation_id: bytes,
        fingerprint: bytes,
        result: list[bytes],
        ttl_ms: int,
        limit: int,
    ) -> list[bytes] | None:
        if len(self.replays[name]) >= limit:
            return [b"1", b"reconciliation_required", b"", b"0"]
        self.replays[name][operation_id] = (fingerprint, result, self.now_ms + ttl_ms)
        return None

    async def _command(self, name: str, *args: object, **kwargs: object) -> object:
        self.command_calls.append((name, args, kwargs))
        key = args[0]
        assert isinstance(key, str)
        stored = self.values.get(key)
        if stored is not None and self._expired(stored[1]):
            del self.values[key]
            stored = None
        if name == "get":
            return None if stored is None else stored[0]
        if name == "delete":
            if stored is None:
                return 0
            del self.values[key]
            return 1
        assert name == "set"
        value = args[1]
        assert isinstance(value, bytes)
        if kwargs.get("nx") and stored is not None:
            return None
        ttl = kwargs.get("px")
        assert ttl is None or isinstance(ttl, int)
        self.values[key] = (value, None if ttl is None else self.now_ms + ttl)
        return True

    def run_script(self, name: str, keys: list[str], args: list[object]) -> list[bytes]:
        key_count, arg_count = self._KEY_COUNTS[name]
        assert len(keys) == key_count and len(args) == arg_count
        assert all(isinstance(key, str) and "{" in key and "}" in key for key in keys)
        assert len({key[key.index("{") + 1 : key.index("}")] for key in keys}) == 1
        assert all(isinstance(arg, bytes) for arg in args)
        byte_args = [arg for arg in args if isinstance(arg, bytes)]
        if name == "epoch_read":
            return [b"1", b"ok", str(self.epoch[0]).encode(), self.epoch[1]]
        if name in {"epoch_advance", "epoch_ready"}:
            expected, operation_id, ttl, limit = byte_args
            existing = self._replay(name, operation_id, expected)
            if existing is not None:
                if existing[1] == b"reconciliation_required":
                    return [b"1", b"reconciliation_required", b"", b""]
                if existing[1] == b"not_applied":
                    return [b"1", b"ok", str(self.epoch[0]).encode(), self.epoch[1]]
                return existing
            expected_int, limit_int = int(expected), int(limit)
            if name == "epoch_advance" and self.epoch == (expected_int, b"ready"):
                result = [b"1", b"ok", str(expected_int + 1).encode(), b"reconciling"]
                capacity = self._remember(name, operation_id, expected, result, int(ttl), limit_int)
                if capacity is not None:
                    return [b"1", b"reconciliation_required", b"", b""]
                self.epoch = (expected_int + 1, b"reconciling")
                return result
            if name == "epoch_ready" and self.epoch == (expected_int, b"reconciling"):
                result = [b"1", b"ok", expected, b"ready"]
                capacity = self._remember(name, operation_id, expected, result, int(ttl), limit_int)
                if capacity is not None:
                    return [b"1", b"reconciliation_required", b"", b""]
                self.epoch = (expected_int, b"ready")
                return result
            return [b"1", b"ok", str(self.epoch[0]).encode(), self.epoch[1]]
        if name == "cas":
            expected, payload, ttl, epoch, operation_id, fingerprint, limit = byte_args
            if self.epoch != (int(epoch), b"ready"):
                return [b"1", b"not_applied", b"", b"0"]
            existing = self._replay(name, operation_id, fingerprint)
            if existing is not None:
                return existing
            record = self.cas.get(keys[1])
            if record is not None and record[2] <= self.now_ms:
                del self.cas[keys[1]]
                record = None
            revision = 1 if record is None else record[0] + 1
            applied = (record is None and expected == b"0") or (
                record is not None and record[0] == int(expected)
            )
            result = (
                [b"1", b"applied", str(revision).encode(), b"0"]
                if applied
                else [b"1", b"not_applied", b"", b"0"]
            )
            capacity = self._remember(name, operation_id, fingerprint, result, int(ttl), int(limit))
            if capacity is not None:
                return capacity
            if applied:
                self.cas[keys[1]] = (revision, payload, self.now_ms + int(ttl))
            return result
        if name == "invalidation":
            epoch, operation_id, ttl, fingerprint, limit = byte_args
            if self.epoch != (int(epoch), b"ready"):
                return [b"1", b"not_applied", b"", b"0"]
            existing = self._replay(name, operation_id, fingerprint)
            if existing is not None:
                return existing
            generation = self.generations.get(keys[1], 0) + 1
            result = [b"1", b"applied", str(generation).encode(), b"0"]
            capacity = self._remember(name, operation_id, fingerprint, result, int(ttl), int(limit))
            if capacity is not None:
                return capacity
            self.generations[keys[1]] = generation
            return result
        if name == "invalidation_read":
            generation = self.generations.get(keys[0])
            return [b"1", b"ok", b"" if generation is None else str(generation).encode()]
        if name == "increment":
            amount, ttl = byte_args
            current = self.values.get(keys[0])
            value = 0 if current is None or self._expired(current[1]) else int(current[0])
            value += int(amount)
            self.values[keys[0]] = (
                str(value).encode(),
                None if not ttl else self.now_ms + int(ttl),
            )
            return [b"1", b"ok", str(value).encode()]
        assert name == "lock_release"
        stored = self.values.get(keys[0])
        deleted = stored is not None and not self._expired(stored[1]) and stored[0] == byte_args[0]
        if deleted:
            del self.values[keys[0]]
        return [b"1", b"ok", b"1" if deleted else b"0"]


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

    async def test_operation_specific_reply_forms_reject_impossible_replay_flags(self) -> None:
        self.queue("cas", [b"1", b"not_applied", b"", b"1"], [b"1", b"applied", b"", b"0"])
        for request in (
            CasRequest("key", 0, b"value", 1, 1, "not-applied-replay"),
            CasRequest("key", 0, b"value", 1, 1, "missing-revision"),
        ):
            with self.subTest(request=request.operation_id):
                with self.assertRaises(CoordinationCorruptError):
                    await self.store.compare_and_set(request)

        self.queue(
            "invalidation",
            [b"1", b"not_applied", b"", b"1"],
            [b"1", b"applied", b"", b"0"],
        )
        for request in (
            InvalidationRequest("scope", 1, "not-applied-replay", 1),
            InvalidationRequest("scope", 1, "missing-generation", 1),
        ):
            with self.subTest(request=request.operation_id):
                with self.assertRaises(CoordinationCorruptError):
                    await self.store.invalidate(request)

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

    async def test_generic_get_set_delete_and_increment_preserve_legacy_text_values(self) -> None:
        self.client.command_replies["set"].append(True)
        self.client.command_replies["get"].append(b"42")
        self.client.command_replies["delete"].append(1)
        self.client.script_replies["increment"].append([b"1", b"ok", b"6"])

        await self.store.set("raw-generic-key", 42, ttl_seconds=2.25)
        value = await self.store.get("raw-generic-key")
        incremented = await self.store.increment("raw-generic-key", 5, ttl_seconds=3)
        await self.store.delete("raw-generic-key")

        self.assertEqual(value, "42")
        self.assertEqual(incremented, 6)
        command_keys = [args[0] for _name, args, _kwargs in self.client.command_calls]
        script_key = self.client.script_calls[0][1][0]
        self.assertTrue(all(key == script_key for key in command_keys))
        self.assertNotIn("raw-generic-key", script_key)
        self.assertEqual(self.client.command_calls[0][1][1], b"42")
        self.assertEqual(self.client.script_calls[0][2], [b"5", b"3000"])

    async def test_generic_non_utf8_and_noncanonical_integer_replies_fail_closed(self) -> None:
        self.client.command_replies["get"].append(b"\xff")
        with self.assertRaises(CoordinationCorruptError):
            await self.store.get("key")

        for reply in ([b"1", b"ok", b"-0"], [b"1", b"ok", b"+1"], [b"1", b"ok", b"01"]):
            with self.subTest(reply=reply):
                self.client.script_replies["increment"].append(reply)
                with self.assertRaises(CoordinationCorruptError):
                    await self.store.increment("counter")

    async def test_stateful_driver_exercises_fenced_public_sequence_and_bounds(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="prod-west",
            _coordination_replay_limit_for_testing=2,
            _redis_module_for_testing=FakeRedisModule(client),
        )
        self.assertEqual((await store.read_epoch()).state, EpochState.READY)
        self.assertEqual((await store.advance_epoch(1, "advance")).state, EpochState.RECONCILING)
        self.assertFalse(
            (await store.compare_and_set(CasRequest("key", 0, b"one", 1, 1, "stale"))).applied
        )
        self.assertEqual((await store.mark_epoch_ready(2, "ready")).state, EpochState.READY)

        created = await store.compare_and_set(CasRequest("key", 0, b"one", 1, 2, "create"))
        replay = await store.compare_and_set(CasRequest("key", 0, b"one", 1, 2, "create"))
        conflict = await store.compare_and_set(CasRequest("key", 0, b"changed", 1, 2, "create"))
        self.assertEqual((created.applied, created.revision), (True, 1))
        self.assertTrue(replay.idempotent)
        self.assertFalse(conflict.applied)
        client.advance(1_000)
        self.assertTrue(
            (await store.compare_and_set(CasRequest("key", 0, b"two", 1, 2, "expired"))).applied
        )

        invalidated = await store.invalidate(InvalidationRequest("scope", 2, "invalidate", 1))
        invalidation_replay = await store.invalidate(
            InvalidationRequest("scope", 2, "invalidate", 1)
        )
        self.assertEqual((await store.read_invalidation_generation("scope")).generation, 1)
        self.assertEqual((invalidated.generation, invalidation_replay.idempotent), (1, True))
        await store.set("generic", {"value": 1})
        self.assertEqual(await store.get("generic"), "{'value': 1}")
        self.assertEqual(await store.increment("counter", 2), 2)

        cap_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="other-zone",
            _coordination_replay_limit_for_testing=1,
            _redis_module_for_testing=FakeRedisModule(StatefulRedisClient()),
        )
        await cap_store.compare_and_set(CasRequest("cap", 0, b"one", 5, 1, "one"))
        with self.assertRaises(CoordinationReconciliationRequiredError):
            await cap_store.compare_and_set(CasRequest("other", 0, b"two", 5, 1, "two"))

        cleanup_client = StatefulRedisClient()
        cleanup_client.replays["cas"] = {
            f"due-{index}".encode(): (b"fingerprint", [b"1", b"applied", b"1", b"0"], 0)
            for index in range(257)
        }
        cleanup_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="cleanup-zone",
            _redis_module_for_testing=FakeRedisModule(cleanup_client),
        )
        with self.assertRaises(CoordinationReconciliationRequiredError):
            await cleanup_store.compare_and_set(CasRequest("cleanup", 0, b"one", 5, 1, "cleanup"))

    async def test_lock_release_is_bound_to_the_acquiring_task(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        acquired_by_old = asyncio.Event()
        acquired_by_new = asyncio.Event()
        allow_old_release = asyncio.Event()
        old_released = asyncio.Event()

        async def old_owner() -> None:
            self.assertTrue(await store.acquire_lock("lock", 1))
            acquired_by_old.set()
            await allow_old_release.wait()
            await store.release_lock("lock")
            old_released.set()

        async def new_owner() -> None:
            await acquired_by_old.wait()
            client.advance(1_000)
            self.assertTrue(await store.acquire_lock("lock", 1))
            acquired_by_new.set()
            await old_released.wait()
            await store.release_lock("lock")

        old_task = asyncio.create_task(old_owner())
        new_task = asyncio.create_task(new_owner())
        await acquired_by_new.wait()
        allow_old_release.set()
        await asyncio.gather(old_task, new_task)

        release_calls = [call for call in client.script_calls if call[0] == "lock_release"]
        self.assertEqual(len(release_calls), 2)
        old_token = client.command_calls[0][1][1]
        new_token = client.command_calls[1][1][1]
        self.assertEqual(release_calls[0][2], [old_token])
        self.assertEqual(release_calls[1][2], [new_token])

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
                    "local function valid_replay(value, score)",
                    SCRIPT_SOURCES[name],
                    "Replay hash/ZSET pairs must be strict before tonumber().",
                )
                self.assertIn("for _, operation_id in ipairs(due) do", SCRIPT_SOURCES[name])
                self.assertTrue(
                    "saved_expiry == score" in SCRIPT_SOURCES[name]
                    or "saved_expiry ~= score" in SCRIPT_SOURCES[name]
                )
                self.assertIn("string.format('%.0f', expires_at)", SCRIPT_SOURCES[name])

        self.assertIn("saved_epoch ~= next_integer(ARGV[1])", SCRIPT_SOURCES["epoch_advance"])
        self.assertIn("saved_state ~= 'reconciling'", SCRIPT_SOURCES["epoch_advance"])
        self.assertIn("saved_epoch ~= ARGV[1]", SCRIPT_SOURCES["epoch_ready"])
        self.assertIn("saved_state ~= 'ready'", SCRIPT_SOURCES["epoch_ready"])

    def test_compatibility_reexport_and_virtual_subclass(self) -> None:
        self.assertIs(CompatibilityRedisStateStore, RedisStateStore)
        self.assertTrue(issubclass(RedisStateStore, BaseStateStore))
        self.assertIsInstance(self.store, BaseStateStore)


if __name__ == "__main__":
    unittest.main()
