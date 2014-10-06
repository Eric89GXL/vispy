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

from ctypes import (Structure, POINTER, CFUNCTYPE, cast, pointer, cdll, util,
                    create_string_buffer, c_int, c_ulong, c_char_p, c_ubyte)

from .xlib import XVisualInfo, Display

GLX_VENDOR = 1 	# /usr/include/GL/glx.h:104
GLX_VERSION = 2 	# /usr/include/GL/glx.h:105
# H (/usr/include/GL/glx.h:26)
GLX_BUFFER_SIZE = 2
GLX_LEVEL = 3
GLX_DOUBLEBUFFER = 5
GLX_STEREO = 6
GLX_AUX_BUFFERS = 7
GLX_RED_SIZE = 8
GLX_GREEN_SIZE = 9 	# /usr/include/GL/glx.h:78
GLX_BLUE_SIZE = 10 	# /usr/include/GL/glx.h:79
GLX_ALPHA_SIZE = 11 	# /usr/include/GL/glx.h:80
GLX_DEPTH_SIZE = 12 	# /usr/include/GL/glx.h:81
GLX_STENCIL_SIZE = 13 	# /usr/include/GL/glx.h:82
GLX_ACCUM_RED_SIZE = 14 	# /usr/include/GL/glx.h:83
GLX_ACCUM_GREEN_SIZE = 15 	# /usr/include/GL/glx.h:84
GLX_ACCUM_BLUE_SIZE = 16 	# /usr/include/GL/glx.h:85
GLX_ACCUM_ALPHA_SIZE = 17 	# /usr/include/GL/glx.h:86
GLX_RGBA = 4 	# /usr/include/GL/glx.h:73
GLX_SAMPLES = 100001 	# /usr/include/GL/glx.h:174
GLX_X_RENDERABLE = 32786 	# /usr/include/GL/glx.h:147
GLX_RGBA_TYPE = 32788 	# /usr/include/GL/glx.h:149
GLX_BAD_CONTEXT = 5 	# /usr/include/GL/glx.h:96

# From glxproto.h
GLXBadFBConfig = 9


class struct___GLXcontextRec(Structure):
    __slots__ = []
struct___GLXcontextRec._fields_ = [('_opaque_struct', c_int)]


class struct___GLXcontextRec(Structure):
    __slots__ = []
struct___GLXcontextRec._fields_ = [('_opaque_struct', c_int)]


GLXContext = POINTER(struct___GLXcontextRec) 	# /usr/include/GL/glx.h:178
XID = c_ulong 	# /usr/include/X11/X.h:66
GLXPixmap = XID 	# /usr/include/GL/glx.h:179
GLXDrawable = XID 	# /usr/include/GL/glx.h:180


class struct___GLXFBConfigRec(Structure):
    __slots__ = []
struct___GLXFBConfigRec._fields_ = [('_opaque_struct', c_int)]


class struct___GLXFBConfigRec(Structure):
    __slots__ = [
    ]
struct___GLXFBConfigRec._fields_ = [
    ('_opaque_struct', c_int)
]

GLXFBConfig = POINTER(struct___GLXFBConfigRec) 	# /usr/include/GL/glx.h:182
GLXFBConfigID = XID 	# /usr/include/GL/glx.h:183
GLXContextID = XID 	# /usr/include/GL/glx.h:184
GLXWindow = XID 	# /usr/include/GL/glx.h:185
GLXPbuffer = XID 	# /usr/include/GL/glx.h:186
Window = XID 	# /usr/include/X11/X.h:96


_fname = util.find_library('GL')
if not _fname:
    raise RuntimeError('Could not load OpenGL library.')
gl_lib = cdll.LoadLibrary(_fname)
try:
    glXGetProcAddressARB = getattr(gl_lib, 'glXGetProcAddressARB')
    glXGetProcAddressARB.restype = POINTER(CFUNCTYPE(None))
    glXGetProcAddressARB.argtypes = [POINTER(c_ubyte)]
    _have_getprocaddress = True
except AttributeError:
    _have_getprocaddress = False


def _link(name, restype, argtypes):
    try:
        func = getattr(gl_lib, name)
        func.restype = restype
        func.argtypes = argtypes
        return func
    except AttributeError:
        if _have_getprocaddress:
            # Fallback if implemented but not in ABI
            bname = cast(pointer(create_string_buffer(name)), POINTER(c_ubyte))
            addr = glXGetProcAddressARB(bname)
            if addr:
                ftype = CFUNCTYPE(*((restype,) + tuple(argtypes)))
                func = cast(addr, ftype)
                return func
        else:
            raise RuntimeError('function %s not found' % name)


glXChooseVisual = _link('glXChooseVisual', POINTER(XVisualInfo),
                        [POINTER(Display), c_int, POINTER(c_int)])
glXCreateContext = _link('glXCreateContext', GLXContext,
                         [POINTER(Display), POINTER(XVisualInfo),
                          GLXContext, c_int])
glXDestroyContext = _link('glXDestroyContext', None,
                          [POINTER(Display), GLXContext])
glXMakeCurrent = _link('glXMakeCurrent', c_int,
                       [POINTER(Display), GLXDrawable, GLXContext])
glXSwapBuffers = _link('glXSwapBuffers', None,
                       [POINTER(Display), GLXDrawable])
glXChooseFBConfig = _link('glXChooseFBConfig', POINTER(GLXFBConfig),
                          [POINTER(Display), c_int, POINTER(c_int),
                           POINTER(c_int)])
glXGetVisualFromFBConfig = _link('glXGetVisualFromFBConfig',
                                 POINTER(XVisualInfo),
                                 [POINTER(Display), GLXFBConfig])
glXCreateWindow = _link('glXCreateWindow', GLXWindow,
                        [POINTER(Display), GLXFBConfig,
                         Window, POINTER(c_int)])
glXDestroyWindow = _link('glXDestroyWindow', None,
                         [POINTER(Display), GLXWindow])
glXCreateNewContext = _link('glXCreateNewContext', GLXContext,
                            [POINTER(Display), GLXFBConfig, c_int,
                             GLXContext, c_int])
glXMakeContextCurrent = _link('glXMakeContextCurrent', c_int,
                              [POINTER(Display), GLXDrawable,
                               GLXDrawable, GLXContext])
glXQueryExtension = _link('glXQueryExtension', c_int,
                          [POINTER(Display), POINTER(c_int), POINTER(c_int)])
glXGetClientString = _link('glXGetClientString', c_char_p,
                           [POINTER(Display), c_int])
glXQueryExtensionsString = _link('glXQueryExtensionsString', c_char_p,
                                 [POINTER(Display), c_int])
glXSwapIntervalMESA = _link('glXSwapIntervalMESA', c_int, [c_int])
glXSwapIntervalSGI = _link('glXSwapIntervalSGI', c_int, [c_int])


class GLXInfo(object):
    def __init__(self, display):
        self.display = display

    def have_version(self, major, minor=0):
        if not glXQueryExtension(self.display, None, None):
            raise RuntimeError('requires an X server with GLX')
        server_version = self.get_server_version().split()[0]
        client_version = self.get_client_version().split()[0]
        server = [int(i) for i in server_version.split('.')]
        client = [int(i) for i in client_version.split('.')]
        return (tuple(server) >= (major, minor) and
                tuple(client) >= (major, minor))

    def get_client_vendor(self):
        self.check_display()
        return glXGetClientString(self.display, GLX_VENDOR).decode('utf-8')

    def get_client_version(self):
        self.check_display()
        return glXGetClientString(self.display, GLX_VERSION).decode('utf-8')

    def get_extensions(self):
        return glXQueryExtensionsString(self.display,
                                        0).decode('utf-8').split()

    def have_extension(self, extension):
        self.check_display()
        if not self.have_version(1, 1):
            return False
        return extension in self.get_extensions()
