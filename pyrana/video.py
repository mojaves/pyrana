"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

from enum import IntEnum
from .common import to_pixel_format, to_picture_type
from .codec import BaseFrame, BaseDecoder, bind_frame
from .codec import Payload, make_payload, wire_decoder
from .errors import ProcessingError, SetupError
from . import ff
# the following is just to export to the clients the Enums.
# pylint: disable=W0611
from .ffenums import PixelFormat, PictureType


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


def _image_from_frame(ffh, parent, cframe, pixfmt):
    """
    builds an Image from a C-frame, by converting the data
    into the given pixfmt. Assumes the source pixfmt is
    different from the source one; otherwise, you just
    need a new Image with a shared underlying Frame
    (see Frame.image()).
    """
    # if we got here, either we have an HUGE bug lurking or
    # srcFormat is already good.
    if pixfmt == PixelFormat.AV_PIX_FMT_NONE or \
      not ffh.sws.sws_isSupportedOutput(pixfmt):
        msg = "unsupported pixel format: %s" % pixfmt
        raise ProcessingError(msg)
    null = ffh.ffi.NULL
    width, height = cframe.width, cframe.height
    sws = ffh.sws.sws_getCachedContext(null,
                                       width, height, cframe.format,
                                       width, height, pixfmt,
                                       SWSMode.SWS_BILINEAR,
                                       null, null, null)
    # we don't care about the _resizing_ algorithm here, because
    # we will NOT do any resizing.
    if not sws:
        msg = "cannot get a SWScale context"
        raise ProcessingError(msg)
    with bind_frame(ffh) as ppframe:
        # alignement does more hurt than good here.
        ret = ffh.lavu.av_image_alloc(ppframe[0].data,
                                      ppframe[0].linesize,
                                      width, height, pixfmt, 1)
        if ret < 0:
            msg = "unable to alloc a %ix%i(%s) picture" \
                  % (width, height, pixfmt)
            raise ProcessingError(msg)
        ret = ffh.sws.sws_scale(sws,
                                cframe.data, cframe.linesize,
                                0, height,
                                ppframe[0].data, ppframe[0].linesize)
        if ret < 0:
            msg = "swscale failed in pixfmt conversion"
            raise ProcessingError(msg)
        ppframe[0].width = width
        ppframe[0].height = height
        ppframe[0].format = pixfmt
        return Image.from_cdata(ppframe, sws, parent)


def _plane_copy(pixels, plane,
                dst_linesize, src_linesize,
                bwidth, height,
                dst=0):
    """
    workhorse function. Copy data between two (optionally)
    strided data planes.
    Usually the destination buffer isn't padded, aka
    has stride == width.
    """
    if src_linesize < bwidth or dst_linesize < bwidth:
        raise ProcessingError('bytewidth too small')
    src = 0
    while height:
        pixels[dst:dst+bwidth] = plane[src:src+bwidth]
        dst += dst_linesize
        src += src_linesize
        height -= 1
    return dst


class Image(Payload):
    """
    Represents the Picture data inside a Frame.
    """
    def __init__(self):
        # mostly for documentation purposes, and to make pylint happy.
        self._ff = None
        self._ppframe = None
        self._parent = None
        self._sws = None
        raise SetupError("Cannot be created directly. Yet.")

    @classmethod
    def from_cdata(cls, ppframe, sws=None, parent=None):
        """
        builds a pyrana Image from a (cffi-wrapped) libav*
        Frame object. The Picture data itself will still be hold in the
        Frame object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = ff.get_handle()
        image = make_payload(cls, ffh, ppframe, parent)
        setattr(image, '_sws', sws)
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

    def blob(self):
        """
        returns the bytes() dump of the object.
        """
        pixels = bytearray(len(self))
        idx, dst = 0, 0
        while self._ppframe[0].data[idx] != self._ff.ffi.NULL:
            pixels, dst = self._dump_plane(idx, pixels, dst)
            idx += 1
        return bytes(pixels)

    def _dump_plane(self, idx, pixels=None, dst=0):
        """
        Dump (a copy of) a single plane into a (optionally given)
        bytearray.
        """
        ffh = self._ff
        frm = self._ppframe[0]
        bwidth = ffh.lavu.av_image_get_linesize(frm.format, frm.width, idx)
        height = self._plane_height(idx)
        pixels = bytearray(bwidth * height) if pixels is None else pixels
        plane = ffh.ffi.buffer(frm.data[idx], frm.linesize[idx] * height)
        dst += _plane_copy(pixels, plane,
                           bwidth, frm.linesize[idx],
                           bwidth, height, dst)
        return pixels, dst

    def _plane_height(self, idx=0):
        """
        Computes a plane height. Due to chroma subsampling, plane dimensions
        aren't necessarily equal to each other.
        """
        frm = self._ppframe[0]
        height = frm.height
        if idx == 1 or idx == 2:
            desc = self._ff.lavu.av_pix_fmt_desc_get(frm.format)
            height = frm.height >> desc.log2_chroma_h
        return height

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
        return _image_from_frame(self._ff, self, self._ppframe[0], pixfmt)

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
        num, den = self.asr
        return "%s, ptype=%i, ilace=%s, tff=%s," \
               " cnum=%i, dnum=%i, asr=%i/%i)" \
               % (base[:-1],
                  self.pict_type,
                  self.is_interlaced, self.top_field_first,
                  self.coded_pict_number, self.display_pict_number,
                  num, den)

    def image(self, pixfmt=None):
        """
        Returns a new Image object which provides access to the
        Picture (thus the pixel as bytes()) data.
        """
        if pixfmt is None:  # native data, no conversion
            return Image.from_cdata(self._ppframe, parent=self)
        return _image_from_frame(self._ff, self, self._ppframe[0], pixfmt)

    @property
    def asr(self):
        """
        The sample aspect ratio of the frame.
        """
        sar = self._frame.sample_aspect_ratio  # shortcut
        return (sar.num, sar.den)

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


class Decoder(BaseDecoder):
    """
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    @staticmethod
    def wire(dec):
        """
        wire up the Decoder. See codec.wire_decoder
        """
        ffh = ff.get_handle()
        return wire_decoder(dec,
                            ffh.lavc.avcodec_decode_video2,
                            Frame.from_cdata,
                            "video")

    def __init__(self, input_codec, params=None):
        super(Decoder, self).__init__(input_codec, params)
        self.wire(self)

    @classmethod
    def from_cdata(cls, ctx):
        """
        builds a pyrana Video Decoder from (around) a (cffi-wrapped) libav*
        (video)decoder object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        return cls.wire(BaseDecoder.from_cdata(ctx))
