#!/usr/bin/env python3

import sys
import time
import sdl2
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.video import PixelFormat
from pyrana.formats import MediaType


class PySDL2Viewer(object):
    def __init__(self):
        self._window = None
        self._renderer = None
        self._texture = None
        self._w = 0
        self._h = 0
        self._frames = 0

    @property
    def frames(self):
        return self._frames

    def setup(self, w, h):
        self._w = w
        self._h = h
        self._window = sdl2.SDL_CreateWindow('Pyrana'.encode('utf-8'),
                                             sdl2.SDL_WINDOWPOS_UNDEFINED,
                                             sdl2.SDL_WINDOWPOS_UNDEFINED,
                                             w,
                                             h,
                                             sdl2.SDL_WINDOW_SHOWN)
        self._renderer = sdl2.SDL_CreateRenderer(self._window, -1, 0)
        self._texture = sdl2.SDL_CreateTexture(self._renderer,
                                               sdl2.SDL_PIXELFORMAT_YV12,
                                               sdl2.SDL_TEXTUREACCESS_STREAMING,
                                               w,
                                               h)

    def show(self, Y, U, V):
        displayrect = sdl2.SDL_Rect(0, 0, self._w, self._h)
        pitch = self._w * sdl2.SDL_BYTESPERPIXEL(sdl2.SDL_PIXELFORMAT_YV12)
        sdl2.SDL_UpdateTexture(self._texture,
                               None,
                               # We need to swap the CB and CR planes
                               Y + V + U,
                               pitch)
        sdl2.SDL_RenderClear(self._renderer)
        sdl2.SDL_RenderCopy(self._renderer, self._texture, None, displayrect)
        sdl2.SDL_RenderPresent(self._renderer)
        self._frames += 1
        # To avoid X-Video congestion
        time.sleep(0.04)


def play_file(fname, view):
    with open(fname, 'rb') as src:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_VIDEO)
        vstream = dmx.streams[sid]
        print(vstream)

        view.setup(vstream.width, vstream.height)

        vdec = dmx.open_decoder(sid)

        while True:
            frame = vdec.decode(dmx.stream(sid))
            img = frame.image(PixelFormat.AV_PIX_FMT_YUV420P)
            view.show(img.plane(0), img.plane(2), img.plane(1))


def _main(fname):
    sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
    pyrana.setup()

    view = PySDL2Viewer()

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
