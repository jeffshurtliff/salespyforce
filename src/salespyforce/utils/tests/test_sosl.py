# -*- coding: utf-8 -*-
"""
:Module:         salespyforce.utils.tests.test_sobjects
:Synopsis:       This module is used by pytest to test performing SOQL queries
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  29 May 2023
"""

import requests

from . import resources


def test_search_string(monkeypatch):
    """This function tests the ability to search for a string using an SOSL query.

    .. versionadded:: 1.1.0
    """
    # Instantiate the core object
    sfdc_object = resources.get_core_object()

    # Overwrite the requests.post functionality with the mock_success_post() function
    monkeypatch.setattr(requests, 'get', resources.mock_sosl_get)

    # Perform the mock API call
    result = sfdc_object.search_string('Account')
    assert 'searchRecords' in result

