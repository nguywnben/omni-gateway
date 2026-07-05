#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if ! command -v uv >/dev/null 2>&1; then
    echo "[ERROR] uv is required. Install it from https://docs.astral.sh/uv/ and run this script again." >&2
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    uv venv
fi

echo "[INFO] Installing Python dependencies..."
uv pip install -r requirements.txt

echo "[INFO] Starting Omni Gateway..."
exec .venv/bin/python backend/main.py
