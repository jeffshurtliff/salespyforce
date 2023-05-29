# -*- coding: utf-8 -*-
"""
:Module:         khoros.utils.tests.test_instantiate_object
:Synopsis:       This module is used by pytest to test instantiating the core object
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  27 May 2023
"""

from . import resources


def test_instantiate_core_object():
    """This function tests the ability to instantiate the core object.

    .. versionadded:: 1.1.0
    """
    sfdc_object = resources.get_core_object()
    assert 'force.com' in sfdc_object.base_url
