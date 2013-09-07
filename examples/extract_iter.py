#!/usr/bin/env python3

"""
extracts a raw stream from a media file.
"""
# this pyrana example is just a step further the
# `probe' one. It demonstrates the most basic way
# to access the encoded data extracted from a media
# file.
#
# meet the Packets.

import sys
import pyrana.formats
import pyrana.errors

# see the `probe' example to learn why this is fundamental
# and why this cannot be done (easily) automatically.
pyrana.setup()


def itercopy(src, sid, out):
    try:
        dmx = pyrana.formats.Demuxer(src)
        # equivalent to:
        # for pkt in dmx.stream(pyrana.formats.STREAM_ANY):
        #     pass
        # in turn equivalent to (thanks to the default args):
        # for pkt in dmx.stream():
        #     pass
        for pkt in dmx:
            w = out.write(bytes(pkt))
    except pyrana.errors.PyranaError as err:
        sys.stderr.write("%s\n" % err)


def extract_stream(src, sid, out):
    try:
        dmx = pyrana.formats.Demuxer(src)
        for pkt in dmx.stream(sid):
            w = out.write(bytes(pkt))
    except pyrana.errors.PyranaError as err:
        sys.stderr.write("%s\n" % err)


def _main(exe, args):
    try:
        src, sid, dst = args
        with open(src, "rb") as fin, open(dst, 'wb') as fout:
            extract_stream(fin, int(sid), fout)
    except ValueError:
        sys.stderr.write("usage: %s source_file stream_id dest_file\n" % exe)
        sys.exit(1)


if __name__ == "__main__":
    _main(sys.argv[0], sys.argv[1:])
