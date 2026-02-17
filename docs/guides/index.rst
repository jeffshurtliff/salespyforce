Guides
======

Use this section for task-focused walkthroughs once your environment is set up.
These guides show practical patterns for authenticating, querying Salesforce
data, and handling failures in production-oriented workflows.

If you are new to these workflows, follow this order:

1. Read :doc:`authentication` to configure client credentials safely.
2. Continue with :doc:`querying` for SOQL and SOSL retrieval patterns.
3. Finish with :doc:`error-handling` for retries, diagnostics, and exception strategy.

This section is designed to help you:

- Choose a secure authentication pattern for scripts and applications.
- Query records efficiently, including pagination and search use cases.
- Build resilient integrations with explicit error handling and retries.

For first-time package setup, start with :doc:`../getting-started/index`.
For API and exception details, see :doc:`../reference/index`.
For release history, see :doc:`../CHANGELOG`.

.. toctree::
   :maxdepth: 1

   authentication
   querying
   error-handling
