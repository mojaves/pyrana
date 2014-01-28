#!/usr/bin/env python3

import sys
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.audio import SampleFormat, ChannelLayout
from pyrana.formats import MediaType


# this code is also part of the pyrana player tutorial:
# TBD


def process_file(srcname, dstname):
    sys.stdout.write("%s -> %s\n" % (srcname, dstname))

    with open(srcname, 'rb') as src, open(dstname, 'wb') as dst:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_AUDIO)
        adec = dmx.open_decoder(sid)
        params = {
            'bit_rate': 128000,
            'sample_rate': 44100,
            'channel layout': ChannelLayout.AV_CH_LAYOUT_STEREO,
            'sample_fmt': SampleFormat.AV_SAMPLE_FMT_S16
        }
        aenc = pyrana.audio.Encoder("mp2", params)  # FIXME
        num = 0
        while True:
            frame = adec.decode(dmx.stream(sid))
            try:
                pkt = aenc.encode(frame)
                dst.write(bytes(pkt))
                sys.stdout.write("encoded: %05i\r" % num)
            except pyrana.errors.NeedFeedError:
                sys.stderr.write("skipped: %05i\n" % num)
            num += 1


def _main(srcname, dstname):
    """the usual entry point."""
    pyrana.setup()

    try:
        process_file(srcname, dstname)
    except pyrana.errors.PyranaError as err:
        sys.stderr.write("%s\n" % err)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        _main(sys.argv[1], sys.argv[2])
    else:
        sys.stderr.write("usage: %s audiofile mp3file\n" % sys.argv[0])
        sys.exit(1)
