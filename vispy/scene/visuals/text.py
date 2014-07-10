# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

##############################################################################
# Load font into texture

import numpy as np

from ...gloo import (TextureAtlas, set_state, get_parameter,
                     Program, IndexBuffer, VertexBuffer)
from ...ext.six import string_types
from ...util.transforms import ortho
from ...fonts import _load_glyph


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
        self._font = font
        self._glyphs = {}

    def __getitem__(self, char):
        if not (isinstance(char, string_types) and len(char) == 1):
            raise TypeError('index must be a 1-character string')
        if char not in self._glyphs:
            self._load_char(char)
        return self._glyphs[char]

    def _load_char(self, char):
        """Build a glyph corresponding to an individual character

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
        height, width, nc = glyph['bitmap'].shape
        assert nc == 3  # RGB
        region = self._atlas.get_free_region(width + 2, height + 2)
        if region is None:
            raise RuntimeError('Cannot store glyph')
        x, y, w, h = region
        x, y, w, h = x + 1, y + 1, w - 2, h - 2
        self._atlas.set_region((x, y, w, h), glyph['bitmap'])
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

    def get_font(self, face, size=12, bold=False, italic=False, dpi=96):
        """Get a font described by face and size"""
        key = '%s-%s' % (face, size)
        if key not in self._fonts:
            font = dict(face=face, size=size, bold=bold, italic=italic,
                        dpi=dpi)
            self._fonts[key] = TextureFont(font, self.atlas)
        return self._fonts[key]


##############################################################################
# The visual

text_vert = """
// Uniforms
uniform mat4      u_P;
uniform sampler2D u_font_atlas;
uniform vec3      u_font_atlas_shape;
uniform vec4      u_color;

// Attributes
attribute vec2  a_position;
attribute vec2  a_texcoord;
attribute float a_shift;

// Varying
varying vec2  v_texcoord;
varying float v_shift;
varying vec4  v_color;

void main()
{
    // Get color(4)
    v_color = u_color;
    // If color is fully transparent we just will discard the fragment later
    if( v_color.a <= 0.0 ) { gl_Position = vec4(0.0,0.0,0.0,1.0);  return; }

    // Do we take rotation into account for shift ?
    vec2 position = a_position;
    v_shift = position.x-floor(position.x);
    position.x = floor(position.x);
    position.y = floor(position.y);
    gl_Position = u_P * vec4(position,0.0,1.0);

    v_texcoord = a_texcoord;
}
"""

text_frag = """
// Uniforms
uniform mat4      u_P;
uniform sampler2D u_font_atlas;
uniform vec3      u_font_atlas_shape;
uniform vec4      u_color;

// Varying
varying vec2  v_texcoord;
varying vec4  v_color;
varying float v_shift;

void main()
{
    vec3 shape = u_font_atlas_shape;
    vec4 color = v_color;
    vec2 uv = v_texcoord.xy;

    vec4 current = texture2D(u_font_atlas, uv);
    vec4 previous= texture2D(u_font_atlas, uv+vec2(-1.,0.)*(1.0/shape.xy));
    vec4 next    = texture2D(u_font_atlas, uv+vec2(+1.,0.)*(1.0/shape.xy));

    float r = current.r;
    float g = current.g;
    float b = current.b;
    if( v_shift <= 0.333 )
    {
        float z = v_shift/0.333;
        r = mix(current.r, previous.b, z);
        g = mix(current.g, current.r,  z);
        b = mix(current.b, current.g,  z);
    }
    else if( v_shift <= 0.666 )
    {
        float z = (v_shift-0.33)/0.333;
        r = mix(previous.b, previous.g, z);
        g = mix(current.r,  previous.b, z);
        b = mix(current.g,  current.r,  z);
    }
    else if( v_shift < 1.0 )
    {
        float z = (v_shift-0.66)/0.334;
        r = mix(previous.g, previous.r, z);
        g = mix(previous.b, previous.g, z);
        b = mix(current.r,  previous.b, z);
    }
    vec3 rgb = vec3(r,g,b);
    gl_FragColor.rgb = rgb * color.rgb;
    gl_FragColor.a = (rgb.r + rgb.g + rgb.b)/3.0 * color.a;
}
"""


def _text_to_vbo(text, font, anchor_x='center', anchor_y='center'):
    """Convert text characters to VertexBuffer"""
    text_vtype = np.dtype([('a_position', 'f4', 2),
                           ('a_texcoord', 'f4', 2),
                           ('a_shift', 'f4', 1)])
    vertices = np.zeros(len(text) * 4, dtype=text_vtype)
    prev = None
    x = y = width = height = ascender = descender = 0
    for ii, char in enumerate(text):
        glyph = font[char]
        kerning = glyph['kerning'].get(prev, 0.)
        x0 = x + glyph['offset'][0] + kerning
        y0 = y + glyph['offset'][1]
        x1 = x0 + glyph['size'][0]
        y1 = y0 - glyph['size'][1]
        u0, v0, u1, v1 = glyph['texcoords']
        position = [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]
        texcoords = [[u0, v0], [u0, v1], [u1, v1], [u1, v0]]
        vi = ii * 4
        vertices['a_position'][vi:vi+4] = position
        vertices['a_texcoord'][vi:vi+4] = texcoords
        x += glyph['advance'][0] + kerning
        y += glyph['advance'][1]
        ascender = max(ascender, y0)
        descender = min(ascender, y1)
        width += glyph['advance'][0] + kerning
        height = max(height, glyph['size'][1])
        prev = char

    # Tight bounding box (loose would be width, font.height/.ascender/.desc)
    width -= glyph['advance'][0] / 64.0 - kerning + glyph['size'][0]
    dx = dy = 0
    if anchor_y == 'top':
        dy = -ascender
    elif anchor_y == 'center':
        dy = -(height / 2 + descender)
    elif anchor_y == 'bottom':
        dy = -descender
    if anchor_x == 'right':
        dx = -width / 1.0
    elif anchor_x == 'center':
        dx = -width / 2.0
    vertices['a_position'] += (round(dx), round(dy))
    return VertexBuffer(vertices)


class Text(object):
    def __init__(self, text, size=12, color=(0., 0., 0., 1.), bold=False,
                 italic=False, face='Arial', dpi=96,
                 anchor_x='center', anchor_y='center'):
        assert isinstance(text, string_types)
        self._font_manager = FontManager()
        self._program = Program(text_vert, text_frag)
        font = self._font_manager.get_font(face, size, bold, italic, dpi)
        self._program.bind(_text_to_vbo(text, font, anchor_x, anchor_y))
        self._program['u_color'] = color
        self._program['u_font_atlas'] = self._font_manager.atlas
        self._program['u_font_atlas_shape'] = self._font_manager.atlas.shape
        idx = (np.array([0, 1, 2, 0, 2, 3], np.uint32) +
               np.arange(0, 4*len(text), 4, dtype=np.uint32)[:, np.newaxis])
        self._ib = IndexBuffer(idx.ravel())

    def draw(self):
        set_state(blend=True, depth_test=False,
                  blend_func=('src_alpha', 'one_minus_src_alpha'))
        w, h = get_parameter('viewport')[2:]
        dx, dy = w // 2, h // 2
        P = ortho(-dx, dx, -dy, dy, -1, 1)
        self._program['u_P'] = P
        self._program.draw('triangles', self._ib)
