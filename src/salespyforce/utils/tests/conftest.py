# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.utils.tests.conftest
:Synopsis:          Configuration for performing unit testing with pytest
:Usage:             Leveraged by pytest in test modules
:Example:           ``soql_response = salesforce_unit.soql_query(soql_statement)``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     13 Dec 2025

Pytest fixtures for ``salespyforce.utils.tests``.

This module centralizes helpers used across the test suite to avoid
repeated setup in individual test files. It introduces two key fixtures:

* ``salesforce_integration`` — Instantiates the real ``Salesforce``
  client when a helper file is available. Tests using this fixture are
  marked as ``integration`` and are skipped unless ``--integration`` is
  provided.
* ``salesforce_unit`` — Provides a lightweight stub that mimics the
  public API used by existing tests without performing any network I/O.

The goal is to make it easy to switch between fast, isolated unit tests
and opt-in integration runs against a real Salesforce org. Additional
fixtures can be added here to share common mocking or configuration.
"""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
from typing import Iterator

import pytest

from salespyforce.core import Salesforce

# Define constants
HELPER_FILE_NAME = "helper_dm_conn.yml"


# -----------------------------
# Pytest configuration hooks
# -----------------------------

def pytest_addoption(parser: pytest.Parser) -> None:
    """This function registers custom CLI options.

    .. version-added:: 1.4.0

    ``--integration`` enables tests that require access to a real
    Salesforce org. Keeping this opt-in protects routine runs from
    network or credential dependencies.
    """
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run tests that require a Salesforce helper file",
    )


def pytest_configure(config: pytest.Config) -> None:
    """This function declares custom markers so pytest will not warn during collection.

    .. version-added:: 1.4.0
    """
    config.addinivalue_line(
        "markers",
        "integration: marks tests that require a real Salesforce org",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """This function skips integration tests when ``--integration`` is not provided.

    .. version-added:: 1.4.0
    """
    if config.getoption("--integration"):
        return

    skip_integration = pytest.mark.skip(
        reason="requires --integration to run against a Salesforce org"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)


# -----------------------------
# Helper utilities
# -----------------------------

def _find_helper_file() -> Path | None:
    """This function locates a helper file in common locations used by this project.

    .. version-added:: 1.4.0
    """
    helper_locations = [
        Path(os.environ.get("HOME", "")) / "secrets" / HELPER_FILE_NAME,
        Path("local") / HELPER_FILE_NAME,
    ]
    for helper_path in helper_locations:
        if helper_path.is_file():
            return helper_path.resolve()
    return None


# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture(scope="session")
def integration_helper_file() -> Path:
    """This fixture returns the helper file path or skips the test if none is available.

    .. version-added:: 1.4.0

    Keeping this lookup in a session-scoped fixture ensures we only
    perform filesystem checks once per test run and provides a single
    source of truth for integration tests.
    """
    helper_path = _find_helper_file()
    if helper_path is None:
        pytest.skip("No Salesforce helper file found for integration tests")
    return helper_path


@pytest.fixture(scope="session")
def salesforce_integration(integration_helper_file: Path) -> Iterator[Salesforce]:
    """This fixture instantiates the real Salesforce client for integration tests.

    .. version-added:: 1.4.0

    The fixture is session-scoped to avoid repeated authentication and
    to reuse connections across tests. It is intended only for tests
    marked with ``@pytest.mark.integration``.
    """
    client = Salesforce(helper=str(integration_helper_file))
    yield client


@pytest.fixture()
def salesforce_unit(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """This fixture provides a lightweight stub that mimics the ``Salesforce`` API.

    .. version-added:: 1.4.0

    This fixture avoids network calls by supplying deterministic return
    values for the subset of methods exercised by the current tests.
    It can be extended as coverage grows to keep unit tests fast and
    self-contained.
    """
    # Minimal data used across tests
    sample_urls = {
        "base_url": "https://example.force.com",
        "rest_resources": {"metadata": "available"},
        "org_limits": {"DailyApiRequests": {"Remaining": 15000}},
        "sobjects": {"sobjects": []},
        "account": {
            "objectDescribe": {},
            "activateable": False,
        },
        "soql_result": {
            "done": True,
            "totalSize": 1,
            "records": [{"Id": "001XX000003NGqqYAG"}],
        },
        "sosl_result": {
            "searchRecords": [
                {"attributes": {"type": "Account"}, "Id": "001XX000003NGqqYAG"}
            ]
        },
    }

    def _create_response(**overrides):
        """This function creates an API response payload mimicking the Salesforce REST API responses.

        .. version-added:: 1.4.0
        """
        response = {"id": "001D000000IqhSLIAZ", "success": True, "errors": []}
        response.update(overrides)
        return response

    stub = SimpleNamespace()
    stub.base_url = sample_urls["base_url"]
    stub.get_api_versions = lambda: [{"version": "v65.0"}]
    stub.get_rest_resources = lambda: sample_urls["rest_resources"]
    stub.get_org_limits = lambda: sample_urls["org_limits"]
    stub.get_all_sobjects = lambda: sample_urls["sobjects"]
    stub.get_sobject = lambda *_args, **_kwargs: sample_urls["account"]
    stub.describe_object = lambda *_args, **_kwargs: sample_urls["account"]
    stub.create_sobject_record = (
        lambda *_args, **_kwargs: _create_response()
    )
    stub.soql_query = lambda *_args, **_kwargs: sample_urls["soql_result"]
    stub.search_string = lambda *_args, **_kwargs: sample_urls["sosl_result"]

    return stub
