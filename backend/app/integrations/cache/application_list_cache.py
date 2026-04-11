from __future__ import annotations

import json
import logging
from functools import lru_cache

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_CACHE_VERSION_KEY = "cache:applications:list:version"
_CACHE_KEY_PREFIX = "cache:applications:list"

@lru_cache
def _get_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=0.2,
        socket_timeout=0.2,
    )

class ApplicationListCache:
    def __init__(self) -> None:
        settings = get_settings()
        self.ttl_seconds = settings.applications_list_cache_ttl_seconds

    def _safe_get_version(self) -> int:
        try:
            version = _get_redis_client().get(_CACHE_VERSION_KEY)
            if version is None:
                return 1
            return max(1, int(version))
        except (RedisError, ValueError):
            logger.debug("Redis unavailable while reading applications cache version", exc_info=True)
            return 1
        
    def _build_key(
        self,
        *,
        requester_id: str,
        is_admin: bool,
        country: str | None,
        status_filter: str | None,
        version: int,
    ) -> str:
        country_token = country or "all"
        status_token = status_filter or "all"
        role_token = "admin" if is_admin else "user"
        return (
            f"{_CACHE_KEY_PREFIX}:v{version}:role:{role_token}:user:{requester_id}:"
            f"country:{country_token}:status:{status_token}"
        )
    
    def get_list(
        self,
        *,
        requester_id: str,
        is_admin: bool,
        country: str | None,
        status_filter: str | None,
    ) -> list[dict] | None:
        version = self._safe_get_version()
        key = self._build_key(
            requester_id=requester_id,
            is_admin=is_admin,
            country=country,
            status_filter=status_filter,
            version=version,
        )
        try:
            raw_payload = _get_redis_client().get(key)
            if not raw_payload:
                return None
            payload = json.loads(raw_payload)
            if not isinstance(payload, dict):
                return None
            return payload
        except (RedisError, json.JSONDecodeError):
            logger.debug("Redis unavailable while reading applications cache entry", exc_info=True)
            return None
        
    def set_list(
        self,
        *,
        requester_id: str,
        is_admin: bool,
        country: str | None,
        status_filter: str | None,
        payload: dict,
    ) -> None:
        version = self._safe_get_version()
        key = self._build_key(
            requester_id=requester_id,
            is_admin=is_admin,
            country=country,
            status_filter=status_filter,
            version=version,
        )
        try:
            _get_redis_client().setex(key, self.ttl_seconds, json.dumps(payload))
        except RedisError:
            logger.debug("Redis unavailable while writing applications cache entry", exc_info=True)

    def bump_version(self) -> None:
        try:
            _get_redis_client().incr(_CACHE_VERSION_KEY)
        except RedisError:
            logger.debug("Redis unavailable while invalidating applications cache", exc_info=True)