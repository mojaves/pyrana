#!/usr/bin/env python3

"""
decode the first video stream of a media file and writes
it as PPM frames.
"""

import sys
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.video import PixelFormat
from pyrana.formats import MediaType


# this code is also part of the pyrana player tutorial:
# https://github.com/mojaves/writings/blob/master/articles/eng/2013-10-08-pyrana-player-tutorial-1.md


def ppm_write(frame, seqno):
    """
    saves a raw frame in a PPM image. See man ppm for details.
    the `seqno` parameter is just to avoid to overwrite them without
    getting too fancy with the filename generation.
    """
    image = frame.image(PixelFormat.AV_PIX_FMT_RGB24)
    with open("frame%d.ppm" % (seqno), "wb") as dst:
        header = "P6\n%i %i\n255\n" % (image.width, image.height)
        dst.write(header.encode("utf-8"))
        dst.write(bytes(image))


def process_file(srcname, step=1):
    """
    extract the frames from the first video stream found in
    srcname (a path name) and write them down as PPM format.
    write one frame each `step':
    step=1: every frame
    step=2: write,skip,write,skip,...
    and so on.
    """
    with open(srcname, 'rb') as src:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_VIDEO)
        num = 0
        vdec = dmx.open_decoder(sid)
        while True:
            # careful here: you have to decode *and* throw away (optionally)
            # each frame in order, so enough data is actually pulled from the
            # demuxer and progress can be made.
            frame = vdec.decode(dmx.stream(sid))
            if num % step == 0:
                ppm_write(frame, num)
            num += 1


def _main(srcname, step=1):
    """the usual entry point."""
    pyrana.setup()

    try:
        process_file(srcname, step)
    except pyrana.errors.PyranaError as err:
        print(err)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        _main(sys.argv[1], int(sys.argv[2]))
    elif len(sys.argv) == 2:
        _main(sys.argv[1])
    else:
        sys.stderr.write("usage: %s videofile [save_step]\n" % sys.argv[0])
        sys.exit(1)
