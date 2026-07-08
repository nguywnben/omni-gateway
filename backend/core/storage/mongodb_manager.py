"""Internal implementation detail."""

import json
import os
import time
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from log import log


class MongoDBManager:
    """Internal implementation detail."""

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
        """Internal implementation detail."""
        return model_name.replace(".", "-")

    def __init__(self):
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._initialized = False


        self._config_cache: Dict[str, Any] = {}
        self._config_loaded = False


        self._redis = None
        self._redis_enabled: bool = False

    async def initialize(self) -> None:
        """Internal implementation detail."""
        if self._initialized:
            return

        try:
            mongodb_uri = os.getenv("MONGODB_URI")
            if not mongodb_uri:
                raise ValueError("MONGODB_URI environment variable not set")

            database_name = os.getenv("MONGODB_DATABASE", "omni_gateway")

            self._client = AsyncIOMotorClient(mongodb_uri)
            self._db = self._client[database_name]


            await self._db.command("ping")


            await self._create_indexes()


            await self._load_config_cache()

            self._initialized = True
            log.info(f"MongoDB storage initialized (database: {database_name})")


            await self._init_redis()

        except Exception as e:
            log.error(f"Error initializing MongoDB: {e}")
            raise

    async def _create_indexes(self):
        """Internal implementation detail."""
        from pymongo import IndexModel, ASCENDING

        credentials_collection = self._db["credentials"]
        primary_credentials_collection = self._db["primary_credentials"]


        code_assist_indexes = [

            IndexModel([("filename", ASCENDING)], unique=True, name="idx_filename_unique"),



            IndexModel(
                [("disabled", ASCENDING), ("rotation_order", ASCENDING)],
                name="idx_disabled_rotation"
            ),


            IndexModel([("error_codes", ASCENDING)], name="idx_error_codes"),


            IndexModel([("user_email", ASCENDING)], name="idx_user_email"),
        ]


        primary_indexes = [

            IndexModel([("filename", ASCENDING)], unique=True, name="idx_filename_unique"),



            IndexModel(
                [("disabled", ASCENDING), ("rotation_order", ASCENDING)],
                name="idx_disabled_rotation"
            ),


            IndexModel([("error_codes", ASCENDING)], name="idx_error_codes"),


            IndexModel([("user_email", ASCENDING)], name="idx_user_email"),
        ]


        try:
            await credentials_collection.create_indexes(code_assist_indexes)
            await primary_credentials_collection.create_indexes(primary_indexes)
            log.debug("MongoDB indexes created.")
        except Exception as e:

            if "already exists" not in str(e).lower():
                log.warning(f"Index creation warning: {e}")

    async def _load_config_cache(self):
        """Internal implementation detail."""
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



    async def _init_redis(self) -> None:
        """Internal implementation detail."""
        redis_url = os.getenv("REDIS_URL")
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


            import asyncio
            await asyncio.gather(
                self._rebuild_redis_cache("code_assist"),
                self._rebuild_redis_cache("primary"),
                self._load_config_to_redis(),
            )
            log.info("Redis credential pool cache ready")
        except Exception as e:
            log.warning(f"Redis init failed, falling back to MongoDB-only mode: {e}")
            self._redis = None
            self._redis_enabled = False



    def _rk_avail(self, mode: str) -> str:
        """Internal implementation detail."""
        return f"code_assist:avail:{mode}"

    def _rk_tier(self, mode: str, tier: str) -> str:
        """Internal implementation detail."""
        return f"code_assist:tier:{mode}:{tier}"

    def _rk_preview(self, mode: str) -> str:
        """Internal implementation detail."""
        return f"code_assist:preview:{mode}"

    def _rk_cd(self, mode: str, filename: str, escaped_model: str) -> str:
        """Internal implementation detail."""
        return f"code_assist:cd:{mode}:{filename}:{escaped_model}"



    async def _rebuild_redis_cache(self, mode: str) -> None:
        """Internal implementation detail."""
        if not self._redis:
            return
        try:
            collection = self._db[self._get_collection_name(mode)]

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


                    tier = doc.get("tier") or "pro"
                    tier_buckets.setdefault(tier, []).append(filename)


                    if mode == "code_assist" and doc.get("preview", True):
                        preview_members.append(filename)


                    model_cooldowns = doc.get("model_cooldowns") or {}
                    for escaped_model, cooldown_until in model_cooldowns.items():
                        if isinstance(cooldown_until, (int, float)) and cooldown_until > current_time:
                            ttl = int(cooldown_until - current_time)
                            if ttl > 0:
                                cd_key = self._rk_cd(mode, filename, escaped_model)
                                cooldown_entries.append((cd_key, ttl, str(cooldown_until)))

            tmp_avail = self._rk_avail(mode) + ":tmp"

            pipe = self._redis.pipeline()

            pipe.delete(tmp_avail)
            if avail:
                pipe.sadd(tmp_avail, *avail)
            await pipe.execute()


            pipe2 = self._redis.pipeline()
            if avail:
                pipe2.rename(tmp_avail, self._rk_avail(mode))
            else:
                pipe2.delete(self._rk_avail(mode))
                pipe2.delete(tmp_avail)
            await pipe2.execute()


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
        """Internal implementation detail."""
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
        """Internal implementation detail."""
        if not self._redis_enabled:
            return
        try:
            pipe = self._redis.pipeline()
            pipe.srem(self._rk_avail(mode), filename)
            if tier:
                pipe.srem(self._rk_tier(mode, tier), filename)
            else:

                for t in ("free", "pro", "ultra"):
                    pipe.srem(self._rk_tier(mode, t), filename)
            pipe.srem(self._rk_preview(mode), filename)
            await pipe.execute()
        except Exception as e:
            log.warning(f"Redis remove_cred error: {e}")

    async def _redis_sync_cred(self, mode: str, filename: str, disabled: bool, tier: str = "pro", preview: bool = True) -> None:
        """Internal implementation detail."""
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

    async def _choose_best_redis_candidate(self, mode: str, candidates: list[str]) -> Optional[str]:
        """Select the least-used sampled Redis candidate using MongoDB metadata."""
        normalized_candidates = [os.path.basename(str(item)) for item in candidates if item]
        if not normalized_candidates:
            return None

        try:
            collection = self._db[self._get_collection_name(mode)]
            doc = await collection.find_one(
                {"filename": {"$in": normalized_candidates}, "disabled": False},
                projection={
                    "filename": 1,
                    "call_count": 1,
                    "last_success": 1,
                    "rotation_order": 1,
                    "_id": 0,
                },
                sort=[
                    ("call_count", 1),
                    ("last_success", 1),
                    ("rotation_order", 1),
                    ("filename", 1),
                ],
            )
            if doc and doc.get("filename"):
                return str(doc["filename"])
        except Exception as e:
            log.debug(f"Redis candidate ranking fell back to sampled order: {e}")

        return normalized_candidates[0]

    async def _get_next_available_from_redis(
        self, mode: str, model_name: Optional[str], exclude_free_tier: bool = False, preview_only: bool = False
    ) -> Optional[tuple]:
        """Internal implementation detail."""
        try:

            if preview_only and exclude_free_tier:

                preview_set = await self._redis.smembers(self._rk_preview(mode))
                pro_members = await self._redis.smembers(self._rk_tier(mode, "pro"))
                ultra_members = await self._redis.smembers(self._rk_tier(mode, "ultra"))
                non_free = pro_members | ultra_members
                all_candidates = list(preview_set & non_free)
                if not all_candidates:
                    log.debug(f"[Redis MISS] mode={mode} preview+non-free: no candidates, fallback to MongoDB")
                    return None
                candidates = sorted(all_candidates)
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
                candidates = sorted(all_candidates)
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


            if model_name:
                escaped = self._escape_model_name(model_name)
                available_candidates = []
                for filename in candidates:
                    cd_key = self._rk_cd(mode, filename, escaped)
                    if not await self._redis.exists(cd_key):
                        available_candidates.append(filename)

                filename = await self._choose_best_redis_candidate(mode, available_candidates)
                if filename:
                    credential_data = await self.get_credential(filename, mode)
                    if mode == "primary":
                        state = await self.get_credential_state(filename, mode)
                        credential_data = credential_data or {}
                        credential_data["enable_credit"] = bool(state.get("enable_credit", False))
                    log.debug(f"[Redis HIT] mode={mode} model={model_name} -> {filename}")
                    return filename, credential_data

                log.debug(f"[Redis MISS] mode={mode} model={model_name}: all {len(candidates)} candidates in cooldown, fallback to MongoDB")
                return None
            else:
                filename = await self._choose_best_redis_candidate(mode, candidates)
                if not filename:
                    return None
                credential_data = await self.get_credential(filename, mode)
                if mode == "primary":
                    state = await self.get_credential_state(filename, mode)
                    credential_data = credential_data or {}
                    credential_data["enable_credit"] = bool(state.get("enable_credit", False))
                log.debug(f"[Redis HIT] mode={mode} -> {filename}")
                return filename, credential_data
        except Exception as e:
            log.warning(f"Redis get_next_available error: {e}")
            return None

    async def close(self) -> None:
        """Internal implementation detail."""
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
        """Internal implementation detail."""
        if not self._initialized:
            raise RuntimeError("MongoDB manager not initialized")

    def _get_collection_name(self, mode: str) -> str:
        """Internal implementation detail."""
        if mode == "primary":
            return "primary_credentials"
        elif mode == "code_assist":
            return "credentials"
        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'code_assist' or 'primary'")



    async def get_next_available_credential(
        self, mode: str = "code_assist", model_name: Optional[str] = None
    ) -> Optional[tuple[str, Dict[str, Any]]]:
        """Internal implementation detail."""
        self._ensure_initialized()


        if self._redis_enabled:
            model_lower = model_name.lower() if model_name else ""
            exclude_free = False
            preview_only = mode == "code_assist" and "preview" in model_lower
            result = await self._get_next_available_from_redis(
                mode, model_name, exclude_free_tier=exclude_free, preview_only=preview_only
            )
            if result is not None:
                return result

            log.debug(f"[MongoDB fallback] mode={mode} model={model_name}")

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            current_time = time.time()


            match_query: Dict[str, Any] = {"disabled": False}


            if mode == "code_assist" and model_name and "preview" in model_name.lower():
                match_query["preview"] = True


            if model_name:
                escaped_model_name = self._escape_model_name(model_name)
                field = f"model_cooldowns.{escaped_model_name}"
                match_query["$or"] = [
                    {field: {"$exists": False}},
                    {field: {"$lte": current_time}},
                ]


            projection = {"filename": 1, "credential_data": 1, "enable_credit": 1, "_id": 0}
            docs = await (
                collection
                .find(match_query, projection)
                .sort([("call_count", 1), ("last_success", 1), ("rotation_order", 1), ("filename", 1)])
                .limit(1)
                .to_list(1)
            )

            if docs:
                doc = docs[0]
                credential_data = doc.get("credential_data") or {}
                if mode == "primary":
                    credential_data["enable_credit"] = bool(doc.get("enable_credit", False))
                return doc["filename"], credential_data

            return None

        except Exception as e:
            log.error(f"Error getting next available credential (mode={mode}, model_name={model_name}): {e}")
            return None

    async def get_available_credentials_list(self, mode: str = "code_assist") -> List[str]:
        """Internal implementation detail."""
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



    async def store_credential(self, filename: str, credential_data: Dict[str, Any], mode: str = "code_assist") -> bool:
        """Internal implementation detail."""
        self._ensure_initialized()


        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            current_ts = time.time()






            result = await collection.update_one(
                {"filename": filename},
                {
                    "$set": {
                        "credential_data": credential_data,
                        "updated_at": current_ts,
                    }
                }
            )


            if result.matched_count == 0:

                pipeline = [
                    {"$group": {"_id": None, "max_order": {"$max": "$rotation_order"}}},
                    {"$project": {"_id": 0, "next_order": {"$add": ["$max_order", 1]}}}
                ]

                result_list = await collection.aggregate(pipeline).to_list(length=1)
                next_order = result_list[0]["next_order"] if result_list else 0


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

                    if mode == "primary":
                        new_credential["enable_credit"] = False

                    await collection.insert_one(new_credential)

                    await self._redis_add_cred(mode, filename)
                except Exception as insert_error:

                    if "duplicate key" in str(insert_error).lower():

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
        """Internal implementation detail."""
        self._ensure_initialized()


        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


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
        """Internal implementation detail."""
        self._ensure_initialized()

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


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
        """Internal implementation detail."""
        self._ensure_initialized()


        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


            result = await collection.delete_one({"filename": filename})
            deleted_count = result.deleted_count

            if deleted_count > 0:

                await self._redis_remove_cred(mode, filename)
                log.debug(f"Deleted {deleted_count} credentials: {filename} (mode={mode}).")
                return True
            else:
                log.warning(f"No credential found to delete: {filename} (mode={mode})")
                return False

        except Exception as e:
            log.error(f"Error deleting credential {filename}: {e}")
            return False

    async def get_duplicate_credentials_by_email(self, mode: str = "code_assist") -> Dict[str, Any]:
        """Internal implementation detail."""
        self._ensure_initialized()

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


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


            duplicate_groups = []
            total_duplicate_count = 0

            for email, files in email_to_files.items():
                if len(files) > 1:

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
        """Internal implementation detail."""
        self._ensure_initialized()


        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


            valid_updates = {
                k: v for k, v in state_updates.items() if k in self.STATE_FIELDS
            }

            if mode != "primary":
                valid_updates.pop("enable_credit", None)

            if not valid_updates:
                return True

            valid_updates["updated_at"] = time.time()


            result = await collection.update_one(
                {"filename": filename}, {"$set": valid_updates}
            )
            updated_count = result.modified_count + result.matched_count


            if self._redis_enabled and "disabled" in valid_updates:
                if valid_updates["disabled"]:

                    await self._redis_remove_cred(mode, filename)
                else:

                    doc = await collection.find_one(
                        {"filename": filename},
                        projection={"tier": 1, "preview": 1, "_id": 0},
                    )
                    tier_val = (doc or {}).get("tier", "pro") or "pro"
                    preview_val = (doc or {}).get("preview", True)
                    await self._redis_sync_cred(mode, filename, disabled=False, tier=tier_val, preview=preview_val)
            elif self._redis_enabled and ("tier" in valid_updates or "preview" in valid_updates):

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
        """Internal implementation detail."""
        self._ensure_initialized()


        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            current_time = time.time()


            doc = await collection.find_one({"filename": filename})

            if doc:
                model_cooldowns = doc.get("model_cooldowns", {})

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
                if mode == "primary":
                    state["enable_credit"] = doc.get("enable_credit", False)
                return state


            default_state = {
                "disabled": False,
                "error_codes": [],
                "last_success": current_time,
                "user_email": None,
                "model_cooldowns": {},
                "preview": True,
                "tier": "pro",
            }
            if mode == "primary":
                default_state["enable_credit"] = False
            return default_state

        except Exception as e:
            log.error(f"Error getting credential state {filename}: {e}")
            return {}

    async def get_all_credential_states(self, mode: str = "code_assist") -> Dict[str, Dict[str, Any]]:
        """Internal implementation detail."""
        self._ensure_initialized()

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


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
                if mode == "primary":
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
        """Internal implementation detail."""
        self._ensure_initialized()

        try:

            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


            query = {}
            if status_filter == "enabled":
                query["disabled"] = False
            elif status_filter == "disabled":
                query["disabled"] = True


            if error_code_filter and str(error_code_filter).strip().lower() != "all":
                if str(error_code_filter).strip().lower() == "none":

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

                if mode == "primary":
                    summary["enable_credit"] = bool(doc.get("enable_credit", False))

                if mode == "code_assist" and preview_filter:
                    preview_value = summary.get("preview", True)
                    if preview_filter == "preview" and not preview_value:
                        continue
                    if preview_filter == "no_preview" and preview_value:
                        continue


                if tier_filter and tier_filter in ("free", "pro", "ultra"):
                    if summary["tier"] != tier_filter:
                        continue


                if cooldown_filter == "in_cooldown":

                    if active_cooldowns:
                        all_summaries.append(summary)
                elif cooldown_filter == "no_cooldown":

                    if not active_cooldowns:
                        all_summaries.append(summary)
                else:

                    all_summaries.append(summary)


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



    def _rk_config(self, key: str) -> str:
        """Internal implementation detail."""
        return f"code_assist:config:{key}"

    def _rk_config_all(self) -> str:
        """Internal implementation detail."""
        return "code_assist:config"

    async def _load_config_to_redis(self) -> None:
        """Internal implementation detail."""
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
        """Internal implementation detail."""
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
        """Internal implementation detail."""
        self._ensure_initialized()
        if self._redis_enabled:
            await self._load_config_to_redis()
        else:
            self._config_loaded = False
            await self._load_config_cache()
        log.info("Config cache reloaded from database")

    async def get_config(self, key: str, default: Any = None) -> Any:
        """Internal implementation detail."""
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
        """Internal implementation detail."""
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
        """Internal implementation detail."""
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
        """Internal implementation detail."""
        self._ensure_initialized()


        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


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



    async def set_model_cooldown(
        self,
        filename: str,
        model_name: str,
        cooldown_until: Optional[float],
        mode: str = "code_assist"
    ) -> bool:
        """Internal implementation detail."""
        self._ensure_initialized()


        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]


            escaped_model_name = self._escape_model_name(model_name)


            if cooldown_until is None:

                result = await collection.update_one(
                    {"filename": filename},
                    {
                        "$unset": {f"model_cooldowns.{escaped_model_name}": ""},
                        "$set": {"updated_at": time.time()}
                    }
                )
            else:

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


            if self._redis_enabled:
                cd_key = self._rk_cd(mode, filename, escaped_model_name)
                if cooldown_until is None:
                    await self._redis.delete(cd_key)
                else:
                    ttl = int(cooldown_until - time.time())
                    if ttl > 0:
                        await self._redis.setex(cd_key, ttl, str(cooldown_until))
                    else:

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
        """Internal implementation detail."""
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
        """Internal implementation detail."""
        self._ensure_initialized()
        filename = os.path.basename(filename)

        try:
            collection_name = self._get_collection_name(mode)
            collection = self._db[collection_name]
            now = time.time()


            await collection.update_one(
                {"filename": filename},
                {"$set": {
                    "last_success": now,
                    "error_codes": [],
                    "error_messages": {},
                    "updated_at": now,
                }, "$inc": {"call_count": 1}}
            )


            if model_name:
                escaped = self._escape_model_name(model_name)
                await collection.update_one(
                    {"filename": filename, f"model_cooldowns.{escaped}": {"$exists": True}},
                    {"$unset": {f"model_cooldowns.{escaped}": ""}, "$set": {"updated_at": now}}
                )

                if self._redis_enabled:
                    await self._redis.delete(self._rk_cd(mode, filename, escaped))

        except Exception as e:
            log.error(f"Error recording success for {filename}: {e}")
