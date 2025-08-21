# Routing & Blueprints

- Organize endpoints by blueprint under `app/blueprints/`.
- Use Flask-RESTful or class-based views for REST APIs.
- Export routes and resources with explicit names for easy imports.
- Keep route handlers thin; delegate work to services, validators, or utilities.
- Apply consistent blueprint names and URL prefixes (e.g., `api`, `public`, `admin`).
