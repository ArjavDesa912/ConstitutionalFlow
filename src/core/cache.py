import redis
import json
import pickle
from typing import Any, Optional
from src.core.config import settings

class RedisCache:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set a value in cache with expiration"""
        try:
            if isinstance(value, (dict, list)):
                serialized_value = json.dumps(value)
            else:
                serialized_value = pickle.dumps(value)
            return self.redis_client.setex(key, expire, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return pickle.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    def set_hash(self, name: str, mapping: dict, expire: int = 3600) -> bool:
        """Set a hash in cache"""
        try:
            result = self.redis_client.hset(name, mapping=mapping)
            if expire > 0:
                self.redis_client.expire(name, expire)
            return bool(result)
        except Exception as e:
            print(f"Cache set_hash error: {e}")
            return False
    
    def get_hash(self, name: str) -> Optional[dict]:
        """Get a hash from cache"""
        try:
            return self.redis_client.hgetall(name)
        except Exception as e:
            print(f"Cache get_hash error: {e}")
            return None

# Global cache instance
cache = RedisCache() 