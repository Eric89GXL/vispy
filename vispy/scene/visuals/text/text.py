# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

##############################################################################
# Load font into texture

import numpy as np
from copy import deepcopy

from ._sdf import _get_sdf
from ....gloo import (TextureAtlas, set_state, get_parameter,
                      Program, IndexBuffer, VertexBuffer)
from ....ext.six import string_types
from ....util.transforms import ortho
from ....fonts import _load_glyph


class TextureFont(object):
    """Gather a set of glyphs relative to a given font name and size

    Parameters
    ----------
    font : dict
        Dict with entries "face", "size", "bold", "italic".
    atlas: Atlas
        Atlas where glyph will be stored.
    """
    def __init__(self, font, atlas):
        self._atlas = atlas
        self._font = deepcopy(font)
        self._font['size'] = 512  # use high resolution point size for SDF
        self._lowres_size = 64  # end at this point size for storage
        self._spread = 32  # spread/border at the high-res for SDF calculation
        self._glyphs = {}

    @property
    def ratio(self):
        """Ratio of the initial high-res to final stored low-res glyph"""
        return self._lowres_size / float(self._font['size'])

    @property
    def slop(self):
        """Extra space along each glyph edge due to SDF borders"""
        return (self.ratio * self._spread)

    def __getitem__(self, char):
        if not (isinstance(char, string_types) and len(char) == 1):
            raise TypeError('index must be a 1-character string')
        if char not in self._glyphs:
            self._load_char(char)
        return self._glyphs[char]

    def _load_char(self, char):
        """Build and store a glyph corresponding to an individual character

        Parameters:
        -----------
        char : str
            A single character to be represented.
        """
        assert isinstance(char, string_types) and len(char) == 1
        assert char not in self._glyphs
        # load new glyph data from font
        _load_glyph(self._font, char, self._glyphs)
        # put new glyph into the texture
        glyph = self._glyphs[char]
        bitmap = glyph['bitmap']

        # convert to padded double array
        sdf = _get_sdf(glyph['bitmap'], spread=self._spread)

        # scale down for storage
        h, w = sdf.shape
        xp = (np.arange(w) + 0.5) / float(w)
        x = (np.arange(int(round(w*self.ratio))) + 0.5) / round(w*self.ratio)
        bitmap = np.array([np.interp(x, xp, ss) for ss in sdf])
        xp = (np.arange(h) + 0.5) / h
        x = (np.arange(int(round(h*self.ratio))) + 0.5) / round(h*self.ratio)
        bitmap = np.array([np.interp(x, xp, ss) for ss in bitmap.T]).T
        height, width = bitmap.shape

        # Store
        region = self._atlas.get_free_region(width + 2, height + 2)
        if region is None:
            raise RuntimeError('Cannot store glyph')
        x, y, w, h = region
        x, y, w, h = x + 1, y + 1, w - 2, h - 2
        self._atlas.set_region((x, y, w, h), bitmap)
        u0 = x / float(self._atlas.shape[1])
        v0 = y / float(self._atlas.shape[0])
        u1 = (x+w) / float(self._atlas.shape[1])
        v1 = (y+h) / float(self._atlas.shape[0])
        texcoords = (u0, v0, u1, v1)
        glyph.update(dict(size=(w, h), texcoords=texcoords))


class FontManager(object):
    def __init__(self):
        self.atlas = TextureAtlas()
        self._fonts = {}

    def get_font(self, face, bold=False, italic=False):
        """Get a font described by face and size"""
        key = '%s-%s-%s' % (face, bold, italic)
        if key not in self._fonts:
            font = dict(face=face, bold=bold, italic=italic)
            self._fonts[key] = TextureFont(font, self.atlas)
        return self._fonts[key]


##############################################################################
# The visual

text_vert = """
// Uniforms
uniform mat4      transform;
uniform sampler2D u_font_atlas;
uniform vec4      u_color;

// Attributes
attribute vec2  a_position;
attribute vec2  a_texcoord;

// Varying
varying vec2  v_texcoord;
varying vec4  v_color;

void main()
{
    v_color = u_color;
    gl_Position = transform * vec4(a_position, 0.0, 1.0);
    v_texcoord = a_texcoord;
}
"""

text_frag = """
// Uniforms
uniform mat4      u_P;
uniform sampler2D u_font_atlas;
uniform vec4      u_color;

// Varying
varying vec2  v_texcoord;
varying vec4  v_color;

const float smooth_center = 0.5;

void main()
{
    vec4 color = v_color;
    vec2 uv = v_texcoord.xy;
    vec4 rgb = texture2D(u_font_atlas, uv);

    float distance = rgb.r;
    float smooth_width = fwidth(distance);
    float alpha = smoothstep(smooth_center - smooth_width,
                             smooth_center + smooth_width, distance);
    gl_FragColor = vec4(color.rgb, color.a * alpha);
}
"""


class Text(object):
    def __init__(self, text, color=(0., 0., 0., 1.), bold=False,
                 italic=False, face='OpenSans',
                 anchor_x='center', anchor_y='center'):
        assert isinstance(text, string_types)
        assert len(text) > 0  # XXX TODO: should fix this simple corner case
        assert anchor_y in ('top', 'center', 'middle', 'bottom')
        assert anchor_x in ('left', 'center', 'right')
        self._font_manager = FontManager()
        self._program = Program(text_vert, text_frag)
        self._program.bind(self._text_to_vbo(text, face, bold, italic,
                                             anchor_x, anchor_y))
        self._program['u_color'] = color
        self._program['u_font_atlas'] = self._font_manager.atlas
        idx = (np.array([0, 1, 2, 0, 2, 3], np.uint32) +
               np.arange(0, 4*len(text), 4, dtype=np.uint32)[:, np.newaxis])
        self._ib = IndexBuffer(idx.ravel())

    def _text_to_vbo(self, text, face, bold, italic, anchor_x, anchor_y):
        """Convert text characters to VertexBuffer"""
        font = self._font_manager.get_font(face, bold, italic)
        text_vtype = np.dtype([('a_position', 'f4', 2),
                               ('a_texcoord', 'f4', 2)])
        vertices = np.zeros(len(text) * 4, dtype=text_vtype)
        prev = None
        width = height = ascender = descender = 0
        ratio, slop = font.ratio, font.slop
        x_off = -slop
        for ii, char in enumerate(text):
            glyph = font[char]
            kerning = glyph['kerning'].get(prev, 0.) * ratio
            x0 = x_off + glyph['offset'][0] * ratio + kerning
            y0 = glyph['offset'][1] * ratio + slop
            x1 = x0 + glyph['size'][0]
            y1 = y0 - glyph['size'][1]
            u0, v0, u1, v1 = glyph['texcoords']
            position = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]
            texcoords = [[u0, v0], [u0, v1], [u1, v1], [u1, v0]]
            vi = ii * 4
            vertices['a_position'][vi:vi+4] = position
            vertices['a_texcoord'][vi:vi+4] = texcoords
            x_move = glyph['advance'] * ratio + kerning
            x_off += x_move
            ascender = max(ascender, y0 - slop)
            descender = min(descender, y1 + slop)
            width += x_move
            height = max(height, glyph['size'][1] - 2*slop)
            prev = char

        # Tight bounding box (loose would be width, font.height /.asc / .desc)
        width -= glyph['advance'] * ratio - (glyph['size'][0] - 2*slop)
        dx = dy = 0
        if anchor_y == 'top':
            dy = -ascender
        elif anchor_y in ('center', 'middle'):
            dy = -(height / 2 + descender)
        elif anchor_y == 'bottom':
            dy = -descender
        if anchor_x == 'right':
            dx = -width
        elif anchor_x == 'center':
            dx = -width / 2.
        vertices['a_position'] += (dx, dy)
        return VertexBuffer(vertices)

    def draw(self):
        set_state(blend=True, depth_test=False,
                  blend_func=('src_alpha', 'one_minus_src_alpha'))
        w, h = get_parameter('viewport')[2:]
        dx, dy = w / 2., h / 2.
        P = ortho(-dx, dx, -dy, dy, -1, 1)
        self._program['transform'] = P
        self._program.draw('triangles', self._ib)
