# Monitoring & Ops

- Use `current_app.logger` for structured logs with context.
- Expose health, memory, and metrics endpoints for remote monitoring.
- Utilize scripts in `scripts/` (e.g., `memory_monitor.py`) for performance tracking.
- Watch key metrics: response time, memory, CPU, and database connections.
- Ensure teardown hooks clean up resources and connections.
- /api/health must always return JSON: {"status":"ok","version":<env GIT_SHA or "dev">,"uptime_s":<int>} with Cache-Control: no-store.
- /api/memory-status, /api/metrics, and /api/debug/* must only be exposed if ENABLE_DIAGNOSTICS=true AND user is admin; otherwise return 404.
- /api/metrics must return exactly:
  {
    "uptime_s": <int>,
    "p95_ms": <int|null>,
    "cache_bytes": <int>,
    "db_pool_in_use": <int>
  }