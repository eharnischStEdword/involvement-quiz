# Validation & Serialization

- Validate input at the start of functions using guard clauses and early returns.
- Use Marshmallow schemas or dedicated validator functions for request data.
- Sanitize and normalize user input (strip, lowercase, remove unsafe characters).
- Return structured errors with helpful messages; log validation failures.
- Serialize responses via schemas or explicit dicts following the RORO pattern.
