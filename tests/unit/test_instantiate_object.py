# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         tests.unit.test_instantiate_object
:Synopsis:       This module is used by pytest to test instantiating the core object
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff (via GPT-5.5-codex)
:Modified Date:  15 Jul 2026

These tests rely on the ``salesforce_unit`` fixture defined in
``conftest.py`` to keep them fast and deterministic. When you want to
verify behavior against a real org, add ``@pytest.mark.integration``
and switch the fixture parameter to ``salesforce_integration``.
"""

import json

import pytest
import yaml

from salespyforce import constants as const
from salespyforce import errors
from salespyforce.core import Salesforce


def test_instantiate_core_object(salesforce_unit):
    """This function tests the ability to instantiate the core object.

    .. versionadded:: 1.1.0

    .. versionchanged:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    sfdc_object = salesforce_unit
    assert 'force.com' in sfdc_object.base_url


def test_get_api_versions(salesforce_unit):
    """This function tests the get_api_versions() method in the core object.

    .. versionadded:: 1.1.0

    .. versionchanged:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    api_versions = salesforce_unit.get_api_versions()
    assert isinstance(api_versions, list) and 'version' in api_versions[0]


def test_get_rest_resources(salesforce_unit):
    """This function tests the get_rest_resources() method in the core object.

    .. versionadded:: 1.1.0

    .. versionchanged:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    rest_resources = salesforce_unit.get_rest_resources()
    assert 'metadata' in rest_resources


def test_get_org_limits(salesforce_unit):
    """This function tests the get_org_limits() method in the core object.

    .. versionadded:: 1.1.0

    .. versionchanged:: 1.4.0
       The function now utilizes the ``salesforce_unit`` fixture.
    """
    org_limits = salesforce_unit.get_org_limits()
    assert 'DailyApiRequests' in org_limits


def _mock_client_initialization(monkeypatch):
    """Replace network-dependent client initialization operations."""
    monkeypatch.setattr(
        Salesforce,
        'connect',
        lambda _self: {
            const.CLIENT_SETTINGS.ACCESS_TOKEN: 'token',
            const.CLIENT_SETTINGS.INSTANCE_URL: 'https://example.my.salesforce.com',
            const.CLIENT_SETTINGS.SIGNATURE: 'signature',
        },
    )
    monkeypatch.setattr(Salesforce, 'get_latest_api_version', lambda _self: '65.0')
    monkeypatch.setattr(
        Salesforce,
        'retrieve_current_user_info',
        lambda _self, **_kwargs: {},
    )


@pytest.mark.parametrize('extension', ['yml', 'yaml'])
def test_salesforce_infers_yaml_helper_string_paths(monkeypatch, tmp_path, extension):
    """String helper paths infer both supported YAML extensions."""
    _mock_client_initialization(monkeypatch)
    helper_path = tmp_path / f'helper.{extension}'
    helper_path.write_text(yaml.safe_dump({const.HELPER_SETTINGS.CONNECTION: {}}))

    client = Salesforce(helper=str(helper_path))

    assert client.helper_path == str(helper_path)
    assert const.HELPER_SETTINGS.CONNECTION in client._helper_settings


def test_salesforce_infers_json_helper_string_path(monkeypatch, tmp_path):
    """String JSON helper paths select the JSON parser automatically."""
    _mock_client_initialization(monkeypatch)
    helper_path = tmp_path / 'helper.json'
    helper_path.write_text(json.dumps({const.HELPER_SETTINGS.CONNECTION: {}}))

    client = Salesforce(helper=str(helper_path))

    assert client.helper_path == str(helper_path)
    assert const.HELPER_SETTINGS.CONNECTION in client._helper_settings


def test_salesforce_helper_string_rejects_missing_file(monkeypatch, tmp_path):
    """Missing string helper paths retain the documented FileNotFoundError behavior."""
    _mock_client_initialization(monkeypatch)

    with pytest.raises(FileNotFoundError):
        Salesforce(helper=str(tmp_path / 'missing.json'))


def test_salesforce_helper_string_rejects_unknown_file_type(monkeypatch, tmp_path):
    """Unknown string helper file types retain UnknownFileTypeError behavior."""
    _mock_client_initialization(monkeypatch)
    helper_path = tmp_path / 'helper.txt'
    helper_path.write_text('unrecognized helper content')

    with pytest.warns((DeprecationWarning, UserWarning)):
        with pytest.raises(errors.exceptions.UnknownFileTypeError):
            Salesforce(helper=str(helper_path))


@pytest.mark.parametrize(
    'helper_value_factory',
    [
        lambda path: (str(path), const.FILE_EXTENSIONS.YAML),
        lambda path: [str(path), const.FILE_EXTENSIONS.YAML],
        lambda path: {str(path), const.FILE_EXTENSIONS.YAML},
        lambda path: {
            'path': str(path),
            'type': const.FILE_EXTENSIONS.YAML,
        },
    ],
)
def test_salesforce_preserves_explicit_helper_forms(
    monkeypatch,
    tmp_path,
    helper_value_factory,
):
    """Explicit sequence and mapping helper forms retain their parser selection."""
    _mock_client_initialization(monkeypatch)
    helper_path = tmp_path / 'helper.data'
    helper_path.write_text(yaml.safe_dump({const.HELPER_SETTINGS.CONNECTION: {}}))

    client = Salesforce(helper=helper_value_factory(helper_path))

    assert const.HELPER_SETTINGS.CONNECTION in client._helper_settings
