# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
vispy backend for kivy.
"""

from __future__ import division

from time import sleep

from ..base import (BaseApplicationBackend, BaseCanvasBackend,
                    BaseTimerBackend, BaseSharedContext)
from ...util import keys
from ...util.ptime import time


# -------------------------------------------------------------------- init ---

try:
    from kivy.uix.widget import Widget
    from kivy.config import Config
    # Map native keys to vispy keys
    KEYMAP = {}

    BUTTONMAP = {}
except Exception as exp:
    available, testable, why_not, which = False, False, str(exp), None

    class Widget(self):
        pass
else:
    available, testable, why_not = True, True, None
    which = 'kivy ' + str(kivy.__version__)


# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    vsync=True,
    resizable=True,
    decorate=False,
    fullscreen=True,
    context=False,
    multi_window=False,
    scroll=False,
)


# ------------------------------------------------------- set_configuration ---

def _set_config(config):
    """Set gl configuration
    pyglet_config = pyglet.gl.Config()

    pyglet_config.red_size = config['red_size']
    pyglet_config.green_size = config['green_size']
    pyglet_config.blue_size = config['blue_size']
    pyglet_config.alpha_size = config['alpha_size']

    pyglet_config.accum_red_size = 0
    pyglet_config.accum_green_size = 0
    pyglet_config.accum_blue_size = 0
    pyglet_config.accum_alpha_size = 0

    pyglet_config.depth_size = config['depth_size']
    pyglet_config.stencil_size = config['stencil_size']
    pyglet_config.double_buffer = config['double_buffer']
    pyglet_config.stereo = config['stereo']
    pyglet_config.samples = config['samples']
    """
    raise NotImplementedError
    return None


class SharedContext(BaseSharedContext):
    _backend = 'kivy'


# ------------------------------------------------------------- application ---

class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)

    def _vispy_get_backend_name(self):
        return 'Pyglet'

    def _vispy_process_events(self):
        # pyglet.app.platform_event_loop.step(0.0)
        pyglet.clock.tick()
        for window in pyglet.app.windows:
            window.switch_to()
            window.dispatch_events()
            window.dispatch_event('on_draw')

    def _vispy_run(self):
        return pyglet.app.run()

    def _vispy_quit(self):
        return pyglet.app.exit()

    def _vispy_get_native_app(self):
        return pyglet.app


# ------------------------------------------------------------------ canvas ---

class CanvasBackend(Widget, BaseCanvasBackend):

    """ Pyglet backend for Canvas abstract class."""

    def __init__(self, **kwargs):
        BaseCanvasBackend.__init__(self, capability, SharedContext)
        title, size, position, show, vsync, resize, dec, fs, context = \
            self._process_backend_kwargs(kwargs)
        Config.set('kivy', 'exit_on_escape', 0)
        if position is not None:
            Config.set('graphics', 'position', 'custom')
            Config.set('graphics', 'top', position[0])
            Config.set('graphics', 'left', position[1])
        Config.set('graphics', 'resizable', int(resize))
        if fs is not False:
            if isinstance(fs, int):
                logger.warn('Cannot specify monitor number for kivy '
                            'fullscreen, using default')
            Canfig.set('graphics', 'fullscreen', 'auto')
        Widget.__init__(self)
        layout = FloatLayout(size=(*size))
        layout.add_widget(self)

    @property
    def _vispy_context(self):
        """Context to return for sharing"""
        return SharedContext(None)

    def _vispy_warmup(self):
        etime = time() + 0.25
        while time() < etime:
            sleep(0.01)
            self._vispy_set_current()
            self._vispy_canvas.app.process_events()

    def _vispy_set_current(self):
        # Make this the current context
        self.switch_to()

    def _vispy_swap_buffers(self):
        # Swap front and back buffer
        pyglet.window.Window.flip(self)

    def _vispy_set_title(self, title):
        # Set the window title. Has no effect for widgets
        self.set_caption(title)

    def _vispy_set_size(self, w, h):
        # Set size of the widget or window
        self.set_size(w, h)

    def _vispy_set_position(self, x, y):
        # Set positionof the widget or window. May have no effect for widgets
        if self._draw_ok:
            self.set_location(x, y)
        else:
            self._pending_position = x, y

    def _vispy_set_visible(self, visible):
        # Show or hide the window or widget
        self.set_visible(visible)

    def _vispy_update(self):
        # Invoke a redraw
        pyglet.clock.schedule_once(self.our_paint_func, 0.0)

    def _vispy_close(self):
        # Force the window or widget to shut down
        # In Pyglet close is equivalent to destroy (window becomes invalid)
        self.close()

    def _vispy_get_size(self):
        x, y = self.get_size()
        return x, y

    def _vispy_get_position(self):
        w, h = self.get_location()
        return w, h

    def on_show(self):
        if self._vispy_canvas is None:
            return
        self._vispy_set_current()
        self._vispy_canvas.events.initialize()
        # Set location now if we must. For some reason we get weird
        # offsets in viewport if set_location is called before the
        # widget is shown.
        if self._pending_position:
            x, y = self._pending_position
            self._pending_position = None
            self.set_location(x, y)
        # Redraw
        self._vispy_update()

    def on_close(self):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.close()
        #self.close()  # Or the window wont close
        # AK: seems so wrong to try a close in the close event handler ...

    def on_resize(self, w, h):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.resize(size=(w, h))
        # self._vispy_update()

    def our_paint_func(self, dummy=None):
        if not self._draw_ok or self._vispy_canvas is None:
            return
        # (0, 0, self.width, self.height))
        self._vispy_set_current()
        self._vispy_canvas.events.paint(region=None)

    def on_mouse_press(self, x, y, button, modifiers=None):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_press(
            pos=(x, self.get_size()[1] - y),
            button=BUTTONMAP.get(button, 0),
            modifiers=self._modifiers(),
        )
#         if ev2.handled:
#             self._buttons_accepted |= button

    def on_mouse_release(self, x, y, button, modifiers=None):
        if self._vispy_canvas is None:
            return
        if True:  # (button & self._buttons_accepted) > 0:
            self._vispy_mouse_release(
                pos=(x, self.get_size()[1] - y),
                button=BUTTONMAP.get(button, 0),
                modifiers=self._modifiers(),
            )
            #self._buttons_accepted &= ~button

    def on_mouse_motion(self, x, y, dx, dy):
        if self._vispy_canvas is None:
            return
        self._vispy_mouse_move(
            pos=(x, self.get_size()[1] - y),
            modifiers=self._modifiers(),
        )

    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.on_mouse_motion(x, y, dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self._vispy_canvas is None:
            return
        self._vispy_canvas.events.mouse_wheel(
            delta=(float(scroll_x), float(scroll_y)),
            pos=(x, y),
            modifiers=self._modifiers(),
        )

    def on_key_press(self, key, modifiers):
        # Process modifiers
        if key in (pyglet.window.key.LCTRL, pyglet.window.key.RCTRL,
                   pyglet.window.key.LALT, pyglet.window.key.RALT,
                   pyglet.window.key.LSHIFT, pyglet.window.key.RSHIFT):
            self._current_modifiers.add(key)
        # Emit
        self._vispy_canvas.events.key_press(
            key=self._processKey(key),
            text='',  # Handlers that trigger on text wont see this event
            modifiers=self._modifiers(modifiers))

    def on_text(self, text):
        # Typically this is called after on_key_press and before
        # on_key_release
        self._vispy_canvas.events.key_press(
            key=None,  # Handlers that trigger on key wont see this event
            text=text,
            modifiers=self._modifiers())

    def on_key_release(self, key, modifiers):
        # Process modifiers
        if key in (pyglet.window.key.LCTRL, pyglet.window.key.RCTRL,
                   pyglet.window.key.LALT, pyglet.window.key.RALT,
                   pyglet.window.key.LSHIFT, pyglet.window.key.RSHIFT):
            self._current_modifiers.discard(key)
        # Get txt
        try:
            text = chr(key)
        except Exception:
            text = ''
        # Emit
        self._vispy_canvas.events.key_release(
            key=self._processKey(key), text=text,
            modifiers=self._modifiers(modifiers))

    def _processKey(self, key):
        if 97 <= key <= 122:
            key -= 32
        if key in KEYMAP:
            return KEYMAP[key]
        elif key >= 32 and key <= 127:
            return keys.Key(chr(key))
        else:
            return None

    def _modifiers(self, pygletmod=None):
        mod = ()
        if pygletmod is None:
            pygletmod = self._current_modifiers
        if isinstance(pygletmod, set):
            for key in pygletmod:
                mod += KEYMAP[key],
        else:
            if pygletmod & pyglet.window.key.MOD_SHIFT:
                mod += keys.SHIFT,
            if pygletmod & pyglet.window.key.MOD_CTRL:
                mod += keys.CONTROL,
            if pygletmod & pyglet.window.key.MOD_ALT:
                mod += keys.ALT,
        return mod


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):

    def _vispy_start(self, interval):
        interval = self._vispy_timer._interval
        if self._vispy_timer.max_iterations == 1:
            pyglet.clock.schedule_once(self._vispy_timer._timeout, interval)
        else:
            # seems pyglet does not give the expected behavior when interval==0
            if interval == 0:
                interval = 1e-9
            pyglet.clock.schedule_interval(
                self._vispy_timer._timeout,
                interval)

    def _vispy_stop(self):
        pyglet.clock.unschedule(self._vispy_timer._timeout)

    def _vispy_get_native_timer(self):
        return pyglet.clock
