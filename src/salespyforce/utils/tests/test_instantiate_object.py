# -*- coding: utf-8 -*-
"""
:Module:         salespyforce.utils.tests.test_instantiate_object
:Synopsis:       This module is used by pytest to test instantiating the core object
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  29 May 2023
"""

from . import resources


def test_instantiate_core_object():
    """This function tests the ability to instantiate the core object.

    .. versionadded:: 1.1.0
    """
    sfdc_object = resources.get_core_object()
    assert 'force.com' in sfdc_object.base_url


def test_get_api_versions():
    """This function tests the get_api_versions() method in the core object.

    .. versionadded:: 1.1.0
    """
    sfdc_object = resources.get_core_object()
    api_versions = sfdc_object.get_api_versions()
    assert isinstance(api_versions, list) and 'version' in api_versions[0]


def test_get_rest_resources():
    """This function tests the get_rest_resources() method in the core object.

    .. versionadded:: 1.1.0
    """
    sfdc_object = resources.get_core_object()
    rest_resources = sfdc_object.get_rest_resources()
    assert 'metadata' in rest_resources


def test_get_org_limits():
    """This function tests the get_org_limits() method in the core object.

    .. versionadded:: 1.1.0
    """
    sfdc_object = resources.get_core_object()
    org_limits = sfdc_object.get_org_limits()
    assert 'DailyApiRequests' in org_limits
