"""Finite deterministic provider and TCP fault fixture for the isolated HA topology."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import signal
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final

MAX_HTTP_HEADER_BYTES: Final = 16_384
MAX_HTTP_BODY_BYTES: Final = 1_048_576
MAX_PROXY_CONNECTIONS: Final = 128


class FaultAction(StrEnum):
    RESET = "reset"
    REDIS_APP_A_BLOCK = "redis-app-a-block"
    REDIS_APP_A_RESTORE = "redis-app-a-restore"
    REDIS_APP_B_BLOCK = "redis-app-b-block"
    REDIS_APP_B_RESTORE = "redis-app-b-restore"
    REDIS_ALL_BLOCK = "redis-all-block"
    REDIS_ALL_RESTORE = "redis-all-restore"
    POSTGRES_APP_A_BLOCK = "postgres-app-a-block"
    POSTGRES_APP_A_RESTORE = "postgres-app-a-restore"
    POSTGRES_APP_B_BLOCK = "postgres-app-b-block"
    POSTGRES_APP_B_RESTORE = "postgres-app-b-restore"
    POSTGRES_ALL_BLOCK = "postgres-all-block"
    POSTGRES_ALL_RESTORE = "postgres-all-restore"
    REDIS_PROMOTE_STANDBY = "redis-promote-standby"
    REDIS_VERIFY_STANDBY_CAUGHT_UP = "redis-verify-standby-caught-up"
    REDIS_RESTORE_PRIMARY = "redis-restore-primary"
    PROVIDER_HOLD = "provider-hold"
    PROVIDER_RELEASE = "provider-release"
    PROVIDER_DROP_NEXT = "provider-drop-next"


@dataclass(slots=True)
class FixtureState:
    redis_enabled: dict[str, bool] = field(default_factory=lambda: {"app-a": True, "app-b": True})
    postgres_enabled: dict[str, bool] = field(
        default_factory=lambda: {"app-a": True, "app-b": True}
    )
    redis_target: str = "redis-primary"
    provider_held: bool = False
    provider_drop_next: bool = False
    fault_revision: int = 0
    provider_attempts: int = 0
    proxy_accepts: dict[str, int] = field(default_factory=dict)
    milestones: dict[str, int] = field(default_factory=dict)
    release_event: asyncio.Event = field(default_factory=asyncio.Event)
    active_connections: dict[str, set[asyncio.StreamWriter]] = field(
        default_factory=dict, repr=False
    )

    def __post_init__(self) -> None:
        self.release_event.set()

    def snapshot(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "fault_revision": self.fault_revision,
            "redis_enabled": dict(sorted(self.redis_enabled.items())),
            "postgres_enabled": dict(sorted(self.postgres_enabled.items())),
            "redis_target": self.redis_target,
            "provider_held": self.provider_held,
            "provider_drop_next": self.provider_drop_next,
            "provider_attempts": self.provider_attempts,
            "proxy_accepts": dict(sorted(self.proxy_accepts.items())),
            "milestones": dict(sorted(self.milestones.items())),
        }

    def mark(self, name: str) -> None:
        self.milestones[name] = self.milestones.get(name, 0) + 1

    async def close_connections(self, *labels: str) -> None:
        writers = {
            writer for label in labels for writer in self.active_connections.get(label, set())
        }
        for writer in writers:
            writer.close()
        if writers:
            await asyncio.gather(
                *(writer.wait_closed() for writer in writers), return_exceptions=True
            )

    async def apply(self, action: FaultAction) -> None:
        self.fault_revision += 1
        self.mark(action.value)
        if action is FaultAction.RESET:
            self.redis_enabled = {"app-a": True, "app-b": True}
            self.postgres_enabled = {"app-a": True, "app-b": True}
            self.redis_target = "redis-primary"
            self.provider_held = False
            self.provider_drop_next = False
            self.release_event.set()
        elif action is FaultAction.REDIS_APP_A_BLOCK:
            self.redis_enabled["app-a"] = False
            await self.close_connections("redis:app-a")
        elif action is FaultAction.REDIS_APP_A_RESTORE:
            self.redis_enabled["app-a"] = True
        elif action is FaultAction.REDIS_APP_B_BLOCK:
            self.redis_enabled["app-b"] = False
            await self.close_connections("redis:app-b")
        elif action is FaultAction.REDIS_APP_B_RESTORE:
            self.redis_enabled["app-b"] = True
        elif action is FaultAction.REDIS_ALL_BLOCK:
            self.redis_enabled = {"app-a": False, "app-b": False}
            await self.close_connections("redis:app-a", "redis:app-b")
        elif action is FaultAction.REDIS_ALL_RESTORE:
            self.redis_enabled = {"app-a": True, "app-b": True}
        elif action is FaultAction.POSTGRES_APP_A_BLOCK:
            self.postgres_enabled["app-a"] = False
            await self.close_connections("postgres:app-a")
        elif action is FaultAction.POSTGRES_APP_A_RESTORE:
            self.postgres_enabled["app-a"] = True
        elif action is FaultAction.POSTGRES_APP_B_BLOCK:
            self.postgres_enabled["app-b"] = False
            await self.close_connections("postgres:app-b")
        elif action is FaultAction.POSTGRES_APP_B_RESTORE:
            self.postgres_enabled["app-b"] = True
        elif action is FaultAction.POSTGRES_ALL_BLOCK:
            self.postgres_enabled = {"app-a": False, "app-b": False}
            await self.close_connections("postgres:app-a", "postgres:app-b")
        elif action is FaultAction.POSTGRES_ALL_RESTORE:
            self.postgres_enabled = {"app-a": True, "app-b": True}
        elif action is FaultAction.REDIS_VERIFY_STANDBY_CAUGHT_UP:
            await _verify_standby_caught_up()
        elif action is FaultAction.REDIS_PROMOTE_STANDBY:
            await _promote_standby()
            self.redis_target = "redis-standby"
            await self.close_connections("redis:app-a", "redis:app-b")
        elif action is FaultAction.REDIS_RESTORE_PRIMARY:
            await _restore_primary()
            self.redis_target = "redis-primary"
            await self.close_connections("redis:app-a", "redis:app-b")
        elif action is FaultAction.PROVIDER_HOLD:
            self.provider_held = True
            self.release_event.clear()
        elif action is FaultAction.PROVIDER_RELEASE:
            self.provider_held = False
            self.release_event.set()
        elif action is FaultAction.PROVIDER_DROP_NEXT:
            self.provider_drop_next = True


async def _redis_command(host: str, *arguments: str) -> bytes | int:
    reader, writer = await asyncio.wait_for(asyncio.open_connection(host, 6379), timeout=3.0)
    try:
        encoded = [argument.encode("ascii") for argument in arguments]
        writer.write(
            f"*{len(encoded)}\r\n".encode("ascii")
            + b"".join(
                f"${len(argument)}\r\n".encode("ascii") + argument + b"\r\n" for argument in encoded
            )
        )
        await writer.drain()
        first = await asyncio.wait_for(reader.readline(), timeout=6.0)
        if first.startswith(b"+"):
            return first[1:-2]
        if first.startswith(b":"):
            return int(first[1:-2])
        if first.startswith(b"$"):
            size = int(first[1:-2])
            payload = await asyncio.wait_for(reader.readexactly(size + 2), timeout=6.0)
            return payload[:-2]
        raise RuntimeError("Redis fixture command failed.")
    finally:
        writer.close()
        await writer.wait_closed()


async def _promote_standby() -> None:
    if await _redis_command("redis-standby", "REPLICAOF", "NO", "ONE") != b"OK":
        raise RuntimeError("Redis standby promotion was not acknowledged.")
    replication = await _redis_command("redis-standby", "INFO", "replication")
    if not isinstance(replication, bytes) or b"role:master" not in replication:
        raise RuntimeError("Redis standby did not become primary authority.")


def _replication_offset(payload: bytes, field: bytes) -> int:
    prefix = field + b":"
    for line in payload.splitlines():
        if line.startswith(prefix):
            value = line[len(prefix) :]
            if value.isdigit():
                return int(value)
    raise RuntimeError("Redis replication offset is unavailable.")


async def _verify_standby_caught_up() -> None:
    acknowledgements = await _redis_command("redis-primary", "WAIT", "1", "5000")
    if not isinstance(acknowledgements, int) or acknowledgements < 1:
        raise RuntimeError("Redis standby did not acknowledge primary history.")
    primary = await _redis_command("redis-primary", "INFO", "replication")
    standby = await _redis_command("redis-standby", "INFO", "replication")
    if (
        not isinstance(primary, bytes)
        or not isinstance(standby, bytes)
        or b"role:master" not in primary
        or b"role:slave" not in standby
        or b"master_link_status:up" not in standby
        or _replication_offset(standby, b"slave_repl_offset")
        < _replication_offset(primary, b"master_repl_offset")
    ):
        raise RuntimeError("Redis standby is not caught up with the primary.")


async def _restore_primary() -> None:
    if await _redis_command("redis-primary", "REPLICAOF", "redis-standby", "6379") != b"OK":
        raise RuntimeError("Redis former primary did not enter replica mode.")
    for _ in range(30):
        replication = await _redis_command("redis-primary", "INFO", "replication")
        if isinstance(replication, bytes) and b"master_link_status:up" in replication:
            break
        await asyncio.sleep(0.25)
    else:
        raise RuntimeError("Redis former primary did not synchronize from the promoted standby.")
    replicas = await _redis_command("redis-standby", "WAIT", "1", "5000")
    if not isinstance(replicas, int) or replicas < 1:
        raise RuntimeError("Redis restored primary did not acknowledge the promoted history.")
    if await _redis_command("redis-primary", "REPLICAOF", "NO", "ONE") != b"OK":
        raise RuntimeError("Redis primary restoration was not acknowledged.")
    if await _redis_command("redis-standby", "REPLICAOF", "redis-primary", "6379") != b"OK":
        raise RuntimeError("Redis standby did not rejoin the restored primary.")


class TcpProxy:
    def __init__(
        self,
        state: FixtureState,
        *,
        family: str,
        replica: str,
        target_port: int,
    ) -> None:
        self.state = state
        self.family = family
        self.replica = replica
        self.target_port = target_port
        self._semaphore = asyncio.Semaphore(MAX_PROXY_CONNECTIONS)

    async def __call__(self, downstream_reader: asyncio.StreamReader, downstream_writer) -> None:
        label = f"{self.family}:{self.replica}"
        self.state.proxy_accepts[label] = self.state.proxy_accepts.get(label, 0) + 1
        enabled = (
            self.state.redis_enabled[self.replica]
            if self.family == "redis"
            else self.state.postgres_enabled[self.replica]
        )
        if not enabled:
            self.state.mark(f"{label}:blocked")
            downstream_writer.close()
            await downstream_writer.wait_closed()
            return
        target_host = self.state.redis_target if self.family == "redis" else "postgres"
        async with self._semaphore:
            try:
                upstream_reader, upstream_writer = await asyncio.wait_for(
                    asyncio.open_connection(target_host, self.target_port), timeout=3.0
                )
            except (OSError, TimeoutError):
                self.state.mark(f"{label}:connect-failed")
                downstream_writer.close()
                await downstream_writer.wait_closed()
                return

            active = self.state.active_connections.setdefault(label, set())
            active.update((downstream_writer, upstream_writer))

            async def copy(reader: asyncio.StreamReader, writer) -> None:
                try:
                    while chunk := await reader.read(65_536):
                        writer.write(chunk)
                        await writer.drain()
                except (ConnectionError, OSError):
                    pass
                finally:
                    writer.close()

            try:
                await asyncio.gather(
                    copy(downstream_reader, upstream_writer),
                    copy(upstream_reader, downstream_writer),
                )
            finally:
                active.discard(downstream_writer)
                active.discard(upstream_writer)


async def _read_http(reader: asyncio.StreamReader) -> tuple[str, str, dict[str, str], bytes]:
    try:
        header = await reader.readuntil(b"\r\n\r\n")
    except (asyncio.IncompleteReadError, asyncio.LimitOverrunError) as exc:
        raise ValueError("HTTP header is incomplete.") from exc
    if len(header) > MAX_HTTP_HEADER_BYTES:
        raise ValueError("HTTP header is too large.")
    lines = header.decode("ascii").split("\r\n")
    request = lines[0].split(" ")
    if len(request) != 3 or request[2] != "HTTP/1.1":
        raise ValueError("HTTP request line is invalid.")
    headers: dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        name, separator, value = line.partition(":")
        if not separator or name.lower() in headers:
            raise ValueError("HTTP header is invalid.")
        headers[name.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if not 0 <= length <= MAX_HTTP_BODY_BYTES:
        raise ValueError("HTTP body is too large.")
    return request[0], request[1], headers, await reader.readexactly(length)


async def _respond(writer, status: int, payload: object) -> None:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    reason = {200: "OK", 202: "Accepted", 400: "Bad Request", 404: "Not Found"}[status]
    writer.write(
        f"HTTP/1.1 {status} {reason}\r\nContent-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
        + body
    )
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def provider_handler(state: FixtureState, reader: asyncio.StreamReader, writer) -> None:
    try:
        method, path, _, body = await _read_http(reader)
        if method == "GET" and path in {"/health", "/api/tags"}:
            await _respond(writer, 200, {"models": [{"name": "omni-evidence-model"}]})
            return
        if method != "POST" or path not in {"/api/chat", "/v1/chat/completions"}:
            await _respond(writer, 404, {"error": "unsupported_fixture_route"})
            return
        request = json.loads(body)
        if not isinstance(request, dict):
            raise ValueError("Provider payload is invalid.")
        state.provider_attempts += 1
        state.mark("provider-request")
        if state.provider_held:
            await asyncio.wait_for(state.release_event.wait(), timeout=120.0)
        if state.provider_drop_next:
            state.provider_drop_next = False
            state.mark("provider-response-dropped")
            writer.close()
            await writer.wait_closed()
            return
        digest = hashlib.sha256(body).hexdigest()[:16]
        if path == "/api/chat":
            payload = {
                "model": "omni-evidence-model",
                "created_at": "2026-01-01T00:00:00Z",
                "message": {"role": "assistant", "content": f"evidence-{digest}"},
                "done": True,
                "prompt_eval_count": 8,
                "eval_count": 4,
            }
        else:
            payload = {
                "id": f"chatcmpl-{digest}",
                "object": "chat.completion",
                "created": 1_767_225_600,
                "model": "omni-evidence-model",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": f"evidence-{digest}"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
            }
        await _respond(writer, 200, payload)
    except (ValueError, UnicodeError, json.JSONDecodeError, TimeoutError):
        await _respond(writer, 400, {"error": "invalid_fixture_request"})


async def control_handler(state: FixtureState, reader: asyncio.StreamReader, writer) -> None:
    try:
        method, path, headers, _ = await _read_http(reader)
        if method == "GET" and path == "/health":
            await _respond(writer, 200, {"state": "ready", "schema_version": 1})
            return
        if method == "GET" and path == "/state":
            await _respond(writer, 200, state.snapshot())
            return
        prefix = "/actions/"
        if method != "POST" or not path.startswith(prefix):
            await _respond(writer, 404, {"error": "unsupported_fixture_route"})
            return
        expected = os.getenv("EVIDENCE_CONTROL_TOKEN", "")
        supplied = headers.get("x-evidence-control", "")
        if not expected or not hmac.compare_digest(expected, supplied):
            await _respond(writer, 404, {"error": "unsupported_fixture_route"})
            return
        try:
            action = FaultAction(path.removeprefix(prefix))
        except ValueError:
            await _respond(writer, 404, {"error": "unknown_fault_action"})
            return
        await state.apply(action)
        await _respond(
            writer,
            202,
            {"action": action.value, "fault_revision": state.fault_revision, "accepted": True},
        )
    except (ValueError, UnicodeError, TimeoutError):
        await _respond(writer, 400, {"error": "invalid_fixture_request"})


async def serve() -> None:
    state = FixtureState()
    servers = [
        await asyncio.start_server(lambda r, w: provider_handler(state, r, w), "0.0.0.0", 8080),
        await asyncio.start_server(lambda r, w: control_handler(state, r, w), "0.0.0.0", 8081),
        await asyncio.start_server(
            TcpProxy(state, family="redis", replica="app-a", target_port=6379), "0.0.0.0", 16379
        ),
        await asyncio.start_server(
            TcpProxy(state, family="redis", replica="app-b", target_port=6379), "0.0.0.0", 16380
        ),
        await asyncio.start_server(
            TcpProxy(state, family="postgres", replica="app-a", target_port=5432), "0.0.0.0", 15432
        ),
        await asyncio.start_server(
            TcpProxy(state, family="postgres", replica="app-b", target_port=5432), "0.0.0.0", 15433
        ),
    ]
    stopped = asyncio.Event()
    loop = asyncio.get_running_loop()
    for name in ("SIGTERM", "SIGINT"):
        signal_value = getattr(signal, name, None)
        if signal_value is not None:
            try:
                loop.add_signal_handler(signal_value, stopped.set)
            except NotImplementedError:
                pass
    try:
        await stopped.wait()
    finally:
        for server in servers:
            server.close()
        await asyncio.gather(*(server.wait_closed() for server in servers))


def main() -> None:
    if os.getenv("OMNI_RUNTIME_MODE"):
        raise RuntimeError("The evidence fixture cannot run as an application replica.")
    asyncio.run(serve())


if __name__ == "__main__":
    main()
