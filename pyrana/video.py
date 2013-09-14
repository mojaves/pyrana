"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.codec import BaseFrame, BaseDecoder, CodecMixin
from pyrana.pixelfmt import PixelFormat
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
        return "%sFrame(pts=%i, pict_type=%i, is_interlaced=%s," \
               " top_field_first=%s) # %ix%i@%i %i/%i" \
                    % ("Key" if self.is_key else "",
                       self.pts, self.pict_type,
                       self.is_interlaced, self.top_field_first,
                       self.width, self.height, self.pixel_format,
                       self.coded_pict_number, self.display_pict_number)

    @property
    def width(self):
        return self._frame.width

    @property
    def height(self):
        return self._frame.height

    @property
    def pixel_format(self):
        return self._frame.format  # FIXME

    @property
    def pict_type(self):
        return self._frame.pict_type  # FIXME

    @property
    def coded_pict_number(self):
        return self._frame.coded_picture_number

    @property
    def display_pict_number(self):
        return self._frame.display_picture_number

    @property
    def top_field_first(self):
        return bool(self._frame.top_field_first)

    @property
    def is_interlaced(self):
        return bool(self._frame.interlaced_frame)


def _wire_dec(dec):
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
        dec = BaseDecoder.from_cdata(ctx)
        return _wire_dec(dec)


#class Encoder(CodecMixin):
#    """
#    - add the 'params' property (read-only preferred alias for getParams)
#    - no conversion/scaling will be performed
#    - add flush() operation
#    """
#    def __init__(self, output_codec, params=None):
#        CodecMixin.__init__(self, params)
#        # yes, here we're *intentionally* calling
#        # the superclass init explicitely.
#        # we *want* this dependency explicit
#        # TODO
#
#    def encode(self, frame):
#        """
#        encode(Frame) -> Packet
#        """
#        raise NotImplementedError
#
#    def flush(self):
#        """
#        flush() -> Packet
#        """
#        raise NotImplementedError
