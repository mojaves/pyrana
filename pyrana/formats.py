"""
This module provides the transport layer interface: encoded packets,
Muxer, Demuxers and their support code.
"""

from enum import IntEnum

from pyrana.common import MediaType, to_media_type
from pyrana.common import find_source_format, get_field_int
from pyrana.iobridge import IOSource
from pyrana.packet import Packet, _new_cpkt
from pyrana.codec import decoder_for_stream
import pyrana.audio  # see #1 below
import pyrana.video  # see #1 below
import pyrana.errors
import pyrana.ff

# #1 those are upside down dependencies which needs to be removed.
# From a layering standpoint, Demuxer/Muxer/Packets are at a lowe
# level wrt Decoder/Encoder/Frames.
# thus, this module is a lower level one and it is not good (tm)
# to have lower-level modules depending on higher ones.
# A bit more formally, those are upside arrows in the dependency
# graphs. We're just one step away from a cycle in the dependency
# graph aka cyclic import, and that is not good.
# the proper fix would probably be something like moving
# decoder_for_stream and friends in a separate module.

# meh
# pylint: disable=R0921

STREAM_ANY = -1


INPUT_FORMATS = frozenset()
OUTPUT_FORMATS = frozenset()


def is_streamable(name):
    """
    tells if a given format is streamable (do NOT need seek()) or not.
    """
    return name in INPUT_FORMATS or name in OUTPUT_FORMATS  # TODO


def find_stream(streams, nth, media):
    """
    find the nth stream of the specified media a streams info
    (as in Demuxer().streams).
    Return the corresponding stream_id.
    Raise NotFoundError otherwise.
    """
    try:
        cnt = 0
        for sid, stream in enumerate(streams):
            if stream["type"] == media:
                if cnt == nth:
                    return sid
                cnt += 1
        msg = "mismatching media types for stream"
    except KeyError:
        msg = "malformed stream #%i" % sid
    raise pyrana.errors.NotFoundError(msg)


# see avformat for the meaning of the flags
class FormatFlags(IntEnum):
    """
    wrapper for the (wannabe)enum of AVFormatFlags
    in libavformat/avformat.h
    """
    AVFMT_FLAG_GENPTS = 0x0001
    AVFMT_FLAG_IGNIDX = 0x0002
    AVFMT_FLAG_NONBLOCK = 0x0004
    AVFMT_FLAG_IGNDTS = 0x0008
    AVFMT_FLAG_NOFILLIN = 0x0010
    AVFMT_FLAG_NOPARSE = 0x0020
    AVFMT_FLAG_NOBUFFER = 0x0040
    AVFMT_FLAG_CUSTOM_IO = 0x0080
    AVFMT_FLAG_DISCARD_CORRUPT = 0x0100
    AVFMT_FLAG_MP4A_LATM = 0x8000
    AVFMT_FLAG_SORT_DTS = 0x10000
    AVFMT_FLAG_PRIV_OPT = 0x20000
    AVFMT_FLAG_KEEP_SIDE_DATA = 0x40000


def _codec_name(ffh, codec_id):
    """
    grabs the codec name from a codec ID.
    the FFMpeg API requires a (trivial) bit of machinery.
    """
    avcodec = ffh.lavc.avcodec_find_decoder(codec_id)
    return ffh.ffi.string(avcodec.name).decode('utf-8')


def _audio_stream_info(ctx, ffh):
    """
    extract the audio stream info from an AVCodecContext (ctx)
    """
    return {
        "sample_rate": get_field_int(ctx, "ar"),
        "channels": get_field_int(ctx, "ac"),
        "sample_bytes": ffh.lavu.av_get_bytes_per_sample(ctx.sample_fmt)
    }


def _video_stream_info(ctx):
    """
    extract the video stream info from an AVCodecContext (ctx)
    """
    return {
        "width": ctx.width,
        "height": ctx.height
    }


def _read_frame(ffh, ctx, new_pkt, stream_id):
    """
    frame pulling function, made separate and private
    for easier testing. Returns the first valid packet.
    You should not use this directly; use a Demuxer instead.
    """
    pkt = new_pkt(ffh, 0)
    av_read_frame = ffh.lavf.av_read_frame  # shortcut to speedup
    while True:
        err = av_read_frame(ctx, pkt)
        if err < 0:
            if ffh.lavf.url_feof(ctx.pb):
                raise pyrana.errors.EOSError()
            else:
                msg = "error while reading data: %i" % err
                raise pyrana.errors.ProcessingError(msg)
        if stream_id == STREAM_ANY or pkt.stream_index == stream_id:
            break
        ffh.lavc.av_free_packet(pkt)
    return Packet.from_cdata(pkt)


class Demuxer(object):
    """
    Demuxer object. Use a file-like for real I/O.
    The file-like must be already open, and must support read()
    returning bytes (not strings).
    If the file format is_seekable but the file-like doesn't support
    seek, expect weird things.
    """
    def __init__(self, src, name=None, delay_open=False):
        """
        Demuxer(src, name="")
        Initialize a new demuxer for the file type `name';
        Use "" (empty) for auto probing.
        A Demuxer needs a RawIOBase-compliant as a source of data.
        The RawIOBase-compliant object must be already open.
        """
        self._ff = pyrana.ff.get_handle()
        ffh = self._ff  # shortcut
        self._streams = []
        self._pctx = ffh.ffi.new('AVFormatContext **')
        # cffi purposefully doesn't have an address-of (C's &) operator.
        # but libavformat requires a pointer-to-pointer as context argument,
        # so we need to allocate a simple lone double pointer
        # to act as junction.
        self._src = IOSource(src)
        self._pctx[0] = ffh.lavf.avformat_alloc_context()
        self._pctx[0].pb = self._src.avio
        self._pctx[0].flags |= FormatFlags.AVFMT_FLAG_CUSTOM_IO
        self._ready = False
        if not delay_open:
            self.open(name)

    def __del__(self):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.read_frame()
        except pyrana.errors.EOSError:
            pass
        raise StopIteration

    def close(self):
        """
        close the underlying demuxer.
        """
        if self._pctx[0] != self._ff.ffi.NULL:
            self._ff.lavf.avformat_close_input(self._pctx)

    def open(self, name=None):
        """
        open the underlying demuxer.
        """
        ffh = self._ff
        filename = bytes()
        fmt = find_source_format(name)
        err = ffh.lavf.avformat_open_input(self._pctx, filename,
                                           fmt, ffh.ffi.NULL)
        if err < 0:
            raise pyrana.errors.SetupError("open error=%i" % err)
        ffh.lavf.avformat_find_stream_info(self._pctx[0], ffh.ffi.NULL)
        # as first attempt we want to be optimist and we choose
        # to ignore any errors here, deemed as not critical
        self._ready = True

    def seek_frame(self, stream_id, frameno):
        """
        seek to the given frame number in the stream.
        """
        raise NotImplementedError

    def seek_ts(self, stream_id, tstamp):
        """
        seek to the given timestamp (msecs) in the stream.
        """
        raise NotImplementedError

    def read_frame(self, stream_id=STREAM_ANY):
        """
        reads and returns a new complete encoded frame (enclosed in a Packet)
        from the demuxer.
        if the optional `stream_id' argument is !ANY, returns a frame
        belonging to the specified streams.

        raises EndOfStreamError if
        - a stream id is specified, and such streams doesn't exists.
        - the streams ends.
        """
        if not self._ready:
            raise pyrana.errors.ProcessingError("stream not yet open")

        return _read_frame(self._ff, self._pctx[0], _new_cpkt, stream_id)

    def open_decoder(self, stream_id):
        """
        open_decoder(stream_id) -> Decoder instance
        create and returns a full-blown decoder Instance capable
        to decode the selected stream.
        Like doing things manually, just easily.
        """
        if not self._ready:
            raise pyrana.errors.ProcessingError("media not yet open")

        nstreams = len(self.streams)
        if stream_id < 0 or stream_id > nstreams:
            msg = "invalid stream id not in [0,%i]" % nstreams
            raise pyrana.errors.ProcessingError(msg)

        ctx = self._pctx[0].streams[stream_id].codec
        return decoder_for_stream(ctx, stream_id,
                                  pyrana.video.Decoder,
                                  pyrana.audio.Decoder)

    def _stream_info(self, stream):
        """
        extract the stream info from an AVStream.
        FIXME: switch to namedtuple. This will break our API,
        but someone actually cares at this stage?
        """
        ffh = self._ff  # shortcut
        ctx = stream.codec
        _type = to_media_type(ctx.codec_type)
        info = {
            "id": stream.id,
            "index": stream.index,
            "type": _type,
            "name": _codec_name(ffh, ctx.codec_id),
            "bit_rate": get_field_int(ctx, "b")
        }
        if _type == MediaType.AVMEDIA_TYPE_AUDIO:
            info.update(_audio_stream_info(ctx, ffh))
        if _type == MediaType.AVMEDIA_TYPE_VIDEO:
            info.update(_video_stream_info(ctx))
        return info

    def _parse_streams(self):
        """
        convert the stream informations found in an AVFormatContext
        in the API-compliant, more pythonic, friendlier version.
        """
        streams = []
        for idx in range(self._pctx[0].nb_streams):
            streams.append(self._stream_info(self._pctx[0].streams[idx]))
        return tuple(streams)

    def stream(self, sid=STREAM_ANY):
        """
        generator that returns all packets that belong to a
        specified stream id.
        """
        while True:
            try:
                yield self.read_frame(sid)
            except pyrana.errors.EOSError:
                break
        raise StopIteration

    @property
    def streams(self):
        """
        streams: read-only attribute
        list of StreamInfo objects describing the streams found by
        the demuxer (as in old pyrana, no changes)
        """
        if not self._streams:
            self._streams = self._parse_streams()
            if not self._streams:
                raise pyrana.errors.ProcessingError("no streams found")
        return self._streams
