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


# for a more pythonic and definitely recommended interface,
# look at the `extract_iter.py' example.
def extract_stream(src, sid, out):
    """
    extracts only the `sid' stream from the source and write it into the
    destination.
    `src' is an externally managed file-like. It must be open in read only mode,
    and must returns bytes() when read.
    `dst' is an externally managed file-like too. It must be open in a
    write-compatible mode, and must handle bytes() writes.
    """
    try:
        dmx = pyrana.formats.Demuxer(src)
        while True:
            # Demuxers can extracts Packets from the media file.
            # A Packet is just a smart container for the encoded binary data.
            # Packets allow the client code to easily access the most
            # fundamental fields; however, you cannot directly modify a
            # Packet (content). You have to do that using the functions or the
            # classes provided by Pyrana, most notably Encoders and Decoders.
            #
            # Demuxers can extract any packet they find, in the order they
            # find them, or they can fetch only those belonging to a specific
            # logical stream. See Demuxer.streams and find_stream to find the
            # right logical stream identifier.
            pkt = dmx.read_frame(sid)
            # Once you got a Packet, you can easily convert it to bytes()
            # Packet data is immutable, so the conversion is straightforward.
            out.write(bytes(pkt))
    except pyrana.errors.EOSError:
        pass  # normal termination! much like StopIteration.
    except pyrana.errors.PyranaError as err:
        # don't do that on your real code :)
        sys.stderr.write("%s\n" % err)


def _main(exe, args):
    """the usual entry point."""
    try:
        src, sid, dst = args
        with open(src, "rb") as fin, open(dst, 'wb') as fout:
            extract_stream(fin, int(sid), fout)
    except ValueError:
        sys.stderr.write("usage: %s source_file stream_id dest_file\n" % exe)
        sys.exit(1)


if __name__ == "__main__":
    _main(sys.argv[0], sys.argv[1:])
