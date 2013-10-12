#!/usr/bin/env python3

import sys
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.formats import MediaType


# see https://github.com/mojaves/writings/blob/master/articles/eng/2013-10-08-pyrana-player-tutorial-1.md
# for the corresponding tutorial


def ppm_write(frame, seqno):
    """
    saves a raw frame in a PPM image. See man ppm for details.
    the `seqno` parameter is just to avoid to overwrite them without
    getting too fancy with the filename generation.
    """
    image = frame.image(pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
    with open("frame%d.ppm" % (seqno), "wb") as dst:
        header = "P6\n%i %i\n255\n" % (image.width, image.height)
        dst.write(header.encode("utf-8"))
        dst.write(bytes(image))


def process_file(fname, step=1):
    with open(fname, 'rb') as src:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_VIDEO)
        vstream = dmx.streams[sid]
        width = vstream['width']
        height = vstream['height']

        num = 0
        vdec = dmx.open_decoder(sid)
        while True:
            # careful here: you have to decode *and* throw away (optionally)
            # each frame in order, so enough daa is actually pulled from the
            # demuxer and progress can be made.
            frame = vdec.decode(dmx.stream(sid))
            if num % step == 0:
                ppm_write(frame, num)
            num += 1


def _main(fname, step=1):
    pyrana.setup()

    try:
        process_file(fname, step)
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
