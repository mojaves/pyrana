"""
this module provides the audio codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.codec import BaseDecoder, CodecMixin
from pyrana.samplefmt import SampleFormat


INPUT_CODECS = frozenset()
OUTPUT_CODECS = frozenset()


class Decoder(BaseDecoder):
    """
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, input_codec, params=None):
        super(Decoder, self).__init__(params)
    
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
    Like the old Pyrana class,
    - add the 'params' property (read-only preferred alias for getParams)
    - no conversion/scaling will be performed
    - add flush() operation
    """
    def __init__(self, name, params=None):
        CodecMixin.__init__(self, params)
        # yes, here we're *intentionally* calling
        # the superclass init explicitely.
        # we *want* this dependency explicit
        # TODO

    def encode(self, frame):
        """encode(frame) -> Packet"""
        raise NotImplementedError

    def flush(self):
        """flush() -> Packet"""
        raise NotImplementedError
