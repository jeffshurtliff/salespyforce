# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.api
:Synopsis:          Defines the basic functions associated with the Salesforce API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via claude-opus-5-5)
:Modified Date:     29 Sep 2026
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from . import constants as const
from . import errors
from .utils import core_utils

logger = logging.getLogger(__name__)


def get(
    sfdc_object,
    endpoint: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int | None = None,
    show_full_error: bool = True,
    return_json: bool = True,
) -> dict[str, Any] | requests.Response:
    """Performs a GET request against the Salesforce instance.
    (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`__)

    .. versionchanged:: 1.4.0
       The full URL for the API call is now constructed prior to making the call. The provided URL is also
       now evaluated to ensure it is a valid Salesforce URL. Additionally, a global constant is now leveraged
       for the API timeout value instead of hardcoding the value. (Timeout is still **30** seconds in this version)

    .. versionchanged:: 1.5.0
       Successful responses with empty bodies are returned without attempting JSON conversion.

    .. versionchanged:: 2.1.0
       The function now fails with the :py:exc:`salespyforce.errors.exceptions.GETRequestError` exception rather
       than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param endpoint: The API endpoint to query
    :type endpoint: str
    :param params: The query parameters (where applicable)
    :type params: dict, optional
    :param headers: Specific API headers to use when performing the API call
    :type headers: dict, optional
    :param timeout: The timeout period in seconds (defaults to ``30``)
    :type timeout: int, optional
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :type return_json: bool
    :returns: The API response in JSON format or as a ``requests.Response`` object
    :rtype: dict[str, Any], requests.Response
    :raises TypeError: If an invalid data type is supplied for a parameter value
    :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
    :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
    :raises requests.exceptions.Timeout: If the API request times out
    :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Construct the request URL
    url = _construct_full_query_url(endpoint, sfdc_object.instance_url)

    # Define the API request timeout (using default value if not explicitly defined with parameter)
    timeout = const.DEFAULT_API_TIMEOUT_SECONDS if not timeout else timeout

    # Perform the API call
    response = requests.get(url, headers=headers, params=params, timeout=timeout)
    if response.status_code >= 300:
        _raise_exception_for_failed_request(const.API_REQUEST_TYPES.GET, response, show_full_error)
    if return_json and not _has_empty_response_body(response):
        response = response.json()
    return response


def api_call_with_payload(
    sfdc_object,
    method: str,
    endpoint: str,
    payload: dict,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int | None = None,
    show_full_error: bool = True,
    return_json: bool = True,
) -> dict[str, Any] | requests.Response:
    """Performs a POST call against the Salesforce instance.
    (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`__)

    .. versionchanged:: 1.4.0
       The full URL for the API call is now constructed prior to making the call. The provided URL is also
       now evaluated to ensure it is a valid Salesforce URL. Additionally, a global constant is now leveraged
       for the API timeout value instead of hardcoding the value. (Timeout is still **30** seconds in this version)

    .. versionchanged:: 1.5.0
       Successful responses with empty bodies are returned without attempting JSON conversion.

    .. versionchanged:: 2.1.0
       Failed API requests now return more specific exceptions in place of the generic :py:exc:`RuntimeError` exception.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param method: The API method (``post``, ``put``, or ``patch``)
    :type method: str
    :param endpoint: The API endpoint to query
    :type endpoint: str
    :param payload: The payload to leverage in the API call
    :type payload: dict
    :param params: The query parameters (where applicable)
    :type params: dict, optional
    :param headers: Specific API headers to use when performing the API call
    :type headers: dict, optional
    :param timeout: The timeout period in seconds (defaults to ``30``)
    :type timeout: int, optional
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :type return_json: bool
    :returns: The API response in JSON format or as a ``requests.response`` object
    :rtype: dict[str, Any], requests.Response
    :raises TypeError: If an invalid data type is supplied for a parameter value
    :raises ValueError: If an invalid API call method is supplied
    :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
    :raises salespyforce.errors.exceptions.PATCHRequestError: If PATCH request does not return a successful response
    :raises salespyforce.errors.exceptions.PUTRequestError: If PUT request does not return a successful response
    :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
    :raises requests.exceptions.Timeout: If the API request times out
    :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Construct the request URL
    url = _construct_full_query_url(endpoint, sfdc_object.instance_url)

    # Define the API request timeout (using default value if not explicitly defined with parameter)
    timeout = const.DEFAULT_API_TIMEOUT_SECONDS if not timeout else timeout

    # Perform the API call
    if method.upper() == const.API_REQUEST_TYPES.POST:
        response = requests.post(url, json=payload, headers=headers, params=params, timeout=timeout)
    elif method.upper() == const.API_REQUEST_TYPES.PATCH:
        response = requests.patch(url, json=payload, headers=headers, params=params, timeout=timeout)
    elif method.upper() == const.API_REQUEST_TYPES.PUT:
        response = requests.put(url, json=payload, headers=headers, params=params, timeout=timeout)
    else:
        exc_msg = 'The API call method (POST or PATCH or PUT) must be defined'
        logger.error(exc_msg)
        raise ValueError(exc_msg)

    # Examine the result
    if response.status_code >= 300:
        # Raise the appropriate exception depending on the API method
        _raise_exception_for_failed_request(method.upper(), response, show_full_error)
    if return_json and not _has_empty_response_body(response):
        response = response.json()
    return response


def delete(
    sfdc_object,
    endpoint: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int | None = None,
    show_full_error: bool = True,
    return_json: bool = True,
) -> dict[str, Any] | requests.Response:
    """Performs a DELETE request against the Salesforce instance.

    .. versionadded:: 1.4.0

    .. versionchanged:: 1.5.0
       Successful responses with empty bodies are returned without attempting JSON conversion.

    .. versionchanged:: 2.1.0
       The function now fails with the :py:exc:`salespyforce.errors.exceptions.DELETERequestError` exception rather
       than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param endpoint: The API endpoint to query
    :type endpoint: str
    :param params: The query parameters (where applicable)
    :type params: dict, optional
    :param headers: Specific API headers to use when performing the API call
    :type headers: dict, optional
    :param timeout: The timeout period in seconds (defaults to ``30``)
    :type timeout: int, optional
    :param show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type show_full_error: bool
    :param return_json: Determines if the response should be returned in JSON format (defaults to ``True``)
    :type return_json: bool
    :returns: The API response in JSON format or as a ``requests.Response`` object
    :rtype: dict[str, Any], requests.Response
    :raises TypeError: If an invalid data type is supplied for a parameter value
    :raises salespyforce.errors.exceptions.DELETERequestError: If Salesforce does not return a successful response
    :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
    :raises requests.exceptions.Timeout: If the API request times out
    :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
    """
    # Define the parameters as an empty dictionary if none are provided
    params = {} if params is None else params

    # Define the headers
    default_headers = _get_headers(sfdc_object.access_token)
    headers = default_headers if not headers else headers

    # Construct the request URL
    url = _construct_full_query_url(endpoint, sfdc_object.instance_url)

    # Define the API request timeout (using default value if not explicitly defined with parameter)
    timeout = const.DEFAULT_API_TIMEOUT_SECONDS if not timeout else timeout

    # Perform the API call
    response = requests.delete(url, headers=headers, params=params, timeout=timeout)
    if response.status_code >= 300:
        _raise_exception_for_failed_request(const.API_REQUEST_TYPES.DELETE, response, show_full_error)
    if return_json and not _has_empty_response_body(response):
        response = response.json()
    return response


def _raise_exception_for_failed_request(
    _api_method: str,
    _response: requests.Response,
    _show_full_error: bool = True,
) -> None:
    """Raises an appropriate exception for a failed API request.

    .. versionadded:: 2.1.0

    :param _api_method: The API method of the request (e.g. GET, POST, etc.)
    :type _api_method: str
    :param _response: The API response to inspect
    :type _response: requests.Response
    :param _show_full_error: Determines if the full error message should be displayed (defaults to ``True``)
    :type _show_full_error: bool
    :returns: None
    :raises salespyforce.errors.exceptions.GETRequestError: If GET request does not return a successful response
    :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
    :raises salespyforce.errors.exceptions.PATCHRequestError: If PATCH request does not return a successful response
    :raises salespyforce.errors.exceptions.PUTRequestError: If PUT request does not return a successful response
    :raises salespyforce.errors.exceptions.DELETERequestError: If DELETE request does not return a successful response
    :raises salespyforce.errors.exceptions.APIRequestError: If an unrecognized API method was provided with the response
    """
    _exc_msg = f'The {_api_method.upper()} request failed with a {_response.status_code} status code.'
    _exc_msg += f'\n{_response.text}' if _show_full_error else ''
    logger.error(_exc_msg)
    if _api_method.upper() == const.API_REQUEST_TYPES.GET:
        raise errors.exceptions.GETRequestError(_exc_msg)
    elif _api_method.upper() == const.API_REQUEST_TYPES.POST:
        raise errors.exceptions.POSTRequestError(_exc_msg)
    elif _api_method.upper() == const.API_REQUEST_TYPES.PATCH:
        raise errors.exceptions.PATCHRequestError(_exc_msg)
    elif _api_method.upper() == const.API_REQUEST_TYPES.PUT:
        raise errors.exceptions.PUTRequestError(_exc_msg)
    elif _api_method.upper() == const.API_REQUEST_TYPES.DELETE:
        raise errors.exceptions.DELETERequestError(_exc_msg)
    else:
        raise errors.exceptions.APIRequestError(_exc_msg)


def _has_empty_response_body(_response: requests.Response) -> bool:
    """Determines whether a successful API response has an empty body.

    .. versionadded:: 1.5.0

    :param _response: The API response to inspect.
    :type _response: requests.Response
    :returns: Whether the response has no content to deserialize.
    :rtype: bool
    """
    if _response.status_code in (204, 205):
        return True

    missing_content = object()
    content = getattr(_response, 'content', missing_content)
    return content is not missing_content and content in (b'', '')


def _get_headers(_access_token: str, _header_type: str = 'default') -> dict[str, str]:
    """Returns the appropriate HTTP headers to use for different types of API calls.

    .. versionchanged:: 1.5.0
       A warning message is now logged if an invalid header type is passed to the function.

    :param _access_token: The access token for the API request
    :type _access_token: str
    :param _header_type: The type or scope of HTTP headers to use
    :type _header_type: str
    :returns: Dictionary of HTTP headers
    :rtype: dict[str, str]
    """
    headers = {
        const.HEADERS.CONTENT_TYPE: const.CONTENT_TYPES.JSON,
        const.HEADERS.ACCEPT_ENCODING: const.ENCODING_TYPES.GZIP,
        const.HEADERS.AUTHORIZATION: const.AUTH_SCHEMES.BEARER.format(token=_access_token),
    }
    if _header_type == 'articles':
        headers[const.HEADERS.ACCEPT_LANGUAGE] = const.LANGUAGES.EN_US
    elif _header_type not in const.VALID_HEADER_TYPES:
        logger.warning(f"'{_header_type}' is not a valid header type and the default type/scope will be leveraged")
    return headers


def _construct_full_query_url(_endpoint: str, _instance_url: str) -> str:
    """Constructs the URL to use in an API call to the Salesforce REST API.

    .. versionadded:: 1.4.0

    :param _endpoint: The endpoint provided when calling an API call method or function
    :type _endpoint: str
    :param _instance_url: The Salesforce instance URL defined when the core object was instantiated
    :type _instance_url: str
    :returns: The fully qualified URL
    :rtype: str
    :raises TypeError: If the provided endpoint is not a string
    :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
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
            logger.error(f"'{_endpoint}' is not a valid Salesforce URL")
            raise errors.exceptions.InvalidURLError(url=_endpoint)
        _url = _endpoint
    else:
        _endpoint = f'/{_endpoint}' if not _endpoint.startswith('/') else _endpoint
        _url = f'{_instance_url}{_endpoint}'

    # Return the constructed URL
    return _url
