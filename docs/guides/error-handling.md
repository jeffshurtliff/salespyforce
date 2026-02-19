# Error Handling

This guide covers practical error-handling patterns for `salespyforce`,
including:

- How API errors are currently surfaced by the library
- How to add safe retries in your application code
- How to collect useful diagnostics during failures
- Gaps in current behavior that are good candidates for future releases

Before applying these patterns, make sure your client is configured correctly.
See [Authentication](authentication.md) and [Quickstart](../getting-started/quickstart.md).

## Error Types You Should Expect

In current `salespyforce` releases, API failures can appear in a few forms:

- `RuntimeError` from API helper methods when Salesforce returns HTTP status
  `>= 300` (for example, `get()`, `post()`, `patch()`, `put()`, `delete()`).
- `requests` exceptions (for example, connection or timeout errors) can bubble
  up directly in places where they are not wrapped.
- Library-specific exceptions from
  [`salespyforce.errors.exceptions`](../reference/exceptions.rst), such as:
  - `InvalidURLError`
  - `MissingRequiredDataError`
  - `InvalidParameterError`
  - `DataMismatchError`
  - `APIRequestError` (used in selected flows, such as
    `retrieve_current_user_info(..., raise_exc_on_error=True)`)

For reference details, see [Exception Classes](../reference/exceptions.rst) and
[Client API](../reference/client.rst).

## Base Handling Pattern

Use a layered `try/except` approach:

- Catch library-specific exceptions first for validation and misuse cases.
- Catch `requests.RequestException` next for transport/network failures.
- Catch `RuntimeError` for HTTP error responses surfaced by current API methods.
- Add a final broad fallback to ensure your application does not silently fail.

```python
import logging
import requests

from salespyforce import Salesforce
from salespyforce.errors import exceptions as spf_exc

logger = logging.getLogger(__name__)

sfdc = Salesforce(helper="/path/to/helper.yml")

try:
    result = sfdc.soql_query("SELECT Id, Name FROM Account LIMIT 5")
except spf_exc.SalesPyForceError as exc:
    logger.error("SalesPyForce validation/domain error: %s", exc)
    raise
except requests.RequestException as exc:
    logger.error("Network/transport error calling Salesforce: %s", exc)
    raise
except RuntimeError as exc:
    logger.error("Salesforce API returned an error response: %s", exc)
    raise
except Exception as exc:
    logger.exception("Unexpected failure: %s", exc)
    raise
```

## Retry Strategy

`salespyforce` does not currently implement built-in retry/backoff behavior for
API calls. In production workloads, implement retries in your application layer.

### What To Retry

Retry only transient failures, such as:

- Transport exceptions (`requests.ConnectionError`, `requests.Timeout`)
- HTTP `429` (rate limiting)
- HTTP `5xx` responses

Do not blindly retry all `4xx` responses (many are permanent input/auth issues).

### Idempotency Guidance

- Safest to retry: `GET`, read-only operations (`soql_query`, `search_string`).
- Retry with caution: `PATCH`, `PUT`, `DELETE` (usually idempotent with same
  target/payload assumptions, but validate business impact).
- Be careful with `POST` creates: retries can create duplicates unless you add
  deduplication or idempotency controls in your integration design.

### Example Retry Wrapper (Exponential Backoff)

```python
import random
import time
import requests

from salespyforce import Salesforce


def call_with_retry(func, *, attempts=4, base_delay=0.5, max_delay=8.0):
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except requests.RequestException:
            if attempt == attempts:
                raise
        except RuntimeError as exc:
            message = str(exc)
            transient = any(code in message for code in (" 429 ", " 500 ", " 502 ", " 503 ", " 504 "))
            if not transient or attempt == attempts:
                raise
        sleep_seconds = min(max_delay, base_delay * (2 ** (attempt - 1)))
        sleep_seconds += random.uniform(0, 0.2 * sleep_seconds)  # jitter
        time.sleep(sleep_seconds)


sfdc = Salesforce(helper="/path/to/helper.yml")
accounts = call_with_retry(
    lambda: sfdc.soql_query("SELECT Id, Name FROM Account ORDER BY LastModifiedDate DESC LIMIT 50")
)
```

## Diagnostics And Observability

When handling failures, collect enough context to debug quickly:

- Operation metadata: method, endpoint, object type, record ID, query shape.
- Timing metadata: timeout used, start/end timestamps, retry attempt number.
- Salesforce context: org identifier, API version, user ID (if available).
- Error data: exception class, message, and traceback.

### Avoid Logging Secrets

Do not log:

- Access tokens
- Passwords/security tokens
- Connected app client secrets
- Full request payloads that contain PII unless sanitized

### Recommended Logging Practices

- Configure application logging centrally and include structured fields.
- Keep `show_full_error=True` for debugging environments.
- Use `show_full_error=False` when error bodies might expose sensitive data.
- For raw response diagnostics, call low-level methods with `return_json=False`
  and inspect `status_code`, headers, and body safely.

Reference utility APIs: [Utilities](../reference/utilities.rst).

## Timeouts

The API helper methods support a `timeout` parameter (default `30` seconds).
Tune this per operation:

- Lower timeout for frequent, interactive reads.
- Higher timeout for large/slow operations where appropriate.

Example:

```python
result = sfdc.get(
    endpoint=f"/services/data/{sfdc.version}/limits",
    timeout=15,
    show_full_error=False,
)
```

## Practical Checklist

- Use targeted exception handling (`SalesPyForceError`, `requests`, `RuntimeError`).
- Implement retry with exponential backoff + jitter for transient failures.
- Restrict retries to operations that are safe in your business context.
- Set explicit timeouts for long-running or latency-sensitive operations.
- Log structured diagnostics, but redact credentials and sensitive payload data.
- Alert on persistent `429` and `5xx` patterns.

:::{seealso}
- [Authentication](authentication.md)
- [Querying](querying.md)
- [Quickstart](../getting-started/quickstart.md)
- [Client API Reference](../reference/client.rst)
- [Exceptions Reference](../reference/exceptions.rst)
- [Utilities Reference](../reference/utilities.rst)
- [Changelog](../CHANGELOG.md)
:::
