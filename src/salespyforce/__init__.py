# -*- coding: utf-8 -*-
"""
:Module:            salespyforce
:Synopsis:          This is the ``__init__`` module for the salespyforce package
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     08 May 2023
"""

from . import core
from .core import Salesforce
from .utils import version

__all__ = ['core', 'Salesforce']

# Define the package version by pulling from the highspot.utils.version module
__version__ = version.get_full_version()


# Allow the core.define_connection_info() function to be executed directly
def define_connection_info():
    """This function prompts the user for the connection information.

    :returns: The connection info in a dictionary
    """
    return core.define_connection_info()


# Allow the core.compile_connection_info() function to be executed directly
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
    return core.compile_connection_info(base_url, org_id, username, password, endpoint_url,
                                        client_id, client_secret, security_token)
