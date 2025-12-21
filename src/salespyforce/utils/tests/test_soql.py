# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         salespyforce.utils.tests.test_soql
:Synopsis:       This module is used by pytest to test performing SOQL queries
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  20 Dec 2025
"""


def test_soql_query(salesforce_unit):
    """This function tests the ability to perform a SOQL query.

    .. versionadded:: 1.1.0

    .. version-changed:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    soql_statement = 'SELECT Id FROM Account LIMIT 1'
    soql_response = salesforce_unit.soql_query(soql_statement)
    assert 'done' in soql_response and soql_response.get('done') is True
    assert 'totalSize' in soql_response and 'records' in soql_response
