# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.core
:Synopsis:          This module performs the core Salesforce-related operations
:Usage:             ``from salespyforce import Salesforce``
:Example:           ``sfdc = Salesforce(helper=helper_file_path)``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via claude-opus-5-5)
:Modified Date:     29 Sep 2026
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional, Tuple, Union

import requests

from . import api, errors
from . import chatter as chatter_module
from . import constants as const
from . import knowledge as knowledge_module
from .utils import core_utils
from .utils.helper import get_helper_settings

logger = logging.getLogger(__name__)


class Salesforce:
    """Class for the core client object.

    .. versionchanged:: 1.4.0
       The authorized Salesforce org is now queried to determine the latest API version to leverage unless
       explicitly defined with the ``version`` parameter when instantiating the object.

    .. versionchanged:: 1.5.0
       String helper paths now infer JSON or YAML parsing from the file extension.

    :param connection_info: The information for connecting to the Salesforce instance
    :type connection_info: dict, optional
    :param version: The Salesforce API version to utilize (uses latest version from org if not explicitly defined)
    :type version: str, optional
    :param base_url: The base URL of the Salesforce instance
    :type base_url: str, optional
    :param org_id: The Org ID of the Salesforce instance
    :type org_id: str, optional
    :param username: The username of the API user
    :type username: str, optional
    :param password: The password of the API user
    :type password: str, optional
    :param endpoint_url: The endpoint URL for the Salesforce instance
    :type endpoint_url: str, optional
    :param client_id: The Client ID for the Salesforce instance
    :type client_id: str, optional
    :param client_secret: The Client Secret for the Salesforce instance
    :type client_secret: str, optional
    :param security_token: The Security Token for the Salesforce instance
    :type security_token: str, optional
    :param helper: The file path of a helper file
    :type helper: str, tuple, list, set, dict, optional
    :returns: The instantiated client object
    :rtype: Salesforce
    :raises: :py:exc:`TypeError`,
             :py:exc:`RuntimeError`
    :raises TypeError: If the helper argument is not a tuple, string, list, set or dict
    :raises salespyforce.errors.exceptions.InvalidHelperArgumentsError: If the helper argument is not usable
    """

    # Define the function that initializes the object instance (i.e. instantiates the object)
    def __init__(
        self,
        connection_info: dict | None = None,
        version: str | None = None,
        base_url: str | None = None,
        org_id: str | None = None,
        username: str | None = None,
        password: str | None = None,
        endpoint_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        security_token: str | None = None,
        helper: str | tuple | list | set | dict | None = None,
    ) -> None:
        """Instantiates the core Salesforce client object."""
        # Define the default settings
        self._helper_settings = {}

        # Check for provided connection info
        if connection_info is None:
            # Check for a supplied helper file
            if helper:
                # Parse the helper file contents
                self.helper_path = helper
                if isinstance(helper, (tuple, list)):
                    helper_file_path, helper_file_type = helper
                elif isinstance(helper, set):
                    valid_file_types = {
                        const.FILE_EXTENSIONS.JSON,
                        const.FILE_EXTENSIONS.YAML,
                        const.FILE_EXTENSIONS.YML,
                    }
                    helper_file_type = next((item for item in helper if item in valid_file_types), None)
                    helper_file_path = next((item for item in helper if item != helper_file_type), None)
                elif isinstance(helper, str):
                    helper_file_path = helper
                    helper_file_type = core_utils.get_file_type(helper_file_path)
                elif isinstance(helper, dict):
                    helper_file_path, helper_file_type = helper.values()
                else:
                    exc_msg = "The 'helper' argument can only be supplied as tuple, string, list, set or dict."
                    logger.error(exc_msg)
                    raise TypeError(exc_msg)

                if isinstance(helper_file_path, str) and isinstance(helper_file_type, str):
                    self._helper_settings = get_helper_settings(helper_file_path, helper_file_type)
                    connection_info = self._parse_helper_connection_info()
                else:
                    exc_msg = (
                        'The helper_file_path and helper_file_type arguments must both be strings '
                        f'(Provided: {type(helper_file_path).__name__} and {type(helper_file_type).__name__})'
                    )
                    logger.error(exc_msg)
                    raise errors.exceptions.InvalidHelperArgumentsError(exc_msg)
            elif not any((base_url, org_id, username, password, endpoint_url, client_id, client_secret, security_token)):
                # Prompt for the connection info if not defined
                connection_info = define_connection_info()
            else:
                # Compile the connection info from the provided parameters
                connection_info = compile_connection_info(
                    base_url, org_id, username, password, endpoint_url, client_id, client_secret, security_token
                )

        # Get the connection information used to connect to the instance
        self.connection_info = connection_info if connection_info is not None else self._get_empty_connection_info()

        # Define the base URL and Org ID
        self.base_url = self.connection_info.get(const.CLIENT_SETTINGS.BASE_URL, '')
        self.org_id = self.connection_info.get(const.CLIENT_SETTINGS.ORG_ID, '')

        # Define the connection response data variables
        auth_response = self.connect()
        self.access_token = auth_response.get(const.CLIENT_SETTINGS.ACCESS_TOKEN)
        self.instance_url = auth_response.get(const.CLIENT_SETTINGS.INSTANCE_URL)
        self.signature = auth_response.get(const.CLIENT_SETTINGS.SIGNATURE)

        # Define the version with explicitly provided version or by querying the Salesforce org
        self.version = f'v{version}' if version else f'v{self.get_latest_api_version()}'

        # Retrieve info about current user
        self.current_user_info = self.retrieve_current_user_info(on_init=True, raise_exc_on_error=False)

        # Import inner object classes so their methods can be called from the primary object
        self.chatter = self._import_chatter_class()
        self.knowledge = self._import_knowledge_class()

    def _import_chatter_class(self):
        """Allows the :py:class:`salespyforce.core.Salesforce.Chatter` class to be utilized in the client object."""
        return Salesforce.Chatter(self)

    def _import_knowledge_class(self):
        """Allows the :py:class:`salespyforce.core.Salesforce.Knowledge` class to be utilized in the client object."""
        return Salesforce.Knowledge(self)

    @staticmethod
    def _get_empty_connection_info() -> dict:
        """Returns an empty connection_info dictionary with all blank values."""
        _connection_info = {}
        _fields = const.CLIENT_SETTINGS.CONNECTION_INFO_FIELDS
        for _field in _fields:
            _connection_info[_field] = ''
        return _connection_info

    def _parse_helper_connection_info(self) -> dict:
        """Parses the helper content to populate the connection info."""
        _connection_info = {}
        _fields = const.CLIENT_SETTINGS.CONNECTION_INFO_FIELDS
        for _field in _fields:
            if _field in self._helper_settings[const.HELPER_SETTINGS.CONNECTION]:
                _connection_info[_field] = self._helper_settings[const.HELPER_SETTINGS.CONNECTION][_field]
        return _connection_info

    def _get_headers(
        self,
        _header_type: str = const.HEADER_TYPE_DEFAULT,
    ) -> dict[str, str]:
        """Returns the appropriate HTTP headers to use for different types of API calls.

        .. versionchanged:: 1.5.0
           A warning message is now logged if an invalid header type is passed to the function.

        :param _header_type: The type or scope of HTTP headers to use
        :type _header_type: str
        :returns: Dictionary of HTTP headers
        :rtype: dict[str, str]
        """
        return api._get_headers(_access_token=self.access_token, _header_type=_header_type)

    def _get_cached_user_info(
        self,
        _field: str,
        _retrieve_if_missing: bool = False,
    ) -> str | bool | None:
        """Attempts to retrieve a value for a given field in the cached ``userinfo`` data and
           optionally queries the API as needed to retrieve the data when not found.

        .. versionadded:: 1.4.0

        :param _field: The name of the field for which the value is needed
        :type _field: str
        :param _retrieve_if_missing: Will query the Salesforce REST API for the data when missing if ``True``
                                     (``False`` by default)
        :type _retrieve_if_missing: bool
        :returns: The field value when found (or retrieved), or a None value if the field value could not be obtained
        :rtype: str, bool, None
        :raises salespyforce.errors.exceptions.APIRequestError: If the API call to retrieve current user info fails
        """
        _field_value = None
        _not_present_msg = f"The '{_field}' field is not present in the current user info data"
        if self.current_user_info and _field in self.current_user_info:
            _field_value = self.current_user_info[_field]
        else:
            logger.warning(_not_present_msg)
            if _retrieve_if_missing:
                self.current_user_info = self.retrieve_current_user_info(raise_exc_on_error=True)
                if self.current_user_info and _field in self.current_user_info:
                    _field_value = self.current_user_info[_field]
                else:
                    logger.error(f'{_not_present_msg} even after refreshing cached current user info')
        return _field_value

    # TODO: Expand this functionality to support External Client Apps with various supported auth flows
    def connect(self):
        """Connects to the Salesforce instance to obtain the access token.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`__)

        .. versionchanged:: 2.1.0
           A failed API call now raises a :py:exc:`salespyforce.errors.exceptions.POSTRequestError` exception
           instead of a generic :py:exc:`RuntimeError` exception.

        :returns: The API call response with the authorization information
        :raises salespyforce.errors.exceptions.POSTRequestError: If Salesforce returns an unsuccessful response
        :raises requests.exceptions.Timeout: If the authentication request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        params = {
            const.CLIENT_SETTINGS.GRANT_TYPE: const.CLIENT_SETTINGS.PASSWORD,
            const.CLIENT_SETTINGS.CLIENT_ID: self.connection_info.get(const.CLIENT_SETTINGS.CLIENT_KEY),
            const.CLIENT_SETTINGS.CLIENT_SECRET: self.connection_info.get(const.CLIENT_SETTINGS.CLIENT_SECRET),
            const.CLIENT_SETTINGS.USERNAME: self.connection_info.get(const.CLIENT_SETTINGS.USERNAME),
            const.CLIENT_SETTINGS.PASSWORD: f'{self.connection_info.get(const.CLIENT_SETTINGS.PASSWORD)}'
            f'{self.connection_info.get(const.CLIENT_SETTINGS.SECURITY_TOKEN)}',
        }
        response = requests.post(
            self.connection_info.get(const.CLIENT_SETTINGS.ENDPOINT_URL),
            params=params,
            timeout=const.DEFAULT_API_TIMEOUT_SECONDS,
        )
        if response.status_code != 200:
            exc_msg = f'Failed to connect to the Salesforce instance.\n{response.text}'
            logger.error(exc_msg)
            raise errors.exceptions.POSTRequestError(exc_msg)
        return response.json()

    def retrieve_current_user_info(
        self,
        all_data: bool = False,
        raise_exc_on_error: bool = False,
        on_init: bool = False,
    ) -> dict[str, str | None]:
        """Retrieves the ``userinfo`` data for the current/running user.

        .. versionadded:: 1.4.0

        :param all_data: Returns all ``userinfo`` data from the API when True instead of only the relevant fields/values
                         (``False`` by default)
        :type all_data: bool
        :param raise_exc_on_error: Raises an exception if the API retrieval attempt fails when True (``False`` by default)
        :type raise_exc_on_error: bool
        :param on_init: Indicates if the method is being called during the core object instantiation (``False`` by default)
        :type on_init: bool
        :returns: The user info data within a dictionary
        :rtype: dict[str, str | None]
        :raises salespyforce.errors.exceptions.APIRequestError: If the API call to retrieve user info is not successful
        """
        user_info = {
            const.CLIENT_SETTINGS.USER_ID: '',
            const.CLIENT_SETTINGS.NICKNAME: '',
            const.CLIENT_SETTINGS.NAME: '',
            const.CLIENT_SETTINGS.EMAIL: '',
            const.CLIENT_SETTINGS.USER_TYPE: '',
            const.CLIENT_SETTINGS.LANGUAGE: '',
            const.CLIENT_SETTINGS.LOCALE: '',
            const.CLIENT_SETTINGS.UTC_OFFSET: '',
            const.CLIENT_SETTINGS.IS_INTEGRATION_USER: None,
        }
        base_error_msg = 'Failed to retrieve current user info'
        msg_init_segment = 'on core client object instantiation'
        if on_init:
            base_error_msg = f'{base_error_msg} {msg_init_segment}'
        try:
            response = self.get(const.REST_PATHS.USER_INFO)
            if isinstance(response, dict) and all_data:
                user_info = response
            elif isinstance(response, dict):
                for field in user_info.keys():
                    if field in response:
                        default_val = None if field in const.CLIENT_SETTINGS.USER_INFO_BOOL_FIELDS else ''
                        user_info[field] = response.get(field, default_val)
            else:
                logger.error(f'{base_error_msg} with a usable format')
        except Exception as exc:
            exc_type = errors.handlers.get_exception_type(exc)
            exc_msg = f'{base_error_msg} due to {exc_type} exception: {exc}'
            logger.error(exc_msg)
            if raise_exc_on_error:
                raise errors.exceptions.APIRequestError(f'{exc_type}: {exc}')

        # Return the populated user info
        return user_info

    def get(
        self,
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
        return api.get(
            self,
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
            show_full_error=show_full_error,
            return_json=return_json,
        )

    def api_call_with_payload(
        self,
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
        return api.api_call_with_payload(
            self,
            method=method,
            endpoint=endpoint,
            payload=payload,
            params=params,
            headers=headers,
            timeout=timeout,
            show_full_error=show_full_error,
            return_json=return_json,
        )

    def post(
        self,
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
               A global constant is now leveraged for the API timeout value instead of hardcoding the value.
               (Timeout is still **30** seconds in this version)

            .. versionchanged:: 2.1.0
               The function now fails with the :py:exc:`salespyforce.errors.exceptions.POSTRequestError` exception rather
               than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

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
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        return api.api_call_with_payload(
            self,
            method=const.API_REQUEST_TYPES.POST,
            endpoint=endpoint,
            payload=payload,
            params=params,
            headers=headers,
            timeout=timeout,
            show_full_error=show_full_error,
            return_json=return_json,
        )

    def patch(
        self,
        endpoint: str,
        payload: dict,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
        show_full_error: bool = True,
        return_json: bool = False,
    ) -> dict[str, Any] | requests.Response:
        """This method performs a PATCH call against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`__)

        .. versionchanged:: 1.4.0
           A global constant is now leveraged for the API timeout value instead of hardcoding the value.
           (Timeout is still **30** seconds in this version)

        .. versionchanged:: 1.5.0
           The default value for ``return_json`` is ``False`` to preserve the published 1.4.0 behavior.

        .. versionchanged:: 2.1.0
           The function now fails with the :py:exc:`salespyforce.errors.exceptions.PATCHRequestError` exception rather
           than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

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
        :param return_json: Determines if the response should be returned in JSON format (defaults to ``False``)
        :type return_json: bool
        :returns: The API response in JSON format or as a ``requests`` object
        :rtype: dict[str, Any], requests.Response
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises ValueError: If an invalid API call method is supplied
        :raises salespyforce.errors.exceptions.PATCHRequestError: If PATCH request does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        return api.api_call_with_payload(
            self,
            method=const.API_REQUEST_TYPES.PATCH,
            endpoint=endpoint,
            payload=payload,
            params=params,
            headers=headers,
            timeout=timeout,
            show_full_error=show_full_error,
            return_json=return_json,
        )

    def put(
        self,
        endpoint: str,
        payload: dict,
        params: dict | None = None,
        headers: dict | None = None,
        timeout: int | None = None,
        show_full_error: bool = True,
        return_json: bool = True,
    ):
        """This method performs a PUT call against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`__)

        .. versionchanged:: 1.4.0
           A global constant is now leveraged for the API timeout value instead of hardcoding the value.
           (Timeout is still **30** seconds in this version)

        .. versionchanged:: 2.1.0
           The function now fails with the :py:exc:`salespyforce.errors.exceptions.PUTRequestError` exception rather
           than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

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
        :returns: The API response in JSON format or as a ``requests`` object
        :rtype: dict[str, Any], requests.Response
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises ValueError: If an invalid API call method is supplied
        :raises salespyforce.errors.exceptions.PUTRequestError: If PUT request does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        return api.api_call_with_payload(
            self,
            method=const.API_REQUEST_TYPES.PUT,
            endpoint=endpoint,
            payload=payload,
            params=params,
            headers=headers,
            timeout=timeout,
            show_full_error=show_full_error,
            return_json=return_json,
        )

    def delete(
        self,
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
        :type return_json: bool
        :returns: The API response in JSON format or as a ``requests.Response`` object
        :rtype: dict[str, Any], requests.Response
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.DELETERequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        return api.delete(
            self,
            endpoint=endpoint,
            params=params,
            headers=headers,
            timeout=timeout,
            show_full_error=show_full_error,
            return_json=return_json,
        )

    def get_api_versions(self) -> list:
        """Returns the API versions for the Salesforce releases.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_versions.htm>`__)

        :returns: A list containing the API metadata from the ``/services/data`` endpoint.
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        # TODO: Confirm that the API JSON response is a list as noted in documentation rather than a dict[str, list]
        return self.get(const.REST_PATHS.SERVICES_DATA)

    def get_latest_api_version(self) -> str:
        """Returns the latest Salesforce API version by querying the authorized org.

        .. versionadded:: 1.4.0

        :returns: The latest Salesforce API version for the authorized org as a string (e.g. ``67.0``)
        :rtype: str
        """
        versions = self.get_api_versions()
        try:
            latest_version = versions[-1][const.RESPONSE_KEYS.VERSION]
        except Exception as exc:
            exc_type = errors.handlers.get_exception_type(exc)
            logger.warning(
                f'Failed to retrieve API version due to a(n) {exc_type} exception; defaulting to '
                f'the fallback version {const.FALLBACK_SFDC_API_VERSION}'
            )
            latest_version = const.FALLBACK_SFDC_API_VERSION
        return latest_version

    def get_org_limits(self):
        """Returns a list of all org limits.

        .. versionadded:: 1.1.0

        :returns: The Salesforce org governor limits data
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        endpoint = const.REST_PATHS.LIMITS.format(api_version=self.version)
        return self.get(endpoint=endpoint)

    def get_all_sobjects(self) -> dict[str, Any]:
        """Returns a list of all Salesforce objects (i.e. sObjects) within a JSON response.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_describeGlobal.htm>`__)

        :returns: The list of all Salesforce objects within a JSON API response
        :rtype: dict[str, Any]
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        endpoint = const.REST_PATHS.SOBJECTS.format(api_version=self.version)
        return self.get(endpoint=endpoint, return_json=True)

    def get_sobject(self, object_name: str, describe: bool = False):
        """Returns basic information or the full (describe) information for a specific sObject.
        (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_basic_info_get.htm>`__,
        `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm>`__)

        :param object_name: The name of the Salesforce object
        :type object_name: str
        :param describe: Determines if the full (i.e. ``describe``) data should be returned (defaults to ``False``)
        :type describe: bool
        :returns: The Salesforce object data
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        if describe:
            endpoint = const.REST_PATHS.SOBJECT_DESCRIBE.format(
                api_version=self.version,
                sobject=object_name,
            )
        else:
            endpoint = const.REST_PATHS.SOBJECT.format(
                api_version=self.version,
                sobject=object_name,
            )
        return self.get(endpoint=endpoint)

    def describe_object(self, object_name: str):
        """Returns the full (describe) information for a specific sObject.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm>`__)

        :param object_name: The name of the Salesforce object
        :type object_name: str
        :returns: The Salesforce object data
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        return self.get_sobject(object_name=object_name, describe=True)

    def get_rest_resources(self):
        """Returns a list of all available REST resources.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_discoveryresource.htm>`__)

        :returns: The list of all available REST resources for the Salesforce org
        :raises: :py:exc:`RuntimeError`
        """
        endpoint = const.REST_PATHS.SERVICES_DATA_API.format(api_version=self.version)
        return self.get(endpoint)

    @staticmethod
    def get_18_char_id(record_id: str) -> str:
        """Converts a 15-character Salesforce record ID to its 18-character case-insensitive form.

        .. versionadded:: 1.4.0

        :param record_id: The Salesforce record ID to convert (or return unchanged if already 18 characters)
        :type record_id: str
        :returns: The 18-character Salesforce record ID
        :rtype: str
        :raises TypeError: If the Salesforce record ID provided is not a string
        :raises ValueError: If the Salesforce record ID provided is not 15 or 18 characters in length
        """
        return core_utils.get_18_char_id(record_id=record_id)

    def soql_query(
        self,
        query: str,
        replace_quotes: bool = True,
        next_records_url: bool = False,
    ) -> dict[str, Any]:
        """Performs a SOQL query and returns the results in JSON format.
        (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`__,
        `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`__)

        :param query: The SOQL query to perform
        :type query: str
        :param replace_quotes: Determines if double-quotes should be replaced with single-quotes (``True`` by default)
        :type replace_quotes: bool
        :param next_records_url: Indicates that the ``query`` parameter is a ``nextRecordsUrl`` value.
        :type next_records_url: bool
        :returns: The result of the SOQL query
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        if next_records_url:
            query = re.sub(r'^.*/', '', query) if '/' in query else query
        else:
            if replace_quotes:
                query = query.replace('"', "'")
            query = core_utils.url_encode(query)
            query = f'?{const.QUERY_PARAMS.Q}={query}'
        endpoint = f'{const.REST_PATHS.QUERY.format(api_version=self.version)}/{query}'
        return self.get(endpoint=endpoint, return_json=True)

    def search_string(self, string_to_search: str):
        """Performs a SOSL query to search for a given string.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_search.htm>`__)

        .. versionadded:: 1.1.0

        :param string_to_search: The string for which to search
        :type string_to_search: str
        :returns: The SOSL response data in JSON format
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        query = 'FIND {' + string_to_search + '}'
        query = core_utils.url_encode(query)
        endpoint = f'{const.REST_PATHS.SEARCH.format(api_version=self.version)}?{const.QUERY_PARAMS.Q}={query}'
        return self.get(endpoint)

    def check_user_record_access(self, record_id: str, user_id: str | None = None) -> dict[str, bool]:
        """This method checks the Read, Edit, and Delete access for a given record and user.

        .. versionadded:: 1.4.0

        :param record_id: The ``Id`` value of the record against which to check the user access
        :type record_id: str
        :param user_id: The ``Id`` of the user to evaluate (or the current user's ID if not explicitly defined)
        :type user_id: str, optional
        :returns: Dictionary with Boolean values for ``HasReadAccess``, ``HasEditAccess``, and ``HasDeleteAccess``
        :rtype: dict[str, bool]
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        record_access = {
            const.SOBJECT_FIELDS.HAS_READ_ACCESS: None,
            const.SOBJECT_FIELDS.HAS_EDIT_ACCESS: None,
            const.SOBJECT_FIELDS.HAS_DELETE_ACCESS: None,
        }

        # Use the current/running user's ID if an ID was not explicitly provided
        if not user_id:
            user_id = self._get_cached_user_info(_field=const.CLIENT_SETTINGS.USER_ID, _retrieve_if_missing=True)
            if user_id:
                logger.debug(f'Using the User Id {user_id} for the running user as an Id was not specified')

        # Raise an exception if the User ID is still undefined
        if not user_id:
            exc_msg = f'The user access for record Id {record_id} cannot be checked as the User Id is undefined'
            logger.error(exc_msg)
            raise errors.exceptions.MissingRequiredDataError(exc_msg)

        # Perform SOQL query for the access data
        select_fields = ', '.join(
            (
                const.SOBJECT_FIELDS.RECORD_ID,
                const.SOBJECT_FIELDS.HAS_READ_ACCESS,
                const.SOBJECT_FIELDS.HAS_EDIT_ACCESS,
                const.SOBJECT_FIELDS.HAS_DELETE_ACCESS,
            )
        )
        query = f"""
            SELECT {select_fields}
            FROM {const.SOBJECTS.USER_RECORD_ACCESS}
            WHERE {const.SOBJECT_FIELDS.USER_ID} = '{user_id}' 
            AND {const.SOBJECT_FIELDS.RECORD_ID} = '{record_id}'
        """
        response = self.soql_query(query=query)

        # Parse the response to extract the relevant field values
        if const.RESPONSE_KEYS.RECORDS in response and response[const.RESPONSE_KEYS.RECORDS]:
            response = response[const.RESPONSE_KEYS.RECORDS][0]
            for field in record_access.keys():
                record_access[field] = response.get(field, None)

        # Return the record access data
        return record_access

    @staticmethod
    def _eval_user_record_access(
        _field: str,
        _record_id: str,
        _record_access_data: dict,
        _raise_exc_on_failure: bool = True,
    ) -> bool:
        """Checks for an access level given the field and the record access data.

        .. versionadded:: 1.4.0

        :param _field: The access level field to evaluate (``HasReadAccess``, ``HasEditAccess``, ``HasDeleteAccess``)
        :type _field: str
        :param _record_id: The ID value for the record whose access is being checked
        :type _record_id: str
        :param _record_access_data: The user record access data that has already been retrieved
        :type _record_access_data: dict
        :param _raise_exc_on_failure: Raises an exception rather than returning a ``None`` value (``True`` by default)
        :type _raise_exc_on_failure: bool
        :returns: Boolean value indicating the access level for the given field
        :raises salespyforce.errors.exceptions.InvalidFieldError: If an invalid record access level field is provided
        :raises salespyforce.errors.exceptions.MissingRequiredDataError: If the field value is undefined
        """
        # Raise an exception if a valid access control field is not provided
        if _field not in const.SOBJECT_FIELDS.VALID_ACCESS_CONTROL_FIELDS:
            _exc_msg = f"The field '{_field}' is not a valid record access level field"
            logger.error(_exc_msg)
            raise errors.exceptions.InvalidFieldError(_exc_msg)

        # Identify the access level value if possible (API retrievals should be handled in a parent method)
        _has_access = _record_access_data.get(_field) if _field in _record_access_data else None
        if _has_access is None:
            _error_msg = f"The value for the '{_field}' is undefined for the given Record Id '{_record_id}'"
            logger.error(_error_msg)
            if _raise_exc_on_failure:
                raise errors.exceptions.MissingRequiredDataError(_error_msg)

        # Return the identified access level value
        return _has_access

    def can_access_record(
        self,
        access_type: str,
        record_id: str,
        user_id: str | None = None,
        record_access_data: dict | None = None,
        raise_exc_on_failure: bool = True,
    ) -> bool:
        """Evaluates if a user can access a specific record given the access type.

        .. versionadded:: 1.4.0

        :param access_type: The type of access to evaluate (``read``, ``edit``, or ``delete``)
        :type access_type: str
        :param record_id: The ID of the record
        :type record_id: str
        :param user_id: The ID of the user to evaluate (defaults to the current/running user if not defined)
        :type user_id: str, optional
        :param record_access_data: The user record access data that has already been retrieved (optional)
        :type record_access_data: dict, optional
        :param raise_exc_on_failure: Raises an exception rather than returning a ``None`` value (``True`` by default)
        :type raise_exc_on_failure: bool
        :returns: Boolean value indicating the access level for the given field
        :raises salespyforce.errors.exceptions.InvalidFieldError: If an invalid record access level field is provided
        :raises salespyforce.errors.exceptions.MissingRequiredDataError: If the field value is undefined
        """
        # Define the initial value for the result
        can_access = None

        # Identify the correct field to query based on access type
        access_type_field_mapping = {
            'read': const.SOBJECT_FIELDS.HAS_READ_ACCESS,
            'edit': const.SOBJECT_FIELDS.HAS_EDIT_ACCESS,
            'delete': const.SOBJECT_FIELDS.HAS_DELETE_ACCESS,
        }
        if access_type.lower() not in access_type_field_mapping:
            error_msg = f"The access_type '{access_type}' is invalid (must use 'read', 'edit', or 'delete')"
            logger.error(error_msg)
            if raise_exc_on_failure:
                raise errors.exceptions.InvalidParameterError(error_msg)
        else:
            # Retrieve the field name to check
            read_access_field = access_type_field_mapping.get(access_type.lower())

            # Check to see if record access data was provided and validate that it is a dictionary
            if record_access_data and not isinstance(record_access_data, dict):
                error_msg = f'The record_access_data provided is Type {type(read_access_field)} but must be a dict'
                logger.error(error_msg)
                if raise_exc_on_failure:
                    raise errors.exceptions.DataMismatchError(error_msg)

            # Perform the API all to check the record access for the user if data not provided
            if not record_access_data:
                record_access_data = self.check_user_record_access(record_id=record_id, user_id=user_id)

            # Return the access level value
            can_access = self._eval_user_record_access(
                _field=read_access_field,
                _record_id=record_id,
                _record_access_data=record_access_data,
                _raise_exc_on_failure=raise_exc_on_failure,
            )

        # Emit a warning if the value is None rather than a boolean
        if can_access is None:
            warn_msg = 'The record access check could not be completed and the function will return a None value'
            logger.warning(warn_msg)
            errors.handlers.display_warning(warn_msg)

        # Return the result
        return can_access

    def can_read_record(
        self,
        record_id: str,
        user_id: str | None = None,
        record_access_data: dict | None = None,
        raise_exc_on_failure: bool = True,
    ) -> bool:
        """Evaluates if a user has access to read a specific record.

        .. versionadded:: 1.4.0

        :param record_id: The ID of the record
        :type record_id: str
        :param user_id: The ID of the user to evaluate (defaults to the current/running user if not defined)
        :type user_id: str, optional
        :param record_access_data: The user record access data that has already been retrieved (optional)
        :type record_access_data: dict, optional
        :param raise_exc_on_failure: Raises an exception rather than returning a ``None`` value (``True`` by default)
        :type raise_exc_on_failure: bool
        :returns: Boolean value indicating the access level for the given field
        :raises salespyforce.errors.exceptions.InvalidFieldError: If an invalid record access level field is provided
        :raises salespyforce.errors.exceptions.MissingRequiredDataError: If the field value is undefined
        """
        return self.can_access_record(
            access_type='read',
            record_id=record_id,
            user_id=user_id,
            record_access_data=record_access_data,
            raise_exc_on_failure=raise_exc_on_failure,
        )

    def can_edit_record(
        self,
        record_id: str,
        user_id: str | None = None,
        record_access_data: dict | None = None,
        raise_exc_on_failure: bool = True,
    ) -> bool:
        """Evaluates if a user has access to edit a specific record.

        .. versionadded:: 1.4.0

        :param record_id: The ID of the record
        :type record_id: str
        :param user_id: The ID of the user to evaluate (defaults to the current/running user if not defined)
        :type user_id: str, None
        :param record_access_data: The user record access data that has already been retrieved (optional)
        :type record_access_data: dict, optional
        :param raise_exc_on_failure: Raises an exception rather than returning a ``None`` value (``True`` by default)
        :type raise_exc_on_failure: bool
        :returns: Boolean value indicating the access level for the given field
        :raises salespyforce.errors.exceptions.InvalidFieldError: If an invalid record access level field is provided
        :raises salespyforce.errors.exceptions.MissingRequiredDataError: If the field value is undefined
        """
        return self.can_access_record(
            access_type='edit',
            record_id=record_id,
            user_id=user_id,
            record_access_data=record_access_data,
            raise_exc_on_failure=raise_exc_on_failure,
        )

    def can_delete_record(
        self,
        record_id: str,
        user_id: str | None = None,
        record_access_data: dict | None = None,
        raise_exc_on_failure: bool = True,
    ) -> bool:
        """Evaluates if a user has access to delete a specific record.

        .. versionadded:: 1.4.0

        :param record_id: The ID of the record
        :type record_id: str
        :param user_id: The ID of the user to evaluate (defaults to the current/running user if not defined)
        :type user_id: str, optional
        :param record_access_data: The user record access data that has already been retrieved (optional)
        :type record_access_data: dict, optional
        :param raise_exc_on_failure: Raises an exception rather than returning a ``None`` value (``True`` by default)
        :type raise_exc_on_failure: bool
        :returns: Boolean value indicating the access level for the given field
        :raises salespyforce.errors.exceptions.InvalidFieldError: If an invalid record access level field is provided
        :raises salespyforce.errors.exceptions.MissingRequiredDataError: If the field value is undefined
        """
        return self.can_access_record(
            access_type='edit',
            record_id=record_id,
            user_id=user_id,
            record_access_data=record_access_data,
            raise_exc_on_failure=raise_exc_on_failure,
        )

    def create_sobject_record(self, sobject: str, payload: dict) -> dict[str, Any] | requests.Response:
        """Creates a new record for a specific sObject.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_create.htm>`__)

        :param sobject: The sObject under which to create the new record
        :type sobject: str
        :param payload: The JSON payload with the record details
        :type payload: dict
        :returns: The API response from the POST request
        :rtype: dict[str, Any], requests.Response
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises ValueError: If an invalid API call method is supplied
        :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        # Ensure the payload is in the appropriate format
        if not isinstance(payload, dict):
            logger.error(const._LOG_MESSAGES._SOBJECT_PAYLOAD_MUST_BE_DICT)
            raise TypeError(const._LOG_MESSAGES._SOBJECT_PAYLOAD_MUST_BE_DICT)

        # Perform the API call and return the response
        endpoint = const.REST_PATHS.SOBJECT.format(api_version=self.version, sobject=sobject)
        response = self.post(endpoint, payload=payload)
        return response

    def update_sobject_record(self, sobject: str, record_id: str, payload: dict):
        """Updates an existing sObject record.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_update_fields.htm>`__)

        :param sobject: The sObject under which to update the record
        :type sobject: str
        :param record_id: The ID of the record to be updated
        :type record_id: str
        :param payload: The JSON payload with the record details to be updated
        :type payload: dict
        :returns: The API response from the PATCH request
        :rtype: dict[str, Any], requests.Response
        :raises TypeError: If an invalid data type is supplied for a parameter value
        :raises ValueError: If an invalid API call method is supplied
        :raises salespyforce.errors.exceptions.PATCHRequestError: If PATCH request does not return a successful response
        :raises salespyforce.errors.exceptions.InvalidURLError: If an invalid URL is provided
        :raises requests.exceptions.Timeout: If the API request times out
        :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
        """
        # Ensure the payload is in the appropriate format
        if not isinstance(payload, dict):
            logger.error(const._LOG_MESSAGES._SOBJECT_PAYLOAD_MUST_BE_DICT)
            raise TypeError(const._LOG_MESSAGES._SOBJECT_PAYLOAD_MUST_BE_DICT)

        # Perform the API call and return the response
        endpoint = const.REST_PATHS.SOBJECT_BY_ID.format(
            api_version=self.version,
            sobject=sobject,
            record_id=record_id,
        )
        response = self.patch(endpoint, payload=payload)
        return response

    def download_image(
        self,
        image_url: str,
        record_id: str,
        field_name: str,
        file_path: str | None = None,
        sobject: str | None = None,
    ) -> str:
        """Downloads an image using the sObject Rich Text Image Retrieve functionality.
        (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_rich_text_image_retrieve.htm>`__,
        `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_rich_text_image_retrieve.htm>`__)

        .. versionchanged:: 1.5.0
           Errors are now logged and Exceptions are raised when downloading the image fails.

        :param image_url: The URL for the image to be downloaded
        :type image_url: str
        :param record_id: The Record ID where the image is found
        :type record_id: str
        :param field_name: The field name within the record where the image is found
        :type field_name: str
        :param file_path: The path to the directory where the image should be saved (current directory if not defined)
        :type file_path: str, optional
        :param sobject: The sObject for the record where the image is found (``Knowledge__kav`` by default)
        :type sobject: str, optional
        :returns: The full path to the downloaded image
        :raises RuntimeError: If the image fails to download for an unexpected reason
        :raises salespyforce.errors.exceptions.MissingRequiredDataError: If an image URL and API response are both missing
        :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
        :raises requests.exceptions.Timeout: If the GET request for the image times out
        """
        # Ensure a valid sObject is defined (SFDC Knowledge unless otherwise specified)
        if not sobject or not isinstance(sobject, str):
            sobject = const.SOBJECTS.KNOWLEDGE
            logger.info(f'The {sobject} sObject will be leveraged to download the image as an object was not provided')

        # Retrieve the reference ID for the image
        ref_id = core_utils.get_image_ref_id(image_url)

        # Define the URI and perform the API call
        try:
            endpoint = const.REST_PATHS.RICH_TEXT_IMAGE_FIELD_BY_REF_ID.format(
                api_version=self.version,
                sobject=sobject,
                record_id=record_id,
                field_name=field_name,
                ref_id=ref_id,
            )
            response = self.get(endpoint, return_json=False)

            # Save the image as an image file
            try:
                image_path = core_utils.download_image(
                    file_name=f'{ref_id}.{const.FILE_EXTENSIONS.JPEG}',
                    file_path=file_path,
                    response=response,
                )
            except RuntimeError:
                exc_msg = f'Failed to download the image with refid {ref_id}.'
                logger.error(exc_msg)
                raise RuntimeError(exc_msg)
        except Exception as exc:
            exc_type = errors.handlers.get_exception_type(exc)
            exc_msg = f'Failed to download the image with refid {ref_id} due to {exc_type} exception: {exc}'
            logger.error(exc_msg)
            raise RuntimeError(exc_msg)
        return image_path

    class Chatter:
        """Includes methods associated with Salesforce Chatter."""

        def __init__(self, sfdc_object: Salesforce):
            """Initializes the :py:class:`salespyforce.core.Salesforce.Chatter` inner class object.

            :param sfdc_object: The core :py:class:`salespyforce.Salesforce` object
            :type sfdc_object: class[salespyforce.Salesforce]
            """
            self.sfdc_object = sfdc_object

        def get_my_news_feed(self, site_id: str | None = None) -> dict[str, Any]:
            """Retrieves the news feed for the user calling the function.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_news_feed.htm>`__)

            .. versionchanged:: 2.1.0
               The function now fails with the :py:exc:`salespyforce.errors.exceptions.GETRequestError` exception rather
               than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, optional
            :returns: The news feed data
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return chatter_module.get_my_news_feed(self.sfdc_object, site_id=site_id)

        def get_user_news_feed(self, user_id: str, site_id: str | None = None) -> dict[str, Any]:
            """Retrieves another user's news feed.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_user_profile_feed.htm>`__)

            .. versionchanged:: 2.1.0
               The function now fails with the :py:exc:`salespyforce.errors.exceptions.GETRequestError` exception rather
               than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

            :param user_id: The ID of the user whose feed you wish to return
            :type user_id: str
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :returns: The news feed data
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return chatter_module.get_user_news_feed(self.sfdc_object, user_id=user_id, site_id=site_id)

        def get_group_feed(self, group_id: str, site_id: str | None = None) -> dict[str, Any]:
            """Retrieves a group's news feed.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_group_feed.htm>`__)

            .. versionchanged:: 2.1.0
               The function now fails with the :py:exc:`salespyforce.errors.exceptions.GETRequestError` exception rather
               than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

            :param group_id: The ID of the group whose feed you wish to return
            :type group_id: str
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :returns: The news feed data
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return chatter_module.get_group_feed(self.sfdc_object, group_id=group_id, site_id=site_id)

        def post_feed_item(
            self,
            subject_id: str,
            message_text: str | None = None,
            message_segments: Optional[list] = None,
            site_id: str | None = None,
            created_by_id: str | None = None,
        ) -> dict[str, Any]:
            """Publishes a new Chatter feed item.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_feed_item.htm>`__)

            .. versionchanged:: 1.4.0
               The function now raises the :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception
               rather than the generic :py:exc:`RuntimeError` exception.

            .. versionchanged:: 2.1.0
               The function now fails with the :py:exc:`salespyforce.errors.exceptions.POSTRequestError` exception rather
               than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response, and
               fails with the :py:exc:`salespyforce.errors.exceptions.DataMismatchError` exception if both message text and
               message segments are provided or if message segments are improperly structured.

            :param subject_id: The Subject ID against which to publish the feed item (e.g. ``0F9B000000000W2``)
            :type subject_id: str
            :param message_text: Plaintext to be used as the message body
            :type message_text: str, None
            :param message_segments: Collection of message segments to use instead of a plaintext message
            :type message_segments: list, None
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :param created_by_id: The ID of the user to impersonate (**Experimental**)
            :type created_by_id: str, None
            :returns: The response of the POST request
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If neither message text nor segments are provided
            :raises salespyforce.errors.exceptions.DataMismatchError: If both message text and message segments are provided or
                                                                      if message segments are improperly structured
            :raises salespyforce.errors.exceptions.POSTRequestError: If Salesforce does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return chatter_module.post_feed_item(
                self.sfdc_object,
                subject_id=subject_id,
                message_text=message_text,
                message_segments=message_segments,
                site_id=site_id,
                created_by_id=created_by_id,
            )

        def post_comment(
            self,
            feed_element_id: str,
            message_text: str | None = None,
            message_segments: Optional[list] = None,
            site_id: str | None = None,
            created_by_id: str | None = None,
        ) -> dict[str, Any]:
            """Publishes a comment on a Chatter feed item.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_comment_to_feed_element.htm>`__)

            .. versionchanged:: 1.5.0
               This method now utilizes centralized constants and a new helper function to construct the endpoint and payload.
               It also now raises the :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception rather
               than the generic :py:exc:`RuntimeError` exception.

            .. versionchanged:: 2.1.0
               The method now fails with the :py:exc:`salespyforce.errors.exceptions.POSTRequestError` exception rather
               than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response, and
               fails with the :py:exc:`salespyforce.errors.exceptions.DataMismatchError` exception if both message text and
               message segments are provided or if message segments are improperly structured.

            :param feed_element_id: The ID of the feed element on which to post the comment
            :type feed_element_id: str
            :param message_text: Plaintext to be used as the message body
            :type message_text: str, optional
            :param message_segments: Collection of message segments to use instead of a plaintext message
            :type message_segments: list, optional
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, optional
            :param created_by_id: The ID of the user to impersonate (**Experimental**)
            :type created_by_id: str, optional
            :returns: The response of the POST request in JSON format
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If neither message text nor segments are provided
            :raises salespyforce.errors.exceptions.DataMismatchError: If both message text and message segments are provided or
                                                                      if message segments are improperly structured
            :raises salespyforce.errors.exceptions.POSTRequestError: If Salesforce does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return chatter_module.post_comment(
                self.sfdc_object,
                feed_element_id=feed_element_id,
                message_text=message_text,
                message_segments=message_segments,
                site_id=site_id,
                created_by_id=created_by_id,
            )

    class Knowledge:
        """Includes methods associated with Salesforce Knowledge."""

        def __init__(self, sfdc_object: Salesforce):
            """Initializes the :py:class:`salespyforce.core.Salesforce.Knowledge` inner class object.

            :param sfdc_object: The core :py:class:`salespyforce.Salesforce` object
            :type sfdc_object: class[salespyforce.Salesforce]
            """
            self.sfdc_object = sfdc_object

        def check_for_existing_article(
            self,
            title: str,
            sobject: str | None = None,
            return_id: bool = False,
            return_id_and_number: bool = False,
            include_archived: bool = False,
        ) -> str | Tuple[str, str]:
            """Checks to see if an article already exists with a given title and returns its article number.
            (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`__.
            `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`__)

            :param title: The title of the knowledge article for which to check
            :type title: str
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :param return_id: Determines if the Article ID should be returned (``False`` by default)
            :type return_id: bool
            :param return_id_and_number: Determines if Article ID and Article Number should be returned (``False`` by default)
            :type return_id_and_number: bool
            :param include_archived: Determines if archived articles should be included (``False`` by default)
            :type include_archived: bool
            :returns: The Article Number, Article ID, or both (if found), or a blank string if not found
            :rtype: str, Tuple[str, str]
            :raises TypeError: If ``sobject`` value is not a string
            :raises salespyforce.errors.exceptions.DataMismatchError: If attempting to use the ``knowledgeArticles`` endpoint
                                                                      with a non-standard Knowledge sObject
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.check_for_existing_article(
                self.sfdc_object,
                title=title,
                sobject=sobject,
                return_id=return_id,
                return_id_and_number=return_id_and_number,
                include_archived=include_archived,
            )

        def get_article_id_from_number(
            self,
            article_number: Union[str, int],
            sobject: str | None = None,
            return_uri: bool = False,
        ) -> str:
            """Returns the Article ID when an article number is provided.
            (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`__,
            `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`__)

            .. warning::
               The ability to retrieve the article URI/URL rather than the ID will be moved to a separate function in
               a future release.

            :param article_number: The Article Number to query
            :type article_number: str, int
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param return_uri: Determines if the URI of the article should be returned rather than the ID (``False`` by default)
            :type return_uri: bool
            :returns: The Article ID or Article URI, or a blank string if no article is found
            :rtype: str
            :raises TypeError: If ``sobject`` value is not a string
            :raises salespyforce.errors.exceptions.DataMismatchError: If attempting to use the ``knowledgeArticles``
                                                                      endpoint with a non-standard Knowledge sObject
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful, valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            # TODO: Move return_uri functionality (here and in underlying function) to a separate method/function
            return knowledge_module.get_article_id_from_number(
                self.sfdc_object,
                article_number=article_number,
                sobject=sobject,
                return_uri=return_uri,
            )

        def get_articles_list(
            self,
            query: str | None = None,
            sort: str | None = None,
            order: str | None = None,
            page_size: int = const.QUERY_PARAMS.DEFAULT_PAGE_SIZE,
            page_num: int = const.QUERY_PARAMS.DEFAULT_PAGE_NUM,
        ) -> list:
            """Retrieves a list of knowledge articles.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artlist.htm>`__)

            .. versionchanged:: 1.4.0
               The errors now log as errors via the logger rather than to the stderr console.

            .. versionchanged:: 2.1.0
               It is now possible to return the list of articles (default) or the full API response in JSON format.

            :param query: A SOQL query with which to filter the results (optional)
            :type query: str, optional
            :param sort: Optionally sort the results with one of the following values: ``LastPublishedDate``,
                         ``CreatedDate``, ``Title``, or ``ViewScore``
            :type sort: str, optional
            :param order: Optionally define the ORDER BY as ``ASC`` or ``DESC``
            :type order: str, optional
            :param page_size: The number of results per page (``20`` by default)
            :type page_size: int
            :param page_num: The starting page number (``1`` by default)
            :type page_num: int
            :returns: The list of retrieved knowledge articles
            :rtype: list[dict], dict[str, Any]
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful, valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.get_articles_list(
                self.sfdc_object,
                query=query,
                sort=sort,
                order=order,
                page_size=page_size,
                page_num=page_num,
            )

        def get_article_details(
            self,
            article_id: str,
            sobject: str | None = None,
            use_knowledge_articles_endpoint: Optional[bool] = None,
        ) -> dict[str, Any]:
            """Retrieves details for a single knowledge article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`__)

            .. versionchanged:: 1.4.0
               A logic issue was resolved and the new optional ``use_knowledge_articles_endpoint`` parameter can
               now be set to force the ``knowledgeArticles`` endpoint to be used for the GET request rather than
               the ``sobjects`` endpoint.

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :param use_knowledge_articles_endpoint: Optionally use the ``knowledgeArticles`` endpoint rather than
                                                    ``sobjects`` to retrieve the article details (``False`` by default)
            :type use_knowledge_articles_endpoint: bool, optional
            :returns: The details for the knowledge article
            :rtype: dict[str, Any]
            :raises TypeError: if ``sobject`` is not a string
            :raises salespyforce.errors.exceptions.DataMismatchError: If attempting to use the ``knowledgeArticles`` endpoint
                                                                      with a non-standard Knowledge sObject
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful, valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.get_article_details(
                self.sfdc_object,
                article_id=article_id,
                sobject=sobject,
                use_knowledge_articles_endpoint=use_knowledge_articles_endpoint,
            )

        def get_validation_status(
            self,
            article_id: str | None = None,
            article_details: dict | None = None,
            sobject: str | None = None,
            use_knowledge_articles_endpoint: Optional[bool] = None,
        ) -> str:
            """Retrieves the Validation Status for a given Article ID.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`__)

            .. versionchanged:: 1.4.0
               The method now returns an empty string rather than a ``None`` value if the ``ValidationStatus`` field
               is not found in the article details data, and a more specific exception class is used when input
               data is missing instead of the generic :py:exc:`RuntimeError` exception class.

            .. versionchanged:: 1.5.0
               The `use_knowledge_articles_endpoint` parameter is now supported, which allows you to specify the
               REST path to utilize for the API query.

            .. versionchanged:: 2.1.0
               A :py:exc:`TypeError` exception is now raised if the article details is not the appropriate data type.

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str, optional
            :param article_details: The dictionary of article details for the given article
            :type article_details: dict, optional
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :param use_knowledge_articles_endpoint: Optionally use the ``knowledgeArticles`` endpoint rather than ``sobjects``
                                                    to retrieve the article details (``False`` by default)
            :type use_knowledge_articles_endpoint: bool, optional
            :returns: The validation status as a text string
            :rtype: str
            :raises TypeError: If the article details are an invalid data type and cannot be parsed
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If missing both the article ID and article details
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful, valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.get_validation_status(
                self.sfdc_object,
                article_id=article_id,
                article_details=article_details,
                sobject=sobject,
                use_knowledge_articles_endpoint=use_knowledge_articles_endpoint,
            )

        def get_article_metadata(self, article_id: str) -> dict:
            """Retrieves metadata for a specific knowledge article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_metadata.htm>`__)

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str
            :returns: The article metadata as a dictionary
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful, valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.get_article_metadata(self.sfdc_object, article_id=article_id)

        def get_article_version(self, article_id: str):
            """Retrieves the version ID for a given master article ID.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_version.htm>`__)

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str
            :returns: The version ID for the given master article ID
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful, valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            # TODO: Determine how the data is returned and if it needs to be pruned to just the article version
            return knowledge_module.get_article_version(self.sfdc_object, article_id=article_id)

        def get_article_url(
            self,
            article_id: str | None = None,
            article_number: Optional[Union[str, int]] = None,
            sobject: str | None = None,
        ) -> str:
            """Constructs the URL to view a knowledge article in Lightning or Classic.

            .. versionchanged:: 1.2.0
               Changed when lightning URLs are defined and fixed an issue with extraneous slashes.

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str, optional
            :param article_number: The article number for which to retrieve details
            :type article_number: str, int, optional
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :returns: The article URL as a string
            :rtype: str
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If missing both the article ID and article number
            :raises salespyforce.errors.exceptions.DataMismatchError: If attempting to use the ``knowledgeArticles``
                                                                      endpoint with a non-standard Knowledge sObject
            :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful, valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.get_article_url(
                self.sfdc_object, article_id=article_id, article_number=article_number, sobject=sobject
            )

        def create_article(
            self,
            article_data: dict,
            sobject: str | None = None,
            full_response: bool = False,
        ) -> str | dict[str, Any]:
            """Creates a new knowledge article draft.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_create.htm>`__)

            :param article_data: The article data used to populate the article
            :type article_data: dict
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :param full_response: Determines if the full API response should be returned instead of the article ID (``False`` by default)
            :type full_response: bool
            :returns: The API response in JSON format or the ID of the article draft
            :rtype: str, dict[str, Any]
            :raises TypeError: if sobject is not a string or the article data is not a dictionary and cannot be parsed
            :raises ValueError: if the ``id`` field is not found in the API response
            :raises salespyforce.errors.exceptions.DataMismatchError: If the article data is required but not provided
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If a required field is missing from the article data
            :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.create_article(
                self.sfdc_object,
                article_data=article_data,
                sobject=sobject,
                full_response=full_response,
            )

        def update_article(
            self,
            record_id: str,
            article_data: dict,
            sobject: str | None = None,
            include_status_code: bool = False,
        ) -> bool | Tuple[bool, int]:
            """Updates an existing knowledge article draft.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_update_fields.htm>`__)

            .. versionchanged:: 2.1.0
               Fixed an issue where the PATCH response was being incorrectly converted to JSON format.

            :param record_id: The ID of the article draft record to be updated
            :type record_id: str
            :param article_data: The article data used to update the article
            :type article_data: dict[str, Any]
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :param include_status_code: Determines if the API response status code should be returned (``False`` by default)
            :type include_status_code: bool
            :returns: A Boolean indicating if the update operation was successful, and optionally the API response status code
            :rtype: bool, Tuple[bool, int]
            :raises TypeError: if sobject is not a string or the article data is not a dictionary and cannot be parsed
            :raises salespyforce.errors.exceptions.DataMismatchError: If the article data is required but not provided
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If a required field is missing from the article data
            :raises salespyforce.errors.exceptions.PATCHRequestError: If PATCH request does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.update_article(
                self.sfdc_object,
                record_id=record_id,
                article_data=article_data,
                sobject=sobject,
                include_status_code=include_status_code,
            )

        def create_draft_from_online_article(self, article_id: str, unpublish: bool = False):
            """Creates a draft knowledge article from an online article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/actions_obj_knowledge.htm#createDraftFromOnlineKnowledgeArticle>`__)

            :param article_id: The ID of the online article from which to create the draft
            :type article_id: str
            :param unpublish: Determines if the online article should be unpublished when the draft is created (``False`` by default)
            :type unpublish: bool
            :returns: The API response from the POST request in JSON format
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.create_draft_from_online_article(
                self.sfdc_object,
                article_id=article_id,
                unpublish=unpublish,
            )

        def create_draft_from_master_version(
            self,
            article_id: str | None = None,
            knowledge_article_id: str | None = None,
            article_data: dict | None = None,
            sobject: str | None = None,
            full_response: bool = False,
        ):
            """Creates an online version of a master article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.198.0.knowledge_dev.meta/knowledge_dev/knowledge_REST_edit_online_master.htm>`__)

            .. versionchanged:: 1.5.0
               The :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception class is now raised when
               required parameters are missing instead of the generic :py:exc:`RuntimeError` exception.

            :param article_id: The Article ID from which to create the draft
            :type article_id: str, optional
            :param knowledge_article_id: The Knowledge Article ID (``KnowledgeArticleId``) from which to create the draft
            :type knowledge_article_id: str, optional
            :param article_data: The article data associated with the article from which to create the draft
            :type article_data: dict, optional
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :param full_response: Determines if the full API response should be returned instead of the article ID (``False`` by default)
            :type full_response: bool
            :returns: The API response or the ID of the article draft
            :rtype: str, dict[str, Any]
            :raises TypeError: if sobject is not a string or the article data is not a dictionary and cannot be parsed
            :raises salespyforce.errors.exceptions.DataMismatchError: If the article data is required but not provided
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If a required field is missing from the article data
            :raises salespyforce.errors.exceptions.GETRequestError: If GET request does not return a successful response
            :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.create_draft_from_master_version(
                self.sfdc_object,
                article_id=article_id,
                knowledge_article_id=knowledge_article_id,
                article_data=article_data,
                sobject=sobject,
                full_response=full_response,
            )

        def publish_article(self, article_id: str, major_version: bool = True, full_response: bool = False):
            """Publishes a draft knowledge article as a major or minor version.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_publish_master_version.htm>`__)

            .. versionchanged:: 2.1.0
               Fixed an issue where the PATCH response was being incorrectly converted to JSON format.

            :param article_id: The Article ID to publish
            :type article_id: str
            :param major_version: Determines if the published article should be a major version (``True`` by default)
            :type major_version: bool
            :param full_response: Determines if the full API response should be returned (``False`` by default)
            :type full_response: bool
            :returns: A Boolean value indicating the success of the action or the API response from the PATCH request
            :rtype: bool, requests.Response
            :raises salespyforce.errors.exceptions.PATCHRequestError: If PATCH request does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.publish_article(
                self.sfdc_object,
                article_id=article_id,
                major_version=major_version,
                full_response=full_response,
            )

        def publish_multiple_articles(
            self,
            article_id_list: list,
            major_version: bool = True,
        ) -> requests.Response:
            """Publishes multiple knowledge article drafts at one time.
            (`Reference <https://developer.salesforce.com/docs/platform/api-action/guide/actions-obj-knowledge.html#publish-knowledge-articles>`__)

            .. versionchanged:: 1.5.0
               The :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception class is now raised
               when required parameters are missing instead of a more generic exception.

            .. versionchanged:: 2.1.0
               The full ``requests.Response`` object is now always returned.

            :param article_id_list: A list of Article IDs to be published
            :type article_id_list: list
            :param major_version: Determines if the published article should be a major version (``True`` by default)
            :type major_version: bool
            :returns: The API response from the POST request
            :rtype: requests.Response
            :raises salespyforce.errors.exceptions.MissingRequiredDataError: If the article ID list is empty or invalid
            :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.publish_multiple_articles(
                self.sfdc_object,
                article_id_list=article_id_list,
                major_version=major_version,
            )

        def assign_data_category(
            self,
            article_id: str,
            category_group_name: str,
            category_name: str,
        ) -> dict[str, Any]:
            """Assigns a single data category for a knowledge article.
            (`Reference <https://itsmemohit.medium.com/quick-win-15-salesforce-knowledge-rest-apis-bb0725b2040e>`__)

            .. versionadded:: 1.2.0

            :param article_id: The ID of the article to update
            :type article_id: str
            :param category_group_name: The unique Data Category Group Name
            :type category_group_name: str
            :param category_name: The unique Data Category Name
            :type category_name: str
            :returns: The API response from the POST request in JSON format
            :rtype: dict[str, Any]
            :raises salespyforce.errors.exceptions.POSTRequestError: If POST request does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.assign_data_category(
                self.sfdc_object,
                article_id=article_id,
                category_group_name=category_group_name,
                category_name=category_name,
            )

        def archive_article(
            self,
            article_id: str,
            full_response: bool = False,
        ) -> bool | requests.Response:
            """Archives a published knowledge article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_archive_master_version.htm>`__)

            .. versionadded:: 1.3.0

            .. versionchanged:: 2.1.0
               It is now possible to return a Boolean value indicating whether the archival was successful (default), or
               the full API response from the PATCH request.

            :param article_id: The ID of the article to archive
            :type article_id: str
            :param full_response: Returns a full response instead of a Boolean response if ``True`` (``False`` by default)
            :type full_response: bool
            :returns: Boolean value indicating if the archival was successful or the API response from the PATCH request
            :rtype: bool, requests.Response
            :raises salespyforce.errors.exceptions.PATCHRequestError: If PATCH request does not return a valid response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.archive_article(
                self.sfdc_object,
                article_id=article_id,
                full_response=full_response,
            )

        def delete_article_draft(
            self,
            version_id: str,
            sobject: str | None = None,
            use_knowledge_management_endpoint: bool = True,
        ):
            """Deletes an unpublished knowledge article draft.

            .. versionadded:: 1.4.0

            .. versionchanged:: 1.5.0
               An optional ``sobject`` parameter can now be passed to specify the sObject against which to query.

            :param version_id: The 15-character or 18-character ``Id`` (Knowledge Article Version ID) value
            :type version_id: str
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, optional
            :param use_knowledge_management_endpoint: Leverage the ``/knowledgeManagement/articleVersions/masterVersions/``
                                                      endpoint rather than the ``/sobjects/Knowledge__kav/`` endpoint
                                                      (``True`` by default)
            :type use_knowledge_management_endpoint: bool
            :returns: The API response from the DELETE request
            :rtype: requests.Response
            :raises TypeError: if the sobject is not a string
            :raises salespyforce.errors.exceptions.DataMismatchError: If attempting to use the ``knowledgeArticles``
                                                                      endpoint with a non-standard Knowledge sObject
            :raises salespyforce.errors.exceptions.DELETERequestError: If Salesforce does not return a successful response
            :raises requests.exceptions.Timeout: If the API request times out
            :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
            """
            return knowledge_module.delete_article_draft(
                self.sfdc_object,
                version_id=version_id,
                sobject=sobject,
                use_knowledge_management_endpoint=use_knowledge_management_endpoint,
            )


def define_connection_info() -> dict:
    """Prompts the user for the connection information.

    :returns: The connection info in a dictionary
    """
    base_url = input('Enter your instance URL: [] ')
    org_id = input('Enter the Org ID for your instance: [] ')
    username = input('Enter the username of your API user: [] ')
    password = input('Enter the password of your API user: [] ')
    endpoint_url = input('Enter the endpoint URL: [] ')
    client_id = input('Enter the Client ID: [] ')
    client_secret = input('Enter the Client Secret: [] ')
    security_token = input('Enter the Security Token: [] ')
    connection_info = compile_connection_info(
        base_url=base_url,
        org_id=org_id,
        username=username,
        password=password,
        endpoint_url=endpoint_url,
        client_id=client_id,
        client_secret=client_secret,
        security_token=security_token,
    )
    return connection_info


def compile_connection_info(
    base_url: str,
    org_id: str,
    username: str,
    password: str,
    endpoint_url: str,
    client_id: str,
    client_secret: str,
    security_token: str,
) -> dict:
    """Compiles the connection info into a dictionary that can be consumed by the core object.

    :param base_url: The base URL of the Salesforce instance
    :type base_url: str
    :param org_id: The Org ID of the Salesforce instance
    :type org_id: str
    :param username: The username of the API user
    :type username: str
    :param password: The password of the API user
    :type password: str
    :param endpoint_url: The endpoint URL for the Salesforce instance
    :type endpoint_url: str
    :param client_id: The Client ID for the Salesforce instance
    :type client_id: str
    :param client_secret: The Client Secret for the Salesforce instance
    :type client_secret: str
    :param security_token: The Security Token for the Salesforce instance
    :type security_token: str
    :returns: The connection info in a dictionary
    :rtype: dict[str, Any]
    """
    connection_info = {
        'base_url': base_url,
        'org_id': org_id,
        'username': username,
        'password': password,
        'endpoint_url': endpoint_url,
        'client_id': client_id,
        'client_secret': client_secret,
        'security_token': security_token,
    }
    return connection_info
