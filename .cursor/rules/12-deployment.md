# Deployment

- Use Gunicorn or uWSGI as the production WSGI server.
- Configure environments via `Config` and environment variables; fail fast if required vars are missing.
- Enable automatic migrations on startup and verify database connectivity.
- Collect structured logs and metrics in production (e.g., Render.com dashboards).
