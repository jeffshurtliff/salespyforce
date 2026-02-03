# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.api
:Synopsis:          Defines the basic functions associated with the Salesforce API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     03 Feb 2026
"""

from __future__ import annotations

from typing import Optional

import requests

from . import errors
from .utils import core_utils, log_utils

# Define constants
DEFAULT_API_REQUEST_TIMEOUT = 30

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def get(sfdc_object, endpoint, params=None, headers=None, timeout=None, show_full_error=True, return_json=True):
    """This method performs a GET request against the Salesforce instance.
    (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

    .. version-changed:: 1.4.0
       The full URL for the API call is now constructed prior to making the call. The provided URL is also
       now evaluated to ensure it is a valid Salesforce URL. Additionally, a global constant is now leveraged
       for the API timeout value instead of hardcoding the value. (Timeout is still **30** seconds in this version)

    :param sfdc_object: The instantiated SalesPyForce object
    :param endpoint: The API endpoint to query
    :type endpoint: str
    :param params: The query parameters (where applicable)
    :type params: dict, None
    :param headers: Specific API headers to use when performing the API call
    :type headers: dict, None
    :param timeout: The timeout period in seconds (defaults to ``30``)
    :type timeout: int, None
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :returns: The API response in JSON format or as a ``requests`` object
    :raises: :py:exc:`TypeError`,
             :py:exc:`RuntimeError`,
             :py:exc:`salespyforce.errors.exceptions.InvalidURLError`
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Construct the request URL
    url = _construct_full_query_url(endpoint, sfdc_object.instance_url)

    # Define the API request timeout (using default value if not explicitly defined with parameter)
    timeout = DEFAULT_API_REQUEST_TIMEOUT if not timeout else timeout

    # Perform the API call
    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    if response.status_code >= 300:
        # TODO: Functionalize this segment and figure out how to improve on the approach somehow
        if show_full_error:
            raise RuntimeError(f'The GET request failed with a {response.status_code} status code.\n'
                               f'{response.text}')
        else:
            raise RuntimeError(f'The GET request failed with a {response.status_code} status code.')
    # TODO: Leverage private function for this section across all API call functions (see TODO in api_call_with_payload)
    if return_json:
        response = response.json()
    return response


def api_call_with_payload(sfdc_object, method, endpoint, payload, params=None, headers=None, timeout=None,
                          show_full_error=True, return_json=True):
    """This method performs a POST call against the Salesforce instance.
    (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

    .. version-changed:: 1.4.0
       The full URL for the API call is now constructed prior to making the call. The provided URL is also
       now evaluated to ensure it is a valid Salesforce URL. Additionally, a global constant is now leveraged
       for the API timeout value instead of hardcoding the value. (Timeout is still **30** seconds in this version)

    :param sfdc_object: The instantiated SalesPyForce object
    :param method: The API method (``post``, ``put``, or ``patch``)
    :type method: str
    :param endpoint: The API endpoint to query
    :type endpoint: str
    :param payload: The payload to leverage in the API call
    :type payload: dict
    :param params: The query parameters (where applicable)
    :type params: dict, None
    :param headers: Specific API headers to use when performing the API call
    :type headers: dict, None
    :param timeout: The timeout period in seconds (defaults to ``30``)
    :type timeout: int, None
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :returns: The API response in JSON format or as a ``requests`` object
    :raises: :py:exc:`TypeError`,
             :py:exc:`RuntimeError`,
             :py:exc:`ValueError`,
             :py:exc:`salespyforce.errors.exceptions.InvalidURLError`
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Construct the request URL
    url = _construct_full_query_url(endpoint, sfdc_object.instance_url)

    # Define the API request timeout (using default value if not explicitly defined with parameter)
    timeout = DEFAULT_API_REQUEST_TIMEOUT if not timeout else timeout

    # Perform the API call
    if method.lower() == 'post':
        response = requests.post(url, json=payload, headers=headers, params=params, timeout=timeout)
    elif method.lower() == 'patch':
        response = requests.patch(url, json=payload, headers=headers, params=params, timeout=timeout)
    elif method.lower() == 'put':
        response = requests.put(url, json=payload, headers=headers, params=params, timeout=timeout)
    else:
        raise ValueError('The API call method (POST or PATCH or PUT) must be defined')

    # Examine the result
    if response.status_code >= 300:
        if show_full_error:
            # TODO: Functionalize this segment and figure out how to improve on the approach somehow
            raise RuntimeError(f'The POST request failed with a {response.status_code} status code.\n'
                               f'{response.text}')
        else:
            raise RuntimeError(f'The POST request failed with a {response.status_code} status code.')
    # TODO: Break this out into a separate private function so it can be reused and standardized
    if return_json:
        try:
            response = response.json()
        except Exception as exc:
            # TODO: log the exception rather than using a print statement
            print(f'Failed to convert the API response to JSON format due to the following exception: {exc}')
    return response


def delete(sfdc_object, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None, timeout=None, show_full_error=True, return_json=True):
    """This method performs a DELETE request against the Salesforce instance.

    .. version-added:: 1.4.0

    :param sfdc_object: The instantiated SalesPyForce object
    :param endpoint: The API endpoint to query
    :type endpoint: str
    :param params: The query parameters (where applicable)
    :type params: dict, None
    :param headers: Specific API headers to use when performing the API call
    :type headers: dict, None
    :param timeout: The timeout period in seconds (defaults to ``30``)
    :type timeout: int, None
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :returns: The API response in JSON format or as a ``requests`` object
    :raises: :py:exc:`TypeError`,
             :py:exc:`RuntimeError`,
             :py:exc:`salespyforce.errors.exceptions.InvalidURLError`
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Construct the request URL
    url = _construct_full_query_url(endpoint, sfdc_object.instance_url)

    # Define the API request timeout (using default value if not explicitly defined with parameter)
    timeout = DEFAULT_API_REQUEST_TIMEOUT if not timeout else timeout

    # Perform the API call
    response = requests.delete(url, headers=headers, params=params, timeout=timeout)
    if response.status_code >= 300:
        if show_full_error:
            # TODO: Functionalize this segment and figure out how to improve on the approach somehow
            raise RuntimeError(f'The DELETE request failed with a {response.status_code} status code.\n'
                               f'{response.text}')
        else:
            raise RuntimeError(f'The DELETE request failed with a {response.status_code} status code.')
    # TODO: Leverage private function for this section across all API call functions (see TODO in api_call_with_payload)
    if return_json:
        response = response.json()
    return response


def _get_headers(_access_token: str, _header_type: str = 'default') -> dict:
    """This function returns the appropriate HTTP headers to use for different types of API calls."""
    headers = {
        'content-type': 'application/json',
        'accept-encoding': 'gzip',
        'authorization': f'Bearer {_access_token}'
    }
    if _header_type == 'articles':
        headers['accept-language'] = 'en-US'
    return headers


def _construct_full_query_url(_endpoint: str, _instance_url: str) -> str:
    """This function constructs the URL to use in an API call to the Salesforce REST API.

    .. version-added:: 1.4.0

    :param _endpoint: The endpoint provided when calling an API call method or function
    :type _endpoint: str
    :param _instance_url: The Salesforce instance URL defined when the core object was instantiated
    :type _instance_url: str
    :returns: The fully qualified URL
    :raises: :py:exc:`TypeError`,
             :py:exc:`salespyforce.errors.exceptions.InvalidURLError`
    """
    # Raise an exception if the endpoint is not a string
    if not isinstance(_endpoint, str):
        _exc_msg = 'The provided URL must be a string and a valid Salesforce URL'
        logger.critical(_exc_msg)
        raise TypeError(_exc_msg)

    # Construct the URL as needed by prepending the instance URL
    if _endpoint.startswith('https://'):
        # Only permit valid Salesforce URLs
        if not core_utils.is_valid_salesforce_url(_endpoint):
            raise errors.exceptions.InvalidURLError(url=_endpoint)
        _url = _endpoint
    else:
        _endpoint = f'/{_endpoint}' if not _endpoint.startswith('/') else _endpoint
        _url = f'{_instance_url}{_endpoint}'

    # Return the constructed URL
    return _url
