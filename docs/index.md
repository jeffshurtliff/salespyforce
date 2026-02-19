# SalesPyForce Documentation

SalesPyForce is a Python package for working with Salesforce APIs through a
single, high-level client. This documentation covers setup, authentication
patterns, query workflows, error handling, and the complete API reference.

```{toctree}
:maxdepth: 1
:hidden:

getting-started/index
guides/index
reference/index
CHANGELOG
```

## At A Glance

- Purpose: Simplify Salesforce REST API interactions in Python
- Primary interface: `salespyforce.Salesforce`
- Supported Python versions: 3.9+
- License: MIT

## What You Can Do

With SalesPyForce, you can:

- Authenticate against Salesforce using direct credentials or a helper file
- Run SOQL and SOSL queries
- Create, retrieve, update, and delete Salesforce object records
- Access org metadata, REST resources, and API version details
- Work with Salesforce Chatter and Knowledge features

## Installation

```bash
pip install --upgrade salespyforce
```

## Quick Example

```python
from salespyforce import Salesforce

sfdc = Salesforce(helper="/path/to/helper.yml")

query = """
SELECT Id, Name
FROM Account
ORDER BY LastModifiedDate DESC
LIMIT 5
"""

result = sfdc.soql_query(query)
print(result.get("totalSize", 0))
```

For a complete walkthrough, see the {doc}`getting-started/quickstart` page.

## Documentation Map

### Getting Started

- {doc}`getting-started/overview`: Package capabilities and requirements
- {doc}`getting-started/installation`: Installation and environment setup
- {doc}`getting-started/quickstart`: Minimal end-to-end usage example

### Guides

- {doc}`guides/authentication`: Credential patterns and helper-file usage
- {doc}`guides/querying`: SOQL and SOSL examples and best practices
- {doc}`guides/error-handling`: Exceptions, diagnostics, and recovery patterns

### API Reference

- {doc}`reference/client`: `Salesforce` class and client-facing modules
- {doc}`reference/utilities`: Utility functions and helpers
- {doc}`reference/exceptions`: Exception classes and error helpers

### Project Information

- {doc}`CHANGELOG`: Release history and notable changes

## Project Links

- Source code: <https://github.com/jeffshurtliff/salespyforce>
- Package index: <https://pypi.org/project/salespyforce/>
- Issue tracker: <https://github.com/jeffshurtliff/salespyforce/issues>

## Disclaimer

SalesPyForce is an unofficial package and is not endorsed or supported by
[Salesforce Inc](https://www.salesforce.com).

```{note}
Previous documentation has been preserved in `docs_legacy/` for historical
reference.
```
