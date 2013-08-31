#!/usr/bin/env python3

"""
FIXME: document me!
"""

import sys
import pyrana.formats
import pyrana.errors


pyrana.setup()


def extract_stream(src, sid, out):
    try:
        dmx = pyrana.formats.Demuxer(src)
        while True:
            pkt = dmx.read_frame(sid)
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
