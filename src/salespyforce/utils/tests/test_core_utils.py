# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         salespyforce.utils.tests.test_core_utils
:Synopsis:       This module is used by pytest to test core utility functions
:Created By:     Jeff Shurtliff
:Last Modified:  Jeff Shurtliff
:Modified Date:  30 Jan 2026
"""

import os
import pathlib
import warnings

import pytest

from salespyforce import errors
from salespyforce.utils import core_utils


def test_url_encode_and_decode_round_trip():
    """This function tests URL encoding and decoding helper functions.

    .. version-added:: 1.4.0
    """
    raw_string = "My sample string with spaces & symbols!"
    encoded = core_utils.url_encode(raw_string)
    assert "%26" in encoded and "+" in encoded
    decoded = core_utils.url_decode(encoded)
    assert decoded == raw_string


def test_display_warning_emits_userwarning():
    """This function tests that display_warning emits a UserWarning.

    .. version-added:: 1.4.0
    """
    warn_msg = "testing warning"
    with pytest.warns(UserWarning, match=warn_msg):
        core_utils.display_warning(warn_msg)


def test_get_file_type_detects_json_extension(tmp_path):
    """This function tests get_file_type with a JSON extension.

    .. version-added:: 1.4.0
    """
    json_path = tmp_path / "config.json"
    json_path.write_text('{"key": "value"}')
    assert core_utils.get_file_type(str(json_path)) == "json"


def test_get_file_type_detects_yaml_extension(tmp_path):
    """This function tests get_file_type with a YAML extension.

    .. version-added:: 1.4.0
    """
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text("key: value")
    assert core_utils.get_file_type(str(yaml_path)) == "yaml"


def test_get_file_type_reads_unknown_extension_with_warning(tmp_path):
    """This function tests get_file_type fallback detection on unknown extensions.

    .. version-added:: 1.4.0
    """
    txt_path = tmp_path / "config.txt"
    txt_path.write_text("# comment line\n{json: true}")
    with warnings.catch_warnings(record=True) as captured_warnings:
        file_type = core_utils.get_file_type(str(txt_path))
    assert file_type == "json"
    assert any(
        warning.category is UserWarning for warning in captured_warnings
    )


def test_get_file_type_raises_for_unknown_content(tmp_path):
    """This function tests get_file_type when content is unrecognized.

    .. version-added:: 1.4.0
    """
    bad_path = tmp_path / "config.data"
    bad_path.write_text("plain text content")
    with pytest.warns(UserWarning):
        with pytest.raises(errors.exceptions.UnknownFileTypeError):
            core_utils.get_file_type(str(bad_path))


def test_get_file_type_raises_for_missing_file():
    """This function tests get_file_type when a file is missing.

    .. version-added:: 1.4.0
    """
    missing_path = "does/not/exist.json"
    with pytest.raises(FileNotFoundError):
        core_utils.get_file_type(missing_path)


def test_get_random_string_returns_expected_length(monkeypatch):
    """This function tests get_random_string length and prefix handling.

    .. version-added:: 1.4.0
    """
    alphabet = "abc123"
    monkeypatch.setattr(core_utils, "random", core_utils.random)
    monkeypatch.setattr(
        core_utils,
        "string",
        type("DummyString", (), {"ascii_letters": alphabet, "digits": alphabet}),
    )
    result = core_utils.get_random_string(length=5, prefix_string="pre_")
    assert result.startswith("pre_")
    assert len(result) == 5 + len("pre_")
    assert all(char in alphabet for char in result.replace("pre_", ""))


def test_converts_15_char_id_to_18_char():
    """This function tests the conversion of a 15-character Salesforce ID into the 18-character equivalent.

    .. version-added:: 1.4.0
    """
    id_15 = "ka4PO0000002hby"
    id_18 = core_utils.get_18_char_id(id_15)

    assert len(id_18) == 18
    assert id_18.startswith(id_15)


def test_returns_18_char_id_unchanged():
    """This function tests that an 18-character Salesforce ID is returned unchanged during conversion attempt.

    .. version-added:: 1.4.0
    """
    id_18 = "ka4PO0000002hbyYAA"
    assert core_utils.get_18_char_id(id_18) == id_18


def test_invalid_id_length_raises_error():
    """This function tests to ensure passing an invalid Salesforce ID length raises an exception.

    .. version-added:: 1.4.0
    """
    with pytest.raises(ValueError):
        core_utils.get_18_char_id("short")


def test_non_string_id_input_raises_error():
    """This function tests to ensure passing a non-string to the get_18_char_id function raises an exception.

    .. version-added:: 1.4.0
    """
    with pytest.raises(ValueError):
        core_utils.get_18_char_id(12345)


def test_get_image_ref_id_parses_query_param():
    """This function tests get_image_ref_id parsing.

    .. version-added:: 1.4.0
    """
    image_url = (
        "https://example.force.com/servlet/servlet.ImageServer"
        "?oid=00Dxx0000001gPFEAY&refid=abc123&lastMod=123"
    )
    assert core_utils.get_image_ref_id(image_url) == "abc123"


def test_download_image_raises_without_input():
    """This function tests download_image when neither URL nor response is provided.

    .. version-added:: 1.4.0
    """
    with pytest.raises(RuntimeError):
        core_utils.download_image()


def test_download_image_raises_on_bad_status(monkeypatch, tmp_path):
    """This function tests download_image when the response is unsuccessful.

    .. version-added:: 1.4.0
    """
    class DummyResponse:
        status_code = 404
        content = b""

    monkeypatch.setattr(core_utils.requests, "get", lambda *_args, **_kwargs: DummyResponse())
    with pytest.raises(RuntimeError):
        core_utils.download_image(image_url="https://example.com/image", file_path=str(tmp_path))


def test_download_image_writes_response_content(tmp_path):
    """This function tests download_image writing provided response content.

    .. version-added:: 1.4.0
    """
    file_path = tmp_path / "images"
    os.makedirs(file_path, exist_ok=True)

    class DummyResponse:
        status_code = 200
        content = b"image-bytes"

    destination = core_utils.download_image(
        image_url="https://example.com/image",
        file_name="logo.png",
        file_path=str(file_path),
        response=DummyResponse(),
    )
    saved_path = pathlib.Path(destination)
    assert saved_path.name == "logo.png"
    assert saved_path.parent == file_path
    assert saved_path.read_bytes() == DummyResponse.content


def test_download_image_generates_file_name(monkeypatch, tmp_path):
    """This function tests download_image generates a file name when not provided.

    .. version-added:: 1.4.0
    """
    class DummyResponse:
        status_code = 200
        content = b"bytes"

    monkeypatch.setattr(core_utils, "get_random_string", lambda *_args, **_kwargs: "image_stub")
    destination = core_utils.download_image(
        image_url="https://example.com/image",
        file_path=str(tmp_path),
        response=DummyResponse(),
        extension="png",
    )
    assert destination.startswith(f"{tmp_path}{os.sep}image_stub")
    assert destination.endswith("png")
    assert pathlib.Path(destination).read_bytes() == DummyResponse.content
