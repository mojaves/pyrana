"""
this module provides the audio codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.codec import BaseFrame, BaseDecoder, CodecMixin
from pyrana.ffenums import SampleFormat
import pyrana.errors
import pyrana.ff


INPUT_CODECS = frozenset()
OUTPUT_CODECS = frozenset()


class Frame(BaseFrame):
    """
    An Audio frame.
    """
    def __repr__(self):
        # FIXME
        return "Frame(sfmt=%i, samples=%i, rate=%i, chans=%i)" % (
                self.sample_format, self.num_samples,
                self.sample_rate, self.channels)

    @property
    def sample_format(self):
        return self._frame.format  # FIXME

    @property
    def num_samples(self):
        return self._frame.nb_samples

    @property
    def sample_rate(self):
        return self._frame.sample_rate

    @property
    def channels(self):
        return self._frame.channels

def _wire_dec(dec):
    ffh = pyrana.ff.get_handle()
    dec._av_decode = ffh.lavc.avcodec_decode_audio4
    dec._new_frame = Frame.from_cdata
    dec._mtype = "audio"
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
#    Like the old Pyrana class,
#    - add the 'params' property (read-only preferred alias for getParams)
#    - no conversion/scaling will be performed
#    - add flush() operation
#    """
#    def __init__(self, name, params=None):
#        CodecMixin.__init__(self, params)
#        # yes, here we're *intentionally* calling
#        # the superclass init explicitely.
#        # we *want* this dependency explicit
#        # TODO
#
#    def encode(self, frame):
#        """encode(frame) -> Packet"""
#        raise NotImplementedError
#
#    def flush(self):
#        """flush() -> Packet"""
#        raise NotImplementedError
