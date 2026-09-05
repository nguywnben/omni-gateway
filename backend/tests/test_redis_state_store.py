"""Driver-boundary tests for the fenced Redis coordination store."""

from __future__ import annotations

import asyncio
import copy
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
from tests.coordination_store_contract import CoordinationStoreContract

EPOCH_READY = [b"1", b"ok", b"1", b"ready"]
NOSCRIPT_THEN_RELOAD = object()


class FakeRegisteredScript:
    def __init__(self, client: FakeRedisClient, source: str) -> None:
        self.client = client
        self.source = source
        self.name = source.splitlines()[0].removeprefix("-- omni:").rsplit(":v", 1)[0]

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

    async def scan(self, *args: object, **kwargs: object) -> object:
        return await self._command("scan", *args, **kwargs)

    async def hlen(self, *args: object, **kwargs: object) -> object:
        return await self._command("hlen", *args, **kwargs)

    async def zcard(self, *args: object, **kwargs: object) -> object:
        return await self._command("zcard", *args, **kwargs)

    async def zrange(self, *args: object, **kwargs: object) -> object:
        return await self._command("zrange", *args, **kwargs)

    async def hget(self, *args: object, **kwargs: object) -> object:
        return await self._command("hget", *args, **kwargs)

    async def time(self, *args: object, **kwargs: object) -> object:
        return await self._command("time", *args, **kwargs)

    async def pttl(self, *args: object, **kwargs: object) -> object:
        return await self._command("pttl", *args, **kwargs)

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


class ControlledCloseRedisClient(FakeRedisClient):
    def __init__(self, *close_errors: BaseException) -> None:
        super().__init__()
        self.close_errors = deque(close_errors)
        self.close_started = asyncio.Event()
        self.close_release = asyncio.Event()
        self.close_completed = False

    def reset_close_barrier(self) -> None:
        self.close_started = asyncio.Event()
        self.close_release = asyncio.Event()

    async def aclose(self) -> None:
        self.aclose_calls += 1
        self.close_started.set()
        await self.close_release.wait()
        if self.close_errors:
            raise self.close_errors.popleft()
        self.close_completed = True


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
        self.name = source.splitlines()[0].removeprefix("-- omni:").rsplit(":v", 1)[0]
        assert SCRIPT_SOURCES[self.name] == source

    async def __call__(self, *, keys: list[str], args: list[object]) -> object:
        self.client.script_calls.append((self.name, keys, args))
        if "local admission_fenced" in self.source:
            assert keys[-2].endswith(sha256(b"ha-runtime-drain-v1").hexdigest())
            assert keys[-1].endswith(sha256(b"ha-runtime-binding-v1").hexdigest())
            assert len({key.split("{")[1].split("}")[0] for key in keys}) == 1
            entry = self.client.values.get(keys[-2])
            self.client.admission_fenced = entry is not None
            if entry is not None:
                binding_entry = self.client.values.get(keys[-1])
                try:
                    from core.coordination import AdmissionFence, decode_admission_json

                    value = decode_admission_json(entry[0])
                    AdmissionFence.decode(value)
                    binding = decode_admission_json(binding_entry[0])
                    valid = (
                        entry[1] is None
                        and binding_entry[1] is None
                        and type(binding["schema_version"]) is int
                        and binding["schema_version"] == 1
                        and set(value)
                        == {
                            "schema_version",
                            "namespace_digest",
                            "epoch",
                            "quota_reconciliation_cursor",
                            "quota_reconciliation_complete",
                        }
                        and value["schema_version"] == 2
                        and type(value["epoch"]) is int
                        and value["namespace_digest"]
                        == binding["namespace_digest"]
                        == args[-1].decode()
                        and binding["fencing_epoch"] == self.client.epoch[0]
                        and (
                            value["epoch"] == self.client.epoch[0]
                            or (
                                value["epoch"] == self.client.epoch[0] - 1
                                and value["quota_reconciliation_complete"] is True
                            )
                        )
                    )
                except (TypeError, ValueError, KeyError):
                    valid = False
                if not valid:
                    raise RuntimeError("COORDINATION_CORRUPT")
            keys, args = keys[:-2], args[:-1]
            if self.name == "drain_complete":
                epoch, operation, expected = args
                replay = self.client.replays["epoch_ready"].get(operation)
                if (
                    replay is None
                    or replay[0] != epoch
                    or replay[2] <= self.client.now_ms
                    or self.client.epoch != (int(epoch), b"ready")
                    or (entry is not None and entry[0] != expected)
                ):
                    raise RuntimeError("COORDINATION_DRAIN_CONFLICT")
                self.client.values.pop(self.client.script_calls[-1][1][-2], None)
                return [b"1", b"ok"]
            if self.name == "cas":
                operation, fingerprint, proof_target, requested_target, capabilities = args[7:]
                args = [*args[:7], capabilities]
                if operation:
                    settled = self.client.replays["cas"].get(args[4])
                    if (
                        settled is not None
                        and settled[0] == args[5]
                        and settled[2] > self.client.now_ms
                    ):
                        return [*settled[1][:-1], b"1"]
                    proof = self.client.replays["cas"].get(operation)
                    admitted_capabilities = self.client.cas_capabilities.get(operation, b"")
                    if (
                        proof is None
                        or proof[0] != fingerprint
                        or proof[1][1] != b"applied"
                        or proof[2] <= self.client.now_ms
                        or proof_target != requested_target
                        or proof_target not in admitted_capabilities.split(b",")
                    ):
                        raise RuntimeError("COORDINATION_ADMISSION_FENCED")
                elif entry is not None:
                    raise RuntimeError("COORDINATION_ADMISSION_FENCED")
            elif entry is not None and self.name not in {
                "quota_commit",
                "quota_release",
                "oidc_transaction_consume",
            }:
                raise RuntimeError("COORDINATION_ADMISSION_FENCED")
        reply = self.client.run_script(self.name, keys, args)
        if self.name in self.client.cancel_after_response_boundary:
            self.client.cancel_after_response_boundary.remove(self.name)
            raise asyncio.CancelledError()
        return reply


class _StatefulPipeline:
    def __init__(self, client: StatefulRedisClient) -> None:
        self.client = client
        self.operations: list[tuple[str, str, tuple[bytes, ...]]] = []

    async def __aenter__(self) -> _StatefulPipeline:
        return self

    async def __aexit__(self, *_args: object) -> None:
        return None

    def hdel(self, key: str, *members: bytes) -> None:
        self.operations.append(("hdel", key, members))

    def zrem(self, key: str, *members: bytes) -> None:
        self.operations.append(("zrem", key, members))

    def delete(self, key: str) -> None:
        self.operations.append(("delete", key, ()))

    async def execute(self) -> list[int]:
        results: list[int] = []
        for operation, key, members in self.operations:
            if operation == "hdel":
                target = self.client.redis_hashes.setdefault(key, {})
                removed = sum(member in target for member in members)
                for member in members:
                    target.pop(member, None)
                if not target:
                    self.client.redis_hashes.pop(key, None)
                results.append(removed)
            elif operation == "zrem":
                target = self.client.redis_zsets.setdefault(key, {})
                removed = sum(member in target for member in members)
                for member in members:
                    target.pop(member, None)
                if not target:
                    self.client.redis_zsets.pop(key, None)
                results.append(removed)
            else:
                removed = int(
                    self.client.values.pop(key, None) is not None
                    or self.client.redis_hashes.pop(key, None) is not None
                    or self.client.redis_zsets.pop(key, None) is not None
                )
                results.append(removed)
        return results


class StatefulRedisClient(FakeRedisClient):
    """Small deterministic driver model for Task 3's public transition sequence."""

    _KEY_COUNTS = {
        "epoch_read": (2, 0),
        "time_read": (2, 1),
        "epoch_advance": (4, 4),
        "epoch_ready": (4, 4),
        "cas": (5, 8),
        "cas_read": (3, 1),
        "invalidation": (5, 5),
        "invalidation_read": (3, 0),
        "increment": (1, 2),
        "lock_release": (1, 1),
        "quota_reserve": (10, 20),
        "quota_commit": (10, 12),
        "quota_release": (10, 8),
    }

    def __init__(self) -> None:
        super().__init__()
        self.now_ms = 1_000_000
        self.epoch = (1, b"ready")
        self.epoch_exists = True
        self.initialization_exists = True
        self.cas: dict[str, tuple[int, bytes, int]] = {}
        self.cas_capabilities: dict[bytes, bytes] = {}
        self.generations: dict[str, int] = {}
        self.replays: defaultdict[str, dict[bytes, tuple[bytes, list[bytes], int]]] = defaultdict(
            dict
        )
        self.corrupt_replays: set[tuple[str, bytes]] = set()
        self.values: dict[str, tuple[bytes, int | None]] = {}
        self.quota_records: dict[bytes, dict[str, object]] = {}
        self.quota_replays: dict[bytes, tuple[bytes, list[bytes], int, bytes]] = {}
        self.quota_buckets: dict[bytes, dict[int, tuple[int, int, int]]] = {}
        self.quota_schema: dict[bytes, tuple[int, int, str]] = {}
        self.quota_schema_expiring: set[bytes] = set()
        self.quota_record_inspections = 0
        self.rate_bucket_inspections = 0
        self.redis_hashes: dict[str, dict[bytes, bytes]] = {}
        self.redis_zsets: dict[str, dict[bytes, int]] = {}
        self.corrupt_quota_pairs = False
        self.cancel_after_response_boundary: set[str] = set()

    def register_script(self, source: str) -> StatefulRegisteredScript:
        script = StatefulRegisteredScript(self, source)
        self.registered[script.name] = script  # type: ignore[assignment]
        return script

    def pipeline(self, *, transaction: bool) -> _StatefulPipeline:
        assert transaction
        return _StatefulPipeline(self)

    def advance(self, milliseconds: int) -> None:
        self.now_ms += milliseconds

    def seed_retained_record(
        self, *, key_id: bytes, reservation_id: bytes, retained_for_ms: int = 120_000
    ) -> None:
        self.quota_schema[key_id] = (2, self.epoch[0], "ready")
        self.quota_records[reservation_id] = {
            "key": key_id,
            "fingerprint": b"a" * 64,
            "state": "released",
            "created_at": self.now_ms - 61_000,
            "active_until": self.now_ms - 1,
            "retained_until": self.now_ms + retained_for_ms,
            "tokens": 0,
            "rpm": None,
            "tpm": None,
            "retention": retained_for_ms,
        }

    def _expired(self, expires_at: int | None) -> bool:
        return expires_at is not None and expires_at <= self.now_ms

    def _replay(self, name: str, operation_id: bytes, fingerprint: bytes) -> list[bytes] | None:
        if (name, operation_id) in self.corrupt_replays:
            raise RuntimeError("COORDINATION_CORRUPT")
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
            if name == "cas":
                self.cas_capabilities.pop(identifier, None)
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
        if name == "scan":
            cursor = int(args[0])
            pattern = kwargs.get("match")
            assert isinstance(pattern, str) and pattern.endswith("*")
            prefix = pattern[:-1]
            keys = sorted(
                key.encode("ascii")
                for key in {*self.redis_hashes, *self.redis_zsets, *self.values}
                if key.startswith(prefix)
                and (
                    bool(self.redis_hashes.get(key))
                    or bool(self.redis_zsets.get(key))
                    or key in self.values
                )
            )
            count = int(kwargs.get("count", 10))
            selected = keys[cursor : cursor + count]
            next_cursor = 0 if cursor + count >= len(keys) else cursor + count
            return next_cursor, selected
        if name == "hlen":
            return len(self.redis_hashes.get(str(args[0]), {}))
        if name == "zcard":
            return len(self.redis_zsets.get(str(args[0]), {}))
        if name == "zrange":
            key, start, end = str(args[0]), int(args[1]), int(args[2])
            ordered = sorted(
                self.redis_zsets.get(key, {}).items(), key=lambda item: (item[1], item[0])
            )
            selected = ordered[start : end + 1]
            return [(member, float(score)) for member, score in selected]
        if name == "hget":
            return self.redis_hashes.get(str(args[0]), {}).get(args[1])
        if name == "time":
            return self.now_ms // 1000, self.now_ms % 1000 * 1000
        key = args[0]
        assert isinstance(key, str)
        stored = self.values.get(key)
        if stored is not None and self._expired(stored[1]):
            del self.values[key]
            stored = None
        if name == "get":
            return None if stored is None else stored[0]
        if name == "pttl":
            if stored is None:
                return -2
            return -1 if stored[1] is None else stored[1] - self.now_ms
        if name == "delete":
            removed = int(
                self.values.pop(key, None) is not None
                or self.redis_hashes.pop(key, None) is not None
                or self.redis_zsets.pop(key, None) is not None
            )
            return removed
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
            if self.epoch_exists != self.initialization_exists:
                raise RuntimeError("COORDINATION_CORRUPT")
            if not self.epoch_exists:
                self.epoch = (1, b"ready")
                self.epoch_exists = True
                self.initialization_exists = True
            return [b"1", b"ok", str(self.epoch[0]).encode(), self.epoch[1]]
        if name == "time_read":
            if not self.epoch_exists or not self.initialization_exists:
                raise RuntimeError("COORDINATION_CORRUPT")
            if self.epoch != (int(byte_args[0]), b"ready"):
                return [b"1", b"unavailable", b""]
            return [b"1", b"ok", str(self.now_ms).encode()]
        if name in {
            "epoch_advance",
            "epoch_ready",
            "cas",
            "cas_read",
            "invalidation",
            "invalidation_read",
            "quota_reserve",
            "quota_commit",
            "quota_release",
        } and (not self.epoch_exists or not self.initialization_exists):
            raise RuntimeError("COORDINATION_CORRUPT")
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
            expected, payload, ttl, epoch, operation_id, fingerprint, limit, capabilities = (
                byte_args
            )
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
                self.cas_capabilities[operation_id] = capabilities
            else:
                self.cas_capabilities[operation_id] = b""
            return result
        if name == "cas_read":
            epoch = int(byte_args[0])
            if self.epoch != (epoch, b"ready"):
                return [b"1", b"unavailable", b"", b""]
            record = self.cas.get(keys[0])
            if record is not None and record[2] <= self.now_ms:
                del self.cas[keys[0]]
                record = None
            if record is None:
                return [b"1", b"not_found", b"", b""]
            return [b"1", b"found", str(record[0]).encode(), record[1]]
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
        if name.startswith("quota_"):
            return self._run_quota_script(name, byte_args, keys)
        assert name == "lock_release"
        stored = self.values.get(keys[0])
        deleted = stored is not None and not self._expired(stored[1]) and stored[0] == byte_args[0]
        if deleted:
            del self.values[keys[0]]
        return [b"1", b"ok", b"1" if deleted else b"0"]

    def _quota_prune(self, key_id: bytes) -> bool:
        due_records = [
            reservation_id
            for reservation_id, record in self.quota_records.items()
            if record["key"] == key_id and int(record["retained_until"]) <= self.now_ms
        ]
        due_replays = [
            operation_id
            for operation_id, (
                _fingerprint,
                _result,
                expiry,
                replay_key,
            ) in self.quota_replays.items()
            if replay_key == key_id and expiry <= self.now_ms
        ]
        if len(due_records) + len(due_replays) > 256:
            return False
        for reservation_id in due_records:
            del self.quota_records[reservation_id]
        for operation_id in due_replays:
            del self.quota_replays[operation_id]
        return True

    def _quota_replay(
        self, operation_id: bytes, fingerprint: bytes
    ) -> tuple[list[bytes] | None, bytes | None]:
        if self.corrupt_quota_pairs:
            raise RuntimeError("COORDINATION_CORRUPT")
        saved = self.quota_replays.get(operation_id)
        if saved is None:
            return None, None
        saved_fingerprint, result, expiry, key_id = saved
        if expiry <= self.now_ms:
            return None, key_id
        if saved_fingerprint != fingerprint:
            return None, key_id
        replay = list(result)
        replay[-1] = b"1"
        return replay, key_id

    def _quota_locator(self, key: str, field_count: int) -> list[bytes] | None:
        stored = self.values.get(key)
        if stored is None or self._expired(stored[1]):
            self.values.pop(key, None)
            return None
        if stored[1] is None:
            raise RuntimeError("COORDINATION_CORRUPT")
        fields = stored[0].split(b"|")
        invalid_hex = any(value not in b"0123456789abcdef" for value in fields[1])
        fingerprint_invalid = field_count == 3 and (
            len(fields[2]) != 64 or any(value not in b"0123456789abcdef" for value in fields[2])
        )
        if (
            len(fields) != field_count
            or fields[0] != b"2"
            or len(fields[1]) != 64
            or invalid_hex
            or fingerprint_invalid
        ):
            raise RuntimeError("COORDINATION_CORRUPT")
        return fields

    def _quota_locators_match(self, keys: list[str], target_key: bytes, fingerprint: bytes) -> bool:
        reservation = self._quota_locator(keys[5], 2)
        operation = self._quota_locator(keys[6], 3)
        if reservation is not None and reservation[1] != target_key:
            return False
        return operation is None or (operation[1] == target_key and operation[2] == fingerprint)

    def _remember_quota(
        self,
        operation_id: bytes,
        fingerprint: bytes,
        result: list[bytes],
        expiry: int,
        key_id: bytes,
        limit: int,
    ) -> bool:
        if (
            sum(
                1
                for _fp, _result, _expiry, replay_key in self.quota_replays.values()
                if replay_key == key_id
            )
            >= limit
        ):
            return False
        self.quota_replays[operation_id] = (fingerprint, result, expiry, key_id)
        return True

    def _quota_active(self, key_id: bytes) -> list[dict[str, object]]:
        return [
            record
            for record in self.quota_records.values()
            if record["key"] == key_id
            and record["state"] == "active"
            and int(record["active_until"]) > self.now_ms
        ]

    def _quota_committed(self, key_id: bytes) -> list[dict[str, object]]:
        return [
            record
            for record in self.quota_records.values()
            if record["key"] == key_id and record["state"] == "committed"
        ]

    @staticmethod
    def _as_float(value: bytes) -> float:
        return float(value.decode("ascii"))

    def _quota_schema_status(self, key_id: bytes, keys: list[str], epoch: int) -> str:
        marker = self.quota_schema.get(key_id)
        if marker is None:
            nonempty = bool(
                any(record["key"] == key_id for record in self.quota_records.values())
                or any(replay[3] == key_id for replay in self.quota_replays.values())
                or self.quota_buckets.get(key_id)
                or self.values.get(keys[5])
                or self.values.get(keys[6])
            )
            return "reconciliation_required" if nonempty else "initialize"
        if key_id in self.quota_schema_expiring:
            raise RuntimeError("COORDINATION_CORRUPT")
        if (
            not isinstance(marker, tuple)
            or len(marker) != 3
            or not isinstance(marker[0], int)
            or not isinstance(marker[1], int)
            or not isinstance(marker[2], str)
        ):
            raise RuntimeError("COORDINATION_CORRUPT")
        version, marker_epoch, state = marker
        if version == 1 or marker_epoch != epoch:
            return "reconciliation_required"
        if version != 2 or state != "ready":
            raise RuntimeError("COORDINATION_CORRUPT")
        return "ready"

    def _quota_bucket_totals(
        self, key_id: bytes, buckets: dict[int, tuple[int, int, int]] | None = None
    ) -> tuple[int, int, int | None]:
        state = self.quota_buckets.get(key_id, {}) if buckets is None else buckets
        if len(state) > 61:
            raise RuntimeError("COORDINATION_CORRUPT")
        current = self.now_ms // 1000
        requests = tokens = 0
        earliest: int | None = None
        for slot in range(61):
            self.rate_bucket_inspections += 1
            bucket = state.get(slot)
            if bucket is None:
                continue
            second, bucket_requests, bucket_tokens = bucket
            if (
                second % 61 != slot
                or second > current
                or not 0 <= bucket_requests <= 2**63 - 1
                or not 0 <= bucket_tokens <= 2**63 - 1
            ):
                raise RuntimeError("COORDINATION_CORRUPT")
            if second >= current - 60:
                requests += bucket_requests
                tokens += bucket_tokens
                if requests > 2**63 - 1 or tokens > 2**63 - 1:
                    raise RuntimeError("COORDINATION_CORRUPT")
                if bucket_requests or bucket_tokens:
                    earliest = second if earliest is None else min(earliest, second)
        return requests, tokens, earliest

    @staticmethod
    def _quota_adjust_bucket(
        buckets: dict[int, tuple[int, int, int]],
        second: int,
        request_delta: int,
        token_delta: int,
    ) -> None:
        slot = second % 61
        bucket = buckets.get(slot)
        if bucket is None or bucket[0] != second:
            if request_delta < 0 or token_delta < 0:
                raise RuntimeError("COORDINATION_CORRUPT")
            bucket = (second, 0, 0)
        requests, tokens = bucket[1] + request_delta, bucket[2] + token_delta
        if not 0 <= requests <= 2**63 - 1 or not 0 <= tokens <= 2**63 - 1:
            raise RuntimeError("COORDINATION_CORRUPT")
        buckets[slot] = (second, requests, tokens)

    def bucket_totals(self, key_id: bytes) -> tuple[int, int]:
        requests, tokens, _ = self._quota_bucket_totals(key_id)
        return requests, tokens

    def _run_quota_script(self, name: str, args: list[bytes], keys: list[str]) -> list[bytes]:
        epoch = int(args[0])
        if self.epoch != (epoch, b"ready"):
            if name == "quota_reserve":
                return [
                    b"1",
                    b"denied",
                    args[1],
                    b"reconciling" if self.epoch[1] == b"reconciling" else b"stale_epoch",
                    b"0",
                    b"0",
                ]
            return (
                [b"1", b"not_committed", b"0", b"0"]
                if name == "quota_commit"
                else [b"1", b"ok", b"0", b"0"]
            )
        key_id = args[2] if name == "quota_reserve" else args[4]
        schema_status = self._quota_schema_status(key_id, keys, epoch)
        if schema_status == "reconciliation_required":
            if name == "quota_reserve":
                return [b"1", b"denied", args[1], b"reconciliation_required", b"0", b"0"]
            return [b"1", b"reconciliation_required", b"0", b"0"]
        if name == "quota_reserve":
            reservation_id, fingerprint, operation_id = args[1], args[3], args[4]
            if not self._quota_locators_match(keys, key_id, fingerprint):
                return [b"1", b"denied", reservation_id, b"conflict", b"0", b"0"]
            ttl, retention, record_limit, replay_limit = map(int, args[5:9])
            tokens = int(args[10])
            rpm = None if args[12] == b"" else int(args[12])
            tpm = None if args[13] == b"" else int(args[13])
            if not self._quota_prune(key_id):
                return [b"1", b"denied", reservation_id, b"reconciliation_required", b"0", b"0"]
            replay, replay_key = self._quota_replay(operation_id, fingerprint)
            if replay is not None:
                return replay
            if replay_key is not None:
                return [b"1", b"denied", reservation_id, b"conflict", b"0", b"0"]
            self.quota_record_inspections += 1
            record = self.quota_records.get(reservation_id)
            if record is not None:
                if record["key"] != key_id:
                    raise RuntimeError("COORDINATION_CORRUPT")
                if record["fingerprint"] == fingerprint:
                    return [b"1", b"accepted", reservation_id, b"", b"0", b"1"]
                return [b"1", b"denied", reservation_id, b"conflict", b"0", b"0"]
            candidate = dict(self.quota_buckets.get(key_id, {}))
            rate_requests, rate_tokens, earliest = self._quota_bucket_totals(key_id, candidate)
            record_count = sum(1 for item in self.quota_records.values() if item["key"] == key_id)
            retry = (
                max(1, ((earliest + 61) * 1000 - self.now_ms + 999) // 1000)
                if earliest is not None
                else 1
            )
            if record_count >= record_limit:
                result = [b"1", b"denied", reservation_id, b"capacity", b"0", b"0"]
            elif rpm is not None and rate_requests >= rpm:
                result = [b"1", b"denied", reservation_id, b"rpm", str(retry).encode(), b"0"]
            elif tpm is not None and rate_tokens + tokens > tpm:
                result = [b"1", b"denied", reservation_id, b"tpm", str(retry).encode(), b"0"]
            elif rate_tokens + tokens > 2**63 - 1:
                raise RuntimeError("COORDINATION_CORRUPT")
            else:
                self._quota_adjust_bucket(candidate, self.now_ms // 1000, 1, tokens)
                result = [b"1", b"accepted", reservation_id, b"", b"0", b"0"]
            expiry = self.now_ms + (retention if result[1] == b"accepted" else ttl)
            if not self._remember_quota(
                operation_id, fingerprint, result, expiry, key_id, replay_limit
            ):
                return [b"1", b"denied", reservation_id, b"reconciliation_required", b"0", b"0"]
            self.quota_schema[key_id] = (2, epoch, "ready")
            if result[1] == b"accepted":
                self.quota_buckets[key_id] = candidate
                self.quota_records[reservation_id] = {
                    "key": key_id,
                    "fingerprint": fingerprint,
                    "state": "active",
                    "created_at": self.now_ms,
                    "active_until": self.now_ms + ttl,
                    "retained_until": expiry,
                    "tokens": tokens,
                    "rpm": rpm,
                    "tpm": tpm,
                    "retention": retention,
                }
                self.values[keys[5]] = (b"2|" + key_id, expiry)
            self.values[keys[6]] = (b"2|" + key_id + b"|" + fingerprint, expiry)
            return result

        fingerprint, operation_id, reservation_id = args[1:4]
        if not self._quota_locators_match(keys, key_id, fingerprint):
            return (
                [b"1", b"not_committed", b"0", b"0"]
                if name == "quota_commit"
                else [b"1", b"ok", b"0", b"0"]
            )
        record_limit = int(args[9] if name == "quota_commit" else args[6])
        replay_limit = int(args[10] if name == "quota_commit" else args[7])
        unknown_retention = int(args[11] if name == "quota_commit" else args[5])
        if not self._quota_prune(key_id):
            return [b"1", b"reconciliation_required", b"0", b"0"]
        replay, replay_key = self._quota_replay(operation_id, fingerprint)
        if replay is not None:
            return replay if name == "quota_commit" else [b"1", b"ok", b"0", b"1"]
        if replay_key is not None:
            return (
                [b"1", b"not_committed", b"0", b"0"]
                if name == "quota_commit"
                else [b"1", b"ok", b"0", b"0"]
            )
        self.quota_record_inspections += 1
        record = self.quota_records.get(reservation_id)
        if record is not None and record["key"] != key_id:
            raise RuntimeError("COORDINATION_CORRUPT")
        if self._quota_locator(keys[5], 2) is not None and record is None:
            raise RuntimeError("COORDINATION_CORRUPT")
        if getattr(self, "admission_fenced", False) and record is None:
            return (
                [b"1", b"not_committed", b"0", b"0"]
                if name == "quota_commit"
                else [b"1", b"ok", b"0", b"0"]
            )
        candidate = dict(self.quota_buckets.get(key_id, {}))
        active = bool(
            record is not None
            and record["state"] == "active"
            and int(record["active_until"]) > self.now_ms
        )
        expiry = (
            int(record["retained_until"]) if record is not None else self.now_ms + unknown_retention
        )
        if name == "quota_commit":
            actual_tokens = (
                int(record["tokens"]) if args[6] == b"" and record else int(args[6] or b"0")
            )
            overspent = False
            if active and record is not None:
                accepted_second = int(record["created_at"]) // 1000
                if accepted_second >= self.now_ms // 1000 - 60:
                    self._quota_adjust_bucket(
                        candidate, accepted_second, -1, -int(record["tokens"])
                    )
                self._quota_adjust_bucket(candidate, self.now_ms // 1000, 1, actual_tokens)
                _, rate_tokens, _ = self._quota_bucket_totals(key_id, candidate)
                overspent = record["tpm"] is not None and rate_tokens > int(record["tpm"])
                expiry = max(int(record["active_until"]), self.now_ms + 61_000)
            result = [
                b"1",
                b"committed" if active else b"not_committed",
                b"1" if overspent else b"0",
                b"0",
            ]
        else:
            if active and record is not None:
                accepted_second = int(record["created_at"]) // 1000
                if accepted_second >= self.now_ms // 1000 - 60:
                    self._quota_adjust_bucket(
                        candidate, accepted_second, -1, -int(record["tokens"])
                    )
            result = [b"1", b"ok", b"1" if active else b"0", b"0"]
        if not self._remember_quota(
            operation_id, fingerprint, result, expiry, key_id, replay_limit
        ):
            return [b"1", b"reconciliation_required", b"0", b"0"]
        self.quota_schema[key_id] = (2, epoch, "ready")
        if active and record is not None:
            self.quota_buckets[key_id] = candidate
            record["state"] = "committed" if name == "quota_commit" else "released"
            record["retained_until"] = expiry
            if name == "quota_commit":
                record["committed_at"] = self.now_ms
                record["actual_tokens"] = actual_tokens
            self.values[keys[5]] = (b"2|" + key_id, expiry)
        self.values[keys[6]] = (b"2|" + key_id + b"|" + fingerprint, expiry)
        return result

    def _run_quota_script_v1_reference(
        self, name: str, args: list[bytes], keys: list[str]
    ) -> list[bytes]:
        epoch = int(args[0])
        if self.epoch != (epoch, b"ready"):
            if name == "quota_reserve":
                return [
                    b"1",
                    b"denied",
                    args[1],
                    b"reconciling" if self.epoch[1] == b"reconciling" else b"stale_epoch",
                    b"0",
                    b"0",
                ]
            return (
                [b"1", b"not_committed", b"0", b"0"]
                if name == "quota_commit"
                else [b"1", b"ok", b"0", b"0"]
            )
        if name == "quota_reserve":
            reservation_id, key_id, fingerprint, operation_id = args[1:5]
            if not self._quota_locators_match(keys, key_id, fingerprint):
                return [b"1", b"denied", reservation_id, b"conflict", b"0", b"0"]
            ttl, retention, record_limit, replay_limit = map(int, args[5:9])
            request_now = self._as_float(args[9])
            tokens, cost = int(args[10]), self._as_float(args[11])
            rpm = None if args[12] == b"" else int(args[12])
            tpm = None if args[13] == b"" else int(args[13])
            daily_budget = None if args[14] == b"" else self._as_float(args[14])
            monthly_budget = None if args[15] == b"" else self._as_float(args[15])
            daily_spend, monthly_spend = self._as_float(args[16]), self._as_float(args[17])
            daily_snapshot, monthly_snapshot = self._as_float(args[18]), self._as_float(args[19])
            if not self._quota_prune(key_id):
                return [b"1", b"denied", reservation_id, b"reconciliation_required", b"0", b"0"]
            replay, replay_key = self._quota_replay(operation_id, fingerprint)
            if replay is not None:
                return replay
            if replay_key is not None:
                return [b"1", b"denied", reservation_id, b"conflict", b"0", b"0"]
            record = self.quota_records.get(reservation_id)
            if record is not None:
                if record["fingerprint"] == fingerprint:
                    return [b"1", b"accepted", reservation_id, b"", b"0", b"1"]
                return [b"1", b"denied", reservation_id, b"conflict", b"0", b"0"]
            if (
                sum(1 for item in self.quota_records.values() if item["key"] == key_id)
                >= record_limit
            ):
                result = [b"1", b"denied", reservation_id, b"capacity", b"0", b"0"]
            else:
                active, committed = self._quota_active(key_id), self._quota_committed(key_id)
                for item in committed:
                    if bool(item["durable"]) and daily_snapshot >= float(item["commit_business"]):
                        item["daily_reconciled"] = True
                    if bool(item["durable"]) and monthly_snapshot >= float(item["commit_business"]):
                        item["monthly_reconciled"] = True
                cutoff = self.now_ms - 60_000
                rate_items = [item for item in active if int(item["created_at"]) > cutoff] + [
                    item for item in committed if int(item["committed_at"]) > cutoff
                ]
                timestamps = [
                    int(item["created_at"]) for item in active if int(item["created_at"]) > cutoff
                ] + [
                    int(item["committed_at"])
                    for item in committed
                    if int(item["committed_at"]) > cutoff
                ]
                retry = (
                    max(1, (min(timestamps) + 60_000 - self.now_ms + 999) // 1000)
                    if timestamps
                    else 1
                )
                if rpm is not None and len(rate_items) >= rpm:
                    result = [b"1", b"denied", reservation_id, b"rpm", str(retry).encode(), b"0"]
                elif (
                    tpm is not None
                    and sum(
                        int(item["tokens"])
                        if item["state"] == "active"
                        else int(item["actual_tokens"])
                        for item in rate_items
                    )
                    + tokens
                    > tpm
                ):
                    result = [b"1", b"denied", reservation_id, b"tpm", str(retry).encode(), b"0"]
                elif (
                    daily_budget is not None
                    and daily_spend
                    + sum(float(item["cost"]) for item in active)
                    + sum(
                        float(item["actual_cost"])
                        for item in committed
                        if not bool(item["daily_reconciled"])
                    )
                    + cost
                    > daily_budget
                ):
                    result = [b"1", b"denied", reservation_id, b"daily_budget", b"0", b"0"]
                elif (
                    monthly_budget is not None
                    and monthly_spend
                    + sum(float(item["cost"]) for item in active)
                    + sum(
                        float(item["actual_cost"])
                        for item in committed
                        if not bool(item["monthly_reconciled"])
                    )
                    + cost
                    > monthly_budget
                ):
                    result = [b"1", b"denied", reservation_id, b"monthly_budget", b"0", b"0"]
                else:
                    self.quota_records[reservation_id] = {
                        "key": key_id,
                        "fingerprint": fingerprint,
                        "state": "active",
                        "created_at": self.now_ms,
                        "active_until": self.now_ms + ttl,
                        "retained_until": self.now_ms + retention,
                        "tokens": tokens,
                        "cost": cost,
                        "rpm": rpm,
                        "tpm": tpm,
                        "daily_budget": daily_budget,
                        "monthly_budget": monthly_budget,
                        "daily_spend": daily_spend,
                        "monthly_spend": monthly_spend,
                        "retention": retention,
                    }
                    self.values[keys[5]] = (b"2|" + key_id, self.now_ms + retention)
                    result = [b"1", b"accepted", reservation_id, b"", b"0", b"0"]
            expiry = (
                self.now_ms + ttl
                if result[1] == b"denied"
                else int(self.quota_records[reservation_id]["retained_until"])
            )
            if not self._remember_quota(
                operation_id, fingerprint, result, expiry, key_id, replay_limit
            ):
                return [b"1", b"denied", reservation_id, b"reconciliation_required", b"0", b"0"]
            self.values[keys[6]] = (
                b"2|" + key_id + b"|" + fingerprint,
                expiry,
            )
            return result
        if name == "quota_commit":
            fingerprint, operation_id, reservation_id, target_key = args[1:5]
            if not self._quota_locators_match(keys, target_key, fingerprint):
                return [b"1", b"not_committed", b"0", b"0"]
            request_now = self._as_float(args[5])
            actual_tokens = None if args[6] == b"" else int(args[6])
            actual_cost = None if args[7] == b"" else self._as_float(args[7])
            durable = args[8] == b"1"
            replay_limit, unknown_retention = int(args[10]), int(args[11])
            key_id = target_key
            record = self.quota_records.get(reservation_id)
            if record is not None and record["key"] != key_id:
                record = None
            if self._quota_locator(keys[5], 2) is not None and record is None:
                raise RuntimeError("COORDINATION_CORRUPT")
            if not self._quota_prune(key_id):
                return [b"1", b"reconciliation_required", b"0", b"0"]
            replay, replay_key = self._quota_replay(operation_id, fingerprint)
            if replay is not None:
                return replay
            if replay_key is not None:
                return [b"1", b"not_committed", b"0", b"0"]
            if (
                record is None
                or record["state"] != "active"
                or int(record["active_until"]) <= self.now_ms
            ):
                result = [b"1", b"not_committed", b"0", b"0"]
                self._remember_quota(
                    operation_id,
                    fingerprint,
                    result,
                    self.now_ms + unknown_retention,
                    key_id,
                    replay_limit,
                )
                self.values[keys[6]] = (
                    b"2|" + key_id + b"|" + fingerprint,
                    self.now_ms + unknown_retention,
                )
                return result
            record["state"] = "committed"
            record["committed_at"] = self.now_ms
            record["commit_business"] = request_now
            record["actual_tokens"] = (
                int(record["tokens"]) if actual_tokens is None else actual_tokens
            )
            record["actual_cost"] = float(record["cost"]) if actual_cost is None else actual_cost
            record["durable"] = durable
            record["daily_reconciled"] = record["daily_budget"] is None
            record["monthly_reconciled"] = record["monthly_budget"] is None
            evidence_retention = 60_000
            if record["daily_budget"] is not None:
                evidence_retention = max(evidence_retention, 86_400_000)
            if record["monthly_budget"] is not None:
                evidence_retention = max(evidence_retention, 30 * 86_400_000)
            record["retained_until"] = self.now_ms + evidence_retention
            active, committed = self._quota_active(key_id), self._quota_committed(key_id)
            cutoff = self.now_ms - 60_000
            overspent = (
                (
                    record.get("tpm") is not None
                    and sum(
                        int(item["tokens"]) for item in active if int(item["created_at"]) > cutoff
                    )
                    + sum(
                        int(item["actual_tokens"])
                        for item in committed
                        if int(item["committed_at"]) > cutoff
                    )
                    > int(record["tpm"])
                )
                or (
                    record["daily_budget"] is not None
                    and float(record["daily_spend"])
                    + sum(float(item["cost"]) for item in active)
                    + sum(
                        float(item["actual_cost"])
                        for item in committed
                        if not bool(item["daily_reconciled"])
                    )
                    > float(record["daily_budget"])
                )
                or (
                    record["monthly_budget"] is not None
                    and float(record["monthly_spend"])
                    + sum(float(item["cost"]) for item in active)
                    + sum(
                        float(item["actual_cost"])
                        for item in committed
                        if not bool(item["monthly_reconciled"])
                    )
                    > float(record["monthly_budget"])
                )
            )
            result = [b"1", b"committed", b"1" if overspent else b"0", b"0"]
            self._remember_quota(
                operation_id,
                fingerprint,
                result,
                int(record["retained_until"]),
                key_id,
                replay_limit,
            )
            self.values[keys[5]] = (b"2|" + key_id, int(record["retained_until"]))
            self.values[keys[6]] = (
                b"2|" + key_id + b"|" + fingerprint,
                int(record["retained_until"]),
            )
            return result
        fingerprint, operation_id, reservation_id, target_key, retention, _, replay_limit = args[1:]
        if not self._quota_locators_match(keys, target_key, fingerprint):
            return [b"1", b"ok", b"0", b"0"]
        record = self.quota_records.get(reservation_id)
        key_id = target_key
        if record is not None and record["key"] != key_id:
            record = None
        if self._quota_locator(keys[5], 2) is not None and record is None:
            raise RuntimeError("COORDINATION_CORRUPT")
        if not self._quota_prune(key_id):
            return [b"1", b"reconciliation_required", b"0", b"0"]
        replay, replay_key = self._quota_replay(operation_id, fingerprint)
        if replay is not None:
            return [b"1", b"ok", b"0", b"1"]
        if replay_key is not None:
            return [b"1", b"ok", b"0", b"0"]
        released = (
            record is not None
            and record["state"] == "active"
            and int(record["active_until"]) > self.now_ms
        )
        if released:
            record["state"] = "released"
        expiry = (
            int(record["retained_until"]) if record is not None else self.now_ms + int(retention)
        )
        result = [b"1", b"ok", b"1" if released else b"0", b"0"]
        self._remember_quota(operation_id, fingerprint, result, expiry, key_id, int(replay_limit))
        self.values[keys[6]] = (b"2|" + key_id + b"|" + fingerprint, expiry)
        return result


class RedisAdmissionFenceTests(CoordinationStoreContract, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        from tests.test_security_coordination_redis import StatefulSecurityRedisClient

        self.client = StatefulSecurityRedisClient()
        self.namespace = "production-east"
        self.store = RedisStateStore(
            "redis://redis/0",
            self.namespace,
            _redis_module_for_testing=FakeRedisModule(self.client),
        )

    async def test_admission_fence_all_families(self) -> None:
        await self.assert_admission_fence_contract()

    async def test_admission_fence_linearization_and_settlement(self) -> None:
        await self.assert_fence_linearization_and_settlement_contract()

    async def test_cas_settlement_requires_accepted_proof(self) -> None:
        await self.assert_cas_settlement_proof_contract()

    async def test_cas_settlement_proof_rejects_cross_key_and_wrong_transition_reuse(
        self,
    ) -> None:
        await self.assert_cas_settlement_proof_cannot_be_reused_for_other_work()

    async def test_unknown_settlement_does_not_admit_replays(self) -> None:
        async def retained_count() -> int:
            return len(self.client.quota_replays) + len(self.client.oidc_replays)

        await self.assert_unknown_settlement_does_not_admit_replays(retained_count)

    async def test_batch_settlement_during_drain(self) -> None:
        await self.assert_batch_settlement_during_drain_contract()

    async def test_batch_partial_settlement_retry(self) -> None:
        await self.assert_batch_partial_settlement_retry_contract()

    async def test_settlement_replay_outlives_its_admission_proof(self) -> None:
        async def advance(seconds: float) -> None:
            self.client.advance(int(seconds * 1_000))

        await self.assert_settlement_replay_after_proof_expiry(advance)

    async def test_corrupt_fence_blocks_settlement(self) -> None:
        await self.assert_corrupt_fence_blocks_settlement_contract()

    async def test_ambiguous_fence_json_blocks_settlement(self) -> None:
        await self.assert_ambiguous_fence_json_blocks_settlement()

    async def test_drain_completion_identity(self) -> None:
        await self.assert_drain_completion_identity_contract()

    async def test_admission_scripts_receive_fence_and_binding_in_same_slot(self) -> None:
        await self.store.reserve_quota(
            self._quota_request("fenced-script", key_id="fenced-key", operation_id="fenced-script")
        )
        _, keys, _ = self.client.script_calls[-1]
        self.assertIn(self.store._key("generic", "ha-runtime-drain-v1"), keys)
        self.assertIn(self.store._key("generic", "ha-runtime-binding-v1"), keys)
        self.assertEqual(len({key.split("{")[1].split("}")[0] for key in keys}), 1)
        for name in (
            "cas",
            "invalidation",
            "quota_reserve",
            "security_session_issue",
            "security_session_resolve",
            "security_session_rotate",
            "security_session_revoke",
            "security_attempt_reserve",
            "security_attempt_clear",
            "oidc_transaction_create",
        ):
            with self.subTest(script=name):
                self.assertIn("COORDINATION_ADMISSION_FENCED", SCRIPT_SOURCES[name])


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

    @staticmethod
    def _legacy_terminal_record(key_digest: bytes, *, retained_until: int) -> bytes:
        accepted_at = retained_until - 120_000
        active_until = accepted_at + 61_000
        return "|".join(
            (
                "1",
                "a" * 64,
                key_digest.decode("ascii"),
                "released",
                str(active_until),
                str(retained_until),
                str(accepted_at),
                "5",
                "0",
                "0",
                "0",
                "0",
                "0",
                "1",
                "1",
                "0",
                "10",
                "100",
                "n",
                "n",
                "0",
                "0",
                "120000",
                str(retained_until),
            )
        ).encode("ascii")

    @staticmethod
    def _legacy_committed_record(key_digest: bytes, *, now_ms: int) -> tuple[bytes, int]:
        accepted_at = now_ms - 100_000
        active_until = accepted_at + 900_000
        committed_at = accepted_at + 50_000
        retained_until = committed_at + 60_000
        return (
            "|".join(
                (
                    "1",
                    "a" * 64,
                    key_digest.decode("ascii"),
                    "committed",
                    str(active_until),
                    str(retained_until),
                    str(accepted_at),
                    "5",
                    "0",
                    str(committed_at),
                    "5",
                    "0",
                    "1",
                    "1",
                    "1",
                    "0",
                    "10",
                    "100",
                    "n",
                    "n",
                    "0",
                    "0",
                    "900000",
                    str(retained_until),
                )
            ).encode("ascii"),
            retained_until,
        )

    async def test_quota_reconciliation_disposes_v1_state_in_bounded_pages(self) -> None:
        client = StatefulRedisClient()
        client.epoch = (2, b"reconciling")
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-migration",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        key_digest = b"d" * 64
        records_key = store._quota_bucket_key("quota:records", key_digest)
        lifecycle_key = store._quota_bucket_key("quota:lifecycle", key_digest)
        replay_key = store._quota_bucket_key("quota:replay", key_digest)
        replay_expiry_key = store._quota_bucket_key("quota:replay-expiry", key_digest)
        marker_key = store._quota_bucket_key("quota:state-schema", key_digest)
        bucket_key = store._quota_bucket_key("quota:rate-buckets", key_digest)
        reservation = b"legacy-reservation"
        operation = b"release:legacy-operation"
        expiry = client.now_ms + 50_000
        client.redis_hashes[records_key] = {
            reservation: self._legacy_terminal_record(key_digest, retained_until=expiry)
        }
        client.redis_zsets[lifecycle_key] = {reservation: expiry}
        client.redis_hashes[replay_key] = {
            operation: b"1|" + (b"b" * 64) + b"|1|" + str(expiry).encode("ascii")
        }
        client.redis_zsets[replay_expiry_key] = {operation: expiry}
        client.redis_hashes[bucket_key] = {b"0": b"old"}
        client.values[marker_key] = (b"1|1|ready", None)
        client.values[store._key("quota:locator", reservation.decode("ascii"))] = (
            b"1|" + key_digest,
            expiry,
        )
        client.values[store._key("quota:operation", operation.decode("ascii"))] = (
            b"1|" + key_digest + b"|" + (b"b" * 64),
            expiry,
        )

        cursor = None
        pages = 0
        while True:
            page = await store.reconcile_quota_state(epoch=2, cursor=cursor, limit=1, apply=True)
            self.assertLessEqual(page.scanned, 1)
            pages += 1
            if page.complete:
                break
            cursor = page.cursor
            self.assertLess(pages, 20)

        self.assertGreater(pages, 2)
        self.assertEqual(client.redis_hashes.get(records_key, {}), {})
        self.assertEqual(client.redis_hashes.get(replay_key, {}), {})
        self.assertNotIn(bucket_key, client.redis_hashes)
        self.assertEqual(client.values[marker_key][0], b"2|2|ready")
        self.assertNotIn(store._key("quota:locator", reservation.decode("ascii")), client.values)
        self.assertNotIn(store._key("quota:operation", operation.decode("ascii")), client.values)

    async def test_quota_reconciliation_migrates_marker_only_state(self) -> None:
        client = StatefulRedisClient()
        client.epoch = (2, b"reconciling")
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="marker-only",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        key_digest = b"e" * 64
        marker_key = store._quota_bucket_key("quota:state-schema", key_digest)
        bucket_key = store._quota_bucket_key("quota:rate-buckets", key_digest)
        client.values[marker_key] = (b"2|1|ready", None)
        client.redis_hashes[bucket_key] = {b"0": b"old"}

        cursor = None
        for _ in range(12):
            page = await store.reconcile_quota_state(epoch=2, cursor=cursor, limit=1, apply=True)
            if page.complete:
                break
            cursor = page.cursor
        else:
            self.fail("Quota schema reconciliation did not complete.")

        self.assertEqual(client.values[marker_key][0], b"2|2|ready")
        self.assertNotIn(bucket_key, client.redis_hashes)

    async def test_quota_reconciliation_dry_run_is_exact_and_non_mutating(self) -> None:
        client = StatefulRedisClient()
        client.epoch = (2, b"reconciling")
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-preview",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        key_digest = b"c" * 64
        records_key = store._quota_bucket_key("quota:records", key_digest)
        lifecycle_key = store._quota_bucket_key("quota:lifecycle", key_digest)
        reservation = b"preview-reservation"
        expiry = client.now_ms + 50_000
        client.redis_hashes[records_key] = {
            reservation: self._legacy_terminal_record(key_digest, retained_until=expiry)
        }
        client.redis_zsets[lifecycle_key] = {reservation: expiry}
        before = copy.deepcopy((client.redis_hashes, client.redis_zsets, client.values))

        first = await store.reconcile_quota_state(epoch=2, cursor=None, limit=1, apply=False)
        replay = await store.reconcile_quota_state(epoch=2, cursor=None, limit=1, apply=False)

        self.assertEqual(first, replay)
        self.assertEqual((client.redis_hashes, client.redis_zsets, client.values), before)

    async def test_quota_reconciliation_accepts_valid_v1_committed_chronology(self) -> None:
        client = StatefulRedisClient()
        client.epoch = (2, b"reconciling")
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-v1-committed",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        key_digest = b"8" * 64
        records_key = store._quota_bucket_key("quota:records", key_digest)
        lifecycle_key = store._quota_bucket_key("quota:lifecycle", key_digest)
        value, expiry = self._legacy_committed_record(key_digest, now_ms=client.now_ms)
        client.redis_hashes[records_key] = {b"committed-reservation": value}
        client.redis_zsets[lifecycle_key] = {b"committed-reservation": expiry}

        page = await store.reconcile_quota_state(epoch=2, cursor=None, limit=1, apply=True)

        self.assertEqual(page.scanned, 1)
        self.assertEqual(client.redis_hashes.get(records_key, {}), {})

    async def test_quota_reconciliation_never_exceeds_256_records(self) -> None:
        client = StatefulRedisClient()
        client.epoch = (2, b"reconciling")
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-page-bound",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        key_digest = b"9" * 64
        records_key = store._quota_bucket_key("quota:records", key_digest)
        lifecycle_key = store._quota_bucket_key("quota:lifecycle", key_digest)
        expiry = client.now_ms + 50_000
        value = self._legacy_terminal_record(key_digest, retained_until=expiry)
        client.redis_hashes[records_key] = {
            f"reservation-{index:04d}".encode("ascii"): value for index in range(257)
        }
        client.redis_zsets[lifecycle_key] = {
            member: expiry for member in client.redis_hashes[records_key]
        }

        first = await store.reconcile_quota_state(epoch=2, cursor=None, limit=256, apply=True)
        second = await store.reconcile_quota_state(
            epoch=2, cursor=first.cursor, limit=256, apply=True
        )

        self.assertEqual(first.scanned, 256)
        self.assertEqual(second.scanned, 1)
        self.assertEqual(client.redis_hashes.get(records_key, {}), {})

    async def test_quota_reconciliation_rejects_active_and_corrupt_state(self) -> None:
        client = StatefulRedisClient()
        client.epoch = (2, b"reconciling")
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-corrupt",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        key_digest = b"f" * 64
        records_key = store._quota_bucket_key("quota:records", key_digest)
        lifecycle_key = store._quota_bucket_key("quota:lifecycle", key_digest)
        reservation = b"active-reservation"
        active_until = client.now_ms + 1_000
        retained_until = client.now_ms + 61_000
        client.redis_hashes[records_key] = {
            reservation: b"|".join(
                (
                    b"2",
                    b"a" * 64,
                    key_digest,
                    b"active",
                    str(active_until).encode("ascii"),
                    str(retained_until).encode("ascii"),
                    str(client.now_ms).encode("ascii"),
                    b"1",
                    b"0",
                    b"0",
                    b"n",
                    b"n",
                    b"61000",
                    str(active_until).encode("ascii"),
                )
            )
        }
        client.redis_zsets[lifecycle_key] = {reservation: active_until}

        with self.assertRaises(CoordinationReconciliationRequiredError):
            await store.reconcile_quota_state(epoch=2, cursor=None, limit=256, apply=True)
        self.assertIn(reservation, client.redis_hashes[records_key])

        client.redis_zsets[lifecycle_key] = {}
        with self.assertRaises(CoordinationCorruptError):
            await store.reconcile_quota_state(epoch=2, cursor=None, limit=256, apply=True)

        client.redis_hashes[records_key] = {reservation: b"malformed"}
        client.redis_zsets[lifecycle_key] = {reservation: active_until}
        with self.assertRaises(CoordinationCorruptError):
            await store.reconcile_quota_state(epoch=2, cursor=None, limit=256, apply=True)
        with self.assertRaises(ValueError):
            await store.reconcile_quota_state(
                epoch=2, cursor="not-a-closed-cursor", limit=256, apply=True
            )

    async def test_quota_reconciliation_rejects_expiring_schema_before_mutation(self) -> None:
        client = StatefulRedisClient()
        client.epoch = (2, b"reconciling")
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-expiring-marker",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        key_digest = b"7" * 64
        records_key = store._quota_bucket_key("quota:records", key_digest)
        lifecycle_key = store._quota_bucket_key("quota:lifecycle", key_digest)
        marker_key = store._quota_bucket_key("quota:state-schema", key_digest)
        reservation = b"retained-reservation"
        expiry = client.now_ms + 50_000
        client.redis_hashes[records_key] = {
            reservation: self._legacy_terminal_record(key_digest, retained_until=expiry)
        }
        client.redis_zsets[lifecycle_key] = {reservation: expiry}
        client.values[marker_key] = (b"1|1|ready", client.now_ms + 30_000)

        with self.assertRaises(CoordinationCorruptError):
            await store.reconcile_quota_state(epoch=2, cursor=None, limit=256, apply=True)

        self.assertIn(reservation, client.redis_hashes[records_key])
        self.assertIn(reservation, client.redis_zsets[lifecycle_key])

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

    async def test_close_waiter_cancellation_does_not_cancel_the_shared_close(self) -> None:
        client = ControlledCloseRedisClient()
        client.script_replies["epoch_read"].append(EPOCH_READY)
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="cancel-close",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        await store.read_epoch()

        cancelled_waiter = asyncio.create_task(store.close())
        await client.close_started.wait()
        with self.assertRaises(CoordinationUnavailableError):
            await store.read_epoch()
        cancelled_waiter.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await cancelled_waiter

        surviving_waiter = asyncio.create_task(store.close())
        client.close_release.set()
        await surviving_waiter
        self.assertEqual(client.aclose_calls, 1)
        self.assertTrue(client.close_completed)
        with self.assertRaises(CoordinationUnavailableError):
            await store.read_epoch()

    async def test_concurrent_close_waiters_share_one_underlying_close(self) -> None:
        client = ControlledCloseRedisClient()
        client.script_replies["epoch_read"].append(EPOCH_READY)
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="concurrent-close",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        await store.read_epoch()

        first = asyncio.create_task(store.close())
        await client.close_started.wait()
        second = asyncio.create_task(store.close())
        await asyncio.sleep(0)
        client.close_release.set()
        await asyncio.gather(first, second)

        self.assertEqual(client.aclose_calls, 1)

    async def test_close_failure_is_shared_and_a_later_attempt_retries_the_same_client(
        self,
    ) -> None:
        client = ControlledCloseRedisClient(RuntimeError("secret close failure"))
        client.script_replies["epoch_read"].append(EPOCH_READY)
        store = RedisStateStore(
            "redis://alice:super-secret@redis.example/0",
            deployment_namespace="retry-close",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        await store.read_epoch()

        first = asyncio.create_task(store.close())
        await client.close_started.wait()
        second = asyncio.create_task(store.close())
        await asyncio.sleep(0)
        client.close_release.set()
        failures = await asyncio.gather(first, second, return_exceptions=True)

        self.assertEqual(client.aclose_calls, 1)
        self.assertTrue(all(isinstance(item, CoordinationUnavailableError) for item in failures))
        self.assertTrue(all("secret" not in str(item) for item in failures))

        client.script_replies["epoch_read"].append(EPOCH_READY)
        self.assertEqual((await store.read_epoch()).epoch, 1)
        client.reset_close_barrier()
        retry = asyncio.create_task(store.close())
        await client.close_started.wait()
        client.close_release.set()
        await retry
        self.assertEqual(client.aclose_calls, 2)

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
        self.assertEqual(len(keys), 4)
        self.assertTrue(keys[-1].endswith(":initialization"))
        self.assertEqual(args[:3], [b"1", b"advance-1", b"2592000000"])
        self.assertEqual(args[-1], b"100000")

    async def test_cas_keys_and_args_are_exact_and_replay_result_is_strict(self) -> None:
        self.queue("cas", [b"1", b"applied", b"7", b"1"])
        request = CasRequest("opaque-key", 6, b"\x00value\xff", 2.5, 3, "cas-op")
        result = await self.store.compare_and_set(request)
        self.assertEqual((result.applied, result.revision, result.idempotent), (True, 7, True))
        name, keys, args = self.client.script_calls[0]
        self.assertEqual((name, len(keys)), ("cas", 7))
        self.assertTrue(keys[4].endswith(":initialization"))
        self.assertEqual(args[:5], [b"6", b"\x00value\xff", b"2500", b"3", b"cas-op"])
        self.assertEqual(len(args[5]), 64)
        self.assertEqual(args[6], b"100000")

    async def test_cas_read_keys_args_and_reply_schema_are_exact(self) -> None:
        self.queue(
            "cas_read",
            [b"1", b"found", b"7", b"\x00value\xff"],
            [b"1", b"not_found", b"", b""],
            [b"1", b"unavailable", b"", b""],
            [b"1", b"found", b"0", b"value"],
        )

        snapshot = await self.store.read_cas("opaque-key", epoch=3)
        missing = await self.store.read_cas("missing-key", epoch=3)
        self.assertEqual((snapshot.revision, snapshot.payload), (7, b"\x00value\xff"))
        self.assertEqual((missing.revision, missing.payload), (None, None))
        name, keys, args = self.client.script_calls[0]
        self.assertEqual((name, len(keys), args), ("cas_read", 3, [b"3"]))
        self.assertTrue(keys[-1].endswith(":initialization"))
        self.assertNotIn("opaque-key", keys[0])

        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_cas("opaque-key", epoch=3)
        with self.assertRaises(CoordinationCorruptError):
            await self.store.read_cas("opaque-key", epoch=3)

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

    async def test_signed_zero_is_canonicalized_at_the_redis_boundary(self) -> None:
        self.queue("quota_reserve", [b"1", b"accepted", b"zero", b"", b"0", b"0"])
        decision = await self.store.reserve_quota(
            QuotaReservationRequest(
                "zero",
                "key",
                -0.0,
                61.0,
                0,
                -0.0,
                None,
                None,
                None,
                None,
                -0.0,
                -0.0,
                -0.0,
                -0.0,
            )
        )

        self.assertTrue(decision.accepted)
        args = self.client.script_calls[-1][2]
        self.assertEqual([args[index] for index in (9, 11, 16, 17, 18, 19)], [b"0"] * 6)

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
        self.assertEqual(len(keys), 7)
        self.assertTrue(keys[4].endswith(":initialization"))
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
        replay = await self.store.compare_and_set(
            CasRequest("key", 0, b"value", 1, 1, "not-applied-replay")
        )
        self.assertEqual((replay.applied, replay.revision, replay.idempotent), (False, None, True))
        with self.assertRaises(CoordinationCorruptError):
            await self.store.compare_and_set(
                CasRequest("key", 0, b"value", 1, 1, "missing-revision")
            )

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

        self.queue("quota_release", [b"1", b"ok", b"1", b"1"])
        with self.assertRaises(CoordinationCorruptError):
            await self.store.release_quota("reservation", now=1.0)

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
        self.assertEqual(
            (await store.advance_epoch(2, "advance")).state,
            EpochState.RECONCILING,
        )
        self.assertFalse(
            (await store.compare_and_set(CasRequest("key", 0, b"one", 1, 1, "stale"))).applied
        )
        self.assertEqual((await store.mark_epoch_ready(2, "ready")).state, EpochState.READY)
        self.assertEqual((await store.mark_epoch_ready(3, "ready")).state, EpochState.READY)

        created = await store.compare_and_set(CasRequest("key", 0, b"one", 1, 2, "create"))
        replay = await store.compare_and_set(CasRequest("key", 0, b"one", 1, 2, "create"))
        conflict = await store.compare_and_set(CasRequest("key", 0, b"changed", 1, 2, "create"))
        self.assertEqual((created.applied, created.revision), (True, 1))
        self.assertEqual((await store.read_cas("key", epoch=2)).payload, b"one")
        self.assertTrue(replay.idempotent)
        self.assertFalse(conflict.applied)
        denied = await store.compare_and_set(CasRequest("denied", 1, b"one", 1, 2, "deny"))
        denial_replay = await store.compare_and_set(CasRequest("denied", 1, b"one", 1, 2, "deny"))
        denial_conflict = await store.compare_and_set(
            CasRequest("denied", 1, b"changed", 1, 2, "deny")
        )
        self.assertEqual((denied.applied, denied.idempotent), (False, False))
        self.assertEqual((denial_replay.applied, denial_replay.idempotent), (False, True))
        self.assertEqual((denial_conflict.applied, denial_conflict.idempotent), (False, False))
        client.advance(1_000)
        self.assertIsNone((await store.read_cas("key", epoch=2)).payload)
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

    async def test_stateful_epoch_replay_distinguishes_corrupt_record_from_changed_input(
        self,
    ) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="prod-west",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        await store.advance_epoch(1, "advance")
        await store.mark_epoch_ready(2, "ready")
        self.assertEqual((await store.advance_epoch(99, "advance")).epoch, 2)
        self.assertEqual((await store.mark_epoch_ready(99, "ready")).epoch, 2)

        client.corrupt_replays.update({("epoch_advance", b"advance"), ("epoch_ready", b"ready")})
        with self.assertRaises(CoordinationCorruptError):
            await store.advance_epoch(99, "advance")
        with self.assertRaises(CoordinationCorruptError):
            await store.mark_epoch_ready(99, "ready")
        self.assertEqual((await store.read_epoch()).epoch, 2)

    async def test_namespace_bootstrap_is_read_only_and_partial_epoch_loss_fails_closed(
        self,
    ) -> None:
        fresh_client = StatefulRedisClient()
        fresh_client.epoch_exists = False
        fresh_client.initialization_exists = False
        fresh_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="fresh-namespace",
            _redis_module_for_testing=FakeRedisModule(fresh_client),
        )

        with self.assertRaises(CoordinationCorruptError):
            await fresh_store.compare_and_set(CasRequest("key", 0, b"value", 5, 1, "cas"))
        self.assertFalse(fresh_client.epoch_exists)
        self.assertFalse(fresh_client.initialization_exists)

        self.assertEqual((await fresh_store.read_epoch()).epoch, 1)
        self.assertTrue(fresh_client.epoch_exists)
        self.assertTrue(fresh_client.initialization_exists)
        self.assertTrue(
            (await fresh_store.compare_and_set(CasRequest("key", 0, b"value", 5, 1, "cas"))).applied
        )

        for epoch_exists, initialization_exists in ((False, True), (True, False)):
            with self.subTest(
                epoch_exists=epoch_exists,
                initialization_exists=initialization_exists,
            ):
                client = StatefulRedisClient()
                client.epoch_exists = epoch_exists
                client.initialization_exists = initialization_exists
                store = RedisStateStore(
                    "redis://redis.example/0",
                    deployment_namespace=f"partial-{int(epoch_exists)}",
                    _redis_module_for_testing=FakeRedisModule(client),
                )
                with self.assertRaises(CoordinationCorruptError):
                    await store.read_epoch()
                with self.assertRaises(CoordinationCorruptError):
                    await store.invalidate(InvalidationRequest("scope", 1, "invalidate"))

    async def test_cancelled_cas_response_replays_without_a_second_mutation(self) -> None:
        client = StatefulRedisClient()
        client.cancel_after_response_boundary = {"cas"}
        store = RedisStateStore(
            "redis://alice:top-secret@redis.example/0",
            deployment_namespace="cancel-cas",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        request = CasRequest("key", 0, b"value", 5, 1, "cancelled-cas")

        with self.assertRaises(asyncio.CancelledError):
            await store.compare_and_set(request)

        self.assertEqual(len(client.cas), 1)
        replay = await store.compare_and_set(request)
        conflict = await store.compare_and_set(
            CasRequest("key", 0, b"changed", 5, 1, "cancelled-cas")
        )
        self.assertTrue(replay.idempotent)
        self.assertTrue(replay.applied)
        self.assertFalse(conflict.applied)
        self.assertEqual(len(client.cas), 1)
        self.assertNotIn("alice", repr(store))
        self.assertNotIn("top-secret", repr(store))

    async def test_cancelled_quota_response_replays_without_a_second_mutation(self) -> None:
        client = StatefulRedisClient()
        client.cancel_after_response_boundary = {"quota_reserve"}
        store = RedisStateStore(
            "redis://alice:top-secret@redis.example/0",
            deployment_namespace="cancel-quota",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(**changes: object) -> QuotaReservationRequest:
            values: dict[str, object] = {
                "reservation_id": "cancelled-quota",
                "key_id": "key-a",
                "now": 1_000.0,
                "ttl_seconds": 61.0,
                "estimated_tokens": 1,
                "estimated_cost_usd": 0.1,
                "rpm_limit": None,
                "tpm_limit": None,
                "daily_budget_usd": None,
                "monthly_budget_usd": None,
                "daily_spend_usd": 0.0,
                "monthly_spend_usd": 0.0,
                "daily_snapshot_started_at": 1_000.0,
                "monthly_snapshot_started_at": 1_000.0,
            }
            values.update(changes)
            return QuotaReservationRequest(**values)  # type: ignore[arg-type]

        request = reservation(operation_id="cancelled-quota-op")
        with self.assertRaises(asyncio.CancelledError):
            await store.reserve_quota(request)

        self.assertEqual(len(client.quota_records), 1)
        replay = await store.reserve_quota(request)
        conflict = await store.reserve_quota(
            reservation(estimated_tokens=2, operation_id="cancelled-quota-op")
        )
        self.assertTrue(replay.accepted)
        self.assertTrue(replay.idempotent)
        self.assertEqual(conflict.reason, "conflict")
        self.assertEqual(len(client.quota_records), 1)
        self.assertNotIn("alice", repr(store))
        self.assertNotIn("top-secret", repr(store))

    async def test_stateful_v2_reserve_work_is_constant_at_record_capacity(self) -> None:
        def reservation(
            identifier: str, *, rpm_limit: int | None = None
        ) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                "key-a",
                1_000.0,
                61.0,
                1,
                0.0,
                rpm_limit,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
            )

        small_client = StatefulRedisClient()
        small_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-bounded-small",
            _redis_module_for_testing=FakeRedisModule(small_client),
        )
        self.assertTrue((await small_store.reserve_quota(reservation("small"))).accepted)
        small_work = (small_client.quota_record_inspections, small_client.rate_bucket_inspections)

        key_text = b"key-a"
        key_digest = sha256(len(key_text).to_bytes(8, "big") + key_text).hexdigest().encode("ascii")
        full_client = StatefulRedisClient()
        for index in range(100_000):
            full_client.seed_retained_record(
                key_id=key_digest,
                reservation_id=f"old-{index}".encode("ascii"),
            )
        full_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-bounded-full",
            _redis_module_for_testing=FakeRedisModule(full_client),
        )

        capacity = await full_store.reserve_quota(reservation("at-capacity", rpm_limit=100_001))

        self.assertEqual(capacity.reason, "capacity")
        self.assertEqual(
            (full_client.quota_record_inspections, full_client.rate_bucket_inspections),
            small_work,
        )
        self.assertEqual(small_work, (1, 61))

    async def test_denied_or_replayed_reserve_never_double_counts(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-no-double-count",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str, operation_id: str) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                "key-a",
                1_000.0,
                61.0,
                1,
                0.0,
                1,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
                operation_id=operation_id,
            )

        first_request = reservation("first", "first-op")
        first = await store.reserve_quota(first_request)
        replay = await store.reserve_quota(first_request)
        denied = await store.reserve_quota(reservation("second", "second-op"))
        key_digest = client.script_calls[-1][2][2]

        self.assertTrue(first.accepted)
        self.assertTrue(replay.idempotent)
        self.assertEqual(denied.reason, "rpm")
        self.assertEqual(client.bucket_totals(key_digest), (1, 1))

    async def test_stateful_v2_reserve_includes_the_full_boundary_second(self) -> None:
        client = StatefulRedisClient()
        client.now_ms = 1_000_999
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-boundary-second",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                "key-a",
                1_000.999,
                61.0,
                1,
                0.0,
                1,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.999,
                1_000.999,
            )

        self.assertTrue((await store.reserve_quota(reservation("first"))).accepted)
        client.advance(60_000)
        boundary = await store.reserve_quota(reservation("boundary"))
        client.advance(1)
        after = await store.reserve_quota(reservation("after"))

        self.assertEqual(boundary.reason, "rpm")
        self.assertTrue(after.accepted)

    async def test_commit_moves_estimate_to_the_commit_second(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-commit-buckets",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        request = QuotaReservationRequest(
            "commit",
            "key-a",
            1_000.0,
            61.0,
            100,
            0.0,
            None,
            500,
            None,
            None,
            0.0,
            0.0,
            1_000.0,
            1_000.0,
        )
        self.assertTrue((await store.reserve_quota(request)).accepted)
        key_digest = client.script_calls[-1][2][2]
        client.advance(1_000)

        result = await store.commit_quota(
            QuotaCommitRequest("commit", 1_001.0, 250, 9.0, True, operation_id="commit-op")
        )

        self.assertTrue(result.committed)
        self.assertEqual(client.bucket_totals(key_digest), (1, 250))

    async def test_release_reverses_only_a_live_bucket_contribution(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-release-buckets",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        request = QuotaReservationRequest(
            "release",
            "key-a",
            1_000.0,
            61.0,
            50,
            0.0,
            None,
            None,
            None,
            None,
            0.0,
            0.0,
            1_000.0,
            1_000.0,
        )
        self.assertTrue((await store.reserve_quota(request)).accepted)
        key_digest = client.script_calls[-1][2][2]

        self.assertTrue(await store.release_quota("release", now=1_000.0))

        self.assertEqual(client.bucket_totals(key_digest), (0, 0))

    async def test_commit_and_release_after_bucket_age_do_not_subtract_stale_slots(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-aged-transition",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str, tokens: int) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                identifier,
                1_000.0,
                300.0,
                tokens,
                0.0,
                None,
                500,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
            )

        self.assertTrue((await store.reserve_quota(reservation("aged-commit", 100))).accepted)
        commit_digest = client.script_calls[-1][2][2]
        self.assertTrue((await store.reserve_quota(reservation("aged-release", 50))).accepted)
        release_digest = client.script_calls[-1][2][2]
        client.advance(61_000)

        committed = await store.commit_quota(
            QuotaCommitRequest("aged-commit", 1_061.0, 250, 0.0, False)
        )
        released = await store.release_quota("aged-release", now=1_061.0)

        self.assertTrue(committed.committed)
        self.assertTrue(released)
        self.assertEqual(client.bucket_totals(commit_digest), (1, 250))
        self.assertEqual(client.bucket_totals(release_digest), (0, 0))

    async def test_bucket_underflow_fails_closed_before_lifecycle_mutation(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-underflow",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        request = QuotaReservationRequest(
            "underflow",
            "key-a",
            1_000.0,
            61.0,
            10,
            0.0,
            None,
            100,
            None,
            None,
            0.0,
            0.0,
            1_000.0,
            1_000.0,
        )
        self.assertTrue((await store.reserve_quota(request)).accepted)
        key_digest = client.script_calls[-1][2][2]
        slot = (client.now_ms // 1000) % 61
        client.quota_buckets[key_digest][slot] = (client.now_ms // 1000, 0, 0)

        with self.assertRaises(CoordinationCorruptError):
            await store.commit_quota(QuotaCommitRequest("underflow", 1_000.0, 20, 0.0, False))

        self.assertEqual(client.quota_records[b"underflow"]["state"], "active")

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

    async def test_lock_release_retries_uncertain_result_with_the_same_task_token(self) -> None:
        self.client.command_replies["set"].append(True)
        self.client.script_replies["lock_release"].extend(
            [RuntimeError("connection reset"), [b"1", b"ok", b"0"]]
        )
        self.assertTrue(await self.store.acquire_lock("retry-lock"))
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.release_lock("retry-lock")
        await self.store.release_lock("retry-lock")
        await self.store.release_lock("retry-lock")

        release_calls = [call for call in self.client.script_calls if call[0] == "lock_release"]
        self.assertEqual(len(release_calls), 2)
        self.assertEqual(release_calls[0][2], release_calls[1][2])

    async def test_quota_methods_use_fixed_fenced_scripts_and_decode_results(self) -> None:
        reserve = QuotaReservationRequest(
            "reservation",
            "key",
            1.0,
            61.0,
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
            operation_id="reserve-op",
        )
        commit = QuotaCommitRequest("reservation", 1.0, 1, 0.1, True, operation_id="commit-op")
        self.queue(
            "quota_reserve",
            [b"1", b"accepted", b"reservation", b"", b"0", b"0"],
        )
        self.queue("quota_commit", [b"1", b"committed", b"0", b"0"])
        self.queue("quota_release", [b"1", b"ok", b"1", b"0"])
        key_digest = sha256(len(b"key").to_bytes(8, "big") + b"key").hexdigest().encode("ascii")
        locator = b"2|" + key_digest
        self.client.command_replies["get"].extend([locator, None, locator, None])

        decision = await self.store.reserve_quota(reserve)
        committed = await self.store.commit_quota(commit)
        released = await self.store.release_quota("reservation", now=1.0, operation_id="release-op")

        self.assertTrue(decision.accepted)
        self.assertTrue(committed.committed)
        self.assertTrue(released)
        quota_calls = self.client.script_calls[-3:]
        self.assertEqual(
            [call[0] for call in quota_calls], ["quota_reserve", "quota_commit", "quota_release"]
        )
        self.assertEqual([len(call[1]) for call in quota_calls], [12, 12, 12])
        self.assertTrue(all(call[1][7].endswith(":initialization") for call in quota_calls))
        self.assertEqual([len(call[2]) for call in quota_calls], [21, 13, 9])
        self.assertEqual(quota_calls[0][2][2], key_digest)
        self.assertEqual(quota_calls[1][2][4], key_digest)
        self.assertEqual(quota_calls[2][2][4], key_digest)
        self.assertEqual(quota_calls[0][1][1:5], quota_calls[1][1][1:5])
        self.assertEqual(quota_calls[1][1][1:5], quota_calls[2][1][1:5])

    async def test_stateful_quota_lifecycle_replay_capacity_and_terminal_retention(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-zone",
            _quota_record_limit_for_testing=1,
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str, **changes: object) -> QuotaReservationRequest:
            values: dict[str, object] = {
                "reservation_id": identifier,
                "key_id": "key-a",
                "now": 1_000.0,
                "ttl_seconds": 61.0,
                "estimated_tokens": 1,
                "estimated_cost_usd": 0.1,
                "rpm_limit": None,
                "tpm_limit": None,
                "daily_budget_usd": None,
                "monthly_budget_usd": None,
                "daily_spend_usd": 0.0,
                "monthly_spend_usd": 0.0,
                "daily_snapshot_started_at": 1_000.0,
                "monthly_snapshot_started_at": 1_000.0,
            }
            values.update(changes)
            return QuotaReservationRequest(**values)  # type: ignore[arg-type]

        first = reservation("first", operation_id="reserve-first")
        accepted = await store.reserve_quota(first)
        replay = await store.reserve_quota(first)
        conflict = await store.reserve_quota(
            reservation("first", estimated_tokens=2, operation_id="reserve-first")
        )
        capacity = await store.reserve_quota(reservation("second"))
        isolated = await store.reserve_quota(reservation("other", key_id="key-b"))
        released = await store.release_quota("first", now=1_000.0, operation_id="release")
        release_retry = await store.release_quota("first", now=1_000.0, operation_id="release")
        terminal = await store.reserve_quota(reservation("first", now=1_001.0))

        self.assertTrue(accepted.accepted)
        self.assertTrue(replay.idempotent)
        self.assertEqual(conflict.reason, "conflict")
        self.assertEqual(capacity.reason, "capacity")
        self.assertTrue(isolated.accepted)
        self.assertTrue(released)
        self.assertFalse(release_retry)
        self.assertEqual(terminal.reason, "conflict")

        client.advance(61_001)
        after_retention = await store.reserve_quota(reservation("first", now=1_061.0))
        self.assertTrue(after_retention.accepted)

    async def test_stateful_quota_fencing_limits_cleanup_and_corruption_fail_closed(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-fence",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str, **changes: object) -> QuotaReservationRequest:
            values: dict[str, object] = {
                "reservation_id": identifier,
                "key_id": "key-a",
                "now": 1_000.0,
                "ttl_seconds": 61.0,
                "estimated_tokens": 1,
                "estimated_cost_usd": 0.1,
                "rpm_limit": 1,
                "tpm_limit": None,
                "daily_budget_usd": None,
                "monthly_budget_usd": None,
                "daily_spend_usd": 0.0,
                "monthly_spend_usd": 0.0,
                "daily_snapshot_started_at": 1_000.0,
                "monthly_snapshot_started_at": 1_000.0,
            }
            values.update(changes)
            return QuotaReservationRequest(**values)  # type: ignore[arg-type]

        stale = await store.reserve_quota(reservation("stale", fencing_epoch=2))
        self.assertEqual(stale.reason, "stale_epoch")
        self.assertTrue((await store.reserve_quota(reservation("holder"))).accepted)
        rate_denial = await store.reserve_quota(reservation("limited", operation_id="limited"))
        self.assertEqual(rate_denial.reason, "rpm")
        self.assertGreaterEqual(rate_denial.retry_after_seconds, 1)
        self.assertTrue(await store.release_quota("holder", now=1_000.0))
        self.assertEqual(
            (await store.reserve_quota(reservation("limited", operation_id="limited"))).reason,
            "rpm",
        )

        client.corrupt_quota_pairs = True
        with self.assertRaises(CoordinationCorruptError):
            await store.reserve_quota(reservation("corrupt"))

    async def test_stateful_quota_commit_uses_actual_tokens_and_ignores_budget_snapshots(
        self,
    ) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-snapshots",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str, **changes: object) -> QuotaReservationRequest:
            values: dict[str, object] = {
                "reservation_id": identifier,
                "key_id": "key-a",
                "now": 1_000.0,
                "ttl_seconds": 61.0,
                "estimated_tokens": 100,
                "estimated_cost_usd": 0.4,
                "rpm_limit": None,
                "tpm_limit": 1_000,
                "daily_budget_usd": 1.0,
                "monthly_budget_usd": 1.0,
                "daily_spend_usd": 0.0,
                "monthly_spend_usd": 0.0,
                "daily_snapshot_started_at": 1_000.0,
                "monthly_snapshot_started_at": 1_000.0,
            }
            values.update(changes)
            return QuotaReservationRequest(**values)  # type: ignore[arg-type]

        self.assertTrue((await store.reserve_quota(reservation("committed"))).accepted)
        client.advance(1_000)
        commit = QuotaCommitRequest("committed", 1_001.0, 900, 0.4, True, operation_id="commit")
        committed = await store.commit_quota(commit)
        commit_replay = await store.commit_quota(commit)
        tpm_denied = await store.reserve_quota(
            reservation("tokens", now=1_002.0, estimated_tokens=200)
        )
        reconciled = await store.reserve_quota(
            reservation(
                "reconciled",
                now=1_002.0,
                estimated_tokens=1,
                estimated_cost_usd=0.6,
                daily_spend_usd=0.4,
                monthly_spend_usd=0.4,
                daily_snapshot_started_at=1_001.5,
                monthly_snapshot_started_at=1_001.5,
            )
        )

        self.assertTrue(committed.committed)
        self.assertTrue(commit_replay.idempotent)
        self.assertEqual(tpm_denied.reason, "tpm")
        self.assertTrue(reconciled.accepted)

    async def test_stateful_quota_commit_discriminates_overspent_and_fallback(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-accounting",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str, key_id: str, **changes: object) -> QuotaReservationRequest:
            values: dict[str, object] = {
                "reservation_id": identifier,
                "key_id": key_id,
                "now": 1_000.0,
                "ttl_seconds": 61.0,
                "estimated_tokens": 1,
                "estimated_cost_usd": 0.1,
                "rpm_limit": None,
                "tpm_limit": None,
                "daily_budget_usd": None,
                "monthly_budget_usd": None,
                "daily_spend_usd": 0.0,
                "monthly_spend_usd": 0.0,
                "daily_snapshot_started_at": 1_000.0,
                "monthly_snapshot_started_at": 1_000.0,
            }
            values.update(changes)
            return QuotaReservationRequest(**values)  # type: ignore[arg-type]

        self.assertTrue(
            (await store.reserve_quota(reservation("tpm", "tpm", tpm_limit=100))).accepted
        )
        tpm = await store.commit_quota(QuotaCommitRequest("tpm", 1_000.0, 101, 0.1, False))
        self.assertTrue(tpm.committed)
        self.assertTrue(tpm.overspent)

        self.assertTrue(
            (
                await store.reserve_quota(
                    reservation("fallback", "fallback", estimated_tokens=7, tpm_limit=7)
                )
            ).accepted
        )
        fallback = await store.commit_quota(
            QuotaCommitRequest("fallback", 1_000.0, None, None, False)
        )
        self.assertTrue(fallback.committed)
        self.assertFalse(fallback.overspent)
        self.assertEqual(client.quota_records[b"fallback"]["actual_tokens"], 7)

        self.assertTrue(
            (
                await store.reserve_quota(reservation("daily", "daily", daily_budget_usd=0.5))
            ).accepted
        )
        daily = await store.commit_quota(QuotaCommitRequest("daily", 1_000.0, 1, 0.6, False))
        self.assertFalse(daily.overspent)

        self.assertTrue(
            (
                await store.reserve_quota(reservation("monthly", "monthly", monthly_budget_usd=0.5))
            ).accepted
        )
        monthly = await store.commit_quota(QuotaCommitRequest("monthly", 1_000.0, 1, 0.6, False))
        self.assertFalse(monthly.overspent)

    async def test_stateful_quota_preserves_signed_63_bit_token_decisions(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-large-tokens",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(
            identifier: str,
            key_id: str,
            estimated_tokens: int,
            tpm_limit: int,
        ) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                key_id,
                1_000.0,
                61.0,
                estimated_tokens,
                0.0,
                None,
                tpm_limit,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
            )

        for boundary in (2**53 - 1, 2**53, 2**53 + 1, 2**63 - 1):
            with self.subTest(path="reserve", boundary=boundary):
                key_id = f"reserve-{boundary}"
                self.assertTrue(
                    (
                        await store.reserve_quota(
                            reservation(f"first-{boundary}", key_id, boundary, boundary)
                        )
                    ).accepted
                )
                denied = await store.reserve_quota(
                    reservation(f"second-{boundary}", key_id, 1, boundary)
                )
                self.assertEqual(denied.reason, "tpm")

        for limit, actual in (
            (2**53, 2**53 + 1),
            (2**53 + 1, 2**53 + 2),
            (2**63 - 2, 2**63 - 1),
        ):
            with self.subTest(path="commit", limit=limit, actual=actual):
                identifier = f"commit-{limit}"
                self.assertTrue(
                    (
                        await store.reserve_quota(reservation(identifier, identifier, 0, limit))
                    ).accepted
                )
                result = await store.commit_quota(
                    QuotaCommitRequest(identifier, 1_000.0, actual, 0.0, False)
                )
                self.assertTrue(result.committed)
                self.assertTrue(result.overspent)

    async def test_stateful_quota_re_evaluates_identical_and_changed_operations_after_retention(
        self,
    ) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-expired-replay",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(
            identifier: str, *, operation_id: str, tokens: int = 1
        ) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                identifier,
                1_000.0,
                61.0,
                tokens,
                0.0,
                None,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
                operation_id=operation_id,
            )

        original = reservation("reserve", operation_id="reserve-operation")
        self.assertTrue((await store.reserve_quota(original)).accepted)
        client.advance(61_001)
        identical = await store.reserve_quota(original)
        self.assertTrue(identical.accepted)
        self.assertFalse(identical.idempotent)

        client.advance(61_001)
        changed = await store.reserve_quota(
            reservation("reserve", operation_id="reserve-operation", tokens=2)
        )
        self.assertTrue(changed.accepted)
        self.assertFalse(changed.idempotent)

        commit_request = QuotaCommitRequest(
            "commit", 1_000.0, 1, 0.0, False, operation_id="commit-operation"
        )
        self.assertTrue(
            (
                await store.reserve_quota(
                    reservation("commit", operation_id="commit-reservation-1")
                )
            ).accepted
        )
        self.assertTrue((await store.commit_quota(commit_request)).committed)
        client.advance(61_001)
        self.assertTrue(
            (
                await store.reserve_quota(
                    reservation("commit", operation_id="commit-reservation-2")
                )
            ).accepted
        )
        committed = await store.commit_quota(commit_request)
        self.assertTrue(committed.committed)
        self.assertFalse(committed.idempotent)

        self.assertTrue(
            (
                await store.reserve_quota(
                    reservation("release", operation_id="release-reservation-1")
                )
            ).accepted
        )
        self.assertTrue(
            await store.release_quota("release", now=1_000.0, operation_id="release-operation")
        )
        client.advance(61_001)
        self.assertTrue(
            (
                await store.reserve_quota(
                    reservation("release", operation_id="release-reservation-2")
                )
            ).accepted
        )
        self.assertTrue(
            await store.release_quota(
                "release",
                now=1_000.0,
                operation_id="release-operation",
            )
        )

    async def test_stateful_quota_locator_races_and_target_backlog_fail_closed(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-locators",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str, key_id: str = "key-a") -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                key_id,
                1_000.0,
                61.0,
                1,
                0.1,
                None,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
            )

        self.assertTrue((await store.reserve_quota(reservation("locator"))).accepted)
        locator_key = client.script_calls[-1][1][5]
        client.values[locator_key] = (b"2|" + b"b" * 64, client.now_ms + 60_000)
        with self.assertRaises(CoordinationReconciliationRequiredError):
            await store.commit_quota(QuotaCommitRequest("locator", 1_000.0, 1, 0.1, False))
        self.assertTrue((await store.reserve_quota(reservation("isolated", "key-b"))).accepted)

        self.assertTrue((await store.reserve_quota(reservation("persistent", "key-c"))).accepted)
        persistent_locator = client.script_calls[-1][1][5]
        client.values[persistent_locator] = (client.values[persistent_locator][0], None)
        with self.assertRaises(CoordinationCorruptError):
            await store.release_quota("persistent", now=1_000.0)

        self.assertTrue((await store.reserve_quota(reservation("backlog", "key-d"))).accepted)
        source = client.quota_records[b"backlog"]
        for index in range(257):
            client.quota_records[f"due-{index}".encode()] = {
                **source,
                "retained_until": client.now_ms,
            }
        blocked = await store.reserve_quota(reservation("blocked", "key-d"))
        healthy = await store.reserve_quota(reservation("healthy", "key-e"))
        self.assertEqual(blocked.reason, "reconciliation_required")
        self.assertTrue(healthy.accepted)
        self.assertIn(b"due-256", client.quota_records)

    async def test_stateful_long_active_ttl_keeps_lifecycle_and_locator_reachable(self) -> None:
        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-long-active",
            _redis_module_for_testing=FakeRedisModule(client),
        )

        def reservation(identifier: str) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                "key-a",
                1_000.0,
                3_600.0,
                1,
                0.1,
                None,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
            )

        self.assertTrue((await store.reserve_quota(reservation("commit-long"))).accepted)
        commit_locator = client.script_calls[-1][1][5]
        commit_record = client.quota_records[b"commit-long"]
        self.assertGreaterEqual(client.values[commit_locator][1], commit_record["active_until"])
        self.assertTrue((await store.reserve_quota(reservation("release-long"))).accepted)
        release_locator = client.script_calls[-1][1][5]
        release_record = client.quota_records[b"release-long"]
        self.assertGreaterEqual(client.values[release_locator][1], release_record["active_until"])

        client.advance(3_599_000)
        self.assertTrue(
            (
                await store.commit_quota(
                    QuotaCommitRequest("commit-long", 1_100.0, None, None, False)
                )
            ).committed
        )
        self.assertTrue(await store.release_quota("release-long", now=1_100.0))

    async def test_quota_v2_schema_marker_fails_closed_without_mutation(self) -> None:
        key_text = b"key-a"
        key_digest = sha256(len(key_text).to_bytes(8, "big") + key_text).hexdigest().encode("ascii")

        def reservation(identifier: str) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                "key-a",
                1_000.0,
                61.0,
                1,
                0.0,
                None,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
            )

        client = StatefulRedisClient()
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-schema-missing",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        self.assertTrue((await store.reserve_quota(reservation("existing"))).accepted)
        self.assertEqual(client.quota_schema[key_digest], (2, 1, "ready"))
        del client.quota_schema[key_digest]
        before = copy.deepcopy(
            (client.quota_records, client.quota_replays, client.quota_buckets, client.values)
        )

        missing = await store.reserve_quota(reservation("blocked"))

        self.assertEqual(missing.reason, "reconciliation_required")
        self.assertEqual(
            (client.quota_records, client.quota_replays, client.quota_buckets, client.values),
            before,
        )

        for label, marker, expiring, expected_exception in (
            ("v1", (1, 1, "ready"), False, None),
            ("future", (2, 2, "ready"), False, None),
            ("malformed", (2, 1, "broken"), False, CoordinationCorruptError),
            ("expiring", (2, 1, "ready"), True, CoordinationCorruptError),
        ):
            with self.subTest(label=label):
                scenario_client = StatefulRedisClient()
                scenario_client.quota_schema[key_digest] = marker
                if expiring:
                    scenario_client.quota_schema_expiring.add(key_digest)
                scenario_store = RedisStateStore(
                    "redis://redis.example/0",
                    deployment_namespace=f"quota-schema-{label}",
                    _redis_module_for_testing=FakeRedisModule(scenario_client),
                )
                if expected_exception is not None:
                    with self.assertRaises(expected_exception):
                        await scenario_store.reserve_quota(reservation(label))
                else:
                    result = await scenario_store.reserve_quota(reservation(label))
                    self.assertEqual(result.reason, "reconciliation_required")
                self.assertEqual(scenario_client.quota_records, {})
                self.assertEqual(scenario_client.quota_buckets, {})

    async def test_stateful_quota_requires_explicit_namespace_initialization(self) -> None:
        def reservation(identifier: str, epoch: int = 1) -> QuotaReservationRequest:
            return QuotaReservationRequest(
                identifier,
                "key-a",
                1_000.0,
                61.0,
                1,
                0.1,
                None,
                None,
                None,
                None,
                0.0,
                0.0,
                1_000.0,
                1_000.0,
                fencing_epoch=epoch,
            )

        client = StatefulRedisClient()
        client.epoch_exists = False
        client.initialization_exists = False
        store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-bootstrap",
            _redis_module_for_testing=FakeRedisModule(client),
        )
        with self.assertRaises(CoordinationCorruptError):
            await store.reserve_quota(reservation("bootstrap"))
        self.assertFalse(client.epoch_exists)
        self.assertFalse(client.initialization_exists)

        self.assertEqual((await store.read_epoch()).epoch, 1)
        self.assertTrue((await store.reserve_quota(reservation("bootstrap"))).accepted)
        self.assertTrue(client.epoch_exists)
        self.assertTrue(client.initialization_exists)

        stale_client = StatefulRedisClient()
        stale_client.epoch_exists = False
        stale_client.initialization_exists = True
        stale_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-bootstrap-stale",
            _redis_module_for_testing=FakeRedisModule(stale_client),
        )
        with self.assertRaises(CoordinationCorruptError):
            await stale_store.reserve_quota(reservation("stale", epoch=2))
        self.assertFalse(stale_client.epoch_exists)

        corrupt_client = StatefulRedisClient()
        corrupt_client.initialization_exists = False
        corrupt_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="quota-bootstrap-corrupt",
            _redis_module_for_testing=FakeRedisModule(corrupt_client),
        )
        with self.assertRaises(CoordinationCorruptError):
            await corrupt_store.reserve_quota(reservation("corrupt"))
        self.assertTrue(corrupt_client.epoch_exists)

    def test_scripts_are_fixed_cluster_safe_and_bounded(self) -> None:
        self.assertEqual(
            set(SCRIPT_SOURCES),
            {
                "drain_complete",
                "epoch_read",
                "time_read",
                "epoch_advance",
                "epoch_ready",
                "cas",
                "cas_read",
                "invalidation",
                "invalidation_read",
                "increment",
                "lock_release",
                "quota_reserve",
                "quota_commit",
                "quota_release",
                "security_session_issue",
                "security_session_resolve",
                "security_session_rotate",
                "security_session_revoke",
                "security_session_list",
                "security_attempt_reserve",
                "security_attempt_clear",
                "oidc_transaction_create",
                "oidc_transaction_consume",
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
                    self.assertIn("redis.call('ZCARD'", source)
                    if name.startswith("quota_"):
                        self.assertIn("#replay_due > 256", source)
                        self.assertIn("#lifecycle_due > 256", source)
                        self.assertLess(
                            source.index("for _, operation_id in ipairs(replay_due) do"),
                            source.index("redis.call('HDEL'"),
                        )
                    elif not name.startswith("security_session_"):
                        self.assertIn("#due > 256", source)
                        self.assertLess(
                            source.index("local due = redis.call('ZRANGEBYSCORE'"),
                            source.index("redis.call('HDEL'"),
                        )

        for name in (
            "security_session_issue",
            "security_session_resolve",
            "security_session_rotate",
            "security_session_revoke",
            "security_session_list",
        ):
            with self.subTest(name=name):
                source = SCRIPT_SOURCES[name]
                self.assertIn("local plan = plan_cleanup(now_ms)", source)
                self.assertIn("#due + #replay_due > 256", source)
                self.assertLess(
                    source.index("local plan = plan_cleanup(now_ms)"),
                    source.index("-- apply validated mutation"),
                )
                self.assertLess(
                    source.index("-- apply validated mutation"),
                    source.index(
                        "apply_cleanup(plan)", source.index("-- apply validated mutation")
                    ),
                )

        cas_source = SCRIPT_SOURCES["cas"]
        self.assertIn("redis.call('PTTL', KEYS[2])", cas_source)
        self.assertIn("#record[3] > 16384", cas_source)
        self.assertIn("count <= 64", cas_source)
        self.assertIn("ARGV[10] ~= ARGV[11]", cas_source)
        self.assertIn("has_capability(saved.capabilities, ARGV[10])", cas_source)
        self.assertIn("schema == '1'", cas_source)
        self.assertIn("saved.schema ~= '2'", cas_source)

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

        advance_source = SCRIPT_SOURCES["epoch_advance"]
        self.assertIn("valid_integer(fingerprint)", advance_source)
        self.assertIn("saved_epoch == next_integer(fingerprint)", advance_source)
        self.assertIn("saved_state == 'reconciling'", advance_source)
        self.assertNotIn("next_integer(ARGV[1])", advance_source)

        ready_source = SCRIPT_SOURCES["epoch_ready"]
        self.assertIn("valid_integer(fingerprint)", ready_source)
        self.assertIn("saved_epoch == fingerprint", ready_source)
        self.assertIn("saved_state == 'ready'", ready_source)
        self.assertNotIn("saved_epoch ~= ARGV[1]", ready_source)

        for name in ("quota_reserve", "quota_commit", "quota_release"):
            with self.subTest(name=name):
                source = SCRIPT_SOURCES[name]
                self.assertIn("redis.call('TIME')", source)
                self.assertIn("KEYS[1]", source)
                self.assertIn("ZRANGEBYSCORE", source)
                self.assertIn("LIMIT', 0, 257", source)
                self.assertIn("#replay_due > 256", source)
                self.assertIn("replay_count ~= replay_expiry_count", source)
                self.assertIn("record_count ~= lifecycle_count", source)
                self.assertNotIn("KEYS(", source.upper())
                self.assertNotIn("SCAN", source.upper())

    def test_quota_v2_scripts_are_constant_bounded(self) -> None:
        for name in ("quota_reserve", "quota_commit", "quota_release"):
            with self.subTest(name=name):
                source = SCRIPT_SOURCES[name]
                self.assertIn(f"-- omni:{name}:v2", source)
                self.assertNotIn("redis.call('HGETALL', KEYS[2])", source)
                self.assertNotIn("for reservation_id", source.lower())
                self.assertIn("local RATE_BUCKET_COUNT = 61", source)

    def test_quota_keys_include_rate_and_schema_in_the_same_cluster_slot(self) -> None:
        keys = self.store._quota_keys(b"a" * 64, "reservation", "operation")

        self.assertEqual(len(keys), 10)
        self.assertTrue(all("{" + self.store._tag + "}" in key for key in keys))
        self.assertIn(":quota:rate-buckets:", keys[8])
        self.assertIn(":quota:state-schema:", keys[9])

    def test_quota_lua_uses_exact_checked_token_arithmetic(self) -> None:
        quota_reserve = SCRIPT_SOURCES["quota_reserve"]
        quota_commit = SCRIPT_SOURCES["quota_commit"]

        self.assertIn("local function add_uint", quota_reserve)
        self.assertIn("local function subtract_uint", quota_reserve)
        self.assertIn("local function uint_greater_than", quota_reserve)
        self.assertIn("if uint_greater_than(result, MAX_UINT) then return nil end", quota_reserve)
        self.assertNotIn("tonumber(totals.tokens)", quota_reserve)
        self.assertNotIn("tonumber(record.estimated_tokens)", quota_commit)
        self.assertNotIn("tonumber(record.actual_tokens)", quota_commit)

    def test_quota_lua_excludes_due_state_before_replay_decisions(self) -> None:
        for name in ("quota_reserve", "quota_commit", "quota_release"):
            with self.subTest(name=name):
                source = SCRIPT_SOURCES[name]
                exclusion = source.index("if replay and tonumber(replay.expiry) <= now_ms then")
                replay_decision = source.index("if operation and not replay then")
                self.assertLess(exclusion, replay_decision)
                self.assertIn("record_after_planned_prune", source)

    def test_quota_lua_uses_compact_records_and_exact_safe_timestamps(self) -> None:
        source = SCRIPT_SOURCES["quota_reserve"]

        self.assertIn("local function valid_safe_uint", source)
        self.assertIn("split_exact(value, 14, 1536)", source)
        self.assertIn("record.accepted_at_number > record.active_until_number", source)
        self.assertNotIn("daily_budget", source)
        self.assertNotIn("monthly_budget", source)
        self.assertNotIn("estimated_cost", source)
        self.assertNotIn("actual_cost", source)

    def test_compatibility_reexport_and_virtual_subclass(self) -> None:
        self.assertIs(CompatibilityRedisStateStore, RedisStateStore)
        self.assertTrue(issubclass(RedisStateStore, BaseStateStore))
        self.assertIsInstance(self.store, BaseStateStore)


if __name__ == "__main__":
    unittest.main()
