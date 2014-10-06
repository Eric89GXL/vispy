# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

import sys

from ...base import BaseApplicationBackend, BaseTimerBackend
from ....util.ptime import time

available = testable = False
why_not = 'Unsupported OS (%s)' % sys.platform
which = 'Native'
capability = {}

if sys.platform.startswith('win'):
    from ._win32 import CanvasBackend, _VP_NATIVE_ALL_WINDOWS  # noqa
elif sys.platform == 'darwin':
    from ._cocoa import CanvasBackend, _VP_NATIVE_ALL_WINDOWS  # noqa
elif sys.platform.startswith('linux'):
    from ._xorg import CanvasBackend, _VP_NATIVE_ALL_WINDOWS  # noqa
else:
    raise NotImplementedError(why_not)

available = testable = True
why_not = None

# -------------------------------------------------------------- capability ---

capability = dict(  # things that can be set by the backend
    title=True,
    size=True,
    position=True,
    show=True,
    vsync=True,
    resizable=True,
    decorate=True,
    fullscreen=True,
    context=True,
    multi_window=True,
    scroll=True,
    parent=False,
)


# ------------------------------------------------------------- application ---

def _get_windows():
    wins = list()
    for win in _VP_NATIVE_ALL_WINDOWS:
        if isinstance(win, CanvasBackend):
            wins.append(win)
    return wins


class ApplicationBackend(BaseApplicationBackend):

    def __init__(self):
        BaseApplicationBackend.__init__(self)
        self._timers = list()

    def _add_timer(self, timer):
        if timer not in self._timers:
            self._timers.append(timer)

    def _vispy_get_backend_name(self):
        return 'Native'

    def _vispy_process_events(self):
        for timer in self._timers:
            timer._tick()
        wins = _get_windows()
        for win in wins:
            win._poll_events()
            if win._needs_draw:
                win._needs_draw = False
                win._on_draw()

    def _vispy_run(self):
        wins = _get_windows()
        while any(not w._closed for w in wins):
            self._vispy_process_events()
        self._vispy_quit()  # to clean up

    def _vispy_quit(self):
        # Close windows
        wins = _get_windows()
        for win in wins:
            if win._vispy_canvas is not None:
                win._vispy_canvas.close()
        # tear down timers
        for timer in self._timers:
            timer._vispy_stop()
        self._timers = []

    def _vispy_get_native_app(self):
        return self


# ------------------------------------------------------------------- timer ---

class TimerBackend(BaseTimerBackend):

    def __init__(self, vispy_timer):
        BaseTimerBackend.__init__(self, vispy_timer)
        vispy_timer._app._backend._add_timer(self)
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
