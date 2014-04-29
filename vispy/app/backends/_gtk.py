# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
vispy backend for GTK.
"""

from __future__ import division

from time import sleep

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend, BaseSharedContext)
from ...util import keys
from ...util.ptime import time


# -------------------------------------------------------------------- init ---

try:
    import gtk
    import gtk.gtkgl

    # Map native keys to vispy keys
    KEYMAP = {
        gtk.keysyms.Shift_L: keys.SHIFT,
        gtk.keysyms.Shift_R: keys.SHIFT,
        gtk.keysyms.Control_L: keys.CONTROL,
        gtk.keysyms.Control_R: keys.CONTROL,
        gtk.keysyms.Alt_L: keys.ALT,
        gtk.keysyms.Alt_R: keys.ALT,
        gtk.keysyms.Meta_L: keys.META,
        gtk.keysyms.Meta_R: keys.META,

        gtk.keysyms.Left: keys.LEFT,
        gtk.keysyms.Up: keys.UP,
        gtk.keysyms.Right: keys.RIGHT,
        gtk.keysyms.Down: keys.DOWN,
        gtk.keysyms.Page_Up: keys.PAGEUP,
        gtk.keysyms.Page_Down: keys.PAGEDOWN,

        gtk.keysyms.Insert: keys.INSERT,
        gtk.keysyms.Delete: keys.DELETE,
        gtk.keysyms.Home: keys.HOME,
        gtk.keysyms.End: keys.END,

        gtk.keysyms.Escape: keys.ESCAPE,
        gtk.keysyms.BackSpace: keys.BACKSPACE,

        gtk.keysyms.F1: keys.F1,
        gtk.keysyms.F2: keys.F2,
        gtk.keysyms.F3: keys.F3,
        gtk.keysyms.F4: keys.F4,
        gtk.keysyms.F5: keys.F5,
        gtk.keysyms.F6: keys.F6,
        gtk.keysyms.F7: keys.F7,
        gtk.keysyms.F8: keys.F8,
        gtk.keysyms.F9: keys.F9,
        gtk.keysyms.F10: keys.F10,
        gtk.keysyms.F11: keys.F11,
        gtk.keysyms.F12: keys.F12,

        gtk.keysyms.space: keys.SPACE,
        gtk.keysyms.KP_Enter: keys.ENTER,
        gtk.keysyms.Return: keys.ENTER,
        gtk.keysyms.Tab: keys.TAB,
    }
    MOUSEMAP = {gtk.gdk.BUTTON_PRESS: 'down',
                gtk.gdk.BUTTON_RELEASE: 'up',
                gtk.gdk._2BUTTON_PRESS: 'double'}

    _DrawingArea = gtk.gtkgl.DrawingArea
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None

    class _DrawingArea(object):
        pass
else:
    available, testable, why_not = True, True, None
    which = 'gtk ' + '.'.join(str(g) for g in gtk.ver)


# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    vsync=False,
    resizable=True,
    decorate=True,
    fullscreen=True,
    context=False,
    multi_window=True,
    scroll=True,
)


# ------------------------------------------------------- set_configuration ---

def _set_config(c):
    """Set gl configuration for GLFW """
    mode = gtk.gdkgl.MODE_RGBA
    mode |= gtk.gdkgl.MODE_DOUBLE if c['double_buffer'] else 0
    mode |= gtk.gdkgl.MODE_MULTISAMPLE if c['samples'] else 0
    mode |= gtk.gdkgl.MODE_STENCIL if c['stencil_size'] else 0
    mode |= gtk.gdkgl.MODE_DEPTH if c['depth_size'] else 0
    mode |= gtk.gdkgl.MODE_STEREO if c['stereo'] else 0
    glconfig = gtk.gdkgl.Config(mode=mode)
    return glconfig


class SharedContext(BaseSharedContext):
    _backend = 'gtk'


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'Glfw'

    def _vispy_process_events(self):
        gtk.gdk.threads_enter()  # enter/leave prevents IPython -gthread hang
        while gtk.events_pending():
            gtk.main_iteration(False)
        gtk.gdk.threads_leave()

    def _vispy_run(self):
        if not hasattr(gtk, 'vv_do_quit'):
            gtk.vv_do_quit = False
        if gtk.main_level() == 0:
            # We need to start the mainloop.  This means we will also
            # have to kill the mainloop when the last figure is closed.
            gtk.vv_do_quit = True
            gtk.main()
        self._vispy_quit()  # to clean up

    def _vispy_quit(self):
        # Close windows
        #wins = _get_gtk_windows()
        #for win in wins:
        #    win._vispy_close()
        if gtk.vv_do_quit:  # We started the mainloop, so we better kill it.
            gtk.main_quit()

    def _vispy_get_native_app(self):
        return gtk


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(BaseCanvasBackend, _DrawingArea):

    """ GTK backend for Canvas abstract class."""

    def __init__(self, **kwargs):
        BaseCanvasBackend.__init__(self, capability, SharedContext)
        title, size, position, show, vsync, resize, dec, fs, context = \
            self._process_backend_kwargs(kwargs)
        # Init GLFW, add window hints, and create window
        assert isinstance(context, dict)
        glconfig = _set_config(context)

        win = gtk.Window()
        win.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        win.set_resizable(True if resize else False)
        win.set_decorated(True if dec else False)
        win.set_reallocate_redraws(True)
        win.fullscreen() if fs else win.unfullscreen()
        win.add_events(
            gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK |
            gtk.gdk.POINTER_MOTION_MASK | gtk.gdk.POINTER_MOTION_HINT_MASK |
            gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.SCROLL_MASK)
        self._win = win
        self._vispy_set_title(title)
        self._vispy_set_size(size[0], size[1])

        _DrawingArea.__init__(self, glconfig)
        self.set_property('can-focus', True)
        win.add(self)
        self._mod = list()

        # Register callbacks XXX
        self.connect_after('realize', self._on_initialize)
        self.connect('configure-event', self._on_resize)
        self.connect('expose-event', self._on_draw)
        self.connect('destroy', self._on_close)

        self._vispy_canvas_ = None
        self._gl_drawable = None

    @property
    def _vispy_context(self):
        """Context to return for sharing"""
        return SharedContext(None)  # cannot share

    ####################################
    # Deal with events we get from vispy
    @property
    def _vispy_canvas(self):
        """ The parent canvas/window """
        return self._vispy_canvas_

    @_vispy_canvas.setter
    def _vispy_canvas(self, vc):
        # Init events when the property is set by Canvas
        self._vispy_canvas_ = vc
        return self._vispy_canvas

    def _vispy_warmup(self):
        pass

    def _vispy_set_current(self):
        # Make this the current context
        if self._gl_drawable is None:
            return
        self._gl_drawable.gl_begin(self.get_gl_context())

    def _vispy_end_current(self):
        # Make this the current context
        if self._gl_drawable is None:
            return
        self._gl_drawable.gl_end()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        self._vispy_set_current()
        self._gl_drawable.swap_buffers()

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        self._win.set_title(title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        self._win.resize(w, h)

    def _vispy_set_position(self, x, y):
        # Set position of the widget or window. May have no effect for widgets
        self._win.move(self, x, y)

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        if visible:
            self.show()
            self._win.show()
        else:
            self._win.hide()

    def _vispy_update(self):
        self.window.invalidate_rect(self.allocation, False)
        self.window.process_updates(False)

    def _vispy_close(self):
        # Force the window or widget to shut down
        self.destroy()

    def _get_allocation(self):
        self._vispy_set_current()
        x, y, w, h = self.get_allocation()
        return x, y, w, h

    def _vispy_get_size(self):
        return self._get_allocation()[2:]

    def _vispy_get_position(self):
        return self._get_allocation()[:2]

    #########################################
    # Notify vispy of events triggered by GTK

    def _on_initialize(self, _id):
        self._gl_drawable = self.get_gl_drawable()
        assert self._gl_drawable
        self._vispy_set_current()
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.initialize()

    def _on_resize(self, _id, event):
        if self._vispy_canvas is None:
            return
        x, y, w, h = self._get_allocation()
        self._vispy_canvas.events.resize(size=(w, h))

    def _on_draw(self, _id, event):
        if self._vispy_canvas is None:
            return
        self._vispy_set_current()
        self._vispy_canvas.events.paint(region=None)  # (0, 0, w, h))

    def _on_close(self, _id):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.close()


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        #vispy_timer._app._backend._add_timer(self)
        self._vispy_stop()

    def _vispy_start(self, interval):
        self._interval = interval
        self._next_time = time() + self._interval

    def _vispy_stop(self):
        self._next_time = float('inf')

    def _tick(self):
        if time() >= self._next_time:
            self._vispy_timer._timeout()
            self._next_time = time() + self._interval
