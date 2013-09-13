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

class Frame(BaseFrame):
    """
    A Video frame.
    """
    def __repr__(self):
        # FIXME
        return "Frame(pict_type=%i, is_interlaced=%s, top_field_first=%s)" \
               " #%i/%i" % (self.pict_type, self.is_interlaced,
                            self.top_field_first, self.coded_pict_number,
                            self.display_pict_number)

    @property
    def width(self):
        return self._frame.width

    @property
    def height(self):
        return self._frame.height

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
        ppframe = ffh.ffi.new('AVFrame **')
        ppframe[0] = ffh.lavc.avcodec_alloc_frame()
        ret = ffh.lavc.avcodec_decode_video2(self._ctx, ppframe[0],
                                             self._got_frame, pkt)
        if ret < 0:
            self._ff.lavc.avcodec_free_frame(self._ppframe)
            msg = "Error decoding video frame: %i" % ret
            raise pyrana.errors.ProcessingError(msg)

        if not self._got_frame[0]:
            self._ff.lavc.avcodec_free_frame(ppframe)
            raise pyrana.errors.NeedFeedError()

        return ret, Frame.from_cdata(ppframe)

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

    def decode(self, packets):
        """
        XXX
        """
        frames = []
        pkt_seq = iter(packets)
        pkt = next(pkt_seq)
        while not frames:
            try:
                frames.extend(frm for frm in self.decode_packet(pkt))
            except pyrana.errors.NeedFeedError:
                pkt = next(pkt_seq)
        return frames if len(frames) > 1 else frames[0]

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
