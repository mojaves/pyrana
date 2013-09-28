"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

from enum import IntEnum
from pyrana.common import to_pixel_format, to_picture_type
from pyrana.codec import BaseFrame, BaseDecoder, FrameBinder
from pyrana.errors import ProcessingError, SetupError
import pyrana.ff
# the following is just to export to the clients the Enums.
# pylint: disable=W0611
from pyrana.ffenums import PixelFormat, PictureType


INPUT_CODECS = frozenset()
OUTPUT_CODECS = frozenset()


NUM_PLANES = 8


class SWSMode(IntEnum):
    """
    SWS operational flags.
    This wasn't a proper enum, rather a collection
    of #defines, and that's the reason why it is
    defined here.
    """
    SWS_FAST_BILINEAR = 1
    SWS_BILINEAR = 2
    SWS_BICUBIC = 4
    SWS_X = 8
    SWS_POINT = 0x10
    SWS_AREA = 0x20
    SWS_BICUBLIN = 0x40
    SWS_GAUSS = 0x80
    SWS_SINC = 0x100
    SWS_LANCZOS = 0x200
    SWS_SPLINE = 0x400


def _image_from_frame(ffh, frame, pixfmt):
    """
    builds an Image from a C-frame, by converting the data
    into the given pixfmt. Assumes the source pixfmt is
    different from the source one; otherwise, you just
    need a new Image with a shared underlying Frame
    (see Frame.image()).
    """
    # if we got here, either we have an HUGE bug lurking or
    # srcFormat is already good.
    if not ffh.sws.sws_isSupportedOutput(pixfmt):
        msg = "unsupported pixel format: %s" % pixfmt
        raise ProcessingError(msg)
    null = ffh.ffi.NULL
    width, height = frame.width, frame.height
    sws = ffh.sws.sws_getCachedContext(null,
                                       width, height, frame.format,
                                       width, height, pixfmt,
                                       SWSMode.SWS_BILINEAR,
                                       null, null, null)
    # we don't care about the _resizing_ algorithm here, because
    # we will NOT do any resizing.
    if not sws:
        msg = "cannot get a SWScale context"
        raise ProcessingError(msg)
    with FrameBinder(ffh) as ppframe:
        # alignement does more hurt than good here.
        ret = ffh.lavu.av_image_alloc(ppframe[0].data,
                                      ppframe[0].linesize,
                                      width, height, pixfmt, 1)
        if ret < 0:
            msg = "unable to alloc a %ix%i(%s) picture" \
                  % (width, height, pixfmt)
            raise ProcessingError(msg)
        ret = ffh.sws.sws_scale(sws,
                                frame.data, frame.linesize,
                                0, height,
                                ppframe[0].data, ppframe[0].linesize)
        if ret < 0:
            msg = "swscale failed in pixfmt conversion"
            raise ProcessingError(msg)
        ppframe[0].width = width
        ppframe[0].height = height
        ppframe[0].format = pixfmt
        return Image.from_cdata(ppframe, sws)


class Image(object):
    """
    Represents the Picture data inside a Frame.
    """
    def __init__(self):
        # mostly for documentation purposes, and to make pylint happy.
        self._ff = None
        self._sws = None
        self._ppframe = None
        raise SetupError("Cannot be created directly. Yet.")

    @classmethod
    def from_cdata(cls, ppframe, sws=None):
        """
        builds a pyrana Image from a (cffi-wrapped) libav*
        Frame object. The Picture data itself will still be hold in the
        Frame object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = pyrana.ff.get_handle()
        image = object.__new__(cls)
        image._ff = ffh
        image._sws = sws
        image._ppframe = ppframe
        return image

    def __repr__(self):
        return "Image(width=%i, height=%i, pixfmt=%s," \
               " planes=%i, shared=%s)" \
               % (self.width, self.height, self.pixel_format,
                  self.planes, self.is_shared)

    def __del__(self):
        if not self.is_shared:
            # following the libavcodec headers (and sources),
            # data and extended_data are aliaes.
            # extended_data is alread free()d in avcodec_free_frame().
            self._ff.lavc.avcodec_free_frame(self._ppframe)

    def __len__(self):
        frm = self._ppframe[0]
        return self._ff.lavu.av_image_get_buffer_size(frm.format,
                                                      frm.width,
                                                      frm.height,
                                                      1)

    def __bytes__(self):
        frm = self._ppframe[0]
        pixels = bytearray(len(self))
        idx, dst = 0, 0
        while frm.data[idx] != self._ff.ffi.NULL:
            pixels, dst = self._dump_plane(idx, pixels, dst)
            idx += 1
        return bytes(pixels)

    def _dump_plane(self, idx, pixels=None, dst=0):
        """
        Dump (a copy of) a single plane into a (optionally given)
        bytearray.
        """
        src = 0
        ffh = self._ff
        frm = self._ppframe[0]
        bwidth = ffh.lavu.av_image_get_linesize(frm.format, frm.width, idx)
        size = frm.height * bwidth
        pixels = bytearray(size) if pixels is None else pixels
        plane = ffh.ffi.buffer(frm.data[idx], size)
        for line in range(frm.height):
            dst += line * bwidth
            src += line * frm.linesize[idx]
            pixels[dst:dst+bwidth] = plane[src:src+bwidth]
        return pixels, dst

    def plane(self, idx):
        """
        Read-only byte access to a single plane of the Image.
        """
        if idx < 0 or idx >= NUM_PLANES or \
           self._ppframe[0].data[idx] == self._ff.ffi.NULL:
            raise ProcessingError("bad plane %i" % idx)
        pixels, _ = self._dump_plane(idx)
        return bytes(pixels)

    @property
    def is_shared(self):
        """
        Is the underlying C-Frame shared with the parent py-Frame?
        """
        return self._sws is None

    def convert(self, pixfmt):
        """
        convert the Image data in a new PixelFormat.
        returns a brand new, independent Image.
        """
        return _image_from_frame(self._ff, self._ppframe[0], pixfmt)

    @property
    def planes(self):
        """
        Return the number of planes in the Picture data.
        e.g. RGB: 1; YUV420: 3
        """
        return sum(int(self._ppframe[0].data[idx] != self._ff.ffi.NULL)
                   for idx in range(NUM_PLANES))

    @property
    def width(self):
        """
        Frame width. Expected to be always equal to the stream width.
        """
        frm = self._ppframe[0]
        return frm.width

    @property
    def height(self):
        """
        Frame height. Expected to be always equal to the stream height.
        """
        frm = self._ppframe[0]
        return frm.height

    @property
    def pixel_format(self):
        """
        Frame pixel format. Expected to be always equal
        to the stream pixel format.
        """
        frm = self._ppframe[0]
        return to_pixel_format(frm.format)


class Frame(BaseFrame):
    """
    A Video frame.
    """
    def __repr__(self):
        base = super(Frame, self).__repr__()
        return "%s, ptype=%i, ilace=%s, tff=%s, cnum=%i, dnum=%i)" \
               % (base[:-1],
                  self.pict_type,
                  self.is_interlaced, self.top_field_first,
                  self.coded_pict_number, self.display_pict_number)

    # FIXME: access the ASR.

    def image(self, pixfmt=None):
        """
        Returns a new Image object which provides access to the
        Picture (thus the pixel as bytes()) data.
        """
        if pixfmt is None:  # native data, no conversion
            # FIXME: CAREFUL, gringo: what if the parent frame got GC'd
            # while the derived Image is still alive?
            return Image.from_cdata(self._ppframe)
        return _image_from_frame(self._ff, self._ppframe[0], pixfmt)

    @property
    def pict_type(self):
        """
        Picture type of the frame, see AVPictureType.
        """
        return to_picture_type(self._frame.pict_type)

    @property
    def coded_pict_number(self):
        """
        Picture number in bitstream order.
        """
        return self._frame.coded_picture_number

    @property
    def display_pict_number(self):
        """
        Picture number in display order.
        """
        return self._frame.display_picture_number

    @property
    def top_field_first(self):
        """
        If is_interlaced(), is top field displayed first?
        """
        return bool(self._frame.top_field_first)

    @property
    def is_interlaced(self):
        """
        Is the content of the picture interlaced?
        """
        return bool(self._frame.interlaced_frame)


def _wire_dec(dec):
    """
    Inject the video decoding hooks in a generic decoder.
    """
    ffh = pyrana.ff.get_handle()
    dec._av_decode = ffh.lavc.avcodec_decode_video2
    dec._new_frame = Frame.from_cdata
    dec._mtype = "video"
    return dec


class Decoder(BaseDecoder):
    """
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, input_codec, params=None):
        super(Decoder, self).__init__(input_codec, params)
        _wire_dec(self)

    @classmethod
    def from_cdata(cls, ctx):
        """
        builds a pyrana Video Decoder from (around) a (cffi-wrapped) libav*
        (video)decoder object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        dec = BaseDecoder.from_cdata(ctx)
        return _wire_dec(dec)
