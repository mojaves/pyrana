#!/usr/bin/env python3

import sys
import pyrana.video
import pyrana.formats
import PIL
from PIL import Image

pyrana.setup()

f = open(sys.argv[-1], 'rb')
dmx = pyrana.formats.Demuxer(f)
vdec = dmx.open_decoder(0)
vframe = vdec.decode(dmx.stream(0))[0]
print(vframe)
src_img = vframe.image(pyrana.video.PixelFormat.AV_PIX_FMT_RGBA)
print(src_img)
dst_img = PIL.Image.frombytes("RGBA",
                             (src_img.width, src_img.height),
                             bytes(src_img))
dst_img.show()
sys.stdin.read()
