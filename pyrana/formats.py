"""
This module provides the transport layer interface: encoded packets,
Muxer, Demuxers and their support code.
"""

from enum import IntEnum

from pyrana.common import MediaType, to_media_type
from pyrana.common import find_source_format
from pyrana.common import get_field_int
from pyrana.codec import decoder_for_stream
import pyrana.audio
import pyrana.video
import pyrana.errors
import pyrana.ff


STREAM_ANY = -1
# this save us a call to ffi.cast("int64_t", TS_NULL)
# in C, we have fixed size integers, overflows and overflow tricks.
# in Python, we have unlimited integers aka longs and transparent
# promotions. Sometimes the two things mismatch.
TS_NULL = -0x8000000000000000
PKT_SIZE = 4096


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


class Buffer:
    """
    Wrapper class for a buffer properly aligned for
    optimal usage by ffmpeg libraries.
    """
    def __init__(self, size=PKT_SIZE):
        self._ff = pyrana.ff.get_handle()
        self._size = size
        self._data = self._ff.lavu.av_malloc(size)

    def __del__(self):
        self._ff.lavu.av_free(self._data)

    def __len__(self):
        return self._size

    def __repr__(self):
        return "Buffer(%i)" % self._size

    @property
    def size(self):
        """
        size (bytes) of the buffer.
        BUG?: what about the padding?
        """
        return self._size

    @property
    def data(self):
        """
        return the payload data suitable for access by Python code.
        BUG?: what about mutability?
        """
        return self._ff.ffi.buffer(self._data, self._size)

    @property
    def cdata(self):
        """
        return the payload data suitable for access by C code,
        of course through cffi.
        """
        return self._data


# see avcodec for the meaning of flags
class PacketFlags(IntEnum):
    """
    wrapper for the (wannabe)enum of AVPktFlag
    in libavcodec/avcodec.h
    """
    AV_PKT_FLAG_KEY = 0x0001
    AV_PKT_FLAG_CORRUPT = 0x0002


def _alloc_pkt(ffh, pkt, size):
    """
    allocates a Packet suitable for libav* usage,
    of the desired size. Checks for errors and raises
    Exceptions accordingly.
    and that's the reason why we use a separate private
    function.
    """
    err = ffh.lavc.av_new_packet(pkt, size)
    if err < 0:
        raise pyrana.errors.ProcessingError("cannot allocate packet")
    return pkt


def _new_cpkt(ffh, size):
    """
    builds a new C(ffi) packet of the given size.
    """
    pkt = ffh.ffi.new('AVPacket *')
    return _alloc_pkt(ffh, pkt, size)


# In the current incarnation, it could be happily replaced by a namedtuple.
# however, things are expected to change once Muxer get implemented.
class Packet:
    """
    a Packet object represents an immutable, encoded packet of a
    multimedia stream.
    """
    def __init__(self, stream_id=None,
                 data=None, pts=TS_NULL, dts=TS_NULL, is_key=False):
        self._ff = pyrana.ff.get_handle()
        ffi = self._ff.ffi  # shortcut

        size = PKT_SIZE
        if data is not None:
            data = bytes(data)
            size = len(data)

        self._pkt = _new_cpkt(self._ff, size)

        if stream_id is not None:
            self._pkt.stream_index = stream_id
        self._pkt.pts = ffi.cast("int64_t", pts)
        self._pkt.dts = ffi.cast("int64_t", dts)
        if is_key:
            self._pkt.flags |= PacketFlags.AV_PKT_FLAG_KEY
        self._raw_data = ffi.buffer(self._pkt.data, self._pkt.size)
        if data is not None:
            self._raw_data[:size] = data  # FIXME

    @classmethod
    def from_cdata(cls, cpkt):
        """
        builds a pyrana Packet from (around) a (cffi-wrapped) libav*
        packet object.
        The libav object must be already initialized and ready to go.
        WARNING: raw access. Use with care.
        """
        ffh = pyrana.ff.get_handle()
        pkt = object.__new__(cls)
        pkt._ff = ffh
        pkt._pkt = cpkt
        pkt._raw_data = ffh.ffi.buffer(cpkt.data, cpkt.size)
        return pkt

    def __del__(self):
        self._ff.lavc.av_free_packet(self._pkt)

    def __repr__(self):
        return "Packet(stream_id=%i, size=%i, " \
               "pts=%i, dts=%i, is_key=%i)" \
               % (self.stream_id, self.size, self.pts,
                  self.dts, self.is_key)

    def __len__(self):
        return self.size

    def __bytes__(self):
        return bytes(self.data)

    def __eq__(self, other):
        return self.data == other.data

    def __hash__(self):
        return hash(self.data)

    @property
    def size(self):
        """
        Size of the packet data (bytes)
        """
        return self._pkt.size

    @property
    def data(self):
        """
        the raw data (bytes) this packet carries.
        """
        return self._raw_data[:self.size]

    @property
    def stream_id(self):
        """
        the identifier of the logical stream which this packet belongs to.
        """
        return self._pkt.stream_index

    @property
    def pts(self):
        """
        the Presentation TimeStamp of this packet.
        """
        return self._pkt.pts

    @property
    def dts(self):
        """
        the Decoding TimeStamp of this packet.
        """
        return self._pkt.dts

    @property
    def is_key(self):
        """
        boolean flag. Is this packet a key frame?
        (provided by libav*)
        """
        return bool(self._pkt.flags & PacketFlags.AV_PKT_FLAG_KEY)


def _read(handle, buf, buf_size):
    """
    libavformat read callback. Actually: wrapper. Do not use directly.
    """
    ffh = pyrana.ff.get_handle()
    src = ffh.ffi.from_handle(handle)
    rbuf = ffh.ffi.buffer(buf, buf_size)
    ret = src.readinto(rbuf)
    return ret if ret is not None else -1


# not yet needed
#def _write(handle, buf, buf_size):
#    """
#    libavformat write callback. Actually: wrapper. Do not use directly.
#    """
#    ffh = pyrana.ff.get_handle()
#    dst = ffh.ffi.from_handle(handle)
#    wbuf = ffh.ffi.buffer(buf, buf_size)
#    dst.write(wbuf)


def _seek(handle, offset, whence):
    """
    libavformat seek callback. Actually: wrapper. Do not use directly.
    """
    ffh = pyrana.ff.get_handle()
    src = ffh.ffi.from_handle(handle)
    ret = src.seek(offset, whence)
    return ret


class IOSource:
    """
    wraps the avio handling.
    A separate classe is advisable because
    1. you need to handle a Buffer for I/O and take good care of it.
    2. you need o propelry av_free the avio once done
    which is enough (it is?) to build a class.
    """
    def __init__(self, src, seekable=True, bufsize=PKT_SIZE, delay_open=False):
        self._ff = pyrana.ff.get_handle()
        ffi = self._ff.ffi
        self.avio = ffi.NULL
        self._buf = Buffer(bufsize)
        self._src = src
        self._read = ffi.callback("int(void *, uint8_t *, int)", _read)
        self._seek = ffi.NULL
        if seekable:
            self.seek = ffi.callback("int64_t(void *, int64_t, int)", _seek)
        if not delay_open:
            self.open()

    def __del__(self):
        self.close()

    def __repr__(self):
        seekable = self._seek != self._ff.ffi.NULL
        return "IOSource(src=None, seekable=%i)" % (seekable)

    def _alloc_buf(self, size):
        """
        allocates a slice of memory suitable for libav* usage.
        Why don't use a Buffer, you may ask.
        avio_alloc_context takes ownership of the given buffer,
        and dutifully free()s it on avio_close.
        So there is little sense to pack the lifetime handling
        in Buffer here.
        """
        self._ff = pyrana.ff.get_handle()
        return self._ff.lavu.av_malloc(size)

    def open(self):
        """
        open (really: allocate) the underlying avio
        """
        ffi = self._ff.ffi
        self.avio = self._ff.lavf.avio_alloc_context(self._alloc_buf(PKT_SIZE),
                                                     PKT_SIZE,
                                                     0,
                                                     ffi.new_handle(self._src),
                                                     self._read,
                                                     ffi.NULL,
                                                     self._seek)

    def close(self):
        """
        close (really: deallocate) the underlying avio
        """
        self._ff.lavu.av_free(self.avio)
        self.avio = self._ff.ffi.NULL


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


def _audio_stream_info(ctx):
    """
    extract the audio stream info from an AVCodecContext (ctx)
    """
    return {
        "sample_rate": get_field_int(ctx, "ar"),
        "channels": get_field_int(ctx, "ac"),
        "sample_bytes": 2  # FIXME: BPP is hardcoded
    }


def _video_stream_info(ctx):
    """
    extract the video stream info from an AVCodecContext (ctx)
    """
    return {
        "width": 0,  # FIXME
        "height": 0  # FIXME
    }


def _read_frame(ffh, ctx, new_pkt, stream_id):
    """
    frame pulling function, made separate and private
    for easier testing. Returns the first valid packet.
    You should not use this directly; use a Demuxer instead.
    """
    pkt = new_pkt(ffh, PKT_SIZE)
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
    return Packet.from_cdata(pkt)


class Demuxer:
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
        return self.stream()

    def close(self):
        """
        close the underlying demuxer. TODO: check for leaks.
        """
#        if self._pctx != self._ff.ffi.NULL:
#            self._ff.lavf.avformat_close_input(self._pctx)

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

    def flush(self):
        """
        returns any Packet buffered by Demuxer, if any.
        """
        # FIXME
        raise pyrana.errors.EOSError("No Packets buffered")

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
            info.update(_audio_stream_info(ctx))
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
        try:
            while True:
                pkt = self.read_frame(sid)
                yield pkt
        except pyrana.errors.EOSError:
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


class Muxer:
    """
    Muxer object. Use a file-like for real I/O.
    The file-like must be already open, and must support write()
    dealing with bytes (not strings).
    If the file format is_seekable but the file-like doesn't support
    seek, expect weird things.
    """
    def __init__(self, dst, name):
        """
        Muxer(dst, name="")
        Initialize a new muxer for the file type `name'
        A Muxer needs a RawIOBase-compliant as a sink of data.
        The RawIOBase-compliant object must be already open.
        """
        pass

    def add_stream(self, stream_id, params=None):
        """
        setup the muxer to handle the given stream.
        The stream will be bound to the logical id `stream_id'.
        pass a `params' dict to fill the detail of
        the new stream.
        """
        params = {} if params is None else params
        raise NotImplementedError

    def write_header(self):
        """
        write the stream header on media.
        """
        raise NotImplementedError

    def write_trailer(self):
        """
        write the stream trailer on media.
        """
        raise NotImplementedError

    def write_frame(self, packet):
        """
        requires an encoded frame enclosed in a Packet!
        """
        raise NotImplementedError

    def get_pts(self, stream_id):
        """
        returns the last PTS written for the given stream.
        """
        raise NotImplementedError

    def flush(self):
        """
        immediately writes ay buffered data on the
        underlying file(-like).
        Blocking.
        """
        raise NotImplementedError
