# Testing

SalesPyForce tests live in the repository root `tests/` directory.

## Run the Test Suite

Install dependencies and run all tests:

```bash
poetry install
poetry run pytest -q
```

## Integration Tests

Integration tests are opt-in and require helper credentials. To include them:

```bash
poetry run pytest --integration -q
```

If no helper file is available, integration tests are skipped automatically.

## Coverage

Run coverage locally with:

```bash
poetry run python -m pip install --upgrade pytest-cov
poetry run pytest --cov-report=xml --cov=salespyforce tests/ --color=yes
```
