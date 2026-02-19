# -*- coding: utf-8 -*-
# bandit: skip=B101
"""
:Module:         salespyforce.utils.tests.test_version_utils
:Synopsis:       Pytest suite for salespyforce.utils.version helpers
:Created By:     Jeff Shurtliff
:Last Modified:  Anonymous (via GPT-5.2-Codex)
:Modified Date:  19 Feb 2026
"""

import importlib
import importlib.metadata as importlib_metadata

from salespyforce.utils import version as version_utils


def test_get_full_version_returns_metadata(monkeypatch):
    """This function tests get_full_version returns the package metadata."""
    expected_version = "1.2.3"
    monkeypatch.setattr(
        version_utils, "version", lambda package: expected_version
    )

    assert version_utils.get_full_version() == expected_version


def test_get_full_version_handles_missing_package(monkeypatch, caplog):
    """This function tests get_full_version fallback when package is missing."""
    def raise_not_found(_package):
        raise version_utils.PackageNotFoundError("salespyforce")

    monkeypatch.setattr(version_utils, "version", raise_not_found)
    monkeypatch.setattr(version_utils, "get_version_from_pyproject", lambda: "5.4.3")

    with caplog.at_level("DEBUG"):
        version_string = version_utils.get_full_version()

    assert version_string == "5.4.3"


def test_get_major_minor_version_returns_two_components(monkeypatch):
    """This function tests extracting the major.minor version components."""
    monkeypatch.setattr(
        version_utils, "get_full_version", lambda: "2.3.4"
    )

    assert version_utils.get_major_minor_version() == "2.3"


def test_get_major_minor_version_returns_full_when_missing_minor(monkeypatch):
    """This function tests get_major_minor_version with a single-part version."""
    monkeypatch.setattr(version_utils, "get_full_version", lambda: "7")

    assert version_utils.get_major_minor_version() == "7"


def test_get_version_from_pyproject_reads_project_version(tmp_path):
    """This function tests get_version_from_pyproject with PEP 621 layout."""
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text('[project]\nversion = "3.2.1"\n', encoding="utf-8")

    assert version_utils.get_version_from_pyproject(str(pyproject_file)) == "3.2.1"


def test_get_version_from_pyproject_reads_poetry_version(tmp_path):
    """This function tests get_version_from_pyproject with Poetry layout."""
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text('[tool.poetry]\nversion = "4.5.6"\n', encoding="utf-8")

    assert version_utils.get_version_from_pyproject(str(pyproject_file)) == "4.5.6"


def test_get_version_from_pyproject_returns_default_when_missing_version(tmp_path, caplog):
    """This function tests get_version_from_pyproject fallback default value."""
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text('[project]\nname = "salespyforce"\n', encoding="utf-8")

    with caplog.at_level("WARNING"):
        version_string = version_utils.get_version_from_pyproject(str(pyproject_file))

    assert version_string == "0.0.0"
    assert any("falling back to '0.0.0'" in message for message in caplog.messages)


def test_dunder_version_matches_full_version(monkeypatch):
    """This function tests __version__ initialization uses get_full_version."""
    expected_version = "9.8.7"
    monkeypatch.setattr(
        importlib_metadata, "version", lambda package: expected_version
    )

    reloaded_module = importlib.reload(version_utils)
    assert reloaded_module.__version__ == expected_version
    assert reloaded_module.get_full_version() == expected_version
    importlib.reload(version_utils)
