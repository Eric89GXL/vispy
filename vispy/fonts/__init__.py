# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import sys

if sys.platform.startswith('linux'):
    from ._freetype import _load_glyph, list_fonts  # noqa
elif sys.platform == 'darwin':
    from ._quartz import _load_glyph, list_fonts  # noqa
elif sys.platform == 'win32':
    from ._win32 import _load_glyph, list_fonts  # noqa
else:
    raise NotImplementedError('unknown system %s' % sys.platform)

list_fonts.__doc__ = """List system fonts

Returns
-------
fonts : list of str
    List of system fonts.
"""
