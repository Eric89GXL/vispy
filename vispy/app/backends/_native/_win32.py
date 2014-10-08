# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

# Adapted from Pyglet:
# ----------------------------------------------------------------------------
# pyglet
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------


from ctypes import (byref, c_wchar_p, c_int16, sizeof,
                    c_int, windll, POINTER, CFUNCTYPE, c_char_p, c_short)
from ctypes.wintypes import HANDLE, UINT, BOOL

from ...base import BaseCanvasBackend
from ....ext.gdi32plus import (gdi32, kernel32, user32,
                               RECT, POINT, HDC, WNDCLASS, WNDPROC,
                               MONITORINFOEX, MAKEINTRESOURCE, DEVMODE,
                               PIXELFORMATDESCRIPTOR, MONITORENUMPROC)
from ....ext import gdi32plus as g32
from ....util import keys


# Screens ####################################################################

def _get_screens():
    """Get system screens, with info"""
    screens = []

    def enum_proc(hMonitor, hdcMonitor, lprcMonitor, dwData):
        r = lprcMonitor.contents
        info = MONITORINFOEX()
        info.cbSize = sizeof(MONITORINFOEX)
        user32.GetMonitorInfoW(hMonitor, byref(info))
        device_name = info.szDevice
        mode = DEVMODE()
        mode.dmSize = sizeof(DEVMODE)
        user32.EnumDisplaySettingsW(device_name, g32.ENUM_CURRENT_SETTINGS,
                                    byref(mode))
        screens.append(dict(monitor=hMonitor, name=device_name,
                            x=r.left, y=r.top,
                            width=r.right-r.left, height=r.bottom-r.top,
                            mode=mode, depth=mode.dmBitsPerPel,
                            rate=mode.dmDisplayFrequency))
        return True
    enum_proc_ptr = MONITORENUMPROC(enum_proc)
    user32.EnumDisplayMonitors(None, None, enum_proc_ptr, 0)
    return screens


def _get_location(lParam):
    """Convert lParam to x, y"""
    return c_int16(lParam & 0xffff).value, c_int16(lParam >> 16).value


def _get_modifiers(key_lParam=0):
    modifiers = []
    if user32.GetKeyState(g32.VK_SHIFT) & 0xff00:
        modifiers.append(keys.SHIFT)
    if user32.GetKeyState(g32.VK_CONTROL) & 0xff00:
        modifiers.append(keys.CONTROL)
    if user32.GetKeyState(g32.VK_LWIN) & 0xff00:
        modifiers.append(keys.META)
    if key_lParam:
        if key_lParam & (1 << 29):
            modifiers.append(keys.ALT)
    elif user32.GetKeyState(g32.VK_MENU) < 0:
        modifiers.append(keys.ALT)
    return modifiers

# GL Context #################################################################

PFD_TYPE_RGBA = 0
PFD_DOUBLEBUFFER = 0x00000001
PFD_STEREO = 0x00000002
PFD_DRAW_TO_WINDOW = 0x00000004
PFD_SUPPORT_OPENGL = 0x00000020
PFD_DEPTH_DONTCARE = 0x20000000
PFD_DOUBLEBUFFER_DONTCARE = 0x40000000
PFD_STEREO_DONTCARE = 0x80000000


def _set_pfd(hdc, double_buffer=True, stereo=False, depth_size=None,
             buffer_size=None, stencil_size=None,
             blue_size=None, red_size=None, green_size=None, alpha_size=None,
             accum_red_size=None, accum_green_size=None, accum_blue_size=None,
             accum_alpha_size=None, aux_buffers=None, samples=None):
    """Set pixel format of a drawing context"""
    pfd = PIXELFORMATDESCRIPTOR()
    pfd.nSize = sizeof(PIXELFORMATDESCRIPTOR)
    pfd.nVersion = 1
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL
    if double_buffer:
        pfd.dwFlags |= PFD_DOUBLEBUFFER
    else:
        pfd.dwFlags |= PFD_DOUBLEBUFFER_DONTCARE
    pfd.dwFlags |= PFD_STEREO if stereo else PFD_STEREO_DONTCARE

    if not depth_size:
        pfd.dwFlags |= PFD_DEPTH_DONTCARE
    pfd.iPixelType = PFD_TYPE_RGBA
    pfd.cColorBits = buffer_size or 0
    pfd.cRedBits = red_size or 0
    pfd.cGreenBits = green_size or 0
    pfd.cBlueBits = blue_size or 0
    pfd.cAlphaBits = alpha_size or 0
    pfd.cAccumRedBits = accum_red_size or 0
    pfd.cAccumGreenBits = accum_green_size or 0
    pfd.cAccumBlueBits = accum_blue_size or 0
    pfd.cAccumAlphaBits = accum_alpha_size or 0
    pfd.cDepthBits = depth_size or 0
    pfd.cStencilBits = stencil_size or 0
    pfd.cAuxBuffers = aux_buffers or 0
    pf = gdi32.ChoosePixelFormat(hdc, byref(pfd))
    if not pf:
        raise RuntimeError('could not get correct pixel format')
    gdi32.SetPixelFormat(hdc, pf, pfd)
    # XXX Add samples


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

wgl = windll.opengl32
HGLRC = HANDLE
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


class _Win32Context(object):
    """Create and manage a given context"""
    def __init__(self, hdc, cfg, share_context=None):
        _set_pfd(hdc, **cfg)
        self._context = wgl.wglCreateContext(hdc)
        if not self._context:
            raise RuntimeError('context could not be created')
        if share_context is not None:
            if not wgl.wglShareLists(share_context, self._context):
                raise RuntimeError('Unable to share contexts')
        # wglSwapIntervalEXT(cfg.get('vsync', True)) XXX FIX
        self._hdc = hdc

    def set_current(self):
        if self._context is not None:
            wgl.wglMakeCurrent(self._hdc, self._context)

    def detach(self):
        if self._context is not None:
            wgl.wglDeleteContext(self._context)
            self._context = None

    def swap_buffers(self):
        if self._context is not None:
            wgl.wglSwapLayerBuffers(self._hdc, WGL_SWAP_MAIN_PLANE)


# Window #####################################################################

_VP_NATIVE_ALL_WINDOWS = []

button_map = {
    g32.WM_LBUTTONDOWN: 1,
    g32.WM_LBUTTONUP: 1,
    g32.WM_MBUTTONDOWN: 2,
    g32.WM_MBUTTONUP: 2,
    g32.WM_RBUTTONDOWN: 3,
    g32.WM_RBUTTONUP: 3,
}


class CanvasBackend(BaseCanvasBackend):
    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        title, size, position, show, vsync, resize, dec, fs, parent, context, \
            = self._process_backend_kwargs(kwargs)

        screens = _get_screens()
        if fs is True or fs is not False:
            if fs is True:
                self._screen = screens[0]
            else:
                self._screen = screens[fs]
            self._ws = g32.WS_POPUP & ~(g32.WS_THICKFRAME | g32.WS_MAXIMIZEBOX)
        elif fs is False:
            self._screen = screens[0]
            self._ws = g32.WS_OVERLAPPEDWINDOW
            if resize:
                self._ws |= g32.WS_THICKFRAME
        self._resizable = resize

        if fs is not False:
            self._fullscreen = True
            x, y = self._screen['x'], self._screen['y']
            width, height = self._screen['width'], self._screen['height']
            hwnd_after = g32.HWND_TOPMOST
        else:
            self._fullscreen = False
            width, height = self._client_to_window_size(*size)
            hwnd_after = g32.HWND_NOTOPMOST
        self._width, self._height = width, height

        module = kernel32.GetModuleHandleW(None)
        black = gdi32.GetStockObject(g32.BLACK_BRUSH)
        self._wc = WNDCLASS()
        self._wc.lpszClassName = u'GenericAppClass%d' % id(self)
        self._wc.lpfnWndProc = WNDPROC(self._wnd_proc)
        self._wc.style = g32.CS_VREDRAW | g32.CS_HREDRAW
        self._wc.hIcon = user32.LoadIconW(module, MAKEINTRESOURCE(1))
        self._wc.hbrBackground = black
        self._wc.lpszMenuName = None
        self._wc.hInstance = self._wc.cbClsExtra = self._wc.cbWndExtra = 0
        user32.RegisterClassW(byref(self._wc))
        self._hwnd = user32.CreateWindowExW(
            0, self._wc.lpszClassName, title, self._ws, g32.CW_USEDEFAULT,
            g32.CW_USEDEFAULT, width, height, 0, 0, self._wc.hInstance, 0)
        self._dc = user32.GetDC(self._hwnd)
        # Deal with context
        if not context.istaken:
            context.take('native', self)
            share = None
        elif context.istaken == 'native':
            share = context.backend_canvas.context
        else:
            raise RuntimeError('Different backends cannot share a context.')
        self.context = _Win32Context(self._dc, context.config, share)
        self.context.set_current()

        # Position and size window
        flags = g32.SWP_FRAMECHANGED
        if not self._fullscreen:
            if position is None:
                position = (0, 0)
                flags |= g32.SWP_NOMOVE
            x, y = self._client_to_window_pos(*position)
        user32.SetWindowPos(self._hwnd, hwnd_after, x, y, width, height, flags)
        self._vispy_set_visible(show)
        self._closed = False
        self._needs_draw = True
        self._vispy_canvas.events.initialize()
        self._mouse_pos = (0, 0)
        _VP_NATIVE_ALL_WINDOWS.append(self)

    def _vispy_set_current(self):
        self._vispy_context.set_current(False)  # Mark as current
        self.context.set_current()

    def _vispy_swap_buffers(self):
        self.context.swap_buffers()

    def _vispy_set_title(self, title):
        user32.SetWindowTextW(self._hwnd, c_wchar_p(title))

    def _vispy_set_size(self, w, h):
        if self._fullscreen:
            raise RuntimeError('Cannot set size of fullscreen window.')
        self._width, self._height = self._client_to_window_size(w, h)
        user32.SetWindowPos(self._hwnd, 0, 0, 0, self._width, self._height,
                            g32.SWP_NOZORDER | g32.SWP_NOMOVE |
                            g32.SWP_NOOWNERZORDER)

    def _vispy_set_position(self, x, y):
        x, y = self._client_to_window_pos(x, y)
        user32.SetWindowPos(self._hwnd, 0, x, y, 0, 0,
                            g32.SWP_NOZORDER | g32.SWP_NOSIZE |
                            g32.SWP_NOOWNERZORDER)

    def _vispy_set_visible(self, visible):
        if visible:
            ins_after = g32.HWND_TOPMOST if self._fullscreen else g32.HWND_TOP
            user32.SetWindowPos(self._hwnd, ins_after, 0, 0, 0, 0,
                                g32.SWP_NOMOVE | g32.SWP_NOSIZE |
                                g32.SWP_SHOWWINDOW)
        else:
            user32.ShowWindow(self._hwnd, g32.SW_HIDE)

    def _vispy_set_fullscreen(self, fullscreen):
        raise NotImplementedError()

    def _vispy_update(self):
        self._needs_draw = True

    def _on_draw(self):
        self._vispy_set_current()
        self._vispy_canvas.events.draw(region=None)  # (0, 0, w, h))

    def _vispy_close(self):
        if not self._hwnd:
            return
        self._closed = True
        self.context.detach()
        user32.DestroyWindow(self._hwnd)
        user32.UnregisterClassW(self._wc.lpszClassName, 0)
        user32.ReleaseDC(None, self._dc)
        self._hwnd = self._dc = None
        _VP_NATIVE_ALL_WINDOWS[_VP_NATIVE_ALL_WINDOWS.index(self)] = None

    def _vispy_get_size(self):
        rect = RECT()
        user32.GetClientRect(self._hwnd, byref(rect))
        return rect.right - rect.left, rect.bottom - rect.top

    def _vispy_get_position(self):
        rect, point = RECT(), POINT()
        user32.GetClientRect(self._hwnd, byref(rect))
        point.x, point.y = rect.left, rect.top
        user32.ClientToScreen(self._hwnd, byref(point))
        return point.x, point.y

    def _vispy_get_fullscreen(self):
        return self._fullscreen

    def _poll_events(self):
        msg = g32.MSG()
        while user32.PeekMessageW(byref(msg), 0, 0, 0, g32.PM_REMOVE):
            user32.TranslateMessage(byref(msg))
            user32.DispatchMessageW(byref(msg))

    def _client_to_window_size(self, width, height):
        r = RECT()
        r.left, r.top, r.right, r.bottom = 0, 0, width, height
        user32.AdjustWindowRectEx(byref(r), self._ws, False, 0)
        return (r.right - r.left, r.bottom - r.top)

    def _client_to_window_pos(self, x, y):
        r = RECT()
        r.left, r.top = x, y
        user32.AdjustWindowRectEx(byref(r), self._ws, False, 0)
        return (r.left, r.top)

    def _wnd_proc(self, hwnd, msg, wParam, lParam):
        if msg in (g32.WM_KEYDOWN, g32.WM_KEYUP, g32.WM_SYSKEYDOWN,
                   g32.WM_SYSKEYUP):
            repeat = False
            if lParam & (1 << 30):
                if msg not in (g32.WM_KEYUP, g32.WM_SYSKEYUP):
                    repeat = True
                fun = self._vispy_canvas.events.key_release
            else:
                fun = self._vispy_canvas.events.key_press
            sym = keymap.get(wParam, None)
            if symbol is None:
                ch = user32.MapVirtualKeyW(wParam, g32.MAPVK_VK_TO_CHAR)
                sym = chmap.get(ch)
                if sym is None:
                    sym = key.user_key(wParam)
            if not repeat:
                fun(sym, '', modifiers=_get_modifiers(lParam))
        elif msg == g32.WM_MOUSEMOVE:
            x, y = _get_location(lParam)
            m = _get_modifiers()
            self._vispy_canvas.events.mouse_move(pos=(x, y), modifiers=m)
        elif msg in (g32.WM_LBUTTONUP, g32.WM_LBUTTONDOWN,
                     g32.WM_MBUTTONUP, g32.WM_MBUTTONDOWN,
                     g32.WM_RBUTTONUP, g32.WM_RBUTTONDOWN):
            if msg in (g32.WM_LBUTTONDOWN, g32.WM_MBUTTONDOWN,
                       g32.WM_RBUTTONDOWN):
                fun = self._vispy_canvas.events.mouse_press
                user32.SetCapture(self._hwnd)
            else:
                fun = self._vispy_canvas.events.mouse_release
                user32.ReleaseCapture()
            button = button_map[msg]
            x, y = _get_location(lParam)
            fun(pos=(x, y), button=button, modifiers=_get_modifiers())
            self._mouse_pos = (x, y)
        elif msg == g32.WM_MOUSEWHEEL:
            delta = (0, c_short(wParam >> 16).value / float(g32.WHEEL_DELTA))
            self._vispy_canvas.events.mouse_wheel(pos=self._mouse_pos,
                                                  delta=delta,
                                                  modifiers=_get_modifiers())
        elif msg == g32.WM_CLOSE:
            self._vispy_canvas.close()
            return 0
        elif msg == g32.WM_PAINT:
            self._vispy_canvas.events.draw(region=None)
        elif msg == g32.WM_SIZING:
            return 1
        elif msg == g32.WM_SIZE:
            # Ignore window creation size event (appears for fullscreen only)
            if not self._dc:
                return user32.DefWindowProcW(hwnd, msg, wParam, lParam)
            w, h = _get_location(lParam)
            if not self._fullscreen:
                self._width, self._height = w, h
            self._vispy_set_current()
            self._vispy_canvas.events.resize(size=(self._width, self._height))
        elif msg == g32.WM_ERASEBKGND:
            # Prevent flicker during resize; but erase bkgnd if we're fullscreen.
            if not self._fullscreen:
                return 1
        #elif msg == g32.WM_SYSCOMMAND:
        #    return 0
        #elif msg == g32.WM_EXITSIZEMOVE:
        #    return 0
        #elif msg in (g32.WM_SETFOCUS, g32.WM_KILLFOCUS):
        #    return 0
        elif msg == g32.WM_GETMINMAXINFO:
            info = g32.MINMAXINFO.from_address(lParam)
            if not self._resizable:
                lims = self._client_to_window_size(self._width, self._height)
                info.ptMinTrackSize.x, info.ptMinTrackSize.y = lims
                info.ptMaxTrackSize.x, info.ptMaxTrackSize.y = lims
        return user32.DefWindowProcW(hwnd, msg, wParam, lParam)
