# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.core
:Synopsis:          This module performs the core Salesforce-related operations
:Usage:             ``from salespyforce import Salesforce``
:Example:           ``sfdc = Salesforce(helper=helper_file_path)``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     30 Jan 2026
"""

import re

import requests

from . import api, errors
from . import chatter as chatter_module
from . import knowledge as knowledge_module
from .utils import core_utils, log_utils
from .utils.helper import get_helper_settings

# Define constants
FALLBACK_SFDC_API_VERSION = '65.0'      # Used if querying the org for the version fails

# Initialize logging
logger = log_utils.initialize_logging(__name__)


class Salesforce(object):
    """This is the class for the core object leveraged in this module."""
    # Define the function that initializes the object instance (i.e. instantiates the object)
    def __init__(self, connection_info=None, version=None, base_url=None, org_id=None, username=None,
                 password=None, endpoint_url=None, client_id=None, client_secret=None, security_token=None, helper=None):
        """This method instantiates the core Salesforce object.

        .. version-changed:: 1.4.0
           The authorized Salesforce org is now queried to determine the latest API version to leverage unless
           explicitly defined with the ``version`` parameter when instantiating the object.

        :param connection_info: The information for connecting to the Salesforce instance
        :type connection_info: dict, None
        :param version: The Salesforce API version to utilize (uses latest version from org if not explicitly defined)
        :type version: str, None
        :param base_url: The base URL of the Salesforce instance
        :type base_url: str, None
        :param org_id: The Org ID of the Salesforce instance
        :type org_id: str, None
        :param username: The username of the API user
        :type username: str, None
        :param password: The password of the API user
        :type password: str, None
        :param endpoint_url: The endpoint URL for the Salesforce instance
        :type endpoint_url: str, None
        :param client_id: The Client ID for the Salesforce instance
        :type client_id: str, None
        :param client_secret: The Client Secret for the Salesforce instance
        :type client_secret: str, None
        :param security_token: The Security Token for the Salesforce instance
        :type security_token: str, None
        :param helper: The file path of a helper file
        :type helper: str, None
        :returns: The instantiated object
        :raises: :py:exc:`TypeError`,
                 :py:exc:`RuntimeError`
        """
        # Define the default settings
        self._helper_settings = {}

        # Check for provided connection info
        if connection_info is None:
            # Check for a supplied helper file
            if helper:
                # Parse the helper file contents
                self.helper_path = helper
                if any((isinstance(helper, tuple), isinstance(helper, list), isinstance(helper, set))):
                    helper_file_path, helper_file_type = helper
                elif isinstance(helper, str):
                    helper_file_path, helper_file_type = (helper, 'yaml')
                elif isinstance(helper, dict):
                    helper_file_path, helper_file_type = helper.values()
                else:
                    error_msg = "The 'helper' argument can only be supplied as tuple, string, list, set or dict."
                    logger.error(error_msg)
                    raise TypeError(error_msg)
                self._helper_settings = get_helper_settings(helper_file_path, helper_file_type)
                connection_info = self._parse_helper_connection_info()
            elif not any((base_url, org_id, username, password, endpoint_url, client_id, client_secret, security_token)):
                # Prompt for the connection info if not defined
                connection_info = define_connection_info()
            else:
                # Compile the connection info from the provided parameters
                connection_info = compile_connection_info(base_url, org_id, username, password, endpoint_url,
                                                          client_id, client_secret, security_token)

        # Get the connection information used to connect to the instance
        self.connection_info = connection_info if connection_info is not None else self._get_empty_connection_info()

        # Define the base URL value
        self.base_url = self.connection_info.get('base_url')

        # Define the connection response data variables
        auth_response = self.connect()
        self.access_token = auth_response.get('access_token')
        self.instance_url = auth_response.get('instance_url')
        self.signature = auth_response.get('signature')

        # Define the version with explicitly provided version or by querying the Salesforce org
        self.version = f'v{version}' if version else f'v{self.get_latest_api_version()}'

        # Import inner object classes so their methods can be called from the primary object
        self.chatter = self._import_chatter_class()
        self.knowledge = self._import_knowledge_class()

    def _import_chatter_class(self):
        """This method allows the :py:class:`salespyforce.core.Salesforce.Chatter` class to be utilized in the core object."""
        return Salesforce.Chatter(self)

    def _import_knowledge_class(self):
        """This method allows the :py:class:`salespyforce.core.Salesforce.Knowledge` class to be utilized in the core object."""
        return Salesforce.Knowledge(self)

    @staticmethod
    def _get_empty_connection_info():
        """This method returns an empty connection_info dictionary with all blank values."""
        _connection_info = {}
        _fields = ['username', 'password', 'base_url', 'endpoint_url',
                   'client_key', 'client_secret', 'org_id', 'security_token']
        for _field in _fields:
            _connection_info[_field] = ''
        return _connection_info

    def _parse_helper_connection_info(self):
        """This method parses the helper content to populate the connection info."""
        _connection_info = {}
        _fields = ['username', 'password', 'base_url', 'endpoint_url',
                   'client_key', 'client_secret', 'org_id', 'security_token']
        for _field in _fields:
            if _field in self._helper_settings['connection']:
                _connection_info[_field] = self._helper_settings['connection'][_field]
        return _connection_info

    def _get_headers(self, _header_type='default'):
        """This method returns the appropriate HTTP headers to use for different types of API calls."""
        return api._get_headers(_access_token=self.access_token, _header_type=_header_type)

    def connect(self):
        """This method connects to the Salesforce instance to obtain the access token.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

        :returns: The API call response with the authorization information
        :raises: :py:exc:`RuntimeError`
        """
        params = {
            'grant_type': 'password',
            'client_id': self.connection_info.get('client_key'),
            'client_secret': self.connection_info.get('client_secret'),
            'username': self.connection_info.get('username'),
            'password': f'{self.connection_info.get("password")}{self.connection_info.get("security_token")}'
        }
        response = requests.post(self.connection_info.get('endpoint_url'), params=params)
        if response.status_code != 200:
            raise RuntimeError(f'Failed to connect to the Salesforce instance.\n{response.text}')
        return response.json()

    def get(self, endpoint, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
        """This method performs a GET request against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

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
        :raises: :py:exc:`RuntimeError`
        """
        return api.get(self, endpoint=endpoint, params=params, headers=headers, timeout=timeout,
                       show_full_error=show_full_error, return_json=return_json)

    def api_call_with_payload(self, method, endpoint, payload, params=None, headers=None, timeout=30,
                              show_full_error=True, return_json=True):
        """This method performs a POST call against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

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
        :raises: :py:exc:`RuntimeError`
        """
        return api.api_call_with_payload(self, method=method, endpoint=endpoint, payload=payload, params=params,
                                         headers=headers, timeout=timeout, show_full_error=show_full_error,
                                         return_json=return_json)

    def post(self, endpoint, payload, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
        """This method performs a POST call against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

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
        :raises: :py:exc:`RuntimeError`
        """
        return api.api_call_with_payload(self, 'post', endpoint=endpoint, payload=payload, params=params,
                                         headers=headers, timeout=timeout, show_full_error=show_full_error,
                                         return_json=return_json)

    def patch(self, endpoint, payload, params=None, headers=None, timeout=30, show_full_error=True, return_json=False):
        """This method performs a PATCH call against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

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
        :raises: :py:exc:`RuntimeError`
        """
        return api.api_call_with_payload(self, 'patch', endpoint=endpoint, payload=payload, params=params,
                                         headers=headers, timeout=timeout, show_full_error=show_full_error,
                                         return_json=return_json)

    def put(self, endpoint, payload, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
        """This method performs a PUT call against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

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
        :raises: :py:exc:`RuntimeError`
        """
        return api.api_call_with_payload(self, 'put', endpoint=endpoint, payload=payload, params=params,
                                         headers=headers, timeout=timeout, show_full_error=show_full_error,
                                         return_json=return_json)

    def delete(self, endpoint, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
        """This method performs a DELETE request against the Salesforce instance.
        (`Reference <https://jereze.com/code/authentification-salesforce-rest-api-python/>`_)

        .. version-added:: 1.4.0

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
        :raises: :py:exc:`RuntimeError`
        """
        return api.delete(self, endpoint=endpoint, params=params, headers=headers, timeout=timeout,
                          show_full_error=show_full_error, return_json=return_json)

    def get_api_versions(self) -> list:
        """This method returns the API versions for the Salesforce releases.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_versions.htm>`_)

        :returns: A list containing the API metadata from the ``/services/data`` endpoint.
        :raises: :py:exc:`RuntimeError`
        """
        return self.get('/services/data')

    def get_latest_api_version(self) -> str:
        """This method returns the latest Salesforce API version by querying the authorized org.

        .. version-added:: 1.4.0

        :returns: The latest Salesforce API version for the authorized org as a string (e.g. ``65.0``)
        """
        versions = self.get_api_versions()
        try:
            latest_version = versions[-1]['version']
        except Exception as exc:
            exc_type = type(exc).__name__
            logger.warning(
                f"Failed to retrieve API version due to a(n) {exc_type} exception; defaulting to "
                f"the fallback version {FALLBACK_SFDC_API_VERSION}"
            )
            latest_version = FALLBACK_SFDC_API_VERSION
        return latest_version

    def get_org_limits(self):
        """This method returns a list of all org limits.

        .. version-added:: 1.1.0

        :returns: The Salesforce org governor limits data
        :raises: :py:exc:`RuntimeError`
        """
        return self.get(f'/services/data/{self.version}/limits')

    def get_all_sobjects(self):
        """This method returns a list of all Salesforce objects. (i.e. sObjects)
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_describeGlobal.htm>`_)

        :returns: The list of all Salesforce objects
        :raises: :py:exc:`RuntimeError`
        """
        return self.get(f'/services/data/{self.version}/sobjects')

    def get_sobject(self, object_name, describe=False):
        """This method returns basic information or the full (describe) information for a specific sObject.
        (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_basic_info_get.htm>`_,
        `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm>`_)

        :param object_name: The name of the Salesforce object
        :type object_name: str
        :param describe: Determines if the full (i.e. ``describe``) data should be returned (defaults to ``False``)
        :type describe: bool
        :returns: The Salesforce object data
        :raises: :py:exc:`RuntimeError`
        """
        uri = f'/services/data/{self.version}/sobjects/{object_name}'
        uri = f'{uri}/describe' if describe else uri
        return self.get(uri)

    def describe_object(self, object_name):
        """This method returns the full (describe) information for a specific sObject.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm>`_)

        :param object_name: The name of the Salesforce object
        :type object_name: str
        :returns: The Salesforce object data
        :raises: :py:exc:`RuntimeError`
        """
        return self.get_sobject(object_name, describe=True)

    def get_rest_resources(self):
        """This method returns a list of all available REST resources.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_discoveryresource.htm>`_)

        :returns: The list of all available REST resources for the Salesforce org
        :raises: :py:exc:`RuntimeError`
        """
        return self.get(f'/services/data/{self.version}')

    @staticmethod
    def get_18_char_id(record_id: str) -> str:
        """This method converts a 15-character Salesforce record ID to its 18-character case-insensitive form.

        .. version-added:: 1.4.0

        :param record_id: The Salesforce record ID to convert (or return unchanged if already 18 characters)
        :type record_id: str
        :returns: The 18-character Salesforce record ID
        :raises: :py:exc:`ValueError`
        """
        return core_utils.get_18_char_id(record_id=record_id)

    def soql_query(self, query, replace_quotes=True, next_records_url=False):
        """This method performs a SOQL query and returns the results in JSON format.
        (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`_,
        `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`_)

        :param query: The SOQL query to perform
        :type query: str
        :param replace_quotes: Determines if double-quotes should be replaced with single-quotes (``True`` by default)
        :type replace_quotes: bool
        :param next_records_url: Indicates that the ``query`` parameter is a ``nextRecordsUrl`` value.
        :type next_records_url: bool
        :returns: The result of the SOQL query
        :raises: :py:exc:`RuntimeError`
        """
        if next_records_url:
            query = re.sub(r'^.*/', '', query) if '/' in query else query
        else:
            if replace_quotes:
                query = query.replace('"', "'")
            query = core_utils.url_encode(query)
            query = f'?q={query}'
        return self.get(f'/services/data/{self.version}/query/{query}')

    def search_string(self, string_to_search):
        """This method performs a SOSL query to search for a given string.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_search.htm>`_)

        .. version-added:: 1.1.0

        :param string_to_search: The string for which to search
        :type string_to_search: str
        :returns: The SOSL response data in JSON format
        :raises: :py:exc:`RuntimeError`
        """
        query = 'FIND {' + string_to_search + '}'
        query = core_utils.url_encode(query)
        return self.get(f'/services/data/{self.version}/search/?q={query}')

    def create_sobject_record(self, sobject, payload):
        """This method creates a new record for a specific sObject.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_create.htm>`_)

        :param sobject: The sObject under which to create the new record
        :type sobject: str
        :param payload: The JSON payload with the record details
        :type payload: dict
        :returns: The API response from the POST request
        :raises: :py:exc:`RuntimeError`,
                 :py:exc:`TypeError`
        """
        # Ensure the payload is in the appropriate format
        if not isinstance(payload, dict):
            raise TypeError('The sObject payload must be provided as a dictionary.')

        # Perform the API call and return the response
        response = self.post(f'/services/data/{self.version}/sobjects/{sobject}', payload=payload)
        return response

    def update_sobject_record(self, sobject, record_id, payload):
        """This method updates an existing sObject record.
        (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_update_fields.htm>`_)

        :param sobject: The sObject under which to update the record
        :type sobject: str
        :param record_id: The ID of the record to be updated
        :type record_id: str
        :param payload: The JSON payload with the record details to be updated
        :type payload: dict
        :returns: The API response from the PATCH request
        :raises: :py:exc:`RuntimeError`,
                 :py:exc:`TypeError`
        """
        # Ensure the payload is in the appropriate format
        if not isinstance(payload, dict):
            raise TypeError('The sObject payload must be provided as a dictionary.')

        # Perform the API call and return the response
        response = self.patch(f'/services/data/{self.version}/sobjects/{sobject}/{record_id}', payload=payload)
        return response

    def download_image(self, image_url, record_id, field_name, file_path=None, sobject=None):
        """This method downloads an image using the sObject Rich Text Image Retrieve functionality.
        (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_rich_text_image_retrieve.htm>`_,
        `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_rich_text_image_retrieve.htm>`_)

        :param image_url: The URL for the image to be downloaded
        :type image_url: str
        :param record_id: The Record ID where the image is found
        :type record_id: str
        :param field_name: The field name within the record where the image is found
        :type field_name: str
        :param file_path: The path to the directory where the image should be saved (current directory if not defined)
        :type file_path: str, None
        :param sobject: The sObject for the record where the image is found (``Knowledge__kav`` by default)
        :type sobject: str
        :returns: The full path to the downloaded image
        :raises: :py:exc:`RuntimeError`
        """
        # Ensure a valid sObject is defined (SFDC Knowledge unless otherwise specified)
        sobject = 'Knowledge__kav' if not sobject else sobject

        # Retrieve the reference ID for the image
        ref_id = core_utils.get_image_ref_id(image_url)

        # Define the URI and perform the API call
        image_path = None
        try:
            uri = f'/services/data/{self.version}/sobjects/{sobject}/{record_id}/richTextImageFields/{field_name}/{ref_id}'
            response = self.get(uri, return_json=False)

            # Save the image as an image file
            try:
                image_path = core_utils.download_image(file_name=f'{ref_id}.jpeg', file_path=file_path,
                                                       response=response)
            except RuntimeError:
                errors.handlers.eprint(f'Failed to download the image with refid {ref_id}.')
        except RuntimeError as exc:
            errors.handlers.eprint(exc)
        return image_path

    class Chatter(object):
        """This class includes methods associated with Salesforce Chatter."""
        def __init__(self, sfdc_object):
            """This method initializes the :py:class:`salespyforce.core.Salesforce.Chatter` inner class object.

            :param sfdc_object: The core :py:class:`salespyforce.Salesforce` object
            :type sfdc_object: class[salespyforce.Salesforce]
            """
            self.sfdc_object = sfdc_object

        def get_my_news_feed(self, site_id=None):
            """This method retrieves the news feed for the user calling the function.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_news_feed.htm>`_)

            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :returns: The news feed data
            :raises: :py:exc:`RuntimeError`
            """
            return chatter_module.get_my_news_feed(self.sfdc_object, site_id=site_id)

        def get_user_news_feed(self, user_id, site_id=None):
            """This method retrieves another user's news feed.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_user_profile_feed.htm>`_)

            :param user_id: The ID of the user whose feed you wish to return
            :type user_id: str
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :returns: The news feed data
            :raises: :py:exc:`RuntimeError`
            """
            return chatter_module.get_user_news_feed(self.sfdc_object, user_id=user_id, site_id=site_id)

        def get_group_feed(self, group_id, site_id=None):
            """This method retrieves a group's news feed.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_group_feed.htm>`_)

            :param group_id: The ID of the group whose feed you wish to return
            :type group_id: str
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :returns: The news feed data
            :raises: :py:exc:`RuntimeError`
            """
            return chatter_module.get_group_feed(self.sfdc_object, group_id=group_id, site_id=site_id)

        def post_feed_item(self, subject_id, message_text=None, message_segments=None, site_id=None, created_by_id=None):
            """This method publishes a new Chatter feed item.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_feed_item.htm>`_)

            :param subject_id: The Subject ID against which to publish the feed item (e.g. ``0F9B000000000W2``)
            :type subject_id: str
            :param message_text: Plaintext to be used as the message body
            :type message_segments: str, None
            :param message_segments: Collection of message segments to use instead of a plaintext message
            :type message_segments: list, None
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :param created_by_id: The ID of the user to impersonate (**Experimental**)
            :type created_by_id: str, None
            :returns: The response of the POST request
            :raises: :py:exc:`RuntimeError`
            """
            return chatter_module.post_feed_item(self.sfdc_object, subject_id=subject_id, message_text=message_text,
                                                 message_segments=message_segments, site_id=site_id,
                                                 created_by_id=created_by_id)

        def post_comment(self, feed_element_id, message_text=None, message_segments=None, site_id=None, created_by_id=None):
            """This method publishes a comment on a Chatter feed item.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_comment_to_feed_element.htm>`_)

            :param feed_element_id: The ID of the feed element on which to post the comment
            :type feed_element_id: str
            :param message_text: Plaintext to be used as the message body
            :type message_segments: str, None
            :param message_segments: Collection of message segments to use instead of a plaintext message
            :type message_segments: list, None
            :param site_id: The ID of an Experience Cloud site against which to query (optional)
            :type site_id: str, None
            :param created_by_id: The ID of the user to impersonate (**Experimental**)
            :type created_by_id: str, None
            :returns: The response of the POST request
            :raises: :py:exc:`RuntimeError`
            """
            return chatter_module.post_comment(self.sfdc_object, feed_element_id=feed_element_id,
                                               message_text=message_text, message_segments=message_segments,
                                               site_id=site_id, created_by_id=created_by_id)

    class Knowledge(object):
        """This class includes methods associated with Salesforce Knowledge."""
        def __init__(self, sfdc_object):
            """This method initializes the :py:class:`salespyforce.core.Salesforce.Knowledge` inner class object.

            :param sfdc_object: The core :py:class:`salespyforce.Salesforce` object
            :type sfdc_object: class[salespyforce.Salesforce]
            """
            self.sfdc_object = sfdc_object

        def check_for_existing_article(self, title, sobject=None, return_id=False, return_id_and_number=False,
                                       include_archived=False):
            """This method checks to see if an article already exists with a given title and returns its article number.
            (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`_.
            `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`_)

            :param title: The title of the knowledge article for which to check
            :type title: str
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param return_id: Determines if the Article ID should be returned (``False`` by default)
            :type return_id: bool
            :param return_id_and_number: Determines if Article ID and Article Number should be returned (``False`` by default)
            :type return_id_and_number: bool
            :param include_archived: Determines if archived articles should be included (``False`` by default)
            :type include_archived: bool
            :returns: The Article Number, Article ID, or both, if found, or a blank string if not found
            """
            return knowledge_module.check_for_existing_article(self.sfdc_object, title=title,
                                                               sobject=sobject, return_id=return_id,
                                                               return_id_and_number=return_id_and_number,
                                                               include_archived=include_archived)

        def get_article_id_from_number(self, article_number, sobject=None, return_uri=False):
            """This method returns the Article ID when an article number is provided.
            (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm>`_,
            `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm>`_)

            :param article_number: The Article Number to query
            :type article_number: str, int
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param return_uri: Determines if the URI of the article should be returned rather than the ID (``False`` by default)
            :type return_uri: bool
            :returns: The Article ID or Article URI, or a blank string if no article is found
            :raises: :py:exc:`ValueError`,
                     :py:exc:`RuntimeError`
            """
            return knowledge_module.get_article_id_from_number(self.sfdc_object, article_number=article_number,
                                                               sobject=sobject, return_uri=return_uri)

        def get_articles_list(self, query=None, sort=None, order=None, page_size=20, page_num=1):
            """This method retrieves a list of knowledge articles.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artlist.htm>`_)

            :param query: A SOQL query with which to filter the results (optional)
            :type query: str, None
            :param sort: One of the following optional values: ``LastPublishedDate``, ``CreatedDate``, ``Title``, or ``ViewScore``
            :type sort: str, None
            :param order: Optionally define the ORDER BY as ``ASC`` or ``DESC``
            :type order: str, None
            :param page_size: The number of results per page (``20`` by default)
            :type page_size: int
            :param page_num: The starting page number (``1`` by default)
            :type page_num: int
            :returns: The list of retrieved knowledge articles
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.get_articles_list(self.sfdc_object, query=query, sort=sort, order=order,
                                                      page_size=page_size, page_num=page_num)

        def get_article_details(self, article_id, sobject=None):
            """This method retrieves details for a single knowledge article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`_)

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :returns: The details for the knowledge article
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.get_article_details(self.sfdc_object, article_id=article_id, sobject=sobject)

        def get_validation_status(self, article_id=None, article_details=None, sobject=None):
            """This method retrieves the Validation Status for a given Article ID.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm>`_)

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str, None
            :param article_details: The dictionary of article details for the given article
            :type article_details: dict, None
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :returns: The validation status as a text string
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.get_validation_status(self.sfdc_object, article_id=article_id,
                                                          article_details=article_details, sobject=sobject)

        def get_article_metadata(self, article_id):
            """This method retrieves metadata for a specific knowledge article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_metadata.htm>`_)

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str
            :returns: The article metadata as a dictionary
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.get_article_metadata(self.sfdc_object, article_id=article_id)

        def get_article_version(self, article_id):
            """This method retrieves the version ID for a given master article ID.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_retrieve_article_version.htm>`_)

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str
            :returns: The version ID for the given master article ID
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.get_article_version(self.sfdc_object, article_id=article_id)

        def get_article_url(self, article_id=None, article_number=None, sobject=None):
            """This function constructs the URL to view a knowledge article in Lightning or Classic.

            :param article_id: The Article ID for which to retrieve details
            :type article_id: str, None
            :param article_number: The article number for which to retrieve details
            :type article_number: str, int, None
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :returns: The article URL as a string
            :raises: :py:exc:`ValueError`,
                     :py:exc:`RuntimeError`
            """
            return knowledge_module.get_article_url(self.sfdc_object, article_id=article_id,
                                                    article_number=article_number, sobject=sobject)

        def create_article(self, article_data, sobject=None, full_response=False):
            """This method creates a new knowledge article draft.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_create.htm>`_)

            :param article_data: The article data used to populate the article
            :type article_data: dict
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param full_response: Determines if the full API response should be returned instead of the article ID (``False`` by default)
            :type full_response: bool
            :returns: The API response or the ID of the article draft
            :raises: :py:exc:`ValueError`,
                     :py:exc:`TypeError`,
                     :py:exc:`RuntimeError`
            """
            return knowledge_module.create_article(self.sfdc_object, article_data=article_data, sobject=sobject,
                                                   full_response=full_response)

        def update_article(self, record_id, article_data, sobject=None, include_status_code=False):
            """This method updates an existing knowledge article draft.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_update_fields.htm>`_)

            :param record_id: The ID of the article draft record to be updated
            :type record_id: str
            :param article_data: The article data used to update the article
            :type article_data: dict
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param include_status_code: Determines if the API response status code should be returned (``False`` by default)
            :type include_status_code: bool
            :returns: A Boolean indicating if the update operation was successful, and optionally the API response status code
            :raises: :py:exc:`ValueError`,
                     :py:exc:`TypeError`,
                     :py:exc:`RuntimeError`
            """
            return knowledge_module.update_article(self.sfdc_object, record_id=record_id, article_data=article_data,
                                                   sobject=sobject, include_status_code=include_status_code)

        def create_draft_from_online_article(self, article_id, unpublish=False):
            """This method creates a draft knowledge article from an online article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/actions_obj_knowledge.htm#createDraftFromOnlineKnowledgeArticle>`_)

            :param article_id: The ID of the online article from which to create the draft
            :type article_id: str
            :param unpublish: Determines if the online article should be unpublished when the draft is created (``False`` by default)
            :type unpublish: bool
            :returns: The API response from the POST request
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.create_draft_from_online_article(self.sfdc_object, article_id=article_id,
                                                                     unpublish=unpublish)

        def create_draft_from_master_version(self, article_id=None, knowledge_article_id=None, article_data=None,
                                             sobject=None, full_response=False):
            """This method creates an online version of a master article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.198.0.knowledge_dev.meta/knowledge_dev/knowledge_REST_edit_online_master.htm>`_)

            :param article_id: The Article ID from which to create the draft
            :type article_id: str, None
            :param knowledge_article_id: The Knowledge Article ID (``KnowledgeArticleId``) from which to create the draft
            :type knowledge_article_id: str, None
            :param article_data: The article data associated with the article from which to create the draft
            :type article_data: dict, None
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param full_response: Determines if the full API response should be returned instead of the article ID (``False`` by default)
            :type full_response: bool
            :returns: The API response or the ID of the article draft
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.create_draft_from_master_version(self.sfdc_object, article_id=article_id,
                                                                     knowledge_article_id=knowledge_article_id,
                                                                     article_data=article_data, sobject=sobject,
                                                                     full_response=full_response)

        def publish_article(self, article_id, major_version=True, full_response=False):
            """This method publishes a draft knowledge article as a major or minor version.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_publish_master_version.htm>`_)

            :param article_id: The Article ID to publish
            :type article_id: str
            :param major_version: Determines if the published article should be a major version (``True`` by default)
            :type major_version: bool
            :param full_response: Determines if the full API response should be returned (``False`` by default)
            :type full_response: bool
            :returns: A Boolean value indicating the success of the action or the API response from the PATCH request
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.publish_article(self.sfdc_object, article_id=article_id,
                                                    major_version=major_version, full_response=full_response)

        def publish_multiple_articles(self, article_id_list, major_version=True):
            """This method publishes multiple knowledge article drafts at one time.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/actions_obj_knowledge.htm#publishKnowledgeArticles>`_)

            :param article_id_list: A list of Article IDs to be published
            :type article_id_list: list
            :param major_version: Determines if the published article should be a major version (``True`` by default)
            :type major_version: bool
            :returns: The API response from the POST request
            :raises: :py:exc:`RuntimeError`,
                     :py:exc:`TypeError`,
                     :py:exc:`ValueError`
            """
            return knowledge_module.publish_multiple_articles(self.sfdc_object, article_id_list=article_id_list,
                                                              major_version=major_version)

        def assign_data_category(self, article_id, category_group_name, category_name):
            """This method assigns a single data category for a knowledge article.
            (`Reference <https://itsmemohit.medium.com/quick-win-15-salesforce-knowledge-rest-apis-bb0725b2040e>`_)

            .. version-added:: 1.2.0

            :param article_id: The ID of the article to update
            :type article_id: str
            :param category_group_name: The unique Data Category Group Name
            :type category_group_name: str
            :param category_name: The unique Data Category Name
            :type category_name: str
            :returns: The API response from the POST request
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.assign_data_category(self.sfdc_object, article_id=article_id,
                                                         category_group_name=category_group_name,
                                                         category_name=category_name)

        def archive_article(self, article_id):
            """This function archives a published knowledge article.
            (`Reference <https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_REST_archive_master_version.htm>`_)

            .. version-added:: 1.3.0

            :param article_id: The ID of the article to archive
            :type article_id: str
            :returns: The API response from the POST request
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.archive_article(self.sfdc_object, article_id=article_id)

        def delete_article_draft(self, version_id):
            """This function deletes an unpublished knowledge article draft.

            .. version-added:: 1.4.0

            :param version_id: The 15-character or 18-character ``Id`` (Knowledge Article Version ID) value
            :type version_id: str
            :returns: The API response from the DELETE request
            :raises: :py:exc:`RuntimeError`
            """
            return knowledge_module.delete_article_draft(self.sfdc_object, version_id=version_id)


def define_connection_info():
    """This function prompts the user for the connection information.

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
    connection_info = compile_connection_info(base_url, org_id, username, password, endpoint_url,
                                              client_id, client_secret, security_token)
    return connection_info


def compile_connection_info(base_url, org_id, username, password, endpoint_url,
                            client_id, client_secret, security_token):
    """This function compiles the connection info into a dictionary that can be consumed by the core object.

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
