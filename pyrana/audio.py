"""
this module provides the audio codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.common import to_sample_format
from pyrana.codec import BaseFrame, BaseDecoder
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
        """
        Frame sample format. Expected to be always equal
        to the stream sample format.
        """
        return to_sample_format(self._frame.format)

    @property
    def num_samples(self):
        """
        The number of audio samples (per channel) described by this frame.
        """
        return self._frame.nb_samples

    @property
    def sample_rate(self):
        """
        Sample rate of the audio data.
        """
        return self._ff.lavc.av_frame_get_sample_rate(self._frame)

    @property
    def channels(self):
        """
        The number of audio channels, only used for audio.
        """
        return self._ff.lavc.av_frame_get_channels(self._frame)


def _wire_dec(dec):
    """
    Inject the audio decoding hooks in a generic decoder.
    """
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
        """
        builds a pyrana Audio Decoder from (around) a (cffi-wrapped) libav*
        (audio)decoder object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        dec = BaseDecoder.from_cdata(ctx)
        return _wire_dec(dec)
