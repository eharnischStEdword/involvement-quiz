# Security & Auth

- Enforce HTTPS and a strict Content Security Policy via Talisman in production.
- Store secrets in environment variables and validate them at startup.
- Use Flask-JWT-Extended or session-based auth with hashed passwords.
- Apply CSRF protection for state-changing requests.
- Rate-limit login attempts and log all security-relevant events.
