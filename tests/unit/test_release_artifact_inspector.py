# -*- coding: utf-8 -*-
"""
:Module:            test_release_artifact_inspector
:Synopsis:          Tests the SalesPyForce release artifact inspector
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff (via GPT-5.6-sol)
:Modified Date:     30 Aug 2026
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from types import ModuleType


def load_inspector() -> ModuleType:
    """Load the repository skill's artifact inspector as a module."""
    repository_root = Path(__file__).resolve().parents[2]
    script_path = repository_root / '.agents/skills/salespyforce-stable-release-prep/scripts/inspect_release_artifacts.py'
    module = ModuleType('salespyforce_release_artifact_inspector')
    module.__file__ = str(script_path)
    exec(compile(script_path.read_text(encoding='utf-8'), str(script_path), 'exec'), module.__dict__)
    return module


def test_inspect_wheel_warns_about_nested_package_tests(tmp_path: Path) -> None:
    """Reject test content nested below the import package in strict runs."""
    inspector = load_inspector()
    wheel_path = tmp_path / 'salespyforce-2.0.0-py3-none-any.whl'
    with zipfile.ZipFile(wheel_path, mode='w') as archive:
        archive.writestr('salespyforce/__init__.py', '')
        archive.writestr('salespyforce/tests/test_embedded.py', '')
        archive.writestr('salespyforce-2.0.0.dist-info/METADATA', 'Name: salespyforce\nVersion: 2.0.0\n')

    errors, warnings = inspector.inspect_wheel(wheel_path, 'salespyforce', '2.0.0')

    assert errors == []
    assert warnings == [f'{wheel_path.name}: test content included: salespyforce/tests/test_embedded.py']


def test_wheel_metadata_paths_are_not_treated_as_test_content() -> None:
    """Ignore test-like path components within wheel metadata directories."""
    inspector = load_inspector()

    assert inspector.wheel_test_members(['salespyforce-2.0.0.dist-info/tests/metadata.json']) == []
