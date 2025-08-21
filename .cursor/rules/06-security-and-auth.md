# Security & Auth

- Enforce HTTPS and a strict Content Security Policy via Talisman in production.
- Store secrets in environment variables and validate them at startup.
- Use Flask-JWT-Extended or session-based auth with hashed passwords.
- Apply CSRF protection for state-changing requests.
- Rate-limit login attempts and log all security-relevant events.
- Require security headers on every response:
  - Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - Referrer-Policy: strict-origin-when-cross-origin
- Generate a per-request CSP nonce and require `<script nonce="{{ csp_nonce() }}">` for all inline scripts.
- Clamp `SESSION_TIMEOUT` between 900 and 86400 seconds at startup; log warning once if clamped.
- Ensure admin/export endpoints return `Cache-Control: no-store`.