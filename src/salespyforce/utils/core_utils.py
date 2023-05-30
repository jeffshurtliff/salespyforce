# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.utils.core_utils
:Synopsis:          Collection of supporting utilities and functions to complement the primary modules
:Usage:             ``from salespyforce.utils import core_utils``
:Example:           ``encoded_string = core_utils.encode_url(decoded_string)``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     29 May 2023
"""

import random
import string
import os.path
import warnings
import urllib.parse

import requests

from . import log_utils
from .. import errors

# Initialize the logger for this module
logger = log_utils.initialize_logging(__name__)


def url_encode(raw_string):
    """This function encodes a string for use in URLs.

    :param raw_string: The raw string to be encoded
    :type raw_string: str
    :returns: The encoded string
    """
    return urllib.parse.quote_plus(raw_string)


def url_decode(encoded_string):
    """This function decodes a url-encoded string.

    :param encoded_string: The url-encoded string
    :type encoded_string: str
    :returns: The unencoded string
    """
    return urllib.parse.unquote_plus(encoded_string)


def display_warning(warn_msg):
    """This function displays a :py:exc:`UserWarning` message via the :py:mod:`warnings` module.

    :param warn_msg: The message to be displayed
    :type warn_msg: str
    :returns: None
    """
    warnings.warn(warn_msg, UserWarning)


def get_file_type(file_path):
    """This function attempts to identify if a given file path is for a YAML or JSON file.

    :param file_path: The full path to the file
    :type file_path: str
    :returns: The file type in string format (e.g. ``yaml`` or ``json``)
    :raises: :py:exc:`FileNotFoundError`, :py:exc:`khoros.errors.exceptions.UnknownFileTypeError`
    """
    file_type = 'unknown'
    if os.path.isfile(file_path):
        if file_path.endswith('.json'):
            file_type = 'json'
        elif file_path.endswith('.yml') or file_path.endswith('.yaml'):
            file_type = 'yaml'
        else:
            display_warning(f"Unable to recognize the file type of '{file_path}' by its extension.")
            with open(file_path) as cfg_file:
                for line in cfg_file:
                    if line.startswith('#'):
                        continue
                    else:
                        if '{' in line:
                            file_type = 'json'
                            break
        if file_type == 'unknown':
            raise errors.exceptions.UnknownFileTypeError(file=file_path)
    else:
        raise FileNotFoundError(f"Unable to locate the following file: {file_path}")
    return file_type


def get_random_string(length=32, prefix_string=""):
    """This function returns a random alphanumeric string.

    :param length: The length of the string (``32`` by default)
    :type length: int
    :param prefix_string: A string to which the random string should be appended (optional)
    :type prefix_string: str
    :returns: The alphanumeric string
    """
    return f"{prefix_string}{''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])}"


def get_image_ref_id(image_url):
    """This function parses an image URL to identify the reference ID (refid) value.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_rich_text_image_retrieve.htm>`_,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_rich_text_image_retrieve.htm>`_)

    :param image_url: The URL of an image from within Salesforce
    :type image_url: str
    :returns: The reference ID (``refid``) value
    """
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(image_url).query)
    # noinspection PyTypeChecker
    ref_id = query_params.get('refid')
    ref_id = ref_id[0] if not isinstance(ref_id, str) else ref_id
    return ref_id


def download_image(image_url=None, file_name=None, file_path=None, response=None, extension='jpeg'):
    """This function downloads an image and saves it to a specified directory.

    :param image_url: The absolute URL to the image
    :type image_url: str
    :param file_name: The file name including extension as which to save the file
    :type file_name: str
    :param file_path: File path where the image file should be saved (default: ``var/images/``)
    :type file_path: str, None
    :param response: The response of the previously performed API call
    :param extension: The file extension to use if a file name with extension is not provided
    :type extension: str
    :returns: The full path to the downloaded image
    :raises: :py:exc:`RuntimeError`
    """
    if not image_url and not response:
        raise RuntimeError('An image URL or an API response must be provided to download an image.')

    # Define an appropriate file path
    file_path = './' if not file_path else file_path
    file_path = f'{file_path}/' if not any((file_path.endswith('/'), file_path.endswith('\\'))) else file_path

    # Define a file name if not provided
    if not file_name:
        file_name = get_random_string(10, 'image_')
        file_name += extension

    # Perform the API call if not supplied
    if not response:
        response = requests.get(image_url)
    if response.status_code != 200:
        raise RuntimeError(f'The image failed to download with a {response.status_code} status code.')

    # Export the response data as an image file
    with open(f'{file_path}{file_name}', 'wb') as file:
        file.write(response.content)
    return f'{file_path}{file_name}'
