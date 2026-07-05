"""
å‡­è¯ç®¡ç†å™¨
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from log import log

from omni_gateway.google_oauth_api import Credentials
from omni_gateway.storage_adapter import get_storage_adapter

class CredentialManager:
    """
    ç»Ÿä¸€å‡­è¯ç®¡ç†å™¨
    æ‰€æœ‰å­˜å‚¨æ“ä½œé€è¿‡storage_adapterè¿›è¡Œ
    """

    def __init__(self):
        # æ ¸å¿ƒç¶æ€
        self._initialized = False
        self._storage_adapter = None

        # å¹¶å‘æ§åˆ¶ï¼ˆç®€åŒ–ï¼‰
        # åç«¯æ•°æ®åº“è‡ªè¡Œå¤„ç†å¹¶å‘ï¼Œcredential_manager ä¸å†ä½¿ç”¨æœ¬åœ°é”

    async def _ensure_initialized(self):
        """ç¡®ä¿ç®¡ç†å™¨å·²åˆå§‹åŒ–ï¼ˆå†…éƒ¨ä½¿ç”¨ï¼‰"""
        if not self._initialized or self._storage_adapter is None:
            await self.initialize()

    async def initialize(self):
        """åˆå§‹åŒ–å‡­è¯ç®¡ç†å™¨"""
        if self._initialized and self._storage_adapter is not None:
            return

        # åˆå§‹åŒ–ç»Ÿä¸€å­˜å‚¨é€‚é…å™¨
        self._storage_adapter = await get_storage_adapter()
        self._initialized = True

    async def close(self):
        """æ¸…ç†èµ„æº"""
        log.debug("Closing credential manager...")
        self._initialized = False
        log.debug("Credential manager closed")

    async def get_valid_credential(
        self, mode: str = "code_assist", model_name: Optional[str] = None
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        è·å–æœ‰æ•ˆç„å‡­è¯ - éæœºè´Ÿè½½å‡è¡¡ç‰ˆ
        æ¯æ¬¡éæœºé€‰æ‹©ä¸€ä¸ªå¯ç”¨ç„å‡­è¯ï¼ˆæœªç¦ç”¨ă€æœªå†·å´ă€ç¬¦åˆpreviewè¦æ±‚ï¼‰
        å¦‚æœåˆ·æ–°å¤±è´¥ä¼è‡ªå¨ç¦ç”¨å¤±æ•ˆå‡­è¯å¹¶é‡è¯•è·å–ä¸‹ä¸€ä¸ªå¯ç”¨å‡­è¯

        Args:
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")
            model_name: å®Œæ•´æ¨¡å‹åï¼Œç”¨äºæ¨¡å‹çº§å†·å´æ£€æŸ¥å’Œpreviewç­›é€‰
                       - code_assist: å®Œæ•´æ¨¡å‹å
                                   - åŒ…å« "preview" ç„æ¨¡å‹åªèƒ½ä½¿ç”¨ preview=True ç„å‡­è¯
                                   - ä¸åŒ…å« "preview" ç„æ¨¡å‹ä¼˜å…ˆä½¿ç”¨ preview=False ç„å‡­è¯
                       - omni: å®Œæ•´æ¨¡å‹åï¼ˆå¦‚ "gemini-2.0-flash-exp"ï¼‰
        """
        await self._ensure_initialized()

        # æœ€å¤é‡è¯•3æ¬¡
        max_retries = 3
        for attempt in range(max_retries):
            result = await self._storage_adapter._backend.get_next_available_credential(
                mode=mode, model_name=model_name
            )

            # å¦‚æœæ²¡æœ‰å¯ç”¨å‡­è¯ï¼Œç›´æ¥è¿”å›None
            if not result:
                if attempt == 0:
                    log.warning(f"No available credentials (mode={mode}, model_name={model_name})")
                return None

            filename, credential_data = result

            # Token åˆ·æ–°æ£€æŸ¥
            if await self._should_refresh_token(credential_data):
                log.debug(f"Token needs to be refreshed - File: {filename} (mode = {mode})")
                refreshed_data = await self._refresh_token(credential_data, filename, mode=mode)
                if refreshed_data:
                    # åˆ·æ–°æˆåŸï¼Œè¿”å›å‡­è¯
                    credential_data = refreshed_data
                    log.debug(f"Token successfully refreshed: {filename} (mode = {mode})")
                    return filename, credential_data
                else:
                    # åˆ·æ–°å¤±è´¥ï¼ˆ_refresh_tokenå†…éƒ¨å·²è‡ªå¨ç¦ç”¨å¤±æ•ˆå‡­è¯ï¼‰
                    log.warning(f"Token refresh failed, attempt to get next credentials: {filename} (mode = {mode}, attempt = {attempt+1}/{max_retries})")
                    # ç»§ç»­å¾ªç¯ï¼Œå°è¯•è·å–ä¸‹ä¸€ä¸ªå¯ç”¨å‡­è¯
                    continue
            else:
                # Tokenæœ‰æ•ˆï¼Œç›´æ¥è¿”å›
                return filename, credential_data

        # é‡è¯•æ¬¡æ•°ç”¨å°½
        log.error(f"No available credentials after {max_retries} retries (mode={mode}, model_name={model_name})")
        return None

    async def get_unified_mode_and_credential(
        self, model_name: Optional[str] = None
    ) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        Get unified credential and its mode ("omni").
        Returns (mode, filename, credential_data)
        """
        await self._ensure_initialized()
        
        # Check omni active credentials
        anti_res = await self._storage_adapter._backend.get_next_available_credential(
            mode="omni", model_name=model_name
        )
        if not anti_res:
            log.warning("No active credentials found in Omni mode")
            return None
            
        filename, credential_data = anti_res
        selected_mode = "omni"
        
        # Token refresh check
        if await self._should_refresh_token(credential_data):
            refreshed_data = await self._refresh_token(credential_data, filename, mode=selected_mode)
            if refreshed_data:
                credential_data = refreshed_data
            else:
                return None
                    
        return selected_mode, filename, credential_data

    async def add_credential(self, credential_name: str, credential_data: Dict[str, Any]):
        """
        æ–°å¢æˆ–æ›´æ–°ä¸€ä¸ªå‡­è¯
        å­˜å‚¨å±‚ä¼è‡ªå¨å¤„ç†è½®æ¢é¡ºåº
        """
        await self._ensure_initialized()
        await self._storage_adapter.store_credential(credential_name, credential_data)
        log.info(f"Credential added/updated: {credential_name}")

    async def add_omni_credential(self, credential_name: str, credential_data: Dict[str, Any]):
        """
        æ–°å¢æˆ–æ›´æ–°ä¸€ä¸ªOmniå‡­è¯
        å­˜å‚¨å±‚ä¼è‡ªå¨å¤„ç†è½®æ¢é¡ºåº
        """
        await self._ensure_initialized()
        await self._storage_adapter.store_credential(credential_name, credential_data, mode="omni")
        log.info(f"Omni credential added/updated: {credential_name}")

    async def remove_credential(self, credential_name: str, mode: str = "code_assist") -> bool:
        """åˆ é™¤ä¸€ä¸ªå‡­è¯"""
        await self._ensure_initialized()
        try:
            await self._storage_adapter.delete_credential(credential_name, mode=mode)
            log.info(f"Credential removed: {credential_name} (mode={mode})")
            return True
        except Exception as e:
            log.error(f"Error removing credential {credential_name}: {e}")
            return False

    async def update_credential_state(self, credential_name: str, state_updates: Dict[str, Any], mode: str = "code_assist"):
        """æ›´æ–°å‡­è¯ç¶æ€"""
        log.debug(f"[CredMgr] update_credential_state Start: credential_name = {credential_name}, state_updates = {state_updates}, mode = {mode}")
        log.debug(f"[CredMgr] Calling_ensure_initialized...")
        await self._ensure_initialized()
        log.debug(f"[CredMgr]_ensure_initialized Done")
        try:
            log.debug(f"[CredMgr] Calling storage_adapter.update_credential_state...")
            success = await self._storage_adapter.update_credential_state(
                credential_name, state_updates, mode=mode
            )
            log.debug(f"[CredMgr] storage_adapter.update_credential_state returned: {success}")
            if success:
                log.debug(f"Updated credential state: {credential_name} (mode={mode})")
            else:
                log.warning(f"Failed to update credential state: {credential_name} (mode={mode})")
            return success
        except Exception as e:
            log.error(f"Error updating credential state {credential_name}: {e}")
            return False

    async def set_cred_disabled(self, credential_name: str, disabled: bool, mode: str = "code_assist"):
        """è®¾ç½®å‡­è¯ç„å¯ç”¨/ç¦ç”¨ç¶æ€"""
        try:
            log.info(f"[CredMgr] set_cred_disabled Start: credential_name = {credential_name}, disabled = {disabled}, mode = {mode}")
            success = await self.update_credential_state(
                credential_name, {"disabled": disabled}, mode=mode
            )
            log.info(f"[CredMgr] update_credential_state returned: success = {success}")
            if success:
                action = "disabled" if disabled else "enabled"
                log.info(f"Credential {action}: {credential_name} (mode={mode})")
            else:
                log.warning(f"[CredMgr] Failed to set disable status: credential_name = {credential_name}, disabled = {disabled}")
            return success
        except Exception as e:
            log.error(f"Error setting credential disabled state {credential_name}: {e}")
            return False

    async def get_creds_status(self) -> Dict[str, Dict[str, Any]]:
        """è·å–æ‰€æœ‰å‡­è¯ç„ç¶æ€"""
        await self._ensure_initialized()
        try:
            return await self._storage_adapter.get_all_credential_states()
        except Exception as e:
            log.error(f"Error getting credential statuses: {e}")
            return {}

    async def get_creds_summary(self) -> List[Dict[str, Any]]:
        """
        è·å–æ‰€æœ‰å‡­è¯ç„æ‘˜è¦ä¿¡æ¯ï¼ˆè½»é‡çº§ï¼Œä¸åŒ…å«å®Œæ•´å‡­è¯æ•°æ®ï¼‰
        ä½¿ç”¨åç«¯ç„é«˜æ€§èƒ½æŸ¥è¯¢
        """
        await self._ensure_initialized()
        try:
            return await self._storage_adapter._backend.get_credentials_summary()
        except Exception as e:
            log.error(f"Error getting credentials summary: {e}")
            return []

    async def get_or_fetch_user_email(self, credential_name: str, mode: str = "code_assist") -> Optional[str]:
        """è·å–æˆ–è·å–ç”¨æˆ·é‚®ç®±åœ°å€"""
        try:
            # ç¡®ä¿å·²åˆå§‹åŒ–
            await self._ensure_initialized()
            
            # ä»ç¶æ€ä¸­è·å–ç¼“å­˜ç„é‚®ç®±
            state = await self._storage_adapter.get_credential_state(credential_name, mode=mode)
            cached_email = state.get("user_email") if state else None

            if cached_email:
                return cached_email

            # å¦‚æœæ²¡æœ‰ç¼“å­˜ï¼Œä»å‡­è¯æ•°æ®è·å–
            credential_data = await self._storage_adapter.get_credential(credential_name, mode=mode)
            if not credential_data:
                return None

            # åˆ›å»ºå‡­è¯å¯¹è±¡å¹¶è‡ªå¨åˆ·æ–° token
            from .google_oauth_api import Credentials, get_user_email

            credentials = Credentials.from_dict(credential_data)
            if not credentials:
                return None

            # è‡ªå¨åˆ·æ–° tokenï¼ˆå¦‚æœéœ€è¦ï¼‰
            token_refreshed = await credentials.refresh_if_needed()

            # å¦‚æœ token è¢«åˆ·æ–°äº†ï¼Œæ›´æ–°å­˜å‚¨
            if token_refreshed:
                log.info(f"Token automatically refreshed: {credential_name} (mode = {mode})")
                updated_data = credentials.to_dict()
                await self._storage_adapter.store_credential(credential_name, updated_data, mode=mode)

            # è·å–é‚®ç®±
            email = await get_user_email(credentials)

            if email:
                # ç¼“å­˜é‚®ç®±åœ°å€
                await self._storage_adapter.update_credential_state(
                    credential_name, {"user_email": email}, mode=mode
                )
                return email

            return None

        except Exception as e:
            log.error(f"Error fetching user email for {credential_name}: {e}")
            return None

    async def record_api_call_result(
        self,
        credential_name: str,
        success: bool,
        error_code: Optional[int] = None,
        cooldown_until: Optional[float] = None,
        mode: str = "code_assist",
        model_name: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """
        è®°å½•APIè°ƒç”¨ç»“æœ

        Args:
            credential_name: å‡­è¯åç§°
            success: æ˜¯å¦æˆåŸ
            error_code: é”™è¯¯ç ï¼ˆå¦‚æœå¤±è´¥ï¼‰
            cooldown_until: å†·å´æˆªæ­¢æ—¶é—´æˆ³ï¼ˆUnixæ—¶é—´æˆ³ï¼Œé’ˆå¯¹429 QUOTA_EXHAUSTEDï¼‰
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")
            model_name: æ¨¡å‹åï¼ˆç”¨äºè®¾ç½®æ¨¡å‹çº§å†·å´ï¼‰
            error_message: é”™è¯¯ä¿¡æ¯ï¼ˆå¦‚æœå¤±è´¥ï¼‰
        """
        await self._ensure_initialized()
        try:
            if success:
            # æ¡ä»¶å†™å…¥ï¼ä»…å½“å‡­è¯æœ‰é”™è¯¯ç¶æ€æˆ–æ¨¡å‹å†·å´æ—¶æ‰å†™ DBï¼Œé›¶å†…å­˜ç¼“å­˜
            # fire-and-forgetï¼Œä¸é˜»å¡è¯·æ±‚é“¾è·¯
                asyncio.create_task(
                    self._storage_adapter._backend.record_success(
                        credential_name, model_name=model_name, mode=mode
                    )
                )

            elif error_code:
                # è®°å½•é”™è¯¯ç å’Œé”™è¯¯ä¿¡æ¯
                error_messages = {}
                if error_message:
                    error_messages[str(error_code)] = error_message

                state_updates = {
                    "error_codes": [error_code],
                    "error_messages": error_messages,
                }

                await self.update_credential_state(credential_name, state_updates, mode=mode)

                # è®¾ç½®æ¨¡å‹çº§å†·å´
                if cooldown_until is not None and model_name:
                    if hasattr(self._storage_adapter._backend, 'set_model_cooldown'):
                        await self._storage_adapter._backend.set_model_cooldown(
                            credential_name, model_name, cooldown_until, mode=mode
                        )
                        log.info(
                            f"Setting model-level cooldown: {credential_name}, model_name={model_name}, "
                            f"cooldown_until: {datetime.fromtimestamp(cooldown_until, timezone.utc).isoformat()}"
                        )

        except Exception as e:
            log.error(f"Error recording API call result for {credential_name}: {e}")

    async def _should_refresh_token(self, credential_data: Dict[str, Any]) -> bool:
        """æ£€æŸ¥tokenæ˜¯å¦éœ€è¦åˆ·æ–°"""
        try:
            # å¦‚æœæ²¡æœ‰access_tokenæˆ–è¿‡æœŸæ—¶é—´ï¼Œéœ€è¦åˆ·æ–°
            if not credential_data.get("access_token") and not credential_data.get("token"):
                log.debug("No access_token found, refresh required")
                return True

            expiry_str = credential_data.get("expiry")
            if not expiry_str:
                log.debug("No expiration time found, refresh required")
                return True

            # è§£æè¿‡æœŸæ—¶é—´
            try:
                if isinstance(expiry_str, str):
                    if "+" in expiry_str:
                        file_expiry = datetime.fromisoformat(expiry_str)
                    elif expiry_str.endswith("Z"):
                        file_expiry = datetime.fromisoformat(expiry_str.replace("Z", "+00:00"))
                    else:
                        file_expiry = datetime.fromisoformat(expiry_str)
                else:
                    log.debug("Invalid expiration time format, refresh required")
                    return True

                # ç¡®ä¿æ—¶åŒºä¿¡æ¯
                if file_expiry.tzinfo is None:
                    file_expiry = file_expiry.replace(tzinfo=timezone.utc)

                # æ£€æŸ¥æ˜¯å¦è¿˜æœ‰è‡³å°‘5åˆ†é’Ÿæœ‰æ•ˆæœŸ
                now = datetime.now(timezone.utc)
                time_left = (file_expiry - now).total_seconds()

                log.debug(
                    f"Token time check: "
                    f"current UTC time={now.isoformat()}, "
                    f"expiry={file_expiry.isoformat()}, "
                    f"time left={int(time_left/60)}m {int(time_left%60)}s"
                )

                if time_left > 300:  # 5åˆ†é’Ÿç¼“å†²
                    return False
                else:
                    log.debug(f"Token is about to expire ({int(time_left/60)} minutes left) and needs to be refreshed")
                    return True

            except Exception as e:
                log.warning(f"Failed to parse expiration time: {e}, refresh required")
                return True

        except Exception as e:
            log.error(f"Error occurred while checking token expiration: {e}")
            return True

    async def _refresh_token(
        self, credential_data: Dict[str, Any], filename: str, mode: str = "code_assist"
    ) -> Optional[Dict[str, Any]]:
        """åˆ·æ–°tokenå¹¶æ›´æ–°å­˜å‚¨"""
        await self._ensure_initialized()
        try:
            # åˆ›å»ºCredentialså¯¹è±¡
            creds = Credentials.from_dict(credential_data)

            # æ£€æŸ¥æ˜¯å¦å¯ä»¥åˆ·æ–°
            if not creds.refresh_token:
                log.error(f"No refresh_token found, unable to refresh: {filename} (mode={mode})")
                # è‡ªå¨ç¦ç”¨æ²¡æœ‰refresh_tokenç„å‡­è¯
                try:
                    await self.update_credential_state(filename, {"disabled": True}, mode=mode)
                    log.warning(f"Credential automatically disabled (missing refresh_token): {filename}")
                except Exception as e:
                    log.error(f"Failed to disable credential {filename}: {e}")
                return None

            # åˆ·æ–°token
            log.debug(f"Refreshing token: {filename} (mode={mode})")
            await creds.refresh()

            # æ›´æ–°å‡­è¯æ•°æ®
            if creds.access_token:
                credential_data["access_token"] = creds.access_token
                # ä¿æŒå…¼å®¹æ€§
                credential_data["token"] = creds.access_token

            if creds.expires_at:
                credential_data["expiry"] = creds.expires_at.isoformat()

            # ä¿å­˜åˆ°å­˜å‚¨
            await self._storage_adapter.store_credential(filename, credential_data, mode=mode)
            log.info(f"Token refreshed successfully and saved: {filename} (mode = {mode})")

            return credential_data

        except Exception as e:
            error_msg = str(e)
            log.error(f"Token refresh failed {filename} (mode = {mode}): {error_msg}")

            # å°è¯•æå–HTTPç¶æ€ç ï¼ˆTokenErrorå¯èƒ½æºå¸¦status_codeå±æ€§ï¼‰
            status_code = None
            if hasattr(e, 'status_code'):
                status_code = e.status_code

            # æ£€æŸ¥æ˜¯å¦æ˜¯å‡­è¯æ°¸ä¹…å¤±æ•ˆç„é”™è¯¯ï¼ˆåªæœ‰æ˜ç¡®ç„400/403ç­‰æ‰åˆ¤å®ä¸ºæ°¸ä¹…å¤±æ•ˆï¼‰
            is_permanent_failure = self._is_permanent_refresh_failure(error_msg, status_code)

            if is_permanent_failure:
                log.warning(f"Permanent credential failure detected (HTTP {status_code}): {filename}")
                # è®°å½•å¤±æ•ˆç¶æ€
                if status_code:
                    await self.record_api_call_result(filename, False, status_code, mode=mode)
                else:
                    await self.record_api_call_result(filename, False, 400, mode=mode)

                # ç¦ç”¨å¤±æ•ˆå‡­è¯
                try:
                    # ç›´æ¥ç¦ç”¨è¯¥å‡­è¯ï¼ˆéæœºé€‰æ‹©æœºåˆ¶ä¼è‡ªå¨è·³è¿‡å®ƒï¼‰
                    disabled_ok = await self.update_credential_state(filename, {"disabled": True}, mode=mode)
                    if disabled_ok:
                        log.warning(f"Permanently failed credential disabled: {filename}")
                    else:
                        log.warning("Failed to disable permanently failed credential, handling will be deferred to higher-level logic")
                except Exception as e2:
                    log.error(f"Error occurred while disabling permanently failed credential {filename}: {e2}")
            else:
                # ç½‘ç»œé”™è¯¯æˆ–å…¶ä»–ä¸´æ—¶æ€§é”™è¯¯ï¼Œä¸å°ç¦å‡­è¯
                log.warning(f"Token refresh failed but not a permanent error (http {status_code}), do not ban credentials: {filename}")

            return None

    def _is_permanent_refresh_failure(self, error_msg: str, status_code: Optional[int] = None) -> bool:
        """
        åˆ¤æ–­æ˜¯å¦æ˜¯å‡­è¯æ°¸ä¹…å¤±æ•ˆç„é”™è¯¯

        Args:
            error_msg: é”™è¯¯ä¿¡æ¯
            status_code: HTTPç¶æ€ç ï¼ˆå¦‚æœæœ‰ï¼‰

        Returns:
            Trueè¡¨ç¤ºå‡­è¯æ°¸ä¹…å¤±æ•ˆåº”å°ç¦ï¼ŒFalseè¡¨ç¤ºä¸´æ—¶é”™è¯¯ä¸åº”å°ç¦
        """
        # ä¼˜å…ˆä½¿ç”¨HTTPç¶æ€ç åˆ¤æ–­
        if status_code is not None:
            # 400/401/403 æ˜ç¡®è¡¨ç¤ºå‡­è¯æœ‰é—®é¢˜ï¼Œåº”è¯¥å°ç¦
            if status_code in [400, 401, 403]:
                log.debug(f"Client error status code {status_code} detected, classifying as a permanent failure")
                return True
            # 500/502/503/504 æ˜¯æœå¡å™¨é”™è¯¯ï¼Œä¸åº”å°ç¦å‡­è¯
            elif status_code in [500, 502, 503, 504]:
                log.debug(f"Server error status code {status_code} detected, should not ban credential")
                return False
            # 429 (é™æµ) ä¸åº”å°ç¦å‡­è¯
            elif status_code == 429:
                log.debug("Rate limit error 429 detected, should not ban credential")
                return False

        # å¦‚æœæ²¡æœ‰ç¶æ€ç ï¼Œå›é€€åˆ°é”™è¯¯ä¿¡æ¯åŒ¹é…ï¼ˆè°¨æ…åˆ¤æ–­ï¼‰
        # åªæœ‰æ˜ç¡®ç„å‡­è¯å¤±æ•ˆé”™è¯¯æ‰åˆ¤å®ä¸ºæ°¸ä¹…å¤±æ•ˆ
        permanent_error_patterns = [
            "invalid_grant",
            "refresh_token_expired",
            "invalid_refresh_token",
            "unauthorized_client",
            "access_denied",
        ]

        error_msg_lower = error_msg.lower()
        for pattern in permanent_error_patterns:
            if pattern.lower() in error_msg_lower:
                log.debug(f"Error message matches permanent failure pattern: {pattern}")
                return True

        # é»˜è®¤è®¤ä¸ºæ˜¯ä¸´æ—¶é”™è¯¯ï¼ˆå¦‚ç½‘ç»œé—®é¢˜ï¼‰ï¼Œä¸åº”å°ç¦å‡­è¯
        log.debug("No explicit permanent failure pattern matched; classifying as a transient error")
        return False

class _CredentialManagerSingleton:
    """å•ä¾‹åŒ…è£…å™¨ï¼Œæ”¯æŒæ‡’å è½½å’Œè‡ªå¨åˆå§‹åŒ–"""

    _instance: Optional[CredentialManager] = None
    _lock = None

    def __init__(self):
        self._manager = None

    async def _get_or_create(self) -> CredentialManager:
        """è·å–æˆ–åˆ›å»ºå•ä¾‹å®ä¾‹ï¼ˆçº¿ç¨‹å®‰å…¨ï¼‰"""
        if self._instance is None:
            # ç®€å•ç„å®ä¾‹åˆ›å»ºï¼ˆå¼‚æ­¥ç¯å¢ƒä¸‹ä¸€èˆ¬ä¸éœ€è¦å¤æ‚ç„é”ï¼‰
            if self._instance is None:
                self._instance = CredentialManager()
                await self._instance.initialize()
                log.debug("CredentialManager singleton initialized")

        return self._instance

    def __getattr__(self, name):
        """ä»£ç†æ‰€æœ‰æ–¹æ³•è°ƒç”¨åˆ°çœŸå®ç„ CredentialManager å®ä¾‹"""
        async def _async_wrapper(*args, **kwargs):
            manager = await self._get_or_create()
            method = getattr(manager, name)
            return await method(*args, **kwargs)

        return _async_wrapper


# å…¨å±€å•ä¾‹å®ä¾‹ - ç›´æ¥å¯¼å…¥å³å¯ä½¿ç”¨
credential_manager = _CredentialManagerSingleton()
