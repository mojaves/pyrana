"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

import pyrana.errors
from pyrana.packet import raw_packet
from pyrana.codec import BaseDecoder, CodecMixin
from pyrana.codec import BaseFrame
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

class Frame(BaseFrame):
    """
    A Video frame.
    """
    def __repr__(self):
        return "Frame() video"


class Decoder(BaseDecoder):
    """
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, input_codec, params=None):
        super(Decoder, self).__init__(input_codec, params)

    def _decode_pkt(self, pkt):
        """
        A packet can legally contain more than one frame.
        """
        ffh = self._ff
        self._ppframe[0] = ffh.lavc.avcodec_alloc_frame()
        ret = ffh.lavc.avcodec_decode_video2(self._ctx, self._ppframe[0],
                                             self._got_frame, pkt)
        if ret < 0:
            self._ff.lavc.avcodec_free_frame(self._ppframe)
            msg = "Error decoding video frame: %i" % ret
            raise pyrana.errors.ProcessingError(msg)

        if not self._got_frame[0]:
            self._ff.lavc.avcodec_free_frame(self._ppframe)
            raise pyrana.errors.NeedFeedError()

        return ret, Frame.from_cdata(self._ppframe[0])

    def decode_packet(self, packet):
        """
        XXX
        """
        with packet.raw_pkt() as pkt:
            while pkt.size > 0:
                ret, frame = self._decode_pkt(pkt)
                yield frame
                pkt.data += ret
                pkt.size -= ret

    def decode(self, packet):
        """
        decode(packet) -> frame
        """
        frames = list(self.decode_packet(packet))
        return frames[0] if len(frames) == 1 else frames

    def flush(self):
        """
        flush() -> Frame
        """
        with raw_packet(0) as cpkt:
            _, frame = self._decode_pkt(cpkt)
            return frame


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
