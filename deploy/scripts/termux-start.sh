#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if [ ! -d ".venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    python -m venv .venv
fi

echo "[INFO] Installing Python dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

if command -v pm2 >/dev/null 2>&1; then
    echo "[INFO] Starting Omni Gateway with PM2..."
    pm2 start .venv/bin/python --name omni-gateway -- backend/main.py
else
    echo "[INFO] PM2 is not installed. Starting Omni Gateway in the foreground..."
    exec .venv/bin/python backend/main.py
fi
