"""
this module provides the audio codec interface.
Encoders, Decoders and their support code.
"""

from pyrana.common import to_sample_format
from pyrana.codec import BaseFrame, BaseDecoder, FrameBinder
from pyrana.errors import ProcessingError, SetupError
import pyrana.ff
# the following is just to export to the clients the Enums.
# pylint: disable=W0611
from pyrana.ffenums import SampleFormat


INPUT_CODECS = frozenset()
OUTPUT_CODECS = frozenset()


def _samples_from_frame(ffh, frame, smpfmt):
    pass


class Samples(object):
    """
    Represents the Sample data inside a Frame.
    """
    def __init__(self):
        # mostly for documentation purposes, and to make pylint happy.
        self._ff = None
        self._res = None
        self._ppframe = None
        raise SetupError("Cannot be created directly. Yet.")

    @classmethod
    def from_cdata(cls, ppframe, res=None):
        """
        builds a pyrana Image from a (cffi-wrapped) libav*
        Frame object. The Picture data itself will still be hold in the
        Frame object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = pyrana.ff.get_handle()
        samples = object.__new__(cls)
        samples._ff = ffh
        samples._res = res
        samples._ppframe = ppframe
        return samples

    def __repr__(self):
        return "Samples(sfmt=%i, samples=%i," \
               " rate=%i, chans=%i, bps=%i, shared=%s)" \
               % (self.sample_format, self.num_samples,
                  self.sample_rate, self.channels, self.bps,
                  self.is_shared)

    def __del__(self):
        if not self.is_shared:
            self._ff.lavc.avcodec_free_frame(self._ppframe)

    def __len__(self):
        return self.bps * self.num_samples * self.channels

    def __bytes__(self):
        frm = self._ppframe[0]
        samples = bytearray(len(self))
        return bytes(samples)

    @property
    def is_shared(self):
        """
        Is the underlying C-Frame shared with the parent py-Frame?
        """
        return self._res is None

    def convert(self, smpfmt):
        """
        convert the Image data in a new PixelFormat.
        returns a brand new, independent Image.
        """
        return _samples_from_frame(self._ff, self._ppframe[0], smpfmt)

    @property
    def sample_format(self):
        """
        Frame sample format. Expected to be always equal
        to the stream sample format.
        """
        frm = self._ppframe[0]
        return to_sample_format(frm.format)

    @property
    def num_samples(self):
        """
        The number of audio samples (per channel) described by this frame.
        """
        frm = self._ppframe[0]
        return frm.nb_samples

    @property
    def sample_rate(self):
        """
        Sample rate of the audio data.
        """
        frm = self._ppframe[0]
        return self._ff.lavc.av_frame_get_sample_rate(frm)

    @property
    def channels(self):
        """
        The number of audio channels, only used for audio.
        """
        frm = self._ppframe[0]
        return self._ff.lavc.av_frame_get_channels(frm)

    @property
    def bps(self):
        """
        Bytes per sample.
        """
        frm = self._ppframe[0]
        return self._ff.lavu.av_get_bytes_per_sample(frm.format)


class Frame(BaseFrame):
    """
    An Audio frame.
    """
    def __repr__(self):
        base = super(Frame, self).__repr__()
        # FIXME
        return "%s)" \
                    % (base[:-1])  # FIXME

    def samples(self, smpfmt=None):
        """
        Returns a new Image object which provides access to the
        Picture (thus the pixel as bytes()) data.
        """
        if smpfmt is None:  # native data, no conversion
            return Samples.from_cdata(self._ppframe)
        return _samples_from_frame(self._ff, self._ppframe[0], smpfmt)



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
