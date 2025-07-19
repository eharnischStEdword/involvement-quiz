# Memory Leak Fixes - St. Edward Ministry Finder

## Overview
This document outlines the memory leak fixes implemented to address the 2GB memory usage issue identified in the application.

## Root Causes Identified

### 1. Unbounded In-Memory Cache
- **Issue**: Cache could grow to unlimited size with no memory-based limits
- **Impact**: Large objects stored in cache could consume significant memory
- **Fix**: Added memory monitoring and limits to `CacheManager`

### 2. Global Variables Accumulating Data
- **Issue**: Login attempts, request monitoring, and other tracking data grew indefinitely
- **Impact**: Memory usage increased over time without cleanup
- **Fix**: Added periodic cleanup and size limits

### 3. Database Connection Pool Issues
- **Issue**: No connection timeouts could lead to hanging connections
- **Impact**: Connections not properly returned to pool
- **Fix**: Added connection timeouts and better error handling

### 4. Keep-Alive Service Inefficiency
- **Issue**: Multiple HTTP requests without proper cleanup
- **Impact**: Request objects and responses not freed
- **Fix**: Optimized to single endpoint with explicit cleanup

## Fixes Implemented

### 1. Enhanced Cache Management (`app/cache.py`)
```python
# Added memory monitoring
self.max_memory_mb = 50  # Maximum 50MB for cache
self.cleanup_interval = 60  # Cleanup every 60 seconds

# Added memory usage tracking
def _get_memory_usage(self) -> float:
    cache_size = len(str(self.memory_cache))
    return cache_size / (1024 * 1024)  # Convert to MB

# Added periodic cleanup
def _should_cleanup(self) -> bool:
    return (current_time - self.last_cleanup) > self.cleanup_interval
```

**Changes:**
- Reduced max cache size from 1000 to 500 entries
- Added 50MB memory limit for cache
- Added periodic cleanup every 60 seconds
- Added memory usage monitoring and logging

### 2. Login Attempt Cleanup (`app/auth.py`)
```python
# Added cleanup configuration
MAX_TRACKED_IPS = 1000  # Maximum number of IPs to track
CLEANUP_INTERVAL = 3600  # Cleanup every hour

# Added periodic cleanup function
def cleanup_old_attempts():
    # Remove old attempts from all IPs
    # Limit number of tracked IPs
    # Clean up expired data
```

**Changes:**
- Added maximum limit of 1000 tracked IPs
- Added hourly cleanup of old login attempts
- Added automatic cleanup of expired data
- Improved memory management for login tracking

### 3. Monitoring System Optimization (`app/monitoring.py`)
```python
# Added memory management
self.max_error_counts = 100  # Maximum number of error types to track
self.cleanup_interval = 300  # Cleanup every 5 minutes

# Added cleanup function
def _cleanup_old_data(self):
    # Limit response times array
    # Limit request counts
    # Limit error counts
```

**Changes:**
- Added maximum limits for all tracking arrays
- Added 5-minute cleanup interval
- Added automatic cleanup of old monitoring data
- Added memory usage reporting

### 4. Database Connection Improvements (`app/database.py`)
```python
# Added connection timeouts
_connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn, maxconn, DATABASE_URL,
    sslmode='require',
    connect_timeout=10,  # 10 second connection timeout
    options='-c statement_timeout=30000'  # 30 second query timeout
)
```

**Changes:**
- Added 10-second connection timeout
- Added 30-second query timeout
- Added null checks for connection pool
- Improved error handling

### 5. Keep-Alive Service Optimization (`main.py`)
```python
# Simplified to single endpoint
try:
    response = requests.get(f'{url}/api/health', timeout=10)
    logger.info(f"Keep-alive ping to {url}/api/health - Status: {response.status_code}")
    # Explicitly close response to free memory
    response.close()
except Exception as e:
    logger.warning(f"Keep-alive ping failed: {e}")
```

**Changes:**
- Reduced from 3 endpoints to 1 endpoint
- Added explicit response cleanup
- Reduced timeout from 15 to 10 seconds
- Improved error handling

### 6. Memory Monitoring Tools

#### Memory Monitoring Script (`scripts/memory_monitor.py`)
- Real-time memory usage tracking
- Process and system memory monitoring
- Cache and monitoring data size tracking
- Configurable monitoring intervals

#### Memory Status API Endpoint (`/api/memory-status`)
- Current memory usage information
- Cache statistics
- Monitoring data sizes
- System memory information

## Expected Results

### Memory Usage Reduction
- **Before**: 2GB+ memory usage
- **After**: Expected 100-500MB normal usage
- **Cache Limit**: Maximum 50MB for cache
- **Monitoring Data**: Limited to prevent unbounded growth

### Performance Improvements
- **Response Times**: Should improve due to reduced memory pressure
- **CPU Usage**: Should decrease due to less garbage collection
- **Stability**: Reduced risk of out-of-memory crashes

### Monitoring Capabilities
- **Real-time Tracking**: Memory usage can be monitored via API
- **Alerts**: High memory usage warnings in logs
- **Debugging**: Detailed memory breakdown available

## Monitoring Commands

### Check Current Memory Status
```bash
# Using the monitoring script
python scripts/memory_monitor.py --status

# Using the API endpoint
curl https://involvement-quiz.onrender.com/api/memory-status
```

### Monitor Memory Over Time
```bash
# Monitor for 1 hour with 30-second intervals
python scripts/memory_monitor.py --interval 30 --duration 3600

# Monitor indefinitely with 60-second intervals
python scripts/memory_monitor.py --interval 60
```

## Verification Steps

1. **Deploy Changes**: Deploy the updated code to production
2. **Monitor Memory**: Use the memory monitoring tools to track usage
3. **Check Logs**: Look for memory cleanup and warning messages
4. **Verify Stability**: Ensure application remains stable over time
5. **Performance Test**: Verify response times have improved

## Future Improvements

1. **Redis Integration**: Consider moving cache to Redis for better scalability
2. **Memory Profiling**: Add detailed memory profiling for deeper analysis
3. **Automatic Scaling**: Implement automatic scaling based on memory usage
4. **Alerting**: Add automated alerts for high memory usage

## Notes

- All changes are backward compatible
- No breaking changes to existing functionality
- Monitoring tools are optional and can be disabled
- Memory limits can be adjusted based on actual usage patterns 