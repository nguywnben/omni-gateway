"""
æ—¥å¿—è·¯ç”±æ¨¡å— - å¤„ç† /ogw/logs/* ç›¸å…³ç„HTTPè¯·æ±‚å’ŒWebSocketè¿æ¥
"""

import asyncio
import datetime
import os

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from starlette.websockets import WebSocketState

import config
from log import log
from paths import DEFAULT_LOG_FILE
from omni_gateway.utils import verify_panel_token
from .utils import ConnectionManager


# åˆ›å»ºè·¯ç”±å™¨
router = APIRouter(prefix="/ogw/logs", tags=["logs"])

# WebSocketè¿æ¥ç®¡ç†å™¨
manager = ConnectionManager()


@router.post("/clear")
async def clear_logs(token: str = Depends(verify_panel_token)):
    """æ¸…ç©ºæ—¥å¿—æ–‡ä»¶"""
    try:
        # ç›´æ¥ä½¿ç”¨ç¯å¢ƒå˜é‡è·å–æ—¥å¿—æ–‡ä»¶è·¯å¾„
        log_file_path = os.getenv("OGW_LOG_FILE", str(DEFAULT_LOG_FILE))

        # æ£€æŸ¥æ—¥å¿—æ–‡ä»¶æ˜¯å¦å­˜åœ¨
        if os.path.exists(log_file_path):
            try:
                # æ¸…ç©ºæ–‡ä»¶å†…å®¹ï¼ˆä¿ç•™æ–‡ä»¶ï¼‰ï¼Œç¡®ä¿ä»¥UTF-8ç¼–ç å†™å…¥
                # ä½¿ç”¨ with ç¡®ä¿æ–‡ä»¶æ­£ç¡®å…³é—­
                with open(log_file_path, "w", encoding="utf-8") as f:
                    f.write("")
                    f.flush()  # å¼ºåˆ¶åˆ·æ–°åˆ°ç£ç›˜
                    # with é€€å‡ºæ—¶ä¼è‡ªå¨å…³é—­æ–‡ä»¶
                log.info(f"Log file cleared: {log_file_path}")

                # é€çŸ¥æ‰€æœ‰WebSocketè¿æ¥æ—¥å¿—å·²æ¸…ç©º
                await manager.broadcast("--- æ—¥å¿—æ–‡ä»¶å·²æ¸…ç©º ---")

                return JSONResponse(
                    content={"message": f"Log file cleared: {os.path.basename(log_file_path)}"}
                )
            except Exception as e:
                log.error(f"Failed to clear log file: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to clear log file: {str(e)}")
        else:
            return JSONResponse(content={"message": "Log file does not exist"})

    except Exception as e:
        log.error(f"Failed to clear log file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear log file: {str(e)}")


@router.get("/download")
async def download_logs(token: str = Depends(verify_panel_token)):
    """ä¸‹è½½æ—¥å¿—æ–‡ä»¶"""
    try:
        # ç›´æ¥ä½¿ç”¨ç¯å¢ƒå˜é‡è·å–æ—¥å¿—æ–‡ä»¶è·¯å¾„
        log_file_path = os.getenv("OGW_LOG_FILE", str(DEFAULT_LOG_FILE))

        # æ£€æŸ¥æ—¥å¿—æ–‡ä»¶æ˜¯å¦å­˜åœ¨
        if not os.path.exists(log_file_path):
            raise HTTPException(status_code=404, detail="Log file does not exist")

        # æ£€æŸ¥æ–‡ä»¶æ˜¯å¦ä¸ºç©º
        file_size = os.path.getsize(log_file_path)
        if file_size == 0:
            raise HTTPException(status_code=404, detail="Log file is empty")

        # ç”Ÿæˆæ–‡ä»¶åï¼ˆåŒ…å«æ—¶é—´æˆ³ï¼‰
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ogw_logs_{timestamp}.txt"

        log.info(f"Downloading log file: {log_file_path}")

        return FileResponse(
            path=log_file_path,
            filename=filename,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to download log file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download log file: {str(e)}")


@router.websocket("/stream")
async def websocket_logs(websocket: WebSocket):
    """WebSocketç«¯ç‚¹ï¼Œç”¨äºå®æ—¶æ—¥å¿—æµ"""
    # WebSocket è®¤è¯: ä»æŸ¥è¯¢å‚æ•°è·å– token
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=403, reason="Missing authentication token")
        log.warning("WebSocket Connection Denied: Missing Authentication Token")
        return

    # éªŒè¯ token
    try:
        panel_password = await config.get_panel_password()
        if token != panel_password:
            await websocket.close(code=403, reason="Invalid authentication token")
            log.warning("WebSocket connection denied: token verification failed")
            return
    except Exception as e:
        await websocket.close(code=1011, reason="Authentication error")
        log.error(f"Error during WebSocket authentication: {e}")
        return

    # æ£€æŸ¥è¿æ¥æ•°é™åˆ¶
    if not await manager.connect(websocket):
        return

    try:
        # ç›´æ¥ä½¿ç”¨ç¯å¢ƒå˜é‡è·å–æ—¥å¿—æ–‡ä»¶è·¯å¾„
        log_file_path = os.getenv("OGW_LOG_FILE", str(DEFAULT_LOG_FILE))

        # å‘é€åˆå§‹æ—¥å¿—ï¼ˆé™åˆ¶ä¸ºæœ€å50è¡Œï¼Œå‡å°‘å†…å­˜å ç”¨ï¼‰
        if os.path.exists(log_file_path):
            try:
                # ä½¿ç”¨ with ç¡®ä¿æ–‡ä»¶æ­£ç¡®å…³é—­
                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # åªå‘é€æœ€å50è¡Œï¼Œå‡å°‘åˆå§‹å†…å­˜æ¶ˆè€—
                    for line in lines[-50:]:
                        if line.strip():
                            await websocket.send_text(line.strip())
            except Exception as e:
                await websocket.send_text(f"Error reading log file: {e}")
                log.error(f"WebSocket initial log read error: {e}")

        # ç›‘æ§æ—¥å¿—æ–‡ä»¶å˜åŒ–
        last_size = os.path.getsize(log_file_path) if os.path.exists(log_file_path) else 0
        max_read_size = 8192  # é™åˆ¶å•æ¬¡è¯»å–å¤§å°ä¸º8KBï¼Œé˜²æ­¢å¤§é‡æ—¥å¿—é€ æˆå†…å­˜æ¿€å¢
        check_interval = 2  # å¢å æ£€æŸ¥é—´é”ï¼Œå‡å°‘CPUå’ŒI/Oå¼€é”€

        # åˆ›å»ºåå°ä»»å¡ç›‘å¬å®¢æˆ·ç«¯æ–­å¼€
        # å³ä½¿æ²¡æœ‰æ—¥å¿—æ›´æ–°ï¼Œreceive_text() ä¹Ÿèƒ½å³æ—¶æ„ŸçŸ¥æ–­å¼€
        async def listen_for_disconnect():
            try:
                while True:
                    await websocket.receive_text()
            except Exception:
                pass

        listener_task = asyncio.create_task(listen_for_disconnect())

        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                # ä½¿ç”¨ asyncio.wait åŒæ—¶ç­‰å¾…å®æ—¶å™¨å’Œæ–­å¼€ä¿¡å·
                # timeout=check_interval æ›¿ä»£äº† asyncio.sleep
                done, pending = await asyncio.wait(
                    [listener_task],
                    timeout=check_interval,
                    return_when=asyncio.FIRST_COMPLETED
                )

                # å¦‚æœç›‘å¬ä»»å¡ç»“æŸï¼ˆé€å¸¸æ˜¯å› ä¸ºè¿æ¥æ–­å¼€ï¼‰ï¼Œåˆ™é€€å‡ºå¾ªç¯
                if listener_task in done:
                    break

                if os.path.exists(log_file_path):
                    current_size = os.path.getsize(log_file_path)
                    if current_size > last_size:
                        # é™åˆ¶è¯»å–å¤§å°ï¼Œé˜²æ­¢å•æ¬¡è¯»å–è¿‡å¤å†…å®¹
                        read_size = min(current_size - last_size, max_read_size)

                        try:
                            # ä½¿ç”¨ with ç¡®ä¿æ–‡ä»¶æ­£ç¡®å…³é—­ï¼Œå³ä½¿å‘ç”Ÿå¼‚å¸¸
                            with open(log_file_path, "r", encoding="utf-8", errors="replace") as f:
                                f.seek(last_size)
                                new_content = f.read(read_size)
                                # with é€€å‡ºæ—¶è‡ªå¨å…³é—­æ–‡ä»¶å¥æŸ„

                                # å¤„ç†ç¼–ç é”™è¯¯ç„æƒ…å†µ
                                if not new_content:
                                    last_size = current_size
                                    continue

                                # åˆ†è¡Œå‘é€ï¼Œé¿å…å‘é€ä¸å®Œæ•´ç„è¡Œ
                                lines = new_content.splitlines(keepends=True)
                                if lines:
                                    # å¦‚æœæœ€åä¸€è¡Œæ²¡æœ‰æ¢è¡Œç¬¦ï¼Œä¿ç•™åˆ°ä¸‹æ¬¡å¤„ç†
                                    if not lines[-1].endswith("\n") and len(lines) > 1:
                                        # é™¤äº†æœ€åä¸€è¡Œï¼Œå…¶ä»–éƒ½å‘é€
                                        for line in lines[:-1]:
                                            if line.strip():
                                                await websocket.send_text(line.rstrip())
                                        # æ›´æ–°ä½ç½®ï¼Œä½†è¦é€€å›æœ€åä¸€è¡Œç„å­—è‚æ•°
                                        last_size += len(new_content.encode("utf-8")) - len(
                                            lines[-1].encode("utf-8")
                                        )
                                    else:
                                        # æ‰€æœ‰è¡Œéƒ½å‘é€
                                        for line in lines:
                                            if line.strip():
                                                await websocket.send_text(line.rstrip())
                                        last_size += len(new_content.encode("utf-8"))
                        except UnicodeDecodeError as e:
                            # é‡åˆ°ç¼–ç é”™è¯¯æ—¶ï¼Œè·³è¿‡è¿™éƒ¨åˆ†å†…å®¹
                            log.warning(f"WebSocket log read encoding error: {e}, skipping partial content")
                            last_size = current_size
                        except Exception as e:
                            await websocket.send_text(f"Error reading new content: {e}")
                            # å‘ç”Ÿå…¶ä»–é”™è¯¯æ—¶ï¼Œé‡ç½®æ–‡ä»¶ä½ç½®
                            last_size = current_size

                    # å¦‚æœæ–‡ä»¶è¢«æˆªæ–­ï¼ˆå¦‚æ¸…ç©ºæ—¥å¿—ï¼‰ï¼Œé‡ç½®ä½ç½®
                    elif current_size < last_size:
                        last_size = 0
                        await websocket.send_text("--- æ—¥å¿—å·²æ¸…ç©º ---")

        finally:
            # ç¡®ä¿æ¸…ç†ç›‘å¬ä»»å¡
            if not listener_task.done():
                listener_task.cancel()
                try:
                    await listener_task
                except asyncio.CancelledError:
                    pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        log.error(f"WebSocket logs error: {e}")
    finally:
        manager.disconnect(websocket)
