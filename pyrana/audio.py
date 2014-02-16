"""
this module provides the audio codec interface.
Encoders, Decoders and their support code.
"""

from enum import IntEnum
from .common import to_sample_format
from .codec import BaseFrame, BaseDecoder, BaseEncoder, bind_frame
from .codec import Payload, make_payload, wire_decoder, wire_encoder
from .codec import _new_av_frame_pp
from .errors import ProcessingError, SetupError
from . import ff
# the following is just to export to the clients the Enums.
# pylint: disable=W0611
from .ffenums import SampleFormat
from .ffaclayout import ChannelLayout


InputCodec = None  # to be filled in setup()
OutputCodec = None  # to be filled in setup()


class AVRounding(IntEnum):
    """
    Rounding methods.
    Maybe should be moved into a more generic module.
    """
    AV_ROUND_ZERO = 0
    AV_ROUND_INF = 1
    AV_ROUND_DOWN = 2
    AV_ROUND_UP = 3
    AV_ROUND_NEAR_INF = 5
    AV_ROUND_PASS_MINMAX = 8192


def _setup_av_frame_pp(ffh, ppframe, rate, layout, samplefmt, nsamples):
    """
    WRITEME
    """
    ppframe[0].channel_layout = layout
    ppframe[0].sample_rate = rate
    ppframe[0].format = samplefmt
    ppframe[0].nb_samples = ffh.lavu.av_rescale_rnd(nsamples,
                                                    rate,
                                                    rate,
                                                    AVRounding.AV_ROUND_UP)

    nb_channels = ffh.lavu.av_get_channel_layout_nb_channels(layout)

    ret = ffh.lavu.av_samples_alloc(ppframe[0].data,
                                    ppframe[0].linesize,
                                    nb_channels,
                                    ppframe[0].nb_samples,
                                    samplefmt,
                                    1)
    if ret < 0:
        raise ProcessingError('cannot allocate the samples buffer')


def _samples_from_frame(ffh, parent, frame, smpfmt):
    """
    builds an Samples from a C-frame, by converting the data
    into the given smpfmt. Assumes the source smpfmt is
    different from the source one; otherwise, you just
    need a new Samples with a shared underlying Frame
    (see Frame.samples()).
    """
    null = ffh.ffi.NULL
    swr = ffh.swr.swr_alloc_set_opts(null,
                                     frame.channel_layout,
                                     smpfmt,
                                     frame.sample_rate,
                                     frame.channel_layout,
                                     frame.format,
                                     frame.sample_rate,
                                     0,
                                     null)
    if not swr:
        msg = "cannot get a SWResample context"
        raise ProcessingError(msg)

    ret = ffh.swr.swr_init(swr)
    if ret < 0:
        msg = "cannot initialize the resampling context"
        raise ProcessingError(msg)

    with bind_frame(ffh) as ppframe:
        _setup_av_frame_pp(ffh,
                           ppframe,
                           frame.sample_rate,
                           frame.channel_layout,
                           smpfmt,
                           frame.nb_samples)
        ret = ffh.swr.swr_convert(swr,
                                  ppframe[0].data,
                                  ppframe[0].nb_samples,
                                  frame.data,
                                  frame.nb_samples)
        if ret < 0:
            raise ProcessingError('cannot convert the audio buffer')
        return Samples.from_cdata(ppframe, swr, parent)


class Samples(Payload):
    """
    Represents the Sample data inside a Frame.
    """
    def __init__(self):
        # mostly for documentation purposes, and to make pylint happy.
        self._ff = None
        self._ppframe = None
        self._parent = None
        self._swr = None
        raise SetupError("Cannot be created directly. Yet.")

    @classmethod
    def from_cdata(cls, ppframe, swr=None, parent=None):
        """
        builds a pyrana Image from a (cffi-wrapped) libav*
        Frame object. The Picture data itself will still be hold in the
        Frame object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = ff.get_handle()
        samples = make_payload(cls, ffh, ppframe, parent)
        setattr(samples, '_swr', swr)
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
        frm = self._ppframe[0]  # shortcut
        return sum(int(frm.linesize[idx])
                   for idx in range(self.channels))

    def blob(self):
        """returns the bytes() dump of the object"""
        frm = self._ppframe[0]
        samples = bytearray(len(self))
        idx, dst = 0, 0
        while frm.extended_data[idx] != self._ff.ffi.NULL:
            samples, dst = self._dump_channel(idx, samples, dst)
            idx += 1
        return bytes(samples)

    def _dump_channel(self, idx, samples=None, dst=0):
        """
        Dump (a copy of) a single channel into a (optionally given)
        bytearray.
        """
        frm = self._ppframe[0]  # shortcut
        size = frm.linesize[idx]
        samples = bytearray(size) if samples is None else samples
        chan = self._ff.ffi.buffer(frm.extended_data[idx], size)
        samples[dst:dst+size] = chan[:]
        return samples, dst+size

    def channel(self, idx):
        """
        Read-only byte access to a single channel of the Samples.
        """
        if idx < 0 or idx > self.channels or \
           self._ppframe[0].extended_data[idx] == self._ff.ffi.NULL:
            raise ProcessingError("bad channel %i" % idx)
        samples, _ = self._dump_channel(idx)
        return bytes(samples)

    @property
    def is_shared(self):
        """
        Is the underlying C-Frame shared with the parent py-Frame?
        """
        return self._swr is None

    def convert(self, smpfmt):
        """
        convert the Samples data in a new SampleFormat.
        returns a brand new, independent Image.
        """
        return _samples_from_frame(self._ff, self, self._ppframe[0], smpfmt)

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
    def __init__(self, rate, layout, samplefmt):
        super(Frame, self).__init__()
        self._ppframe = _new_av_frame_pp(self._ff)
        self._frame = self._ppframe[0]
        _setup_av_frame_pp(self._ff, self._ppframe, rate, layout, samplefmt,
                           1024)  # FIXME

    def __repr__(self):
        base = super(Frame, self).__repr__()
        return "%s)" \
               % (base[:-1])

    def samples(self, smpfmt=None):
        """
        Returns a new Image object which provides access to the
        Picture (thus the pixel as bytes()) data.
        """
        if smpfmt is None:  # native data, no conversion
            return Samples.from_cdata(self._ppframe)
        return _samples_from_frame(self._ff, self, self._ppframe[0], smpfmt)


def fill_s16(frame):
    """
    fill a audio frame with a single tone sound
    """
    frm = frame.cdata  # shortcut
    if frm.format != SampleFormat.AV_SAMPLE_FMT_S16:  # 0
        raise ProcessingError("wrong sample format")

    # TODO


class Decoder(BaseDecoder):
    """
    Decodes audio Packets into audio Frames.
    """
    @staticmethod
    def wire(dec):
        """
        wire up the Decoder. See codec.wire_decoder
        """
        ffh = ff.get_handle()
        return wire_decoder(dec,
                            ffh.lavc.avcodec_decode_audio4,
                            Frame.from_cdata,
                            "audio")

    def __init__(self, input_codec, params=None):
        super(Decoder, self).__init__(input_codec, params)
        self.wire(self)

    @classmethod
    def from_cdata(cls, ctx):
        """
        builds a pyrana Audio Decoder from (around) a (cffi-wrapped) libav*
        (audio)decoder object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        return cls.wire(BaseDecoder.from_cdata(ctx))


class Encoder(BaseEncoder):
    """
    Encode audio Frames into Packets.
    """
    @staticmethod
    def wire(enc):
        """
        wire up the Encoder. See codec.wire_encoder
        """
        ffh = ff.get_handle()
        return wire_encoder(enc,
                            ffh.lavc.avcodec_encode_audio2,
                            "audio")

    def setup(self):
        super(Encoder, self).setup()
        layout = self._params.get("channel_layout")
        if layout is not None:
            # this HAS to prevail on channels
            count_channels = self._ff.lavu.av_get_channel_layout_nb_channels
            # shortcut
            self._params["channels"] = count_channels(layout)

    def __init__(self, output_codec, params):
        super(Encoder, self).__init__(output_codec, params)
        self.wire(self)

    @classmethod
    def from_cdata(cls, ctx, params, codec=None):
        """
        builds a pyrana audio Encoder from (around) a (cffi-wrapped) liabv*
        (audio) context.
        WARNING: raw access. Use with care.
        """
        return cls.wire(BaseEncoder.from_cdata(ctx, params, codec))
