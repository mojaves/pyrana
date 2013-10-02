#!/usr/bin/env python3

import sys
import time
import pprint
import pygame
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.formats import MediaType


class PygameViewer(object):
    def __init__(self):
        self._ovl = None
        self._frames = 0

    def get_error(self):
        return ''

    @property
    def frames(self):
        return self._frames

    def setup(self, w, h):
        pygame.display.set_mode((w, h))
        self._ovl = pygame.Overlay(pygame.YV12_OVERLAY, (w, h))
        self._ovl.set_location(0, 0, w, h)

    def show(self, Y, U, V):
        self._ovl.display((Y, U, V))
        self._frames += 1


def play_file(fname, view):
    with open(fname, 'rb') as src:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_VIDEO)
        vstream = dmx.streams[sid]
        pprint.pprint(vstream)
        width = vstream['width']
        height = vstream['height']

        view.setup(width, height)

        vdec = dmx.open_decoder(sid)

        while True:
            frame = vdec.decode(dmx.stream(sid))
            img = frame.image()
            view.show(img.plane(0), img.plane(1), img.plane(2))


def _main(fname):
    pygame.init()
    pyrana.setup()

    view = PygameViewer()

    start = time.time()
    try:
        play_file(fname, view)
    except Exception as exc:  # FIXME
        print(exc)
        stop = time.time()
    finally:
        pass

    elapsed = stop - start
    print("\n%i frames in %f seconds = %3.f FPS" % (
          view.frames, elapsed, view.frames/elapsed))


if __name__ == "__main__":
    if len(sys.argv) == 2:
        _main(sys.argv[1])
    else:
        sys.stderr.write("usage: %s videofile\n" % sys.argv[0])
        sys.exit(1)
