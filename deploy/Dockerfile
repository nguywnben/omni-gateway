# syntax=docker/dockerfile:1.7
FROM python:3.12-slim@sha256:423ed6ab25b1921a477529254bfeeabf5855151dc2c3141699a1bfc852199fbf AS runtime

ARG BUILD_DATE=""
ARG VERSION="dev"
ARG REVISION="unknown"

LABEL org.opencontainers.image.title="Omni Gateway" \
      org.opencontainers.image.description="Universal AI router for coding tools" \
      org.opencontainers.image.source="https://github.com/nguywnben/omni-gateway" \
      org.opencontainers.image.url="https://github.com/nguywnben/omni-gateway" \
      org.opencontainers.image.documentation="https://github.com/nguywnben/omni-gateway#readme" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${REVISION}"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    TZ=UTC \
    BUILD_DATE=${BUILD_DATE} \
    BUILD_VERSION=${VERSION} \
    BUILD_REVISION=${REVISION}

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gosu && \
    rm -rf /var/lib/apt/lists/* && \
    groupadd --gid 10001 gateway && \
    useradd --uid 10001 --gid gateway --create-home --shell /usr/sbin/nologin gateway

COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock

COPY --chown=gateway:gateway backend ./backend
COPY --chown=gateway:gateway frontend ./frontend
COPY --chown=gateway:gateway README.md LICENSE .env.example ./
COPY deploy/scripts/docker-entrypoint.sh /usr/local/bin/omni-gateway-entrypoint

RUN chmod 0755 /usr/local/bin/omni-gateway-entrypoint && \
    mkdir -p /app/backend/data/creds /app/backend/data/logs && \
    chown -R gateway:gateway /app

EXPOSE 4283
STOPSIGNAL SIGTERM

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; port = os.getenv('PORT', '4283'); urllib.request.urlopen(f'http://127.0.0.1:{port}/ready', timeout=3).read()" || exit 1

ENTRYPOINT ["/usr/local/bin/omni-gateway-entrypoint"]
CMD ["python", "backend/main.py"]
