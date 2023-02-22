# -*- coding: utf-8 -*-
"""
:Module:            salespyforce.errors.handlers
:Synopsis:          Functions that handle various error situations within the namespace
:Created By:        Jeff Shurtliff
:Last Modified:     Jeff Shurtliff
:Modified Date:     22 Feb 2023
"""

import sys


def eprint(*args, **kwargs):
    """This function behaves the same as the ``print()`` function but is leveraged to print errors to ``sys.stderr``."""
    print(*args, file=sys.stderr, **kwargs)
