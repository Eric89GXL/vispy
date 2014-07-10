# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Adapted from Pyglet

# Use Win32 calls to get glyph bitmaps

import numpy as np
import warnings


from ctypes import (create_string_buffer, create_unicode_buffer,
                    byref, memmove, c_byte, c_float, c_void_p, c_wchar_p)

from ..ext.gdi32plus import (gdiplus, gdi32, user32,
                             LOGFONT, TEXTMETRIC, FW_BOLD, FW_NORMAL,
                             ANTIALIASED_QUALITY, FontStyleBold,
                             FontStyleItalic, UnitPixel, Rectf,
                             TextRenderingHintAntiAliasGridFit,
                             StringFormatFlagsMeasureTrailingSpaces,
                             StringFormatFlagsNoClip, ImageLockModeRead,
                             StringFormatFlagsNoFitBlackBox,
                             PixelFormat24bppRGB, Rect, BitmapData)
# Changed pixel format, used 3 * instead of 4 *


def _load_glyph(f, char, glyph_dict):
    """Load glyph from font into dict"""
    _gdipfont, hfont, width, height = _load_font(**f)

    # Pessimistically round up width and height to 4 byte alignment
    width = (width | 0x3) + 1
    height = (height | 0x3) + 1
    _data = (c_byte * (3 * width * height))()
    _bitmap = c_void_p()
    _format = PixelFormat24bppRGB
    gdiplus.GdipCreateBitmapFromScan0(width, height, width * 3,
                                      _format, _data, byref(_bitmap))
    _graphics = c_void_p()
    gdiplus.GdipGetImageGraphicsContext(_bitmap, byref(_graphics))
    gdiplus.GdipSetPageUnit(_graphics, UnitPixel)
    _dc = user32.GetDC(0)
    gdi32.SelectObject(_dc, hfont)
    gdiplus.GdipSetTextRenderingHint(_graphics,
                                     TextRenderingHintAntiAliasGridFit)
    _brush = c_void_p()
    gdiplus.GdipCreateSolidFill(0xffffffff, byref(_brush))
    _matrix = c_void_p()
    gdiplus.GdipCreateMatrix(byref(_matrix))
    #_flags = (DriverStringOptionsCmapLookup |
    #          DriverStringOptionsRealizedAdvance)
    _rect = Rect(0, 0, width, height)
    _bitmap_height = height
    gdi32.SelectObject(_dc, hfont)
    ch = create_unicode_buffer(char)

    # Layout rectangle; not clipped against so not terribly important.
    width = 10000
    height = _bitmap_height
    rect = Rectf(0, _bitmap_height - height, width, height)

    # Set up GenericTypographic with 1 character measure range
    generic = c_void_p()
    gdiplus.GdipStringFormatGetGenericTypographic(byref(generic))
    format = c_void_p()
    gdiplus.GdipCloneStringFormat(generic, byref(format))

    # Measure advance
    bbox = Rectf()
    flags = (StringFormatFlagsMeasureTrailingSpaces |
             StringFormatFlagsNoClip |
             StringFormatFlagsNoFitBlackBox)
    gdiplus.GdipSetStringFormatFlags(format, flags)
    gdiplus.GdipMeasureString(_graphics, ch, 1, _gdipfont, byref(rect), format,
                              byref(bbox), None, None)
    # lsb = 0
    advance = int(np.ceil(bbox.width))
    width = advance
    if f['italic']:
        width += width // 2
    gdiplus.GdipGraphicsClear(_graphics, 0x00000000)
    gdiplus.GdipDrawString(_graphics, ch, 1, _gdipfont, byref(rect), format,
                           _brush)
    gdiplus.GdipFlush(_graphics, 1)

    bitmap_data = BitmapData()
    gdiplus.GdipBitmapLockBits(_bitmap, byref(_rect),
                               ImageLockModeRead, _format,
                               byref(bitmap_data))
    buffer = create_string_buffer(
        bitmap_data.Stride * bitmap_data.Height)
    memmove(buffer, bitmap_data.Scan0, len(buffer))
    gdiplus.GdipBitmapUnlockBits(_bitmap, byref(bitmap_data))
    bitmap = np.array(buffer)  # BGRA
    bitmap.shape = (height, width, 3)
    bitmap = bitmap[:, :, [2, 1, 0]]
    return bitmap


def _get_logfont(name, size, bold, italic, dpi):
    # # Create a dummy DC for coordinate mapping
    dc = user32.GetDC(0)  # noqa, analysis:ignore
    logpixelsy = dpi
    logfont = LOGFONT()
    # Conversion of point size to device pixels
    logfont.lfHeight = int(-size * logpixelsy // 72)
    logfont.lfWeight = FW_BOLD if bold else FW_NORMAL
    logfont.lfItalic = italic
    logfont.lfFaceName = name.encode('ASCII')
    logfont.lfQuality = ANTIALIASED_QUALITY
    return logfont


def _load_font(face, size, bold, italic, dpi):
    fallback_face = 'Arial'
    logfont = _get_logfont(face, size, bold, italic, dpi)
    hfont = gdi32.CreateFontIndirectA(byref(logfont))
    dc = user32.GetDC(0)
    metrics = TEXTMETRIC()
    gdi32.SelectObject(dc, hfont)
    gdi32.GetTextMetricsA(dc, byref(metrics))
    ascent = metrics.tmAscent
    descent = -metrics.tmDescent
    max_glyph_width = metrics.tmMaxCharWidth
    family = c_void_p()
    gdiplus.GdipCreateFontFamilyFromName(c_wchar_p(face), None,
                                         byref(family))
    if not family:
        gdiplus.GdipCreateFontFamilyFromName(c_wchar_p(fallback_face),
                                             None, byref(family))
        warnings.warn('Could not find face match "%s", falling back to "%s"'
                      % (face, fallback_face))
    unit = UnitPixel
    size = (size * dpi) // 72
    style = 0
    style |= FontStyleBold if bold else 0
    style |= FontStyleItalic if italic else 0
    _gdipfont = c_void_p()
    gdiplus.GdipCreateFont(family, c_float(size),
                           style, unit, byref(_gdipfont))
    width = max_glyph_width
    height = ascent - descent
    return _gdipfont, hfont, width, height


def list_fonts():
    # http://www.gdiplus.ru/gdiplus/gdiplusreference/flatfontfamily.htm
    # width = 100
    # height = 100
    # _data = (c_byte * (3 * width * height))()
    # _bitmap = c_void_p()
    # _format = PixelFormat24bppRGB
    # gdiplus.GdipCreateBitmapFromScan0(width, height, width * 3,
    #                                   _format, _data, byref(_bitmap))
    # _graphics = c_void_p()
    # gdiplus.GdipGetImageGraphicsContext(_bitmap, byref(_graphics))
    # n_found = INT()
    # gdiplus.GdipFontCollectionEnumerable(_collection, _graphics,
    #                                      byref(n_found))
    # GdipFontCollectionEnumerate
    raise NotImplementedError('font name enumeration not supported on windows')
