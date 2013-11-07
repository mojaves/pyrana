#!/usr/bin/env python3

"""
extracts a raw stream from a media file,
using the python iterator interface,
"""
# This pyrana example is an extension of thw
# `extract' one. It shows a more pythonic
# interface with respect to the basic one.
# featurewise and performancewise, the two interfaces
# are (almost) identical.
# So, you're encouraged to use this one unless
# you've crystal clear why it does NOT fit in your code.

import sys
import pyrana.formats
import pyrana.errors


# see the `probe' example to learn why this is fundamental
# and why this cannot be done (easily) automatically.
pyrana.setup()


def copy_all_iter(src, dst):
    """
    copy all the data from the source to the destination, but operating by
    frames and not by chunks of bytes. And yes, for this very purposes this
    has exactly zero advantages over the raw byte copies. It's just a demo of
    the API.
    `src' is an externally managed file-like. It must be open in read only mode,
    and must returns bytes() when read.
    `dst' is an externally managed file-like too. It must be open in a
    write-compatible mode, and must handle bytes() writes.
    """

    try:
        dmx = pyrana.formats.Demuxer(src)
        # equivalent to:
        # for pkt in dmx.stream(pyrana.formats.STREAM_ANY):
        #     pass
        # in turn equivalent to (thanks to the default args):
        # for pkt in dmx.stream():
        #     pass
        #
        # As you have proably noted, you cannot specify
        # a specific stream with this interface.
        # It would'nt make sense to do so because the very
        # act to consider a Demuxer as an (abstract) collection
        # of Packets inhibits any filtering at this level.
        #
        # In a nutshell: if you want a specific stream,
        # you must use the Demuxer.stream() API.
        for pkt in dmx:
            dst.write(bytes(pkt))
    except pyrana.errors.PyranaError as err:
        sys.stderr.write("%s\n" % err)


# as stated above, the stream_id do not make sense here.
def _main(exe, args):
    """the usual entry point."""
    try:
        src, dst = args
        # BIG FAT WARNING!
        # this IS NOT AN EXACT COPY!
        # You are going to lose the stream header and
        # the stream trailer, if any.
        # use this code as reference, NOT as template code.
        with open(src, "rb") as fin, \
             open(dst, 'wb') as fdst:
            copy_all_iter(fin, fdst)
    except ValueError:
        sys.stderr.write("usage: %s source_file dest_file\n" % exe)
        sys.exit(1)


if __name__ == "__main__":
    _main(sys.argv[0], sys.argv[1:])
