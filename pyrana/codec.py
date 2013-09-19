"""
Common code shared by audio and video codecs.
This module is not part of the pyrana public API.
"""

# of course I trust the stdlib. What else must I trust?!
# pylint: disable=E0611
from types import MappingProxyType as frozendict
# thanks to
# http://me.veekun.com/blog/2013/08/05/ \
#        frozendicthack-or-activestate-code-considered-harmful/

from pyrana.packet import raw_packet
from pyrana.common import MediaType, to_media_type, to_str
import pyrana.errors
import pyrana.ff


def decoder_for_stream(ctx, stream_id, vdec, adec):
    """
    builds the right decoder for a given stream (by id)
    of an AVCodecContext.
    """
    def unsupported(_):
        """
        adapter factory function of a stream type
        not supported by pyrana.
        """
        msg = "unsupported type %s for stream %i" \
              % (to_media_type(ctx.codec_type), stream_id)
        raise pyrana.errors.ProcessingError(msg)

    maker = {MediaType.AVMEDIA_TYPE_VIDEO: vdec.from_cdata,
             MediaType.AVMEDIA_TYPE_AUDIO: adec.from_cdata}
    xdec = maker.get(ctx.codec_type, unsupported)
    return xdec(ctx)


class CodecMixin(object):
    """
    Mixin. Abstracts the common codec attributes:
    parameters reference, read-only access, extradata
    management.
    """
    def __init__(self, params=None):
        params = {} if params is None else params
        self._ff = pyrana.ff.get_handle()
        self._params = params
        self._codec = None
        self._ctx = None
        self._xdata = None

    @property
    def params(self):
        """
        dict, read-only
        """
        return frozendict(self._params)

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
        self._ff = pyrana.ff.get_handle()
        self._ppframe = None
        self._frame = None

    def __del__(self):
        # FIXME: is really the data safely handled? check for memleaks.
        self._ff.lavc.avcodec_free_frame(self._ppframe)

    def __repr__(self):
        return "%sFrame(pts=%i)" % ("Key" if self.is_key else "", self.pts)

    def handle(self):
        """
        Returns a file-like which provides frame data access.
        """
        raise NotImplementedError

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

    @classmethod
    def from_cdata(cls, ppframe):
        """
        builds a pyrana generic Base Frame from (around) a (cffi-wrapped)
        libav* AVFrame object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = pyrana.ff.get_handle()
        frame = object.__new__(cls)
        frame._ff = ffh
        frame._ppframe = ppframe
        frame._frame = ppframe[0]
        return frame


def _null_av_decode(*args):
    """
    private use only. Placeholder callable for hooks
    in the BaseDecoder which MUST have to be replaced in the
    specific {Audio,Video,...} Decoders.
    """
    return -1


def _null_new_frame(*args):
    """
    private use only. Placeholder callable for hooks
    in the BaseDecoder which MUST have to be replaced in the
    specific {Audio,Video,...} Decoders.
    """
    raise pyrana.errors.ProcessingError("Generic decoders cannot run")


def _new_av_frame_pp(ffh):
    """
    allocates an indirect AVFrame reference
    needed by the constraint of the FFMpeg API.
    """
    ppframe = ffh.ffi.new('AVFrame **')
    ppframe[0] = ffh.lavc.avcodec_alloc_frame()
    return ppframe


class FrameBinder(object):
    """
    allocates an AVFrame and cleans it up on exception.
    FIXME: weakrefs?
    """
    def __init__(self, ffh):
        self._ff = ffh

    def __enter__(self):
        self._ppframe = _new_av_frame_pp(self._ff)
        return self._ppframe

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self._ff.lavc.avcodec_free_frame(self._ppframe)
            return False
        return True


class BaseDecoder(CodecMixin):
    """
    Decoder base class. Common both to audio and video decoders.
    """
    def __init__(self, input_codec, params=None, delay_open=False):
        super(BaseDecoder, self).__init__(params)
        ffh = self._ff
        if isinstance(input_codec, str):
            name = input_codec.encode('utf-8')
            self._codec = ffh.lavc.avcodec_find_decoder_by_name(name)
        else:
            raise pyrana.errors.SetupError("not yet supported")
        self._ctx = ffh.lavc.avcodec_alloc_context3(self._codec)
        self._av_decode = _null_av_decode
        self._new_frame = _null_new_frame
        self._got_frame = None
        self._mtype = "abstract"
        if not delay_open:
            self._open()

    def _open(self, ffh=None):  # ffh parameter only for testing purposes.
        """
        opens the codec into the codec context.
        """
        ffh = self._ff if ffh is None else ffh
        self._got_frame = ffh.ffi.new("int [1]")
        err = ffh.lavc.avcodec_open2(self._ctx, self._codec, ffh.ffi.NULL)
        if err < 0:
            raise pyrana.errors.SetupError("avcodec open failed: %i" % err)
        return self

    def __repr__(self):
        # how funny. If we use an array of chars like a string, it crashes.
        codec_id = self._codec.id  # if self._codec else self._ctx.codec_id
        cname = self._ff.lavc.avcodec_get_name(codec_id)
        return "Decoder(input_codec=%s)" % (to_str(cname))

    def _decode_pkt(self, pkt):
        """
        A packet can legally contain more than one frame.
        """
        with FrameBinder(self._ff) as ppframe:
            ret = self._av_decode(self._ctx, ppframe[0], self._got_frame, pkt)
            if ret < 0:
                msg = "Error decoding %s frame: %i" % (self._mtype, ret)
                raise pyrana.errors.ProcessingError(msg)

            if not self._got_frame[0]:
                raise pyrana.errors.NeedFeedError()

            return ret, self._new_frame(ppframe)

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
        return frames

    def flush(self):
        """
        flush() -> frame
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
        ffh = pyrana.ff.get_handle()
        dec = object.__new__(cls)
        CodecMixin.__init__(dec, {})  # MUST be explicit
        ctx.codec = ffh.lavc.avcodec_find_decoder(ctx.codec_id)
        dec._codec = ctx.codec
        dec._ctx = ctx
        dec._av_decode = _null_av_decode
        dec._new_frame = _null_new_frame
        dec._got_frame = None
        dec._mtype = "abstract"
        return dec._open()
