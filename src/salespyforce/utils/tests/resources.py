# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.utils.tests.resources
:Synopsis:          Frequently used resources for performing unit testing
:Usage:             ``from salespyforce.utils.tests import resources``
:Example:           ``exceptions = resources.import_exceptions_module()``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     14 Nov 2025
"""

import os
import sys
import importlib

import pytest

# Define constants
SKIP_LOCAL_TEST_MSG = 'skipping local-only tests'
HELPER_FILE_NAME = 'helper_dm_conn.yml'


class MockResponse:
    """This class simulates an API response for testing purposes.

    .. versionadded:: 1.1.0
    """
    def __init__(self, json_body, status_code=200):
        self.json_body = json_body
        self.status_code = status_code

    def json(self):
        return self.json_body


def mock_success_post(*args, **kwargs):
    """This function works with the `MockedResponse` class to simulate a successful API response.

    .. versionadded:: 1.1.0
    """
    return MockResponse({
        "id": "001D000000IqhSLIAZ",
        "errors": [],
        "success": True
    })


def mock_error_post(*args, **kwargs):
    """This function works with the `MockedResponse` class to simulate a failed API response.

    .. versionadded:: 1.1.0
    """
    return MockResponse({
        "errors": [],
        "success": False
    })


def mock_sosl_get(*args, **kwargs):
    """This function works with the `MockedResponse` class to simulate an SOSL response."""
    return MockResponse({
        "searchRecords": [
            {
                'attributes': {
                    'type': 'Account',
                    'url': '/services/data/v57.0/sobjects/Account/0018V00002NeqAxQAJ'
                },
                'Id': '0018V00002NeqAxQAJ'
            }
        ]
    })


def set_package_path():
    """This function adds the high-level salespyforce directory to the sys.path list.

    .. versionadded:: 1.1.0
    """
    sys.path.insert(0, os.path.abspath('../..'))


def import_modules(*modules):
    """This function imports and returns one or more modules to utilize in a unit test.

    .. versionadded:: 1.1.0

    :param modules: One or more module paths (absolute) in string format
    :returns: The imported module(s) as an individual object or a tuple of objects
    """
    imported_modules = []
    for module in modules:
        imported_modules.append(importlib.import_module(module))
    tuple(imported_modules)
    return imported_modules if len(imported_modules) > 1 else imported_modules[0]


def secrets_helper_exists():
    """This function checks to see if the unencrypted helper file exists for GitHub Actions.

    .. versionadded:: 1.1.0
    """
    helper_path = f'{os.environ.get("HOME")}/secrets/{HELPER_FILE_NAME}'
    return os.path.isfile(helper_path)


def local_helper_exists():
    """This function checks to see if a helper file is present in the ``local/`` directory.

    .. versionadded:: 1.1.0
    """
    return os.path.exists(f'local/{HELPER_FILE_NAME}')


def get_core_object():
    """This function instantiates and returns the core object using a local helper file.

    .. versionadded:: 1.1.0
    """
    set_package_path()
    if secrets_helper_exists():
        sfdc_object = instantiate_with_secrets_helper()
    else:
        if not local_helper_exists():
            pytest.skip('skipping tests where a valid helper file is needed')
        sfdc_object = instantiate_with_local_helper()
    return sfdc_object


def instantiate_with_secrets_helper():
    """This function instantiates the Salesforce object using the unencrypted helper file intended for GitHub Actions.

    .. versionadded:: 1.1.0

    :returns: The instantiated :py:class:`salespyforce.core.Salesforce` object
    :raises: :py:exc:`FileNotFoundError`
    """
    if not secrets_helper_exists():
        raise FileNotFoundError('The unencrypted GitHub Actions helper file cannot be found.')
    file_name = f'{os.environ.get("HOME")}/secrets/{HELPER_FILE_NAME}'
    set_package_path()
    core_module = importlib.import_module('salespyforce.core')
    return core_module.Salesforce(helper=file_name)


def instantiate_with_local_helper():
    """This function instantiates the Salesforce object using a local helper file for unit testing.

    .. versionadded:: 1.1.0

    :returns: The instantiated :py:class:`salespyforce.core.Salesforce` object
    :raises: :py:exc:`FileNotFoundError`
    """
    if not local_helper_exists():
        raise FileNotFoundError('The local helper file cannot be found.')
    set_package_path()
    core_module = importlib.import_module('salespyforce.core')
    return core_module.Salesforce(helper=f"local/{HELPER_FILE_NAME}")
