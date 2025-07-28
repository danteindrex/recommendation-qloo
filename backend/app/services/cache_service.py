import json
import redis.asyncio as redis
from typing import Any, Optional
from app.core.config import settings


class CacheService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set value in cache with expiration."""
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.setex(key, expire, serialized_value)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter in cache."""
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Cache increment error: {e}")
            return 0
    
    async def set_hash(self, key: str, field: str, value: Any) -> bool:
        """Set hash field in cache."""
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis_client.hset(key, field, serialized_value)
            return True
        except Exception as e:
            print(f"Cache hash set error: {e}")
            return False
    
    async def get_hash(self, key: str, field: str) -> Optional[Any]:
        """Get hash field from cache."""
        try:
            value = await self.redis_client.hget(key, field)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache hash get error: {e}")
            return None


# Global cache instance
cache = CacheService()