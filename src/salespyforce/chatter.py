# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.chatter
:Synopsis:          Defines the Chatter-related functions associated with the Salesforce Connect API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     13 Mar 2023
"""

from .utils import log_utils

# Initialize logging
logger = log_utils.initialize_logging(__name__)


def _get_site_endpoint_segment(_site_id=None):
    """This function constructs the endpoint segment when querying a specific Experience Cloud site.

    :param _site_id: The Site ID of the Experience Cloud site
    :type _site_id: str
    :returns: The API endpoint segment (or a blank string if no Site ID was provided)
    """
    _endpoint_segment = f'/connect/communities/{_site_id}' if _site_id else ''
    return _endpoint_segment


def get_my_news_feed(sfdc_object, site_id=None):
    """This function retrieves the news feed for the user calling the function.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_news_feed.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param site_id: The ID of an Experience Cloud site against which to query (optional)
    :type site_id: str, None
    :returns: The news feed data
    :raises: :py:exc:`RuntimeError`
    """
    site_segment = _get_site_endpoint_segment(site_id)
    endpoint = f'/services/data/{sfdc_object.version}{site_segment}/chatter/feeds/news/me/feed-elements'
    return sfdc_object.get(endpoint)


def get_user_news_feed(sfdc_object, user_id, site_id=None):
    """This function retrieves another user's news feed.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_user_profile_feed.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param user_id: The ID of the user whose feed you wish to return
    :type user_id: str
    :param site_id: The ID of an Experience Cloud site against which to query (optional)
    :type site_id: str, None
    :returns: The news feed data
    :raises: :py:exc:`RuntimeError`
    """
    site_segment = _get_site_endpoint_segment(site_id)
    endpoint = f'/services/data/{sfdc_object.version}{site_segment}/chatter/feeds/user-profile/{user_id}/feed-elements'
    return sfdc_object.get(endpoint)


def get_group_feed(sfdc_object, group_id, site_id=None):
    """This function retrieves a group's news feed.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_get_group_feed.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
    :param group_id: The ID of the group whose feed you wish to return
    :type group_id: str
    :param site_id: The ID of an Experience Cloud site against which to query (optional)
    :type site_id: str, None
    :returns: The news feed data
    :raises: :py:exc:`RuntimeError`
    """
    site_segment = _get_site_endpoint_segment(site_id)
    endpoint = f'/services/data/{sfdc_object.version}{site_segment}/chatter/feeds/record/{group_id}/feed-elements'
    return sfdc_object.get(endpoint)


def post_feed_item(sfdc_object, subject_id, message_text=None, message_segments=None, site_id=None, created_by_id=None):
    """This function publishes a new Chatter feed item.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_feed_item.htm>`_)

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
    :raises: :py:exc:`RuntimeError`
    """
    site_segment = _get_site_endpoint_segment(site_id)
    if not any((message_text, message_segments)):
        raise RuntimeError('Message text or message segments are required to post a feed item.')
    if not message_segments:
        message_segments = _construct_simple_message_segment(message_text)
    body = {
        'body': {
            'messageSegments': message_segments
        },
        'feedElementType': 'FeedItem',
        'subjectId': subject_id,
    }
    if created_by_id:
        body['createdById'] = created_by_id
    endpoint = f'/services/data/{sfdc_object.version}{site_segment}/chatter/feed-elements?' \
               f'feedElementType=FeedItem&subjectId={subject_id}'
    return sfdc_object.post(endpoint=endpoint, payload=body)


def post_comment(sfdc_object, feed_element_id, message_text=None, message_segments=None, site_id=None, created_by_id=None):
    """This function publishes a comment on a Chatter feed item.
    (`Reference <https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickreference_post_comment_to_feed_element.htm>`_)

    :param sfdc_object: The instantiated SalesPyForce object
    :type sfdc_object: class[salespyforce.Salesforce]
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
    site_segment = _get_site_endpoint_segment(site_id)
    if not any((message_text, message_segments)):
        raise RuntimeError('Message text or message segments are required to post a feed comment.')
    if not message_segments:
        message_segments = _construct_simple_message_segment(message_text)
    body = {
        'body': {
            'messageSegments': message_segments
        }
    }
    if created_by_id:
        body['createdById'] = created_by_id
    endpoint = f'/services/data/{sfdc_object.version}{site_segment}/chatter/feed-elements/' \
               f'{feed_element_id}/capabilities/comments/items'
    return sfdc_object.post(endpoint=endpoint, payload=body)


def _construct_simple_message_segment(_message_text):
    """This function constructs a simple message segments collection to be used in an API payload.

    :param _message_text: The plaintext message to be embedded in a message segment.
    :type _message_text: str
    :returns: The constructed message segments payload
    """
    _message_segments = [
        {
            'type': 'text',
            'text': _message_text
        }
    ]
    return _message_segments

