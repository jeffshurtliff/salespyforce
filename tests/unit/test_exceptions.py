# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         tests.unit.test_exceptions
:Synopsis:       Tests API request exception message construction
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff (via GPT-5.5-codex)
:Modified Date:  15 Jul 2026
"""

import pytest

from salespyforce.errors import exceptions


@pytest.mark.parametrize(
    ('exception_class', 'request_type'),
    [
        (exceptions.GETRequestError, 'GET'),
        (exceptions.PATCHRequestError, 'PATCH'),
        (exceptions.POSTRequestError, 'POST'),
        (exceptions.PUTRequestError, 'PUT'),
        (exceptions.DELETERequestError, 'DELETE'),
    ],
)
def test_api_request_exception_default_message(exception_class, request_type):
    """API request exceptions provide request-specific default messages."""
    error = exception_class()

    assert str(error) == f'The {request_type} request did not return a successful response.'


@pytest.mark.parametrize(
    ('exception_class', 'request_type'),
    [
        (exceptions.GETRequestError, 'GET'),
        (exceptions.PATCHRequestError, 'PATCH'),
        (exceptions.POSTRequestError, 'POST'),
        (exceptions.PUTRequestError, 'PUT'),
        (exceptions.DELETERequestError, 'DELETE'),
    ],
)
def test_api_request_exception_custom_message(exception_class, request_type):
    """API request exceptions append custom message details."""
    error = exception_class(message='Additional details.')

    assert str(error) == f'The {request_type} request failed with the following message: Additional details.'


@pytest.mark.parametrize(
    ('exception_class', 'request_type'),
    [
        (exceptions.GETRequestError, 'GET'),
        (exceptions.PATCHRequestError, 'PATCH'),
        (exceptions.POSTRequestError, 'POST'),
        (exceptions.PUTRequestError, 'PUT'),
        (exceptions.DELETERequestError, 'DELETE'),
    ],
)
def test_api_request_exception_status_code_message(exception_class, request_type):
    """API request exceptions include a supplied response status code."""
    error = exception_class(status_code=404)

    assert str(error) == f'The {request_type} request returned the 404 status code.'


@pytest.mark.parametrize(
    ('exception_class', 'request_type'),
    [
        (exceptions.GETRequestError, 'GET'),
        (exceptions.PATCHRequestError, 'PATCH'),
        (exceptions.POSTRequestError, 'POST'),
        (exceptions.PUTRequestError, 'PUT'),
        (exceptions.DELETERequestError, 'DELETE'),
    ],
)
def test_api_request_exception_status_and_custom_message(exception_class, request_type):
    """API request exceptions combine status codes and custom details."""
    error = exception_class(status_code=404, message='Additional details.')

    assert str(error) == (
        f'The {request_type} request returned the 404 status code with the following message: Additional details.'
    )
