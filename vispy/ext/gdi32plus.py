# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Adapted from Pyglet

import atexit
from functools import partial
import struct

from ctypes import (windll, Structure, POINTER, byref, WINFUNCTYPE, cast,
                    c_uint, c_float, c_int, c_ulong, c_uint64, c_short,
                    c_void_p, c_uint32, c_wchar, c_wchar_p, c_char_p)
from ctypes.wintypes import (LONG, BYTE, HFONT, HGDIOBJ, BOOL, UINT, INT,
                             DWORD, LPARAM, WPARAM, HMONITOR, HINSTANCE,
                             HICON, HBRUSH, HANDLE, HWND, WORD, HMODULE,
                             ATOM, LPVOID, HMENU, LPPOINT)

try:
    import _winreg as winreg
except ImportError:
    import winreg  # noqa, analysis:ignore

_64_bit = (8 * struct.calcsize("P")) == 64

LF_FACESIZE = 32
FW_BOLD = 700
FW_NORMAL = 400
ANTIALIASED_QUALITY = 4
FontStyleBold = 1
FontStyleItalic = 2
UnitPixel = 2
UnitPoint = 3
DEFAULT_CHARSET = 1
ANSI_CHARSET = 0
TRUETYPE_FONTTYPE = 4
GM_ADVANCED = 2
CSIDL_FONTS = 0x0014

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

INT_PTR = c_int
REAL = c_float
TCHAR = c_wchar
UINT32 = c_uint32
HDC = c_void_p
PSTR = c_uint64 if _64_bit else c_uint
LRESULT = LPARAM
HCURSOR = HANDLE
WCHAR = BCHAR = c_wchar
CCHDEVICENAME = 32
CCHFORMNAME = 32

HORZSIZE = 4
VERTSIZE = 6

HORZRES = 8
VERTRES = 10


# gdi32

def MAKEINTRESOURCE(i):
    return cast(c_void_p(i & 0xFFFF), c_wchar_p)


class POINT(Structure):
    _fields_ = [('x', LONG), ('y', LONG)]


class RECT(Structure):
    _fields_ = [('left', LONG), ('top', LONG),
                ('right', LONG), ('bottom', LONG)]

LPRECT = POINTER(RECT)


class PANOSE(Structure):
    _fields_ = [
        ('bFamilyType', BYTE), ('bSerifStyle', BYTE), ('bWeight', BYTE),
        ('bProportion', BYTE), ('bContrast', BYTE), ('bStrokeVariation', BYTE),
        ('bArmStyle', BYTE), ('bLetterform', BYTE), ('bMidline', BYTE),
        ('bXHeight', BYTE)]


class TEXTMETRIC(Structure):
    _fields_ = [
        ('tmHeight', LONG), ('tmAscent', LONG), ('tmDescent', LONG),
        ('tmInternalLeading', LONG), ('tmExternalLeading', LONG),
        ('tmAveCharWidth', LONG), ('tmMaxCharWidth', LONG),
        ('tmWeight', LONG), ('tmOverhang', LONG),
        ('tmDigitizedAspectX', LONG), ('tmDigitizedAspectY', LONG),
        ('tmFirstChar', TCHAR), ('tmLastChar', TCHAR),
        ('tmDefaultChar', TCHAR), ('tmBreakChar', TCHAR),
        ('tmItalic', BYTE), ('tmUnderlined', BYTE),
        ('tmStruckOut', BYTE), ('tmPitchAndFamily', BYTE),
        ('tmCharSet', BYTE)]


class OUTLINETEXTMETRIC(Structure):
    _fields_ = [
        ('otmSize', UINT), ('otmTextMetrics', TEXTMETRIC),
        ('otmMysteryBytes', BYTE), ('otmPanoseNumber', PANOSE),
        ('otmMysteryByte', BYTE),
        ('otmfsSelection', UINT), ('otmfsType', UINT),
        ('otmsCharSlopeRise', INT), ('otmsCharSlopeRun', INT),
        ('otmItalicAngle', INT), ('otmEMSquare', UINT), ('otmAscent', INT),
        ('otmDescent', INT), ('otmLineGap', UINT), ('otmsCapEmHeight', UINT),
        ('otmsXHeight', UINT), ('otmrcFontBox', RECT), ('otmMacAscent', INT),
        ('otmMacDescent', INT), ('otmMacLineGap', UINT),
        ('otmusMinimumPPEM', UINT), ('otmptSubscriptSize', POINT),
        ('otmptSubscriptOffset', POINT), ('otmptSuperscriptSize', POINT),
        ('otmptSuperscriptOffset', POINT), ('otmsStrikeoutSize', UINT),
        ('otmsStrikeoutPosition', INT), ('otmsUnderscoreSize', INT),
        ('otmsUnderscorePosition', INT), ('otmpFamilyName', PSTR),
        ('otmpFaceName', PSTR), ('otmpStyleName', PSTR),
        ('otmpFullName', PSTR), ('junk', (BYTE) * 1024)]  # room for strs


class LOGFONT(Structure):
    _fields_ = [
        ('lfHeight', LONG), ('lfWidth', LONG), ('lfEscapement', LONG),
        ('lfOrientation', LONG), ('lfWeight', LONG), ('lfItalic', BYTE),
        ('lfUnderline', BYTE), ('lfStrikeOut', BYTE), ('lfCharSet', BYTE),
        ('lfOutPrecision', BYTE), ('lfClipPrecision', BYTE),
        ('lfQuality', BYTE), ('lfPitchAndFamily', BYTE),
        ('lfFaceName', (TCHAR * LF_FACESIZE))]


class MONITORINFOEX(Structure):
    _fields_ = [
        ('cbSize', DWORD),
        ('rcMonitor', RECT),
        ('rcWork', RECT),
        ('dwFlags', DWORD),
        ('szDevice', WCHAR * CCHDEVICENAME)
    ]
    __slots__ = [f[0] for f in _fields_]


class DEVMODE(Structure):
    _fields_ = [
        ('dmDeviceName', BCHAR * CCHDEVICENAME),
        ('dmSpecVersion', WORD),
        ('dmDriverVersion', WORD),
        ('dmSize', WORD),
        ('dmDriverExtra', WORD),
        ('dmFields', DWORD),
        # Just using largest union member here
        ('dmOrientation', c_short),
        ('dmPaperSize', c_short),
        ('dmPaperLength', c_short),
        ('dmPaperWidth', c_short),
        ('dmScale', c_short),
        ('dmCopies', c_short),
        ('dmDefaultSource', c_short),
        ('dmPrintQuality', c_short),
        # End union
        ('dmColor', c_short),
        ('dmDuplex', c_short),
        ('dmYResolution', c_short),
        ('dmTTOption', c_short),
        ('dmCollate', c_short),
        ('dmFormName', BCHAR * CCHFORMNAME),
        ('dmLogPixels', WORD),
        ('dmBitsPerPel', DWORD),
        ('dmPelsWidth', DWORD),
        ('dmPelsHeight', DWORD),
        ('dmDisplayFlags', DWORD),  # union with dmNup
        ('dmDisplayFrequency', DWORD),
        ('dmICMMethod', DWORD),
        ('dmICMIntent', DWORD),
        ('dmDitherType', DWORD),
        ('dmReserved1', DWORD),
        ('dmReserved2', DWORD),
        ('dmPanningWidth', DWORD),
        ('dmPanningHeight', DWORD),
    ]


class PIXELFORMATDESCRIPTOR(Structure):
    _fields_ = [
        ('nSize', WORD),
        ('nVersion', WORD),
        ('dwFlags', DWORD),
        ('iPixelType', BYTE),
        ('cColorBits', BYTE),
        ('cRedBits', BYTE),
        ('cRedShift', BYTE),
        ('cGreenBits', BYTE),
        ('cGreenShift', BYTE),
        ('cBlueBits', BYTE),
        ('cBlueShift', BYTE),
        ('cAlphaBits', BYTE),
        ('cAlphaShift', BYTE),
        ('cAccumBits', BYTE),
        ('cAccumRedBits', BYTE),
        ('cAccumGreenBits', BYTE),
        ('cAccumBlueBits', BYTE),
        ('cAccumAlphaBits', BYTE),
        ('cDepthBits', BYTE),
        ('cStencilBits', BYTE),
        ('cAuxBuffers', BYTE),
        ('iLayerType', BYTE),
        ('bReserved', BYTE),
        ('dwLayerMask', DWORD),
        ('dwVisibleMask', DWORD),
        ('dwDamageMask', DWORD)
    ]

WNDPROC = WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)
MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, LPRECT, LPARAM)


class WNDCLASS(Structure):
    _fields_ = [
        ('style', UINT),
        ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', c_int),
        ('cbWndExtra', c_int),
        ('hInstance', HINSTANCE),
        ('hIcon', HICON),
        ('hCursor', HCURSOR),
        ('hbrBackground', HBRUSH),
        ('lpszMenuName', c_char_p),
        ('lpszClassName', c_wchar_p)
    ]

FONTENUMPROC = WINFUNCTYPE(INT, POINTER(LOGFONT), POINTER(TEXTMETRIC),
                           DWORD, c_void_p)


gdi32 = windll.gdi32
gdi32.ChoosePixelFormat.restype = c_int
gdi32.ChoosePixelFormat.argtypes = [HDC, POINTER(PIXELFORMATDESCRIPTOR)]
gdi32.CreateFontIndirectW.restype = HFONT
gdi32.CreateFontIndirectW.argtypes = [POINTER(LOGFONT)]
gdi32.EnumFontFamiliesExW.restype = INT
gdi32.EnumFontFamiliesExW.argtypes = [HDC, POINTER(LOGFONT),
                                      FONTENUMPROC, LPARAM, DWORD]
gdi32.GetDeviceCaps.argtypes = [HDC, INT]
gdi32.GetDeviceCaps.restype = INT
gdi32.GetOutlineTextMetricsW.restype = UINT
gdi32.GetOutlineTextMetricsW.argtypes = [HDC, UINT,
                                         POINTER(OUTLINETEXTMETRIC)]
gdi32.GetTextMetricsW.restype = BOOL
gdi32.GetTextMetricsW.argtypes = [HDC, POINTER(TEXTMETRIC)]
gdi32.GetStockObject.restype = HGDIOBJ
gdi32.GetStockObject.argtypes = [c_int]
gdi32.SelectObject.restype = HGDIOBJ
gdi32.SelectObject.argtypes = [HDC, HGDIOBJ]
gdi32.SetGraphicsMode.restype = INT
gdi32.SetGraphicsMode.argtypes = [HDC, INT]
gdi32.SetPixelFormat.restype = BOOL
gdi32.SetPixelFormat.argtypes = [HDC, c_int, POINTER(PIXELFORMATDESCRIPTOR)]


kernel32 = windll.kernel32
kernel32.GetModuleHandleW.restype = HMODULE
kernel32.GetModuleHandleW.argtypes = [c_wchar_p]

user32 = windll.user32
user32.AdjustWindowRectEx.restype = BOOL
user32.AdjustWindowRectEx.argtypes = [LPRECT, DWORD, BOOL, DWORD]
user32.ClientToScreen.restype = BOOL
user32.ClientToScreen.argtypes = [HWND, LPPOINT]
user32.CreateWindowExW.restype = HWND
user32.CreateWindowExW.argtypes = [DWORD, c_wchar_p, c_wchar_p, DWORD, c_int,
                                   c_int, c_int, c_int, HWND, HMENU, HINSTANCE,
                                   LPVOID]
user32.DefWindowProcW.restype = LRESULT
user32.DefWindowProcW.argtypes = [HWND, UINT, WPARAM, LPARAM]
user32.DestroyWindow.restype = BOOL
user32.DestroyWindow.argtypes = [HWND]
user32.GetClientRect.restype = BOOL
user32.GetClientRect.argtypes = [HWND, LPRECT]
user32.GetDC.restype = HDC
user32.GetDC.argtypes = [HWND]
user32.GetMonitorInfoW.restype = BOOL
user32.GetMonitorInfoW.argtypes = [HMONITOR, POINTER(MONITORINFOEX)]
user32.GetWindowTextW.restype = INT
user32.GetWindowTextW.argtypes = [HWND, c_wchar_p, INT]
user32.EnumDisplayMonitors.restype = BOOL
user32.EnumDisplayMonitors.argtypes = [HDC, LPRECT, MONITORENUMPROC, LPARAM]
user32.EnumDisplaySettingsW.restype = BOOL
user32.EnumDisplaySettingsW.argtypes = [c_wchar_p, DWORD, POINTER(DEVMODE)]
user32.InvalidateRect.restype = BOOL
user32.InvalidateRect.argtypes = [HWND, LPRECT, BOOL]
user32.IsWindowVisible.restype = BOOL
user32.IsWindowVisible.argtypes = [HWND]
user32.LoadIconW.restype = HICON
user32.LoadIconW.argtypes = [HINSTANCE, c_wchar_p]
user32.RegisterClassW.restype = ATOM
user32.RegisterClassW.argtypes = [POINTER(WNDCLASS)]
user32.ReleaseDC.argtypes = [c_void_p, HDC]
user32.SetProcessDPIAware.argtypes = []
user32.SetWindowPos.restype = BOOL
user32.SetWindowPos.argtypes = [HWND, HWND, c_int, c_int, c_int, c_int, UINT]
user32.SetWindowTextW.restype = BOOL
user32.SetWindowTextW.argtypes = [HWND, c_wchar_p]
user32.ShowWindow.restype = BOOL
user32.ShowWindow.argtypes = [HWND, c_int]
user32.UnregisterClassW.restype = BOOL
user32.UnregisterClassW.argtypes = [c_wchar_p, HINSTANCE]


# gdiplus

class GdiplusStartupInput(Structure):
    _fields_ = [
        ('GdiplusVersion', UINT32), ('DebugEventCallback', c_void_p),
        ('SuppressBackgroundThread', BOOL), ('SuppressExternalCodecs', BOOL)]


class GdiplusStartupOutput(Structure):
    _fields = [('NotificationHookProc', c_void_p),
               ('NotificationUnhookProc', c_void_p)]

gdiplus = windll.gdiplus
gdiplus.GdipCreateFontFamilyFromName.restype = c_int
gdiplus.GdipCreateFontFamilyFromName.argtypes = [c_wchar_p, c_void_p, c_void_p]
gdiplus.GdipNewPrivateFontCollection.restype = c_int
gdiplus.GdipNewPrivateFontCollection.argtypes = [c_void_p]
gdiplus.GdipPrivateAddFontFile.restype = c_int
gdiplus.GdipPrivateAddFontFile.argtypes = [c_void_p, c_wchar_p]
gdiplus.GdipGetFamilyName.restype = c_int
gdiplus.GdipGetFamilyName.argtypes = [c_void_p, c_wchar_p, c_int]


def gdiplus_init():
    token = c_ulong()
    startup_in = GdiplusStartupInput()
    startup_in.GdiplusVersion = 1
    startup_out = GdiplusStartupOutput()
    gdiplus.GdiplusStartup(byref(token), byref(startup_in), byref(startup_out))
    atexit.register(partial(gdiplus.GdiplusShutdown, token))

gdiplus_init()
