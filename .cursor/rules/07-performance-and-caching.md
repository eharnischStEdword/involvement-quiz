# Performance & Caching

- Cache expensive computations with Flask-Caching and set sensible expirations.
- Optimize database queries; use indexing and avoid N+1 patterns.
- Reuse pooled connections and close them quickly.
- Offload heavy work to background tasks (e.g., Celery or scripts).
- Avoid redundant computation and prefer iteration over duplication.
- Apply rate limiting (default: 5 submissions/hour/IP) to submission endpoints; on exceed return 429 with {"error":"rate_limited"}.
- Never cache admin pages, exports, or diagnostic endpoints; add Cache-Control: no-store.
- Add metrics export for cache size (bytes) and database pool usage.