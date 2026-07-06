"""Internal implementation detail."""

import asyncio
import datetime
import os

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from starlette.websockets import WebSocketState

from log import log, redact_text
from paths import DEFAULT_LOG_FILE
from core.utils import verify_panel_token, verify_panel_token_value
from .utils import ConnectionManager



router = APIRouter(prefix="/api/logs", tags=["logs"])


manager = ConnectionManager()


@router.post("/clear")
async def clear_logs(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:

        log_file_path = os.getenv("LOG_FILE", str(DEFAULT_LOG_FILE))


        if os.path.exists(log_file_path):
            try:


                with open(log_file_path, "w", encoding="utf-8") as f:
                    f.write("")
                    f.flush()

                log.info(f"Log file cleared: {log_file_path}")


                await manager.broadcast("--- Log file cleared. ---")

                return JSONResponse(
                    content={"message": f"Log file cleared: {os.path.basename(log_file_path)}."}
                )
            except Exception as e:
                log.error(f"Failed to clear log file: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to clear log file: {str(e)}")
        else:
            return JSONResponse(content={"message": "Log file does not exist."})

    except Exception as e:
        log.error(f"Failed to clear log file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear log file: {str(e)}")


@router.get("/download")
async def download_logs(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:

        log_file_path = os.getenv("LOG_FILE", str(DEFAULT_LOG_FILE))


        if not os.path.exists(log_file_path):
            raise HTTPException(status_code=404, detail="Log file does not exist")


        file_size = os.path.getsize(log_file_path)
        if file_size == 0:
            raise HTTPException(status_code=404, detail="Log file is empty")


        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"logs_{timestamp}.txt"

        log.info(f"Downloading log file: {log_file_path}")

        def sanitized_log_lines():
            with open(log_file_path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    yield redact_text(line)

        return StreamingResponse(
            sanitized_log_lines(),
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
    """Internal implementation detail."""
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=403, reason="Missing authentication token")
        log.warning("WebSocket Connection Denied: Missing Authentication Token")
        return


    try:
        await verify_panel_token_value(token)
    except HTTPException as e:
        close_code = 4401 if e.status_code in {401, 428} else 4403
        await websocket.close(code=close_code, reason=str(e.detail))
        log.warning("WebSocket connection denied: token verification failed")
        return
    except Exception as e:
        await websocket.close(code=1011, reason="Authentication error")
        log.error(f"Error during WebSocket authentication: {e}")
        return


    if not await manager.connect(websocket):
        return

    try:

        log_file_path = os.getenv("LOG_FILE", str(DEFAULT_LOG_FILE))


        if os.path.exists(log_file_path):
            try:

                with open(log_file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                    for line in lines[-50:]:
                        if line.strip():
                            await websocket.send_text(redact_text(line.strip()))
            except Exception as e:
                await websocket.send_text(f"Error reading log file: {e}")
                log.error(f"WebSocket initial log read error: {e}")


        last_size = os.path.getsize(log_file_path) if os.path.exists(log_file_path) else 0
        max_read_size = 8192
        check_interval = 2



        async def listen_for_disconnect():
            try:
                while True:
                    await websocket.receive_text()
            except Exception:
                pass

        listener_task = asyncio.create_task(listen_for_disconnect())

        try:
            while websocket.client_state == WebSocketState.CONNECTED:


                done, pending = await asyncio.wait(
                    [listener_task],
                    timeout=check_interval,
                    return_when=asyncio.FIRST_COMPLETED
                )


                if listener_task in done:
                    break

                if os.path.exists(log_file_path):
                    current_size = os.path.getsize(log_file_path)
                    if current_size > last_size:

                        read_size = min(current_size - last_size, max_read_size)

                        try:

                            with open(log_file_path, "r", encoding="utf-8", errors="replace") as f:
                                f.seek(last_size)
                                new_content = f.read(read_size)



                                if not new_content:
                                    last_size = current_size
                                    continue


                                lines = new_content.splitlines(keepends=True)
                                if lines:

                                    if not lines[-1].endswith("\n") and len(lines) > 1:

                                        for line in lines[:-1]:
                                            if line.strip():
                                                await websocket.send_text(redact_text(line.rstrip()))

                                        last_size += len(new_content.encode("utf-8")) - len(
                                            lines[-1].encode("utf-8")
                                        )
                                    else:

                                        for line in lines:
                                            if line.strip():
                                                await websocket.send_text(redact_text(line.rstrip()))
                                        last_size += len(new_content.encode("utf-8"))
                        except UnicodeDecodeError as e:

                            log.warning(f"WebSocket log read encoding error: {e}, skipping partial content")
                            last_size = current_size
                        except Exception as e:
                            await websocket.send_text(f"Error reading new content: {e}")

                            last_size = current_size


                    elif current_size < last_size:
                        last_size = 0
                        await websocket.send_text("--- Log file cleared. ---")

        finally:

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
