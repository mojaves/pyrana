#!/usr/bin/env python3

"""
inspects and prints the content of a media file.
"""
# This is the simpler and most fundamental pyrana example.
# If nothing else, just have a quick glance at this.

import sys
# You've to import a pyrana subpackage to deal with
# a specific subsystem. You'll very likely need to deal
# with media files, so you'll need the `formats' subpackage.
import pyrana.formats
# In order to see (and catch) the pyrana exceptions,
# you need to import this subpackage.
import pyrana.errors

# Call this first, just after all the main imports,
# and before any other code.
#
# Due to constraints inherited by the ffmpeg libraries,
# you need to initialize the package before to use it.
# Otherwise, things are not gonna work, or worse.
#
# Following the zen of Python, you have to do it explicitely.
# It is safe to call setup() multiple times; however,
# you should do it just once
pyrana.setup()


class MediaInfo(object):
    """easy access to the informations about a media stream."""
    def __init__(self, path):
        self._path = path
        self._info = []
        self.inspect(path=path)

    def inspect(self, path):
        """inspects the media stream at the given path."""
        with open(path, "rb") as src:
            try:
                # Demuxer objects need binary access to a file(-like).
                # The file-like must be already open, and Demuxers will
                # take a new reference to this.
                # Anyway, Demuxers (and any other pyrana object) will NOT
                # close, destroy, dispose or generally finalize the objects
                # they are given to. The calling code must handle this
                # explicitely.
                #
                # In this example, the demuxer will just pull out data from
                # the file-like; seek() and tell() should be supported too
                # depending on the format being carried.
                dmx = pyrana.formats.Demuxer(src)
                # streams: a tuple of informations about the media file
                # streams. Of course each metadata refers to the corresponding
                # index.
                self._info = dmx.streams
            except pyrana.errors.PyranaError:
                self._info = ()

    def __str__(self):  
        return \
            "Media(name=\"%s\")\n " % (self._path) + \
            "\n ".join(str(info) for info in self._info)


def _main(args):
    """the usual entry point."""
    for arg in args:
        print(str(MediaInfo(arg)))


if __name__ == "__main__":
    _main(sys.argv[1:])
