"""
Redis Cache Service for AI Data Agent
Provides caching functionality using Redis/Upstash
"""

import redis
import json
import pickle
import asyncio
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
from functools import wraps
import hashlib

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class RedisCache:
    """Redis cache service with async/sync support"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.redis_url
        self.default_ttl = settings.cache_ttl
        self._client = None
        self._connected = False
        
    def _get_client(self) -> redis.Redis:
        """Get Redis client instance"""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    socket_timeout=10,
                    socket_connect_timeout=10,
                    retry_on_timeout=True,
                    decode_responses=True
                )
                # Test connection
                self._client.ping()
                self._connected = True
                logger.info("Redis connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._connected = False
                # Return a mock client for fallback
                return self._get_mock_client()
        
        return self._client
    
    def _get_mock_client(self):
        """Return a mock client for fallback when Redis is unavailable"""
        class MockRedis:
            def __init__(self):
                self._data = {}
            
            def ping(self):
                return True
            
            def set(self, key, value, ex=None):
                self._data[key] = {"value": value, "expires": None if ex is None else datetime.now() + timedelta(seconds=ex)}
                return True
            
            def get(self, key):
                if key in self._data:
                    item = self._data[key]
                    if item["expires"] is None or item["expires"] > datetime.now():
                        return item["value"]
                    else:
                        del self._data[key]
                return None
            
            def delete(self, *keys):
                count = 0
                for key in keys:
                    if key in self._data:
                        del self._data[key]
                        count += 1
                return count
            
            def exists(self, key):
                return key in self._data
            
            def expire(self, key, seconds):
                if key in self._data:
                    self._data[key]["expires"] = datetime.now() + timedelta(seconds=seconds)
                    return True
                return False
            
            def ttl(self, key):
                if key in self._data and self._data[key]["expires"]:
                    remaining = (self._data[key]["expires"] - datetime.now()).total_seconds()
                    return max(0, int(remaining))
                return -1
            
            def keys(self, pattern="*"):
                return list(self._data.keys())
            
            def flushdb(self):
                self._data.clear()
                return True
        
        logger.warning("Using mock Redis client for fallback")
        return MockRedis()
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage"""
        try:
            if isinstance(value, (str, int, float, bool)):
                return json.dumps({"type": "json", "data": value})
            else:
                # Use pickle for complex objects
                pickled = pickle.dumps(value)
                # Convert to base64 for Redis string storage
                import base64
                encoded = base64.b64encode(pickled).decode('utf-8')
                return json.dumps({"type": "pickle", "data": encoded})
        except Exception as e:
            logger.error(f"Failed to serialize value: {e}")
            return json.dumps({"type": "json", "data": str(value)})
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from Redis storage"""
        try:
            data = json.loads(value)
            if data["type"] == "json":
                return data["data"]
            elif data["type"] == "pickle":
                import base64
                pickled = base64.b64decode(data["data"].encode('utf-8'))
                return pickle.loads(pickled)
        except Exception as e:
            logger.error(f"Failed to deserialize value: {e}")
            return value
    
    def _generate_key(self, prefix: str, key: str) -> str:
        """Generate cache key with prefix"""
        return f"ai_data_agent:{prefix}:{key}"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, prefix: str = "cache") -> bool:
        """Set a value in cache"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            serialized_value = self._serialize_value(value)
            expire_time = ttl or self.default_ttl
            
            result = client.set(cache_key, serialized_value, ex=expire_time)
            logger.debug(f"Cache SET: {cache_key} (TTL: {expire_time}s)")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
    def get(self, key: str, prefix: str = "cache") -> Optional[Any]:
        """Get a value from cache"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            
            value = client.get(cache_key)
            if value is not None:
                logger.debug(f"Cache HIT: {cache_key}")
                return self._deserialize_value(value)
            
            logger.debug(f"Cache MISS: {cache_key}")
            return None
        except Exception as e:
            logger.error(f"Cache GET error: {e}")
            return None
    
    def delete(self, key: str, prefix: str = "cache") -> bool:
        """Delete a value from cache"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            
            result = client.delete(cache_key)
            logger.debug(f"Cache DELETE: {cache_key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Cache DELETE error: {e}")
            return False
    
    def exists(self, key: str, prefix: str = "cache") -> bool:
        """Check if key exists in cache"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            return bool(client.exists(cache_key))
        except Exception as e:
            logger.error(f"Cache EXISTS error: {e}")
            return False
    
    def get_ttl(self, key: str, prefix: str = "cache") -> int:
        """Get remaining TTL for a key"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            return client.ttl(cache_key)
        except Exception as e:
            logger.error(f"Cache TTL error: {e}")
            return -1
    
    def set_hash(self, key: str, mapping: Dict[str, Any], ttl: Optional[int] = None, prefix: str = "hash") -> bool:
        """Set hash values in cache"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            
            # Serialize all values in mapping
            serialized_mapping = {}
            for field, value in mapping.items():
                serialized_mapping[field] = self._serialize_value(value)
            
            # Use regular SET for hash-like functionality with JSON
            client.set(cache_key, json.dumps(serialized_mapping), ex=ttl or self.default_ttl)
            logger.debug(f"Cache HSET: {cache_key}")
            return True
        except Exception as e:
            logger.error(f"Cache HSET error: {e}")
            return False
    
    def get_hash(self, key: str, field: Optional[str] = None, prefix: str = "hash") -> Union[Dict[str, Any], Any, None]:
        """Get hash values from cache"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            
            value = client.get(cache_key)
            if value is None:
                return None
            
            hash_data = json.loads(value)
            
            # Deserialize all values
            deserialized_hash = {}
            for field_name, field_value in hash_data.items():
                deserialized_hash[field_name] = self._deserialize_value(field_value)
            
            if field:
                return deserialized_hash.get(field)
            
            logger.debug(f"Cache HGET: {cache_key}")
            return deserialized_hash
        except Exception as e:
            logger.error(f"Cache HGET error: {e}")
            return None
    
    def increment(self, key: str, amount: int = 1, prefix: str = "counter") -> Optional[int]:
        """Increment a counter"""
        try:
            client = self._get_client()
            cache_key = self._generate_key(prefix, key)
            return client.incr(cache_key, amount)
        except Exception as e:
            logger.error(f"Cache INCR error: {e}")
            return None
    
    def clear_pattern(self, pattern: str, prefix: str = "cache") -> int:
        """Clear all keys matching pattern"""
        try:
            client = self._get_client()
            pattern_key = self._generate_key(prefix, pattern)
            
            keys = client.keys(pattern_key)
            if keys:
                return client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache CLEAR error: {e}")
            return 0
    
    def get_info(self) -> Dict[str, Any]:
        """Get cache information"""
        try:
            client = self._get_client()
            if hasattr(client, 'info'):
                info = client.info()
                return {
                    "connected": self._connected,
                    "redis_version": info.get("redis_version", "Unknown"),
                    "used_memory": info.get("used_memory_human", "Unknown"),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands_processed": info.get("total_commands_processed", 0)
                }
            else:
                return {
                    "connected": False,
                    "redis_version": "Mock",
                    "used_memory": "N/A",
                    "connected_clients": 1,
                    "total_commands_processed": 0
                }
        except Exception as e:
            logger.error(f"Cache INFO error: {e}")
            return {"connected": False, "error": str(e)}

# Decorators for caching

def cache_result(ttl: int = 300, prefix: str = "cache", key_func: Optional[callable] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Create key from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                key_str = "|".join(key_parts)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key, prefix)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl, prefix)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

def async_cache_result(ttl: int = 300, prefix: str = "cache", key_func: Optional[callable] = None):
    """Decorator to cache async function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache = RedisCache()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Create key from function name and arguments
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                key_str = "|".join(key_parts)
                cache_key = hashlib.md5(key_str.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key, prefix)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl, prefix)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

# Global cache instance
cache = RedisCache()