# Cursor Rules Index

These rules are **authoritative** for this repo. Prefer functional Python, Flask app-factory + blueprints, strict validation, early-returns, and small, testable units. Do not introduce new stacks without explicit instruction.

**Project map (from README)**:
- `app/` (app factory, config, database pool, cache, monitoring, auth, models, validators, utils, blueprints/*)  
- `scripts/` (monitoring utilities)  
- `templates/`, `static/`, `sw.js` (PWA)  
- Deployment: Render.com; production env vars required.  [oai_citation:1‡GitHub](https://github.com/eharnischStEdword/involvement-quiz)

**Rule groups**:
- 01 Style & Conventions
- 02 Python / Flask Core
- 03 Routing & Blueprints
- 04 Validation & Serialization
- 05 Database & Migrations
- 06 Security & Auth
- 07 Performance & Caching
- 08 Monitoring & Ops
- 09 Testing
- 10 API Docs
- 11 Frontend & PWA
- 12 Deployment
- 13 Refactors & Safety Rails
- 99 Cursor Task Recipes


- Always prefer small diffs; never broaden route behavior without tests.
- App factory is authoritative; blueprints live under app/blueprints/*.py and contain only routing wiring.
- Use guard clauses, early returns; avoid else-after-return; type-hint all public fns.
- Never introduce user PII fields; validators must reject unknown fields.
