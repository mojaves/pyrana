"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.codec import BaseFrame, BaseDecoder
from pyrana.ffenums import PixelFormat
import pyrana.errors
import pyrana.ff


INPUT_CODECS = frozenset()
OUTPUT_CODECS = frozenset()

#
#class Plane:
#    # no constructor, can be generated only from Images
#    plane_id
#    stride
#    width
#    height
#    pixel_format
#    data
#    size
#
#
#class Image:
#    def __init__(self, width, height, pixel_format, data):
#        """not yet decided"""
#        pass
#    width
#    height
#    pixel_format
#    def plane(self, num):
#        return Plane # FIXME
#    def convert(self, *args):
#        return Image


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
        return self._frame.format  # FIXME: convert to Enum

    # FIXME: access the ASR.

    @property
    def pict_type(self):
        """
        Picture type of the frame, see AVPictureType.
        """
        return self._frame.pict_type  # FIXME: convert to Enum

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
