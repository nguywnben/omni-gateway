from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

from core.utils import verify_panel_token
from core.usage_stats import UNASSIGNED_USAGE_FILENAME
from .usage import get_credential_counts, get_stats_24h, reset_stats

router = APIRouter(prefix="/api/usage", tags=["usage"])

class ResetUsageRequest(BaseModel):
    filename: str = "all"

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
        successful_calls = sum(item.get("successful_calls_24h", 0) for item in data_24h.values())
        failed_calls = sum(item.get("failed_calls_24h", 0) for item in data_24h.values())
        assigned_data_24h = {
            filename: item for filename, item in data_24h.items()
            if filename != UNASSIGNED_USAGE_FILENAME
        }
        assigned_calls = sum(item["calls_24h"] for item in assigned_data_24h.values())
        input_tokens = sum(item.get("input_tokens_24h", 0) for item in data_24h.values())
        output_tokens = sum(item.get("output_tokens_24h", 0) for item in data_24h.values())
        total_tokens = sum(item.get("total_tokens_24h", 0) for item in data_24h.values())
        cached_tokens = sum(item.get("cached_tokens_24h", 0) for item in data_24h.values())
        reasoning_tokens = sum(item.get("reasoning_tokens_24h", 0) for item in data_24h.values())
        credential_counts = await get_credential_counts()
        total_files = credential_counts["total"]
        active_files = credential_counts["active"]
        disabled_files = credential_counts["disabled"]
        avg_calls = assigned_calls / active_files if active_files > 0 else 0.0
        avg_tokens = total_tokens / successful_calls if successful_calls > 0 else 0.0

        return {
            "success": True,
            "data": {
                "total_calls_24h": total_calls,
                "assigned_calls_24h": assigned_calls,
                "successful_calls_24h": successful_calls,
                "failed_calls_24h": failed_calls,
                "total_files": total_files,
                "active_files": active_files,
                "disabled_files": disabled_files,
                "avg_calls_per_file": avg_calls,
                "input_tokens_24h": input_tokens,
                "output_tokens_24h": output_tokens,
                "total_tokens_24h": total_tokens,
                "cached_tokens_24h": cached_tokens,
                "reasoning_tokens_24h": reasoning_tokens,
                "avg_tokens_per_successful_request": avg_tokens
            }
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})

@router.post("/reset")
async def reset_usage_stats(request: ResetUsageRequest, token: str = Depends(verify_panel_token)):
    try:
        reset_stats(request.filename)
        target = "all credentials" if request.filename == "all" else request.filename
        return {"success": True, "message": f"Usage statistics reset for {target}."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "detail": str(e)})
