"""
MongoDB å­˜å‚¨ç®¡ç†å™¨
"""

import json
import os
import random
import time
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from log import log


class MongoDBManager:
    """MongoDB æ•°æ®åº“ç®¡ç†å™¨"""

    # ç¶æ€å­—æ®µå¸¸é‡
    STATE_FIELDS = {
        "error_codes",
        "error_messages",
        "disabled",
        "last_success",
        "user_email",
        "model_cooldowns",
        "preview",
        "tier",
        "enable_credit",
    }

    @staticmethod
    def _escape_model_name(model_name: str) -> str:
        """
        è½¬ä¹‰æ¨¡å‹åä¸­ç„ç‚¹å·,é¿å… MongoDB å°†å…¶è§£é‡ä¸ºåµŒå¥—ç»“æ„

        Args:
            model_name: åŸå§‹æ¨¡å‹å (å¦‚ "gemini-2.5-flash")

        Returns:
            è½¬ä¹‰åç„æ¨¡å‹å (å¦‚ "gemini-2-5-flash")
        """
        return model_name.replace(".", "-")

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._initialized = False

        # å†…å­˜é…ç½®ç¼“å­˜ - åˆå§‹åŒ–æ—¶å è½½ä¸€æ¬¡
        self._config_cache: Dict[str, Any] = {}
        self._config_loaded = False

        # Redis ç¼“å­˜ï¼ˆä»…å½“ OGW_REDIS_URL ç¯å¢ƒå˜é‡å­˜åœ¨æ—¶å¯ç”¨ï¼‰
        self._redis = None
        self._redis_enabled: bool = False

    async def initialize(self) -> None:
        """åˆå§‹åŒ– MongoDB è¿æ¥"""
        if self._initialized:
            return

        try:
            mongodb_uri = os.getenv("OGW_MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("OGW_MONGODB_URI environment variable not set")

            database_name = os.getenv("OGW_MONGODB_DATABASE", "omni_gateway")

            self._client = AsyncIOMotorClient(mongodb_uri)
            self._db = self._client[database_name]

            # æµ‹è¯•è¿æ¥
            await self._db.command("ping")

            # åˆ›å»ºç´¢å¼•
            await self._create_indexes()

            # å è½½é…ç½®åˆ°å†…å­˜
            await self._load_config_cache()

            self._initialized = True
            log.info(f"MongoDB storage initialized (database: {database_name})")

            # å°è¯•åˆå§‹åŒ– Redisï¼ˆå¯é€‰ï¼‰
            await self._init_redis()

        except Exception as e:
            log.error(f"Error initializing MongoDB: {e}")
            raise

    async def _create_indexes(self):
        """
        åˆ›å»ºç´¢å¼•
        """
        from pymongo import IndexModel, ASCENDING

        credentials_collection = self._db["credentials"]
        omni_credentials_collection = self._db["omni_credentials"]

        # ===== Code Assist å‡­è¯ç´¢å¼• =====
        code_assist_indexes = [
            # å”¯ä¸€ç´¢å¼• - ç”¨äºæ‰€æœ‰æŒ‰æ–‡ä»¶åç„ç²¾ç¡®æŸ¥è¯¢
            IndexModel([("filename", ASCENDING)], unique=True, name="idx_filename_unique"),

            # å¤åˆç´¢å¼• - ç”¨äº get_next_available_credential å’Œ get_available_credentials_list
            # æŸ¥è¯¢æ¨¡å¼: {disabled: False} + sort by rotation_order
            IndexModel(
                [("disabled", ASCENDING), ("rotation_order", ASCENDING)],
                name="idx_disabled_rotation"
            ),

            # å•å­—æ®µç´¢å¼• - ç”¨äº get_credentials_summary ç„é”™è¯¯ç­›é€‰
            IndexModel([("error_codes", ASCENDING)], name="idx_error_codes"),

            # å•å­—æ®µç´¢å¼• - ç”¨äº get_duplicate_credentials_by_email ç„å»é‡æŸ¥è¯¢
            IndexModel([("user_email", ASCENDING)], name="idx_user_email"),
        ]

        # ===== Omni å‡­è¯ç´¢å¼• =====
        omni_indexes = [
            # å”¯ä¸€ç´¢å¼•
            IndexModel([("filename", ASCENDING)], unique=True, name="idx_filename_unique"),
            
            # å¤åˆç´¢å¼• - æŸ¥è¯¢æ¨¡å¼: {disabled: False} + sort by rotation_order
            # æŸ¥è¯¢æ¨¡å¼: {disabled: False} + å¯é€‰ sort by rotation_order
            IndexModel(
                [("disabled", ASCENDING), ("rotation_order", ASCENDING)],
                name="idx_disabled_rotation"
            ),
            
            # å•å­—æ®µç´¢å¼• - é”™è¯¯ç­›é€‰
            IndexModel([("error_codes", ASCENDING)], name="idx_error_codes"),
            
            # å•å­—æ®µç´¢å¼• - å»é‡æŸ¥è¯¢
            IndexModel([("user_email", ASCENDING)], name="idx_user_email"),
        ]

        # å¹¶è¡Œåˆ›å»ºæ–°ç´¢å¼•
        try:
            await credentials_collection.create_indexes(code_assist_indexes)
            await omni_credentials_collection.create_indexes(omni_indexes)
            log.debug("MongoDB indexes created successfully")
        except Exception as e:
            # å¦‚æœç´¢å¼•å·²å­˜åœ¨ï¼Œå¿½ç•¥é”™è¯¯
            if "already exists" not in str(e).lower():
                log.warning(f"Index creation warning: {e}")

    async def _load_config_cache(self):
        """å è½½é…ç½®åˆ°å†…å­˜ç¼“å­˜ï¼ˆä»…åœ¨åˆå§‹åŒ–æ—¶è°ƒç”¨ä¸€æ¬¡ï¼‰"""
        if self._config_loaded:
            return

        try:
            config_collection = self._db["config"]
            cursor = config_collection.find({})

            async for doc in cursor:
                self._config_cache[doc["key"]] = doc.get("value")

            self._config_loaded = True
            log.debug(f"Loaded {len(self._config_cache)} config items into cache")

        except Exception as e:
            log.error(f"Error loading config cache: {e}")
            self._config_cache = {}

    # ============ Redis ç¼“å­˜ï¼ˆå¯é€‰ï¼Œä»…å½“ OGW_REDIS_URL å­˜åœ¨æ—¶å¯ç”¨ï¼‰============

    async def _init_redis(self) -> None:
        """åˆå§‹åŒ– Redis è¿æ¥å¹¶é‡å»ºå‡­è¯æ± ç¼“å­˜ï¼ˆè‹¥ OGW_REDIS_URL å­˜åœ¨ï¼‰"""
        redis_url = os.getenv("OGW_REDIS_URL")
        if not redis_url:
            return

        try:
            import redis.asyncio as aioredis  # type: ignore
        except ImportError:
            log.warning("redis package not installed, Redis cache disabled. Run: pip install redis")
            return

        try:
            self._redis = aioredis.from_url(redis_url, decode_responses=True)
            await self._redis.ping()
            self._redis_enabled = True
            log.info("Redis connected, rebuilding credential pool cache...")

            # å¹¶è¡Œé‡å»ºä¸¤ä¸ª mode ç„ç¼“å­˜åé…ç½®ç¼“å­˜
            import asyncio
            await asyncio.gather(
                self._rebuild_redis_cache("code_assist"),
                self._rebuild_redis_cache("omni"),
                self._load_config_to_redis(),
            )
            log.info("Redis credential pool cache ready")
        except Exception as e:
            log.warning(f"Redis init failed, falling back to MongoDB-only mode: {e}")
            self._redis = None
            self._redis_enabled = False

    # ---- Redis key å·¥å…· ----

    def _rk_avail(self, mode: str) -> str:
        """æ‰€æœ‰æœªç¦ç”¨å‡­è¯ç„ Redis Set key"""
        return f"code_assist:avail:{mode}"

    def _rk_tier(self, mode: str, tier: str) -> str:
        """æŒ‰ tier åˆ†æ¡¶ç„æœªç¦ç”¨å‡­è¯ Redis Set key"""
        return f"code_assist:tier:{mode}:{tier}"

    def _rk_preview(self, mode: str) -> str:
        """preview=True å‡­è¯ç„ Redis Set key"""
        return f"code_assist:preview:{mode}"

    def _rk_cd(self, mode: str, filename: str, escaped_model: str) -> str:
        """æ¨¡å‹å†·å´ Redis keyï¼ˆå¸¦ TTLï¼‰"""
        return f"code_assist:cd:{mode}:{filename}:{escaped_model}"

    # ---- Redis ç¼“å­˜ç»´æ¤ ----

    async def _rebuild_redis_cache(self, mode: str) -> None:
        """
        ä» MongoDB é‡å»ºæŒ‡å® mode ç„ Redis å‡­è¯æ± ç¼“å­˜ă€‚

        ä½¿ç”¨ä¸´æ—¶ key + RENAME åŸå­æ›¿æ¢
        """
        if not self._redis:
            return
        try:
            collection = self._db[self._get_collection_name(mode)]
            # åŒæ—¶æ•å½± model_cooldownsă€tieră€previewï¼Œä»¥ä¾¿é‡å»ºç¼“å­˜
            projection: Dict[str, Any] = {"filename": 1, "disabled": 1, "model_cooldowns": 1, "tier": 1, "preview": 1, "_id": 0}

            avail: List[str] = []
            tier_buckets: Dict[str, List[str]] = {}  # tier -> [filename, ...]
            preview_members: List[str] = []
            cooldown_entries: List[tuple] = []  # (cd_key, ttl_seconds, value)
            current_time = time.time()

            async for doc in collection.find({}, projection=projection):
                if not doc.get("disabled", False):
                    filename = doc["filename"]
                    avail.append(filename)

                    # æŒ‰ tier åˆ†æ¡¶
                    tier = doc.get("tier") or "pro"
                    tier_buckets.setdefault(tier, []).append(filename)

                    # preview åˆ†æ¡¶ï¼ˆä»… code_assistï¼‰
                    if mode == "code_assist" and doc.get("preview", True):
                        preview_members.append(filename)

                    # æ”¶é›†æœªè¿‡æœŸç„æ¨¡å‹å†·å´ï¼Œé‡å»º Redis TTL Key
                    model_cooldowns = doc.get("model_cooldowns") or {}
                    for escaped_model, cooldown_until in model_cooldowns.items():
                        if isinstance(cooldown_until, (int, float)) and cooldown_until > current_time:
                            ttl = int(cooldown_until - current_time)
                            if ttl > 0:
                                cd_key = self._rk_cd(mode, filename, escaped_model)
                                cooldown_entries.append((cd_key, ttl, str(cooldown_until)))

            tmp_avail = self._rk_avail(mode) + ":tmp"

            pipe = self._redis.pipeline()
            # å…ˆå†™ä¸´æ—¶ keyï¼ˆæ­¤æ—¶æ­£å¼ key ä»å®Œæ•´å¯ç”¨ï¼‰
            pipe.delete(tmp_avail)
            if avail:
                pipe.sadd(tmp_avail, *avail)
            await pipe.execute()

            # RENAME æ˜¯åŸå­æ“ä½œï¼ç¬é—´åˆ‡æ¢ï¼Œä¸å­˜åœ¨ç©ºçª—
            pipe2 = self._redis.pipeline()
            if avail:
                pipe2.rename(tmp_avail, self._rk_avail(mode))
            else:
                pipe2.delete(self._rk_avail(mode))
                pipe2.delete(tmp_avail)
            await pipe2.execute()

            # é‡å»º tier åˆ†æ¡¶ Setï¼ˆåŸå­æ›¿æ¢ï¼‰
            all_tiers = ("free", "pro", "ultra")
            pipe3 = self._redis.pipeline()
            for tier in all_tiers:
                tier_key = self._rk_tier(mode, tier)
                tmp_tier_key = tier_key + ":tmp"
                pipe3.delete(tmp_tier_key)
                members = tier_buckets.get(tier, [])
                if members:
                    pipe3.sadd(tmp_tier_key, *members)
            await pipe3.execute()

            pipe4 = self._redis.pipeline()
            for tier in all_tiers:
                tier_key = self._rk_tier(mode, tier)
                tmp_tier_key = tier_key + ":tmp"
                members = tier_buckets.get(tier, [])
                if members:
                    pipe4.rename(tmp_tier_key, tier_key)
                else:
                    pipe4.delete(tier_key)
                    pipe4.delete(tmp_tier_key)
            await pipe4.execute()

            # é‡å»º preview åˆ†æ¡¶ï¼ˆä»… code_assistï¼‰
            preview_key = self._rk_preview(mode)
            tmp_preview_key = preview_key + ":tmp"
            pipe5 = self._redis.pipeline()
            pipe5.delete(tmp_preview_key)
            if preview_members:
                pipe5.sadd(tmp_preview_key, *preview_members)
            await pipe5.execute()
            pipe6 = self._redis.pipeline()
            if preview_members:
                pipe6.rename(tmp_preview_key, preview_key)
            else:
                pipe6.delete(preview_key)
                pipe6.delete(tmp_preview_key)
            await pipe6.execute()

            # æ‰¹é‡æ¢å¤æœªè¿‡æœŸç„æ¨¡å‹å†·å´ TTL Key
            if cooldown_entries:
                pipe7 = self._redis.pipeline()
                for cd_key, ttl, value in cooldown_entries:
                    pipe7.setex(cd_key, ttl, value)
                await pipe7.execute()

            log.debug(
                f"Redis cache rebuilt [{mode}]: {len(avail)} avail, "
                f"tiers={{{', '.join(f'{t}:{len(tier_buckets.get(t, []))}' for t in all_tiers)}}}, "
                f"preview={len(preview_members)}, "
                f"{len(cooldown_entries)} cooldown key(s) restored"
            )
        except Exception as e:
            log.warning(f"Redis rebuild cache error [{mode}]: {e}")

    async def _redis_add_cred(self, mode: str, filename: str, tier: str = "pro", preview: bool = True) -> None:
        """å°†å‡­è¯å å…¥ Redis å¯ç”¨æ± åå¯¹åº” tier åˆ†æ¡¶ă€preview åˆ†æ¡¶"""
        if not self._redis_enabled:
            return
        try:
            pipe = self._redis.pipeline()
            pipe.sadd(self._rk_avail(mode), filename)
            pipe.sadd(self._rk_tier(mode, tier), filename)
            if mode == "code_assist" and preview:
                pipe.sadd(self._rk_preview(mode), filename)
            await pipe.execute()
        except Exception as e:
            log.warning(f"Redis add_cred error: {e}")

    async def _redis_remove_cred(self, mode: str, filename: str, tier: Optional[str] = None) -> None:
        """ä» Redis æ‰€æœ‰æ± ä¸­ç§»é™¤å‡­è¯"""
        if not self._redis_enabled:
            return
        try:
            pipe = self._redis.pipeline()
            pipe.srem(self._rk_avail(mode), filename)
            if tier:
                pipe.srem(self._rk_tier(mode, tier), filename)
            else:
                # tier æœªçŸ¥æ—¶ä»æ‰€æœ‰åˆ†æ¡¶ä¸­ç§»é™¤
                for t in ("free", "pro", "ultra"):
                    pipe.srem(self._rk_tier(mode, t), filename)
            pipe.srem(self._rk_preview(mode), filename)
            await pipe.execute()
        except Exception as e:
            log.warning(f"Redis remove_cred error: {e}")

    async def _redis_sync_cred(self, mode: str, filename: str, disabled: bool, tier: str = "pro", preview: bool = True) -> None:
        """æ ¹æ®æœ€æ–°ç¶æ€åŒæ­¥å•ä¸ªå‡­è¯åœ¨ Redis ä¸­ç„é›†åˆæˆå‘˜"""
        if not self._redis_enabled:
            return
        try:
            pipe = self._redis.pipeline()
            if disabled:
                pipe.srem(self._rk_avail(mode), filename)
                for t in ("free", "pro", "ultra"):
                    pipe.srem(self._rk_tier(mode, t), filename)
                pipe.srem(self._rk_preview(mode), filename)
            else:
                pipe.sadd(self._rk_avail(mode), filename)
                pipe.sadd(self._rk_tier(mode, tier), filename)
                if mode == "code_assist" and preview:
                    pipe.sadd(self._rk_preview(mode), filename)
                else:
                    pipe.srem(self._rk_preview(mode), filename)
            await pipe.execute()
        except Exception as e:
            log.warning(f"Redis sync_cred error: {e}")

    async def _get_next_available_from_redis(
        self, mode: str, model_name: Optional[str], exclude_free_tier: bool = False, preview_only: bool = False
    ) -> Optional[tuple]:
        """
        Redis å¿«é€Ÿè·¯å¾„ï¼éæœºå–å€™é€‰å‡­è¯ï¼Œè·³è¿‡å†·å´ä¸­ç„ï¼Œè¿”å› (filename, credential_data)ă€‚
        å¤±è´¥æˆ–æ± ä¸ºç©ºæ—¶è¿”å› Noneï¼Œç”±è°ƒç”¨æ–¹é™çº§åˆ° MongoDBă€‚
        """
        try:
            # é€‰æ‹©å€™é€‰æ± ä¼˜å…ˆçº§ï¼preview_only > exclude_free_tier > å…¨é‡æ± 
            if preview_only and exclude_free_tier:
                # preview ä¸”é freeï¼preview âˆ© (pro âˆª ultra)
                preview_set = await self._redis.smembers(self._rk_preview(mode))
                pro_members = await self._redis.smembers(self._rk_tier(mode, "pro"))
                ultra_members = await self._redis.smembers(self._rk_tier(mode, "ultra"))
                non_free = pro_members | ultra_members
                all_candidates = list(preview_set & non_free)
                if not all_candidates:
                    log.debug(f"[Redis MISS] mode={mode} preview+non-free: no candidates, fallback to MongoDB")
                    return None
                sample_size = min(len(all_candidates), 10)
                candidates = random.sample(all_candidates, sample_size)
            elif preview_only:
                preview_key = self._rk_preview(mode)
                preview_size = await self._redis.scard(preview_key)
                if preview_size == 0:
                    log.debug(f"[Redis MISS] mode={mode} preview_only: pool empty, fallback to MongoDB")
                    return None
                sample_size = min(preview_size, 10)
                candidates = await self._redis.srandmember(preview_key, sample_size)
                if not candidates:
                    return None
            elif exclude_free_tier:
                pro_members = await self._redis.smembers(self._rk_tier(mode, "pro"))
                ultra_members = await self._redis.smembers(self._rk_tier(mode, "ultra"))
                all_candidates = list(pro_members | ultra_members)
                if not all_candidates:
                    log.debug(f"[Redis MISS] mode={mode} exclude_free: no non-free creds, fallback to MongoDB")
                    return None
                sample_size = min(len(all_candidates), 10)
                candidates = random.sample(all_candidates, sample_size)
            else:
                pool_key = self._rk_avail(mode)
                pool_size = await self._redis.scard(pool_key)
                if pool_size == 0:
                    log.debug(f"[Redis MISS] mode={mode} pool_key={pool_key}: pool empty, fallback to MongoDB")
                    return None
                sample_size = min(pool_size, 10)
                candidates = await self._redis.srandmember(pool_key, sample_size)
                if not candidates:
                    return None

            # è¿‡æ»¤å†·å´ä¸­ç„å‡­è¯
            if model_name:
                escaped = self._escape_model_name(model_name)
                for filename in candidates:
                    cd_key = self._rk_cd(mode, filename, escaped)
                    if not await self._redis.exists(cd_key):
                        credential_data = await self.get_credential(filename, mode)
                        if mode == "omni":
                            state = await self.get_credential_state(filename, mode)
                            credential_data = credential_data or {}
                            credential_data["enable_credit"] = bool(state.get("enable_credit", False))
                        log.debug(f"[Redis HIT] mode={mode} model={model_name} -> {filename}")
                        return filename, credential_data
                # æ‰€æœ‰å€™é€‰éƒ½åœ¨å†·å´ä¸­ï¼Œé™çº§åˆ° MongoDB
                log.debug(f"[Redis MISS] mode={mode} model={model_name}: all {len(candidates)} candidates in cooldown, fallback to MongoDB")
                return None
            else:
                filename = candidates[0]
                credential_data = await self.get_credential(filename, mode)
                if mode == "omni":
                    state = await self.get_credential_state(filename, mode)
                    credential_data = credential_data or {}
                    credential_data["enable_credit"] = bool(state.get("enable_credit", False))
                log.debug(f"[Redis HIT] mode={mode} -> {filename}")
                return filename, credential_data
        except Exception as e:
            log.warning(f"Redis get_next_available error: {e}")
            return None

    async def close(self) -> None:
        """å…³é—­ MongoDB è¿æ¥"""
        if self._redis:
            await self._redis.aclose()
            self._redis = None
            self._redis_enabled = False
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
        self._initialized = False
        log.debug("MongoDB storage closed")

    def _ensure_initialized(self):
        """ç¡®ä¿å·²åˆå§‹åŒ–"""
        if not self._initialized:
            raise RuntimeError("MongoDB manager not initialized")

    def _get_collection_name(self, mode: str) -> str:
        """æ ¹æ® mode è·å–å¯¹åº”ç„é›†åˆå"""
        if mode == "omni":
            return "omni_credentials"
        elif mode == "code_assist":
            return "credentials"
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'code_assist' or 'omni'")

    # ============ SQL æ–¹æ³• ============

    async def get_next_available_credential(
        self, mode: str = "code_assist", model_name: Optional[str] = None
    ) -> Optional[tuple[str, Dict[str, Any]]]:
        """
        éæœºè·å–ä¸€ä¸ªå¯ç”¨å‡­è¯ï¼ˆè´Ÿè½½å‡è¡¡ï¼‰
        - æœªç¦ç”¨
        - å¦‚æœæä¾›äº† model_nameï¼Œè¿˜ä¼æ£€æŸ¥æ¨¡å‹çº§å†·å´
        - éæœºé€‰æ‹©

        Args:
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")
            model_name: å®Œæ•´æ¨¡å‹åï¼ˆå¦‚ "gemini-2.0-flash-exp"ï¼‰

        Note:
            - å¼€å¯ Redis æ—¶ï¼åˆ©ç”¨ Redis Set éæœºé€‰å‡­è¯ + TTL key åˆ¤æ–­å†·å´
            - æœªå¼€å¯ Redis æ—¶ï¼ä½¿ç”¨ count + random skip + limit(1)
        """
        self._ensure_initialized()

        # Redis å¿«é€Ÿè·¯å¾„ï¼æ ¹æ®æ¨¡å‹åæ´¾ç”Ÿè¿‡æ»¤æ ‡å¿—ï¼Œç›´æ¥åœ¨ Redis åˆ†æ¡¶ä¸­ç­›é€‰
        if self._redis_enabled:
            model_lower = model_name.lower() if model_name else ""
            exclude_free = False
            preview_only = mode == "code_assist" and "preview" in model_lower
            result = await self._get_next_available_from_redis(
                mode, model_name, exclude_free_tier=exclude_free, preview_only=preview_only
            )
            if result is not None:
                return result
            # result ä¸º Noneï¼æ± ä¸ºç©ºæˆ–æ‰€æœ‰å€™é€‰éƒ½å†·å´ä¸­ï¼Œé™çº§åˆ° MongoDB ä»¥æ‰©å¤§æ ·æœ¬ç©ºé—´
            log.debug(f"[MongoDB fallback] mode={mode} model={model_name}")

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            current_time = time.time()

            # æ„å»ºæ™®é€æŸ¥è¯¢ï¼ˆé¿å… $sample èåˆå¯¼è‡´å…¨é›†åˆæ‰«æï¼‰
            match_query: Dict[str, Any] = {"disabled": False}

            # preview æ¨¡å‹åªå…è®¸ preview=True ç„å‡­è¯
            if mode == "code_assist" and model_name and "preview" in model_name.lower():
                match_query["preview"] = True

            # å†·å´æ£€æŸ¥ï¼ç›´æ¥ç”¨ MongoDB æŸ¥è¯¢è¡¨è¾¾ï¼Œæ— éœ€ $addFields
            if model_name:
                escaped_model_name = self._escape_model_name(model_name)
                field = f"model_cooldowns.{escaped_model_name}"
                match_query["$or"] = [
                    {field: {"$exists": False}},
                    {field: {"$lte": current_time}},
                ]

            # ç»Ÿè®¡ç¬¦åˆæ¡ä»¶ç„å‡­è¯æ€»æ•°ï¼ˆèµ°ç´¢å¼•ï¼Œæå¿«ï¼‰
            count = await collection.count_documents(match_query)
            if count == 0:
                return None

            # éæœºåç§» + limit(1)ï¼Œæ›¿ä»£ $sampleï¼Œé¿å…å…¨é›†åˆéæœºæ’åº
            skip_n = random.randint(0, count - 1)
            projection = {"filename": 1, "credential_data": 1, "enable_credit": 1, "_id": 0}
            docs = await collection.find(match_query, projection).skip(skip_n).limit(1).to_list(1)

            if docs:
                doc = docs[0]
                credential_data = doc.get("credential_data") or {}
                if mode == "omni":
                    credential_data["enable_credit"] = bool(doc.get("enable_credit", False))
                return doc["filename"], credential_data

            return None

        except Exception as e:
            log.error(f"Error getting next available credential (mode={mode}, model_name={model_name}): {e}")
            return None

    async def get_available_credentials_list(self, mode: str = "code_assist") -> List[str]:
        """
        è·å–æ‰€æœ‰å¯ç”¨å‡­è¯åˆ—è¡¨
        - æœªç¦ç”¨
        - æŒ‰è½®æ¢é¡ºåºæ’åº
        """
        self._ensure_initialized()

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            pipeline = [
                {"$match": {"disabled": False}},
                {"$sort": {"rotation_order": 1}},
                {"$project": {"filename": 1, "_id": 0}}
            ]

            docs = await collection.aggregate(pipeline).to_list(length=None)
            return [doc["filename"] for doc in docs]

        except Exception as e:
            log.error(f"Error getting available credentials list (mode={mode}): {e}")
            return []

    # ============ StorageBackend åè®®æ–¹æ³• ============

    async def store_credential(self, filename: str, credential_data: Dict[str, Any], mode: str = "code_assist") -> bool:
        """å­˜å‚¨æˆ–æ›´æ–°å‡­è¯"""
        self._ensure_initialized()

        # ç»Ÿä¸€ä½¿ç”¨ basename å¤„ç†æ–‡ä»¶å
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            current_ts = time.time()

            # ä½¿ç”¨ upsert + $setOnInsert
            # å¦‚æœæ–‡æ¡£å­˜åœ¨ï¼Œåªæ›´æ–° credential_data å’Œ updated_at
            # å¦‚æœæ–‡æ¡£ä¸å­˜åœ¨ï¼Œè®¾ç½®æ‰€æœ‰é»˜è®¤å­—æ®µ

            # å…ˆå°è¯•æ›´æ–°ç°æœ‰æ–‡æ¡£
            result = await collection.update_one(
                {"filename": filename},
                {
                    "$set": {
                        "credential_data": credential_data,
                        "updated_at": current_ts,
                    }
                }
            )

            # å¦‚æœæ²¡æœ‰åŒ¹é…åˆ°ï¼ˆæ–°å‡­è¯ï¼‰ï¼Œéœ€è¦æ’å…¥
            if result.matched_count == 0:
                # è·å–ä¸‹ä¸€ä¸ª rotation_order
                pipeline = [
                    {"$group": {"_id": None, "max_order": {"$max": "$rotation_order"}}},
                    {"$project": {"_id": 0, "next_order": {"$add": ["$max_order", 1]}}}
                ]

                result_list = await collection.aggregate(pipeline).to_list(length=1)
                next_order = result_list[0]["next_order"] if result_list else 0

                # æ’å…¥æ–°å‡­è¯ï¼ˆä½¿ç”¨ insert_oneï¼Œå› ä¸ºæˆ‘ä»¬å·²ç»ç¡®è®¤ä¸å­˜åœ¨ï¼‰
                try:
                    new_credential = {
                        "filename": filename,
                        "credential_data": credential_data,
                        "disabled": False,
                        "error_codes": [],
                        "error_messages": [],
                        "last_success": current_ts,
                        "user_email": None,
                        "model_cooldowns": {},
                        "preview": True,
                        "tier": "pro",
                        "rotation_order": next_order,
                        "call_count": 0,
                        "created_at": current_ts,
                        "updated_at": current_ts,
                    }

                    if mode == "omni":
                        new_credential["enable_credit"] = False

                    await collection.insert_one(new_credential)
                    # æ–°å‡­è¯æ’å…¥æˆåŸï¼Œæ·»å åˆ° Redis å¯ç”¨æ± 
                    await self._redis_add_cred(mode, filename)
                except Exception as insert_error:
                    # å¤„ç†å¹¶å‘æ’å…¥å¯¼è‡´ç„é‡å¤é”®é”™è¯¯
                    if "duplicate key" in str(insert_error).lower():
                        # é‡è¯•æ›´æ–°ï¼ˆå·²å­˜åœ¨ç„å‡­è¯ï¼Œæ— éœ€æ›´æ–° Redisï¼‰
                        await collection.update_one(
                            {"filename": filename},
                            {"$set": {"credential_data": credential_data, "updated_at": current_ts}}
                        )
                    else:
                        raise

            log.debug(f"Stored credential: {filename} (mode={mode})")
            return True

        except Exception as e:
            log.error(f"Error storing credential {filename}: {e}")
            return False

    async def get_credential(self, filename: str, mode: str = "code_assist") -> Optional[Dict[str, Any]]:
        """è·å–å‡­è¯æ•°æ®"""
        self._ensure_initialized()

        # ç»Ÿä¸€ä½¿ç”¨ basename å¤„ç†æ–‡ä»¶å
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # ç²¾ç¡®åŒ¹é…ï¼Œåªæ•å½±éœ€è¦ç„å­—æ®µ
            doc = await collection.find_one(
                {"filename": filename},
                {"credential_data": 1, "_id": 0}
            )
            if doc:
                return doc.get("credential_data")

            return None

        except Exception as e:
            log.error(f"Error getting credential {filename}: {e}")
            return None

    async def list_credentials(self, mode: str = "code_assist") -> List[str]:
        """åˆ—å‡ºæ‰€æœ‰å‡­è¯æ–‡ä»¶å"""
        self._ensure_initialized()

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # ä½¿ç”¨èåˆç®¡é“
            pipeline = [
                {"$sort": {"rotation_order": 1}},
                {"$project": {"filename": 1, "_id": 0}}
            ]

            docs = await collection.aggregate(pipeline).to_list(length=None)
            return [doc["filename"] for doc in docs]

        except Exception as e:
            log.error(f"Error listing credentials: {e}")
            return []

    async def delete_credential(self, filename: str, mode: str = "code_assist") -> bool:
        """åˆ é™¤å‡­è¯"""
        self._ensure_initialized()

        # ç»Ÿä¸€ä½¿ç”¨ basename å¤„ç†æ–‡ä»¶å
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # ç²¾ç¡®åŒ¹é…åˆ é™¤
            result = await collection.delete_one({"filename": filename})
            deleted_count = result.deleted_count

            if deleted_count > 0:
                # ä» Redis æ± ä¸­ç§»é™¤
                await self._redis_remove_cred(mode, filename)
                log.debug(f"Deleted {deleted_count} credential(s): {filename} (mode={mode})")
                return True
            else:
                log.warning(f"No credential found to delete: {filename} (mode={mode})")
                return False

        except Exception as e:
            log.error(f"Error deleting credential {filename}: {e}")
            return False

    async def get_duplicate_credentials_by_email(self, mode: str = "code_assist") -> Dict[str, Any]:
        """
        è·å–æŒ‰é‚®ç®±åˆ†ç»„ç„é‡å¤å‡­è¯ä¿¡æ¯ï¼ˆåªæŸ¥è¯¢é‚®ç®±å’Œæ–‡ä»¶åï¼Œä¸å è½½å®Œæ•´å‡­è¯æ•°æ®ï¼‰
        ç”¨äºå»é‡æ“ä½œ

        Args:
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")

        Returns:
            åŒ…å« email_groupsï¼ˆé‚®ç®±åˆ†ç»„ï¼‰ă€duplicate_countï¼ˆé‡å¤æ•°é‡ï¼‰ă€no_email_countï¼ˆæ— é‚®ç®±æ•°é‡ï¼‰ç„å­—å…¸
        """
        self._ensure_initialized()

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # ä½¿ç”¨èåˆç®¡é“ï¼ŒåªæŸ¥è¯¢ filename å’Œ user_email å­—æ®µ
            pipeline = [
                {
                    "$project": {
                        "filename": 1,
                        "user_email": 1,
                        "_id": 0
                    }
                },
                {
                    "$sort": {"filename": 1}
                }
            ]

            docs = await collection.aggregate(pipeline).to_list(length=None)

            # æŒ‰é‚®ç®±åˆ†ç»„
            email_to_files = {}
            no_email_files = []

            for doc in docs:
                filename = doc.get("filename")
                user_email = doc.get("user_email")

                if user_email:
                    if user_email not in email_to_files:
                        email_to_files[user_email] = []
                    email_to_files[user_email].append(filename)
                else:
                    no_email_files.append(filename)

            # æ‰¾å‡ºé‡å¤ç„é‚®ç®±ç»„
            duplicate_groups = []
            total_duplicate_count = 0

            for email, files in email_to_files.items():
                if len(files) > 1:
                    # ä¿ç•™ç¬¬ä¸€ä¸ªæ–‡ä»¶ï¼Œå…¶ä»–ä¸ºé‡å¤
                    duplicate_groups.append({
                        "email": email,
                        "kept_file": files[0],
                        "duplicate_files": files[1:],
                        "duplicate_count": len(files) - 1,
                    })
                    total_duplicate_count += len(files) - 1

            return {
                "email_groups": email_to_files,
                "duplicate_groups": duplicate_groups,
                "duplicate_count": total_duplicate_count,
                "no_email_files": no_email_files,
                "no_email_count": len(no_email_files),
                "unique_email_count": len(email_to_files),
                "total_count": len(docs),
            }

        except Exception as e:
            log.error(f"Error getting duplicate credentials by email: {e}")
            return {
                "email_groups": {},
                "duplicate_groups": [],
                "duplicate_count": 0,
                "no_email_files": [],
                "no_email_count": 0,
                "unique_email_count": 0,
                "total_count": 0,
            }

    async def update_credential_state(
        self, filename: str, state_updates: Dict[str, Any], mode: str = "code_assist"
    ) -> bool:
        """æ›´æ–°å‡­è¯ç¶æ€"""
        self._ensure_initialized()

        # ç»Ÿä¸€ä½¿ç”¨ basename å¤„ç†æ–‡ä»¶å
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # è¿‡æ»¤åªæ›´æ–°ç¶æ€å­—æ®µ
            valid_updates = {
                k: v for k, v in state_updates.items() if k in self.STATE_FIELDS
            }

            if mode != "omni":
                valid_updates.pop("enable_credit", None)

            if not valid_updates:
                return True

            valid_updates["updated_at"] = time.time()

            # ç²¾ç¡®åŒ¹é…æ›´æ–°
            result = await collection.update_one(
                {"filename": filename}, {"$set": valid_updates}
            )
            updated_count = result.modified_count + result.matched_count

            # å¦‚æœ disabled å‘ç”Ÿå˜åŒ–ï¼ŒåŒæ­¥ Redis æ± æˆå‘˜å…³ç³»
            if self._redis_enabled and "disabled" in valid_updates:
                if valid_updates["disabled"]:
                    # ç›´æ¥ç¦ç”¨ï¼ä»é›†åˆä¸­ç§»é™¤
                    await self._redis_remove_cred(mode, filename)
                else:
                    # é‡æ–°å¯ç”¨ï¼éœ€è¦è¯»å–å½“å‰ tier/preview ä»¥æ­£ç¡®æ”¾å…¥åˆ†æ¡¶
                    doc = await collection.find_one(
                        {"filename": filename},
                        projection={"tier": 1, "preview": 1, "_id": 0},
                    )
                    tier_val = (doc or {}).get("tier", "pro") or "pro"
                    preview_val = (doc or {}).get("preview", True)
                    await self._redis_sync_cred(mode, filename, disabled=False, tier=tier_val, preview=preview_val)
            elif self._redis_enabled and ("tier" in valid_updates or "preview" in valid_updates):
                # tier æˆ– preview æ›´æ–°ï¼é‡æ–°åŒæ­¥åˆ†æ¡¶ï¼ˆåªåœ¨å‡­è¯æœªç¦ç”¨æ—¶ï¼‰
                doc = await collection.find_one(
                    {"filename": filename},
                    projection={"disabled": 1, "tier": 1, "preview": 1, "_id": 0},
                )
                if doc and not doc.get("disabled", False):
                    tier_val = doc.get("tier", "pro") or "pro"
                    preview_val = doc.get("preview", True)
                    await self._redis_sync_cred(mode, filename, disabled=False, tier=tier_val, preview=preview_val)

            return updated_count > 0

        except Exception as e:
            log.error(f"Error updating credential state {filename}: {e}")
            return False

    async def get_credential_state(self, filename: str, mode: str = "code_assist") -> Dict[str, Any]:
        """è·å–å‡­è¯ç¶æ€ï¼ˆä¸åŒ…å«error_messagesï¼‰"""
        self._ensure_initialized()

        # ç»Ÿä¸€ä½¿ç”¨ basename å¤„ç†æ–‡ä»¶å
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            current_time = time.time()

            # ç²¾ç¡®åŒ¹é…
            doc = await collection.find_one({"filename": filename})

            if doc:
                model_cooldowns = doc.get("model_cooldowns", {})
                # è¿‡æ»¤æ‰æŸåç„æ•°æ®(dictç±»å‹)å’Œè¿‡æœŸç„å†·å´
                if model_cooldowns:
                    model_cooldowns = {
                        k: v for k, v in model_cooldowns.items()
                        if isinstance(v, (int, float)) and v > current_time
                    }

                state = {
                    "disabled": doc.get("disabled", False),
                    "error_codes": doc.get("error_codes", []),
                    "last_success": doc.get("last_success", current_time),
                    "user_email": doc.get("user_email"),
                    "model_cooldowns": model_cooldowns,
                    "preview": doc.get("preview", True),
                    "tier": doc.get("tier", "pro"),
                }
                if mode == "omni":
                    state["enable_credit"] = doc.get("enable_credit", False)
                return state

            # è¿”å›é»˜è®¤ç¶æ€
            default_state = {
                "disabled": False,
                "error_codes": [],
                "last_success": current_time,
                "user_email": None,
                "model_cooldowns": {},
                "preview": True,
                "tier": "pro",
            }
            if mode == "omni":
                default_state["enable_credit"] = False
            return default_state

        except Exception as e:
            log.error(f"Error getting credential state {filename}: {e}")
            return {}

    async def get_all_credential_states(self, mode: str = "code_assist") -> Dict[str, Dict[str, Any]]:
        """è·å–æ‰€æœ‰å‡­è¯ç¶æ€ï¼ˆä¸åŒ…å«error_messagesï¼‰"""
        self._ensure_initialized()

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # ä½¿ç”¨æ•å½±åªè·å–éœ€è¦ç„å­—æ®µï¼ˆä¸åŒ…å«error_messagesï¼‰
            projection = {
                "filename": 1,
                "disabled": 1,
                "error_codes": 1,
                "last_success": 1,
                "user_email": 1,
                "model_cooldowns": 1,
                "preview": 1,
                "tier": 1,
                "enable_credit": 1,
                "_id": 0
            }

            cursor = collection.find({}, projection=projection)

            states = {}
            current_time = time.time()

            async for doc in cursor:
                filename = doc["filename"]
                model_cooldowns = doc.get("model_cooldowns", {})

                # è‡ªå¨è¿‡æ»¤æ‰å·²è¿‡æœŸç„æ¨¡å‹CD
                if model_cooldowns:
                    model_cooldowns = {
                        k: v for k, v in model_cooldowns.items()
                        if isinstance(v, (int, float)) and v > current_time
                    }

                state = {
                    "disabled": doc.get("disabled", False),
                    "error_codes": doc.get("error_codes", []),
                    "last_success": doc.get("last_success", time.time()),
                    "user_email": doc.get("user_email"),
                    "model_cooldowns": model_cooldowns,
                    "preview": doc.get("preview", True),
                    "tier": doc.get("tier", "pro"),
                }
                if mode == "omni":
                    state["enable_credit"] = doc.get("enable_credit", False)
                states[filename] = state

            return states

        except Exception as e:
            log.error(f"Error getting all credential states: {e}")
            return {}

    async def get_credentials_summary(
        self,
        offset: int = 0,
        limit: Optional[int] = None,
        status_filter: str = "all",
        mode: str = "code_assist",
        error_code_filter: Optional[str] = None,
        cooldown_filter: Optional[str] = None,
        preview_filter: Optional[str] = None,
        tier_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        è·å–å‡­è¯ç„æ‘˜è¦ä¿¡æ¯ï¼ˆä¸åŒ…å«å®Œæ•´å‡­è¯æ•°æ®ï¼‰- æ”¯æŒåˆ†é¡µå’Œç¶æ€ç­›é€‰

        Args:
            offset: è·³è¿‡ç„è®°å½•æ•°ï¼ˆé»˜è®¤0ï¼‰
            limit: è¿”å›ç„æœ€å¤§è®°å½•æ•°ï¼ˆNoneè¡¨ç¤ºè¿”å›æ‰€æœ‰ï¼‰
            status_filter: ç¶æ€ç­›é€‰ï¼ˆall=å…¨éƒ¨, enabled=ä»…å¯ç”¨, disabled=ä»…ç¦ç”¨ï¼‰
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")
            error_code_filter: é”™è¯¯ç ç­›é€‰ï¼ˆæ ¼å¼å¦‚"400"æˆ–"403"ï¼Œç­›é€‰åŒ…å«è¯¥é”™è¯¯ç ç„å‡­è¯ï¼‰
            cooldown_filter: å†·å´ç¶æ€ç­›é€‰ï¼ˆ"in_cooldown"=å†·å´ä¸­, "no_cooldown"=æœªå†·å´ï¼‰
            preview_filter: Previewç­›é€‰ï¼ˆ"preview"=æ”¯æŒpreview, "no_preview"=ä¸æ”¯æŒpreviewï¼Œä»…code_assistæ¨¡å¼æœ‰æ•ˆï¼‰
            tier_filter: tierç­›é€‰ï¼ˆ"free", "pro", "ultra"ï¼‰

        Returns:
            åŒ…å« itemsï¼ˆå‡­è¯åˆ—è¡¨ï¼‰ă€totalï¼ˆæ€»æ•°ï¼‰ă€offsetă€limit ç„å­—å…¸
        """
        self._ensure_initialized()

        try:
            # æ ¹æ® mode é€‰æ‹©é›†åˆå
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # æ„å»ºæŸ¥è¯¢æ¡ä»¶
            query = {}
            if status_filter == "enabled":
                query["disabled"] = False
            elif status_filter == "disabled":
                query["disabled"] = True

            # é”™è¯¯ç ç­›é€‰ - å…¼å®¹å­˜å‚¨ä¸ºæ•°å­—æˆ–å­—ç¬¦ä¸²ç„æƒ…å†µ
            if error_code_filter and str(error_code_filter).strip().lower() != "all":
                if str(error_code_filter).strip().lower() == "none":
                    # ç­›é€‰æ— é”™è¯¯ç„å‡­è¯ï¼error_codes ä¸ºç©ºæ•°ç»„ă€ä¸å­˜åœ¨ă€æˆ–ä¸º null
                    query["$or"] = [
                        {"error_codes": {"$exists": False}},
                        {"error_codes": None},
                        {"error_codes": []},
                        {"error_codes": "[]"},
                    ]
                else:
                    filter_value = str(error_code_filter).strip()
                    query_values = [filter_value]
                    try:
                        query_values.append(int(filter_value))
                    except ValueError:
                        pass
                    query["error_codes"] = {"$in": query_values}

            # è®¡ç®—å…¨å±€ç»Ÿè®¡æ•°æ®ï¼ˆä¸å—ç­›é€‰æ¡ä»¶å½±å“ï¼‰
            global_stats = {"total": 0, "normal": 0, "disabled": 0}
            stats_pipeline = [
                {
                    "$group": {
                        "_id": "$disabled",
                        "count": {"$sum": 1}
                    }
                }
            ]

            stats_result = await collection.aggregate(stats_pipeline).to_list(length=10)
            for item in stats_result:
                count = item["count"]
                global_stats["total"] += count
                if item["_id"]:
                    global_stats["disabled"] = count
                else:
                    global_stats["normal"] = count

            # è·å–æ‰€æœ‰åŒ¹é…ç„æ–‡æ¡£ï¼ˆç”¨äºå†·å´ç­›é€‰ï¼Œå› ä¸ºéœ€è¦åœ¨Pythonä¸­åˆ¤æ–­ï¼‰
            projection = {
                "filename": 1,
                "disabled": 1,
                "error_codes": 1,
                "last_success": 1,
                "user_email": 1,
                "rotation_order": 1,
                "model_cooldowns": 1,
                "preview": 1,
                "tier": 1,
                "enable_credit": 1,
                "_id": 0
            }

            cursor = collection.find(query, projection=projection).sort("rotation_order", 1)

            all_summaries = []
            current_time = time.time()

            async for doc in cursor:
                model_cooldowns = doc.get("model_cooldowns", {})

                # è‡ªå¨è¿‡æ»¤æ‰å·²è¿‡æœŸç„æ¨¡å‹CD
                active_cooldowns = {}
                if model_cooldowns:
                    active_cooldowns = {
                        k: v for k, v in model_cooldowns.items()
                        if isinstance(v, (int, float)) and v > current_time
                    }

                summary = {
                    "filename": doc["filename"],
                    "disabled": doc.get("disabled", False),
                    "error_codes": doc.get("error_codes", []),
                    "last_success": doc.get("last_success", current_time),
                    "user_email": doc.get("user_email"),
                    "rotation_order": doc.get("rotation_order", 0),
                    "model_cooldowns": active_cooldowns,
                    "preview": doc.get("preview", True),
                    "tier": doc.get("tier", "pro"),
                }

                if mode == "omni":
                    summary["enable_credit"] = bool(doc.get("enable_credit", False))

                if mode == "code_assist" and preview_filter:
                    preview_value = summary.get("preview", True)
                    if preview_filter == "preview" and not preview_value:
                        continue
                    if preview_filter == "no_preview" and preview_value:
                        continue

                # åº”ç”¨tierç­›é€‰
                if tier_filter and tier_filter in ("free", "pro", "ultra"):
                    if summary["tier"] != tier_filter:
                        continue

                # åº”ç”¨å†·å´ç­›é€‰
                if cooldown_filter == "in_cooldown":
                    # åªä¿ç•™æœ‰å†·å´ç„å‡­è¯
                    if active_cooldowns:
                        all_summaries.append(summary)
                elif cooldown_filter == "no_cooldown":
                    # åªä¿ç•™æ²¡æœ‰å†·å´ç„å‡­è¯
                    if not active_cooldowns:
                        all_summaries.append(summary)
                else:
                    # ä¸ç­›é€‰å†·å´ç¶æ€
                    all_summaries.append(summary)

            # åº”ç”¨åˆ†é¡µ
            total_count = len(all_summaries)
            if limit is not None:
                summaries = all_summaries[offset:offset + limit]
            else:
                summaries = all_summaries[offset:]

            return {
                "items": summaries,
                "total": total_count,
                "offset": offset,
                "limit": limit,
                "stats": global_stats,
            }

        except Exception as e:
            log.error(f"Error getting credentials summary: {e}")
            return {
                "items": [],
                "total": 0,
                "offset": offset,
                "limit": limit,
                "stats": {"total": 0, "normal": 0, "disabled": 0},
            }

    # ============ é…ç½®ç®¡ç†ï¼ˆå†…å­˜ç¼“å­˜ + å¯é€‰ Redisï¼‰============

    def _rk_config(self, key: str) -> str:
        """é…ç½®é¡¹ç„ Redis key"""
        return f"code_assist:config:{key}"

    def _rk_config_all(self) -> str:
        """æ‰€æœ‰é…ç½®ç„ Redis Hash key"""
        return "code_assist:config"

    async def _load_config_to_redis(self) -> None:
        """å°†æ‰€æœ‰é…ç½®ä» MongoDB åŒæ­¥åˆ° Redis Hash"""
        if not self._redis_enabled:
            return
        try:
            config_collection = self._db["config"]
            cursor = config_collection.find({})
            mapping = {}
            async for doc in cursor:
                mapping[doc["key"]] = json.dumps(doc.get("value"))
            pipe = self._redis.pipeline()
            pipe.delete(self._rk_config_all())
            if mapping:
                pipe.hset(self._rk_config_all(), mapping=mapping)
            await pipe.execute()
            log.debug(f"Synced {len(mapping)} config items to Redis")
        except Exception as e:
            log.warning(f"Failed to sync config to Redis: {e}")

    async def set_config(self, key: str, value: Any) -> bool:
        """è®¾ç½®é…ç½®ï¼ˆå†™å…¥æ•°æ®åº“ï¼›Redis å¯ç”¨æ—¶å†™ Redisï¼Œå¦åˆ™æ›´æ–°å†…å­˜ç¼“å­˜ï¼‰"""
        self._ensure_initialized()

        try:
            config_collection = self._db["config"]
            await config_collection.update_one(
                {"key": key},
                {"$set": {"value": value, "updated_at": time.time()}},
                upsert=True,
            )

            if self._redis_enabled:
                try:
                    await self._redis.hset(self._rk_config_all(), key, json.dumps(value))
                except Exception as e:
                    log.warning(f"Redis config set error for key={key}: {e}")
            else:
                self._config_cache[key] = value

            return True

        except Exception as e:
            log.error(f"Error setting config {key}: {e}")
            return False

    async def reload_config_cache(self):
        """é‡æ–°å è½½é…ç½®ç¼“å­˜ï¼ˆåœ¨æ‰¹é‡ä¿®æ”¹é…ç½®åè°ƒç”¨ï¼‰"""
        self._ensure_initialized()
        if self._redis_enabled:
            await self._load_config_to_redis()
        else:
            self._config_loaded = False
            await self._load_config_cache()
        log.info("Config cache reloaded from database")

    async def get_config(self, key: str, default: Any = None) -> Any:
        """è·å–é…ç½®ï¼ˆRedis å¯ç”¨æ—¶ä» Redis è¯»å–ï¼Œå¦åˆ™ä»å†…å­˜ç¼“å­˜ï¼‰"""
        self._ensure_initialized()

        if self._redis_enabled:
            try:
                raw = await self._redis.hget(self._rk_config_all(), key)
                if raw is not None:
                    return json.loads(raw)
                return default
            except Exception as e:
                log.warning(f"Redis config get error for key={key}: {e}")
                return default

        return self._config_cache.get(key, default)

    async def get_all_config(self) -> Dict[str, Any]:
        """è·å–æ‰€æœ‰é…ç½®ï¼ˆRedis å¯ç”¨æ—¶ä» Redis è¯»å–ï¼Œå¦åˆ™ä»å†…å­˜ç¼“å­˜ï¼‰"""
        self._ensure_initialized()

        if self._redis_enabled:
            try:
                raw_map = await self._redis.hgetall(self._rk_config_all())
                return {k: json.loads(v) for k, v in raw_map.items()}
            except Exception as e:
                log.warning(f"Redis config getall error: {e}")
                return {}

        return self._config_cache.copy()

    async def delete_config(self, key: str) -> bool:
        """åˆ é™¤é…ç½®"""
        self._ensure_initialized()

        try:
            config_collection = self._db["config"]
            result = await config_collection.delete_one({"key": key})

            if self._redis_enabled:
                try:
                    await self._redis.hdel(self._rk_config_all(), key)
                except Exception as e:
                    log.warning(f"Redis config delete error for key={key}: {e}")
            else:
                self._config_cache.pop(key, None)

            return result.deleted_count > 0

        except Exception as e:
            log.error(f"Error deleting config {key}: {e}")
            return False

    async def get_credential_errors(self, filename: str, mode: str = "code_assist") -> Dict[str, Any]:
        """
        ä¸“é—¨è·å–å‡­è¯ç„é”™è¯¯ä¿¡æ¯ï¼ˆåŒ…å« error_codes å’Œ error_messagesï¼‰

        Args:
            filename: å‡­è¯æ–‡ä»¶å
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")

        Returns:
            åŒ…å« error_codes å’Œ error_messages ç„å­—å…¸
        """
        self._ensure_initialized()

        # ç»Ÿä¸€ä½¿ç”¨ basename å¤„ç†æ–‡ä»¶å
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # ç²¾ç¡®åŒ¹é…
            doc = await collection.find_one(
                {"filename": filename},
                {"error_codes": 1, "error_messages": 1, "_id": 0}
            )

            if doc:
                return {
                    "filename": filename,
                    "error_codes": doc.get("error_codes", []),
                    "error_messages": doc.get("error_messages", []),
                }

            # Credential does not existï¼Œè¿”å›ç©ºé”™è¯¯ä¿¡æ¯
            return {
                "filename": filename,
                "error_codes": [],
                "error_messages": [],
            }

        except Exception as e:
            log.error(f"Error getting credential errors {filename}: {e}")
            return {
                "filename": filename,
                "error_codes": [],
                "error_messages": [],
                "error": str(e)
            }

    # ============ æ¨¡å‹çº§å†·å´ç®¡ç† ============

    async def set_model_cooldown(
        self,
        filename: str,
        model_name: str,
        cooldown_until: Optional[float],
        mode: str = "code_assist"
    ) -> bool:
        """
        è®¾ç½®ç‰¹å®æ¨¡å‹ç„å†·å´æ—¶é—´

        Args:
            filename: å‡­è¯æ–‡ä»¶å
            model_name: æ¨¡å‹åï¼ˆå®Œæ•´æ¨¡å‹åï¼Œå¦‚ "gemini-2.0-flash-exp"ï¼‰
            cooldown_until: å†·å´æˆªæ­¢æ—¶é—´æˆ³ï¼ˆNone è¡¨ç¤ºæ¸…é™¤å†·å´ï¼‰
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")

        Returns:
            æ˜¯å¦æˆåŸ
        """
        self._ensure_initialized()

        # ç»Ÿä¸€ä½¿ç”¨ basename å¤„ç†æ–‡ä»¶å
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            # è½¬ä¹‰æ¨¡å‹åä¸­ç„ç‚¹å·
            escaped_model_name = self._escape_model_name(model_name)

            # ä½¿ç”¨åŸå­æ“ä½œç›´æ¥æ›´æ–°ï¼Œé¿å…ç«æ€æ¡ä»¶
            if cooldown_until is None:
                # åˆ é™¤æŒ‡å®æ¨¡å‹ç„å†·å´
                result = await collection.update_one(
                    {"filename": filename},
                    {
                        "$unset": {f"model_cooldowns.{escaped_model_name}": ""},
                        "$set": {"updated_at": time.time()}
                    }
                )
            else:
                # è®¾ç½®å†·å´æ—¶é—´
                result = await collection.update_one(
                    {"filename": filename},
                    {
                        "$set": {
                            f"model_cooldowns.{escaped_model_name}": cooldown_until,
                            "updated_at": time.time()
                        }
                    }
                )

            if result.matched_count == 0:
                log.warning(f"Credential {filename} not found")
                return False

            # åŒæ­¥å†™å…¥ Redis TTL key
            if self._redis_enabled:
                cd_key = self._rk_cd(mode, filename, escaped_model_name)
                if cooldown_until is None:
                    await self._redis.delete(cd_key)
                else:
                    ttl = int(cooldown_until - time.time())
                    if ttl > 0:
                        await self._redis.setex(cd_key, ttl, str(cooldown_until))
                    else:
                        # å†·å´å·²ç»è¿‡æœŸï¼Œç¡®ä¿æ¸…é™¤
                        await self._redis.delete(cd_key)

            log.debug(f"Set model cooldown: {filename}, model_name={model_name}, cooldown_until={cooldown_until}")
            return True

        except Exception as e:
            log.error(f"Error setting model cooldown for {filename}: {e}")
            return False

    async def clear_all_model_cooldowns(
        self,
        filename: str,
        mode: str = "code_assist"
    ) -> bool:
        """
        æ¸…é™¤æŸä¸ªå‡­è¯ç„æ‰€æœ‰æ¨¡å‹å†·å´æ—¶é—´

        Args:
            filename: å‡­è¯æ–‡ä»¶å
            mode: å‡­è¯æ¨¡å¼ ("code_assist" æˆ– "omni")

        Returns:
            æ˜¯å¦æˆåŸ
        """
        self._ensure_initialized()

        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]

            doc = await collection.find_one(
                {"filename": filename},
                {"model_cooldowns": 1, "_id": 0}
            )
            if not doc:
                log.warning(f"Credential {filename} not found")
                return False

            model_cooldowns = doc.get("model_cooldowns") or {}

            await collection.update_one(
                {"filename": filename},
                {
                    "$set": {
                        "model_cooldowns": {},
                        "updated_at": time.time(),
                    }
                }
            )

            if self._redis_enabled and isinstance(model_cooldowns, dict) and model_cooldowns:
                redis_keys = [self._rk_cd(mode, filename, escaped_model) for escaped_model in model_cooldowns.keys()]
                await self._redis.delete(*redis_keys)

            log.debug(f"Cleared all model cooldowns: {filename} (mode={mode})")
            return True

        except Exception as e:
            log.error(f"Error clearing all model cooldowns for {filename}: {e}")
            return False

    async def record_success(
        self,
        filename: str,
        model_name: Optional[str] = None,
        mode: str = "code_assist"
    ) -> None:
        """
        æˆåŸè°ƒç”¨åç„æ¡ä»¶å†™å…¥ï¼
        - åªæœ‰å½“å‰ error_codes éç©ºæ—¶æ‰æ¸…é™¤é”™è¯¯å¹¶å†™ last_success
        - åªæœ‰å½“å‰å­˜åœ¨è¯¥æ¨¡å‹ç„å†·å´é”®æ—¶æ‰æ¸…é™¤
        é€è¿‡ MongoDB æœå¡ç«¯æ¡ä»¶åŒ¹é…å®ç°
        """
        self._ensure_initialized()
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            now = time.time()

            # æ¡ä»¶å†™å…¥ï¼åªæœ‰ error_codes éç©ºæ—¶æ‰è§¦å‘ï¼Œé¿å…æ— æ„ä¹‰ç„å†™ IO
            await collection.update_one(
                {"filename": filename, "error_codes": {"$ne": []}},
                {"$set": {
                    "last_success": now,
                    "error_codes": [],
                    "error_messages": {},
                    "updated_at": now,
                }}
            )

            # æ¡ä»¶åˆ é™¤æ¨¡å‹å†·å´ï¼åªæœ‰è¯¥é”®å­˜åœ¨æ—¶æ‰å†™å…¥
            if model_name:
                escaped = self._escape_model_name(model_name)
                await collection.update_one(
                    {"filename": filename, f"model_cooldowns.{escaped}": {"$exists": True}},
                    {"$unset": {f"model_cooldowns.{escaped}": ""}, "$set": {"updated_at": now}}
                )
                # åŒæ­¥åˆ é™¤ Redis å†·å´ key
                if self._redis_enabled:
                    await self._redis.delete(self._rk_cd(mode, filename, escaped))

        except Exception as e:
            log.error(f"Error recording success for {filename}: {e}")
