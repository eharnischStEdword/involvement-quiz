# Testing

- Use `pytest` with the Flask test client for unit and integration tests.
- Create fixtures for the app, database, and common payloads.
- Run `python -m pytest tests/ -v` before committing.
- Avoid network calls or external state in tests; keep them deterministic.
- Aim for thorough coverage of validators, routes, and edge cases.
- Add tests to verify:
  - /api/health returns {"status","version","uptime_s"} and includes Cache-Control: no-store.
  - Submissions: first 5 requests return 201; the 6th within an hour returns 429.
  - Admin routes: 401 without credentials, 200 with correct credentials, and CSV export includes expected headers.
  - At least one public GET response includes all required security headers.
- Maintain minimum 80% coverage; fail CI if below threshold.