#!/usr/bin/env bash
set -euo pipefail

log() {
    echo "[INFO] $1"
}

fail() {
    echo "[ERROR] $1" >&2
    exit 1
}

if [[ "${OSTYPE:-}" != darwin* ]]; then
    fail "This installer is intended for macOS."
fi

if ! command -v brew >/dev/null 2>&1; then
    log "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    if [ -x "/opt/homebrew/bin/brew" ]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [ -x "/usr/local/bin/brew" ]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
fi

log "Installing required tools..."
brew update
brew install git uv

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
    log "Creating virtual environment..."
    uv venv
fi

log "Installing Python dependencies..."
uv pip install -r requirements.txt

log "Starting Omni Gateway..."
exec .venv/bin/python backend/main.py
