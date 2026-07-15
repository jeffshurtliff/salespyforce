# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         tests.unit.test_knowledge
:Synopsis:       Tests Salesforce Knowledge endpoint and validation behavior
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff (via GPT-5.5-codex)
:Modified Date:  15 Jul 2026
"""

from types import SimpleNamespace

import pytest

from salespyforce import constants as const
from salespyforce import errors, knowledge


def test_publish_article_uses_centralized_master_version_endpoint():
    """Knowledge publishing formats the centralized master-version endpoint."""
    captured = {}
    response = SimpleNamespace(status_code=204)

    def patch(endpoint, payload):
        captured['endpoint'] = endpoint
        captured['payload'] = payload
        return response

    client = SimpleNamespace(version='v65.0', patch=patch)

    result = knowledge.publish_article(client, 'ka0xx000000001', major_version=True)

    assert result is True
    assert captured['endpoint'] == const.REST_PATHS.ARTICLE_MASTER_VERSION_BY_ID.format(
        api_version='v65.0',
        article_id='ka0xx000000001',
    )
    assert captured['payload'] == {
        const.QUERY_PARAMS.PUBLISH_STATUS: const.PAYLOAD_VALUES.ONLINE,
        const.QUERY_PARAMS.VERSION_NUMBER: const.PAYLOAD_VALUES.NEXT_VERSION,
    }


def test_publish_article_returns_full_response_for_minor_version():
    """Knowledge publishing can return the raw response and omit the major-version field."""
    captured = {}
    response = SimpleNamespace(status_code=204)

    def patch(endpoint, payload):
        captured['endpoint'] = endpoint
        captured['payload'] = payload
        return response

    client = SimpleNamespace(version='v65.0', patch=patch)

    result = knowledge.publish_article(
        client,
        'ka0xx000000001',
        major_version=False,
        full_response=True,
    )

    assert result is response
    assert captured['payload'] == {
        const.QUERY_PARAMS.PUBLISH_STATUS: const.PAYLOAD_VALUES.ONLINE,
    }


def test_validate_knowledge_sobject_supplies_default():
    """Missing Knowledge sObjects use the centralized default."""
    assert knowledge._validate_knowledge_sobject() == const.SOBJECTS.KNOWLEDGE


def test_validate_knowledge_sobject_rejects_endpoint_conflict():
    """Custom sObjects cannot be combined with the Knowledge Articles endpoint."""
    with pytest.raises(errors.exceptions.DataMismatchError):
        knowledge._validate_knowledge_sobject('FAQ__kav', True)


def test_validate_knowledge_sobject_rejects_non_string():
    """Knowledge sObjects must be supplied as strings."""
    with pytest.raises(TypeError):
        knowledge._validate_knowledge_sobject(123)


def test_validate_article_data_requires_populated_dictionary():
    """Required article data cannot be omitted or supplied as another type."""
    with pytest.raises(errors.exceptions.MissingRequiredDataError):
        knowledge._validate_article_data(_required=True)

    with pytest.raises(TypeError):
        knowledge._validate_article_data('invalid')


def test_check_required_article_fields_accepts_complete_data():
    """Complete article data passes required-field validation."""
    article_data = {
        const.SOBJECT_FIELDS.TITLE: 'Example',
        const.SOBJECT_FIELDS.URL_NAME: 'example',
    }

    assert knowledge._check_required_article_fields(article_data) is None


def test_check_required_article_fields_rejects_missing_field():
    """Incomplete article data raises MissingRequiredDataError."""
    with pytest.raises(errors.exceptions.MissingRequiredDataError):
        knowledge._check_required_article_fields({const.SOBJECT_FIELDS.TITLE: 'Example'})
