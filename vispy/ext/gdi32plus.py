# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Adapted from Pyglet

import atexit
from ctypes import (windll, Structure, POINTER, byref, c_long, c_char, c_byte,
                    c_uint, c_float, c_int, c_ulong, c_void_p, c_uint32,
                    c_wchar_p)
from ctypes.wintypes import (LONG, BYTE, HFONT, HGDIOBJ, BOOL, INT_PTR, UINT,
                             REAL, INT)

LF_FACESIZE = 32
FW_BOLD = 700
FW_NORMAL = 400
ANTIALIASED_QUALITY = 4
FontStyleBold = 1
FontStyleItalic = 2
UnitPixel = 2
UnitPoint = 3

PixelFormat24bppRGB = 137224
PixelFormat32bppRGB = 139273
PixelFormat32bppARGB = 2498570

DriverStringOptionsCmapLookup = 1
DriverStringOptionsRealizedAdvance = 4
TextRenderingHintAntiAlias = 4
TextRenderingHintAntiAliasGridFit = 3
ImageLockModeRead = 1
StringFormatFlagsMeasureTrailingSpaces = 0x00000800
StringFormatFlagsNoClip = 0x00004000
StringFormatFlagsNoFitBlackBox = 0x00000004


# gdi32

class TEXTMETRIC(Structure):
    _fields_ = [
        ('tmHeight', c_long), ('tmAscent', c_long), ('tmDescent', c_long),
        ('tmInternalLeading', c_long), ('tmExternalLeading', c_long),
        ('tmAveCharWidth', c_long), ('tmMaxCharWidth', c_long),
        ('tmWeight', c_long), ('tmOverhang', c_long),
        ('tmDigitizedAspectX', c_long), ('tmDigitizedAspectY', c_long),
        ('tmFirstChar', c_char), ('tmLastChar', c_char),
        ('tmDefaultChar', c_char), ('tmBreakChar', c_char),
        ('tmItalic', c_byte), ('tmUnderlined', c_byte),
        ('tmStruckOut', c_byte), ('tmPitchAndFamily', c_byte),
        ('tmCharSet', c_byte)]
    __slots__ = [f[0] for f in _fields_]


class LOGFONT(Structure):
    _fields_ = [
        ('lfHeight', LONG), ('lfWidth', LONG), ('lfEscapement', LONG),
        ('lfOrientation', LONG), ('lfWeight', LONG), ('lfItalic', BYTE),
        ('lfUnderline', BYTE), ('lfStrikeOut', BYTE), ('lfCharSet', BYTE),
        ('lfOutPrecision', BYTE), ('lfClipPrecision', BYTE),
        ('lfQuality', BYTE), ('lfPitchAndFamily', BYTE),
        ('lfFaceName', (c_char * LF_FACESIZE))]


class Rectf(Structure):
    _fields_ = [('x', c_float), ('y', c_float),
                ('width', c_float), ('height', c_float)]


gdi32 = windll.gdi32
gdi32.CreateFontIndirectA.restype = HFONT
gdi32.CreateFontIndirectA.argtypes = [POINTER(LOGFONT)]
gdi32.SelectObject.restype = HGDIOBJ
gdi32.SelectObject.argtypes = [c_void_p, HGDIOBJ]  # HDC
gdi32.GetTextMetricsA.restype = BOOL
gdi32.GetTextMetricsA.argtypes = [c_void_p, POINTER(TEXTMETRIC)]  # HDC


# gdiplus

class Rect(Structure):
    _fields_ = [('X', c_int), ('Y', c_int),
                ('Width', c_int), ('Height', c_int)]


class BitmapData(Structure):
    _fields_ = [('Width', c_uint), ('Height', c_uint), ('Stride', c_int),
                ('PixelFormat', c_int), ('Scan0', POINTER(c_byte)),
                ('Reserved', POINTER(c_uint))]


class GdiplusStartupInput(Structure):
    _fields_ = [
        ('GdiplusVersion', c_uint32), ('DebugEventCallback', c_void_p),
        ('SuppressBackgroundThread', BOOL), ('SuppressExternalCodecs', BOOL)]


class GdiplusStartupOutput(Structure):
    _fields = [('NotificationHookProc', c_void_p),
               ('NotificationUnhookProc', c_void_p)]

gdiplus = windll.gdiplus

gdiplus.GdipCreateBitmapFromScan0.restype = c_int
gdiplus.GdipCreateBitmapFromScan0.argtypes = [c_int, c_int, c_int, c_int,
                                              POINTER(BYTE), c_void_p]
gdiplus.GdipGetImageGraphicsContext.restype = c_int
gdiplus.GdipGetImageGraphicsContext.argtypes = [c_void_p, c_void_p]
gdiplus.GdipSetPageUnit.restype = c_int
gdiplus.GdipSetPageUnit.argtypes = [c_void_p, c_int]
gdiplus.GdipSetTextRenderingHint.restype = c_int
gdiplus.GdipSetTextRenderingHint.argtypes = [c_void_p, c_int]
gdiplus.GdipCreateSolidFill.restype = c_int
gdiplus.GdipCreateSolidFill.argtypes = [c_int, c_void_p]  # ARGB
gdiplus.GdipCreateMatrix.restype = None
gdiplus.GdipCreateMatrix.argtypes = [c_void_p]
gdiplus.GdipStringFormatGetGenericTypographic.restype = c_int
gdiplus.GdipStringFormatGetGenericTypographic.argtypes = [c_void_p]
gdiplus.GdipCloneStringFormat.restype = c_int
gdiplus.GdipCloneStringFormat.argtypes = [c_void_p, c_void_p]
gdiplus.GdipSetStringFormatFlags.restype = c_int
gdiplus.GdipSetStringFormatFlags.argtypes = [c_void_p, c_int]
gdiplus.GdipMeasureString.restype = c_int
gdiplus.GdipMeasureString.argtypes = [c_void_p, c_wchar_p, c_int, c_void_p,
                                      c_void_p, c_void_p, c_void_p, INT_PTR,
                                      INT_PTR]
gdiplus.GdipGraphicsClear.restype = c_int
gdiplus.GdipGraphicsClear.argtypes = [c_void_p, c_int]  # ARGB
gdiplus.GdipDrawString.restype = c_int
gdiplus.GdipDrawString.argtypes = [c_void_p, c_wchar_p, c_int, c_void_p,
                                   c_void_p, c_void_p, c_void_p]
gdiplus.GdipFlush.restype = c_int
gdiplus.GdipFlush.argtypes = [c_void_p, c_int]
gdiplus.GdipBitmapLockBits.restype = c_int
gdiplus.GdipBitmapLockBits.argtypes = [c_void_p, c_void_p, UINT, c_int,
                                       c_void_p]
gdiplus.GdipBitmapUnlockBits.restype = c_int
gdiplus.GdipBitmapUnlockBits.argtypes = [c_void_p, c_void_p]
gdiplus.GdipCreateFontFamilyFromName.restype = c_int
gdiplus.GdipCreateFontFamilyFromName.argtypes = [c_wchar_p, c_void_p, c_void_p]
gdiplus.GdipCreateFont.restype = c_int
gdiplus.GdipCreateFont.argtypes = [c_void_p, REAL, INT, c_int, c_void_p]


def gdiplus_init():
    token = c_ulong()
    startup_in = GdiplusStartupInput()
    startup_in.GdiplusVersion = 1
    startup_out = GdiplusStartupOutput()
    gdiplus.GdiplusStartup(byref(token), byref(startup_in), byref(startup_out))
    atexit.register(gdiplus.GdiplusShutdown(token))

gdiplus_init()


# user32

user32 = windll.user32

user32.GetDC.restype = c_void_p  # HDC
user32.GetDC.argtypes = [c_uint32]  # HWND
