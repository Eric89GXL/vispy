# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Use freetype to get glyph bitmaps

from ....ext.freetype import (FT_LOAD_RENDER, FT_LOAD_FORCE_AUTOHINT,
                              FT_LOAD_TARGET_LCD, Face, Vector, Matrix)
from ....ext.fontconfig import find_font


def _load_glyph(f, char, glyphs_dict):
    """Load glyph from font into dict"""
    freetype_flags = (FT_LOAD_RENDER | FT_LOAD_FORCE_AUTOHINT |
                      FT_LOAD_TARGET_LCD)
    fname = find_font(f['face'], f['size'], f['bold'], f['italic'])
    face = Face(fname)
    pen = Vector(0, 0)
    hres = 64
    face.set_char_size(int(f['size'] * 64), 0, hres*72, 72)
    # 1024 == int((1./64.) * 0x10000L), 65536 = int(1. * 0x10000L)
    matrix = Matrix(1024, 0, 0, 65536)
    face.set_transform(matrix, pen)
    # actually get the character of interest
    face.load_char(char, freetype_flags)
    bitmap = face.glyph.bitmap
    left = face.glyph.bitmap_left
    top = face.glyph.bitmap_top
    width = face.glyph.bitmap.width
    rows = face.glyph.bitmap.rows
    pitch = face.glyph.bitmap.pitch
    advance = (face.glyph.advance.x, face.glyph.advance.y)
    glyph = dict(char=char, offset=(left, top), bitmap=bitmap.buffer,
                 width=width, rows=rows, pitch=pitch,
                 advance=advance, kerning={})
    glyphs_dict[char] = glyph
    # Generate kerning
    for other_char, other_glyph in glyphs_dict.items():
        # 64 * 64 because of 26.6 encoding AND the transform matrix
        # used in texture_font_load_face (hres = 64)
        kerning = face.get_kerning(other_char, char)
        if kerning.x != 0:
            glyph['kerning'][other_char] = kerning.x / (64.0*hres)
        kerning = face.get_kerning(char, other_char)
        if kerning.x != 0:
            other_glyph['kerning'][char] = kerning.x / (64.0*hres)
