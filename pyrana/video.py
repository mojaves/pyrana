"""
this module provides the video codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.common import CodecMixin
from pyrana.pixelfmt import PixelFormat


INPUT_CODECS = frozenset()
OUTPUT_CODECS = frozenset()


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

    def decode(self, packet):
        """
        decode(packet) -> frame
        """
        raise NotImplementedError

    def flush(self):
        """
        flush() -> frame
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
        encode(frame) -> packet
        """
        raise NotImplementedError

    def flush(self):
        """
        flush() -> packet
        """
        raise NotImplementedError
