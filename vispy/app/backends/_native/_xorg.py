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

from copy import deepcopy
from ctypes import (c_int, POINTER, byref, c_ulong, pointer, cast, c_ubyte,
                    create_string_buffer, c_char_p, c_uint)


from ...base import BaseCanvasBackend
from ....ext.six import string_types
from ....ext import glx, xlib
from ....util import keys

KEYMAP = {
    65505: keys.SHIFT, 65506: keys.SHIFT,
    65507: keys.CONTROL, 65508: keys.CONTROL,
    65513: keys.ALT, 65514: keys.ALT,
    65511: keys.META, 65512: keys.META,

    65361: keys.LEFT, 65362: keys.UP, 65363: keys.RIGHT, 65364: keys.DOWN,
    65365: keys.PAGEUP, 65366: keys.PAGEDOWN,

    65379: keys.INSERT, 65535: keys.DELETE,
    65360: keys.HOME, 655367: keys.END,

    65307: keys.ESCAPE, 65288: keys.BACKSPACE,

    65470: keys.F1, 65471: keys.F2, 65472: keys.F3, 65473: keys.F4,
    65474: keys.F5, 65475: keys.F6, 65476: keys.F7, 65477: keys.F8,
    65478: keys.F9, 65479: keys.F10, 65480: keys.F11, 65481: keys.F12,

    32: keys.SPACE, 65293: keys.ENTER, 65421: keys.ENTER, 65289: keys.TAB,
}

_default_ev_mask = (0x1ffffff & ~xlib.PointerMotionHintMask
                    & ~xlib.ResizeRedirectMask & ~xlib.SubstructureNotifyMask)


def _get_visual_info(x_display, x_screen, cfg):
    attribute_ids = {
        'buffer_size': glx.GLX_BUFFER_SIZE,
        'level': glx.GLX_LEVEL,     # Not supported
        'double_buffer': glx.GLX_DOUBLEBUFFER,
        'stereo': glx.GLX_STEREO,
        'aux_buffers': glx.GLX_AUX_BUFFERS,
        'red_size': glx.GLX_RED_SIZE,
        'green_size': glx.GLX_GREEN_SIZE,
        'blue_size': glx.GLX_BLUE_SIZE,
        'alpha_size': glx.GLX_ALPHA_SIZE,
        'depth_size': glx.GLX_DEPTH_SIZE,
        'stencil_size': glx.GLX_STENCIL_SIZE,
        'accum_red_size': glx.GLX_ACCUM_RED_SIZE,
        'accum_green_size': glx.GLX_ACCUM_GREEN_SIZE,
        'accum_blue_size': glx.GLX_ACCUM_BLUE_SIZE,
        'accum_alpha_size': glx.GLX_ACCUM_ALPHA_SIZE,
    }
    info = glx.GLXInfo(x_display)
    have_13 = info.have_version(1, 3)
    attrs = []
    cfg = deepcopy(cfg)
    # version 10 ATI doesn't support stereo
    if not have_13:
        if 'ATI' in info.get_client_vendor():
            del attribute_ids['stereo']
            cfg['stereo'] = False
        attrs.extend([glx.GLX_RGBA, True])
    else:
        attribute_ids.update({'samples': glx.GLX_SAMPLES,
                              'x_renderable': glx.GLX_X_RENDERABLE})
        attrs.extend([glx.GLX_X_RENDERABLE, True])
    for name, value in cfg.items():
        attr = attribute_ids.get(name, None)
        if attr is not None and value is not None:
            attrs.extend([attr, int(value)])
    attrs.extend([0, 0])
    attrib_list = (c_int * len(attrs))(*attrs)
    fbconfigs = None
    if have_13:
        elements = c_int()
        configs = glx.glXChooseFBConfig(x_display, x_screen, attrib_list,
                                        byref(elements))
        if not configs:
            raise RuntimeError('no matching GL configs found')
        fbconfigs = cast(configs, POINTER(glx.GLXFBConfig * elements.value))
        fbconfigs = fbconfigs.contents
        visual_info = glx.glXGetVisualFromFBConfig(x_display, fbconfigs[0])
        visual_info = visual_info.contents
    else:
        visual_info = glx.glXChooseVisual(x_display, x_screen, attrib_list)
    return visual_info, fbconfigs


class XContext(object):
    def __init__(self, display, screen, window, visual_info, fbconfigs,
                 vsync, share):
        self.x_display = display
        self.x_window = window
        info = glx.GLXInfo(self.x_display)
        # In order of preference: GLX_MESA_swap_control, GLX_SGI_swap_control
        if info.have_extension('GLX_MESA_swap_control'):
            glx.glXSwapIntervalMESA(int(vsync))
        elif info.have_extension('GLX_SGI_swap_control') and vsync:
            glx.glXSwapIntervalSGI(1)
        self.glx_window = None
        have_13 = info.have_version(1, 3)
        share_context = share.glx_context if share else None
        if not have_13:
            self.glx_context = glx.glXCreateContext(
                self.x_display, visual_info, share_context, True)
        else:
            self.glx_context = glx.glXCreateNewContext(
                self.x_display, fbconfigs[0], glx.GLX_RGBA_TYPE,
                share_context, True)
            self.glx_window = glx.glXCreateWindow(
                self.x_display, fbconfigs[0], self.x_window, None)
        glx_context_id = self.glx_context.contents._opaque_struct
        if glx_context_id == glx.GLX_BAD_CONTEXT:
            raise RuntimeError('Invalid context share')
        elif glx_context_id == glx.GLXBadFBConfig:
            raise RuntimeError('Invalid GL configuration')
        elif glx_context_id < 0:
            raise RuntimeError('Could not create GL context')
        self._destroyed = False

    def set_current(self):
        if self._destroyed:
            return
        if self.glx_window is not None:
            glx.glXMakeContextCurrent(self.x_display, self.glx_window,
                                      self.glx_window, self.glx_context)
        else:
            glx.glXMakeCurrent(self.x_display, self.x_window, self.glx_context)

    def destroy(self):
        if self._destroyed:
            return
        if self.glx_window is not None:
            glx.glXDestroyWindow(self.x_display, self.glx_window)
            self.glx_window = None
        if self.glx_context is not None:
            glx.glXDestroyContext(self.x_display, self.glx_context)
            self.glx_context = None
        self._destroyed = True

    def swap_buffers(self):
        if self._destroyed:
            return
        window = self.x_window if self.glx_window is None else self.glx_window
        glx.glXSwapBuffers(self.x_display, window)


_VP_NATIVE_ALL_WINDOWS = []


def _pass(event):
    """Dummy event processor"""
    pass


def _translate_modifiers(state):
    """Translate X state to modifiers"""
    modifiers = []
    if state & xlib.ShiftMask:
        modifiers.append(keys.SHIFT)
    if state & xlib.ControlMask:
        modifiers.append(keys.CONTROL)
    if state & xlib.Mod1Mask:
        modifiers.append(keys.ALT)
    if state & xlib.Mod4Mask:
        modifiers.append(keys.META)
    return modifiers


class CanvasBackend(BaseCanvasBackend):

    def __init__(self, *args, **kwargs):
        BaseCanvasBackend.__init__(self, *args)
        title, size, position, show, vsync, resize, dec, fs, parent, context, \
            = self._process_backend_kwargs(kwargs)
        self._mapped = False

        # Determine display/screen to use
        self._x_screen_id = 0
        if fs is False:
            self._fullscreen = False
        else:
            self._fullscreen = True
            if fs is not True:
                self._x_screen_id = fs
        self._x_screen_id = 0
        self._x_display = xlib.XOpenDisplay(None)
        if not self._x_display:
            raise RuntimeError('Cannot connect to display')
        screen_count = xlib.XScreenCount(self._x_display)
        if self._x_screen_id >= screen_count:
            raise RuntimeError('Display has no screen %s' % self._x_screen_num)
        si = xlib.XScreenOfDisplay(self._x_display, self._x_screen_id)
        self._screen_width = si.contents.width
        self._screen_height = si.contents.height
        root = xlib.XRootWindow(self._x_display, self._x_screen_id)
        visual_info, fbconfigs = _get_visual_info(self._x_display,
                                                  self._x_screen_id,
                                                  context.config)
        visual = visual_info.visual
        visual_id = xlib.XVisualIDFromVisual(visual)
        default_visual = xlib.XDefaultVisual(
            self._x_display, self._x_screen_id)
        default_visual_id = xlib.XVisualIDFromVisual(default_visual)
        window_attributes = xlib.XSetWindowAttributes()
        if visual_id != default_visual_id:
            window_attributes.colormap = xlib.XCreateColormap(
                self._x_display, root, visual, xlib.AllocNone)
        else:
            window_attributes.colormap = xlib.XDefaultColormap(
                self._x_display, self._x_screen_id)
        window_attributes.bit_gravity = xlib.StaticGravity
        mask = xlib.CWColormap | xlib.CWBitGravity | xlib.CWBackPixel
        if self._fullscreen:
            self._width, self._height = self._screen_width, self._screen_height
        else:
            self._width, self._height = size
        self._window = xlib.XCreateWindow(
            self._x_display, root, 0, 0, self._width, self._height,
            0, visual_info.depth, xlib.InputOutput, visual, mask,
            byref(window_attributes))
        xlib.XMapWindow(self._x_display, self._window)
        xlib.XSelectInput(self._x_display, self._window, _default_ev_mask)

        # Deal with context
        if not context.istaken:
            context.take('native', self)
            share = None
        elif context.istaken == 'native':
            share = context.backend_canvas.context
        else:
            raise RuntimeError('Different backends cannot share a context.')
        self.context = XContext(self._x_display, self._x_screen_id,
                                self._window,
                                visual_info, fbconfigs, vsync, share)
        protocols = []
        protocols.append(xlib.XInternAtom(
            self._x_display, 'WM_DELETE_WINDOW'.encode('ASCII'), False))
        protocols = (c_ulong * len(protocols))(*protocols)
        xlib.XSetWMProtocols(self._x_display, self._window,
                             protocols, len(protocols))
        # Set window attributes
        attributes = xlib.XSetWindowAttributes()
        attributes_mask = 0

        if self._fullscreen:
            self._set_wm_state('_NET_WM_STATE_FULLSCREEN')
            xlib.XMoveResizeWindow(self._x_display, self._window, 0, 0,
                                   self._screen_width, self._screen_height)
        else:
            xlib.XResizeWindow(self._x_display, self._window,
                               self._width, self._height)

        xlib.XChangeWindowAttributes(self._x_display, self._window,
                                     attributes_mask, byref(attributes))
        # Set style
        self._set_atoms_property('_NET_WM_WINDOW_TYPE',
                                 ('_NET_WM_WINDOW_TYPE_NORMAL',))

        # Set resizeable
        if not resize and not self._fullscreen:
            self._set_minmax_size(self._width, self._height)

        # Set caption
        self._vispy_set_title(title)

        _NET_WM_BYPASS_COMPOSITOR_HINT_ON = c_ulong(int(self._fullscreen))
        name = xlib.XInternAtom(self._x_display,
                                '_NET_WM_BYPASS_COMPOSITOR'.encode('ASCII'),
                                False)
        ptr = pointer(_NET_WM_BYPASS_COMPOSITOR_HINT_ON)
        xlib.XChangeProperty(self._x_display, self._window,
                             name, xlib.XA_CARDINAL, 32,
                             xlib.PropModeReplace,
                             cast(ptr, POINTER(c_ubyte)), 1)

        self._closed = False
        _VP_NATIVE_ALL_WINDOWS.append(self)
        self._vispy_set_current()
        self._resizable = resize
        self._needs_draw = True
        self._vispy_canvas.events.initialize()
        if show:
            self._vispy_set_visible(True)
        self._event_handlers = {}
        self._event_handlers[xlib.KeyPress] = self._event_key
        self._event_handlers[xlib.KeyRelease] = self._event_key
        self._event_handlers[xlib.MotionNotify] = self._event_motion
        self._event_handlers[xlib.ClientMessage] = self._event_clientmessage
        self._event_handlers[xlib.ButtonPress] = self._event_button
        self._event_handlers[xlib.ButtonRelease] = self._event_button
        self._event_handlers[xlib.ConfigureNotify] = self._event_configure

    def _map(self):
        if self._mapped:
            return
        # Map the window, wait for map event before continuing.
        xlib.XSelectInput(
            self._x_display, self._window, xlib.StructureNotifyMask)
        xlib.XMapRaised(self._x_display, self._window)
        e = xlib.XEvent()
        while True:
            xlib.XNextEvent(self._x_display, e)
            if e.type == xlib.ConfigureNotify:
                self._width = e.xconfigure.width
                self._height = e.xconfigure.height
            elif e.type == xlib.MapNotify:
                break
        xlib.XSelectInput(self._x_display, self._window, _default_ev_mask)
        self._mapped = True

    def _unmap(self):
        if not self._mapped:
            return
        xlib.XSelectInput(self._x_display, self._window,
                          xlib.StructureNotifyMask)
        xlib.XUnmapWindow(self._x_display, self._window)
        e = xlib.XEvent()
        while True:
            xlib.XNextEvent(self._x_display, e)
            if e.type == xlib.UnmapNotify:
                break
        xlib.XSelectInput(self._x_display, self._window, _default_ev_mask)
        self._mapped = False

    def _get_root(self):
        attributes = xlib.XWindowAttributes()
        xlib.XGetWindowAttributes(self._x_display, self._window,
                                  byref(attributes))
        return attributes.root

    def _is_reparented(self):
        root, parent = c_ulong(), c_ulong()
        children, n_children = pointer(c_ulong()), c_uint()
        xlib.XQueryTree(self._x_display, self._window,
                        byref(root), byref(parent), byref(children),
                        byref(n_children))
        return root.value != parent.value

    def _set_minmax_size(self, width, height):
        self._minmax_size = width, height
        hints = xlib.XAllocSizeHints().contents
        hints.flags |= xlib.PMinSize | xlib.PMaxSize
        hints.min_width, hints.min_height = self._minmax_size
        hints.max_width, hints.max_height = self._minmax_size
        xlib.XSetWMNormalHints(self._x_display, self._window, byref(hints))

    def _set_text_property(self, name, value, allow_utf8=True):
        atom = xlib.XInternAtom(self._x_display, name.encode('ASCII'), False)
        if not atom:
            raise RuntimeError('Undefined atom "%s"' % name)
        assert isinstance(value, string_types)
        prop = xlib.XTextProperty()
        buf = create_string_buffer(value.encode('ascii', 'ignore'))
        result = xlib.XStringListToTextProperty(
            cast(pointer(buf), c_char_p), 1, byref(prop))
        if result < 0:
            raise RuntimeError('Could not create text property')
        xlib.XSetTextProperty(self._x_display, self._window, byref(prop), atom)

    def _set_atoms_property(self, name, values):
        name_atom = xlib.XInternAtom(self._x_display,
                                     name.encode('ASCII'), False)
        atoms = []
        for value in values:
            atoms.append(xlib.XInternAtom(self._x_display,
                                          value.encode('ASCII'), False))
        atom_type = xlib.XInternAtom(self._x_display,
                                     'ATOM'.encode('ASCII'), False)
        if len(atoms):
            atoms_ar = (xlib.Atom * len(atoms))(*atoms)
            xlib.XChangeProperty(self._x_display, self._window,
                                 name_atom, atom_type, 32,
                                 xlib.PropModeReplace,
                                 cast(pointer(atoms_ar), POINTER(c_ubyte)),
                                 len(atoms))
        else:
            xlib.XDeleteProperty(self._x_display, self._window, name_atom)
        return name_atom, atoms

    def _set_wm_state(self, *states):
        # Set property
        net_wm_state, atoms = self._set_atoms_propert('_NET_WM_STATE', states)
        # Nudge the WM
        e = xlib.XEvent()
        e.xclient.type = xlib.ClientMessage
        e.xclient.message_type = net_wm_state
        e.xclient.display = cast(self._x_display, POINTER(xlib.Display))
        e.xclient.window = self._window
        e.xclient.format = 32
        e.xclient.data.l[0] = xlib.PropModePrepend
        for i, atom in enumerate(atoms):
            e.xclient.data.l[i + 1] = atom
        xlib.XSendEvent(self._x_display, self._get_root(),
                        False, xlib.SubstructureRedirectMask, byref(e))

    def _vispy_warmup(self):
        pass

    def _vispy_close(self):
        if not self._window:
            return
        self.context.destroy()
        self._unmap()
        xlib.XDestroyWindow(self._x_display, self._window)
        self._window = None
        self._closed = True
        _VP_NATIVE_ALL_WINDOWS[_VP_NATIVE_ALL_WINDOWS.index(self)] = None

    def _vispy_set_current(self):
        self.context.set_current()

    def _vispy_swap_buffers(self):
        self.context.swap_buffers()

    def _vispy_set_title(self, title):
        self._set_text_property('WM_NAME', title.encode('ASCII'),
                                allow_utf8=False)
        self._set_text_property('WM_ICON_NAME', title.encode('ASCII'),
                                allow_utf8=False)
        self._set_text_property('_NET_WM_NAME', title.encode('ASCII'))
        self._set_text_property('_NET_WM_ICON_NAME', title.encode('ASCII'))

    def _vispy_set_size(self, w, h):
        if self._fullscreen:
            raise RuntimeError('Cannot set size of fullscreen window.')
        self._width = w
        self._height = h
        if not self._resizable:
            self._set_minmax_size(self._width, self._height)
        xlib.XResizeWindow(self._x_display, self._window,
                           self._width, self._height)

    def _vispy_set_fullscreen(self, fullscreen):
        raise NotImplementedError()

    def _vispy_update(self):
        if self._vispy_canvas is None or self._window is None:
            return
        self._needs_draw = True

    def _vispy_get_size(self):
        attrs = xlib.XWindowAttributes()
        xlib.XGetWindowAttributes(self._x_display, self._window, byref(attrs))
        return attrs.width, attrs.height

    def _vispy_set_position(self, x, y):
        if self._is_reparented():
            attrs = xlib.XWindowAttributes()
            xlib.XGetWindowAttributes(self._x_display, self._window,
                                      byref(attrs))
            x -= attrs.x
            y -= attrs.y
        xlib.XMoveWindow(self._x_display, self._window, x, y)

    def _vispy_get_position(self):
        child = xlib.Window()
        x, y = c_int(), c_int()
        xlib.XTranslateCoordinates(self._x_display, self._window,
                                   self._get_root(), 0, 0,
                                   byref(x), byref(y), byref(child))
        return x.value, y.value

    def _vispy_set_visible(self, visible):
        self._map() if visible else self._unmap()

    def _poll_events(self):
        if self._window is None:
            return
        # Check for the events specific to this window, view, then close event
        e = xlib.XEvent()
        check = xlib.XCheckWindowEvent
        while self._window is not None and \
                check(self._x_display, self._window, 0x1ffffff, byref(e)):
            # Key events are filtered by the xlib window event
            # handler so they get a shot at the prefiltered event.
            if e.xany.type not in (xlib.KeyPress, xlib.KeyRelease):
                if xlib.XFilterEvent(e, 0):
                    continue
            self._event_handlers.get(e.type, _pass)(e)
        while self._window is not None and \
                check(self._x_display, self._window,
                      xlib.ClientMessage, byref(e)):
            self._event_handlers.get(e.type, _pass)(e)

    def _on_draw(self):
        self._vispy_set_current()
        self._vispy_canvas.events.draw(region=None)  # (0, 0, w, h))

    def _event_key(self, ev):
        key, buf = xlib.KeySym(), create_string_buffer(128)
        xlib.XLookupString(ev.xkey, buf, len(buf) - 1, byref(key), None)
        key = int(key.value)
        if 97 <= key <= 122:
            key -= 32
        if key in KEYMAP:
            key = KEYMAP[key]
        elif key >= 32 and key <= 127:
            key = keys.Key(chr(key))
        else:
            return  # unknown key
        m = _translate_modifiers(ev.xkey.state)
        if ev.type == xlib.KeyPress:
            self._vispy_canvas.events.key_press(key=key, text='', modifiers=m)
        elif ev.type == xlib.KeyRelease and key:
            self._vispy_canvas.events.key_release(key=key, text='',
                                                  modifiers=m)

    def _event_motion(self, ev):
        x, y = ev.xmotion.x, ev.xmotion.y
        m = _translate_modifiers(ev.xkey.state)
        self._vispy_canvas.events.mouse_move(pos=(x, y), modifiers=m)

    def _event_clientmessage(self, ev):
        atom = ev.xclient.data.l[0]
        if atom == xlib.XInternAtom(ev.xclient.display,
                                    'WM_DELETE_WINDOW'.encode('ASCII'), False):
            self._vispy_canvas.close()

    def _event_button(self, ev):
        x, y = ev.xmotion.x, ev.xmotion.y
        m = _translate_modifiers(ev.xbutton.state)
        button = ev.xbutton.button  # already 1, 2, 3 as we need
        if ev.type == xlib.ButtonPress:
            if ev.xbutton.button in (4, 5):
                dy = 1. if ev.xbutton.button == 4 else -1.
                self._vispy_canvas.events.mouse_wheel(pos=(x, y),
                                                      delta=(0, dy),
                                                      modifiers=m)
            elif ev.xbutton.button < 4:
                self._vispy_canvas.events.mouse_press(pos=(x, y),
                                                      button=button,
                                                      modifiers=m)
        else:
            if ev.xbutton.button < 4:
                self._vispy_canvas.events.mouse_release(pos=(x, y),
                                                        button=button,
                                                        modifiers=m)

    def _event_configure(self, ev):
        if self._fullscreen:
            return
        w, h = ev.xconfigure.width, ev.xconfigure.height
        if self._width != w or self._height != h:
            self._width, self._height = w, h
            self._vispy_canvas.events.resize(size=(self._width, self._height))
