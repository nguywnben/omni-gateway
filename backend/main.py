"""
Main Web Integration - Integrates all routers and modules
é›†åˆrouterå¹¶å¼€å¯ä¸»æœå¡
"""

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

# å…¨å±€å‡­è¯ç®¡ç†å™¨
global_credential_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """åº”ç”¨ç”Ÿå‘½å‘¨æœŸç®¡ç†"""
    global global_credential_manager

    log.info("Starting Omni Gateway main service")

    # åˆå§‹åŒ–é…ç½®ç¼“å­˜ï¼ˆä¼˜å…ˆæ‰§è¡Œï¼‰
    try:
        import config
        await config.init_config()
        log.info("Configuration cache initialized successfully")
    except Exception as e:
        log.error(f"Failed to initialize configuration cache: {e}")

    # åˆå§‹åŒ–å…¨å±€å‡­è¯ç®¡ç†å™¨ï¼ˆé€è¿‡å•ä¾‹å·¥å‚ï¼‰
    try:
        # credential_manager ä¼åœ¨ç¬¬ä¸€æ¬¡è°ƒç”¨æ—¶è‡ªå¨åˆå§‹åŒ–
        # è¿™é‡Œé¢„å…ˆè§¦å‘åˆå§‹åŒ–ä»¥ä¾¿åœ¨å¯å¨æ—¶æ£€æµ‹é”™è¯¯
        await credential_manager._get_or_create()
        log.info("Credential manager initialized successfully")
    except Exception as e:
        log.error(f"Credential manager initialization failed: {e}")
        global_credential_manager = None

    # OAuthå›è°ƒæœå¡å™¨å°†åœ¨éœ€è¦æ—¶æŒ‰éœ€å¯å¨

    # å¯å¨ä¿æ´»æœå¡ï¼ˆæœªé…ç½®URLæ—¶è‡ªå¨è·³è¿‡ï¼Œé›¶å¼€é”€ï¼‰
    try:
        await keepalive_service.start()
    except Exception as e:
        log.error(f"Failed to start keep-alive service: {e}")

    yield

    # æ¸…ç†èµ„æº
    log.info("Starting shutdown of Omni Gateway main service")

    # åœæ­¢ä¿æ´»æœå¡
    try:
        await keepalive_service.stop()
    except Exception as e:
        log.error(f"Error while shutting down keep-alive service: {e}")

    # é¦–å…ˆå…³é—­æ‰€æœ‰å¼‚æ­¥ä»»å¡
    try:
        await shutdown_all_tasks(timeout=10.0)
        log.info("All asynchronous tasks have been shut down")
    except Exception as e:
        log.error(f"Error while shutting down asynchronous tasks: {e}")

    # ç„¶åå…³é—­å‡­è¯ç®¡ç†å™¨
    if global_credential_manager:
        try:
            await global_credential_manager.close()
            log.info("Credential manager closed")
        except Exception as e:
            log.error(f"Error while shutting down credential manager: {e}")

    log.info("Omni Gateway Master Service Stopped")


# åˆ›å»ºFastAPIåº”ç”¨
app = FastAPI(
    title="Omni Gateway",
    description="Gemini API proxy with OpenAI compatibility",
    version="2.0.0",
    lifespan=lifespan,
)

# CORSä¸­é—´ä»¶
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Omniè·¯ç”± - å¤„ç†OpenAIæ ¼å¼è¯·æ±‚å¹¶è½¬æ¢ä¸ºOmni API
app.include_router(omni_openai_router, prefix="", tags=["Omni OpenAI API"])

# Omniè·¯ç”± - å¤„ç†Geminiæ ¼å¼è¯·æ±‚å¹¶è½¬æ¢ä¸ºOmni API
app.include_router(omni_gemini_router, prefix="", tags=["Omni Gemini API"])

# Omniæ¨¡å‹åˆ—è¡¨è·¯ç”± - å¤„ç†Geminiæ ¼å¼ç„æ¨¡å‹åˆ—è¡¨è¯·æ±‚
app.include_router(omni_model_list_router, prefix="", tags=["Omni Model List"])

# Omni Anthropic Messages è·¯ç”± - Anthropic Messages æ ¼å¼å…¼å®¹
app.include_router(omni_anthropic_router, prefix="", tags=["Omni Anthropic Messages"])

# Panelè·¯ç”± - åŒ…å«è®¤è¯ă€å‡­è¯ç®¡ç†å’Œæ§åˆ¶é¢æ¿åŸèƒ½
app.include_router(panel_router, prefix="", tags=["Panel Interface"])

# Vertex AI è·¯ç”± - Gemini åŸç”Ÿæ ¼å¼
app.include_router(vertex_gemini_router, prefix="", tags=["Vertex Gemini API"])

# Vertex AI è·¯ç”± - OpenAI å…¼å®¹æ ¼å¼
app.include_router(vertex_openai_router, prefix="", tags=["Vertex OpenAI API"])

# Vertex AI è·¯ç”± - æ¨¡å‹åˆ—è¡¨
app.include_router(vertex_model_list_router, prefix="", tags=["Vertex Model List"])

# é™æ€æ–‡ä»¶è·¯ç”± - æœå¡frontç›®å½•ä¸‹ç„æ–‡ä»¶ï¼ˆHTMLă€JSă€CSSç­‰ï¼‰
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


# ä¿æ´»æ¥å£ï¼ˆä»…å“åº” HEADï¼‰
@app.head("/keepalive")
async def keepalive() -> Response:
    return Response(status_code=200)

def main():
    """ä¸»å¯å¨å‡½æ•°"""
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
        # å¤ worker æ¨¡å¼ä¸‹ hypercorn run è‡ªè¡Œç®¡ç†è¿›ç¨‹ï¼Œå…ˆåŒæ­¥è·å–é…ç½®
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
