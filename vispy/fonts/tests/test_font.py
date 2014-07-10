import numpy as np
from nose.tools import assert_true, assert_equal

from vispy.fonts import list_fonts, _load_glyph


def test_font_list():
    """Test font listing"""
    f = list_fonts()
    assert_true(len(f) > 0)


def test_font_glyph():
    """Test loading glyphs"""
    font_dict = dict(face='Arial', size=12, bold=True, italic=True, dpi=96)
    glyphs_dict = dict()
    chars = 'foobar^C&#'
    for char in chars:
        _load_glyph(font_dict, char, glyphs_dict)
    assert_equal(len(glyphs_dict), np.unique([c for c in chars]).size)
