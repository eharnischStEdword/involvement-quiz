# Database & Migrations

- Use Flask-SQLAlchemy for ORM models in `app/models.py`.
- Manage schema changes with Flask-Migrate; run migrations on startup in production.
- Reuse connections through pooling (`app/database.py`) and close sessions promptly.
- Keep queries parameterized; prefer ORM relationships over raw SQL where possible.
- Index frequently queried columns and document migration steps.
