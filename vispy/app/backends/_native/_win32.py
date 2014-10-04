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

# Adapted from Pyglet

from ctypes import (byref, c_wchar_p, c_int16, create_unicode_buffer, sizeof,
                    c_int, windll, POINTER, CFUNCTYPE, c_char_p)
from ctypes.wintypes import HANDLE, UINT, BOOL
from vispy.ext.gdi32plus import (gdi32, kernel32, user32,
                                 RECT, POINT, HDC, WNDCLASS, WNDPROC,
                                 MONITORINFOEX, MAKEINTRESOURCE, DEVMODE,
                                 PIXELFORMATDESCRIPTOR, MONITORENUMPROC)

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
        user32.EnumDisplaySettingsW(device_name, ENUM_CURRENT_SETTINGS,
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
             accum_alpha_size=None, aux_buffers=None):
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


def wglCreateContextAttribsARB(hdc, hglrc, attribs):
    funcname = c_char_p('wglCreateContextAttribsARB'.encode('ASCII'))
    func = wgl.wglGetProcAddress(funcname)
    assert func
    return func(hdc, hglrc, attribs)


class Win32Context(object):
    def __init__(self, hdc, cfg, share_context=None):
        attrs = []
        if cfg.get('major_version', None) is not None:
            attrs.extend([WGL_CONTEXT_MAJOR_VERSION_ARB, cfg['major_version']])
        if cfg.get('minor_version', None) is not None:
            attrs.extend([WGL_CONTEXT_MINOR_VERSION_ARB, cfg['minor_version']])
        flags = WGL_CONTEXT_FORWARD_COMPATIBLE_BIT_ARB
        attrs.extend([WGL_CONTEXT_FLAGS_ARB, flags])
        attrs.append(0)
        attrs = (c_int * len(attrs))(*attrs)
        #self._context = wglCreateContextAttribsARB(hdc, share_context, attrs)
        _set_pfd(hdc)
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

_event_key = {
    WM_KEYDOWN: 'keydown',
    WM_KEYUP: 'keyup',
    WM_SYSKEYDOWN: 'syskeydown',
    WM_SYSKEYUP: 'syskeyup',
    WM_CHAR: 'char',
    WM_MOUSEMOVE: 'mousemove',
    WM_MOUSELEAVE: 'mouseleave',
    WM_LBUTTONDOWN: 'lbuttondown',
    WM_LBUTTONUP: 'lbuttonup',
    WM_MBUTTONDOWN: 'mbuttondown',
    WM_MBUTTONUP: 'mbuttondown',
    WM_RBUTTONDOWN: 'rbuttondown',
    WM_RBUTTONUP: 'rbuttonup',
    WM_MOUSEWHEEL: 'mousewheel',
    WM_CLOSE: 'close',
    WM_PAINT: 'paint',
    WM_SIZING: 'sizing',
    WM_SIZE: 'size',
    WM_SYSCOMMAND: 'syscommand',
    WM_MOVE: 'move',
    WM_EXITSIZEMOVE: 'exitsizemove',
    WM_SETFOCUS: 'setfocus',
    WM_KILLFOCUS: 'killfocus',
    WM_GETMINMAXINFO: 'minmax',
    WM_ERASEBKGND: 'erase bg',
}


class Window(object):
    def __init__(self, size=(800, 600), pos=None, title='test',
                 resizable=True, fullscreen=False, visible=True, vsync=True):
        screens = _get_screens()
        if fullscreen is True or fullscreen is not False:
            if fullscreen is True:
                self._screen = screens[0]
            else:
                self._screen = screens[fullscreen]
            self._ws = WS_POPUP & ~(WS_THICKFRAME | WS_MAXIMIZEBOX)
        elif fullscreen is False:
            self._screen = screens[0]
            self._ws = WS_OVERLAPPEDWINDOW
            if resizable:
                self._ws |= WS_THICKFRAME

        if fullscreen is not False:
            self._fullscreen = True
            x, y = self._screen['x'], self._screen['y']
            width, height = self._screen['width'], self._screen['height']
            hwnd_after = HWND_TOPMOST
        else:
            self._fullscreen = False
            width, height = self._client_to_window_size(*size)
            hwnd_after = HWND_NOTOPMOST

        module = kernel32.GetModuleHandleW(None)
        black = gdi32.GetStockObject(BLACK_BRUSH)
        self._wc = WNDCLASS()
        self._wc.lpszClassName = u'GenericAppClass%d' % id(self)
        self._wc.lpfnWndProc = WNDPROC(self._wnd_proc)
        self._wc.style = CS_VREDRAW | CS_HREDRAW
        self._wc.hIcon = user32.LoadIconW(module, MAKEINTRESOURCE(1))
        self._wc.hbrBackground = black
        self._wc.lpszMenuName = None
        self._wc.hInstance = self._wc.cbClsExtra = self._wc.cbWndExtra = 0
        user32.RegisterClassW(byref(self._wc))
        self._hwnd = user32.CreateWindowExW(
            0, self._wc.lpszClassName, title, self._ws, CW_USEDEFAULT,
            CW_USEDEFAULT, width, height, 0, 0, self._wc.hInstance, 0)

        self._vwc = WNDCLASS()
        self._vwc.lpszClassName = u'GenericViewClass%d' % id(self)
        self._vwc.lpfnWndProc = WNDPROC(self._wnd_proc_view)
        self._vwc.hbrBackground = black
        self._vwc.lpszMenuName = None
        self._vwc.style = self._vwc.hInstance = self._vwc.hIcon = 0
        self._vwc.cbClsExtra = self._vwc.cbWndExtra = 0
        user32.RegisterClassW(byref(self._vwc))
        self._view_hwnd = user32.CreateWindowExW(
            0, self._vwc.lpszClassName, u'', WS_CHILD | WS_VISIBLE,
            0, 0, 0, 0, self._hwnd, 0, self._vwc.hInstance, 0)
        self._dc = user32.GetDC(self._view_hwnd)
        self.context = Win32Context(self._dc, dict(vsync=vsync), None)
        self.context.set_current()

        # Position and size window
        flags = SWP_FRAMECHANGED
        if not self._fullscreen:
            if pos is None:
                pos = (0, 0)
                flags |= SWP_NOMOVE
            x, y = self._client_to_window_pos(*pos)
        user32.SetWindowPos(self._hwnd, hwnd_after, x, y, width, height, flags)
        user32.SetWindowPos(self._view_hwnd, 0, x, y, width, height,
                            SWP_NOZORDER | SWP_NOOWNERZORDER)
        self.visible = visible

    def close(self):
        if not self._hwnd:
            return
        self.context.detach()
        user32.DestroyWindow(self._hwnd)
        user32.UnregisterClassW(self._wc.lpszClassName, 0)
        self._hwnd = self._dc = None

    @property
    def pos(self):
        rect = RECT()
        user32.GetClientRect(self._hwnd, byref(rect))
        point = POINT()
        point.x, point.y = rect.left, rect.top
        user32.ClientToScreen(self._hwnd, byref(point))
        return point.x, point.y

    @pos.setter
    def pos(self, pos):
        x, y = self._client_to_window_pos(*pos)
        user32.SetWindowPos(self._hwnd, 0, x, y, 0, 0,
                            SWP_NOZORDER | SWP_NOSIZE | SWP_NOOWNERZORDER)

    @property
    def size(self):
        rect = RECT()
        user32.GetClientRect(self._hwnd, byref(rect))
        return rect.right - rect.left, rect.bottom - rect.top

    @size.setter
    def size(self, size):
        if self._fullscreen:
            raise RuntimeError('Cannot set size of fullscreen window.')
        self._width, self._height = self._client_to_window_size(*size)
        user32.SetWindowPos(self._hwnd, 0, 0, 0, self._width, self._height,
                            SWP_NOZORDER | SWP_NOMOVE | SWP_NOOWNERZORDER)

    @property
    def visible(self):
        return user32.IsWindowVisible(self._hwnd)

    @visible.setter
    def visible(self, visible):
        if visible:
            insertAfter = HWND_TOPMOST if self._fullscreen else HWND_TOP
            user32.SetWindowPos(self._hwnd, insertAfter, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
        else:
            user32.ShowWindow(self._hwnd, SW_HIDE)

    @property
    def title(self):
        buf = create_unicode_buffer('', 512)
        user32.GetWindowTextW(self._hwnd, buf, 512)
        return buf.value

    @title.setter
    def title(self, title):
        user32.SetWindowTextW(self._hwnd, c_wchar_p(title))

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
        print('event %s' % _event_key.get(msg, 'unknown (%s)' % msg))
        result = user32.DefWindowProcW(hwnd, msg, wParam, lParam)
        return result

    def _wnd_proc_view(self, hwnd, msg, wParam, lParam):
        print('view event %s' % _event_key.get(msg, 'unknown (%s)' % msg))
        result = user32.DefWindowProcW(hwnd, msg, wParam, lParam)
        return result


x = Window(fullscreen=False)
