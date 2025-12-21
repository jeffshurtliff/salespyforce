# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         salespyforce.utils.tests.test_sobjects
:Synopsis:       This module is used by pytest to test basic sObject-related methods
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  20 Dec 2025
"""

import requests

from . import resources


def test_get_all_sobjects(salesforce_unit):
    """This function tests the get_all_sobjects() method in the core object.

    .. versionadded:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    all_sobjects = salesforce_unit.get_all_sobjects()
    assert 'sobjects' in all_sobjects


def test_get_and_describe_sobject(salesforce_unit):
    """This function tests the get_sobject() and describe_object() methods in the core object.

    .. versionadded:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    # Test the default query (non-describe)
    account_sobject = salesforce_unit.get_sobject('Account')
    assert 'objectDescribe' in account_sobject

    # Test with describe enabled
    account_sobject_describe = salesforce_unit.get_sobject('Account', describe=True)
    assert 'activateable' in account_sobject_describe

    # Test the describe_object() method
    account_describe = salesforce_unit.describe_object('Account')
    assert 'activateable' in account_describe


def test_create_record(monkeypatch, salesforce_unit):
    """This function tests creating a Salesforce object record.

    .. versionadded:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    # Overwrite the requests.post functionality with the mock_success_post() function
    monkeypatch.setattr(requests, 'post', resources.mock_success_post)

    # Perform the mock API call
    payload = {
        "Name": "Express Logistics and Transport"
    }
    response = salesforce_unit.create_sobject_record('Account', payload)
    assert 'success' in response and response.get('success') is True and 'id' in response
