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
                    CFUNCTYPE, c_uint, c_float, c_int, c_ulong, c_uint64,
                    c_short, c_void_p, c_uint32, c_wchar, c_wchar_p, c_char_p)
from ctypes.wintypes import (LONG, BYTE, HFONT, HGDIOBJ, BOOL, UINT, INT,
                             DWORD, LPARAM, WPARAM, HMONITOR, HINSTANCE,
                             HICON, HBRUSH, HANDLE, HWND, WORD, HMODULE,
                             ATOM, LPVOID, HMENU, LPPOINT, MSG)

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

WM_KEYDOWN = 256
WM_KEYUP = 257
WM_CHAR = 258
WM_SYSKEYDOWN = 260
WM_SYSKEYUP = 261
WM_MOUSEMOVE = 512
WM_LBUTTONDOWN = 513
WM_LBUTTONUP = 514
WM_RBUTTONDOWN = 516
WM_RBUTTONUP = 517
WM_MBUTTONDOWN = 519
WM_MBUTTONUP = 520
WM_MOUSEWHEEL = 522
WM_MOUSELEAVE = 675
WM_PAINT = 15
WM_CLOSE = 16
WM_SIZING = 532
WM_MOVING = 534
WM_SYSCOMMAND = 274
WM_MOVE = 3
WM_SIZE = 5
WM_EXITSIZEMOVE = 562
WM_SETFOCUS = 7
WM_KILLFOCUS = 8
WM_GETMINMAXINFO = 36
WM_ERASEBKGND = 20

WS_CHILD = 1073741824
WS_VISIBLE = 268435456
WS_POPUP = -2147483648
WS_OVERLAPPED = 0
WS_MAXIMIZE = 16777216
WS_MINIMIZE = 536870912
WS_CAPTION = 12582912
WS_SYSMENU = 524288
WS_THICKFRAME = 262144
WS_MAXIMIZEBOX = 65536
WS_MINIMIZEBOX = 131072
WS_OVERLAPPEDWINDOW = (WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_THICKFRAME
                       | WS_MINIMIZEBOX | WS_MAXIMIZEBOX)
WS_EX_DLGMODALFRAME = 1
WS_EX_TOOLWINDOW = 128

WM_CLOSE = 16

VK_SHIFT = 16
VK_CONTROL = 17
VK_MENU = 18
VK_LWIN = 91
MAPVK_VK_TO_CHAR = 2

WHEEL_DELTA = 120

ENUM_CURRENT_SETTINGS = -1

SW_HIDE = 0
SW_MAXIMIZE = 3
SW_MINIMIZE = 6
WHITE_BRUSH = 0
BLACK_BRUSH = 4

CS_VREDRAW = 1
CS_HREDRAW = 2

CW_USEDEFAULT = -2147483648

GWL_STYLE = -16
GWL_EXSTYLE = -20

HWND_TOP = 0
HWND_TOPMOST = -1
HWND_NOTOPMOST = -2

SWP_FRAMECHANGED = 32
SWP_NOSIZE = 1
SWP_NOMOVE = 2
SWP_NOZORDER = 4
SWP_SHOWWINDOW = 64
SWP_NOOWNERZORDER = 512

SIZE_RESTORED = 0
SIZE_MINIMIZED = 1

PM_REMOVE = 1

# http://www.opengl.org/registry/api/wglext.h
WGL_DOUBLE_BUFFER_ARB = 8209
WGL_STEREO_ARB = 8210
WGL_COLOR_BITS_ARB = 8212
WGL_AUX_BUFFERS_ARB = 8228
WGL_SAMPLE_BUFFERS_ARB = 8257
WGL_SAMPLES_ARB = 8258
WGL_RED_BITS_ARB = 8213
WGL_GREEN_BITS_ARB = 8215
WGL_BLUE_BITS_ARB = 8217
WGL_ALPHA_BITS_ARB = 8219
WGL_DEPTH_BITS_ARB = 8226
WGL_STENCIL_BITS_ARB = 8227
WGL_ACCUM_RED_BITS_ARB = 8222
WGL_ACCUM_GREEN_BITS_ARB = 8223
WGL_ACCUM_BLUE_BITS_ARB = 8224
WGL_ACCUM_ALPHA_BITS_ARB = 8225

WGL_CONTEXT_MAJOR_VERSION_ARB = 8337
WGL_CONTEXT_MINOR_VERSION_ARB = 8338
WGL_CONTEXT_FLAGS_ARB = 8340
WGL_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB = 2

WGL_SWAP_MAIN_PLANE = 1
HGLRC = HANDLE

PFD_TYPE_RGBA = 0
PFD_DOUBLEBUFFER = 0x00000001
PFD_STEREO = 0x00000002
PFD_DRAW_TO_WINDOW = 0x00000004
PFD_SUPPORT_OPENGL = 0x00000020
PFD_DEPTH_DONTCARE = 0x20000000
PFD_DOUBLEBUFFER_DONTCARE = 0x40000000
PFD_STEREO_DONTCARE = 0x80000000


# gdi32

def MAKEINTRESOURCE(i):
    return cast(c_void_p(i & 0xFFFF), c_wchar_p)


class POINT(Structure):
    _fields_ = [('x', LONG), ('y', LONG)]


class RECT(Structure):
    _fields_ = [('left', LONG), ('top', LONG),
                ('right', LONG), ('bottom', LONG)]

LPRECT = POINTER(RECT)
LPMSG = POINTER(MSG)


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
    _fields_ = [('cbSize', DWORD), ('rcMonitor', RECT), ('rcWork', RECT),
                ('dwFlags', DWORD), ('szDevice', WCHAR * CCHDEVICENAME)]
    __slots__ = [f[0] for f in _fields_]


class DEVMODE(Structure):
    _fields_ = [
        ('dmDeviceName', BCHAR * CCHDEVICENAME), ('dmSpecVersion', WORD),
        ('dmDriverVersion', WORD), ('dmSize', WORD), ('dmDriverExtra', WORD),
        ('dmFields', DWORD),
        # Just using largest union member here
        ('dmOrientation', c_short), ('dmPaperSize', c_short),
        ('dmPaperLength', c_short), ('dmPaperWidth', c_short),
        ('dmScale', c_short), ('dmCopies', c_short),
        ('dmDefaultSource', c_short), ('dmPrintQuality', c_short),
        # End union
        ('dmColor', c_short), ('dmDuplex', c_short),
        ('dmYResolution', c_short), ('dmTTOption', c_short),
        ('dmCollate', c_short), ('dmFormName', BCHAR * CCHFORMNAME),
        ('dmLogPixels', WORD), ('dmBitsPerPel', DWORD), ('dmPelsWidth', DWORD),
        ('dmPelsHeight', DWORD), ('dmDisplayFlags', DWORD),  # union with dmNup
        ('dmDisplayFrequency', DWORD), ('dmICMMethod', DWORD),
        ('dmICMIntent', DWORD), ('dmDitherType', DWORD),
        ('dmReserved1', DWORD), ('dmReserved2', DWORD),
        ('dmPanningWidth', DWORD), ('dmPanningHeight', DWORD)]


class PIXELFORMATDESCRIPTOR(Structure):
    _fields_ = [
        ('nSize', WORD), ('nVersion', WORD), ('dwFlags', DWORD),
        ('iPixelType', BYTE), ('cColorBits', BYTE), ('cRedBits', BYTE),
        ('cRedShift', BYTE), ('cGreenBits', BYTE), ('cGreenShift', BYTE),
        ('cBlueBits', BYTE), ('cBlueShift', BYTE), ('cAlphaBits', BYTE),
        ('cAlphaShift', BYTE), ('cAccumBits', BYTE), ('cAccumRedBits', BYTE),
        ('cAccumGreenBits', BYTE), ('cAccumBlueBits', BYTE),
        ('cAccumAlphaBits', BYTE), ('cDepthBits', BYTE),
        ('cStencilBits', BYTE), ('cAuxBuffers', BYTE), ('iLayerType', BYTE),
        ('bReserved', BYTE), ('dwLayerMask', DWORD), ('dwVisibleMask', DWORD),
        ('dwDamageMask', DWORD)]

WNDPROC = WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)
MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, LPRECT, LPARAM)


class WNDCLASS(Structure):
    _fields_ = [
        ('style', UINT), ('lpfnWndProc', WNDPROC), ('cbClsExtra', c_int),
        ('cbWndExtra', c_int), ('hInstance', HINSTANCE), ('hIcon', HICON),
        ('hCursor', HCURSOR), ('hbrBackground', HBRUSH),
        ('lpszMenuName', c_char_p), ('lpszClassName', c_wchar_p)]


class MINMAXINFO(Structure):
    _fields_ = [
        ('ptReserved', POINT), ('ptMaxSize', POINT), ('ptMaxPosition', POINT),
        ('ptMinTrackSize', POINT), ('ptMaxTrackSize', POINT)]
    __slots__ = [f[0] for f in _fields_]


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
user32.DispatchMessageW.restype = LRESULT
user32.DispatchMessageW.argtypes = [LPMSG]
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
user32.MapVirtualKeyW.restype = UINT
user32.MapVirtualKeyW.argtypes = [UINT, UINT]
user32.LoadIconW.restype = HICON
user32.LoadIconW.argtypes = [HINSTANCE, c_wchar_p]
user32.PeekMessageW.restype = BOOL
user32.PeekMessageW.argtypes = [LPMSG, HWND, UINT, UINT, UINT]
user32.ReleaseCapture.restype = BOOL
user32.ReleaseCapture.argtypes = []
user32.RegisterClassW.restype = ATOM
user32.RegisterClassW.argtypes = [POINTER(WNDCLASS)]
user32.ReleaseDC.argtypes = [c_void_p, HDC]
user32.SetCapture.restype = HWND
user32.SetCapture.argtypes = [HWND]
user32.SetProcessDPIAware.argtypes = []
user32.SetWindowPos.restype = BOOL
user32.SetWindowPos.argtypes = [HWND, HWND, c_int, c_int, c_int, c_int, UINT]
user32.SetWindowTextW.restype = BOOL
user32.SetWindowTextW.argtypes = [HWND, c_wchar_p]
user32.ShowWindow.restype = BOOL
user32.ShowWindow.argtypes = [HWND, c_int]
user32.TranslateMessage.restype = BOOL
user32.TranslateMessage.argtypes = [LPMSG]
user32.UnregisterClassW.restype = BOOL
user32.UnregisterClassW.argtypes = [c_wchar_p, HINSTANCE]

wgl = windll.opengl32
wgl.wglCreateContext.restype = HGLRC
wgl.wglCreateContext.argtypes = [HDC]
wgl.wglDeleteContext.restype = BOOL
wgl.wglDeleteContext.argtypes = [HGLRC]
wgl.wglMakeCurrent.restype = BOOL
wgl.wglMakeCurrent.argtypes = [HDC, HGLRC]
wgl.wglGetProcAddress.restype = CFUNCTYPE(POINTER(c_int))
wgl.wglGetProcAddress.argtypes = [c_char_p]
wgl.wglShareLists.restype = BOOL
wgl.wglShareLists.argtypes = [HGLRC, HGLRC]
wgl.wglSwapLayerBuffers.restype = BOOL
wgl.wglSwapLayerBuffers.argtypes = [HDC, UINT]


def wglSwapIntervalEXT(interval):
    """Wrapper ensuring it actually exists (only after context exists)"""
    wgl.wglSwapIntervalEXT.restype = BOOL
    wgl.wglSwapIntervalEXT.argtypes = [c_int]
    assert wgl.wglSwapIntervalEXT(int(interval))


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
