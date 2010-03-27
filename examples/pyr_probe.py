#!/usr/bin/env python

import pyrana
import sys



class MediaInfo(object):
    def __init__(self, path):
        self._path = path
        with open(path, "r") as f:
            try:
                dmx = pyrana.format.Demuxer(f)
                self._info = dmx.streams
            except: # FIXME
                self._info = {}
    def _info_to_str(self, info, num=0):
        return  \
             "stream #%2i:\n * " %(num) + \
             "\n * ".join("%-12s: %s" %(k,v) for k,v in info.items() if k != "extradata")
    def __str__(self):  
        return \
            "media=\"%s\"\n" %(self._path) + \
            "\n".join(self._info_to_str(i, n) for n,i in enumerate(self._info)) + \
            "\n"


def _main(args):
    media_files = args[1:]
    for mf in media_files:
        print str(MediaInfo(mf))


if __name__ == "__main__":
    _main(sys.argv)

