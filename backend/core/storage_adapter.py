import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Protocol

from log import log


class StorageBackend(Protocol):
    async def initialize(self) -> None: ...

    async def close(self) -> None: ...

    async def store_credential(
        self, filename: str, credential_data: Dict[str, Any], mode: str = "code_assist"
    ) -> bool: ...

    async def get_credential(
        self, filename: str, mode: str = "code_assist"
    ) -> Optional[Dict[str, Any]]: ...

    async def list_credentials(self, mode: str = "code_assist") -> List[str]: ...

    async def get_all_credentials(self, mode: str = "code_assist") -> Dict[str, Dict[str, Any]]: ...

    async def delete_credential(self, filename: str, mode: str = "code_assist") -> bool: ...

    async def update_credential_state(
        self, filename: str, state_updates: Dict[str, Any], mode: str = "code_assist"
    ) -> bool: ...

    async def get_credential_state(
        self, filename: str, mode: str = "code_assist"
    ) -> Dict[str, Any]: ...

    async def get_all_credential_states(
        self, mode: str = "code_assist"
    ) -> Dict[str, Dict[str, Any]]: ...

    async def record_success(
        self,
        filename: str,
        model_name: Optional[str] = None,
        mode: str = "code_assist",
    ) -> None:
        """Record a completed provider attempt."""
        ...

    async def record_failure(self, filename: str, mode: str = "code_assist") -> None:
        """Record a failed provider attempt for fair routing."""
        ...

    async def set_config(self, key: str, value: Any) -> bool: ...

    async def get_config(self, key: str, default: Any = None) -> Any: ...

    async def get_all_config(self) -> Dict[str, Any]: ...

    async def delete_config(self, key: str) -> bool: ...


class StorageAdapter:
    def __init__(self):
        self._backend: Optional["StorageBackend"] = None
        self._initialized = False
        self._lock = asyncio.Lock()

    async def initialize(self) -> None:
        async with self._lock:
            if self._initialized:
                return

            postgresql_uri = os.getenv("POSTGRESQL_URI", "").strip()
            mongodb_uri = os.getenv("MONGODB_URI", "").strip()

            if postgresql_uri and mongodb_uri:
                raise RuntimeError(
                    "Configure only one external storage backend: POSTGRESQL_URI or MONGODB_URI."
                )

            if postgresql_uri:
                try:
                    from .storage.postgresql_manager import PostgreSQLManager

                    self._backend = PostgreSQLManager()
                    await self._backend.initialize()
                    log.info("Using the PostgreSQL storage backend.")
                except Exception as e:
                    log.error(f"Failed to initialize PostgreSQL backend: {e}")
                    if self._backend:
                        try:
                            await self._backend.close()
                        except Exception:
                            log.warning(
                                "Failed to clean up the PostgreSQL backend after startup failure."
                            )
                    self._backend = None
                    raise RuntimeError(
                        "The configured PostgreSQL storage backend is unavailable."
                    ) from e
            elif not mongodb_uri:
                try:
                    from .storage.sqlite_manager import SQLiteManager

                    self._backend = SQLiteManager()
                    await self._backend.initialize()
                    log.info("Using the SQLite storage backend.")
                except Exception as e:
                    log.error(f"Failed to initialize SQLite backend: {e}")
                    raise RuntimeError("No storage backend is available.") from e
            else:
                try:
                    from .storage.mongodb_manager import MongoDBManager

                    self._backend = MongoDBManager()
                    await self._backend.initialize()
                    log.info("Using the MongoDB storage backend.")
                except Exception as e:
                    log.error(f"Failed to initialize MongoDB backend: {e}")
                    if self._backend:
                        try:
                            await self._backend.close()
                        except Exception:
                            log.warning(
                                "Failed to clean up the MongoDB backend after startup failure."
                            )
                    self._backend = None
                    raise RuntimeError(
                        "The configured MongoDB storage backend is unavailable."
                    ) from e

            self._initialized = True

    async def close(self) -> None:
        if self._backend:
            await self._backend.close()
            self._backend = None
            self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized or not self._backend:
            raise RuntimeError("The storage adapter is not initialized.")

    async def store_credential(
        self, filename: str, credential_data: Dict[str, Any], mode: str = "code_assist"
    ) -> bool:
        self._ensure_initialized()
        return await self._backend.store_credential(filename, credential_data, mode)

    async def get_credential(
        self, filename: str, mode: str = "code_assist"
    ) -> Optional[Dict[str, Any]]:
        self._ensure_initialized()
        return await self._backend.get_credential(filename, mode)

    async def list_credentials(self, mode: str = "code_assist") -> List[str]:
        self._ensure_initialized()
        return await self._backend.list_credentials(mode)

    async def get_all_credentials(self, mode: str = "code_assist") -> Dict[str, Dict[str, Any]]:
        self._ensure_initialized()
        return await self._backend.get_all_credentials(mode)

    async def delete_credential(self, filename: str, mode: str = "code_assist") -> bool:
        self._ensure_initialized()
        return await self._backend.delete_credential(filename, mode)

    async def update_credential_state(
        self, filename: str, state_updates: Dict[str, Any], mode: str = "code_assist"
    ) -> bool:
        self._ensure_initialized()
        return await self._backend.update_credential_state(filename, state_updates, mode)

    async def get_credential_state(
        self, filename: str, mode: str = "code_assist"
    ) -> Dict[str, Any]:
        self._ensure_initialized()
        return await self._backend.get_credential_state(filename, mode)

    async def get_all_credential_states(
        self, mode: str = "code_assist"
    ) -> Dict[str, Dict[str, Any]]:
        self._ensure_initialized()
        return await self._backend.get_all_credential_states(mode)

    async def set_config(self, key: str, value: Any) -> bool:
        self._ensure_initialized()
        return await self._backend.set_config(key, value)

    async def get_config(self, key: str, default: Any = None) -> Any:
        self._ensure_initialized()
        return await self._backend.get_config(key, default)

    async def get_all_config(self) -> Dict[str, Any]:
        self._ensure_initialized()
        return await self._backend.get_all_config()

    async def delete_config(self, key: str) -> bool:
        self._ensure_initialized()
        return await self._backend.delete_config(key)

    async def export_credential_to_json(self, filename: str, output_path: str = None) -> bool:
        self._ensure_initialized()
        if hasattr(self._backend, "export_credential_to_json"):
            return await self._backend.export_credential_to_json(filename, output_path)

        credential_data = await self.get_credential(filename)
        if credential_data is None:
            return False

        if output_path is None:
            output_path = f"{filename}.json"

        import aiofiles

        try:
            async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(credential_data, indent=2, ensure_ascii=False))
            return True
        except Exception:
            return False

    async def import_credential_from_json(self, json_path: str, filename: str = None) -> bool:
        self._ensure_initialized()
        if hasattr(self._backend, "import_credential_from_json"):
            return await self._backend.import_credential_from_json(json_path, filename)

        try:
            import aiofiles

            async with aiofiles.open(json_path, "r", encoding="utf-8") as f:
                content = await f.read()

            credential_data = json.loads(content)

            if filename is None:
                filename = os.path.basename(json_path)

            return await self.store_credential(filename, credential_data)
        except Exception:
            return False

    def get_backend_type(self) -> str:
        if not self._backend:
            return "none"

        backend_class_name = self._backend.__class__.__name__
        if "SQLite" in backend_class_name or "sqlite" in backend_class_name.lower():
            return "sqlite"
        elif "MongoDB" in backend_class_name or "mongo" in backend_class_name.lower():
            return "mongodb"
        elif (
            "PSQL" in backend_class_name
            or "Postgres" in backend_class_name
            or "psql" in backend_class_name.lower()
        ):
            return "postgresql"
        else:
            return "unknown"

    async def get_backend_info(self) -> Dict[str, Any]:
        self._ensure_initialized()

        backend_type = self.get_backend_type()
        info = {"backend_type": backend_type, "initialized": self._initialized}

        if hasattr(self._backend, "get_database_info"):
            try:
                db_info = await self._backend.get_database_info()
                info.update(db_info)
            except Exception as e:
                info["database_error"] = str(e)
        else:
            backend_type = self.get_backend_type()
            if backend_type == "sqlite":
                info.update(
                    {
                        "database_path": getattr(self._backend, "_db_path", None),
                        "credentials_dir": getattr(self._backend, "_credentials_dir", None),
                    }
                )
            elif backend_type == "mongodb":
                info.update(
                    {
                        "database_name": getattr(self._backend, "_db", {}).name
                        if hasattr(self._backend, "_db")
                        else None,
                    }
                )
            elif backend_type == "postgresql":
                info.update(
                    {
                        "dsn": getattr(self._backend, "_dsn", None),
                    }
                )

        return info


_storage_adapter: Optional[StorageAdapter] = None
_storage_adapter_lock = asyncio.Lock()


async def get_storage_adapter() -> StorageAdapter:
    global _storage_adapter

    if _storage_adapter is None:
        async with _storage_adapter_lock:
            if _storage_adapter is None:
                adapter = StorageAdapter()
                await adapter.initialize()
                _storage_adapter = adapter

    return _storage_adapter


async def close_storage_adapter():
    global _storage_adapter

    async with _storage_adapter_lock:
        if _storage_adapter:
            await _storage_adapter.close()
            _storage_adapter = None
