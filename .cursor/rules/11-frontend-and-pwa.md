# Frontend & PWA

- Place templates in `templates/` and static assets in `static/` with `lower_snake_case` names.
- Maintain PWA assets (`sw.js`, manifest) and ensure service workers run over HTTPS.
- Keep the UI mobile-first and accessible; test the `/pwa-test` route for debugging.
- Serve only sanitized data to templates to avoid XSS.
- Serve sw.js with Cache-Control: no-cache, must-revalidate.
- The service worker must never cache admin routes (/admin*), CSV exports (/api/export*), or diagnostics (/api/memory-status*, /api/metrics*, /api/debug*).
- Public pages may be cached offline; admin pages must remain online-only.