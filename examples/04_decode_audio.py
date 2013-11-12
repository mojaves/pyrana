#!/usr/bin/env python3

import sys
import wave
import contextlib
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.audio import SampleFormat
from pyrana.formats import MediaType


# this code is also part of the pyrana player tutorial:
# TBD


def process_file(srcname, outname='out.wav'):
    with open(srcname, 'rb') as src, \
         contextlib.closing(wave.open(outname, 'wb')) as dst:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_AUDIO)
        astream = dmx.streams[sid]
        print(astream)
        dst.setnchannels(astream.channels)
        dst.setframerate(astream.sample_rate)
        dst.setsampwidth(2) # astream.sample_bytes

        adec = dmx.open_decoder(sid)
        while True:
            frame = adec.decode(dmx.stream(sid))
            samples = frame.samples(SampleFormat.AV_SAMPLE_FMT_S16)
            dst.writeframes(bytes(samples))


def _main(srcname):
    pyrana.setup()

    try:
        process_file(srcname)
    except pyrana.errors.PyranaError as err:
        print(err)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        _main(sys.argv[1])
    else:
        sys.stderr.write("usage: %s audiofile\n" % sys.argv[0])
        sys.exit(1)
