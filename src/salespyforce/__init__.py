# -*- coding: utf-8 -*-
"""
:Module:            salespyforce
:Synopsis:          This is the ``__init__`` module for the salespyforce package
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-6.1 Sol)
:Modified Date:     05 Nov 2026
"""

from __future__ import annotations

from . import core
from .core import Salesforce
from .utils import version

__all__ = ['core', 'Salesforce']

# Define the package version by pulling from the highspot.utils.version module
__version__ = version.get_full_version()


# Allow the core.define_connection_info() function to be executed directly
def define_connection_info() -> dict:
    """Prompts the user for the connection information.

    :returns: The connection info in a dictionary
    :rtype: dict
    """
    return core.define_connection_info()


# Allow the core.compile_connection_info() function to be executed directly
def compile_connection_info(
    base_url: str | None,
    org_id: str | None,
    username: str | None,
    password: str | None,
    endpoint_url: str | None,
    client_id: str | None,
    client_secret: str | None,
    security_token: str | None,
) -> dict[str, str]:
    """Compiles the connection info into a dictionary that can be consumed by the core object.

    .. versionchanged:: 2.0.2
       The function parameters now accept strings and None values and the latter get converted to empty strings.

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
    :returns: The connection info in a dictionary
    :rtype: dict
    """
    return core.compile_connection_info(
        base_url=base_url,
        org_id=org_id,
        username=username,
        password=password,
        endpoint_url=endpoint_url,
        client_id=client_id,
        client_secret=client_secret,
        security_token=security_token,
    )
