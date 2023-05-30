# -*- coding: utf-8 -*-
"""
:Module:         salespyforce.utils.tests.test_sobjects
:Synopsis:       This module is used by pytest to test performing SOQL queries
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  29 May 2023
"""

from . import resources


def test_soql_query():
    """This function tests the ability to perform a SOQL query.

    .. versionadded:: 1.1.0
    """
    sfdc_object = resources.get_core_object()
    soql_statement = 'SELECT Id FROM Account LIMIT 1'
    soql_response = sfdc_object.soql_query(soql_statement)
    assert 'done' in soql_response and soql_response.get('done') is True
    assert 'totalSize' in soql_response and 'records' in soql_response

