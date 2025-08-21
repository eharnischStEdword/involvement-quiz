# Style & Conventions

- **Functional > OO** (except Flask views where reasonable).
- **Type hints** everywhere; return `TypedDict`/`dataclass` if needed, but prefer plain dicts with typed signatures (RORO).
- **Names**: `lower_snake_case` for files, modules, funcs. Use auxiliary-verb flags: `is_active`, `has_permission`, `should_cache`.
- **Structure**: keep logic small and composable; avoid duplication; push shared logic to `app/utils.py`.
- **Control flow**: guard-clauses first; early return on invalid states; keep “happy path” last; avoid unnecessary `else`.
- **I/O boundaries**: routes = thin; services/validators/utilities = thick.
- **No hidden globals**. Pass dependencies explicitly via params or `current_app.config`.
- **Logging**: use `current_app.logger` with structured context (`extra={...}`) and levels.
- **Docstrings**: short, top-level purpose + constraints; include input validation expectations.

**Example (early return + RORO):**
```python
from typing import TypedDict, Optional

class MatchRequest(TypedDict):
    age: int
    gender: str
    state: str
    situation: str
    interests: list[str]

class MatchResult(TypedDict):
    ministries: list[dict]
    debug: dict

def get_matches(payload: MatchRequest) -> MatchResult:
    if not payload.get("age") or payload["age"] < 0:
        return {"ministries": [], "debug": {"error": "invalid_age"}}
    # ... rest of logic
    return {"ministries": ministries, "debug": {"rule_version": 2}}
