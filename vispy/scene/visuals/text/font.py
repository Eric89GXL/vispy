# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

import sys

if sys.platform.startswith('linux'):
    from ._freetype import _load_glyph  # noqa
else:
    raise NotImplementedError  # XXX add other methods (Pyglet)
