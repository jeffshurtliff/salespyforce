# Integration Test Layout

Place integration tests in this directory and mark them with `@pytest.mark.integration`.

Example:

```python
import pytest


@pytest.mark.integration
def test_sample_integration(salesforce_integration):
    assert salesforce_integration.base_url
```

Run integration tests with:

```bash
poetry run pytest --integration tests/integration -q
```
