# Cursor Task Recipes

## Add a new API endpoint
1. Create the route in the appropriate blueprint.
2. Implement validation and business logic in `app/` modules.
3. Add tests under `tests/` and update API documentation.
4. Run `python -m pytest tests/ -v` before committing.

## Update database schema
1. Modify models in `app/models.py` and create a migration.
2. Update validators and serializers as needed.
3. Apply migrations and run tests.

## Fix a bug
1. Reproduce the issue with a failing test.
2. Apply the smallest fix and add logging where helpful.
3. Ensure tests pass and update docs if behavior changes.
