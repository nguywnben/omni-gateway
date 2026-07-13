import asyncio
import os
import re
import sys
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app_version import get_application_version
from config import get_server_host, get_server_port, trust_proxy_headers_enabled

# Import managers and utilities
from core.credential_manager import credential_manager
from core.health import router as health_router
from core.keep_alive import keep_alive_service
from core.panel import router as panel_router
from core.panel.setup_security import get_setup_bootstrap_token
from core.request_limits import RequestBodyLimitMiddleware, get_max_request_body_bytes
from core.router.primary.anthropic import router as primary_anthropic_router
from core.router.primary.gemini import router as primary_gemini_router
from core.router.primary.model_list import router as primary_model_list_router

# Import all routers
from core.router.primary.openai import router as primary_openai_router
from core.router.primary.responses import router as primary_responses_router
from core.router.protocol_errors import protocol_error_response, protocol_for_path
from core.router.vertex.gemini import router as vertex_gemini_router
from core.router.vertex.model_list import router as vertex_model_list_router
from core.router.vertex.openai import router as vertex_openai_router
from core.storage_adapter import close_storage_adapter
from core.task_manager import shutdown_all_tasks
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from log import configure_logging, log
from paths import FRONTEND_DIR
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.gzip import GZipMiddleware

_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def _parse_csv_env(name: str) -> list[str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def _get_worker_count() -> int:
    raw_value = os.getenv("WORKERS", "1").strip()
    try:
        workers = int(raw_value)
    except ValueError as exc:
        raise RuntimeError("WORKERS must be the integer 1.") from exc
    if workers != 1:
        raise RuntimeError(
            "Omni Gateway 1.0.0 supports WORKERS=1 only. "
            "Credential reservations, cooldowns, and usage aggregation are not yet coordinated "
            "across multiple worker processes."
        )
    return workers


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Starting the Omni Gateway service.")

    try:
        import config

        await config.init_config()
        log_config = await config.get_log_config()
        configure_logging(
            log_config["level"],
            log_config["max_mb"],
            log_config["backup_count"],
        )
        log.info("Configuration cache initialized.")
        if not await config.has_password_configured() and not os.getenv("SETUP_TOKEN", "").strip():
            print(
                "Remote initial setup token: " + get_setup_bootstrap_token(),
                flush=True,
            )
    except Exception as e:
        log.critical(f"Failed to initialize the configuration cache: {e}")
        raise RuntimeError("Configuration initialization failed.") from e

    try:
        await credential_manager._get_or_create()
        log.info("Credential manager initialized.")
    except Exception as e:
        log.critical(f"Credential manager initialization failed: {e}")
        await close_storage_adapter()
        raise RuntimeError("Credential storage initialization failed.") from e

    try:
        await keep_alive_service.start()
    except Exception as e:
        log.error(f"Failed to start the keep-alive service: {e}")

    try:
        yield
    finally:
        log.info("Starting Omni Gateway shutdown.")

        try:
            await keep_alive_service.stop()
        except Exception as e:
            log.error(f"Error while shutting down the keep-alive service: {e}")

        try:
            await shutdown_all_tasks(timeout=10.0)
            log.info("All asynchronous tasks have been shut down.")
        except Exception as e:
            log.error(f"Error while shutting down asynchronous tasks: {e}")

        try:
            await credential_manager.close()
            log.info("Credential manager closed.")
        except Exception as e:
            log.error(f"Error while shutting down the credential manager: {e}")

        try:
            await close_storage_adapter()
            log.info("Storage adapter closed.")
        except Exception as e:
            log.error(f"Error while shutting down the storage adapter: {e}")

        log.info("Omni Gateway stopped.")


app = FastAPI(
    title="Omni Gateway",
    description="Universal AI router with smart auto-fallback, token-aware request cleanup, usage visibility, and seamless format translation.",
    version=get_application_version(),
    lifespan=lifespan,
)


def _validation_error_message(exc: RequestValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "The request payload is invalid."
    first = errors[0]
    location = ".".join(str(part) for part in first.get("loc", ()) if part != "body")
    message = str(first.get("msg") or "The value is invalid.").strip()
    if message and not message.endswith((".", "!", "?")):
        message += "."
    if location:
        return f"Invalid request field '{location}': {message}"
    return f"Invalid request: {message}"


@app.exception_handler(StarletteHTTPException)
async def handle_http_exception(request: Request, exc: StarletteHTTPException):
    protocol = protocol_for_path(request.url.path)
    if protocol:
        detail = (
            exc.detail if isinstance(exc.detail, str) else "The request could not be completed."
        )
        return protocol_error_response(
            protocol,
            exc.status_code,
            detail,
            headers=exc.headers,
        )
    return JSONResponse(
        {"detail": exc.detail},
        status_code=exc.status_code,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, exc: RequestValidationError):
    protocol = protocol_for_path(request.url.path)
    message = _validation_error_message(exc)
    if protocol:
        return protocol_error_response(protocol, 400, message)
    return JSONResponse({"detail": exc.errors()}, status_code=422)


cors_origins = _parse_csv_env("CORS_ORIGINS")
cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX", "").strip() or None
cors_allow_credentials = bool((cors_origins and "*" not in cors_origins) or cors_origin_regex)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=cors_origin_regex,
    allow_credentials=cors_allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "x-api-key",
        "x-goog-api-key",
        "x-anthropic-auth-token",
        "anthropic-auth-token",
        "access_token",
    ],
    expose_headers=["X-Request-ID", "Retry-After"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)
app.add_middleware(
    RequestBodyLimitMiddleware,
    max_body_bytes=get_max_request_body_bytes(),
)


@app.middleware("http")
async def add_security_headers(request, call_next):
    supplied_request_id = request.headers.get("x-request-id", "").strip()
    request_id = (
        supplied_request_id
        if _REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
        else uuid.uuid4().hex
    )
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Origin-Agent-Cluster"] = "?1"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "script-src-attr 'none'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com; "
        "img-src 'self' data:; "
        "connect-src 'self' ws: wss:; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "worker-src 'self'; "
        "manifest-src 'self'"
    )
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    is_https = request.url.scheme == "https" or (
        trust_proxy_headers_enabled()
        and forwarded_proto.split(",", 1)[0].strip().lower() == "https"
    )
    if is_https:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if request.url.path.startswith("/frontend/"):
        response.headers.setdefault("Cache-Control", "public, max-age=86400")
    else:
        response.headers.setdefault("Cache-Control", "no-store")
    return response


app.include_router(primary_openai_router, prefix="", tags=["OpenAI-compatible API"])


app.include_router(primary_responses_router, prefix="", tags=["OpenAI Responses API"])


app.include_router(primary_gemini_router, prefix="", tags=["Gemini-compatible API"])


app.include_router(primary_model_list_router, prefix="", tags=["Model Catalog"])


app.include_router(primary_anthropic_router, prefix="", tags=["Anthropic-compatible Messages"])


app.include_router(health_router, prefix="")


app.include_router(panel_router, prefix="", tags=["Panel Interface"])


app.include_router(vertex_gemini_router, prefix="", tags=["Vertex Gemini API"])


app.include_router(vertex_openai_router, prefix="", tags=["Vertex OpenAI API"])


app.include_router(vertex_model_list_router, prefix="", tags=["Vertex Model List"])


app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.head("/keepalive")
async def keepalive() -> Response:
    return Response(status_code=200)


def main():
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    _get_worker_count()

    async def _run():
        port = await get_server_port()
        host = await get_server_host()

        log.info("=" * 60)
        log.info("Starting Omni Gateway.")
        log.info("=" * 60)
        log.info(f"Control panel: http://127.0.0.1:{port}")
        log.info("=" * 60)

        config = Config()
        config.bind = [f"{host}:{port}"]
        config.accesslog = "-"
        config.errorlog = "-"
        config.loglevel = "INFO"

        await serve(app, config)

    asyncio.run(_run())


if __name__ == "__main__":
    main()
