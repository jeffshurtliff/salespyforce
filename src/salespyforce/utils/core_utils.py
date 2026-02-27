# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.utils.core_utils
:Synopsis:          Collection of supporting utilities and functions to complement the primary modules
:Usage:             ``from salespyforce.utils import core_utils``
:Example:           ``encoded_string = core_utils.encode_url(decoded_string)``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     27 Feb 2026
"""

from __future__ import annotations

import re
import random
import string
import os.path
import warnings
import urllib.parse
from typing import Optional

import requests

from . import log_utils
from .. import errors
from .. import constants as const
from ..decorators import deprecated

# Initialize the logger for this module
logger = log_utils.initialize_logging(__name__)


def url_encode(raw_string: str) -> str:
    """This function encodes a string for use in URLs.

    :param raw_string: The raw string to be encoded
    :type raw_string: str
    :returns: The encoded string
    """
    return urllib.parse.quote_plus(raw_string)


def url_decode(encoded_string: str) -> str:
    """This function decodes a url-encoded string.

    :param encoded_string: The url-encoded string
    :type encoded_string: str
    :returns: The unencoded string
    """
    return urllib.parse.unquote_plus(encoded_string)


@deprecated(since='1.4.0', replacement='salespyforce.errors.handlers.display_warning', removal='2.0.0')
def display_warning(warn_msg: str) -> None:
    """This function displays a :py:exc:`UserWarning` message via the :py:mod:`warnings` module.

    .. deprecated:: 1.4.0
       Use :py:func:`salespyforce.errors.handlers.display_warning` instead.

    :param warn_msg: The message to be displayed
    :type warn_msg: str
    :returns: None
    """
    warnings.warn(warn_msg, UserWarning)


def get_file_type(file_path: str) -> str:
    """This function attempts to identify if a given file path is for a YAML or JSON file.

    :param file_path: The full path to the file
    :type file_path: str
    :returns: The file type in string format (e.g. ``yaml`` or ``json``)
    :raises: :py:exc:`FileNotFoundError`,
             :py:exc:`salespyforce.errors.exceptions.UnknownFileTypeError`
    """
    file_type = 'unknown'
    if os.path.isfile(file_path):
        if file_path.endswith(const.FILE_EXTENSIONS.DOT_JSON):
            file_type = const.FILE_EXTENSIONS.JSON
        elif file_path.endswith(const.FILE_EXTENSIONS.DOT_YML) or file_path.endswith(const.FILE_EXTENSIONS.DOT_YAML):
            file_type = const.FILE_EXTENSIONS.YAML
        else:
            display_warning(f"Unable to recognize the file type of '{file_path}' by its extension.")
            with open(file_path) as cfg_file:
                for line in cfg_file:
                    if line.startswith('#'):
                        continue
                    else:
                        if '{' in line:
                            file_type = const.FILE_EXTENSIONS.JSON
                            break
        if file_type == 'unknown':
            raise errors.exceptions.UnknownFileTypeError(file=file_path)
    else:
        raise FileNotFoundError(f'Unable to locate the following file: {file_path}')
    return file_type


def get_random_string(length: int = 32, prefix_string: str = '') -> str:
    """This function returns a random alphanumeric string.

    :param length: The length of the string (``32`` by default)
    :type length: int
    :param prefix_string: A string to which the random string should be appended (optional)
    :type prefix_string: str
    :returns: The alphanumeric string
    """
    return f"{prefix_string}{''.join([random.choice(string.ascii_letters + string.digits) for _ in range(length)])}"


def get_18_char_id(record_id: str) -> str:
    """This function converts a 15-character Salesforce record ID to its 18-character case-insensitive form.

    .. versionadded:: 1.4.0

    :param record_id: The Salesforce record ID to convert (or return unchanged if already 18 characters)
    :type record_id: str
    :returns: The 18-character Salesforce record ID
    :raises: :py:exc:`ValueError`
    """
    # Ensure the provided record ID is a string
    if not isinstance(record_id, str):
        raise ValueError('Salesforce ID must be a string')

    # Return the record ID unchanged if it is already 18 characters in length
    if len(record_id) == 18:
        return record_id

    # Ensure the record ID is a valid 15-character value
    if len(record_id) != 15:
        raise ValueError('Salesforce ID must be 15 or 18 characters long')

    # Define the checksum suffix (additional 3 characters)
    suffix = ''
    for i in range(0, 15, 5):
        chunk = record_id[i:i + 5]
        bitmask = 0

        for index, char in enumerate(chunk):
            if 'A' <= char <= 'Z':
                bitmask |= 1 << index

        suffix += const.SALESFORCE_ID_SUFFIX_ALPHABET[bitmask]

    # Return the 18-character ID value
    return record_id + suffix


def matches_regex_pattern(pattern: str, text: str, full_match: bool = False, must_start_with: bool = False) -> bool:
    """This function compares a text string against a regex pattern and determines whether they match.

    .. versionadded:: 1.4.0

    :param pattern: The regex pattern that should match
    :type pattern: str
    :param text: The text string to evaluate
    :type text: str
    :param full_match: Determines if the entire string should be validated
    :type full_match: bool
    :param must_start_with: Determines if the pattern must be at the beginning of the string
    :returns: True if the regex pattern matches anywhere in the text string
    :raises: :py:exc:`TypeError`
    """
    if full_match:
        return bool(re.fullmatch(pattern, text))
    elif must_start_with:
        return bool(re.match(pattern, text))
    else:
        return bool(re.search(pattern, text))


def is_valid_salesforce_url(url: str) -> bool:
    """This function evaluates a URL to determine if it is a valid Salesforce URL.

    .. versionadded:: 1.4.0

    :param url: The URL to evaluate
    :type url: str
    :returns: Boolean value depending on whether the URL meets the criteria
    """
    return True if isinstance(url, str) and matches_regex_pattern(const.VALID_SALESFORCE_URL_PATTERN, url) else False


def get_image_ref_id(image_url: str) -> str:
    """This function parses an image URL to identify the reference ID (refid) value.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_rich_text_image_retrieve.htm>`__,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_rich_text_image_retrieve.htm>`__)

    :param image_url: The URL of an image from within Salesforce
    :type image_url: str
    :returns: The reference ID (``refid``) value
    """
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(image_url).query)
    # noinspection PyTypeChecker
    ref_id = query_params.get(const.QUERY_PARAMS.REF_ID)
    ref_id = ref_id[0] if not isinstance(ref_id, str) else ref_id
    return ref_id


def download_image(image_url: Optional[str] = None, file_name: Optional[str] = None, file_path: Optional[str] = None,
                   response=None, extension: str = const.FILE_EXTENSIONS.JPEG) -> str:
    """This function downloads an image and saves it to a specified directory.

    .. versionchanged:: 1.5.0
       This function now raises more specific exceptions instead of the generic :py:exc:`RuntimeError` exception.

    :param image_url: The absolute URL to the image
    :type image_url: str, None
    :param file_name: The file name (including extension) to use as the file name (Default: randomly generated)
    :type file_name: str, None
    :param file_path: File path where the image file should be saved (Default: ``./``)
    :type file_path: str, None
    :param response: The response of the previously performed API call
    :param extension: The file extension to use if a file name with extension is not provided (Default: ``jpeg``)
    :type extension: str
    :returns: The full path to the downloaded image
    :raises: :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError`,
             :py:exc:`salespyforce.errors.exceptions.GETRequestError`
    """
    if not image_url and not response:
        exc_msg = 'An image URL or an API response must be provided to download an image.'
        raise errors.exceptions.MissingRequiredDataError(exc_msg)

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
        exc_msg = f'The image failed to download with a {response.status_code} status code.'
        raise errors.exceptions.GETRequestError(exc_msg)

    # Export the response data as an image file
    with open(f'{file_path}{file_name}', 'wb') as file:
        file.write(response.content)
    return f'{file_path}{file_name}'
