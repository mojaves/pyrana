"""
this module provides the transport layer facilities.
(WRITEME)
"""

from enum import IntEnum

from pyrana.common import find_source_format
import pyrana.errors
import pyrana.ff


STREAM_ANY = -1
TS_NULL = 0x8000000000000000
PKT_SIZE = 4096


INPUT_FORMATS = frozenset()
OUTPUT_FORMATS = frozenset()


def is_streamable(name):
    """
    is_streamable(name) -> Bool
    tells if a given format is streamable (do NOT need seek()) or not.
    """
    return name in INPUT_FORMATS or name in OUTPUT_FORMATS  # TODO


def find_stream(streams, stream_id, media):
    """
    TODO
    """
    pass


# In the current incarnation, it could be happily replaced by a namedtuple.
# however, things are expected to change once Muxer get implemented.
class Packet:
    """
    a Packet object represents an immutable, encoded packet of a
    multimedia stream.
    """
    def __init__(self, stream_id, data,
                 pts=TS_NULL, dts=TS_NULL, is_key=False):
        self._ff = pyrana.ff.get_handle()
        self._stream_id = stream_id
        self._pts = pts
        self._dts = dts
        self._data = bytes(data)
        self._is_key = is_key

    def __len__(self):
        return len(self._data)

    def __bytes__(self):
        return self._data

    def __hash__(self):
        return hash(self._data)

    @property
    def stream_id(self):
        """
        the identifier of the logical stream which this packet belongs to.
        """
        return self._stream_id

    @property
    def pts(self):
        """
        the Presentation TimeStamp of this packet.
        """
        return self._pts

    @property
    def dts(self):
        """
        the Decoding TimeStamp of this packet.
        """
        return self._dts

    @property
    def data(self):
        """
        the raw data (bytes) this packet carries.
        """
        return self._data

    @property
    def is_key(self):
        """
        boolean flag. Is this packet a key frame?
        (provided by libav*)
        """
        return self._is_key

    @property
    def size(self):
        """
        Size of the packet data (bytes)
        """
        return len(self._data)


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


def _read(handle, buf, buf_size):
    """
    libavformat read callback. Actually: wrapper. Do not use directly.
    """
    ffh = pyrana.ff.get_handle()
    src = ffh.ffi.from_handle(handle)
    rbuf = ffh.ffi.buffer(buf, buf_size)
    src.readinto(rbuf)


def _write(handle, buf, buf_size):
    """
    libavformat write callback. Actually: wrapper. Do not use directly.
    """
    ffh = pyrana.ff.get_handle()
    dst = ffh.ffi.from_handle(handle)
    wbuf = ffh.ffi.buffer(buf, buf_size)
    dst.write(wbuf)


def _seek(handle, offset, whence):
    """
    libavformat seek callback. Actually: wrapper. Do not use directly.
    """
    ffh = pyrana.ff.get_handle()
    src = ffh.ffi.from_handle(handle)
    src.seek(offset, whence)


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
        self.avio = self._ff.ffi.NULL
        self._buf = Buffer(bufsize)
        self._src = src
        if not delay_open:
            self.open(seekable)

    def __del__(self):
        self.close()

    def open(self, seekable):
        """
        open (really: allocate) the underlying avio
        """
        ffi = self._ff.ffi
        read = ffi.callback("int(void *, uint8_t *, int)", _read)
        seek = ffi.NULL
        if seekable:
            seek = ffi.callback("int64_t(void *, int64_t, int)", _seek)
        self.avio = self._ff.lavf.avio_alloc_context(self._buf.cdata,
                                                     self._buf.size,
                                                     0,
                                                     ffi.new_handle(self._src),
                                                     read,
                                                     ffi.NULL,
                                                     seek)

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
        Initialize a new demuxer for the file type `name' (use "" (empty)
        for auto probing).
        A Demuxer needs a RawIOBase-compliant as a source of data.
        The RawIOBase-compliant object must be already open.
        """
        self._ff = pyrana.ff.get_handle()
        ffh = self._ff  # shortcut
        self._streams = []
        self._pctx = ffh.ffi.new('AVFormatContext **')  # FIXME explain
        self._src = IOSource(src)
        self._pctx[0] = ffh.lavf.avformat_alloc_context()
        self._pctx[0].pb = self._src.avio
        self._pctx[0].flags |= FormatFlags.AVFMT_FLAG_CUSTOM_IO
        if not delay_open:
            self.open(name)

    def open(self, name=None):
        """
        open the underlying demuxer.
        """
        filename = bytes()
        fmt = find_source_format(name)
        err = self._ff.lavf.avformat_open_input(self._pctx, filename,
                                                fmt, self._ff.ffi.NULL)
        if err:
            raise pyrana.errors.SetupError()

    def read_frame(self, stream_id=STREAM_ANY):
        """
        read_frame(stream_id=ANY) -> Packet Object
        reads and returns a new complete encoded frame (enclosed in a Packet)
        from the demuxer.
        if the optional `stream_id' argument is !ANY, returns a frame
        belonging to the specified streams.

        raises EndOfStreamError if
        - a stream id is specified, and such streams doesn't exists.
        - the streams ends.
        """
        raise NotImplementedError

    def open_decoder(self, stream_id, params=None):
        """
        open_decoder(stream_id) -> Decoder instance
        create and returns a full-blown decoder Instance capable
        to decode the selected stream.
        Like doing things manually, just easily.
        """
        params = {} if params is None else params
        raise NotImplementedError

    @property
    def streams(self):
        """
        streams: read-only attribute
        list of StreamInfo objects describing the streams found by the demuxer
        (as in old pyrana, no changes)
        """
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
