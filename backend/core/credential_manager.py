"""Internal implementation detail."""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from log import log

from core.google_oauth_api import Credentials
from core.storage_adapter import get_storage_adapter

class CredentialManager:
    """Internal implementation detail."""

    def __init__(self):

        self._initialized = False
        self._storage_adapter = None




    async def _ensure_initialized(self):
        """Internal implementation detail."""
        if not self._initialized or self._storage_adapter is None:
            await self.initialize()

    async def initialize(self):
        """Internal implementation detail."""
        if self._initialized and self._storage_adapter is not None:
            return


        self._storage_adapter = await get_storage_adapter()
        self._initialized = True

    async def close(self):
        """Internal implementation detail."""
        log.debug("Closing credential manager...")
        self._initialized = False
        log.debug("Credential manager closed")

    async def get_valid_credential(
        self, mode: str = "code_assist", model_name: Optional[str] = None
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Internal implementation detail."""
        await self._ensure_initialized()


        max_retries = 3
        for attempt in range(max_retries):
            result = await self._storage_adapter._backend.get_next_available_credential(
                mode=mode, model_name=model_name
            )


            if not result:
                if attempt == 0:
                    log.warning(f"No available credentials (mode={mode}, model_name={model_name})")
                return None

            filename, credential_data = result


            if await self._should_refresh_token(credential_data):
                log.debug(f"Token needs to be refreshed - File: {filename} (mode = {mode})")
                refreshed_data = await self._refresh_token(credential_data, filename, mode=mode)
                if refreshed_data:

                    credential_data = refreshed_data
                    log.debug(f"Token successfully refreshed: {filename} (mode = {mode})")
                    return filename, credential_data
                else:

                    log.warning(f"Token refresh failed, attempt to get next credentials: {filename} (mode = {mode}, attempt = {attempt+1}/{max_retries})")

                    continue
            else:

                return filename, credential_data


        log.error(f"No available credentials after {max_retries} retries (mode={mode}, model_name={model_name})")
        return None

    async def get_unified_mode_and_credential(
        self, model_name: Optional[str] = None
    ) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        Get unified credential and its mode ("primary").
        Returns (mode, filename, credential_data)
        """
        await self._ensure_initialized()

        # Check primary active credentials
        anti_res = await self._storage_adapter._backend.get_next_available_credential(
            mode="primary", model_name=model_name
        )
        if not anti_res:
            log.warning("No active provider credentials found")
            return None

        filename, credential_data = anti_res
        selected_mode = "primary"

        # Token refresh check
        if await self._should_refresh_token(credential_data):
            refreshed_data = await self._refresh_token(credential_data, filename, mode=selected_mode)
            if refreshed_data:
                credential_data = refreshed_data
            else:
                return None

        return selected_mode, filename, credential_data

    async def add_credential(self, credential_name: str, credential_data: Dict[str, Any]):
        """Internal implementation detail."""
        await self._ensure_initialized()
        await self._storage_adapter.store_credential(credential_name, credential_data)
        log.info(f"Credential added/updated: {credential_name}")

    async def add_primary_credential(self, credential_name: str, credential_data: Dict[str, Any]):
        """Internal implementation detail."""
        await self._ensure_initialized()
        await self._storage_adapter.store_credential(credential_name, credential_data, mode="primary")
        log.info(f"Provider credential added/updated: {credential_name}")

    async def remove_credential(self, credential_name: str, mode: str = "code_assist") -> bool:
        """Internal implementation detail."""
        await self._ensure_initialized()
        try:
            await self._storage_adapter.delete_credential(credential_name, mode=mode)
            log.info(f"Credential removed: {credential_name} (mode={mode})")
            return True
        except Exception as e:
            log.error(f"Error removing credential {credential_name}: {e}")
            return False

    async def update_credential_state(self, credential_name: str, state_updates: Dict[str, Any], mode: str = "code_assist"):
        """Internal implementation detail."""
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
        """Internal implementation detail."""
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
        """Internal implementation detail."""
        await self._ensure_initialized()
        try:
            return await self._storage_adapter.get_all_credential_states()
        except Exception as e:
            log.error(f"Error getting credential statuses: {e}")
            return {}

    async def get_creds_summary(self) -> List[Dict[str, Any]]:
        """Internal implementation detail."""
        await self._ensure_initialized()
        try:
            return await self._storage_adapter._backend.get_credentials_summary()
        except Exception as e:
            log.error(f"Error getting credentials summary: {e}")
            return []

    async def get_or_fetch_user_email(self, credential_name: str, mode: str = "code_assist") -> Optional[str]:
        """Internal implementation detail."""
        try:

            await self._ensure_initialized()


            state = await self._storage_adapter.get_credential_state(credential_name, mode=mode)
            cached_email = state.get("user_email") if state else None

            if cached_email:
                return cached_email


            credential_data = await self._storage_adapter.get_credential(credential_name, mode=mode)
            if not credential_data:
                return None


            from .google_oauth_api import Credentials, get_user_email

            credentials = Credentials.from_dict(credential_data)
            if not credentials:
                return None


            token_refreshed = await credentials.refresh_if_needed()


            if token_refreshed:
                log.info(f"Token automatically refreshed: {credential_name} (mode = {mode})")
                updated_data = credentials.to_dict()
                await self._storage_adapter.store_credential(credential_name, updated_data, mode=mode)


            email = await get_user_email(credentials)

            if email:

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
        """Internal implementation detail."""
        await self._ensure_initialized()
        try:
            if success:


                asyncio.create_task(
                    self._storage_adapter._backend.record_success(
                        credential_name, model_name=model_name, mode=mode
                    )
                )

            elif error_code:

                error_messages = {}
                if error_message:
                    error_messages[str(error_code)] = error_message

                state_updates = {
                    "error_codes": [error_code],
                    "error_messages": error_messages,
                }

                await self.update_credential_state(credential_name, state_updates, mode=mode)


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
        """Internal implementation detail."""
        try:

            if not credential_data.get("access_token") and not credential_data.get("token"):
                log.debug("No access_token found, refresh required")
                return True

            expiry_str = credential_data.get("expiry")
            if not expiry_str:
                log.debug("No expiration time found, refresh required")
                return True


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


                if file_expiry.tzinfo is None:
                    file_expiry = file_expiry.replace(tzinfo=timezone.utc)


                now = datetime.now(timezone.utc)
                time_left = (file_expiry - now).total_seconds()

                log.debug(
                    f"Token time check: "
                    f"current UTC time={now.isoformat()}, "
                    f"expiry={file_expiry.isoformat()}, "
                    f"time left={int(time_left/60)}m {int(time_left%60)}s"
                )

                if time_left > 300:
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
        """Internal implementation detail."""
        await self._ensure_initialized()
        try:

            creds = Credentials.from_dict(credential_data)


            if not creds.refresh_token:
                log.error(f"No refresh_token found, unable to refresh: {filename} (mode={mode})")

                try:
                    await self.update_credential_state(filename, {"disabled": True}, mode=mode)
                    log.warning(f"Credential automatically disabled (missing refresh_token): {filename}")
                except Exception as e:
                    log.error(f"Failed to disable credential {filename}: {e}")
                return None


            log.debug(f"Refreshing token: {filename} (mode={mode})")
            await creds.refresh()


            if creds.access_token:
                credential_data["access_token"] = creds.access_token

                credential_data["token"] = creds.access_token

            if creds.expires_at:
                credential_data["expiry"] = creds.expires_at.isoformat()


            await self._storage_adapter.store_credential(filename, credential_data, mode=mode)
            log.info(f"Token refreshed successfully and saved: {filename} (mode = {mode})")

            return credential_data

        except Exception as e:
            error_msg = str(e)
            log.error(f"Token refresh failed {filename} (mode = {mode}): {error_msg}")


            status_code = None
            if hasattr(e, 'status_code'):
                status_code = e.status_code


            is_permanent_failure = self._is_permanent_refresh_failure(error_msg, status_code)

            if is_permanent_failure:
                log.warning(f"Permanent credential failure detected (HTTP {status_code}): {filename}")

                if status_code:
                    await self.record_api_call_result(filename, False, status_code, mode=mode)
                else:
                    await self.record_api_call_result(filename, False, 400, mode=mode)


                try:

                    disabled_ok = await self.update_credential_state(filename, {"disabled": True}, mode=mode)
                    if disabled_ok:
                        log.warning(f"Permanently failed credential disabled: {filename}")
                    else:
                        log.warning("Failed to disable permanently failed credential, handling will be deferred to higher-level logic")
                except Exception as e2:
                    log.error(f"Error occurred while disabling permanently failed credential {filename}: {e2}")
            else:

                log.warning(f"Token refresh failed but not a permanent error (http {status_code}), do not ban credentials: {filename}")

            return None

    def _is_permanent_refresh_failure(self, error_msg: str, status_code: Optional[int] = None) -> bool:
        """Internal implementation detail."""

        if status_code is not None:

            if status_code in [400, 401, 403]:
                log.debug(f"Client error status code {status_code} detected, classifying as a permanent failure")
                return True

            elif status_code in [500, 502, 503, 504]:
                log.debug(f"Server error status code {status_code} detected, should not ban credential")
                return False

            elif status_code == 429:
                log.debug("Rate limit error 429 detected, should not ban credential")
                return False



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


        log.debug("No explicit permanent failure pattern matched; classifying as a transient error")
        return False

class _CredentialManagerSingleton:
    """Internal implementation detail."""
    _instance: Optional[CredentialManager] = None
    _lock = None

    def __init__(self):
        self._manager = None

    async def _get_or_create(self) -> CredentialManager:
        """Internal implementation detail."""
        if self._instance is None:

            if self._instance is None:
                self._instance = CredentialManager()
                await self._instance.initialize()
                log.debug("CredentialManager singleton initialized")

        return self._instance

    def __getattr__(self, name):
        """Internal implementation detail."""
        async def _async_wrapper(*args, **kwargs):
            manager = await self._get_or_create()
            method = getattr(manager, name)
            return await method(*args, **kwargs)

        return _async_wrapper



credential_manager = _CredentialManagerSingleton()
