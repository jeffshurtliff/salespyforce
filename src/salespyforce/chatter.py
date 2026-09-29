# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.chatter
:Synopsis:          Defines the Chatter-related functions associated with the Salesforce Connect API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     28 Sep 2026
"""

from __future__ import annotations

import logging
from typing import Any

from . import constants as const
from . import errors

logger = logging.getLogger(__name__)


def get_my_news_feed(sfdc_object, site_id: str | None = None) -> dict[str, Any]:
    """Retrieves the news feed for the user calling the function.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_news_feed.htm>`__)

    .. versionchanged:: 2.1.0
       The function now fails with the :py:exc:`salespyforce.errors.exceptions.GETRequestError` exception rather
       than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param site_id: The ID of an Experience Cloud site against which to query
    :type site_id: str, optional
    :returns: The news feed data in JSON format
    :rtype: dict[str, Any]
    :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
    :raises requests.exceptions.Timeout: If the API request times out
    :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
    """
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = endpoint_root + const.REST_PATHS.CHATTER_MY_NEWS_FEED
    return sfdc_object.get(endpoint)


def get_user_news_feed(sfdc_object, user_id: str, site_id: str | None = None) -> dict[str, Any]:
    """Retrieves another user's news feed.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_user_profile_feed.htm>`__)

    .. versionchanged:: 2.1.0
       The function now fails with the :py:exc:`salespyforce.errors.exceptions.GETRequestError` exception rather
       than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param user_id: The ID of the user whose feed you wish to return
    :type user_id: str
    :param site_id: The ID of an Experience Cloud site against which to query
    :type site_id: str, optional
    :returns: The news feed data
    :rtype: dict[str, Any]
    :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
    :raises requests.exceptions.Timeout: If the API request times out
    :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
    """
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = endpoint_root + const.REST_PATHS.CHATTER_USER_NEWS_FEED.format(user_id=user_id)
    return sfdc_object.get(endpoint)


def get_group_feed(sfdc_object, group_id: str, site_id: str | None = None):
    """Retrieves a group's news feed.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_group_feed.htm>`__)

    .. versionchanged:: 2.1.0
       The function now fails with the :py:exc:`salespyforce.errors.exceptions.GETRequestError` exception rather
       than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param group_id: The ID of the group whose feed you wish to return
    :type group_id: str
    :param site_id: The ID of an Experience Cloud site against which to query
    :type site_id: str, optional
    :returns: The news feed data
    :rtype: dict[str, Any]
    :raises salespyforce.errors.exceptions.GETRequestError: If Salesforce does not return a successful response
    :raises requests.exceptions.Timeout: If the API request times out
    :raises requests.exceptions.JSONDecodeError: If the response body does not contain valid JSON
    """
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = endpoint_root + const.REST_PATHS.CHATTER_GROUP_NEWS_FEED.format(group_id=group_id)
    return sfdc_object.get(endpoint)


def post_feed_item(
    sfdc_object,
    subject_id: str,
    message_text: str | None = None,
    message_segments: list[dict] | None = None,
    site_id: str | None = None,
    created_by_id: str | None = None,
) -> dict[str, Any]:
    """Publishes a new Chatter feed item.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_feed_item.htm>`__)

    .. versionchanged:: 1.4.0
       The function now raises the :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception rather
       than the generic :py:exc:`RuntimeError` exception.

    .. versionchanged:: 2.1.0
       The function now fails with the :py:exc:`salespyforce.errors.exceptions.POSTRequestError` exception rather
       than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response, and
       fails with the :py:exc:`salespyforce.errors.exceptions.DataMismatchError` exception if both message text and
       message segments are provided or if message segments are improperly structured.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param subject_id: The Subject ID against which to publish the feed item (e.g. ``0F9B000000000W2``)
    :type subject_id: str
    :param message_text: Plaintext to be used as the message body (Cannot be used if message segments are provided)
    :type message_text: str, optional
    :param message_segments: Collection of message segments to use instead of a plaintext message
    :type message_segments: list[dict], optional
    :param site_id: The ID of an Experience Cloud site against which to query
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
    message_segments = _construct_message_segments(message_text, message_segments)
    payload = {
        const.QUERY_PARAMS.BODY: {const.QUERY_PARAMS.MESSAGE_SEGMENTS: message_segments},
        const.QUERY_PARAMS.FEED_ELEMENT_TYPE: const.PAYLOAD_VALUES.FEED_ITEM,
        const.QUERY_PARAMS.SUBJECT_ID: subject_id,
    }
    if created_by_id:
        payload[const.QUERY_PARAMS.CREATED_BY_ID] = created_by_id
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = (
        f'{endpoint_root}{const.REST_PATHS.CHATTER_FEED_ELEMENTS}?'
        f'{const.QUERY_PARAMS.FEED_ELEMENT_TYPE}={const.PAYLOAD_VALUES.FEED_ITEM}&'
        f'{const.QUERY_PARAMS.SUBJECT_ID}={subject_id}'
    )
    return sfdc_object.post(endpoint=endpoint, payload=payload)


def post_comment(
    sfdc_object,
    feed_element_id: str,
    message_text: str | None = None,
    message_segments: list[dict] | None = None,
    site_id: str | None = None,
    created_by_id: str | None = None,
) -> dict[str, Any]:
    """Publishes a comment on an existing Chatter feed item.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_comment_to_feed_element.htm>`__)

    .. versionchanged:: 1.5.0
       This function now utilizes centralized constants and a new helper function to construct the endpoint and payload.
       It also now raises the :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception rather
       than the generic :py:exc:`RuntimeError` exception.

    .. versionchanged:: 2.1.0
       The function now fails with the :py:exc:`salespyforce.errors.exceptions.POSTRequestError` exception rather
       than the generic :py:exc:`RuntimeError` exception if the request does not return a successful response, and
       fails with the :py:exc:`salespyforce.errors.exceptions.DataMismatchError` exception if both message text and
       message segments are provided or if message segments are improperly structured.

    :param sfdc_object: The instantiated ``salespyforce.Salesforce`` object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param feed_element_id: The ID of the feed element on which to post the comment
    :type feed_element_id: str
    :param message_text: Plaintext to be used as the message body (Cannot be used if message segments are provided)
    :type message_text: str, optional
    :param message_segments: Collection of message segments to use instead of a plaintext message
    :type message_segments: list[dict], optional
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
    message_segments = _construct_message_segments(message_text, message_segments)
    payload = {const.QUERY_PARAMS.BODY: {const.QUERY_PARAMS.MESSAGE_SEGMENTS: message_segments}}
    if created_by_id:
        # noinspection PyTypeChecker
        payload[const.QUERY_PARAMS.CREATED_BY_ID] = created_by_id
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = f'{endpoint_root}{const.REST_PATHS.CHATTER_FEED_ELEMENT_COMMENTS.format(feed_element_id=feed_element_id)}'
    return sfdc_object.post(endpoint=endpoint, payload=payload)


def _get_site_endpoint_segment(_site_id: str | None = None) -> str:
    """Constructs the endpoint segment when querying a specific Experience Cloud site.

    :param _site_id: The Site ID of the Experience Cloud site
    :type _site_id: str, optional
    :returns: The API endpoint segment (or a blank string if no Site ID was provided)
    :rtype: str
    """
    _endpoint_segment = const.REST_PATHS.CONNECT_COMMUNITIES_SITE.format(site_id=_site_id) if _site_id else ''
    return _endpoint_segment


def _get_endpoint_root_segment(_api_version: str, _site_id: str | None = None) -> str:
    """Constructs the root segment of the API endpoint to query.

    .. versionadded:: 1.5.0

    :param _api_version: The API version string (e.g. ``v65.0``) to leverage for the API call
    :type _api_version: str
    :param _site_id: The Site ID of an Experience Cloud site to query against
    :type _site_id: str, optional
    :returns: The constructed root segment of the API endpoint as a string
    :rtype: str
    """
    _site_segment = _get_site_endpoint_segment(_site_id)
    return const.REST_PATHS.SERVICES_DATA_API_SITE.format(api_version=_api_version, site_segment=_site_segment)


def _construct_message_segments(
    _message_text: str | None = None,
    _message_segments: list[dict] | None = None,
) -> list[dict]:
    """Constructs the message segments payload when necessary or raises exception for missing or mismatched data.

    .. versionadded:: 2.1.0

    :param _message_text: Plaintext to be used as the message body (Cannot be used if message segments are provided)
    :type _message_text: str, optional
    :param _message_segments: Collection of message segments to use instead of a plaintext message
    :type _message_segments: list[dict], optional
    :returns: The constructed message segments
    :rtype: list[dict]
    :raises salespyforce.errors.exceptions.MissingRequiredDataError: If neither message text nor segments are provided
    :raises salespyforce.errors.exceptions.DataMismatchError: If both message text and message segments are provided or
                                                              if message segments are improperly structured
    """
    _message_text = '' if _message_text is None else _message_text
    if not any((_message_text, _message_segments)):
        _exc_msg = 'Message text or message segments are required to post a feed item or comment.'
        logger.error(_exc_msg)
        raise errors.exceptions.MissingRequiredDataError(_exc_msg)
    if all((_message_text, _message_segments)):
        _exc_msg = 'Message text and message segments cannot both be provided.'
        logger.error(_exc_msg)
        raise errors.exceptions.DataMismatchError(_exc_msg)
    if not _message_segments:
        _message_segments = _construct_simple_message_segment(_message_text)
    elif not all(isinstance(_segment, dict) for _segment in _message_segments):
        _exc_msg = 'Message segments must contain only dictionaries.'
        logger.error(_exc_msg)
        raise errors.exceptions.DataMismatchError(_exc_msg)
    return _message_segments


def _construct_simple_message_segment(_message_text: str) -> list[dict[str, str]]:
    """Constructs a simple message segments collection to be used in an API payload.

    :param _message_text: The plaintext message to be embedded in a message segment.
    :type _message_text: str
    :returns: The constructed message segments payload
    :rtype: list[dict[str, str]]
    """
    _message_segments = [{const.QUERY_PARAMS.TYPE: const.PAYLOAD_VALUES.TEXT, const.QUERY_PARAMS.TEXT: _message_text}]
    return _message_segments
