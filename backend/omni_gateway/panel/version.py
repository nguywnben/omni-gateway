"""Internal implementation detail."""

import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from log import log
from paths import VERSION_FILE



router = APIRouter(prefix="/ogw/version", tags=["version"])


@router.get("/info")
async def get_version_info(check_update: bool = False):
    """Internal implementation detail."""
    try:

        version_file = VERSION_FILE

        # Read version.txt
        if not os.path.exists(version_file):
            return JSONResponse({
                "success": False,
                "error": "version.txt file not found"
            })

        version_data = {}
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    version_data[key] = value

        # Check necessary fields
        if 'short_hash' not in version_data:
            return JSONResponse({
                "success": False,
                "error": "version.txt format error"
            })

        response_data = {
            "success": True,
            "version": version_data.get('short_hash', 'unknown'),
            "full_hash": version_data.get('full_hash', ''),
            "message": version_data.get('message', ''),
            "date": version_data.get('date', '')
        }


        if check_update:
            try:
                from omni_gateway.httpx_client import get_async


                github_version_url = "https://raw.githubusercontent.com/nguywnben/omni-gateway/refs/heads/master/backend/version.txt"


                resp = await get_async(github_version_url, timeout=10.0)

                if resp.status_code == 200:

                    remote_version_data = {}
                    for line in resp.text.strip().split('\n'):
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            remote_version_data[key] = value

                    latest_hash = remote_version_data.get('full_hash', '')
                    latest_short_hash = remote_version_data.get('short_hash', '')
                    current_hash = version_data.get('full_hash', '')

                    has_update = (current_hash != latest_hash) if current_hash and latest_hash else None

                    response_data['check_update'] = True
                    response_data['has_update'] = has_update
                    response_data['latest_version'] = latest_short_hash
                    response_data['latest_hash'] = latest_hash
                    response_data['latest_message'] = remote_version_data.get('message', '')
                    response_data['latest_date'] = remote_version_data.get('date', '')
                else:
                    # GitHub request failed, but does not affect basic version info
                    response_data['check_update'] = False
                    response_data['update_error'] = f"GitHub request failed: {resp.status_code}"

            except Exception as e:
                log.debug(f"Check for updates failed: {e}")
                response_data['check_update'] = False
                response_data['update_error'] = str(e)

        return JSONResponse(response_data)

    except Exception as e:
        log.error(f"Failed to retrieve version information: {e}")
        return JSONResponse({
            "success": False,
            "error": str(e)
        })
