"""Internal implementation detail."""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import get_server_host, get_server_port
from log import log
from paths import FRONTEND_DIR

# Import managers and utilities
from omni_gateway.credential_manager import credential_manager

# Import all routers
from omni_gateway.router.omni.openai import router as omni_openai_router
from omni_gateway.router.omni.gemini import router as omni_gemini_router
from omni_gateway.router.omni.anthropic import router as omni_anthropic_router
from omni_gateway.router.omni.model_list import router as omni_model_list_router
from omni_gateway.router.vertex.gemini import router as vertex_gemini_router
from omni_gateway.router.vertex.openai import router as vertex_openai_router
from omni_gateway.router.vertex.model_list import router as vertex_model_list_router
from omni_gateway.task_manager import shutdown_all_tasks
from omni_gateway.panel import router as panel_router
from omni_gateway.keeplive import keepalive_service


global_credential_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Internal implementation detail."""
    global global_credential_manager

    log.info("Starting Omni Gateway main service")


    try:
        import config
        await config.init_config()
        log.info("Configuration cache initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize configuration cache: {e}")


    try:


        await credential_manager._get_or_create()
        log.info("Credential manager initialized successfully")
    except Exception as e:
        log.error(f"Credential manager initialization failed: {e}")
        global_credential_manager = None




    try:
        await keepalive_service.start()
    except Exception as e:
        log.error(f"Failed to start keep-alive service: {e}")

    yield


    log.info("Starting shutdown of Omni Gateway main service")


    try:
        await keepalive_service.stop()
    except Exception as e:
        log.error(f"Error while shutting down keep-alive service: {e}")


    try:
        await shutdown_all_tasks(timeout=10.0)
        log.info("All asynchronous tasks have been shut down")
    except Exception as e:
        log.error(f"Error while shutting down asynchronous tasks: {e}")


    if global_credential_manager:
        try:
            await global_credential_manager.close()
            log.info("Credential manager closed")
        except Exception as e:
            log.error(f"Error while shutting down credential manager: {e}")

    log.info("Omni Gateway Master Service Stopped")



app = FastAPI(
    title="Omni Gateway",
    description="Universal AI router with smart fallback, token compression, and format translation.",
    version="2.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(omni_openai_router, prefix="", tags=["Omni OpenAI API"])


app.include_router(omni_gemini_router, prefix="", tags=["Omni Gemini API"])


app.include_router(omni_model_list_router, prefix="", tags=["Omni Model List"])


app.include_router(omni_anthropic_router, prefix="", tags=["Omni Anthropic Messages"])


app.include_router(panel_router, prefix="", tags=["Panel Interface"])


app.include_router(vertex_gemini_router, prefix="", tags=["Vertex Gemini API"])


app.include_router(vertex_openai_router, prefix="", tags=["Vertex OpenAI API"])


app.include_router(vertex_model_list_router, prefix="", tags=["Vertex Model List"])


app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")



@app.head("/keepalive")
async def keepalive() -> Response:
    return Response(status_code=200)

def main():
    """Internal implementation detail."""
    from hypercorn.asyncio import serve
    from hypercorn.config import Config
    from hypercorn.run import run

    workers = int(os.environ.get("OGW_WORKERS", 1))

    async def _run():
        port = await get_server_port()
        host = await get_server_host()

        log.info("=" * 60)
        log.info("Starting Omni Gateway")
        log.info("=" * 60)
        log.info(f"Control panel: http://127.0.0.1:{port}")
        if workers > 1:
            log.info(f"Number of Workers: {workers}")
        log.info("=" * 60)

        config = Config()
        config.bind = [f"{host}:{port}"]
        config.accesslog = "-"
        config.errorlog = "-"
        config.loglevel = "INFO"

        await serve(app, config)

    if workers == 1:
        asyncio.run(_run())
    else:

        port = int(os.environ.get("OGW_PORT", 7861))
        host = os.environ.get("OGW_HOST", "0.0.0.0")

        log.info("=" * 60)
        log.info("Starting Omni Gateway")
        log.info("=" * 60)
        log.info(f"Control panel: http://127.0.0.1:{port}")
        log.info(f"Number of Workers: {workers}")
        log.info("=" * 60)

        config = Config()
        config.bind = [f"{host}:{port}"]
        config.accesslog = "-"
        config.errorlog = "-"
        config.loglevel = "INFO"
        config.workers = workers
        config.application_path = "main:app"

        run(config)


if __name__ == "__main__":
    main()
