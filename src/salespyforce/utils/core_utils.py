# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.utils.core_utils
:Synopsis:          Collection of supporting utilities and functions to complement the primary modules
:Usage:             ``from salespyforce.utils import core_utils``
:Example:           ``encoded_string = core_utils.encode_url(decoded_string)``
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     27 Sep 2026
"""

from __future__ import annotations

import logging
import os.path
import re
import secrets
import string
import urllib.parse

import requests

from .. import constants as const
from .. import errors

logger = logging.getLogger(__name__)


def url_encode(raw_string: str) -> str:
    """Encodes a string for use in URLs.

    :param raw_string: The raw string to be encoded
    :type raw_string: str
    :returns: The encoded string
    :rtype: str
    """
    return urllib.parse.quote_plus(raw_string)


def url_decode(encoded_string: str) -> str:
    """Decodes a url-encoded string.

    :param encoded_string: The url-encoded string
    :type encoded_string: str
    :returns: The unencoded string
    :rtype: str
    """
    return urllib.parse.unquote_plus(encoded_string)


def _ensure_prefix_or_suffix(
        _eval_string: str,
        _substring: str,
        _starts_with: bool | None = None,
        _ends_with: bool | None = None,
) -> str:
    """Ensures that a prefix or suffix is found before or after a given string.

    .. versionadded:: 1.5.0

    :param _eval_string: The string to evaluate
    :type _eval_string: str
    :param _substring: The substring that should be the prefix or suffix
    :type _substring: str
    :param _starts_with: Indicates that the evaluated string should start with the substring (i.e. prefix)
    :type _starts_with: bool, optional
    :param _ends_with: Indicates that the evaluated string should end with the substring (i.e. suffix)
    :type _ends_with: bool, optional
    :returns: The string with the prefix or suffix
    :rtype: str
    :raises salespyforce.errors.exceptions.MissingRequiredDataError: If neither a prefix nor a suffix was indicated
    """
    if not any((_starts_with, _ends_with)):
        _error_msg = const._LOG_MESSAGES._MUST_BE_PROVIDED_ERROR.format(data='_starts_with or _ends_with parameter')
        logger.error(_error_msg)
        raise errors.exceptions.MissingRequiredDataError(_error_msg)
    if _starts_with and not _eval_string.startswith(_substring):
        _eval_string = _substring + _eval_string
    elif _ends_with and not _eval_string.endswith(_substring):
        _eval_string = _eval_string + _substring
    return _eval_string


def ensure_starts_with(eval_string: str, prefix: str) -> str:
    """Ensures that a string starts with a given prefix.

    .. versionadded:: 1.5.0

    :param eval_string: The string to be evaluated
    :type eval_string: str
    :param prefix: The prefix string that must be at the beginning of the evaluated string
    :type prefix: str
    :returns: The string with the prefix at the start
    :rtype: str
    """
    return _ensure_prefix_or_suffix(
        _eval_string=eval_string,
        _substring=prefix,
        _starts_with=True,
    )


def ensure_ends_with(eval_string: str, suffix: str) -> str:
    """Ensures that a string ends with a given suffix.

    .. versionadded:: 1.5.0

    :param eval_string: The string to be evaluated
    :type eval_string: str
    :param suffix: The suffix string that must be at the end of the evaluated string
    :type suffix: str
    :returns: The string with the suffix at the end
    :rtype: str
    """
    return _ensure_prefix_or_suffix(
        _eval_string=eval_string,
        _substring=suffix,
        _ends_with=True,
    )


def get_file_type(file_path: str) -> str:
    """Attempts to identify if a given file path is for a YAML or JSON file.

    :param file_path: The full path to the file
    :type file_path: str
    :returns: The file type in string format (e.g. ``yaml`` or ``json``)
    :rtype: str
    :raises FileNotFoundError: If the file in the provided path does not exist
    :raises salespyforce.errors.exceptions.UnknownFileTypeError: If the file type could not be determined
    """
    file_type = 'unknown'
    if os.path.isfile(file_path):
        if file_path.endswith(const.FILE_EXTENSIONS.DOT_JSON):
            file_type = const.FILE_EXTENSIONS.JSON
        elif file_path.endswith(const.FILE_EXTENSIONS.DOT_YML) or file_path.endswith(const.FILE_EXTENSIONS.DOT_YAML):
            file_type = const.FILE_EXTENSIONS.YAML
        else:
            errors.handlers.display_warning(f"Unable to recognize the file type of '{file_path}' by its extension.")
            with open(file_path) as cfg_file:
                for line in cfg_file:
                    if line.startswith('#'):
                        continue
                    else:
                        if '{' in line:
                            file_type = const.FILE_EXTENSIONS.JSON
                            break
        if file_type == 'unknown':
            exc_msg = const._LOG_MESSAGES._UNKNOWN_FILE_TYPE
            logger.error(exc_msg.replace('the given file path', file_path))
            raise errors.exceptions.UnknownFileTypeError(file=file_path)
    else:
        exc_msg = f'Unable to locate the following file: {file_path}'
        logger.error(exc_msg)
        raise FileNotFoundError(exc_msg)
    return file_type


def get_random_string(length: int = 32, prefix_string: str = '') -> str:
    """Returns a random alphanumeric string.

    .. versionchanged:: 2.1.0
       The function now uses the cryptographically secure ``secrets`` module rather than the ``random`` module,
       and also now validates that the length is at least one character.

    :param length: The length of the string (``32`` by default)
    :type length: int
    :param prefix_string: A string to which the random string should be appended
    :type prefix_string: str, optional
    :returns: The alphanumeric string
    :rtype: str
    :raises ValueError: If the specified length is not at least one character
    """
    if length < 1:
        exc_msg = 'String length must be at least one character'
        logger.error(exc_msg)
        raise ValueError(exc_msg)

    characters = string.ascii_letters + string.digits
    return prefix_string + ''.join(secrets.choice(characters) for _ in range(length))


def get_18_char_id(record_id: str) -> str:
    """Converts a 15-character Salesforce record ID to its 18-character case-insensitive form.

    .. versionadded:: 1.4.0

    .. versionchanged:: 2.1.0
       A :py:exc:`TypeError` is now raised instead of :py:exc:`ValueError` if the record ID is not a string.

    :param record_id: The Salesforce record ID to convert (or return unchanged if already 18 characters)
    :type record_id: str
    :returns: The 18-character Salesforce record ID as a string
    :rtype: str
    :raises TypeError: If the Salesforce record ID provided is not a string
    :raises ValueError: If the Salesforce record ID provided is not 15 or 18 characters in length
    """
    # Ensure the provided record ID is a string
    if not isinstance(record_id, str):
        exc_msg = f'Salesforce record ID must be a string (Provided: {type(record_id).__name__})'
        logger.error(exc_msg)
        raise TypeError(exc_msg)

    # Return the record ID unchanged if it is already 18 characters in length
    if len(record_id) == 18:
        return record_id

    # Ensure the record ID is a valid 15-character value
    if len(record_id) != 15:
        exc_msg = f'Salesforce record ID must be 15 or 18 characters in length (Length: {len(record_id)})'
        logger.error(exc_msg)
        raise ValueError(exc_msg)

    # Define the checksum suffix (additional 3 characters)
    suffix = ''
    for i in range(0, 15, 5):
        chunk = record_id[i: i + 5]
        bitmask = 0

        for index, char in enumerate(chunk):
            if 'A' <= char <= 'Z':
                bitmask |= 1 << index

        suffix += const.SALESFORCE_ID_SUFFIX_ALPHABET[bitmask]

    # Return the 18-character ID value
    return record_id + suffix


def matches_regex_pattern(
        pattern: str,
        text: str,
        full_match: bool = False,
        must_start_with: bool = False
) -> bool:
    """Compares a text string against a regex pattern and determines whether they match.

    .. versionadded:: 1.4.0

    :param pattern: The regex pattern that should match
    :type pattern: str
    :param text: The text string to evaluate
    :type text: str
    :param full_match: Determines if the entire string should be validated (``False`` by default)
    :type full_match: bool
    :param must_start_with: Determines if the pattern must be at the beginning of the string (``False`` by default)
    :type must_start_with: bool
    :returns: True if the regex pattern matches anywhere in the text string
    :rtype: bool
    """
    if full_match:
        return bool(re.fullmatch(pattern, text))
    elif must_start_with:
        return bool(re.match(pattern, text))
    else:
        return bool(re.search(pattern, text))


def is_valid_salesforce_url(url: str) -> bool:
    """Evaluates a URL to determine if it is a valid Salesforce URL.

    .. versionadded:: 1.4.0

    :param url: The URL to evaluate
    :type url: str
    :returns: Boolean value depending on whether the URL meets the criteria
    :rtype: bool
    """
    return True if isinstance(url, str) and matches_regex_pattern(const.VALID_SALESFORCE_URL_PATTERN, url) else False


def get_image_ref_id(image_url: str) -> str:
    """Parses an image URL to identify the reference ID (``refid``) value.
    (`Reference 1 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_rich_text_image_retrieve.htm>`__,
    `Reference 2 <https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_sobject_rich_text_image_retrieve.htm>`__)

    :param image_url: The URL of an image from within Salesforce
    :type image_url: str
    :returns: The reference ID (``refid``) value
    :rtype: str
    """
    query_params = urllib.parse.parse_qs(urllib.parse.urlparse(image_url).query)
    ref_id = query_params.get(const.QUERY_PARAMS.REF_ID)
    ref_id = ref_id[0] if ref_id and not isinstance(ref_id, str) else ref_id
    return str(ref_id)


def download_image(
        image_url: str | None = None,
        file_name: str | None = None,
        file_path: str | None = None,
        response: requests.Response | None = None,
        extension: str = const.FILE_EXTENSIONS.JPEG,
) -> str:
    """Downloads an image and saves it to a specified directory.

    .. versionchanged:: 1.5.0
       This function now raises more specific exceptions instead of the generic :py:exc:`RuntimeError` exception.

    :param image_url: The absolute URL to the image
    :type image_url: str, optional
    :param file_name: The file name (including extension) to use as the file name (Default: randomly generated)
    :type file_name: str, optional
    :param file_path: File path where the image file should be saved (Default: ``./``)
    :type file_path: str, optional
    :param response: The response of the previously performed API call
    :type response: requests.Response, optional
    :param extension: The file extension to use if a file name with extension is not provided (Default: ``jpeg``)
    :type extension: str
    :returns: The full path to the downloaded image
    :rtype: str
    :raises salespyforce.errors.exceptions.MissingRequiredDataError: If an image URL and API response are both missing
    :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
    :raises requests.exceptions.Timeout: If the GET request for the image times out
    """
    if not any((image_url, response)):
        exc_msg = 'An image URL or an API response must be provided to download an image.'
        logger.error(exc_msg)
        raise errors.exceptions.MissingRequiredDataError(exc_msg)

    # Define an appropriate file path
    file_path = './' if not file_path else file_path
    file_path = f'{file_path}/' if not any((file_path.endswith('/'), file_path.endswith('\\'))) else file_path

    # Define a file name if not provided
    if not file_name:
        file_name = get_random_string(10, 'image_')
        file_name += extension

    # Perform the API call if not supplied
    if image_url and not response:
        response = requests.get(image_url, timeout=const.DEFAULT_API_TIMEOUT_SECONDS)
    if not response:
        exc_msg = const._LOG_MESSAGES._API_RESPONSE_UNSUCCESSFUL
        logger.error(exc_msg)
        raise errors.exceptions.GETRequestError(exc_msg)
    else:
        if response.status_code != 200:
            exc_msg = f'The image failed to download with a {response.status_code} status code.'
            logger.error(exc_msg)
            raise errors.exceptions.GETRequestError(exc_msg)

        # Export the response data as an image file
        with open(f'{file_path}{file_name}', 'wb') as file:
            file.write(response.content)
        return f'{file_path}{file_name}'
