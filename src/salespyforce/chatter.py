# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.chatter
:Synopsis:          Defines the Chatter-related functions associated with the Salesforce Connect API
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     22 Feb 2023
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


