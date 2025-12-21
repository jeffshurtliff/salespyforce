# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         salespyforce.utils.tests.test_instantiate_object
:Synopsis:       This module is used by pytest to test instantiating the core object
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  20 Dec 2025

These tests rely on the ``salesforce_unit`` fixture defined in
``conftest.py`` to keep them fast and deterministic. When you want to
verify behavior against a real org, add ``@pytest.mark.integration``
and switch the fixture parameter to ``salesforce_integration``.
"""


def test_instantiate_core_object(salesforce_unit):
    """This function tests the ability to instantiate the core object.

    .. version-added:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    sfdc_object = salesforce_unit
    assert 'force.com' in sfdc_object.base_url


def test_get_api_versions(salesforce_unit):
    """This function tests the get_api_versions() method in the core object.

    .. version-added:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    api_versions = salesforce_unit.get_api_versions()
    assert isinstance(api_versions, list) and 'version' in api_versions[0]


def test_get_rest_resources(salesforce_unit):
    """This function tests the get_rest_resources() method in the core object.

    .. version-added:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    rest_resources = salesforce_unit.get_rest_resources()
    assert 'metadata' in rest_resources


def test_get_org_limits(salesforce_unit):
    """This function tests the get_org_limits() method in the core object.

    .. version-added:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    org_limits = salesforce_unit.get_org_limits()
    assert 'DailyApiRequests' in org_limits
