import numpy as np
from nose.tools import assert_true, assert_equal
import warnings

from vispy.fonts import list_fonts, _load_glyph

warnings.simplefilter('always')


def test_font_list():
    """Test font listing"""
    f = list_fonts()
    assert_true(len(f) > 0)


def test_font_glyph():
    """Test loading glyphs"""
    font_dict = dict(face='Arial', size=12, bold=True, italic=True)
    glyphs_dict = dict()
    chars = 'foobar^C&#'
    for char in chars:
        # Warning that Arial might not exist
        with warnings.catch_warnings(record=True):
            warnings.simplefilter('always')
            _load_glyph(font_dict, char, glyphs_dict)
    assert_equal(len(glyphs_dict), np.unique([c for c in chars]).size)
