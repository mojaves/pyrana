#!/usr/bin/env python3

"""
exports video frame data to PIL.
"""

# this example demonstrates the interoperability with
# PIL/Pillow.
# to construct a PIL(low) image from a pyrana.video.Image,
# which is in turn extract from a pyrana.video.Frame,
# you have to convert it to a plain byte instance.
# This is done, unsurprisingly, using the standard bytes()
# constructor function.

# the usual imports. No news here
import sys
import pyrana.video
import pyrana.formats
from pyrana.formats import MediaType
import PIL


def _main(args):
    # never forget this!
    pyrana.setup()

    with open(args[1], 'rb') as f:
        dmx = pyrana.formats.Demuxer(f)
        # automatically finds the first video stream.
        # easy as it seems, really.
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_VIDEO)
        # ask the demuxer to build a decoder suitable for the
        # given stream id, like a factory function.
        # This is just the easy and practical way (inherited from libav*)
        # to get a suitable Decoder instance.
        vdec = dmx.open_decoder(sid)
        # then decode the very first frame.
        # Doing this way, the decoder automatically pulls as much frames
        # as it needs from the logical streams provided by the demuxer.
        vframe = vdec.decode(dmx.stream(sid))
        # just for the show :)
        print(vframe)
        # now fetch the raw image from the frame.
        # A video Frame is Image plus timing and stream informations;
        # a video Image is no much more than the actual matrix of pixels.
        # You can specifiy a Pixel Format for the Image you want to
        # get from the Frame, so the data is automatically converted
        # if it is needed. Otherwise, the Image Pixel Format is the one
        # of the original stream.
        src_img = vframe.image(pyrana.video.PixelFormat.AV_PIX_FMT_RGBA)
        # the show must go on! :)
        print(src_img)
        # now we can finally build the PIL image from the raw Image data.
        dst_img = PIL.Image.frombytes("RGBA",
                                     (src_img.width, src_img.height),
                                     bytes(src_img))
        # ... and show it using the standard PIL methods.
        dst_img.show()
        sys.stdin.read() # just wait for user acknowledgement


if __name__ == "__main__":
    _main(sys.argv[1:])
