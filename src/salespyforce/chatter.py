# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.chatter
:Synopsis:          Defines the Chatter-related functions associated with the Salesforce Connect API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     25 Feb 2026
"""

from __future__ import annotations

from typing import Optional

from . import errors
from . import constants as const
from .utils import log_utils

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def _get_site_endpoint_segment(_site_id: Optional[str] = None) -> str:
    """This function constructs the endpoint segment when querying a specific Experience Cloud site.

    .. versionchanged:: 1.5.0
       The function now leverages a constant for the endpoint segment.

    :param _site_id: The Site ID of the Experience Cloud site
    :type _site_id: str, None
    :returns: The API endpoint segment (or a blank string if no Site ID was provided)
    """
    _endpoint_segment = const.REST_PATHS.CONNECT_COMMUNITIES_SITE.format(site_id=_site_id) if _site_id else ''
    return _endpoint_segment


def _get_endpoint_root_segment(_api_version: str, _site_id: Optional[str] = None) -> str:
    """This function constructs the root segment of the API endpoint to query.

    .. versionadded:: 1.5.0

    :param _api_version: The API version string (e.g. ``v65.0``) to leverage for the API call
    :type _api_version: str
    :param _site_id: The Site ID of an Experience Cloud site to query against (optional)
    :type _site_id: str, None
    :returns: The constructed root segment of the API endpoint as a string
    """
    _site_segment = _get_site_endpoint_segment(_site_id)
    return const.REST_PATHS.SERVICES_DATA_API_SITE.format(api_version=_api_version, site_segment=_site_segment)


def get_my_news_feed(sfdc_object, site_id: Optional[str] = None):
    """This function retrieves the news feed for the user calling the function.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_news_feed.htm>`__)

    .. versionchanged:: 1.5.0
       This function now utilizes centralized constants and a new helper function to construct the endpoint URL.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param site_id: The ID of an Experience Cloud site against which to query (optional)
    :type site_id: str, None
    :returns: The news feed data
    :raises: :py:exc:`RuntimeError`
    """
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = endpoint_root + const.REST_PATHS.CHATTER_MY_NEWS_FEED
    return sfdc_object.get(endpoint)


def get_user_news_feed(sfdc_object, user_id: str, site_id: Optional[str] = None):
    """This function retrieves another user's news feed.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_user_profile_feed.htm>`__)

    .. versionchanged:: 1.5.0
       This function now utilizes centralized constants and a new helper function to construct the endpoint URL.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param user_id: The ID of the user whose feed you wish to return
    :type user_id: str
    :param site_id: The ID of an Experience Cloud site against which to query (optional)
    :type site_id: str, None
    :returns: The news feed data
    :raises: :py:exc:`RuntimeError`
    """
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = endpoint_root + const.REST_PATHS.CHATTER_USER_NEWS_FEED.format(user_id=user_id)
    return sfdc_object.get(endpoint)


def get_group_feed(sfdc_object, group_id: str, site_id: Optional[str] = None):
    """This function retrieves a group's news feed.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_group_feed.htm>`__)

    .. versionchanged:: 1.5.0
       This function now utilizes centralized constants and a new helper function to construct the endpoint URL.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param group_id: The ID of the group whose feed you wish to return
    :type group_id: str
    :param site_id: The ID of an Experience Cloud site against which to query (optional)
    :type site_id: str, None
    :returns: The news feed data
    :raises: :py:exc:`RuntimeError`
    """
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = endpoint_root + const.REST_PATHS.CHATTER_GROUP_NEWS_FEED.format(group_id=group_id)
    return sfdc_object.get(endpoint)


def post_feed_item(
        sfdc_object,
        subject_id: str,
        message_text: Optional[str] = None,
        message_segments: Optional[list] = None,
        site_id: Optional[str] = None,
        created_by_id: Optional[str] = None,
):
    """This function publishes a new Chatter feed item.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_feed_item.htm>`__)

    .. versionchanged:: 1.5.0
       This function now utilizes centralized constants and a new helper function to construct the endpoint and payload.

    .. versionchanged:: 1.4.0
       The function now raises the :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception rather
       than the generic :py:exc:`RuntimeError` exception.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
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
    :raises: :py:exc:`RuntimeError`,
             :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError`
    """
    if not any((message_text, message_segments)):
        raise errors.exceptions.MissingRequiredDataError('Message text or message segments are required to post a feed item.')
    if not message_segments:
        message_segments = _construct_simple_message_segment(message_text)
    payload = {
        const.QUERY_PARAMS.BODY: {
            const.QUERY_PARAMS.MESSAGE_SEGMENTS: message_segments
        },
        const.QUERY_PARAMS.FEED_ELEMENT_TYPE: const.PAYLOAD_VALUES.FEED_ITEM,
        const.QUERY_PARAMS.SUBJECT_ID: subject_id,
    }
    if created_by_id:
        payload[const.QUERY_PARAMS.CREATED_BY_ID] = created_by_id
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = f'{endpoint_root}{const.REST_PATHS.CHATTER_FEED_ELEMENTS}?' \
               f'{const.QUERY_PARAMS.FEED_ELEMENT_TYPE}={const.PAYLOAD_VALUES.FEED_ITEM}&' \
               f'{const.QUERY_PARAMS.SUBJECT_ID}={subject_id}'
    return sfdc_object.post(endpoint=endpoint, payload=payload)


def post_comment(
        sfdc_object,
        feed_element_id: str,
        message_text: Optional[str] = None,
        message_segments: Optional[list] = None,
        site_id: Optional[str] = None,
        created_by_id: Optional[str] = None,
):
    """This function publishes a comment on a Chatter feed item.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_comment_to_feed_element.htm>`__)

    .. versionchanged:: 1.5.0
       This function now utilizes centralized constants and a new helper function to construct the endpoint and payload.
       It also now raises the :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError` exception rather
       than the generic :py:exc:`RuntimeError` exception.

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param feed_element_id: The ID of the feed element on which to post the comment
    :type feed_element_id: str
    :param message_text: Plaintext to be used as the message body
    :type message_text: str, None
    :param message_segments: Collection of message segments to use instead of a plaintext message
    :type message_segments: list, None
    :param site_id: The ID of an Experience Cloud site against which to query (optional)
    :type site_id: str, None
    :param created_by_id: The ID of the user to impersonate (**Experimental**)
    :type created_by_id: str, None
    :returns: The response of the POST request
    :raises: :py:exc:`RuntimeError`
             :py:exc:`salespyforce.errors.exceptions.MissingRequiredDataError`
    """
    if not any((message_text, message_segments)):
        raise errors.exceptions.MissingRequiredDataError('Message text or message segments are required to post a feed comment.')

    if not message_segments:
        message_segments = _construct_simple_message_segment(message_text)
    payload = {
        const.QUERY_PARAMS.BODY: {
            const.QUERY_PARAMS.MESSAGE_SEGMENTS: message_segments
        }
    }
    if created_by_id:
        # noinspection PyTypeChecker
        payload[const.QUERY_PARAMS.CREATED_BY_ID] = created_by_id
    endpoint_root = _get_endpoint_root_segment(sfdc_object.version, site_id)
    endpoint = f'{endpoint_root}{const.REST_PATHS.CHATTER_FEED_ELEMENT_COMMENTS.format(feed_element_id=feed_element_id)}'
    return sfdc_object.post(endpoint=endpoint, payload=payload)


def _construct_simple_message_segment(_message_text: str) -> list:
    """This function constructs a simple message segments collection to be used in an API payload.

    .. versionchanged:: 1.5.0
       This function now utilizes centralized constants to construct the payload.

    :param _message_text: The plaintext message to be embedded in a message segment.
    :type _message_text: str
    :returns: The constructed message segments payload
    """
    _message_segments = [
        {
            const.QUERY_PARAMS.TYPE: const.PAYLOAD_VALUES.TEXT,
            const.QUERY_PARAMS.TEXT: _message_text
        }
    ]
    return _message_segments
