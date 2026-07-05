"""
è®¤è¯APIæ¨¡å—
"""

import asyncio
import socket
import threading
import time
import uuid
from datetime import timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from config import get_config_value, get_ogw_api_url
from log import log

from .google_oauth_api import (
    Credentials,
    Flow,
    enable_required_apis,
    fetch_project_id_and_tier,
    get_user_projects,
    select_default_project,
)
from .storage_adapter import get_storage_adapter
from .utils import (
    OGW_CLIENT_ID,
    OGW_CLIENT_SECRET,
    OGW_SCOPES,
    OGW_USER_AGENT,
    OGW_CODE_ASSIST_CLIENT_ID,
    OGW_CODE_ASSIST_CLIENT_SECRET,
    OGW_CODE_ASSIST_SCOPES,
    CALLBACK_HOST,
    TOKEN_URL,
)


async def get_callback_port():
    """è·å–OAuthå›è°ƒç«¯å£"""
    return int(await get_config_value("oauth_callback_port", "11451", "OGW_OAUTH_CALLBACK_PORT"))


def _prepare_credentials_data(credentials: Credentials, project_id: str, mode: str = "code_assist", subscription_tier: str = None) -> Dict[str, Any]:
    """å‡†å¤‡å‡­è¯æ•°æ®å­—å…¸ï¼ˆç»Ÿä¸€å‡½æ•°ï¼‰"""
    if mode == "omni":
        creds_data = {
            "client_id": OGW_CLIENT_ID,
            "client_secret": OGW_CLIENT_SECRET,
            "token": credentials.access_token,
            "refresh_token": credentials.refresh_token,
            "scopes": OGW_SCOPES,
            "token_uri": TOKEN_URL,
            "project_id": project_id,
        }
    else:
        creds_data = {
            "client_id": OGW_CODE_ASSIST_CLIENT_ID,
            "client_secret": OGW_CODE_ASSIST_CLIENT_SECRET,
            "token": credentials.access_token,
            "refresh_token": credentials.refresh_token,
            "scopes": OGW_CODE_ASSIST_SCOPES,
            "token_uri": TOKEN_URL,
            "project_id": project_id,
        }

    if credentials.expires_at:
        if credentials.expires_at.tzinfo is None:
            expiry_utc = credentials.expires_at.replace(tzinfo=timezone.utc)
        else:
            expiry_utc = credentials.expires_at
        creds_data["expiry"] = expiry_utc.isoformat()

    return creds_data


def _cleanup_auth_flow_server(state: str):
    """æ¸…ç†è®¤è¯æµç¨‹ç„æœå¡å™¨èµ„æº"""
    if state in auth_flows:
        flow_data_to_clean = auth_flows[state]
        try:
            if flow_data_to_clean.get("server"):
                server = flow_data_to_clean["server"]
                port = flow_data_to_clean.get("callback_port")
                async_shutdown_server(server, port)
        except Exception as e:
            log.debug(f"å…³é—­æœå¡å™¨æ—¶å‡ºé”™: {e}")
        del auth_flows[state]


class _OAuthLibPatcher:
    """oauthlibå‚æ•°éªŒè¯è¡¥ä¸ç„ä¸ä¸‹æ–‡ç®¡ç†å™¨"""
    def __init__(self):
        import oauthlib.oauth2.rfc6749.parameters
        self.module = oauthlib.oauth2.rfc6749.parameters
        self.original_validate = None

    def __enter__(self):
        self.original_validate = self.module.validate_token_parameters

        def patched_validate(params):
            try:
                return self.original_validate(params)
            except Warning:
                pass

        self.module.validate_token_parameters = patched_validate
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.original_validate:
            self.module.validate_token_parameters = self.original_validate


# å…¨å±€ç¶æ€ç®¡ç† - ä¸¥æ ¼é™åˆ¶å¤§å°
auth_flows = {}  # å­˜å‚¨è¿›è¡Œä¸­ç„è®¤è¯æµç¨‹
MAX_AUTH_FLOWS = 20  # ä¸¥æ ¼é™åˆ¶æœ€å¤§è®¤è¯æµç¨‹æ•°
DEFAULT_PROJECT_ID = "gemini-pro-1751713012-07fc4dfd"


def cleanup_auth_flows_for_memory():
    """æ¸…ç†è®¤è¯æµç¨‹ä»¥é‡æ”¾å†…å­˜"""
    global auth_flows
    cleanup_expired_flows()
    # å¦‚æœè¿˜æ˜¯å¤ªå¤ï¼Œå¼ºåˆ¶æ¸…ç†ä¸€äº›æ—§ç„æµç¨‹
    if len(auth_flows) > 10:
        # æŒ‰åˆ›å»ºæ—¶é—´æ’åºï¼Œä¿ç•™æœ€æ–°ç„10ä¸ª
        sorted_flows = sorted(
            auth_flows.items(), key=lambda x: x[1].get("created_at", 0), reverse=True
        )
        new_auth_flows = dict(sorted_flows[:10])

        # æ¸…ç†è¢«ç§»é™¤ç„æµç¨‹
        for state, flow_data in auth_flows.items():
            if state not in new_auth_flows:
                try:
                    if flow_data.get("server"):
                        server = flow_data["server"]
                        port = flow_data.get("callback_port")
                        async_shutdown_server(server, port)
                except Exception:
                    pass
                flow_data.clear()

        auth_flows = new_auth_flows
        log.info(f"å¼ºåˆ¶æ¸…ç†è®¤è¯æµç¨‹ï¼Œä¿ç•™ {len(auth_flows)} ä¸ªæœ€æ–°æµç¨‹")

    return len(auth_flows)


async def find_available_port(start_port: int = None) -> int:
    """å¨æ€æŸ¥æ‰¾å¯ç”¨ç«¯å£"""
    if start_port is None:
        start_port = await get_callback_port()

    # é¦–å…ˆå°è¯•é»˜è®¤ç«¯å£
    for port in range(start_port, start_port + 100):  # å°è¯•100ä¸ªç«¯å£
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                log.info(f"æ‰¾åˆ°å¯ç”¨ç«¯å£: {port}")
                return port
        except OSError:
            continue

    # å¦‚æœéƒ½ä¸å¯ç”¨ï¼Œè®©ç³»ç»Ÿè‡ªå¨åˆ†é…ç«¯å£
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", 0))
            port = s.getsockname()[1]
            log.info(f"ç³»ç»Ÿåˆ†é…å¯ç”¨ç«¯å£: {port}")
            return port
    except OSError as e:
        log.error(f"æ— æ³•æ‰¾åˆ°å¯ç”¨ç«¯å£: {e}")
        raise RuntimeError("æ— æ³•æ‰¾åˆ°å¯ç”¨ç«¯å£")


def create_callback_server(port: int) -> HTTPServer:
    """åˆ›å»ºæŒ‡å®ç«¯å£ç„å›è°ƒæœå¡å™¨ï¼Œä¼˜åŒ–å¿«é€Ÿå…³é—­"""
    try:
        # æœå¡å™¨ç›‘å¬0.0.0.0
        server = HTTPServer(("0.0.0.0", port), AuthCallbackHandler)

        # è®¾ç½®socketé€‰é¡¹ä»¥æ”¯æŒå¿«é€Ÿå…³é—­
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # è®¾ç½®è¾ƒçŸ­ç„è¶…æ—¶æ—¶é—´
        server.timeout = 1.0

        log.info(f"åˆ›å»ºOAuthå›è°ƒæœå¡å™¨ï¼Œç›‘å¬ç«¯å£: {port}")
        return server
    except OSError as e:
        log.error(f"åˆ›å»ºç«¯å£{port}ç„æœå¡å™¨å¤±è´¥: {e}")
        raise


class AuthCallbackHandler(BaseHTTPRequestHandler):
    """OAuthå›è°ƒå¤„ç†å™¨"""

    def do_GET(self):
        query_components = parse_qs(urlparse(self.path).query)
        code = query_components.get("code", [None])[0]
        state = query_components.get("state", [None])[0]

        log.info(f"æ”¶åˆ°OAuthå›è°ƒ: code={'å·²è·å–' if code else 'æœªè·å–'}, state={state}")

        if code and state and state in auth_flows:
            # æ›´æ–°æµç¨‹ç¶æ€
            auth_flows[state]["code"] = code
            auth_flows[state]["completed"] = True

            log.info(f"OAuthå›è°ƒæˆåŸå¤„ç†: state={state}")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            # æˆåŸé¡µé¢
            self.wfile.write(
                b"<h1>OAuth authentication successful!</h1><p>You can close this window. Please return to the original page and click 'Get Credentials' button.</p>"
            )
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authentication failed.</h1><p>Please try again.</p>")

    def log_message(self, format, *args):
        # å‡å°‘æ—¥å¿—å™ªéŸ³
        pass


async def create_auth_url(
    project_id: Optional[str] = None, user_session: str = None, mode: str = "code_assist"
) -> Dict[str, Any]:
    """åˆ›å»ºè®¤è¯URLï¼Œæ”¯æŒå¨æ€ç«¯å£åˆ†é…"""
    try:
        # å¨æ€åˆ†é…ç«¯å£
        callback_port = await find_available_port()
        callback_url = f"http://{CALLBACK_HOST}:{callback_port}"

        # ç«‹å³å¯å¨å›è°ƒæœå¡å™¨
        try:
            callback_server = create_callback_server(callback_port)
            # åœ¨åå°çº¿ç¨‹ä¸­è¿è¡Œæœå¡å™¨
            server_thread = threading.Thread(
                target=callback_server.serve_forever,
                daemon=True,
                name=f"OAuth-Server-{callback_port}",
            )
            server_thread.start()
            log.info(f"OAuthå›è°ƒæœå¡å™¨å·²å¯å¨ï¼Œç«¯å£: {callback_port}")
        except Exception as e:
            log.error(f"å¯å¨å›è°ƒæœå¡å™¨å¤±è´¥: {e}")
            return {
                "success": False,
                "error": f"Failed to start OAuth callback server on port {callback_port}: {str(e)}",
            }

        # åˆ›å»ºOAuthæµç¨‹
        # æ ¹æ®æ¨¡å¼é€‰æ‹©é…ç½®
        if mode == "omni":
            client_id = OGW_CLIENT_ID
            client_secret = OGW_CLIENT_SECRET
            scopes = OGW_SCOPES
        else:
            client_id = OGW_CODE_ASSIST_CLIENT_ID
            client_secret = OGW_CODE_ASSIST_CLIENT_SECRET
            scopes = OGW_CODE_ASSIST_SCOPES

        if not client_id or not client_secret:
            client_prefix = "OGW_CLIENT" if mode == "omni" else "OGW_CODE_ASSIST_CLIENT"
            return {
                "success": False,
                "error": f"Missing OAuth client configuration. Set {client_prefix}_ID and {client_prefix}_SECRET.",
            }

        flow = Flow(
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
            redirect_uri=callback_url,
        )

        # ç”Ÿæˆç¶æ€æ ‡è¯†ç¬¦ï¼ŒåŒ…å«ç”¨æˆ·ä¼è¯ä¿¡æ¯
        if user_session:
            state = f"{user_session}_{str(uuid.uuid4())}"
        else:
            state = str(uuid.uuid4())

        # ç”Ÿæˆè®¤è¯URL
        auth_url = flow.get_auth_url(state=state)

        # ä¸¥æ ¼æ§åˆ¶è®¤è¯æµç¨‹æ•°é‡ - è¶…è¿‡é™åˆ¶æ—¶ç«‹å³æ¸…ç†æœ€æ—§ç„
        if len(auth_flows) >= MAX_AUTH_FLOWS:
            # æ¸…ç†æœ€æ—§ç„è®¤è¯æµç¨‹
            oldest_state = min(auth_flows.keys(), key=lambda k: auth_flows[k].get("created_at", 0))
            try:
                # æ¸…ç†æœå¡å™¨èµ„æº
                old_flow = auth_flows[oldest_state]
                if old_flow.get("server"):
                    server = old_flow["server"]
                    port = old_flow.get("callback_port")
                    async_shutdown_server(server, port)
            except Exception as e:
                log.warning(f"Failed to cleanup old auth flow {oldest_state}: {e}")

            del auth_flows[oldest_state]
            log.debug(f"Removed oldest auth flow: {oldest_state}")

        # ä¿å­˜æµç¨‹ç¶æ€
        auth_flows[state] = {
            "flow": flow,
            "project_id": project_id,  # å¯èƒ½ä¸ºNoneï¼Œç¨ååœ¨å›è°ƒæ—¶ç¡®å®
            "user_session": user_session,
            "callback_port": callback_port,  # å­˜å‚¨åˆ†é…ç„ç«¯å£
            "callback_url": callback_url,  # å­˜å‚¨å®Œæ•´å›è°ƒURL
            "server": callback_server,  # å­˜å‚¨æœå¡å™¨å®ä¾‹
            "server_thread": server_thread,  # å­˜å‚¨æœå¡å™¨çº¿ç¨‹
            "code": None,
            "completed": False,
            "created_at": time.time(),
            "auto_project_detection": project_id is None,  # æ ‡è®°æ˜¯å¦éœ€è¦è‡ªå¨æ£€æµ‹é¡¹ç›®ID
            "mode": mode,  # å‡­è¯æ¨¡å¼
        }

        # æ¸…ç†è¿‡æœŸç„æµç¨‹ï¼ˆ30åˆ†é’Ÿï¼‰
        cleanup_expired_flows()

        log.info(f"OAuthæµç¨‹å·²åˆ›å»º: state={state}, project_id={project_id}")
        log.info(f"ç”¨æˆ·éœ€è¦è®¿é—®è®¤è¯URLï¼Œç„¶åOAuthä¼å›è°ƒåˆ° {callback_url}")
        log.info(f"ä¸ºæ­¤è®¤è¯æµç¨‹åˆ†é…ç„ç«¯å£: {callback_port}")

        return {
            "auth_url": auth_url,
            "state": state,
            "callback_port": callback_port,
            "success": True,
            "auto_project_detection": project_id is None,
            "detected_project_id": project_id,
        }

    except Exception as e:
        log.error(f"åˆ›å»ºè®¤è¯URLå¤±è´¥: {e}")
        return {"success": False, "error": str(e)}


def wait_for_callback_sync(state: str, timeout: int = 300) -> Optional[str]:
    """åŒæ­¥ç­‰å¾…OAuthå›è°ƒå®Œæˆï¼Œä½¿ç”¨å¯¹åº”æµç¨‹ç„ä¸“ç”¨æœå¡å™¨"""
    if state not in auth_flows:
        log.error(f"æœªæ‰¾åˆ°ç¶æ€ä¸º {state} ç„è®¤è¯æµç¨‹")
        return None

    flow_data = auth_flows[state]
    callback_port = flow_data["callback_port"]

    # æœå¡å™¨å·²ç»åœ¨create_auth_urlæ—¶å¯å¨äº†ï¼Œè¿™é‡Œåªéœ€è¦ç­‰å¾…
    log.info(f"ç­‰å¾…OAuthå›è°ƒå®Œæˆï¼Œç«¯å£: {callback_port}")

    # ç­‰å¾…å›è°ƒå®Œæˆ
    start_time = time.time()
    while time.time() - start_time < timeout:
        if flow_data.get("code"):
            log.info("OAuthå›è°ƒæˆåŸå®Œæˆ")
            return flow_data["code"]
        time.sleep(0.5)  # æ¯0.5ç§’æ£€æŸ¥ä¸€æ¬¡

        # åˆ·æ–°flow_dataå¼•ç”¨
        if state in auth_flows:
            flow_data = auth_flows[state]

    log.warning(f"ç­‰å¾…OAuthå›è°ƒè¶…æ—¶ ({timeout}ç§’)")
    return None


async def complete_auth_flow(
    project_id: Optional[str] = None, user_session: str = None
) -> Dict[str, Any]:
    """å®Œæˆè®¤è¯æµç¨‹å¹¶ä¿å­˜å‡­è¯ï¼Œæ”¯æŒè‡ªå¨æ£€æµ‹é¡¹ç›®ID"""
    try:
        # æŸ¥æ‰¾å¯¹åº”ç„è®¤è¯æµç¨‹
        state = None
        flow_data = None

        # å¦‚æœæŒ‡å®äº†project_idï¼Œå…ˆå°è¯•åŒ¹é…æŒ‡å®ç„é¡¹ç›®
        if project_id:
            for s, data in auth_flows.items():
                if data["project_id"] == project_id:
                    # å¦‚æœæŒ‡å®äº†ç”¨æˆ·ä¼è¯ï¼Œä¼˜å…ˆåŒ¹é…ç›¸åŒä¼è¯ç„æµç¨‹
                    if user_session and data.get("user_session") == user_session:
                        state = s
                        flow_data = data
                        break
                    # å¦‚æœæ²¡æœ‰æŒ‡å®ä¼è¯ï¼Œæˆ–æ²¡æ‰¾åˆ°åŒ¹é…ä¼è¯ç„æµç¨‹ï¼Œä½¿ç”¨ç¬¬ä¸€ä¸ªåŒ¹é…é¡¹ç›®IDç„
                    elif not state:
                        state = s
                        flow_data = data

        # å¦‚æœæ²¡æœ‰æŒ‡å®é¡¹ç›®IDæˆ–æ²¡æ‰¾åˆ°åŒ¹é…ç„ï¼ŒæŸ¥æ‰¾éœ€è¦è‡ªå¨æ£€æµ‹é¡¹ç›®IDç„æµç¨‹
        if not state:
            for s, data in auth_flows.items():
                if data.get("auto_project_detection", False):
                    # å¦‚æœæŒ‡å®äº†ç”¨æˆ·ä¼è¯ï¼Œä¼˜å…ˆåŒ¹é…ç›¸åŒä¼è¯ç„æµç¨‹
                    if user_session and data.get("user_session") == user_session:
                        state = s
                        flow_data = data
                        break
                    # ä½¿ç”¨ç¬¬ä¸€ä¸ªæ‰¾åˆ°ç„éœ€è¦è‡ªå¨æ£€æµ‹ç„æµç¨‹
                    elif not state:
                        state = s
                        flow_data = data

        if not state or not flow_data:
            return {"success": False, "error": "Authentication flow not found. Please click to get an authentication link first."}

        if not project_id:
            project_id = flow_data.get("project_id")
            if not project_id:
                project_id = DEFAULT_PROJECT_ID
                log.warning(f"æœªè·å–åˆ°project_idï¼Œä½¿ç”¨é»˜è®¤project_id: {project_id}")

        flow = flow_data["flow"]

        # å¦‚æœè¿˜æ²¡æœ‰æˆæƒç ï¼Œéœ€è¦ç­‰å¾…å›è°ƒ
        if not flow_data.get("code"):
            log.info(f"ç­‰å¾…ç”¨æˆ·å®ŒæˆOAuthæˆæƒ (state: {state})")
            auth_code = wait_for_callback_sync(state)

            if not auth_code:
                return {
                    "success": False,
                    "error": "Authorization callback not received. Please ensure you completed OAuth authorization in the browser.",
                }

            # æ›´æ–°æµç¨‹æ•°æ®
            auth_flows[state]["code"] = auth_code
            auth_flows[state]["completed"] = True
        else:
            auth_code = flow_data["code"]

        # ä½¿ç”¨è®¤è¯ä»£ç è·å–å‡­è¯
        with _OAuthLibPatcher():
            try:
                credentials = await flow.exchange_code(auth_code)
                # credentials å·²ç»åœ¨ exchange_code ä¸­è·å¾—

                # å¦‚æœéœ€è¦è‡ªå¨æ£€æµ‹é¡¹ç›®IDä¸”æ²¡æœ‰æä¾›é¡¹ç›®ID
                if flow_data.get("auto_project_detection", False) and not project_id:
                    log.info("å°è¯•é€è¿‡APIè·å–ç”¨æˆ·é¡¹ç›®åˆ—è¡¨...")
                    log.info(f"ä½¿ç”¨ç„token: {credentials.access_token[:20]}...")
                    log.info(f"Tokenè¿‡æœŸæ—¶é—´: {credentials.expires_at}")
                    user_projects = await get_user_projects(credentials)

                    if user_projects:
                        # å¦‚æœåªæœ‰ä¸€ä¸ªé¡¹ç›®ï¼Œè‡ªå¨ä½¿ç”¨
                        if len(user_projects) == 1:
                            # Google API returns projectId in camelCase
                            project_id = user_projects[0].get("projectId")
                            if project_id:
                                flow_data["project_id"] = project_id
                                log.info(f"è‡ªå¨é€‰æ‹©å”¯ä¸€é¡¹ç›®: {project_id}")
                        # å¦‚æœæœ‰å¤ä¸ªé¡¹ç›®ï¼Œå°è¯•é€‰æ‹©é»˜è®¤é¡¹ç›®
                        else:
                            project_id = await select_default_project(user_projects)
                            if project_id:
                                flow_data["project_id"] = project_id
                                log.info(f"è‡ªå¨é€‰æ‹©é»˜è®¤é¡¹ç›®: {project_id}")
                            else:
                                # è¿”å›é¡¹ç›®åˆ—è¡¨è®©ç”¨æˆ·é€‰æ‹©
                                return {
                                    "success": False,
                                    "error": "Please select one of the following projects",
                                    "requires_project_selection": True,
                                    "available_projects": [
                                        {
                                            # Google API returns projectId in camelCase
                                            "project_id": p.get("projectId"),
                                            "name": p.get("displayName") or p.get("projectId"),
                                            "projectNumber": p.get("projectNumber"),
                                        }
                                        for p in user_projects
                                    ],
                                }
                    else:
                        # å¦‚æœæ— æ³•è·å–é¡¹ç›®åˆ—è¡¨ï¼Œä½¿ç”¨é»˜è®¤project_id
                        project_id = DEFAULT_PROJECT_ID
                        flow_data["project_id"] = project_id
                        log.warning(f"æ— æ³•è·å–é¡¹ç›®åˆ—è¡¨ï¼Œä½¿ç”¨é»˜è®¤project_id: {project_id}")

                # å¦‚æœä»ç„¶æ²¡æœ‰é¡¹ç›®IDï¼Œè¿”å›é”™è¯¯
                if not project_id:
                    project_id = DEFAULT_PROJECT_ID
                    flow_data["project_id"] = project_id
                    log.warning(f"ä»æœªè·å–åˆ°project_idï¼Œä½¿ç”¨é»˜è®¤project_id: {project_id}")

                # ä¿å­˜å‡­è¯
                saved_filename = await save_credentials(credentials, project_id)

                # å‡†å¤‡è¿”å›ç„å‡­è¯æ•°æ®
                creds_data = _prepare_credentials_data(credentials, project_id, mode="code_assist")

                # æ¸…ç†ä½¿ç”¨è¿‡ç„æµç¨‹
                _cleanup_auth_flow_server(state)

                log.info("OAuthè®¤è¯æˆåŸï¼Œå‡­è¯å·²ä¿å­˜")
                return {
                    "success": True,
                    "credentials": creds_data,
                    "file_path": saved_filename,
                    "auto_detected_project": flow_data.get("auto_project_detection", False),
                }

            except Exception as e:
                log.error(f"Failed to retrieve credential: {e}")
                return {"success": False, "error": f"Failed to retrieve credential: {str(e)}"}

    except Exception as e:
        log.error(f"å®Œæˆè®¤è¯æµç¨‹å¤±è´¥: {e}")
        return {"success": False, "error": str(e)}


async def asyncio_complete_auth_flow(
    project_id: Optional[str] = None, user_session: str = None, mode: str = "code_assist"
) -> Dict[str, Any]:
    """å¼‚æ­¥å®Œæˆè®¤è¯æµç¨‹ï¼Œæ”¯æŒè‡ªå¨æ£€æµ‹é¡¹ç›®ID"""
    try:
        log.info(
            f"asyncio_complete_auth_flowå¼€å§‹æ‰§è¡Œ: project_id={project_id}, user_session={user_session}"
        )

        # æŸ¥æ‰¾å¯¹åº”ç„è®¤è¯æµç¨‹
        state = None
        flow_data = None

        log.debug(f"å½“å‰æ‰€æœ‰auth_flows: {list(auth_flows.keys())}")

        # å¦‚æœæŒ‡å®äº†project_idï¼Œå…ˆå°è¯•åŒ¹é…æŒ‡å®ç„é¡¹ç›®
        if project_id:
            log.info(f"å°è¯•åŒ¹é…æŒ‡å®ç„é¡¹ç›®ID: {project_id}")
            for s, data in auth_flows.items():
                if data["project_id"] == project_id:
                    # å¦‚æœæŒ‡å®äº†ç”¨æˆ·ä¼è¯ï¼Œä¼˜å…ˆåŒ¹é…ç›¸åŒä¼è¯ç„æµç¨‹
                    if user_session and data.get("user_session") == user_session:
                        state = s
                        flow_data = data
                        log.info(f"æ‰¾åˆ°åŒ¹é…ç„ç”¨æˆ·ä¼è¯: {s}")
                        break
                    # å¦‚æœæ²¡æœ‰æŒ‡å®ä¼è¯ï¼Œæˆ–æ²¡æ‰¾åˆ°åŒ¹é…ä¼è¯ç„æµç¨‹ï¼Œä½¿ç”¨ç¬¬ä¸€ä¸ªåŒ¹é…é¡¹ç›®IDç„
                    elif not state:
                        state = s
                        flow_data = data
                        log.info(f"æ‰¾åˆ°åŒ¹é…ç„é¡¹ç›®ID: {s}")

        # å¦‚æœæ²¡æœ‰æŒ‡å®é¡¹ç›®IDæˆ–æ²¡æ‰¾åˆ°åŒ¹é…ç„ï¼ŒæŸ¥æ‰¾éœ€è¦è‡ªå¨æ£€æµ‹é¡¹ç›®IDç„æµç¨‹
        if not state:
            log.info("æ²¡æœ‰æ‰¾åˆ°æŒ‡å®é¡¹ç›®ç„æµç¨‹ï¼ŒæŸ¥æ‰¾è‡ªå¨æ£€æµ‹æµç¨‹")
            # é¦–å…ˆå°è¯•æ‰¾åˆ°å·²å®Œæˆç„æµç¨‹ï¼ˆæœ‰æˆæƒç ç„ï¼‰
            completed_flows = []
            for s, data in auth_flows.items():
                if data.get("auto_project_detection", False):
                    if user_session and data.get("user_session") == user_session:
                        if data.get("code"):  # ä¼˜å…ˆé€‰æ‹©å·²å®Œæˆç„
                            completed_flows.append((s, data, data.get("created_at", 0)))

            # å¦‚æœæœ‰å·²å®Œæˆç„æµç¨‹ï¼Œé€‰æ‹©æœ€æ–°ç„
            if completed_flows:
                completed_flows.sort(key=lambda x: x[2], reverse=True)  # æŒ‰æ—¶é—´å€’åº
                state, flow_data, _ = completed_flows[0]
                log.info(f"æ‰¾åˆ°å·²å®Œæˆç„æœ€æ–°è®¤è¯æµç¨‹: {state}")
            else:
                # å¦‚æœæ²¡æœ‰å·²å®Œæˆç„ï¼Œæ‰¾æœ€æ–°ç„æœªå®Œæˆæµç¨‹
                pending_flows = []
                for s, data in auth_flows.items():
                    if data.get("auto_project_detection", False):
                        if user_session and data.get("user_session") == user_session:
                            pending_flows.append((s, data, data.get("created_at", 0)))
                        elif not user_session:
                            pending_flows.append((s, data, data.get("created_at", 0)))

                if pending_flows:
                    pending_flows.sort(key=lambda x: x[2], reverse=True)  # æŒ‰æ—¶é—´å€’åº
                    state, flow_data, _ = pending_flows[0]
                    log.info(f"æ‰¾åˆ°æœ€æ–°ç„å¾…å®Œæˆè®¤è¯æµç¨‹: {state}")

        if not state or not flow_data:
            log.error(f"æœªæ‰¾åˆ°è®¤è¯æµç¨‹: state={state}, flow_dataå­˜åœ¨={bool(flow_data)}")
            log.debug(f"å½“å‰æ‰€æœ‰flow_data: {list(auth_flows.keys())}")
            return {"success": False, "error": "Authentication flow not found. Please click to get an authentication link first."}

        log.info(f"æ‰¾åˆ°è®¤è¯æµç¨‹: state={state}")
        log.info(
            f"flow_dataå†…å®¹: project_id={flow_data.get('project_id')}, auto_project_detection={flow_data.get('auto_project_detection')}"
        )
        log.info(f"ä¼ å…¥ç„project_idå‚æ•°: {project_id}")

        # å¦‚æœéœ€è¦è‡ªå¨æ£€æµ‹é¡¹ç›®IDä¸”æ²¡æœ‰æä¾›é¡¹ç›®ID
        log.info(
            f"æ£€æŸ¥auto_project_detectionæ¡ä»¶: auto_project_detection={flow_data.get('auto_project_detection', False)}, not project_id={not project_id}"
        )
        if flow_data.get("auto_project_detection", False) and not project_id:
            log.info("è·³è¿‡è‡ªå¨æ£€æµ‹é¡¹ç›®IDï¼Œè¿›å…¥ç­‰å¾…é˜¶æ®µ")
        elif not project_id:
            log.info("è¿›å…¥project_idæ£€æŸ¥åˆ†æ”¯")
            project_id = flow_data.get("project_id")
            if not project_id:
                project_id = DEFAULT_PROJECT_ID
                flow_data["project_id"] = project_id
                log.warning(f"ç¼ºå°‘é¡¹ç›®IDï¼Œä½¿ç”¨é»˜è®¤project_id: {project_id}")
        else:
            log.info(f"ä½¿ç”¨æä¾›ç„é¡¹ç›®ID: {project_id}")

        # æ£€æŸ¥æ˜¯å¦å·²ç»æœ‰æˆæƒç 
        log.info("å¼€å§‹æ£€æŸ¥OAuthæˆæƒç ...")
        log.info(f"ç­‰å¾…state={state}ç„æˆæƒå›è°ƒï¼Œå›è°ƒç«¯å£: {flow_data.get('callback_port')}")
        log.info(f"å½“å‰flow_dataç¶æ€: completed={flow_data.get('completed')}, codeå­˜åœ¨={bool(flow_data.get('code'))}")
        max_wait_time = 60  # æœ€å¤ç­‰å¾…60ç§’
        wait_interval = 1  # æ¯ç§’æ£€æŸ¥ä¸€æ¬¡
        waited = 0

        while waited < max_wait_time:
            if flow_data.get("code"):
                log.info(f"æ£€æµ‹åˆ°OAuthæˆæƒç ï¼Œå¼€å§‹å¤„ç†å‡­è¯ (ç­‰å¾…æ—¶é—´: {waited}ç§’)")
                break

            # æ¯5ç§’è¾“å‡ºä¸€æ¬¡æç¤º
            if waited % 5 == 0 and waited > 0:
                log.info(f"ä»åœ¨ç­‰å¾…OAuthæˆæƒ... ({waited}/{max_wait_time}ç§’)")
                log.debug(f"å½“å‰state: {state}, flow_data keys: {list(flow_data.keys())}")

            # å¼‚æ­¥ç­‰å¾…
            await asyncio.sleep(wait_interval)
            waited += wait_interval

            # åˆ·æ–°flow_dataå¼•ç”¨ï¼Œå› ä¸ºå¯èƒ½è¢«å›è°ƒæ›´æ–°äº†
            if state in auth_flows:
                flow_data = auth_flows[state]

        if not flow_data.get("code"):
            log.error(f"ç­‰å¾…OAuthå›è°ƒè¶…æ—¶ï¼Œç­‰å¾…äº†{waited}ç§’")
            return {
                "success": False,
                "error": "OAuth callback timed out. Please ensure you completed authorization in your browser and saw the success page.",
            }

        flow = flow_data["flow"]
        auth_code = flow_data["code"]

        log.info(f"å¼€å§‹ä½¿ç”¨æˆæƒç è·å–å‡­è¯: code={'***' + auth_code[-4:] if auth_code else 'None'}")

        # ä½¿ç”¨è®¤è¯ä»£ç è·å–å‡­è¯
        with _OAuthLibPatcher():
            try:
                log.info("è°ƒç”¨flow.exchange_code...")
                credentials = await flow.exchange_code(auth_code)
                log.info(
                    f"æˆåŸè·å–å‡­è¯ï¼Œtokenå‰ç¼€: {credentials.access_token[:20] if credentials.access_token else 'None'}..."
                )

                log.info(
                    f"æ£€æŸ¥æ˜¯å¦éœ€è¦é¡¹ç›®æ£€æµ‹: auto_project_detection={flow_data.get('auto_project_detection')}, project_id={project_id}"
                )

                # æ£€æŸ¥å‡­è¯æ¨¡å¼
                cred_mode = flow_data.get("mode", "code_assist") if flow_data.get("mode") else mode
                if cred_mode == "omni":
                    log.info("Omniæ¨¡å¼ï¼ä»APIè·å–project_id...")
                    # ä½¿ç”¨APIè·å–project_id
                    omni_url = await get_ogw_api_url()
                    project_id, subscription_tier = await fetch_project_id_and_tier(
                        credentials.access_token,
                        OGW_USER_AGENT,
                        omni_url
                    )
                    if project_id:
                        log.info(f"Successfully fetched project_id from API: {project_id}, tier: {subscription_tier}")
                    else:
                        project_id = DEFAULT_PROJECT_ID
                        log.warning(f"Unable to fetch project_id from API, using default project_id: {project_id}")

                    # ä¿å­˜omniå‡­è¯
                    saved_filename = await save_credentials(credentials, project_id, mode="omni", subscription_tier=subscription_tier)

                    # å‡†å¤‡è¿”å›ç„å‡­è¯æ•°æ®
                    creds_data = _prepare_credentials_data(credentials, project_id, mode="omni", subscription_tier=subscription_tier)

                    # æ¸…ç†ä½¿ç”¨è¿‡ç„æµç¨‹
                    _cleanup_auth_flow_server(state)

                    log.info("Omni OAuthè®¤è¯æˆåŸï¼Œå‡­è¯å·²ä¿å­˜")
                    return {
                        "success": True,
                        "credentials": creds_data,
                        "file_path": saved_filename,
                        "auto_detected_project": False,
                        "mode": "omni",
                    }

                # å¦‚æœéœ€è¦è‡ªå¨æ£€æµ‹é¡¹ç›®IDä¸”æ²¡æœ‰æä¾›é¡¹ç›®IDï¼ˆæ ‡å‡†æ¨¡å¼ï¼‰
                if flow_data.get("auto_project_detection", False) and not project_id:
                    log.info("Standard mode: Fetching project_id from project list...")
                    user_projects = await get_user_projects(credentials)

                    if user_projects:
                        # å¦‚æœåªæœ‰ä¸€ä¸ªé¡¹ç›®ï¼Œè‡ªå¨ä½¿ç”¨
                        if len(user_projects) == 1:
                            project_id = user_projects[0].get("projectId")
                            if project_id:
                                flow_data["project_id"] = project_id
                                log.info(f"è‡ªå¨é€‰æ‹©å”¯ä¸€é¡¹ç›®: {project_id}")
                                log.info("æ­£åœ¨è‡ªå¨å¯ç”¨å¿…éœ€ç„APIæœå¡...")
                                await enable_required_apis(credentials, project_id)
                        # å¦‚æœæœ‰å¤ä¸ªé¡¹ç›®ï¼Œå°è¯•é€‰æ‹©é»˜è®¤é¡¹ç›®
                        else:
                            project_id = await select_default_project(user_projects)
                            if project_id:
                                flow_data["project_id"] = project_id
                                log.info(f"è‡ªå¨é€‰æ‹©é»˜è®¤é¡¹ç›®: {project_id}")
                                log.info("æ­£åœ¨è‡ªå¨å¯ç”¨å¿…éœ€ç„APIæœå¡...")
                                await enable_required_apis(credentials, project_id)
                            else:
                                # è¿”å›é¡¹ç›®åˆ—è¡¨è®©ç”¨æˆ·é€‰æ‹©
                                return {
                                    "success": False,
                                    "error": "Please select one of the following projects",
                                    "requires_project_selection": True,
                                    "available_projects": [
                                        {
                                            "project_id": p.get("projectId"),
                                            "name": p.get("displayName") or p.get("projectId"),
                                            "projectNumber": p.get("projectNumber"),
                                        }
                                        for p in user_projects
                                    ],
                                }
                    else:
                        # å¦‚æœæ— æ³•è·å–é¡¹ç›®åˆ—è¡¨ï¼Œä½¿ç”¨é»˜è®¤project_id
                        project_id = DEFAULT_PROJECT_ID
                        flow_data["project_id"] = project_id
                        log.warning(f"æ— æ³•è·å–é¡¹ç›®åˆ—è¡¨ï¼Œä½¿ç”¨é»˜è®¤project_id: {project_id}")
                elif project_id:
                    # å¦‚æœå·²ç»æœ‰é¡¹ç›®IDï¼ˆæ‰‹å¨æä¾›æˆ–ç¯å¢ƒæ£€æµ‹ï¼‰ï¼Œä¹Ÿå°è¯•å¯ç”¨APIæœå¡
                    log.info("æ­£åœ¨ä¸ºå·²æä¾›ç„é¡¹ç›®IDè‡ªå¨å¯ç”¨å¿…éœ€ç„APIæœå¡...")
                    await enable_required_apis(credentials, project_id)

                # å¦‚æœä»ç„¶æ²¡æœ‰é¡¹ç›®IDï¼Œè¿”å›é”™è¯¯
                if not project_id:
                    project_id = DEFAULT_PROJECT_ID
                    flow_data["project_id"] = project_id
                    log.warning(f"ä»æœªè·å–åˆ°project_idï¼Œä½¿ç”¨é»˜è®¤project_id: {project_id}")

                # ä¿å­˜å‡­è¯
                saved_filename = await save_credentials(credentials, project_id)

                # å‡†å¤‡è¿”å›ç„å‡­è¯æ•°æ®
                creds_data = _prepare_credentials_data(credentials, project_id, mode="code_assist")

                # æ¸…ç†ä½¿ç”¨è¿‡ç„æµç¨‹
                _cleanup_auth_flow_server(state)

                log.info("OAuthè®¤è¯æˆåŸï¼Œå‡­è¯å·²ä¿å­˜")
                return {
                    "success": True,
                    "credentials": creds_data,
                    "file_path": saved_filename,
                    "auto_detected_project": flow_data.get("auto_project_detection", False),
                }

            except Exception as e:
                log.error(f"Failed to retrieve credential: {e}")
                return {"success": False, "error": f"Failed to retrieve credential: {str(e)}"}

    except Exception as e:
        log.error(f"Failed to complete asynchronous auth flow: {e}")
        return {"success": False, "error": str(e)}


async def complete_auth_flow_from_callback_url(
    callback_url: str, project_id: Optional[str] = None, mode: str = "code_assist"
) -> Dict[str, Any]:
    """ä»å›è°ƒURLç›´æ¥å®Œæˆè®¤è¯æµç¨‹ï¼Œæ— éœ€å¯å¨æœ¬åœ°æœå¡å™¨"""
    try:
        log.info(f"Starting authentication from callback URL: {callback_url}")

        # è§£æå›è°ƒURL
        parsed_url = urlparse(callback_url)
        query_params = parse_qs(parsed_url.query)

        # éªŒè¯å¿…è¦å‚æ•°
        if "state" not in query_params or "code" not in query_params:
            return {"success": False, "error": "Callback URL is missing required parameters (state or code)"}

        state = query_params["state"][0]
        code = query_params["code"][0]

        log.info(f"Parsed from URL: state={state}, code=xxx...")

        # æ£€æŸ¥æ˜¯å¦æœ‰å¯¹åº”ç„è®¤è¯æµç¨‹
        if state not in auth_flows:
            return {
                "success": False,
                "error": f"Authentication flow not found. Please start authentication first (state: {state})",
            }

        flow_data = auth_flows[state]
        flow = flow_data["flow"]

        # æ„é€ å›è°ƒURLï¼ˆä½¿ç”¨flowä¸­å­˜å‚¨ç„redirect_uriï¼‰
        redirect_uri = flow.redirect_uri
        log.info(f"Using redirect_uri: {redirect_uri}")

        try:
            # ä½¿ç”¨authorization codeè·å–token
            credentials = await flow.exchange_code(code)
            log.info("Access token retrieved successfully")

            # æ£€æŸ¥å‡­è¯æ¨¡å¼
            cred_mode = flow_data.get("mode", "code_assist") if flow_data.get("mode") else mode
            if cred_mode == "omni":
                log.info("Omni mode (from callback URL): Fetching project_id from API...")
                # ä½¿ç”¨APIè·å–project_id
                omni_url = await get_ogw_api_url()
                project_id, subscription_tier = await fetch_project_id_and_tier(
                    credentials.access_token,
                    OGW_USER_AGENT,
                    omni_url
                )
                if project_id:
                    log.info(f"Successfully fetched project_id from API: {project_id}, tier: {subscription_tier}")
                else:
                    project_id = DEFAULT_PROJECT_ID
                    log.warning(f"Unable to fetch project_id from API, using default project_id: {project_id}")

                # ä¿å­˜omniå‡­è¯
                saved_filename = await save_credentials(credentials, project_id, mode="omni", subscription_tier=subscription_tier)

                # å‡†å¤‡è¿”å›ç„å‡­è¯æ•°æ®
                creds_data = _prepare_credentials_data(credentials, project_id, mode="omni", subscription_tier=subscription_tier)

                # æ¸…ç†ä½¿ç”¨è¿‡ç„æµç¨‹
                _cleanup_auth_flow_server(state)

                log.info("Completed Omni OAuth auth from callback URL successfully, credentials saved")
                return {
                    "success": True,
                    "credentials": creds_data,
                    "file_path": saved_filename,
                    "auto_detected_project": False,
                    "mode": "omni",
                }

            # æ ‡å‡†æ¨¡å¼ç„é¡¹ç›®IDå¤„ç†é€»è¾‘
            detected_project_id = None
            auto_detected = False
            subscription_tier = None

            if not project_id:
                # é€è¿‡é¡¹ç›®åˆ—è¡¨è·å–é¡¹ç›®ID
                try:
                    log.info("Standard mode: Fetching project_id from project list...")
                    projects = await get_user_projects(credentials)
                    if projects:
                        if len(projects) == 1:
                            detected_project_id = projects[0]["projectId"]
                            auto_detected = True
                            log.info(f"Automatically detected unique project ID: {detected_project_id}")
                        else:
                            detected_project_id = projects[0]["projectId"]
                            auto_detected = True
                            log.info(
                                f"Detected {len(projects)} projects, automatically selected first: {detected_project_id}"
                            )
                            log.debug(f"Other available projects: {[p['projectId'] for p in projects[1:]]}")
                    else:
                        detected_project_id = DEFAULT_PROJECT_ID
                        auto_detected = False
                        log.warning(f"No accessible projects detected, using default project_id: {detected_project_id}")
                except Exception as e:
                    log.warning(f"Failed to retrieve project list: {e}, using default project_id")
                    detected_project_id = DEFAULT_PROJECT_ID
                    auto_detected = False
            else:
                detected_project_id = project_id

            # å¯ç”¨å¿…éœ€ç„APIæœå¡
            if detected_project_id:
                try:
                    log.info(f"Enabling required API services for project {detected_project_id}...")
                    await enable_required_apis(credentials, detected_project_id)
                except Exception as e:
                    log.warning(f"Failed to enable API services: {e}")

            # ä¿å­˜å‡­è¯
            saved_filename = await save_credentials(credentials, detected_project_id, subscription_tier=subscription_tier)

            # å‡†å¤‡è¿”å›ç„å‡­è¯æ•°æ®
            creds_data = _prepare_credentials_data(credentials, detected_project_id, mode="code_assist", subscription_tier=subscription_tier)

            # æ¸…ç†ä½¿ç”¨è¿‡ç„æµç¨‹
            _cleanup_auth_flow_server(state)

            log.info("Completed OAuth auth from callback URL successfully, credentials saved")
            return {
                "success": True,
                "credentials": creds_data,
                "file_path": saved_filename,
                "auto_detected_project": auto_detected,
            }

        except Exception as e:
            log.error(f"Failed to retrieve credential from callback URL: {e}")
            return {"success": False, "error": f"Failed to retrieve credential: {str(e)}"}

    except Exception as e:
        log.error(f"Failed to complete auth flow from callback URL: {e}")
        return {"success": False, "error": str(e)}


async def save_credentials(creds: Credentials, project_id: str, mode: str = "code_assist", subscription_tier: str = None) -> str:
    """é€è¿‡ç»Ÿä¸€å­˜å‚¨ç³»ç»Ÿä¿å­˜å‡­è¯"""
    # ç”Ÿæˆæ–‡ä»¶åï¼ˆä½¿ç”¨project_idå’Œæ—¶é—´æˆ³ï¼‰
    timestamp = int(time.time())

    # omniæ¨¡å¼ä½¿ç”¨ç‰¹æ®å‰ç¼€
    if mode == "omni":
        filename = f"ag_{project_id}-{timestamp}.json"
    else:
        filename = f"{project_id}-{timestamp}.json"

    # å‡†å¤‡å‡­è¯æ•°æ®
    creds_data = _prepare_credentials_data(creds, project_id, mode, subscription_tier)

    # é€è¿‡å­˜å‚¨é€‚é…å™¨ä¿å­˜
    storage_adapter = await get_storage_adapter()
    success = await storage_adapter.store_credential(filename, creds_data, mode=mode)

    if success:
        # åˆ›å»ºé»˜è®¤ç¶æ€è®°å½•
        try:
            default_state = {
                "error_codes": [],
                "disabled": False,
                "last_success": time.time(),
                "user_email": None,
                "tier": subscription_tier,
            }
            await storage_adapter.update_credential_state(filename, default_state, mode=mode)
            log.info(f"å‡­è¯å’Œç¶æ€å·²ä¿å­˜åˆ°: {filename} (mode={mode})")
        except Exception as e:
            log.warning(f"åˆ›å»ºé»˜è®¤ç¶æ€è®°å½•å¤±è´¥ {filename}: {e}")

        return filename
    else:
        raise Exception(f"ä¿å­˜å‡­è¯å¤±è´¥: {filename}")


def async_shutdown_server(server, port):
    """å¼‚æ­¥å…³é—­OAuthå›è°ƒæœå¡å™¨ï¼Œé¿å…é˜»å¡ä¸»æµç¨‹"""

    def shutdown_server_async():
        try:
            # è®¾ç½®ä¸€ä¸ªæ ‡å¿—æ¥è·Ÿè¸ªå…³é—­ç¶æ€
            shutdown_completed = threading.Event()

            def do_shutdown():
                try:
                    server.shutdown()
                    server.server_close()
                    shutdown_completed.set()
                    log.info(f"å·²å…³é—­ç«¯å£ {port} ç„OAuthå›è°ƒæœå¡å™¨")
                except Exception as e:
                    shutdown_completed.set()
                    log.debug(f"å…³é—­æœå¡å™¨æ—¶å‡ºé”™: {e}")

            # åœ¨å•ç‹¬çº¿ç¨‹ä¸­æ‰§è¡Œå…³é—­æ“ä½œ
            shutdown_worker = threading.Thread(target=do_shutdown, daemon=True)
            shutdown_worker.start()

            # ç­‰å¾…æœ€å¤5ç§’ï¼Œå¦‚æœè¶…æ—¶å°±æ”¾å¼ƒç­‰å¾…
            if shutdown_completed.wait(timeout=5):
                log.debug(f"ç«¯å£ {port} æœå¡å™¨å…³é—­å®Œæˆ")
            else:
                log.warning(f"ç«¯å£ {port} æœå¡å™¨å…³é—­è¶…æ—¶ï¼Œä½†ä¸é˜»å¡ä¸»æµç¨‹")

        except Exception as e:
            log.debug(f"å¼‚æ­¥å…³é—­æœå¡å™¨æ—¶å‡ºé”™: {e}")

    # åœ¨åå°çº¿ç¨‹ä¸­å…³é—­æœå¡å™¨ï¼Œä¸é˜»å¡ä¸»æµç¨‹
    shutdown_thread = threading.Thread(target=shutdown_server_async, daemon=True)
    shutdown_thread.start()
    log.debug(f"å¼€å§‹å¼‚æ­¥å…³é—­ç«¯å£ {port} ç„OAuthå›è°ƒæœå¡å™¨")


def cleanup_expired_flows():
    """æ¸…ç†è¿‡æœŸç„è®¤è¯æµç¨‹"""
    current_time = time.time()
    EXPIRY_TIME = 600  # 10åˆ†é’Ÿè¿‡æœŸ

    # ç›´æ¥éå†åˆ é™¤ï¼Œé¿å…åˆ›å»ºé¢å¤–åˆ—è¡¨
    states_to_remove = [
        state
        for state, flow_data in auth_flows.items()
        if current_time - flow_data["created_at"] > EXPIRY_TIME
    ]

    # æ‰¹é‡æ¸…ç†ï¼Œæé«˜æ•ˆç‡
    cleaned_count = 0
    for state in states_to_remove:
        flow_data = auth_flows.get(state)
        if flow_data:
            # å¿«é€Ÿå…³é—­å¯èƒ½å­˜åœ¨ç„æœå¡å™¨
            try:
                if flow_data.get("server"):
                    server = flow_data["server"]
                    port = flow_data.get("callback_port")
                    async_shutdown_server(server, port)
            except Exception as e:
                log.debug(f"æ¸…ç†è¿‡æœŸæµç¨‹æ—¶å¯å¨å¼‚æ­¥å…³é—­æœå¡å™¨å¤±è´¥: {e}")

            # æ˜¾å¼æ¸…ç†æµç¨‹æ•°æ®ï¼Œé‡æ”¾å†…å­˜
            flow_data.clear()
            del auth_flows[state]
            cleaned_count += 1

    if cleaned_count > 0:
        log.info(f"æ¸…ç†äº† {cleaned_count} ä¸ªè¿‡æœŸç„è®¤è¯æµç¨‹")

    # æ›´ç§¯æç„åƒåœ¾å›æ”¶è§¦å‘æ¡ä»¶
    if len(auth_flows) > 20:  # é™ä½é˜ˆå€¼
        import gc

        gc.collect()
        log.debug(f"è§¦å‘åƒåœ¾å›æ”¶ï¼Œå½“å‰æ´»è·ƒè®¤è¯æµç¨‹æ•°: {len(auth_flows)}")


def get_auth_status(project_id: str) -> Dict[str, Any]:
    """è·å–è®¤è¯ç¶æ€"""
    for state, flow_data in auth_flows.items():
        if flow_data["project_id"] == project_id:
            return {
                "status": "completed" if flow_data["completed"] else "pending",
                "state": state,
                "created_at": flow_data["created_at"],
            }

    return {"status": "not_found"}


# é‰´æƒåŸèƒ½ - ä½¿ç”¨æ›´å°ç„æ•°æ®ç»“æ„
auth_tokens = {}  # å­˜å‚¨æœ‰æ•ˆç„è®¤è¯ä»¤ç‰Œ
TOKEN_EXPIRY = 3600  # 1å°æ—¶ä»¤ç‰Œè¿‡æœŸæ—¶é—´


async def verify_password(password: str) -> bool:
    """éªŒè¯å¯†ç ï¼ˆé¢æ¿ç™»å½•ä½¿ç”¨ï¼‰"""
    from config import get_panel_password

    correct_password = await get_panel_password()
    return password == correct_password
