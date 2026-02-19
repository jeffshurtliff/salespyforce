# Quickstart

This quickstart shows the fastest path to:

1. Import `salespyforce`
2. Instantiate a `Salesforce` client
3. Run a SOQL query
4. Perform a basic record operation

For setup and environment requirements, see [Overview](overview.md) and
[Installation](installation.md).

## 1. Import The Package

```python
import salespyforce
from salespyforce import Salesforce

print(salespyforce.__version__)
```

## 2. Instantiate A Client

Use a helper file for local development and automation so credentials stay out
of your source code.

```python
from salespyforce import Salesforce

sfdc = Salesforce(helper="/path/to/helper.yml")
print(f"Connected to {sfdc.instance_url} using API {sfdc.version}")
```

You can also pass credentials directly:

```python
from salespyforce import Salesforce

sfdc = Salesforce(
    username="admin.user@example.com",
    password="example123",
    org_id="4DJ000000CeMFYA0",
    base_url="https://example-dev-ed.lightning.force.com/",
    endpoint_url="https://example-dev-ed.my.salesforce.com/services/oauth2/token",
    client_id="3MVG9gTv.DiE8cKRIpEtSN_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    client_secret="7536F4A7865559XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    security_token="2muXaXXXXXXXXXXXXXXXoVKxz",
)
```

:::{tip}
Need help choosing the authentication pattern? See
[Authentication Guide](../guides/authentication.md).
:::

## 3. Run A SOQL Query

Use `soql_query()` to fetch records from Salesforce:

```python
query = """
SELECT Id, Name
FROM Account
ORDER BY LastModifiedDate DESC
LIMIT 5
"""

result = sfdc.soql_query(query)

print(f"Total rows returned: {result['totalSize']}")
for row in result.get("records", []):
    print(row["Id"], row.get("Name"))
```

## 4. Perform A Record Operation

Create a record with `create_sobject_record()`:

```python
payload = {"Name": "Acme - Quickstart Demo"}
create_result = sfdc.create_sobject_record("Account", payload)

if create_result.get("success"):
    account_id = create_result["id"]
    print(f"Created Account: {account_id}")
```

Optionally update the same record:

```python
update_payload = {"Description": "Updated by salespyforce quickstart"}
sfdc.update_sobject_record("Account", account_id, update_payload)
print("Account updated.")
```

## Where To Go Next

- Authentication details and helper-file formats:
  [Authentication Guide](../guides/authentication.md)
- Query patterns and additional examples:
  [Querying Guide](../guides/querying.md)
- API errors, exceptions, and diagnostics:
  [Error Handling Guide](../guides/error-handling.md)
- Client and method reference:
  [Client API Reference](../reference/client.rst)
