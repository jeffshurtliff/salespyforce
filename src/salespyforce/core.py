# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.core
:Synopsis:          This module performs the core Salesforce-related operations
:Usage:             ``from salespyforce import Salesforce``
:Example:           ``sfdc = Salesforce()``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     09 Feb 2023
"""

import requests

from . import api
from . import knowledge as knowledge_module
from .utils import core_utils, log_utils

# Define constants
CURRENT_SFDC_VERSION = '55.0'

# Initialize logging
logger = log_utils.initialize_logging(__name__)


class Salesforce(object):
    """This is the class for the core object leveraged in this module."""
    # Define the function that initializes the object instance (i.e. instantiates the object)
    def __init__(self, connection_info=None, version=CURRENT_SFDC_VERSION, base_url=None, org_id=None, username=None,
                 password=None, endpoint_url=None, client_id=None, client_secret=None, security_token=None):
        """This method instantiates the core Salesforce object.

        :param connection_info: The information for connecting to the Salesforce instance
        :type connection_info: dict, None
        :param version: The Salesforce API version to utilize (Default: ``55.0``)
        :type version: str
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
        """
        # Check for provided connection info
        if connection_info is None:
            if not any((base_url, org_id, username, password, endpoint_url, client_id, client_secret, security_token)):
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

        # Define the version value
        self.version = f'v{version}'

        # Define the connection response data variables
        auth_response = self.connect()
        self.access_token = auth_response.get('access_token')
        self.instance_url = auth_response.get('instance_url')
        self.signature = auth_response.get('signature')

        # Import inner object classes so their methods can be called from the primary object
        self.knowledge = self._import_knowledge_class()

    def _import_knowledge_class(self):
        """This method allows the :py:class:`highspot.core.Highspot.Domain` class to be utilized in the core object."""
        return Salesforce.Knowledge(self)

    @staticmethod
    def _get_empty_connection_info():
        """This function returns an empty connection_info dictionary with all blank values."""
        _connection_info = {}
        _fields = ['username', 'password', 'base_url', 'endpoint_url',
                   'client_key', 'client_secret', 'org_id', 'security_token']
        for _field in _fields:
            _connection_info[_field] = ''
        return _connection_info

    def _get_headers(self, header_type='default'):
        """This method returns the appropriate HTTP headers to use for different types of API calls."""
        headers = {
            'content-type': 'application/json',
            'accept-encoding': 'gzip',
            'authorization': f'Bearer {self.access_token}'
        }
        if header_type == 'articles':
            headers['accept-language'] = 'en-US'
        return headers

    def connect(self):
        """This method connects to the Salesforce instance to obtain the access token.
        Reference: `https://jereze.com/code/authentification-salesforce-rest-api-python/`_

        :returns: The API call response with the authorization information
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
        Reference: `https://jereze.com/code/authentification-salesforce-rest-api-python/`_

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
        return api.get(self, endpoint, params, headers, timeout, show_full_error, return_json)

    def api_call_with_payload(self, method, endpoint, payload, params=None, headers=None, timeout=30,
                              show_full_error=True, return_json=True):
        """This method performs a POST call against the Salesforce instance.
        Reference: `https://jereze.com/code/authentification-salesforce-rest-api-python/`_

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
        return api.api_call_with_payload(self, method, endpoint, payload, params, headers, timeout, show_full_error,
                                         return_json)

    def post(self, endpoint, payload, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
        """This method performs a POST call against the Salesforce instance.
        Reference: `https://jereze.com/code/authentification-salesforce-rest-api-python/`_

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
        return api.api_call_with_payload(self, 'post', endpoint, payload, params=params, headers=headers,
                                         timeout=timeout, show_full_error=show_full_error, return_json=return_json)

    def patch(self, endpoint, payload, params=None, headers=None, timeout=30, show_full_error=True, return_json=False):
        """This method performs a PATCH call against the Salesforce instance.
        Reference: `https://jereze.com/code/authentification-salesforce-rest-api-python/`_

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
        return api.api_call_with_payload(self, 'patch', endpoint, payload, params=params, headers=headers,
                                         timeout=timeout, show_full_error=show_full_error, return_json=return_json)

    def put(self, endpoint, payload, params=None, headers=None, timeout=30, show_full_error=True, return_json=True):
        """This method performs a PUT call against the Salesforce instance.
        Reference: `https://jereze.com/code/authentification-salesforce-rest-api-python/`_

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
        return api.api_call_with_payload(self, 'put', endpoint, payload, params=params, headers=headers,
                                         timeout=timeout, show_full_error=show_full_error, return_json=return_json)

    def get_api_versions(self):
        """This method returns the API versions for the Salesforce releases.
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_versions.htm`_
        """
        return self.get('/services/data')

    def get_all_sobjects(self):
        """This method returns a list of all Salesforce objects. (i.e. sObjects)
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_describeGlobal.htm`_
        """
        return self.get(f'/services/data/{self.version}/sobjects')

    def get_sobject(self, object_name, describe=False):
        """This method returns basic information or the full (describe) information for a specific sObject.
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_basic_info_get.htm`_
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm`_

        :param object_name: The name of the Salesforce object
        :type object_name: str
        :param describe: Determines if the full (i.e. ``describe``) data should be returned (defaults to ``False``)
        :type describe: bool
        :returns: The Salesforce object data
        """
        uri = f'/services/data/{self.version}/sobjects/{object_name}'
        uri = f'{uri}/describe' if describe else uri
        return self.get(uri)

    def describe_object(self, object_name):
        """This method returns the full (describe) information for a specific sObject.
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm`_

        :param object_name: The name of the Salesforce object
        :type object_name: str
        :returns: The Salesforce object data
        """
        return self.get_sobject(object_name, describe=True)

    def get_rest_resources(self):
        """This method returns a list of all available REST resources.
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_discoveryresource.htm`_
        """
        return self.get(f'/services/data/{self.version}')

    def soql_query(self, query, replace_quotes=True):
        """This method performs a SOQL query and returns the results in JSON format.
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm`_
        Reference: `https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm`_

        :param query: The SOQL query to perform
        :type query: str
        :param replace_quotes: Determines if double-quotes should be replaced with single-quotes (``True`` by default)
        :type replace_quotes: bool
        :returns: The result of the SOQL query
        """
        if replace_quotes:
            query = query.replace('"', "'")
        query = core_utils.url_encode(query)
        return self.get(f'/services/data/{self.version}/query/?q={query}')

    class Knowledge(object):
        """This class includes methods associated with Highspot domains."""
        def __init__(self, sfdc_object):
            """This method initializes the :py:class:`salespyforce.core.Salesforce.Knowledge` inner class object.

            :param sfdc_object: The core :py:class:`salespyforce.Salesforce` object
            :type sfdc_object: class[salespyforce.Salesforce]
            """
            self.sfdc_object = sfdc_object

        def check_for_existing_article(self, title, sobject=None, return_id=False, return_id_and_number=False):
            """This method checks to see if an article already exists with a given title and returns its article number.
            Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm`_
            Reference: `https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm`_

            :param title: The title of the knowledge article for which to check
            :type title: str
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param return_id: Determines if the Article ID should be returned (``False`` by default)
            :type return_id: bool
            :param return_id_and_number: Determines if Article ID and Article Number should be returned (``False`` by default)
            :type return_id_and_number: bool
            :returns: The Article Number, Article ID, or both, if found, or a blank string if not found
            """
            return knowledge_module.check_for_existing_article(self.sfdc_object, title, sobject, return_id,
                                                               return_id_and_number)

        def get_article_id_from_number(self, article_number, sobject=None, return_uri=False):
            """This method returns the Article ID when an article number is provided.
            Reference: `https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_query.htm`_
            Reference: `https://developer.salesforce.com/docs/atlas.en-us.knowledge_dev.meta/knowledge_dev/knowledge_development_soql_sosl_intro.htm`_

            :param article_number: The Article Number to query
            :type article_number: str, int
            :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
            :type sobject: str, None
            :param return_uri: Determines if the URI of the article should be returned rather than the ID (``False`` by default)
            :type return_uri: bool
            :returns: The Article ID or Article URI, or a blank string if no article is found
            :raises: :py:exc:`ValueError`
            """
            return knowledge_module.get_article_id_from_number(self.sfdc_object, article_number, sobject, return_uri)

    def get_articles_list(self, query=None, sort=None, order=None, page_size=20, page_num=1):
        """This method retrieves a list of knowledge articles.
        Reference: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artlist.htm

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
        """
        # Define the headers
        headers = self._get_headers('articles')

        # Validate the sort field
        valid_sort_options = ['LastPublishedDate', 'CreatedDate', 'Title', 'ViewScore']
        if sort and sort not in valid_sort_options:
            # TODO: Use an eprint function
            print(f'The sort value {sort} is not valid and will be ignored.')
            sort = None

        # Validate the order field
        if order and order.upper() not in ['ASC', 'DESC']:
            # TODO: Use an eprint function
            print(f'The order value {order} is not valid and will be ignored.')
            order = None

        # Validate the page size field
        if page_size > 100:
            # TODO: Use an eprint function
            print(f'The pageSize value exceeds the maximum and will default to 100.')
            page_size = 100

        # Validate the pageNumber field
        if page_num < 1:
            # TODO: Use an eprint function
            print(f'The pageNumber value is not valid and will default to 1.')
            page_num = 1

        # Add values to the parameters dictionary if they have been defined
        params = {}
        if query:
            params['q'] = query
        if sort:
            params['sort'] = sort
        if order:
            params['order'] = order
        params['pageSize'] = page_size
        params['pageNumber'] = page_num

        # Perform the query
        return self.get(f'/services/data/{self.version}/support/knowledgeArticles', params=params, headers=headers)

    def get_article_details(self, article_id, sobject=None):
        """This method retrieves details for a single knowledge article.
        Reference: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_knowledge_support_artdetails.htm

        :param article_id: The Article ID for which to retrieve details
        :type article_id: str
        :param sobject: The Salesforce object to query (``Knowledge__kav`` by default)
        :type sobject: str, None
        :returns: The details for the knowledge article
        """
        # Define the headers
        headers = self._get_headers('articles')

        # Perform the query and return the data
        sobject = 'Knowledge__kav' if sobject is None else sobject
        if sobject is not None:
            data = self.get(f'/services/data/{self.version}/sobjects/{sobject}/{article_id}')
        else:
            data = self.get(f'/services/data/{self.version}/support/knowledgeArticles/{article_id}', headers=headers)
        return data


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
