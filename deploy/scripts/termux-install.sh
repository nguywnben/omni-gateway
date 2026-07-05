#!/usr/bin/env bash
set -euo pipefail

log() {
    echo "[INFO] $1"
}

fail() {
    echo "[ERROR] $1" >&2
    exit 1
}

if [ "$(id -u)" = "0" ]; then
    fail "Do not run this script as root in Termux."
fi

if [ -z "${PREFIX:-}" ]; then
    fail "This installer is intended for Termux."
fi

export DEBIAN_FRONTEND=noninteractive

log "Updating Termux packages..."
pkg update -y

log "Installing required packages..."
pkg install -y python git nodejs-lts

if ! command -v pm2 >/dev/null 2>&1; then
    log "Installing PM2..."
    npm install -g pm2
fi

if [ -f "./backend/main.py" ]; then
    log "Using current Omni Gateway checkout."
elif [ -f "./omni-gateway/backend/main.py" ]; then
    cd ./omni-gateway
else
    log "Cloning Omni Gateway..."
    git clone https://github.com/nguywnben/omni-gateway.git
    cd ./omni-gateway
fi

if [ ! -d ".venv" ]; then
    log "Creating Python virtual environment..."
    python -m venv .venv
fi

log "Installing Python dependencies..."
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r deploy/requirements-termux.txt

log "Starting Omni Gateway with PM2..."
pm2 start .venv/bin/python --name omni-gateway -- backend/main.py
pm2 save
