#!/usr/bin/env python3

"""
FIXME: document me!
"""

import sys
import pyrana.formats
import pyrana.errors


pyrana.setup()


def extract_stream(src, sid, out):
    with open(src, "rb") as f:
        try:
            dmx = pyrana.formats.Demuxer(f)
            while True:
                pkt = dmx.read_frame(sid)
                out.write(pkt)
        except pyrana.errors.PyranaError as err:
            sys.stderr.write("%s\n" % err)


def _main(exe, args):
    try:
        src, sid = args
        extract_stream(src, sid, sys.stdout)
        sys.stdout.flush()
    except ValueError:
        sys.stderr.write("usage: %s source_file stream_id\n" % exe)
        sys.exit(1)


if __name__ == "__main__":
    _main(sys.argv[0], sys.argv[1:])
