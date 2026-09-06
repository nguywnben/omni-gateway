# syntax=docker/dockerfile:1.7
ARG PRODUCTION_IMAGE
FROM ${PRODUCTION_IMAGE}

ARG PRODUCTION_IMAGE
ARG EVIDENCE_LAUNCHER_DIGEST
LABEL com.omni-gateway.evidence.launcher-digest="${EVIDENCE_LAUNCHER_DIGEST}" \
      com.omni-gateway.evidence.production-image="${PRODUCTION_IMAGE}" \
      com.omni-gateway.evidence.production="false"

USER root
COPY --chown=gateway:gateway tools/ha_topology_evidence /evidence/tools/ha_topology_evidence
ENV PYTHONPATH=/app/backend:/evidence
USER gateway
