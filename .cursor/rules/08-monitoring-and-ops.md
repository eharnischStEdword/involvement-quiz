# Monitoring & Ops

- Use `current_app.logger` for structured logs with context.
- Expose health, memory, and metrics endpoints for remote monitoring.
- Utilize scripts in `scripts/` (e.g., `memory_monitor.py`) for performance tracking.
- Watch key metrics: response time, memory, CPU, and database connections.
- Ensure teardown hooks clean up resources and connections.
