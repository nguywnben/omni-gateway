from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

from core.utils import verify_panel_token
from .usage import get_stats_24h, get_total_files_count, reset_stats

router = APIRouter(prefix="/api/usage", tags=["usage"])

class ResetUsageRequest(BaseModel):
    filename: str

@router.get("/stats")
async def get_usage_stats(token: str = Depends(verify_panel_token)):
    try:
        data = await get_stats_24h()
        return {"success": True, "data": data}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})

@router.get("/aggregated")
async def get_aggregated_stats(token: str = Depends(verify_panel_token)):
    try:
        data_24h = await get_stats_24h()
        total_calls = sum(item["calls_24h"] for item in data_24h.values())
        total_files = await get_total_files_count()
        avg_calls = total_calls / total_files if total_files > 0 else 0.0

        return {
            "success": True,
            "data": {
                "total_calls_24h": total_calls,
                "total_files": total_files,
                "avg_calls_per_file": avg_calls
            }
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})

@router.post("/reset")
async def reset_usage_stats(request: ResetUsageRequest, token: str = Depends(verify_panel_token)):
    try:
        reset_stats(request.filename)
        return {"success": True, "message": f"Successfully reset usage statistics for {request.filename}"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})
