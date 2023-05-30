# -*- coding: utf-8 -*-
"""
:Module:         salespyforce.utils.tests.test_sobjects
:Synopsis:       This module is used by pytest to test basic sObject-related methods
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  29 May 2023
"""

import requests

from . import resources


def test_get_all_sobjects():
    """This function tests the get_all_sobjects() method in the core object.

    .. versionadded:: 1.1.0
    """
    sfdc_object = resources.get_core_object()
    all_sobjects = sfdc_object.get_all_sobjects()
    assert 'sobjects' in all_sobjects


def test_get_and_describe_sobject():
    """This function tests the get_sobject() and describe_object() methods in the core object.

    .. versionadded:: 1.1.0
    """
    # Instantiate the core object
    sfdc_object = resources.get_core_object()

    # Test the default query (non-describe)
    account_sobject = sfdc_object.get_sobject('Account')
    assert 'objectDescribe' in account_sobject

    # Test with describe enabled
    account_sobject_describe = sfdc_object.get_sobject('Account', describe=True)
    assert 'activateable' in account_sobject_describe

    # Test the describe_object() method
    account_describe = sfdc_object.describe_object('Account')
    assert 'activateable' in account_describe


def test_create_record(monkeypatch):
    # Instantiate the core object
    sfdc_object = resources.get_core_object()

    # Overwrite the requests.post functionality with the mock_success_post() function
    monkeypatch.setattr(requests, 'post', resources.mock_success_post)

    # Perform the mock API call
    payload = {
        "Name": "Express Logistics and Transport"
    }
    response = sfdc_object.create_sobject_record('Account', payload)
    assert 'success' in response and response.get('success') is True and 'id' in response
