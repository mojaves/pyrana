#!/usr/bin/env python3
# license: LGPL2.1 (same as SDL1.2)

import cffi
import pyrana.formats
import pyrana.errors
import sys

SDL_INIT_TIMER       = 0x00000001
SDL_INIT_AUDIO       = 0x00000010
SDL_INIT_VIDEO       = 0x00000020
SDL_INIT_CDROM       = 0x00000100
SDL_INIT_JOYSTICK    = 0x00000200
SDL_INIT_NOPARACHUTE = 0x00100000
SDL_INIT_EVENTTHREAD = 0x01000000
SDL_INIT_EVERYTHING	 = 0x0000FFFF

SDL_YV12_OVERLAY = 0x32315659	# Planar mode: Y + V + U  (3 planes)
SDL_IYUV_OVERLAY = 0x56555949	# Planar mode: Y + U + V  (3 planes)
SDL_YUY2_OVERLAY = 0x32595559	# Packed mode: Y0+U0+Y1+V0 (1 plane)
SDL_UYVY_OVERLAY = 0x59565955	# Packed mode: U0+Y0+V0+Y1 (1 plane)
SDL_YVYU_OVERLAY = 0x55595659	# Packed mode: Y0+V0+Y1+U0 (1 plane)

SDL_SWSURFACE =	0x00000000
SDL_HWSURFACE =	0x00000001
SDL_ASYNCBLIT =	0x00000004

SDL_ANYFORMAT  = 0x10000000
SDL_HWPALETTE  = 0x20000000
SDL_DOUBLEBUF  = 0x40000000
SDL_FULLSCREEN = 0x80000000
SDL_OPENGL     = 0x00000002
SDL_OPENGLBLIT = 0x0000000A
SDL_RESIZABLE  = 0x00000010
SDL_NOFRAME    = 0x00000020

_SDL_DECLS = """
typedef struct SDL_Surface SDL_Surface;

typedef struct SDL_Overlay {
	uint32_t format;
	int w, h;
	int planes;
	uint16_t *pitches;
	uint8_t **pixels;
    /* ... */
} SDL_Overlay;

typedef struct SDL_Rect {
	int16_t x, y;
	uint16_t w, h;
}SDL_Rect;

int SDL_Init(uint32_t flags);
void SDL_Quit(void);
const char *SDL_GetError(void);

void SDL_WM_SetCaption(const char *title, const char *icon);
SDL_Surface *SDL_SetVideoMode(int width, int height, int bpp, uint32_t flags);

SDL_Overlay *SDL_CreateYUVOverlay(int width, int height,
			                      uint32_t format, SDL_Surface *display);
void SDL_FreeYUVOverlay(SDL_Overlay *overlay);

int SDL_LockYUVOverlay(SDL_Overlay *overlay);
void SDL_UnlockYUVOverlay(SDL_Overlay *overlay);
int SDL_DisplayYUVOverlay(SDL_Overlay *overlay, SDL_Rect *dstrect);
"""

class SDLViewer(object):
    def __init__(self, ffi, SDL):
        self._ffi = ffi
        self._SDL = SDL
        self._surface = None
        self._overlay = None
        self._rect = self._ffi.new("SDL_Rect *")

    def get_error(self):
        return self._ffi.string(self._SDL.SDL_GetError())

    def setup(self, w, h):
        self._rect.x = 0
        self._rect.y = 0
        self._rect.w = w
        self._rect.h = h
        ys = w * h
        self._Ybuf = self._ffi.new("uint8_t[]", ys)
        self._Ubuf = self._ffi.new("uint8_t[]", int(ys/2))
        self._Vbuf = self._ffi.new("uint8_t[]", int(ys/2))
        self._Y = self._ffi.buffer(self._Ybuf, ys)
        self._U = self._ffi.buffer(self._Ubuf, int(ys/2))
        self._V = self._ffi.buffer(self._Vbuf, int(ys/2))
        self._SDL.SDL_WM_SetCaption(b"pyrana SDL preview", self._ffi.NULL)
        self._surface = self._SDL.SDL_SetVideoMode(w, h, 0, SDL_HWSURFACE)
        if self._surface is self._ffi.NULL:
            sys.stderr.write("%s\n" % self.get_error())
        self._overlay = self._SDL.SDL_CreateYUVOverlay(w, h,
                                                       SDL_YV12_OVERLAY,
                                                       self._surface)
        if self._overlay is self._ffi.NULL:
            sys.stderr.write("%s\n" % self.get_error())

    def __del__(self):
        self._SDL.SDL_FreeYUVOverlay(self._overlay);
        # the surface obtained by SetVideoMode will be automagically
        # released by SDL_Quit

    def show(self, Y, U, V):
        self._SDL.SDL_LockYUVOverlay(self._overlay)
        ys = self._rect.w * self._rect.h
        self._Y[:ys] = Y
        self._U[:int(ys/2)] = U
        self._V[:int(ys/2)] = V
        self._overlay.pixels[0] = self._Ybuf
        self._overlay.pixels[1] = self._Ubuf
        self._overlay.pixels[2] = self._Vbuf
        self._SDL.SDL_UnlockYUVOverlay(self._overlay)
        self._SDL.SDL_DisplayYUVOverlay(self._overlay, self._rect);


def _main(fname):
    ffi = cffi.FFI()
    ffi.cdef(_SDL_DECLS)
    SDL = ffi.dlopen("SDL")

    SDL.SDL_Init(SDL_INIT_VIDEO)
    pyrana.setup()


    with open(fname, 'rb') as src:
        dmx = pyrana.formats.Demuxer(src)
        print(dmx.streams[0])
        width = dmx.streams[0]['width']
        height = dmx.streams[0]['height']

        view = SDLViewer(ffi, SDL)
        view.setup(width, height)

        vdec = dmx.open_decoder(0)  # FIXME
        vframe = vdec.decode(dmx.stream(0))

        while True:
            frame = vdec.decode(dmx.stream(0))
            img = frame.image()
            view.show(img.plane(0), img.plane(1), img.plane(2))


    SDL.SDL_Quit()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        _main(sys.argv[1])
    else:
        sys.stderr.write("usage: %s videofile\n" % sys.argv[0])
        sys.exit(1)
