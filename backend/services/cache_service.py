import json
import hashlib
import redis
from typing import Optional
from core.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheService:
    def __init__(self):
        cfg = get_settings()
        self._ttl = cfg.redis_ttl_seconds
        try:
            self._client = redis.Redis(
                host=cfg.redis_host,
                port=cfg.redis_port,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            self._client.ping()
            self._available = True
        except redis.RedisError:
            logger.warning("Redis unavailable — caching disabled")
            self._available = False

    def _key(self, question: str, top_k: int) -> str:
        raw = f"{question.strip().lower()}::{top_k}"
        return "s3rag:" + hashlib.sha256(raw.encode()).hexdigest()

    def get(self, question: str, top_k: int) -> Optional[dict]:
        if not self._available:
            return None
        try:
            value = self._client.get(self._key(question, top_k))
            return json.loads(value) if value else None
        except redis.RedisError as exc:
            logger.warning("Cache get failed", extra={"error": str(exc)})
            return None

    def set(self, question: str, top_k: int, payload: dict):
        if not self._available:
            return
        try:
            self._client.setex(self._key(question, top_k), self._ttl, json.dumps(payload))
        except redis.RedisError as exc:
            logger.warning("Cache set failed", extra={"error": str(exc)})

    def health(self) -> str:
        if not self._available:
            return "down"
        try:
            self._client.ping()
            return "ok"
        except redis.RedisError:
            return "degraded"
