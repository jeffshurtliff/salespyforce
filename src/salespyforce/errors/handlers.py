# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.errors.handlers
:Synopsis:          Functions that handle various error situations within the namespace
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     02 Feb 2026
"""

from __future__ import annotations

import sys
from typing import Final
import warnings

# Define constants
_DEFAULT_CATEGORY: Final[type[Warning]] = UserWarning


def eprint(*args, **kwargs) -> None:
    """This function behaves the same as the ``print()`` function but is leveraged to print errors to ``sys.stderr``."""
    print(*args, file=sys.stderr, **kwargs)


def get_exception_type(exc) -> str:
    """This function returns the exception type (e.g. ``RuntimeError``, ``TypeError``, etc.) for a given exception.

    .. versionadded:: 1.4.0

    :returns: The exception type as a string
    """
    return type(exc).__name__


def display_warning(
    message: str,
    *,
    category: type[Warning] = _DEFAULT_CATEGORY,
    stacklevel: int = 2,
) -> None:
    """This function emits a warning that points to the caller by default.

    .. versionadded:: 1.4.0

    :param message: Warning message to emit
    :type message: str
    :param category: Warning category class (default: ``UserWarning``)
    :type category: type[Warning]
    :param stacklevel: How far up the call stack to attribute the warning (``2`` by default - caller of this helper)
    :type stacklevel: int
    :returns: None
    """
    warnings.warn(message, category=category, stacklevel=stacklevel)
