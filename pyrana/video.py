"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.common import to_pixel_format, to_picture_type
from pyrana.codec import BaseFrame, BaseDecoder
import pyrana.errors
import pyrana.ff
# the following is just to export to the clients the Enums.
# pylint: disable=W0611
from pyrana.ffenums import PixelFormat, PictureType


INPUT_CODECS = frozenset()
OUTPUT_CODECS = frozenset()


def _image_from_frame(ffh, frame, pixfmt):
    # if we got here, either we have an HUGE bug lurking or
    # srcFormat is already good.
    if not ffh.sws.sws_isSupportedOutput(pixfmt):
        msg = "unsupported pixel format: %s" % pixfmt
        raise pyrana.errors.ProcessingError(msg)
    NULL = ffh.ffi.NULL
    width, height = frame.width, frame.height
    sws = ffh.sws.sws_getCachedContext(NULL,
                                       width, height, frame.format,
                                       width, height, pixfmt,
                                       1,  # FIXME
                                       NULL, NULL, NULL)
    if sws is NULL:
        msg = "cannot get a SWScale context"
        raise pyrana.errors.ProcessingError(msg)
    ppframe = ffh.ffi.new('AVFrame **')
    ppframe[0] = ffh.lavc.avcodec_alloc_frame()  # FIXME context manager!
    # alignement does more hurt than good here.
    ret = ffh.lavu.av_image_alloc(ppframe[0].data,
                                  ppframe[0].linesize,
                                  width, height, pixfmt, 1)
    if ret < 0:
        ffh.lavc.avcodec_free_frame(ppframe)
        raise pyrana.errors.ProcessingError("FIXME")
    ret = ffh.sws.sws_scale(sws,
                            frame.data, frame.linesize,
                            0, height,
                            ppframe[0].data, ppframe[0].linesize)
    if ret < 0:
        ffh.lavu.av_free(ppframe[0].data[0])  # FIXME
        ffh.lavc.avcodec_free_frame(ppframe)
        raise pyrana.errors.ProcessingError("FIXME")
    ppframe[0].width = width
    ppframe[0].height = height
    ppframe[0].format = pixfmt
    return Image.from_cdata(ppframe, sws)


class Image(object):
    def __init__(self):
        raise pyrana.errors.SetupError("Cannot be created directly. Yet.")

    @classmethod
    def from_cdata(cls, ppframe, sws=None):
        ffh = pyrana.ff.get_handle()
        image = object.__new__(cls)
        image._ff = ffh
        image._sws = sws
        image._ppframe = ppframe
        return image

    def __repr__(self):
        return "TODO"

    def __del__(self):
        if not self.is_shared:
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
        idx = 0
        while frm.data[idx] != self._ff.ffi.NULL:
            # TODO
            idx += 1
        return bytes(pixels)

    @property
    def is_shared(self):
        return self._sws is None

    def convert(self, pixfmt):
        return _image_from_frame(self._ff, self._ppframe[0], pixfmt)

    @property
    def planes(self):
        """
        Return the number of planes in the Picture data.
        e.g. RGB: 1; YUV420: 3
        """
        frm = self._ppframe[0]
        desc = self._ff.lavu.av_pix_fmt_desc_get(frm.format)
        return desc.nb_components

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
        base = super().__repr__()
        # FIXME
        return "%s, ptype=%i, ilace=%s, tff=%s, cnum=%i, dnum=%i)" \
                    % (base[:-1],
                       self.pict_type,
                       self.is_interlaced, self.top_field_first,
                       self.coded_pict_number, self.display_pict_number)

    # FIXME: access the ASR.

    def image(self, pixfmt=None):
        if pixfmt is None:  # native data, no conversion
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
        super().__init__(input_codec, params)
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
