# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Use freetype to get glyph bitmaps

import sys
import numpy as np

from ..ext.freetype import (FT_LOAD_RENDER, FT_LOAD_FORCE_AUTOHINT,
                            FT_LOAD_TARGET_LIGHT, Face, Vector, Matrix)


# Convert face to filename
if sys.platform.startswith('linux'):
    from ..ext.fontconfig import find_font
elif sys.platform.startswith('win'):
    from ._win32 import find_font  # noqa, analysis:ignore
else:
    raise NotImplementedError

_font_dict = {}


def _load_font(face, size, bold, italic):
    key = '%s-%s-%s-%s' % (face, size, bold, italic)
    if key in _font_dict:
        return _font_dict[key]
    fname = find_font(face, size, bold, italic)
    font = Face(fname)
    _font_dict[key] = font
    return font


def _load_glyph(f, char, glyphs_dict):
    """Load glyph from font into dict"""
    freetype_flags = (FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT |
                      FT_LOAD_TARGET_LIGHT)
    face = _load_font(f['face'], f['size'], f['bold'], f['italic'])
    pen = Vector(0, 0)
    hres = 64
    face.set_char_size(int(f['size'] * 64), 0, hres*f['dpi'], f['dpi'])
    # 1024 == int((1./64.) * 0x10000L), 65536 = int(1. * 0x10000L)
    matrix = Matrix(1024, 0, 0, 65536)
    face.set_transform(matrix, pen)
    # actually get the character of interest
    face.load_char(char, freetype_flags)
    bitmap = face.glyph.bitmap
    left = face.glyph.bitmap_left
    top = face.glyph.bitmap_top
    width = face.glyph.bitmap.width
    height = face.glyph.bitmap.rows
    advance = int(round(face.glyph.advance.x / 64.))
    # reshape bitmap
    bitmap = np.array(bitmap.buffer)
    w0 = bitmap.size // height if bitmap.size > 0 else 0
    bitmap.shape = (height, w0)
    bitmap = (bitmap[:, :width].astype(np.ubyte))
    #bitmap = bitmap.reshape(height, width // 3, 3)  # For LCD rendering
    bitmap.shape = (height, width, 1)
    bitmap = np.repeat(bitmap, 3, axis=-1)
    glyph = dict(char=char, offset=(left, top), bitmap=bitmap,
                 advance=advance, kerning={})
    glyphs_dict[char] = glyph
    # Generate kerning
    for other_char, other_glyph in glyphs_dict.items():
        # 64 * 64 because of 26.6 encoding AND the transform matrix
        # used in texture_font_load_face (hres = 64)
        kerning = face.get_kerning(other_char, char)
        glyph['kerning'][other_char] = kerning.x / (64.0*hres)
        kerning = face.get_kerning(char, other_char)
        other_glyph['kerning'][char] = kerning.x / (64.0*hres)
