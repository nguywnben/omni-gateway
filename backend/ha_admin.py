"""Operator CLI for explicit, dry-run-first HA lifecycle transitions."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from core.ha_activation import verify_ha_activation_record
from core.ha_operator import HaRuntimeOperator
from core.ha_runtime_policy import HaRuntimePolicy
from core.redis_state_store import RedisStateStore
from core.storage_adapter import close_storage_adapter, get_storage_adapter


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect or transition Omni Gateway HA state.")
    parser.add_argument(
        "command",
        choices=("status", "drain", "advance-epoch", "reconcile", "mark-ready", "rollback-plan"),
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply the transition; default is dry-run."
    )
    parser.add_argument("--operation-id", help="Stable idempotency ID for epoch mutations.")
    return parser


async def _execute(arguments: argparse.Namespace) -> dict[str, object]:
    policy = HaRuntimePolicy.from_environment()
    if policy.redis_url is None or policy.coordination_namespace is None:
        raise RuntimeError("The HA operator requires a complete coordinated policy.")
    storage = await get_storage_adapter()
    store = RedisStateStore(
        policy.redis_url,
        deployment_namespace=policy.coordination_namespace,
    )
    operator = HaRuntimeOperator(
        policy,
        storage,
        store,
        activation_verifier=verify_ha_activation_record,
    )
    try:
        if arguments.command == "status":
            return await operator.status()
        if arguments.command == "rollback-plan":
            return await operator.rollback_plan()
        if arguments.command == "drain":
            return await operator.drain(apply=arguments.apply)
        if arguments.command == "reconcile":
            return await operator.reconcile(apply=arguments.apply)
        if not arguments.operation_id:
            raise RuntimeError("--operation-id is required for this command.")
        if arguments.command == "advance-epoch":
            return await operator.advance_epoch(
                arguments.operation_id,
                apply=arguments.apply,
            )
        return await operator.mark_ready(arguments.operation_id, apply=arguments.apply)
    finally:
        await store.close()
        await close_storage_adapter()


def main() -> None:
    arguments = _parser().parse_args()
    try:
        result = asyncio.run(_execute(arguments))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": type(exc).__name__}), file=sys.stderr)
        raise SystemExit(1) from None
    print(json.dumps({"ok": True, "result": result}, sort_keys=True))


if __name__ == "__main__":
    main()
