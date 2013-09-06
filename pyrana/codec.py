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

    maker = { MediaType.AVMEDIA_TYPE_VIDEO: vdec.from_cdata,
              MediaType.AVMEDIA_TYPE_AUDIO: adec.from_cdata }
    xdec = maker.get(ctx.codec_type, unsupported)
    return xdec(ctx)


class CodecMixin:
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

    @property
    def params(self):
        """
        dict, read-only
        """
        return frozendict(self._params)
    
    @property
    def extra_data(self):
        """
        bytearray, read-write
        """
        raise NotImplementedError


class BaseDecoder(CodecMixin):
    """
    Decoder base class. Common both to audio and video decoders.
    """
    def __init__(self, input_codec, params=None):
        super(BaseDecoder, self).__init__(params)
        ffh = self._ff
        if isinstance(input_codec, str):
            name = input_codec.encode('utf-8')
            self._codec = ffh.lavc.avcodec_find_decoder_by_name(name)
        else:
            raise pyrana.errors.SetupError("not yet supported")

    def __repr__(self):
        ffh = self._ff
        # how funny. If we use an array of chars like a string, it crashes.
        codec_id = self._codec.id if self._codec else self._ctx.codec_id
        cname = ffh.lavc.avcodec_get_name(codec_id)
        return "Decoder(input_codec=%s)" % (to_str(cname))

    @classmethod
    def from_cdata(cls, ctx):
        """
        builds a pyrana Decoder from (around) a (cffi-wrapped) libav*
        decoder object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        dec = object.__new__(cls)
        CodecMixin.__init__(dec, {})  # MUST be explicit
        dec._codec = ctx.codec
        dec._ctx = ctx
        return dec
