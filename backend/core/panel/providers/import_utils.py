"""Shared limits and filename handling for provider credential imports."""

MAX_PROVIDER_IMPORT_FILE_BYTES = 2 * 1024 * 1024
MAX_PROVIDER_IMPORT_UNCOMPRESSED_BYTES = 5 * 1024 * 1024
MAX_PROVIDER_IMPORT_ENTRIES = 200


def _safe_import_name(value: str, fallback: str = "credential.json") -> str:
    normalized = str(value or "").replace("\\", "/").rstrip("/")
    return normalized.rsplit("/", 1)[-1] or fallback
