# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.api
:Synopsis:          Defines the basic functions associated with the Salesforce API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     29 Jan 2026
"""

import requests

from .utils import log_utils

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def get(sfdc_object, endpoint, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
    """This method performs a GET request against the Salesforce instance.
    (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :param endpoint: The API endpoint to query
    :type endpoint: str
    :param params: The query parameters (where applicable)
    :type params: dict, None
    :param headers: Specific API headers to use when performing the API call
    :type headers: dict, None
    :param timeout: The timeout period in seconds (defaults to ``30``)
    :type timeout: int, str, None
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :returns: The API response in JSON format or as a ``requests`` object
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Make sure the endpoint begins with a slash
    endpoint = f'/{endpoint}' if not endpoint.startswith('/') else endpoint

    # Perform the API call
    response = requests.get(f'{sfdc_object.instance_url}{endpoint}', headers=headers, params=params, timeout=timeout)
    if response.status_code >= 300:
        if show_full_error:
            raise RuntimeError(f'The GET request failed with a {response.status_code} status code.\n'
                               f'{response.text}')
        else:
            raise RuntimeError(f'The GET request failed with a {response.status_code} status code.')
    if return_json:
        response = response.json()
    return response


def api_call_with_payload(sfdc_object, method, endpoint, payload, params=None, headers=None, timeout=30,
                          show_full_error=True, return_json=True):
    """This method performs a POST call against the Salesforce instance.
    (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

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
    :type timeout: int, str, None
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :returns: The API response in JSON format or as a ``requests`` object
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Make sure the endpoint begins with a slash
    endpoint = f'/{endpoint}' if not endpoint.startswith('/') else endpoint

    # Perform the API call
    if method.lower() == 'post':
        response = requests.post(f'{sfdc_object.instance_url}{endpoint}', json=payload, headers=headers, params=params,
                                 timeout=timeout)
    elif method.lower() == 'patch':
        response = requests.patch(f'{sfdc_object.instance_url}{endpoint}', json=payload, headers=headers, params=params,
                                  timeout=timeout)
    elif method.lower() == 'put':
        response = requests.put(f'{sfdc_object.instance_url}{endpoint}', json=payload, headers=headers, params=params,
                                timeout=timeout)
    else:
        raise ValueError('The API call method (POST or PATCH OR PUT) must be defined.')

    # Examine the result
    if response.status_code >= 300:
        if show_full_error:
            raise RuntimeError(f'The POST request failed with a {response.status_code} status code.\n'
                               f'{response.text}')
        else:
            raise RuntimeError(f'The POST request failed with a {response.status_code} status code.')
    if return_json:
        try:
            response = response.json()
        except Exception as exc:
            print(f'Failed to convert the API response to JSON format due to the following exception: {exc}')
    return response


def delete(sfdc_object, endpoint, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
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
    :type timeout: int, str, None
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :returns: The API response in JSON format or as a ``requests`` object
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Make sure the endpoint begins with a slash
    endpoint = f'/{endpoint}' if not endpoint.startswith('/') else endpoint

    # Perform the API call
    response = requests.delete(f'{sfdc_object.instance_url}{endpoint}', headers=headers, params=params,
                               timeout=timeout)
    if response.status_code >= 300:
        if show_full_error:
            raise RuntimeError(f'The DELETE request failed with a {response.status_code} status code.\n'
                               f'{response.text}')
        else:
            raise RuntimeError(f'The DELETE request failed with a {response.status_code} status code.')
    if return_json:
        response = response.json()
    return response


def _get_headers(_access_token, _header_type='default'):
    """This function returns the appropriate HTTP headers to use for different types of API calls."""
    headers = {
        'content-type': 'application/json',
        'accept-encoding': 'gzip',
        'authorization': f'Bearer {_access_token}'
    }
    if _header_type == 'articles':
        headers['accept-language'] = 'en-US'
    return headers
