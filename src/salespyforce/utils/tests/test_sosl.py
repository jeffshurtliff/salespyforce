# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         salespyforce.utils.tests.test_sosl
:Synopsis:       This module is used by pytest to test performing SOSL queries
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  20 Dec 2025
"""

import requests

from . import resources


def test_search_string(monkeypatch, salesforce_unit):
    """This function tests the ability to search for a string using an SOSL query.

    .. versionadded:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    # Overwrite the requests.post functionality with the mock_success_post() function
    monkeypatch.setattr(requests, 'get', resources.mock_sosl_get)

    # Perform the mock API call
    result = salesforce_unit.search_string('Account')
    assert 'searchRecords' in result
