# Adapted from Pyglet
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

from ctypes import (Structure, POINTER, CFUNCTYPE, util, cdll, Union,
                    c_int, c_uint, c_long, c_ulong, c_char_p, c_ubyte, c_char)


_fname = util.find_library('X11')
if not _fname:
    raise RuntimeError('Could not load the X11 library.')
_lib = cdll.LoadLibrary(_fname)


Atom = c_ulong 	# /usr/include/X11/X.h:74
VisualID = c_ulong 	# /usr/include/X11/X.h:76
XPointer = c_char_p 	# /usr/include/X11/Xlib.h:87

XA_CARDINAL = 6  # Xatom.h:14


XID = c_ulong 	# /usr/include/X11/X.h:66
Time = c_ulong 	# /usr/include/X11/X.h:77
Window = XID 	# /usr/include/X11/X.h:96
Drawable = XID 	# /usr/include/X11/X.h:97
Pixmap = XID 	# /usr/include/X11/X.h:102
Cursor = XID 	# /usr/include/X11/X.h:103
Colormap = XID 	# /usr/include/X11/X.h:104
KeySym = XID 	# /usr/include/X11/X.h:106
PointerMotionHintMask = 128 	# /usr/include/X11/X.h:158
ResizeRedirectMask = 262144 	# /usr/include/X11/X.h:169
SubstructureNotifyMask = 524288 	# /usr/include/X11/X.h:170
SubstructureRedirectMask = 1048576 	# /usr/include/X11/X.h:171
KeyPress = 2 	# /usr/include/X11/X.h:181
KeyRelease = 3 	# /usr/include/X11/X.h:182
ButtonPress = 4 	# /usr/include/X11/X.h:183
ButtonRelease = 5 	# /usr/include/X11/X.h:184
MotionNotify = 6 	# /usr/include/X11/X.h:185
UnmapNotify = 18 	# /usr/include/X11/X.h:197
MapNotify = 19 	# /usr/include/X11/X.h:198
ConfigureNotify = 22 	# /usr/include/X11/X.h:201
ClientMessage = 33 	# /usr/include/X11/X.h:212
ShiftMask = 1 	# /usr/include/X11/X.h:221
ControlMask = 4 	# /usr/include/X11/X.h:223
Mod1Mask = 8 	# /usr/include/X11/X.h:224
Mod4Mask = 64 	# /usr/include/X11/X.h:227
InputOutput = 1 	# /usr/include/X11/X.h:387
CWBackPixel = 2 	# /usr/include/X11/X.h:393
CWBitGravity = 16 	# /usr/include/X11/X.h:396
CWColormap = 8192 	# /usr/include/X11/X.h:405
StaticGravity = 10 	# /usr/include/X11/X.h:431
PropModeReplace = 0 	# /usr/include/X11/X.h:475
PropModePrepend = 1 	# /usr/include/X11/X.h:476
AllocNone = 0 	# /usr/include/X11/X.h:616
PMinSize = 16 	# /usr/include/X11/Xutil.h:4844
PMaxSize = 32 	# /usr/include/X11/Xutil.h:4845


class XExtData(Structure):
    __slots__ = ['number', 'next', 'free_private', 'private_data']
XExtData._fields_ = [
    ('number', c_int), ('next', POINTER(XExtData)),
    ('free_private', POINTER(CFUNCTYPE(c_int, POINTER(XExtData)))),
    ('private_data', XPointer)]


class Visual(Structure):
    __slots__ = ['ext_data', 'visualid', 'class', 'red_mask', 'green_mask',
                 'blue_mask', 'bits_per_rgb', 'map_entries']
Visual._fields_ = [
    ('ext_data', POINTER(XExtData)), ('visualid', VisualID), ('class', c_int),
    ('red_mask', c_ulong), ('green_mask', c_ulong), ('blue_mask', c_ulong),
    ('bits_per_rgb', c_int), ('map_entries', c_int)]


class XVisualInfo(Structure):
    __slots__ = ['visual', 'visualid', 'screen', 'depth', 'class', 'red_mask',
                 'green_mask', 'blue_mask', 'colormap_size', 'bits_per_rgb']
XVisualInfo._fields_ = [
    ('visual', POINTER(Visual)), ('visualid', VisualID), ('screen', c_int),
    ('depth', c_int), ('class', c_int), ('red_mask', c_ulong),
    ('green_mask', c_ulong), ('blue_mask', c_ulong), ('colormap_size', c_int),
    ('bits_per_rgb', c_int)]


class Display(Structure):
    __slots__ = []
Display._fields_ = [('_opaque_struct', c_int)]


class XSizeHints(Structure):
    __slots__ = ['flags', 'x', 'y', 'width', 'height', 'min_width',
                 'min_height', 'max_width', 'max_height', 'width_inc',
                 'height_inc', 'min_aspect', 'max_aspect', 'base_width',
                 'base_height', 'win_gravity']


class struct_anon_96(Structure):
    __slots__ = ['x', 'y']
struct_anon_96._fields_ = [('x', c_int), ('y', c_int)]


class struct_anon_97(Structure):
    __slots__ = ['x', 'y']
struct_anon_97._fields_ = [('x', c_int), ('y', c_int)]

XSizeHints._fields_ = [
    ('flags', c_long), ('x', c_int), ('y', c_int), ('width', c_int),
    ('height', c_int), ('min_width', c_int), ('min_height', c_int),
    ('max_width', c_int), ('max_height', c_int), ('width_inc', c_int),
    ('height_inc', c_int), ('min_aspect', struct_anon_96),
    ('max_aspect', struct_anon_97), ('base_width', c_int),
    ('base_height', c_int), ('win_gravity', c_int)]


class XSetWindowAttributes(Structure):
    __slots__ = ['background_pixmap', 'background_pixel', 'border_pixmap',
                 'border_pixel', 'bit_gravity', 'win_gravity',
                 'backing_store', 'backing_planes', 'backing_pixel',
                 'save_under', 'event_mask', 'do_not_propagate_mask',
                 'override_redirect', 'colormap', 'cursor']
XSetWindowAttributes._fields_ = [
    ('background_pixmap', Pixmap), ('background_pixel', c_ulong),
    ('border_pixmap', Pixmap), ('border_pixel', c_ulong),
    ('bit_gravity', c_int), ('win_gravity', c_int), ('backing_store', c_int),
    ('backing_planes', c_ulong), ('backing_pixel', c_ulong),
    ('save_under', c_int), ('event_mask', c_long),
    ('do_not_propagate_mask', c_long), ('override_redirect', c_int),
    ('colormap', Colormap), ('cursor', Cursor)]


##############################################################################
# EVENTS

class XKeyEvent(Structure):
    __slots__ = ['type', 'serial', 'send_event', 'display', 'window', 'root',
                 'subwindow', 'time', 'x', 'y', 'x_root', 'y_root', 'state',
                 'keycode', 'same_screen']
XKeyEvent._fields_ = [
    ('type', c_int), ('serial', c_ulong), ('send_event', c_int),
    ('display', POINTER(Display)), ('window', Window), ('root', Window),
    ('subwindow', Window), ('time', Time), ('x', c_int), ('y', c_int),
    ('x_root', c_int), ('y_root', c_int), ('state', c_uint),
    ('keycode', c_uint), ('same_screen', c_int)]
XKeyPressedEvent = XKeyEvent 	# /usr/include/X11/Xlib.h:583
XKeyReleasedEvent = XKeyEvent 	# /usr/include/X11/Xlib.h:584


class XButtonEvent(Structure):
    __slots__ = ['type', 'serial', 'send_event', 'display', 'window', 'root',
                 'subwindow', 'time', 'x', 'y', 'x_root', 'y_root', 'state',
                 'button', 'same_screen']
XButtonEvent._fields_ = [
    ('type', c_int), ('serial', c_ulong), ('send_event', c_int),
    ('display', POINTER(Display)), ('window', Window), ('root', Window),
    ('subwindow', Window), ('time', Time), ('x', c_int), ('y', c_int),
    ('x_root', c_int), ('y_root', c_int), ('state', c_uint),
    ('button', c_uint), ('same_screen', c_int)]
XButtonPressedEvent = XButtonEvent 	# /usr/include/X11/Xlib.h:601
XButtonReleasedEvent = XButtonEvent 	# /usr/include/X11/Xlib.h:602


class struct_anon_39(Structure):
    __slots__ = ['type', 'serial', 'send_event', 'display', 'window',
                 'root', 'subwindow', 'time', 'x', 'y', 'x_root',
                 'y_root', 'state', 'is_hint', 'same_screen']
struct_anon_39._fields_ = [
    ('type', c_int), ('serial', c_ulong), ('send_event', c_int),
    ('display', POINTER(Display)), ('window', Window), ('root', Window),
    ('subwindow', Window), ('time', Time), ('x', c_int), ('y', c_int),
    ('x_root', c_int), ('y_root', c_int), ('state', c_uint),
    ('is_hint', c_char), ('same_screen', c_int)]
XMotionEvent = struct_anon_39 	# /usr/include/X11/Xlib.h:618
XPointerMovedEvent = XMotionEvent 	# /usr/include/X11/Xlib.h:619


class XCrossingEvent(Structure):
    __slots__ = ['type', 'serial', 'send_event', 'display', 'window', 'root',
                 'subwindow', 'time', 'x', 'y', 'x_root', 'y_root', 'mode',
                 'detail', 'same_screen', 'focus', 'state']
XCrossingEvent._fields_ = [
    ('type', c_int), ('serial', c_ulong), ('send_event', c_int),
    ('display', POINTER(Display)), ('window', Window), ('root', Window),
    ('subwindow', Window), ('time', Time), ('x', c_int), ('y', c_int),
    ('x_root', c_int), ('y_root', c_int), ('mode', c_int), ('detail', c_int),
    ('same_screen', c_int), ('focus', c_int), ('state', c_uint)]
XEnterWindowEvent = XCrossingEvent 	# /usr/include/X11/Xlib.h:642
XLeaveWindowEvent = XCrossingEvent 	# /usr/include/X11/Xlib.h:643


class XFocusChangeEvent(Structure):
    __slots__ = ['type', 'serial', 'send_event', 'display', 'window',
                 'mode', 'detail']
XFocusChangeEvent._fields_ = [
    ('type', c_int), ('serial', c_ulong), ('send_event', c_int),
    ('display', POINTER(Display)), ('window', Window), ('mode', c_int),
    ('detail', c_int)]
XFocusInEvent = XFocusChangeEvent 	# /usr/include/X11/Xlib.h:660
XFocusOutEvent = XFocusChangeEvent 	# /usr/include/X11/Xlib.h:661


class XKeymapEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'key_vector',
    ]
XKeymapEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('key_vector', c_char * 32),
]


class XExposeEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'x',
        'y',
        'width',
        'height',
        'count',
    ]
XExposeEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
    ('count', c_int),
]


class XGraphicsExposeEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'drawable',
        'x',
        'y',
        'width',
        'height',
        'count',
        'major_code',
        'minor_code',
    ]
XGraphicsExposeEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('drawable', Drawable),
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
    ('count', c_int),
    ('major_code', c_int),
    ('minor_code', c_int),
]


class XNoExposeEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'drawable',
        'major_code',
        'minor_code',
    ]
XNoExposeEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('drawable', Drawable),
    ('major_code', c_int),
    ('minor_code', c_int),
]


class XVisibilityEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'state',
    ]
XVisibilityEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('state', c_int),
]


class XCreateWindowEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'parent',
        'window',
        'x',
        'y',
        'width',
        'height',
        'border_width',
        'override_redirect',
    ]
XCreateWindowEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('parent', Window),
    ('window', Window),
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
    ('border_width', c_int),
    ('override_redirect', c_int),
]


class XDestroyWindowEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'event',
        'window',
    ]
XDestroyWindowEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('event', Window),
    ('window', Window),
]


class XUnmapEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'event',
        'window',
        'from_configure',
    ]
XUnmapEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('event', Window),
    ('window', Window),
    ('from_configure', c_int),
]


class XMapEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'event',
        'window',
        'override_redirect',
    ]
XMapEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('event', Window),
    ('window', Window),
    ('override_redirect', c_int),
]


class XMapRequestEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'parent',
        'window',
    ]
XMapRequestEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('parent', Window),
    ('window', Window),
]


class XReparentEvent(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'event',
        'window',
        'parent',
        'x',
        'y',
        'override_redirect',
    ]
XReparentEvent._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('event', Window),
    ('window', Window),
    ('parent', Window),
    ('x', c_int),
    ('y', c_int),
    ('override_redirect', c_int),
]


class struct_anon_53(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'event',
        'window',
        'x',
        'y',
        'width',
        'height',
        'border_width',
        'above',
        'override_redirect',
    ]
struct_anon_53._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('event', Window),
    ('window', Window),
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
    ('border_width', c_int),
    ('above', Window),
    ('override_redirect', c_int),
]

XConfigureEvent = struct_anon_53 	# /usr/include/X11/Xlib.h:791
class struct_anon_54(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'event',
        'window',
        'x',
        'y',
    ]
struct_anon_54._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('event', Window),
    ('window', Window),
    ('x', c_int),
    ('y', c_int),
]

XGravityEvent = struct_anon_54 	# /usr/include/X11/Xlib.h:801
class struct_anon_55(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'width',
        'height',
    ]
struct_anon_55._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('width', c_int),
    ('height', c_int),
]

XResizeRequestEvent = struct_anon_55 	# /usr/include/X11/Xlib.h:810
class struct_anon_56(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'parent',
        'window',
        'x',
        'y',
        'width',
        'height',
        'border_width',
        'above',
        'detail',
        'value_mask',
    ]
struct_anon_56._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('parent', Window),
    ('window', Window),
    ('x', c_int),
    ('y', c_int),
    ('width', c_int),
    ('height', c_int),
    ('border_width', c_int),
    ('above', Window),
    ('detail', c_int),
    ('value_mask', c_ulong),
]

XConfigureRequestEvent = struct_anon_56 	# /usr/include/X11/Xlib.h:825
class struct_anon_57(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'event',
        'window',
        'place',
    ]
struct_anon_57._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('event', Window),
    ('window', Window),
    ('place', c_int),
]

XCirculateEvent = struct_anon_57 	# /usr/include/X11/Xlib.h:835
class struct_anon_58(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'parent',
        'window',
        'place',
    ]
struct_anon_58._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('parent', Window),
    ('window', Window),
    ('place', c_int),
]

XCirculateRequestEvent = struct_anon_58 	# /usr/include/X11/Xlib.h:845
class struct_anon_59(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'atom',
        'time',
        'state',
    ]
struct_anon_59._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('atom', Atom),
    ('time', Time),
    ('state', c_int),
]

XPropertyEvent = struct_anon_59 	# /usr/include/X11/Xlib.h:856
class struct_anon_60(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'selection',
        'time',
    ]
struct_anon_60._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('selection', Atom),
    ('time', Time),
]

XSelectionClearEvent = struct_anon_60 	# /usr/include/X11/Xlib.h:866
class struct_anon_61(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'owner',
        'requestor',
        'selection',
        'target',
        'property',
        'time',
    ]
struct_anon_61._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('owner', Window),
    ('requestor', Window),
    ('selection', Atom),
    ('target', Atom),
    ('property', Atom),
    ('time', Time),
]

XSelectionRequestEvent = struct_anon_61 	# /usr/include/X11/Xlib.h:879
class struct_anon_62(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'requestor',
        'selection',
        'target',
        'property',
        'time',
    ]
struct_anon_62._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('requestor', Window),
    ('selection', Atom),
    ('target', Atom),
    ('property', Atom),
    ('time', Time),
]

XSelectionEvent = struct_anon_62 	# /usr/include/X11/Xlib.h:891
class struct_anon_63(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'colormap',
        'new',
        'state',
    ]
struct_anon_63._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('colormap', Colormap),
    ('new', c_int),
    ('state', c_int),
]

XColormapEvent = struct_anon_63 	# /usr/include/X11/Xlib.h:906
class struct_anon_64(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'message_type',
        'format',
        'data',
    ]
class struct_anon_65(Union):
    __slots__ = [
        'b',
        's',
        'l',
    ]
struct_anon_65._fields_ = [
    ('b', c_char * 20),
    ('s', c_short * 10),
    ('l', c_long * 5),
]

struct_anon_64._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('message_type', Atom),
    ('format', c_int),
    ('data', struct_anon_65),
]

XClientMessageEvent = struct_anon_64 	# /usr/include/X11/Xlib.h:921
class struct_anon_66(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
        'request',
        'first_keycode',
        'count',
    ]
struct_anon_66._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
    ('request', c_int),
    ('first_keycode', c_int),
    ('count', c_int),
]

XMappingEvent = struct_anon_66 	# /usr/include/X11/Xlib.h:933
class struct_anon_67(Structure):
    __slots__ = [
        'type',
        'display',
        'resourceid',
        'serial',
        'error_code',
        'request_code',
        'minor_code',
    ]
struct_anon_67._fields_ = [
    ('type', c_int),
    ('display', POINTER(Display)),
    ('resourceid', XID),
    ('serial', c_ulong),
    ('error_code', c_ubyte),
    ('request_code', c_ubyte),
    ('minor_code', c_ubyte),
]

XErrorEvent = struct_anon_67 	# /usr/include/X11/Xlib.h:943
class struct_anon_68(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'window',
    ]
struct_anon_68._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('window', Window),
]

XAnyEvent = struct_anon_68 	# /usr/include/X11/Xlib.h:951
class struct_anon_69(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'extension',
        'evtype',
    ]
struct_anon_69._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('extension', c_int),
    ('evtype', c_int),
]

XGenericEvent = struct_anon_69 	# /usr/include/X11/Xlib.h:967
class struct_anon_70(Structure):
    __slots__ = [
        'type',
        'serial',
        'send_event',
        'display',
        'extension',
        'evtype',
        'cookie',
        'data',
    ]
struct_anon_70._fields_ = [
    ('type', c_int),
    ('serial', c_ulong),
    ('send_event', c_int),
    ('display', POINTER(Display)),
    ('extension', c_int),
    ('evtype', c_int),
    ('cookie', c_uint),
    ('data', POINTER(None)),
]

XGenericEventCookie = struct_anon_70 	# /usr/include/X11/Xlib.h:978


class XEvent(Union):
    __slots__ = [
        'type',
        'xany',
        'xkey',
        'xbutton',
        'xmotion',
        'xcrossing',
        'xfocus',
        'xexpose',
        'xgraphicsexpose',
        'xnoexpose',
        'xvisibility',
        'xcreatewindow',
        'xdestroywindow',
        'xunmap',
        'xmap',
        'xmaprequest',
        'xreparent',
        'xconfigure',
        'xgravity',
        'xresizerequest',
        'xconfigurerequest',
        'xcirculate',
        'xcirculaterequest',
        'xproperty',
        'xselectionclear',
        'xselectionrequest',
        'xselection',
        'xcolormap',
        'xclient',
        'xmapping',
        'xerror',
        'xkeymap',
        'xgeneric',
        'xcookie',
        'pad',
    ]
XEvent._fields_ = [
    ('type', c_int),
    ('xany', XAnyEvent),
    ('xkey', XKeyEvent),
    ('xbutton', XButtonEvent),
    ('xmotion', XMotionEvent),
    ('xcrossing', XCrossingEvent),
    ('xfocus', XFocusChangeEvent),
    ('xexpose', XExposeEvent),
    ('xgraphicsexpose', XGraphicsExposeEvent),
    ('xnoexpose', XNoExposeEvent),
    ('xvisibility', XVisibilityEvent),
    ('xcreatewindow', XCreateWindowEvent),
    ('xdestroywindow', XDestroyWindowEvent),
    ('xunmap', XUnmapEvent),
    ('xmap', XMapEvent),
    ('xmaprequest', XMapRequestEvent),
    ('xreparent', XReparentEvent),
    ('xconfigure', XConfigureEvent),
    ('xgravity', XGravityEvent),
    ('xresizerequest', XResizeRequestEvent),
    ('xconfigurerequest', XConfigureRequestEvent),
    ('xcirculate', XCirculateEvent),
    ('xcirculaterequest', XCirculateRequestEvent),
    ('xproperty', XPropertyEvent),
    ('xselectionclear', XSelectionClearEvent),
    ('xselectionrequest', XSelectionRequestEvent),
    ('xselection', XSelectionEvent),
    ('xcolormap', XColormapEvent),
    ('xclient', XClientMessageEvent),
    ('xmapping', XMappingEvent),
    ('xerror', XErrorEvent),
    ('xkeymap', XKeymapEvent),
    ('xgeneric', XGenericEvent),
    ('xcookie', XGenericEventCookie),
    ('pad', c_long * 24),
]

##############################################################################
# FUNCTIONS

XAllocSizeHints = _lib.XAllocSizeHints
XAllocSizeHints.restype = POINTER(XSizeHints)
XAllocSizeHints.argtypes = []

XChangeProperty = _lib.XChangeProperty
XChangeProperty.restype = c_int
XChangeProperty.argtypes = [POINTER(Display), Window, Atom, Atom, c_int, c_int,
                            POINTER(c_ubyte), c_int]

XChangeWindowAttributes = _lib.XChangeWindowAttributes
XChangeWindowAttributes.restype = c_int
XChangeWindowAttributes.argtypes = [POINTER(Display), Window, c_ulong,
                                    POINTER(XSetWindowAttributes)]

XCheckWindowEvent = _lib.XCheckWindowEvent
XCheckWindowEvent.restype = c_int
XCheckWindowEvent.argtypes = [POINTER(Display), Window, c_long,
                              POINTER(XEvent)]

XCreateColormap
XCreateWindow
XDefaultColormap
XDefaultVisual
XDeleteProperty
XEvent
XFilterEvent
XGetWindowAttributes
XInternAtom
XLookupString
XMapWindow
XMapRaised
XMoveResizeWindow
XMoveWindow
XNextEvent
XOpenDisplay
XQueryTree
XResizeWindow
XRootWindow
XScreenCount
XScreenOfDisplay
XSelectInput
XSetTextProperty
XSetWindowAttributes
XSetWMProtocols
XStringListToTextProperty
XTextProperty
XTranslateCoordinates
XUnmapWindow
XVisualIDFromVisual
XWindowAttributes
