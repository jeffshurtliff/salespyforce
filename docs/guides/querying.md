# Querying Data

This guide covers data retrieval with the `salespyforce.Salesforce` client
using:

- `soql_query()` for structured record queries (SOQL)
- `search_string()` for text search (SOSL `FIND { ... }`)

Before querying, make sure your client is authenticated. See
[Authentication](authentication.md) for setup details.

## SOQL Queries With `soql_query()`

Use `soql_query()` when you know which object and fields you want to query.

```python
from salespyforce import Salesforce

sfdc = Salesforce(helper="/path/to/helper.yml")

query = """
SELECT Id, Name, Industry, LastModifiedDate
FROM Account
WHERE IsDeleted = false
ORDER BY LastModifiedDate DESC
LIMIT 10
"""

result = sfdc.soql_query(query)

print(f"Done: {result.get('done')}")
print(f"Total size: {result.get('totalSize')}")
for row in result.get("records", []):
    print(row["Id"], row.get("Name"), row.get("Industry"))
```

Typical SOQL response keys include:

- `totalSize`: Number of records matched by the query.
- `done`: `True` when all available rows for this request are included.
- `records`: A list of records.
- `nextRecordsUrl`: Present when additional rows are available.

:::{seealso}
- [Quickstart](../getting-started/quickstart.md) for a minimal SOQL example.
- [Client API Reference](../reference/client.rst) for full method docs.
:::

## SOQL Pagination (`nextRecordsUrl`)

For larger result sets, Salesforce may return a partial page with
`nextRecordsUrl`. Pass that URL back to `soql_query()` with
`next_records_url=True`.

```python
query = """
SELECT Id, Name
FROM Contact
ORDER BY CreatedDate DESC
"""

response = sfdc.soql_query(query)
all_records = response.get("records", [])

while not response.get("done"):
    response = sfdc.soql_query(
        query=response["nextRecordsUrl"],
        next_records_url=True,
    )
    all_records.extend(response.get("records", []))

print(f"Collected {len(all_records)} contacts")
```

## SOQL Quote Handling (`replace_quotes`)

By default, `soql_query()` replaces double quotes (`"`) with single quotes
(`'`) before sending the query (`replace_quotes=True`).

In most cases, this is convenient. If your query text must preserve double
quotes exactly, disable this behavior:

```python
query = 'SELECT Id FROM Account WHERE Name = "Acme"'
result = sfdc.soql_query(query, replace_quotes=False)
```

:::{note}
Prefer standard SOQL string literals (single quotes) unless you have a specific
reason to preserve double quotes in the outgoing query string.
:::

## SOSL Searches With `search_string()`

Use `search_string()` for keyword-style search across supported objects.

```python
from salespyforce import Salesforce

sfdc = Salesforce(helper="/path/to/helper.yml")
result = sfdc.search_string("Acme")

for record in result.get("searchRecords", []):
    print(record.get("attributes", {}).get("type"), record.get("Id"), record.get("Name"))
```

`search_string()` constructs a SOSL query in the form:

- `FIND {<your search string>}`

Use this method when you want quick full-text style search behavior without
writing SOSL manually.

## Choosing SOQL vs SOSL

- Use `soql_query()` when you need precise filtering, selected fields, sorting,
  and predictable object-specific queries.
- Use `search_string()` when you need text search for records matching a term
  across searchable fields/objects.

## Troubleshooting Query Results

- If you receive authentication errors, confirm your client setup in
  [Authentication](authentication.md).
- If queries fail at runtime, review exception guidance in
  [Error Handling](error-handling.md).
- If expected rows are missing, verify object/field permissions for the API user.

## Next Steps

- Continue to [Error Handling](error-handling.md) for exception handling patterns.
- Review [Client API Reference](../reference/client.rst) for method-level details.
