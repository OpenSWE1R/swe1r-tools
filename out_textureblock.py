#!/usr/bin/env python3

# This is a python script to export textures from out_textureblock.bin.
#
# As out_textureblock.bin only stores pixel data, but no information about
# the pixelformat or texture resolution, we need additional information.
#
# Additional texture information is being loaded from XML files which can be
# generated from out_modelblock.bin using the Sw_Racer XmlConverter tool.
# Sw_Racer can be found at https://github.com/Olganix/Sw_Racer

# Usage: out_textureblock.py <path to out_textureblock.bin> <path to XML> [<path to XML> ...]

import sys
import struct
from xml.dom import minidom
from PIL import Image

def get_value(s):
  if s[0:2] == '0x':
    return int(s[2:], 16)
  else:
    return int(s)

def read8(f):
  return f.read(1)[0]
def read16(f):
  return int.from_bytes(f.read(2), byteorder='big', signed=False)
def read32(f):
  return int.from_bytes(f.read(4), byteorder='big', signed=False)

def shifter(a1):
  v1 = 0x40000000
  v2 = 31
  while(v2 != 0):
    v3 = a1 & v1
    v1 >>= 1
    --v2
    if v3 == 0:
      break
  result = v1 << 1
  if ( result < a1 ):
    result <<= 1
  if ( result < 16 ):
    result = 16
  return result


# Collect information about textures
texinfo = {}
texinfo_source = {}
history = ''
for path in sys.argv[2:]:
  if history != '':
    print('')
  history = ''
  print("Loading models from XML '%s'" % path)
  mydoc = minidom.parse(path)
  Swr_Model = mydoc.documentElement
  #FIXME: Properly follow the structure of the XML
  Section5_Collection = Swr_Model.getElementsByTagName("Section5")
  for Section5 in Section5_Collection:
    texmask = get_value(Section5.getElementsByTagName("textureMask")[0].attributes['u8'].value)
    texindex = get_value(Section5.getElementsByTagName("textureIndex")[0].attributes['u24'].value)
    if texmask != 0x0A:
      print("Unknown texmask 0x%02X" % texmask)
      continue

    Section5b = Section5.getElementsByTagName("Section5b")
    if (len(Section5b) == 0):
      print("  Missing Section5b")
      continue
    #FIXME: assert(len(Section5b) == 1)
    Section5b = Section5b[0]

    t = {}
    t['width'] = get_value(Section5.getElementsByTagName("unk16")[0].attributes['u16'].value)
    t['height'] = get_value(Section5.getElementsByTagName("unk18")[0].attributes['u16'].value)
    t['format_a'] = get_value(Section5.getElementsByTagName("unk12")[0].attributes['u8'].value)
    t['format_b'] = get_value(Section5.getElementsByTagName("unk13")[0].attributes['u8'].value)
    t['flags'] = get_value(Section5b.getElementsByTagName("unk3")[0].attributes['u8'].value)

    if texindex in texinfo:
      if (texinfo[texindex] != t):
        if history != '':
          print('')
        print("  Skipping conflicting texture information for %d" % texindex)
        print("    Old: %s" % (str(texinfo[texindex])))
        print("    New: %s" % (str(t)))
        history = ''
      else:
        if history != 'skipping':
          if history != '':
            print('')
          print("  Skipping known texture information for", end='')
          history = 'skipping'
        print(" %d" % texindex, end='', flush=True)
    else:
      if history != 'adding':
        if history != '':
          print('')
        print("  Adding texture information for", end='')
        history = 'adding'
      print(" %d" % texindex, end='', flush=True)
      texinfo[texindex] = t
      texinfo_source[texindex] = path

# Open the textureblock
with open(sys.argv[1], 'rb') as f:

  # Start to output tags for wxHexEditor
  tags = open("/tmp/swep1r/wxhexeditor.tags", "w")
  tags.write('<?xml version="1.0" encoding="UTF-8"?>\n' + '<wxHexEditor_XML_TAG>\n' + '  <filename>\n')
  tag_id = 0
  def add_tag(start, size, text, colour = "#888888", dump=False):
    global tag_id
    tag_id += 1
    s = ''
    s += '    <TAG id="%s">\n' % tag_id
    s += '      <start_offset>%d</start_offset>\n' % start
    s += '      <end_offset>%d</end_offset>\n' % (start + size - 1)
    s += '      <tag_text>%s (%d bytes)</tag_text>\n' % (text, size)
    s += '      <font_colour>#000000</font_colour>\n'
    s += '      <note_colour>%s</note_colour>\n' % colour
    s += '    </TAG>\n'
    tags.write(s)
    if dump:
      off = f.tell()
      f.seek(start)
      buf = f.read(size)
      with open('/tmp/swep1r/%s.bin' % text, 'wb') as t:
        t.write(buf)
      f.seek(off)

  # Start dumping all textures
  count = read32(f)
  add_tag(0, 4, 'count', '#FF88FF')
  add_tag(4 + 8 * count, 4, 'end-offset', '#8888FF')

  for i in range(0, count):

    f.seek(4 + 8 * i)
    off_a = read32(f)
    off_b = read32(f)
    off_c = read32(f)

    add_tag(4 + 8 * i + 0, 4, 'pixel-offset-%d' % i)
    add_tag(4 + 8 * i + 4, 4, 'palette-offset-%d' % i)

    if i not in texinfo:
      if off_b != 0:
        off_a_end = off_b
        add_tag(off_b, off_c - off_b, 'palette-data-%d-unused' % i, "#88FF88", dump=False)
      else:
        off_a_end = off_c
      add_tag(off_a, off_a_end - off_a, 'pixel-data-%d-0x%02X-unused' % (i, flags), "#FF8888", dump=False)
      print("Unknown texture information for %d" % i)
      continue

    width = texinfo[i]['width']
    height = texinfo[i]['height']
    format_a = texinfo[i]['format_a']
    format_b = texinfo[i]['format_b']
    flags = texinfo[i]['flags']

    #FIXME: POT width and height?!

    # Only flags 0x10 and 0x01 are known to exist
    #FIXME: Also uses 0x20
    #assert(flags & ~0x11 == 0)

    im = Image.new("RGBA", (width, height))
    pixels = im.load()

    f.seek(off_a)

    if format_a == 0 and format_b == 3:

      for y in range(0, height):
        for x in range(0, width):
          r, g, b, a = f.read(4)
          pixels[x, y] = (r, g, b, a)

    elif format_a == 2 and format_b == 0:

      add_tag(off_b, 2 * 16, 'palette-data-%d' % i, "#44FF44", dump=False)

      for y in range(0, height):
        for x in range(0, width):

          if x % 2 == 0:
            # Get index in palette for 2 pixels
            indices = f.read(1)[0]
          index = (indices & 0xF0) >> 4
          indices <<= 4

          # Read palette data
          off = f.tell()
          f.seek(off_b + 2 * index)
          color = int.from_bytes(f.read(2), byteorder='big', signed=False)
          a = (color >> 0) & 0x1
          b = ((color >> 1) & 0x1F) / 0x1F
          g = ((color >> 6) & 0x1F) / 0x1F
          r = ((color >> 11) & 0x1F) / 0x1F
          pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), a * 0xFF)
          f.seek(off)

    elif format_a == 2 and format_b == 1:

      add_tag(off_b, 2 * 256, 'palette-data-%d' % i, "#44FF44", dump=False)

      for y in range(0, height):
        for x in range(0, width):

          # Get index in palette
          index = f.read(1)[0]

          # Read palette data
          off = f.tell()
          f.seek(off_b + 2 * index)
          color = int.from_bytes(f.read(2), byteorder='big', signed=False)
          a = (color >> 0) & 0x1
          b = ((color >> 1) & 0x1F) / 0x1F
          g = ((color >> 6) & 0x1F) / 0x1F
          r = ((color >> 11) & 0x1F) / 0x1F
          pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), a * 0xFF)
          f.seek(off)

    elif format_a == 4 and format_b == 0:

      for y in range(0, height):
        for x in range(0, width):

          if x % 2 == 0:
            # Get color for 2 pixels
            values = f.read(1)[0]
          value = ((values & 0xF0) >> 4) * 0x11
          values <<= 4

          pixels[x, y] = (value, value, value, value)

    elif format_a == 4 and format_b == 1:

      for y in range(0, height):
        for x in range(0, width):
          value = f.read(1)[0]
          pixels[x, y] = (value, value, value, 0xFF)

    else:
      print("Unhandled texture format %d / %d (%s)" % (format_a, format_b, texinfo_source[i]))
      assert(False)

    off_a_end = f.tell()
    add_tag(off_a, off_a_end - off_a, 'pixel-data-%d-0x%02X' % (i, flags), "#FF4444", dump=False)

    im = im.transpose(Image.FLIP_TOP_BOTTOM)
    im.save("/tmp/swep1r/texture_%d.png" % (i), 'PNG')

    if False:
      if (a2 == 1257):
        dword_50C620 = (int)*a3;
      if ( a2 == 1258 ):
        dword_50C624 = (int)*a3;
      if ( a2 == 936 ):
        dword_50C618 = (int)*a3;
      if ( a2 == 352 ):
        dword_50C61C = (int)*a3;
      if ( a2 == 118 ):
        pass # run "invcol" filter

  tags.write('  </filename>\n' + '</wxHexEditor_XML_TAG>\n')
