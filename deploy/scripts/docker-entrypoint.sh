#!/bin/sh
set -eu

mkdir -p /app/backend/data/creds /app/backend/data/logs
chown -R gateway:gateway /app/backend/data/creds /app/backend/data/logs

exec gosu gateway "$@"
