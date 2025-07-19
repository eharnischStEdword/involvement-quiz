# © 2024–2025 Harnisch LLC. All Rights Reserved.
# Licensed exclusively for use by St. Edward Church & School (Nashville, TN).
# Unauthorized use, distribution, or modification is prohibited.

import json
import hashlib
import time
import sys
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
        self.max_cache_size = 500  # Reduced from 1000 to 500
        self.max_memory_mb = 50  # Maximum 50MB for cache
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # Cleanup every 60 seconds
        
        # Use in-memory cache only for simplicity
        logger.info("Using in-memory cache")
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage of cache in MB"""
        try:
            # Estimate memory usage by serializing cache
            cache_size = len(str(self.memory_cache))
            return cache_size / (1024 * 1024)  # Convert to MB
        except Exception:
            return 0.0
    
    def _should_cleanup(self) -> bool:
        """Check if cleanup is needed"""
        current_time = time.time()
        return (current_time - self.last_cleanup) > self.cleanup_interval
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Periodic cleanup
            if self._should_cleanup():
                self._cleanup_expired()
            
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
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            # Use memory cache only
            ttl_seconds = ttl if ttl is not None else self.cache_ttl
            
            # Clean expired entries first
            self._cleanup_expired()
            
            # Check memory usage
            current_memory = self._get_memory_usage()
            if current_memory > self.max_memory_mb:
                logger.warning(f"Cache memory usage {current_memory:.1f}MB exceeds limit {self.max_memory_mb}MB, clearing cache")
                self.clear()
                return False
            
            # Check cache size limit
            if len(self.memory_cache) >= self.max_cache_size:
                # Remove oldest entries (LRU-like behavior)
                oldest_keys = sorted(self.memory_cache.keys(), 
                                   key=lambda k: self.memory_cache[k].get('created', 0))[:50]  # Remove 50 at a time
                for old_key in oldest_keys:
                    del self.memory_cache[old_key]
                logger.debug(f"Cache size limit reached, removed {len(oldest_keys)} old entries")
            
            self.memory_cache[key] = {
                'value': value,
                'expires': time.time() + ttl_seconds,
                'created': time.time()
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
            self.last_cleanup = time.time()
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
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        try:
            current_time = time.time()
            expired_keys = [
                key for key, data in self.memory_cache.items()
                if current_time >= data['expires']
            ]
            for key in expired_keys:
                del self.memory_cache[key]
            
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            self.last_cleanup = current_time
        except Exception as e:
            logger.warning(f"Cache cleanup error: {e}")

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
            memory_usage = cache_manager._get_memory_usage()
            return {
                'type': 'memory',
                'cache_size': len(cache_manager.memory_cache),
                'memory_usage_mb': round(memory_usage, 2),
                'max_memory_mb': cache_manager.max_memory_mb,
                'max_cache_size': cache_manager.max_cache_size
            }
    except Exception as e:
        logger.warning(f"Failed to get cache stats: {e}")
        return {'type': 'unknown', 'error': str(e)} 