import asyncio
import datetime
import os

from core.utils import PANEL_SESSION_COOKIE, verify_panel_token, verify_panel_token_value
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from log import log, redact_text
from paths import DEFAULT_LOG_FILE
from starlette.websockets import WebSocketState

from .utils import ConnectionManager

router = APIRouter(prefix="/api/logs", tags=["logs"])


manager = ConnectionManager()


def _log_file_size(path: str) -> int | None:
    try:
        return os.path.getsize(path)
    except FileNotFoundError:
        return None


def _clear_log_file(path: str) -> bool:
    if not os.path.exists(path):
        return False
    with open(path, "w", encoding="utf-8"):
        pass
    return True


def _read_recent_log_lines(path: str, limit: int) -> list[str]:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as file:
            return file.readlines()[-limit:]
    except FileNotFoundError:
        return []


def _read_log_chunk(path: str, offset: int, size: int) -> tuple[str, int]:
    try:
        with open(path, "rb") as file:
            file.seek(offset)
            content = file.read(size)
    except FileNotFoundError:
        return "", 0
    return content.decode("utf-8", errors="replace"), len(content)


@router.post("/clear")
async def clear_logs(token: str = Depends(verify_panel_token)):
    try:
        log_file_path = os.getenv("LOG_FILE", str(DEFAULT_LOG_FILE))

        if await asyncio.to_thread(_clear_log_file, log_file_path):
            try:
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
    try:
        log_file_path = os.getenv("LOG_FILE", str(DEFAULT_LOG_FILE))

        file_size = await asyncio.to_thread(_log_file_size, log_file_path)
        if file_size is None:
            raise HTTPException(status_code=404, detail="Log file does not exist.")

        if file_size == 0:
            raise HTTPException(status_code=404, detail="Log file is empty.")

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
    token = websocket.cookies.get(PANEL_SESSION_COOKIE) or websocket.query_params.get("token")

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

        try:
            lines = await asyncio.to_thread(_read_recent_log_lines, log_file_path, 50)
            for line in lines:
                if line.strip():
                    await websocket.send_text(redact_text(line.strip()))
        except Exception as e:
            await websocket.send_text(f"Error reading log file: {e}")
            log.error(f"WebSocket initial log read error: {e}")

        last_size = await asyncio.to_thread(_log_file_size, log_file_path) or 0
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
                    [listener_task], timeout=check_interval, return_when=asyncio.FIRST_COMPLETED
                )

                if listener_task in done:
                    break

                current_size = await asyncio.to_thread(_log_file_size, log_file_path)
                if current_size is not None:
                    if current_size > last_size:
                        read_size = min(current_size - last_size, max_read_size)

                        try:
                            new_content, bytes_read = await asyncio.to_thread(
                                _read_log_chunk,
                                log_file_path,
                                last_size,
                                read_size,
                            )

                            if not new_content:
                                last_size = current_size
                                continue

                            lines = new_content.splitlines(keepends=True)
                            if lines and not lines[-1].endswith(("\n", "\r")) and len(lines) > 1:
                                complete_lines = lines[:-1]
                                trailing_bytes = len(lines[-1].encode("utf-8"))
                            else:
                                complete_lines = lines
                                trailing_bytes = 0

                            for line in complete_lines:
                                if line.strip():
                                    await websocket.send_text(redact_text(line.rstrip()))
                            last_size += max(0, bytes_read - trailing_bytes)
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
