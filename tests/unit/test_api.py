# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         tests.unit.test_api
:Synopsis:       Tests low-level Salesforce API request and response handling
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff (via GPT-5.5-codex)
:Modified Date:  15 Jul 2026
"""

from types import SimpleNamespace

import pytest

from salespyforce import api
from salespyforce.core import Salesforce


class FakeResponse:
    """Represent a deterministic requests response for API unit tests."""

    def __init__(self, status_code=200, json_body=None, content=b'{}', json_error=None):
        self.status_code = status_code
        self.json_body = json_body
        self.content = content
        self.json_error = json_error
        self.json_calls = 0
        self.text = content.decode() if isinstance(content, bytes) else str(content)

    def json(self):
        """Return configured JSON data or raise the configured decoding error."""
        self.json_calls += 1
        if self.json_error:
            raise self.json_error
        return self.json_body


@pytest.fixture()
def api_client():
    """Return the minimum client state needed by low-level API functions."""
    return SimpleNamespace(
        access_token='token',
        instance_url='https://example.my.salesforce.com',
    )


@pytest.mark.parametrize('method', ['get', 'post', 'patch', 'put', 'delete'])
def test_api_methods_convert_non_empty_json_responses(monkeypatch, api_client, method):
    """API methods deserialize populated JSON responses when requested."""
    response = FakeResponse(json_body={'success': True})
    monkeypatch.setattr(api.requests, method, lambda *_args, **_kwargs: response)

    if method == 'get':
        result = api.get(api_client, '/services/data')
    elif method == 'delete':
        result = api.delete(api_client, '/services/data/example')
    else:
        result = api.api_call_with_payload(
            api_client,
            method,
            '/services/data/example',
            {'Name': 'Example'},
        )

    assert result == {'success': True}
    assert response.json_calls == 1


@pytest.mark.parametrize(
    ('method', 'status_code', 'content'),
    [
        ('get', 204, b''),
        ('post', 205, b''),
        ('patch', 200, b''),
        ('put', 204, b''),
        ('delete', 204, b''),
    ],
)
def test_api_methods_return_raw_successful_empty_responses(
        monkeypatch, api_client, method, status_code, content,
):
    """Successful empty responses are returned without attempting JSON decoding."""
    response = FakeResponse(status_code=status_code, content=content)
    monkeypatch.setattr(api.requests, method, lambda *_args, **_kwargs: response)

    if method == 'get':
        result = api.get(api_client, '/services/data')
    elif method == 'delete':
        result = api.delete(api_client, '/services/data/example')
    else:
        result = api.api_call_with_payload(
            api_client,
            method,
            '/services/data/example',
            {'Name': 'Example'},
        )

    assert result is response
    assert response.json_calls == 0


def test_return_json_false_returns_raw_response(monkeypatch, api_client):
    """Explicitly disabling JSON conversion returns the original response."""
    response = FakeResponse(json_body={'success': True})
    monkeypatch.setattr(api.requests, 'get', lambda *_args, **_kwargs: response)

    result = api.get(api_client, '/services/data', return_json=False)

    assert result is response
    assert response.json_calls == 0


@pytest.mark.parametrize('method', ['get', 'post', 'patch', 'put', 'delete'])
def test_api_methods_preserve_error_status_behavior(monkeypatch, api_client, method):
    """Non-success status codes continue to raise RuntimeError."""
    response = FakeResponse(status_code=400, content=b'bad request')
    monkeypatch.setattr(api.requests, method, lambda *_args, **_kwargs: response)

    with pytest.raises(RuntimeError, match=f'The {method.upper()} request failed with a 400 status code'):
        if method == 'get':
            api.get(api_client, '/services/data')
        elif method == 'delete':
            api.delete(api_client, '/services/data/example')
        else:
            api.api_call_with_payload(
                api_client,
                method,
                '/services/data/example',
                {'Name': 'Example'},
            )


def test_get_preserves_malformed_non_empty_json_behavior(monkeypatch, api_client):
    """GET continues to surface malformed non-empty JSON conversion errors."""
    response = FakeResponse(content=b'not-json', json_error=ValueError('invalid JSON'))
    monkeypatch.setattr(api.requests, 'get', lambda *_args, **_kwargs: response)

    with pytest.raises(ValueError, match='invalid JSON'):
        api.get(api_client, '/services/data')


def test_delete_preserves_malformed_non_empty_json_behavior(monkeypatch, api_client):
    """DELETE continues to surface malformed non-empty JSON conversion errors."""
    response = FakeResponse(content=b'not-json', json_error=ValueError('invalid JSON'))
    monkeypatch.setattr(api.requests, 'delete', lambda *_args, **_kwargs: response)

    with pytest.raises(ValueError, match='invalid JSON'):
        api.delete(api_client, '/services/data/example')


def test_payload_call_preserves_malformed_non_empty_json_behavior(monkeypatch, api_client, capsys):
    """Payload calls continue to return raw malformed non-empty responses."""
    response = FakeResponse(content=b'not-json', json_error=ValueError('invalid JSON'))
    monkeypatch.setattr(api.requests, 'post', lambda *_args, **_kwargs: response)

    result = api.api_call_with_payload(
        api_client,
        'post',
        '/services/data/example',
        {'Name': 'Example'},
    )

    assert result is response
    assert 'Failed to convert the API response to JSON format' in capsys.readouterr().out


def test_salesforce_patch_defaults_to_raw_response(monkeypatch, api_client):
    """Salesforce.patch preserves the published return_json=False default."""
    captured = {}

    def fake_api_call(*_args, **kwargs):
        captured.update(kwargs)
        return 'response'

    monkeypatch.setattr(api, 'api_call_with_payload', fake_api_call)

    result = Salesforce.patch(api_client, '/services/data/example', {'Name': 'Example'})

    assert result == 'response'
    assert captured['return_json'] is False


def test_salesforce_patch_allows_explicit_json_conversion(monkeypatch, api_client):
    """Salesforce.patch forwards an explicit return_json=True selection."""
    captured = {}

    def fake_api_call(*_args, **kwargs):
        captured.update(kwargs)
        return {'success': True}

    monkeypatch.setattr(api, 'api_call_with_payload', fake_api_call)

    result = Salesforce.patch(
        api_client,
        '/services/data/example',
        {'Name': 'Example'},
        return_json=True,
    )

    assert result == {'success': True}
    assert captured['return_json'] is True
