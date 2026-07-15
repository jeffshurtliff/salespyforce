# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         tests.unit.test_chatter
:Synopsis:       Tests centralized Salesforce Chatter endpoints and payloads
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff (via GPT-5.5-codex)
:Modified Date:  15 Jul 2026
"""

from types import SimpleNamespace

import pytest

from salespyforce import chatter, constants as const, errors


class ChatterClient:
    """Capture Chatter calls without performing network requests."""

    version = 'v65.0'

    def __init__(self):
        self.calls = []

    def get(self, endpoint):
        """Capture a GET endpoint."""
        self.calls.append(('get', endpoint, None))
        return {'endpoint': endpoint}

    def post(self, endpoint, payload):
        """Capture a POST endpoint and payload."""
        self.calls.append(('post', endpoint, payload))
        return SimpleNamespace(status_code=201)


def test_news_feed_endpoints_support_org_and_site_contexts():
    """News-feed helpers format centralized endpoints with and without a site."""
    client = ChatterClient()

    chatter.get_my_news_feed(client)
    chatter.get_user_news_feed(client, '005xx000000001', site_id='0DBxx000000001')
    chatter.get_group_feed(client, '0F9xx000000001')

    assert client.calls[0][1] == '/services/data/v65.0/chatter/feeds/news/me/feed-elements'
    assert client.calls[1][1] == (
        '/services/data/v65.0/connect/communities/0DBxx000000001/'
        'chatter/feeds/user-profile/005xx000000001/feed-elements'
    )
    assert client.calls[2][1] == '/services/data/v65.0/chatter/feeds/record/0F9xx000000001/feed-elements'


def test_post_feed_item_uses_centralized_payload_values():
    """Posting a feed item constructs the expected endpoint and payload."""
    client = ChatterClient()

    result = chatter.post_feed_item(
        client,
        '005xx000000001',
        message_text='Hello',
        created_by_id='005xx000000002',
    )

    method, endpoint, payload = client.calls[0]
    assert result.status_code == 201
    assert method == 'post'
    assert endpoint.endswith('feedElementType=FeedItem&subjectId=005xx000000001')
    assert payload == {
        const.QUERY_PARAMS.BODY: {
            const.QUERY_PARAMS.MESSAGE_SEGMENTS: [
                {
                    const.QUERY_PARAMS.TYPE: const.PAYLOAD_VALUES.TEXT,
                    const.QUERY_PARAMS.TEXT: 'Hello',
                }
            ]
        },
        const.QUERY_PARAMS.FEED_ELEMENT_TYPE: const.PAYLOAD_VALUES.FEED_ITEM,
        const.QUERY_PARAMS.SUBJECT_ID: '005xx000000001',
        const.QUERY_PARAMS.CREATED_BY_ID: '005xx000000002',
    }


@pytest.mark.parametrize(
    ('function', 'required_id'),
    [
        (chatter.post_feed_item, '005xx000000001'),
        (chatter.post_comment, '0D5xx000000001'),
    ],
)
def test_chatter_posts_require_message_content(function, required_id):
    """Chatter post helpers reject calls without message content."""
    with pytest.raises(errors.exceptions.MissingRequiredDataError):
        function(ChatterClient(), required_id)


def test_post_comment_uses_site_endpoint_and_message_segments():
    """Posting a comment respects explicit segments and site context."""
    client = ChatterClient()
    segments = [{const.QUERY_PARAMS.TYPE: const.PAYLOAD_VALUES.TEXT, const.QUERY_PARAMS.TEXT: 'Hi'}]

    chatter.post_comment(
        client,
        '0D5xx000000001',
        message_segments=segments,
        site_id='0DBxx000000001',
    )

    _, endpoint, payload = client.calls[0]
    assert endpoint == (
        '/services/data/v65.0/connect/communities/0DBxx000000001/'
        'chatter/feed-elements/0D5xx000000001/capabilities/comments/items'
    )
    assert payload == {
        const.QUERY_PARAMS.BODY: {
            const.QUERY_PARAMS.MESSAGE_SEGMENTS: segments,
        }
    }
