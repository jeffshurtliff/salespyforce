# Testing

SalesPyForce tests are organized into:

- `tests/unit/` for fast, deterministic unit tests
- `tests/integration/` for opt-in tests that require real helper credentials

## Run the Test Suite

Install dependencies and run all tests:

```bash
poetry install
poetry run pytest -q
```

Run only unit tests:

```bash
poetry run pytest tests/unit -q
```

## Integration Tests

Integration tests are opt-in and require helper credentials. To include them:

```bash
poetry run pytest --integration tests/integration -q
```

If no helper file is available, integration tests are skipped automatically.

## Coverage

Run coverage locally with:

```bash
poetry run pytest --cov-report=xml --cov=salespyforce tests/unit tests/integration --color=yes
```
