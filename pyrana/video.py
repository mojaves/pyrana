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


class Frame(BaseFrame):
    """
    A Video frame.
    """
    def __repr__(self):
        # FIXME
        return "%sFrame(pts=%i, ptype=%i, ilace=%s, tff=%s)" \
               " # %ix%i@%i %i/%i" \
                    % ("Key" if self.is_key else "",
                       self.pts, self.pict_type,
                       self.is_interlaced, self.top_field_first,
                       self.width, self.height, self.pixel_format,
                       self.coded_pict_number, self.display_pict_number)

    def __len__(self):
        return self._ff.lavu.av_image_get_buffer_size(self._frame.format,
                                                      self._frame.width,
                                                      self._frame.height,
                                                      1)

    def __bytes__(self):
        pixels = bytearray(len(self))
        print(len(pixels), len(self))
        idx = 0
        while self._frame.data[idx] != self._ff.ffi.NULL:
            print(self._frame.data[idx])
            print(self._frame.linesize[idx], self._frame.width,
                    self._frame.height)
            idx += 1
        X = bytes(pixels)
        print(len(X))
        return X

    @property
    def planes(self):
        """
        Return the number of planes in the Picture data.
        e.g. RGB: 1; YUV420: 3
        """
        desc = self._ff.lavu.av_pix_fmt_desc_get(self._frame.format)
        return desc.nb_components

    @property
    def width(self):
        """
        Frame width. Expected to be always equal to the stream width.
        """
        return self._frame.width

    @property
    def height(self):
        """
        Frame height. Expected to be always equal to the stream height.
        """
        return self._frame.height

    @property
    def pixel_format(self):
        """
        Frame pixel format. Expected to be always equal
        to the stream pixel format.
        """
        return to_pixel_format(self._frame.format)

    # FIXME: access the ASR.

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
