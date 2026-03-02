# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         tests.unit.test_helper_utils
:Synopsis:       This module is used by pytest to test helper utility functions
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff (via GPT-5.3-Codex)
:Modified Date:  02 Mar 2026
"""

import json

import pytest
import yaml

from salespyforce import constants as const
from salespyforce import errors
from salespyforce.utils import helper


def test_import_helper_file_loads_yaml_content(tmp_path):
    """This function tests importing YAML helper configuration content.

    .. versionadded:: 1.5.0
    """
    config_path = tmp_path / 'helper.yml'
    config_path.write_text('ssl_verify: yes\n')

    parsed_config = helper.import_helper_file(str(config_path), 'yaml')

    assert parsed_config == {'ssl_verify': True}


def test_import_helper_file_loads_json_content(tmp_path):
    """This function tests importing JSON helper configuration content.

    .. versionadded:: 1.5.0
    """
    config_path = tmp_path / 'helper.json'
    payload = {'ssl_verify': False}
    config_path.write_text(json.dumps(payload))

    parsed_config = helper.import_helper_file(str(config_path), 'json')

    assert parsed_config == payload


def test_import_helper_file_rejects_invalid_extension(tmp_path):
    """This function tests import_helper_file when an invalid file type is provided.

    .. versionadded:: 1.5.0
    """
    config_path = tmp_path / 'helper.txt'
    config_path.write_text('ssl_verify: true')

    with pytest.raises(errors.exceptions.InvalidHelperFileTypeError):
        helper.import_helper_file(str(config_path), 'txt')


def test_convert_yaml_to_bool_for_true_and_false_values():
    """This function tests conversion of YAML-style boolean text values

    .. versionadded:: 1.5.0
    """
    assert helper._convert_yaml_to_bool('yes') is True
    assert helper._convert_yaml_to_bool('TRUE') is True
    assert helper._convert_yaml_to_bool('no') is False


def test_get_connection_info_collects_only_supported_fields():
    """This function tests extraction of the supported helper connection keys.

    .. versionadded:: 1.5.0
    """
    helper_config = {
        const.HELPER_SETTINGS.CONNECTION: {
            const.HELPER_SETTINGS.USERNAME: 'user@example.com',
            const.HELPER_SETTINGS.PASSWORD: 'abc123',
            'ignored': 'value',
        }
    }

    connection_info = helper._get_connection_info(helper_config)

    assert connection_info == {
        const.HELPER_SETTINGS.USERNAME: 'user@example.com',
        const.HELPER_SETTINGS.PASSWORD: 'abc123',
    }


def test_collect_values_with_boolean_mapping_and_missing_fields():
    """This function tests collecting values while applying helper defaults and YAML mapping.

    .. versionadded:: 1.5.0
    """
    helper_config = {
        const.HELPER_SETTINGS.SSL_VERIFY: 'yes',
        'custom_key': 'custom-value',
    }

    values = helper._collect_values(
        (const.HELPER_SETTINGS.SSL_VERIFY, 'missing_key', 'custom_key'),
        helper_config,
    )

    assert values == {
        const.HELPER_SETTINGS.SSL_VERIFY: True,
        'missing_key': None,
        'custom_key': 'custom-value',
    }


def test_collect_values_ignores_missing_keys_when_requested():
    """This function tests collect_values when _ignore_missing is set to True.

    .. versionadded:: 1.5.0
    """
    values = helper._collect_values('missing_key', {}, _ignore_missing=True)

    assert values == {}


def test_collect_values_sets_ssl_verify_default_true_when_missing():
    """This function tests collect_values default behavior for a missing ssl_verify key.

    .. versionadded:: 1.5.0
    """
    values = helper._collect_values(const.HELPER_SETTINGS.SSL_VERIFY, {})

    assert values == {const.HELPER_SETTINGS.SSL_VERIFY: True}


def test_get_helper_settings_uses_detected_file_type(monkeypatch, tmp_path):
    """This function tests get_helper_settings falling back to auto file type detection.

    .. versionadded:: 1.5.0
    """
    config_path = tmp_path / 'helper.conf'
    payload = {
        const.HELPER_SETTINGS.CONNECTION: {
            const.HELPER_SETTINGS.USERNAME: 'user@example.com',
            const.HELPER_SETTINGS.PASSWORD: 'abc123',
            'unsupported_key': 'ignore',
        },
        const.HELPER_SETTINGS.SSL_VERIFY: 'no',
    }
    config_path.write_text(yaml.safe_dump(payload))

    monkeypatch.setattr(helper, 'get_file_type', lambda _path: 'yaml')

    settings = helper.get_helper_settings(str(config_path), file_type='unknown')

    assert settings == {
        const.HELPER_SETTINGS.CONNECTION: {
            const.HELPER_SETTINGS.USERNAME: 'user@example.com',
            const.HELPER_SETTINGS.PASSWORD: 'abc123',
        },
        const.HELPER_SETTINGS.SSL_VERIFY: False,
    }


def test_get_helper_settings_respects_defined_settings_overrides(tmp_path):
    """This function tests get_helper_settings when fields are already defined by caller settings.

    .. versionadded:: 1.5.0
    """
    config_path = tmp_path / 'helper.yml'
    config_path.write_text(
        yaml.safe_dump(
            {
                const.HELPER_SETTINGS.CONNECTION: {
                    const.HELPER_SETTINGS.USERNAME: 'user@example.com',
                },
                const.HELPER_SETTINGS.SSL_VERIFY: 'yes',
            }
        )
    )

    settings = helper.get_helper_settings(
        str(config_path),
        defined_settings={
            const.HELPER_SETTINGS.CONNECTION: {'username': 'already-set'},
            const.HELPER_SETTINGS.SSL_VERIFY: False,
        },
    )

    assert settings == {}
