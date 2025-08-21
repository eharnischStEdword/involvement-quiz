# Testing

- Use `pytest` with the Flask test client for unit and integration tests.
- Create fixtures for the app, database, and common payloads.
- Run `python -m pytest tests/ -v` before committing.
- Avoid network calls or external state in tests; keep them deterministic.
- Aim for thorough coverage of validators, routes, and edge cases.
