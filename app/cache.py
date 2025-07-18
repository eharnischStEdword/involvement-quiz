# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import json
import hashlib
import time
from functools import wraps
from typing import Any, Optional, Callable
import logging

from app.logging_config import get_logger

logger = get_logger(__name__)

class CacheManager:
    """Simple caching manager with fallback to in-memory cache"""
    
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}
        self.cache_ttl = 300  # 5 minutes default
        
        # Use in-memory cache only for simplicity
        logger.info("Using in-memory cache")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Use memory cache only
            if key in self.memory_cache:
                data = self.memory_cache[key]
                if time.time() < data['expires']:
                    return data['value']
                else:
                    # Expired, remove it
                    del self.memory_cache[key]
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache with TTL"""
        try:
            # Use memory cache only
            ttl_seconds = ttl or self.cache_ttl
            self.memory_cache[key] = {
                'value': value,
                'expires': time.time() + ttl_seconds
            }
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self.memory_cache:
                del self.memory_cache[key]
            return True
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            self.memory_cache.clear()
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return key in self.memory_cache and time.time() < self.memory_cache[key]['expires']
        except Exception as e:
            logger.warning(f"Cache exists error: {e}")
            return False

# Global cache instance
cache_manager = CacheManager()

def cached(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {prefix}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {prefix}, stored result")
            
            return result
        return wrapper
    return decorator

def cache_ministries(func: Callable) -> Callable:
    """Specialized decorator for ministry data caching"""
    return cached('ministries', ttl=600)(func)  # 10 minutes for ministry data

def cache_submissions(func: Callable) -> Callable:
    """Specialized decorator for submission data caching"""
    return cached('submissions', ttl=300)(func)  # 5 minutes for submission data

def invalidate_ministry_cache():
    """Invalidate all ministry-related cache"""
    try:
        if cache_manager.redis_client:
            # Delete all keys starting with 'ministries:'
            keys = cache_manager.redis_client.keys('ministries:*')
            if keys:
                cache_manager.redis_client.delete(*keys)
        else:
            # Clear memory cache keys starting with 'ministries:'
            keys_to_delete = [k for k in cache_manager.memory_cache.keys() if k.startswith('ministries:')]
            for key in keys_to_delete:
                del cache_manager.memory_cache[key]
        
        logger.info("Ministry cache invalidated")
    except Exception as e:
        logger.warning(f"Failed to invalidate ministry cache: {e}")

def get_cache_stats() -> dict:
    """Get cache statistics"""
    try:
        if cache_manager.redis_client:
            info = cache_manager.redis_client.info()
            return {
                'type': 'redis',
                'connected_clients': info.get('connected_clients', 0),
                'used_memory_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0)
            }
        else:
            return {
                'type': 'memory',
                'cache_size': len(cache_manager.memory_cache),
                'memory_usage': 'N/A'
            }
    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")
        return {'type': 'unknown', 'error': str(e)} 