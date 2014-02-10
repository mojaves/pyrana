"""
Common code shared by audio and video codecs.
This module is not part of the pyrana public API.
"""

from types import GeneratorType
from contextlib import contextmanager
from enum import IntEnum

from .packet import Packet, raw_packet, bind_packet
from .common import PY3, MediaType, to_media_type, to_str, AttrDict, strerror
from .errors import PyranaError, ProcessingError, SetupError
from .errors import NeedFeedError, EOSError, WrongParameterError
from . import ff


class CodecFlag(IntEnum):
    """
    wrapper for the (wannabe) enum in avcodec.h
    CODEC_FLAG_*
    """
    UNALIGNED = 0x0001
    QSCALE = 0x0002  # fixed qscale.
    _4MV = 0x0004  # 4 MV per MB allowed
    OUTPUT_CORRUPT = 0x0008
    QPEL = 0x0010
    GMC = 0x0020
    MV0 = 0x0040  # try a MB with MV=<0,0>.
    INPUT_PRESERVED = 0x0100
    PASS1 = 0x0200
    PASS2 = 0x0400
    GRAY = 0x2000  # decode/encode grayscale.
    PSNR = 0x8000
    TRUNCATED = 0x00010000  # truncated at a random
    NORMALIZE_AQP = 0x00020000
    INTERLACED_DCT = 0x00040000
    LOW_DELAY = 0x00080000
    GLOBAL_HEADER = 0x00400000
    BITEXACT = 0x00800000
    AC_PRED = 0x01000000
    LOOP_FILTER = 0x00000800
    INTERLACED_ME = 0x20000000
    CLOSED_GOP = 0x80000000


class CodecFlag2(IntEnum):
    """
    wrapper for the (wannabe) enum in avcodec.h
    CODEC_FLAG2_*
    """
    FAST = 0x00000001  # non spec compliant speedup
    NO_OUTPUT = 0x00000004  # no bitstream encoding.
    LOCAL_HEADER = 0x00000008  # global headers at every keyframe
    IGNORE_CROP = 0x00010000
    CHUNKS = 0x00008000  # bitstream truncated at a packet boundaries
    SHOW_ALL = 0x00400000


def make_codec(vcodec, acodec, stream_id, ctx, *args):
    """
    builds the right decoder for a given stream
    of an AVCodecContext.
    """
    def unsupported(ctx, *args):
        """
        adapter factory function of a stream type
        not supported by pyrana.
        """
        msg = "unsupported type %s for stream %s" \
              % (to_media_type(ctx.codec_type), stream_id)
        raise ProcessingError(msg)

    maker = {MediaType.AVMEDIA_TYPE_VIDEO: vcodec.from_cdata,
             MediaType.AVMEDIA_TYPE_AUDIO: acodec.from_cdata}
    xcodec = maker.get(ctx.codec_type, unsupported)
    return xcodec(ctx, *args)


def _setup_av_ctx(ctx, params):
    """
    update an AVCodecContext `ctx` with the values
    from the given `params` object.
    """
    for name, value in params.items():
        if name == 'time_base':
            ctx.time_base.num = value[0]
            ctx.time_base.den = value[1]
        else:
            try:
                setattr(ctx, name, value)
            except AttributeError:
                msg = "unsupported parameter: %s" % name
                raise WrongParameterError(msg)


class CodecMixin(object):
    """
    Mixin. Abstracts the common codec attributes:
    parameters reference, read-only access, extradata
    management.
    """
    def __init__(self, params=None):
        params = {} if params is None else params
        self._ff = ff.get_handle()
        self._params = params
        self._codec = None
        self._ctx = None
        self._xdata = None
        self._repr = "CodecMixin(codec=%s)"
        self._got_data = None

    @property
    def ready(self):
        """
        is the codec readu to go?
        """
        return self._got_data is not None

    def __repr__(self):
        # how funny. If we use an array of chars like a string, it crashes.
        codec_id = self._codec.id  # if self._codec else self._ctx.codec_id
        cname = self._ff.lavc.avcodec_get_name(codec_id)
        return self._repr % (to_str(cname))

    def setup(self):
        """
        Dispach the given parameters to the internal
        (FFmpeg) data structures.
        """
        _setup_av_ctx(self._ctx, self._params)

    def open(self, ffh=None):  # ffh parameter only for testing purposes.
        """
        opens the codec into the codec context.
        """
        if self.ready is False:
            ffh = self._ff if ffh is None else ffh
            err = ffh.lavc.avcodec_open2(self._ctx, self._codec,
                                         ffh.ffi.NULL)
            if err < 0:
                raise SetupError("avcodec open failed: %i (%s)" % (
                                 err, strerror(err, ffh)))
            self._got_data = ffh.ffi.new("int [1]")
        return self

    @property
    def media_type(self):
        """
        the codec media type.
        """
        return self._ctx.codec_type

    @property
    def params(self):
        """
        the codec parameters.
        """
        par = AttrDict('Params', self._params)
        par.freeze()
        return par

    @property
    def extra_data(self):
        """
        bytearray-like, read-write
        """
        if self._xdata is None and self._ctx is not None:
            self._xdata = self._ff.ffi.buffer(self._ctx.extradata,
                                              self._ctx.extradata_size)
        return self._xdata


class BaseFrame(object):
    """
    Abstract Frame class. Provides bookkeeping and access
    to attributes common to frames of all media types.
    Do not use directly.
    """
    def __init__(self):
        self._ff = ff.get_handle()
        self._ppframe = None
        self._frame = None

    def __del__(self):
        self._ff.lavc.avcodec_free_frame(self._ppframe)

    def __repr__(self):
        return "%sFrame(pts=%i)" % ("Key" if self.is_key else "", self.pts)

    @property
    def is_key(self):
        """
        Is this a key frame?
        """
        return self._frame.key_frame if self._frame else False

    @property
    def pts(self):
        """
        The Presentation TimeStamp of this Frame.
        """
        return self._frame.pts if self._frame else 0

    @property
    def cdata(self):
        """
        Direct access to the internal C AVFrame object.
        """
        return self._ppframe[0]

    @classmethod
    def from_cdata(cls, ppframe):
        """
        builds a pyrana generic Base Frame from (around) a (cffi-wrapped)
        libav* AVFrame object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = ff.get_handle()
        frame = object.__new__(cls)
        setattr(frame, '_ff', ffh)
        setattr(frame, '_ppframe', ppframe)
        setattr(frame, '_frame', ppframe[0])
        return frame


def _null_av_encode(ctx, pkt, frame, flag):
    """
    private use only. Placeholder callable for hooks
    in the BaseEncoder which MUST have to be replaced in the
    specific {Audio,Video,...} Encoders.
    """
    assert ctx
    assert pkt
    assert frame
    assert flag
    return -1


def _null_av_decode(ctx, frame, flag, pkt):
    """
    private use only. Placeholder callable for hooks
    in the BaseDecoder which MUST have to be replaced in the
    specific {Audio,Video,...} Decoders.
    """
    assert ctx
    assert frame
    assert flag
    assert pkt
    return -1


def _null_new_frame(frame):
    """
    private use only. Placeholder callable for hooks
    in the BaseDecoder which MUST have to be replaced in the
    specific {Audio,Video,...} Decoders.
    """
    assert frame
    raise ProcessingError("Generic decoders cannot run")


def _new_av_frame_pp(ffh):
    """
    allocates an indirect AVFrame reference
    needed by the constraint of the FFMpeg API.
    """
    ppframe = ffh.ffi.new('AVFrame **')
    ppframe[0] = ffh.lavc.avcodec_alloc_frame()
    return ppframe


@contextmanager
def bind_frame(ffh):
    """
    allocates an AVFrame and cleans it up on exception.
    """
    try:
        ppframe = _new_av_frame_pp(ffh)
        yield ppframe
    except PyranaError:
        ffh.lavc.avcodec_free_frame(ppframe)
        raise
    # otherwise the ownership *has* to be passed.


def make_fetcher(seq):
    """
    Builds a callable which extracts, deletes from
    the originating sequence-like (either materialized
    or generating) and returns an item.
    """
    # meh, goodbye to duck typing. Do anyone has a better idea?
    if isinstance(seq, GeneratorType):
        def _fetch():
            """fetch from a generator"""
            return next(seq)
        return _fetch
    elif isinstance(seq, list):
        def _fetch():
            """fetch from a list"""
            return seq.pop(0)
        return _fetch
    else:
        raise ProcessingError("unsupported source type")


def make_payload(cls, ffh, ppframe, parent):
    """
    Setups the common fields of every multimedia payload object.
    """
    payload = object.__new__(cls)
    setattr(payload, '_ff', ffh)
    setattr(payload, '_ppframe', ppframe)
    setattr(payload, '_parent', parent)
    # for shared payloads, we must keep alive the parent (pp)frame.
    return payload


def wire_encoder(enc, av_encode, mtype):
    """
    Injects the specific encoding hooks in a generic encoder.
    """
    setattr(enc, '_av_encode', av_encode)
    setattr(enc, '_mtype', mtype)
    return enc


def wire_decoder(dec, av_decode, new_frame, mtype):
    """
    Injects the specific decoding hooks in a generic decoder.
    """
    setattr(dec, '_av_decode', av_decode)
    setattr(dec, '_new_frame', new_frame)
    setattr(dec, '_mtype', mtype)
    return dec


def find_encoder(output_codec, ffh=None):
    """
    Finds a suitable encoder for the given output codec.
    Raises SetupError if the codec isn't supported.
    """
    ffh = ff.get_handle() if ffh is None else ffh
    if isinstance(output_codec, str):
        name = output_codec.encode('utf-8')
        return ffh.lavc.avcodec_find_encoder_by_name(name)
    raise SetupError("not yet supported")


class BaseEncoder(CodecMixin):
    """
    Encoder base class. Common both to audio and video encoders.
    """
    def __init__(self, output_codec, params, delay_open=False):
        super(BaseEncoder, self).__init__(params)
        ffh = self._ff
        self._codec = find_encoder(output_codec, ffh)
        self._ctx = ffh.lavc.avcodec_alloc_context3(self._codec)
        self._av_encode = _null_av_encode
        self._repr = "Encoder(output_codec=%s)"
        self._mtype = "abstract"
        self.setup()
        if not delay_open:
            self.open()

    def _encode_frame(self, cframe):
        """
        Puts a frame into the encoder, and extracts the encoded packet.
        (WRITEME)
        """
        with bind_packet(self._ff) as pkt:
            ret = self._av_encode(self._ctx, pkt, cframe, self._got_data)
            if ret < 0:
                msg = "Error encoding %s frame: %i" % (self._mtype, ret)
                raise ProcessingError(msg)

            if not self._got_data[0]:
                raise NeedFeedError()

            return ret, Packet.from_cdata(pkt)

    def encode(self, frame):
        """
        Encode a logical frame in one or possibly more)packets, and
        return an iterable which will yield all the packets produced.
        """
        _, pkt = self._encode_frame(frame.cdata)
        return pkt

    def flush(self):
        """
        emits all packets which may have been buffered by the Encoder
        and empties such buffers. Call it last, do not intermix with
        encode*() calls.
        caution: more than one encoded frame (thus many packets)
        can be buffered.
        Raises NeedFeedError if all the internal buffers are empty.
        """
        return self._encode_frame(self._ff.ffi.NULL)

    @classmethod
    def from_cdata(cls, ctx, params, codec=None):
        """
        builds a pyrana Encoder from (around) a (cffi-wrapped) libav*
        decoder object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        enc = object.__new__(cls)
        CodecMixin.__init__(enc, params)  # MUST be explicit
        ctx.codec = codec
        setattr(enc, '_codec', ctx.codec)
        setattr(enc, '_ctx', ctx)
        setattr(enc, '_av_encode', _null_av_encode)
        setattr(enc, '_got_data', None)
        setattr(enc, '_mtype', "abstract")
        setattr(enc, '_repr', "Encoder(output_codec=%s)")
        enc.setup()
        return enc.open()

    def register(self, muxer):
        return muxer.register_stream(self._codec)


class BaseDecoder(CodecMixin):
    """
    Decoder base class. Common both to audio and video decoders.
    """
    def __init__(self, input_codec, params=None, delay_open=False):
        super(BaseDecoder, self).__init__()
        # XXX: intentionally skip Params for now
        ffh = self._ff
        if isinstance(input_codec, str):
            name = input_codec.encode('utf-8')
            self._codec = ffh.lavc.avcodec_find_decoder_by_name(name)
        else:
            raise SetupError("not yet supported")
        self._ctx = ffh.lavc.avcodec_alloc_context3(self._codec)
        self._av_decode = _null_av_decode
        self._new_frame = _null_new_frame
        self._frames = []  # internal buffering
        self._repr = "Decoder(input_codec=%s)"
        self._mtype = "abstract"
        if not delay_open:
            self.open()

    def open(self, ffh=None):  # ffh parameter only for testing purposes.
        """
        opens the codec into the codec context.
        """
        if not self.ready:
            super(BaseDecoder, self).open(ffh)
        return self

    def _decode_pkt(self, pkt):
        """
        Fed a packet of data into decoder, and see if there is a decoded frame
        available. Decoder are complex beasts which must deal with all sort
        of compressed data, and the first line of defense is buffering.
        Often for legitimate purposes (unreliable media, e.g. broadcasting),
        an encoded stream can be split in many small packets, thus a decoder
        may need a lot of them to reconstruct a frame.
        This method deals with the [many packets -> one frame] scenario.
        However, reliable medias are quite common too, so it is not uncommon
        to have a relationship frames:packets close to one; and, most
        important, libavformat does some packing too.
        """
        with bind_frame(self._ff) as ppframe:
            ret = self._av_decode(self._ctx, ppframe[0], self._got_data, pkt)
            if ret < 0:
                msg = "Error decoding %s frame: %i" % (self._mtype, ret)
                raise ProcessingError(msg)

            if not self._got_data[0]:
                raise NeedFeedError()

            return ret, self._new_frame(ppframe)

    def decode_packet(self, packet):
        """
        Generator method.
        Decode a single packet (as in returned by a Demuxer) and extracts
        all the frames encoded into it.
        An encoded packet can legally contain more than one frame, altough
        this is not so common.
        This method deals with the [one packet -> many frames] scenario.
        The internal underlying decoder does its own buffer, so you can
        freely dispose the packet(s) fed into this method after it exited.
        raises ProcessingError if decoding fails;
        raises NeedFeedError if decoding partially succeeds, but more
        data is needed to reconstruct a full frame.
        """
        with packet.raw_pkt() as pkt:
            # careful here: you need of save the pointer state
            while pkt.size > 0:
                ret, frame = self._decode_pkt(pkt)
                yield frame
                pkt.data += ret
                pkt.size -= ret

    def decode(self, packets):
        """
        Decode data from a logical stream of packets, and returns when
        the first next frame is available.
        The input stream can be
        - a materialized sequence of packets (list, tuple...)
        - a generator (e.g. Demuxer.stream()).
        """
        fetch = make_fetcher(packets)
        while not self._frames:
            try:
                self._frames.extend(frm for frm in self.decode_packet(fetch()))
            except NeedFeedError:
                continue
            except StopIteration:
                raise EOSError
        return self._frames.pop(0)

    def flush(self):
        """
        emits all frames that can be recostructed by the data
        buffered into the Decoder, and empties such buffers.
        Call it last, do not intermix with decode*() calls.
        caution: more than one frame can be buffered.
        Raises NeedFeedError if all the internal buffers are empty.
        """
        with raw_packet(0) as cpkt:
            _, frame = self._decode_pkt(cpkt)
            return frame

    @classmethod
    def from_cdata(cls, ctx):
        """
        builds a pyrana Decoder from (around) a (cffi-wrapped) libav*
        decoder object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = ff.get_handle()
        dec = object.__new__(cls)
        CodecMixin.__init__(dec, {})  # MUST be explicit
        ctx.codec = ffh.lavc.avcodec_find_decoder(ctx.codec_id)
        setattr(dec, '_codec', ctx.codec)
        setattr(dec, '_ctx', ctx)
        setattr(dec, '_av_decode', _null_av_decode)
        setattr(dec, '_new_frame', _null_new_frame)
        setattr(dec, '_frames', [])  # internal buffering
        setattr(dec, '_got_data', None)
        setattr(dec, '_mtype', "abstract")
        setattr(dec, '_repr', "Decoder(input_codec=%s)")
        return dec.open()


class Payload(object):
    """
    Generic media-agnostic frame payload.
    """

    def __len__(self):
        raise NotImplementedError

    def blob(self):
        """
        returns the bytes() dump of the object.
        """
        raise NotImplementedError

    def __bytes__(self):
        return self.blob()

    def __getitem__(self, key):
        # a little ugliness for the sake of the coverage
        return self.blob()[key]

    def __str__(self):
        return repr(self) if PY3 else self.blob()
