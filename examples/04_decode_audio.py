#!/usr/bin/env python3

import sys
import wave
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.formats import MediaType


# this code is also part of the pyrana player tutorial:
# TBD


def process_file(fname, dst):
    with open(fname, 'rb') as src:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_AUDIO)
        astream = dmx.streams[sid]
        dst.setnchannels(astream.channels)
        dst.setframerate(astream.sample_rate)
        dst.setsampwidth(astream.sample_bytes)

        adec = dmx.open_decoder(sid)
        while True:
            # careful here: you have to decode *and* throw away (optionally)
            # each frame in order, so enough daa is actually pulled from the
            # demuxer and progress can be made.
            frame = adec.decode(dmx.stream(sid))
            samples = frame.samples()
            dst.writeframes(bytes(samples))


def _main(fname):
    pyrana.setup()

    try:
        dst = wave.open('out.wav', 'wb')
        process_file(fname, dst)
    except pyrana.errors.PyranaError as err:
        print(err)
    finally:
        dst.close()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        _main(sys.argv[1])
    else:
        sys.stderr.write("usage: %s audiofile\n" % sys.argv[0])
        sys.exit(1)
