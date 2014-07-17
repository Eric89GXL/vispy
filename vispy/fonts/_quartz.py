# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

# Use OSX cocoa/quartz to get glyph bitmaps

import numpy as np
from ctypes import c_void_p, byref, c_int32, c_byte

from ..ext.cocoapy import cf, ct, quartz, CFRange, CFSTR, CGGlyph, UniChar, \
    kCTFontFamilyNameAttribute, kCTFontBoldTrait, kCTFontItalicTrait, \
    kCTFontSymbolicTrait, kCTFontTraitsAttribute, kCTFontAttributeName, \
    kCGImageAlphaPremultipliedLast, kCFNumberSInt32Type, ObjCClass


_font_dict = {}


def _load_font(face, size, bold, italic):
    key = '%s-%s-%s-%s' % (face, size, bold, italic)
    if key in _font_dict:
        return _font_dict[key]
    traits = 0
    traits |= kCTFontBoldTrait if bold else 0
    traits |= kCTFontItalicTrait if italic else 0
    face = face.decode('utf-8')

    # Create an attribute dictionary.
    args = [None, 0, cf.kCFTypeDictionaryKeyCallBacks,
            cf.kCFTypeDictionaryValueCallBacks]
    attributes = c_void_p(cf.CFDictionaryCreateMutable(*args))
    # Add family name to attributes.
    cfname = CFSTR(face)
    cf.CFDictionaryAddValue(attributes, kCTFontFamilyNameAttribute, cfname)
    cf.CFRelease(cfname)
    # Construct a CFNumber to represent the traits.
    itraits = c_int32(traits)
    sym_traits = c_void_p(cf.CFNumberCreate(None, kCFNumberSInt32Type,
                                            byref(itraits)))
    if sym_traits:
        # Construct a dictionary to hold the traits values.
        args = [None, 0, cf.kCFTypeDictionaryKeyCallBacks,
                cf.kCFTypeDictionaryValueCallBacks]
        traits_dict = c_void_p(cf.CFDictionaryCreateMutable(*args))
        if traits_dict:
            # Add CFNumber traits to traits dictionary.
            cf.CFDictionaryAddValue(traits_dict, kCTFontSymbolicTrait,
                                    sym_traits)
            # Add traits dictionary to attributes.
            cf.CFDictionaryAddValue(attributes, kCTFontTraitsAttribute,
                                    traits_dict)
            cf.CFRelease(traits_dict)
        cf.CFRelease(sym_traits)
    # Create font descriptor with attributes.
    desc = c_void_p(ct.CTFontDescriptorCreateWithAttributes(attributes))
    cf.CFRelease(attributes)
    font = c_void_p(ct.CTFontCreateWithFontDescriptor(desc, size, None))
    if not font:
        raise RuntimeError("Couldn't load font: %s" % face.decode('utf-8'))
    _font_dict[key] = font
    return font


def _load_glyph(f, char, glyphs_dict):
    font = _load_font(**f)
    # Create an attributed string using text and font.
    args = [None, 1, cf.kCFTypeDictionaryKeyCallBacks,
            cf.kCFTypeDictionaryValueCallBacks]
    attributes = c_void_p(cf.CFDictionaryCreateMutable(*args))
    cf.CFDictionaryAddValue(attributes, kCTFontAttributeName, font)
    string = c_void_p(cf.CFAttributedStringCreate(None, CFSTR(char),
                                                  attributes))
    # Create a CTLine object to render the string.
    line = c_void_p(ct.CTLineCreateWithAttributedString(string))
    cf.CFRelease(string)
    cf.CFRelease(attributes)
    # Get a bounding rectangle for glyphs in string.
    chars = (UniChar * 1)(*map(ord, char.decode('utf-8')))
    glyphs = (CGGlyph * 1)()
    ct.CTFontGetGlyphsForCharacters(font, chars, glyphs, 1)
    rect = ct.CTFontGetBoundingRectsForGlyphs(font, 0, glyphs, None, 1)
    # Get advance for all glyphs in string.
    advance = ct.CTFontGetAdvancesForGlyphs(font, 1, glyphs, None, 1)
    advance = advance
    width = max(int(np.ceil(rect.size.width) + 1), 1)
    height = max(int(np.ceil(rect.size.height) + 1), 1)

    left = rect.origin.x
    baseline = rect.origin.y
    top = height - baseline

    bits_per_component = 8
    bytes_per_row = 4*width
    color_space = c_void_p(quartz.CGColorSpaceCreateDeviceRGB())
    args = [None, width, height, bits_per_component, bytes_per_row,
            color_space, kCGImageAlphaPremultipliedLast]
    bitmap = c_void_p(quartz.CGBitmapContextCreate(*args))
    # Draw text to bitmap context.
    quartz.CGContextSetShouldAntialias(bitmap, True)
    quartz.CGContextSetTextPosition(bitmap, -left, baseline)
    ct.CTLineDraw(line, bitmap)
    cf.CFRelease(line)
    # Create an image to get the data out.
    image_ref = c_void_p(quartz.CGBitmapContextCreateImage(bitmap))
    assert quartz.CGImageGetBytesPerRow(image_ref) == bytes_per_row
    data_provider = c_void_p(quartz.CGImageGetDataProvider(image_ref))
    image_data = c_void_p(quartz.CGDataProviderCopyData(data_provider))
    buffer_size = cf.CFDataGetLength(image_data)
    assert buffer_size == width * height * 4
    buffer = (c_byte * buffer_size)()
    byte_range = CFRange(0, buffer_size)
    cf.CFDataGetBytes(image_data, byte_range, buffer)
    quartz.CGImageRelease(image_ref)
    quartz.CGDataProviderRelease(image_data)
    cf.CFRelease(bitmap)
    cf.CFRelease(color_space)

    # reshape bitmap (don't know why it's only alpha on OSX...)
    bitmap = np.array(buffer, np.ubyte)
    bitmap.shape = (height, width, 4)
    bitmap = bitmap[:, :, 3].copy()
    glyph = dict(char=char, offset=(left, top), bitmap=bitmap,
                 advance=advance, kerning={})
    glyphs_dict[char] = glyph
    # Generate kerning
    for other_char, other_glyph in glyphs_dict.items():
        glyph['kerning'][other_char] = (_get_k_p_a(font, other_char, char) -
                                        other_glyph['advance'])
        other_glyph['kerning'][char] = (_get_k_p_a(font, char, other_char) -
                                        glyph['advance'])


def _get_k_p_a(font, left, right):
    """This actually calculates the kerning + advance"""
    # http://lists.apple.com/archives/coretext-dev/2010/Dec/msg00020.html
    # 1) set up a CTTypesetter
    chars = left + right
    args = [None, 1, cf.kCFTypeDictionaryKeyCallBacks,
            cf.kCFTypeDictionaryValueCallBacks]
    attributes = c_void_p(cf.CFDictionaryCreateMutable(*args))
    cf.CFDictionaryAddValue(attributes, kCTFontAttributeName, font)
    string = c_void_p(cf.CFAttributedStringCreate(None, CFSTR(chars),
                                                  attributes))
    typesetter = ct.CTTypesetterCreateWithAttributedString(string)
    cf.CFRelease(string)
    cf.CFRelease(attributes)
    # 2) extract a CTLine from it
    range = CFRange(0, 1)
    line = ct.CTTypesetterCreateLine(typesetter, range)
    # 3) use CTLineGetOffsetForStringIndex to get the character positions
    offset = ct.CTLineGetOffsetForStringIndex(line, 1, None)
    cf.CFRelease(line)
    cf.CFRelease(typesetter)
    return offset


def list_fonts():
    manager = ObjCClass('NSFontManager').sharedFontManager()
    avail = manager.availableFontFamilies()
    fonts = [avail.objectAtIndex_(ii).UTF8String()
             for ii in range(avail.count())]
    fonts = sorted(fonts, key=lambda f: f.lower())
    return fonts
