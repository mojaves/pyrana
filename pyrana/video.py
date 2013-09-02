"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

import pyrana.formats
from pyrana.common import CodecMixin
from pyrana.pixelfmt import PixelFormat


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
#
#
#class Frame:
#    def __init__(self, image, pts, is_key, is_interlaced, top_field_first):
#        """not yet decided"""
#        pass
#    pts
#    is_key
#    image
#    top_field_first
#    is_interlaced
#    pic_type # can only set by decoder/encoder
#    coded_num # ditto
#    display_num # ditto
#

class Decoder(CodecMixin):
    """
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, input_codec, params=None):
        CodecMixin.__init__(self, params)
        # yes, here we're *intentionally* calling
        # the superclass init explicitely.
        # we *want* this dependency explicit
        # TODO

    @classmethod
    def from_demuxer(cls, dmx, sid):
        pass

    def decode(self, packet):
        """
        decode(Packet) -> Frame
        """
        raise NotImplementedError

    def flush(self):
        """
        flush() -> Frame
        """
        raise NotImplementedError


class Encoder(CodecMixin):
    """
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, output_codec, params=None):
        CodecMixin.__init__(self, params)
        # yes, here we're *intentionally* calling
        # the superclass init explicitely.
        # we *want* this dependency explicit
        # TODO

    def encode(self, frame):
        """
        encode(Frame) -> Packet
        """
        raise NotImplementedError

    def flush(self):
        """
        flush() -> Packet
        """
        raise NotImplementedError
