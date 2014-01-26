"""
This module provides the transport layer interface: encoded packets,
Muxer, Demuxers and their support code.
"""

import warnings
from collections import OrderedDict
from enum import IntEnum

from .common import MediaType, to_media_type, AttrDict
from .common import find_source_format, get_field_int, strerror
from .iobridge import IOSource
from .packet import Packet, _new_cpkt
from .codec import decoder_for_stream
from . import audio  # see #1 below
from . import video  # see #1 below
from . import ff, errors

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
# we don't need to have values equals to C's INT64_MIN/INT64_MAX.
# the following values are close/good enough.
_TS_MIN = -9223372036854775807
_TS_MAX = +9223372036854775807

TIME_BASE = 1000000  # aka AV_TIME_BASE

INPUT_FORMATS = frozenset()
OUTPUT_FORMATS = frozenset()


def find_stream(streams, nth, media):
    """
    find the nth stream of the specified media a streams info
    (as in Demuxer().streams).
    Return the corresponding stream_id.
    Raise NotFoundError otherwise.
    """
    cnt = 0
    for sid, stream in enumerate(streams):
        if stream.media_type == media:
            if cnt == nth:
                return sid
            cnt += 1
    msg = "mismatching media types for stream"
    raise errors.NotFoundError(msg)


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


# see avformat for the meaning of the flags
class SeekFlags(IntEnum):
    """
    wrapper for the (wannabe)enum of AVSeekFlags
    in libavformat/avformat.h
    """
    AVSEEK_FLAG_BACKWARD = 1
    AVSEEK_FLAG_BYTE = 2
    AVSEEK_FLAG_ANY = 4
    AVSEEK_FLAG_FRAME = 8


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
    get_bps = ffh.lavu.av_get_bytes_per_sample  # shortcut
    return OrderedDict((
                        ("sample_rate", get_field_int(ctx, "ar")),
                        ("channels", get_field_int(ctx, "ac")),
                        ("sample_bytes", get_bps(ctx.sample_fmt))
                        ))


def _video_stream_info(ctx):
    """
    extract the video stream info from an AVCodecContext (ctx)
    """
    return OrderedDict((
                        ("width", ctx.width),
                        ("height", ctx.height)
                        ))


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
                raise errors.EOSError()
            else:
                msg = "error while reading data: %i" % err
                raise errors.ProcessingError(msg)
        if stream_id == STREAM_ANY or pkt.stream_index == stream_id:
            break
        ffh.lavc.av_free_packet(pkt)
    return Packet.from_cdata(pkt)


def _tb_to_str(timebase):
    """
    format a time base rational to a string, only for human consumption.
    """
    try:
        return "%.5f" % (timebase.num / float(timebase.den))
    except ZeroDivisionError:
        return "N/A"


AV_TIME_BASE = 1000000


def _time_base_q(ffh):
    """
    Builds an AV_TIME_BASE_Q equivalent
    """
    tb_q = ffh.ffi.new('AVRational *')
    tb_q.num = 1
    tb_q.den = AV_TIME_BASE
    return tb_q


class Demuxer(object):
    """
    Demuxer object. Use a file-like for real I/O.
    The file-like must be already open, and must support read()
    returning bytes (not strings).
    If the file format is_seekable but the file-like doesn't support
    seek, expect weird things.
    """
    def _ensure_ready(self):
        """
        ensures the Demuxer is ready to roll.
        """
        if not self._ready:
            raise errors.ProcessingError("media not yet open")

    def _ensure_stream_id(self, stream_id):
        """
        ensures the given stream_id is valid, and the demuxer is ready.
        """
        nstreams = len(self.streams)
        if stream_id < 0 or stream_id > nstreams:
            msg = "invalid stream id not in [0,%i]" % nstreams
            raise errors.ProcessingError(msg)

    def __init__(self, src, name=None, delay_open=False, streaming=False):
        """
        Demuxer(src, name="")
        Initialize a new demuxer for the file type `name';
        Use "" (empty) for auto probing.
        A Demuxer needs a RawIOBase-compliant as a source of data.
        The RawIOBase-compliant object must be already open.
        """
        self._ff = ff.get_handle()
        ffh = self._ff  # shortcut
        self._streams = []
        self._pctx = ffh.ffi.new('AVFormatContext **')
        # cffi purposefully doesn't have an address-of (C's &) operator.
        # but libavformat requires a pointer-to-pointer as context argument,
        # so we need to allocate a simple lone double pointer
        # to act as junction.
        self._tb_q = _time_base_q(ffh)
        seekable = False if streaming is True else True
        self._src = IOSource(src, seekable)
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
        except errors.EOSError:
            pass
        raise StopIteration

    def next(self):
        """python 2.x iterator hook."""
        return self.__next__()

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
            raise errors.SetupError("open error=%i" % err)
        ffh.lavf.avformat_find_stream_info(self._pctx[0], ffh.ffi.NULL)
        # as first attempt we want to be optimist and we choose
        # to ignore any errors here, deemed as not critical
        self._ready = True
        for s in self.streams:
            print(s)

    def seek_frame(self, frameno, stream_id=STREAM_ANY):
        """
        seek to the given frame number in the stream.
        """
        self._ensure_ready()
        if stream_id != STREAM_ANY:
            self._ensure_stream_id(stream_id)
            warnings.warn("seek interface is still experimental."\
                          "Likely broken if stream_id != STREAM_ANY",
                          RuntimeWarning)
        raise NotImplementedError

    def seek_ts(self, tstamp, stream_id=STREAM_ANY):
        """
        seek to the given timestamp (msecs) in the stream.
        """
        ffh = self._ff
        self._ensure_ready()
        if stream_id == STREAM_ANY:
            tstamp = int(tstamp / float(AV_TIME_BASE))
        else:
            self._ensure_stream_id(stream_id)
            warnings.warn("seek interface is still experimental."\
                          "Likely broken if stream_id != STREAM_ANY",
                          RuntimeWarning)
            stream_tb = self._pctx[0].streams[stream_id].time_base
            tstamp = ffh.lavu.av_rescale_q(tstamp,
                                           self._tb_q[0], stream_tb)
        err = ffh.lavf.avformat_seek_file(self._pctx[0], stream_id,
                                          _TS_MIN, tstamp, _TS_MAX,
                                          SeekFlags.AVSEEK_FLAG_ANY)
        if err < 0:
            msg = "seek to time %i failed (error=%s)" \
                  % (tstamp, strerror(err))
            raise errors.ProcessingError(msg)

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
        self._ensure_ready()
        if stream_id != STREAM_ANY:
            self._ensure_stream_id(stream_id)
        return _read_frame(self._ff, self._pctx[0], _new_cpkt, stream_id)

    def open_decoder(self, stream_id):
        """
        open_decoder(stream_id) -> Decoder instance
        create and returns a full-blown decoder Instance capable
        to decode the selected stream.
        Like doing things manually, just easily.
        """
        self._ensure_ready()
        self._ensure_stream_id(stream_id)  # STREAM_ANY is not valid here
        ctx = self._pctx[0].streams[stream_id].codec
        return decoder_for_stream(ctx, stream_id,
                                  video.Decoder,
                                  audio.Decoder)

    def _stream_info(self, stream):
        """
        extract the stream info from an AVStream.
        exports it as fake, read-only, dot-accessible objects.
        """
        ffh = self._ff  # shortcut
        ctx = stream.codec
        _type = to_media_type(ctx.codec_type)
        info = OrderedDict((
                           ("id", stream.id),
                           ("index", stream.index),
                           ("media_type", _type),
                           ("name", _codec_name(ffh, ctx.codec_id)),
                           ("bit_rate", get_field_int(ctx, "b")),
                           ("time_base", _tb_to_str(ctx.time_base)),
                           ))
        name = 'StreamInfo'
        if _type == MediaType.AVMEDIA_TYPE_AUDIO:
            info.update(_audio_stream_info(ctx, ffh))
            name = 'AudioInfo'
        if _type == MediaType.AVMEDIA_TYPE_VIDEO:
            info.update(_video_stream_info(ctx))
            name = 'VideoInfo'
        return AttrDict(name, info)

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
            except errors.EOSError:
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
                raise errors.ProcessingError("no streams found")
        return self._streams
