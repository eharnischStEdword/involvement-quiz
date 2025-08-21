# Python & Flask Core

- Use `def` with type hints for all functions.
- Prefer functional, declarative code; limit classes to Flask views or lightweight data containers.
- Build the app with the factory pattern (`create_app`) and register blueprints inside it.
- Load configuration from `Config` and environment variables; avoid hard-coded settings.
- Pass dependencies explicitly or via `current_app`; avoid global state.
- Use descriptive variable names and the RORO (Receive an Object, Return an Object) pattern.
