# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.core
:Synopsis:          This module performs the core Salesforce-related operations
:Usage:             ``from salespyforce import Salesforce``
:Example:           ``sfdc = Salesforce()``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     22 Jan 2023
"""

import requests


# Define constants
CURRENT_SFDC_VERSION = '55.0'


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

    @staticmethod
    def _get_empty_connection_info():
        """This function returns an empty connection_info dictionary with all blank values."""
        _connection_info = {}
        _fields = ['username', 'password', 'base_url', 'endpoint_url',
                   'client_key', 'client_secret', 'org_id', 'security_token']
        for _field in _fields:
            _connection_info[_field] = ''
        return _connection_info

    def connect(self):
        """This method connects to the Salesforce instance to obtain the access token.
        Reference: https://jereze.com/code/authentification-salesforce-rest-api-python/
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
