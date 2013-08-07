"""
this module provides the transport layer facilities.
(WRITEME)
"""

import pyrana.errors
import pyrana.ff


STREAM_ANY = -1
TS_NULL = 0x8000000000000000
PKT_SIZE = 4096


INPUT_FORMATS = frozenset()
OUTPUT_FORMATS = frozenset()


def _iter_fmts(ffi, format_next):
    """
    generator. Produces the names as strings
    of all the format supported by libavformat.
    """
    fmt = format_next(ffi.NULL)
    while fmt != ffi.NULL:
        name = ffi.string(fmt.name)
        yield name.decode('utf-8'), fmt
        fmt = format_next(fmt)
    raise StopIteration


def _formats(ff):
    """
    builds the sets of the formats supported by
    libavformat, and which, in turn, by pyrana.
    """
    next_in = ff.lavf.av_iformat_next
    next_out = ff.lavf.av_oformat_next
    return ([x for x, _ in _iter_fmts(ff.ffi, next_in)],
            [x for x, _ in _iter_fmts(ff.ffi, next_out)])


def _find_fmt_by_name(name, next_fmt):
    ff = pyrana.ff.FF()
    for fname, fdesc in _iter_fmts(ff.ffi, next_fmt):
        if name == fname:
            return fdesc
    raise pyrana.errors.UnsupportedError
    


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


class Packet:
    """
    a Packet object represents an immutable, encoded packet of a
    multimedia stream.
    """
    def __init__(self, stream_id, data,
                 pts=TS_NULL, dts=TS_NULL, is_key=False):
        self._ff = pyrana.ff.FF()
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
        boolean flag. Is this packe a key frame?
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
    def __init__(self, size=PKT_SIZE):
        self._ff = pyrana.ff.FF()
        self._size = size
        self._data = self._ff.lavu.av_malloc(size)
    def __del__(self):
        self._ff.lavu.av_free(self._buf)
    def __len__(self):
        return self._size
    @property
    def data(self):
        return self._ff.ffi.buffer(self._data)
    @property
    def cdata(self):
        return self._data


def _read(handle, buf, buf_size):
    ff = pyrana.ff.FF()
    src = ff.ffi.from_handle(handle)
    rbuf = ff.ffi.buffer(buf, buf_size)
    src.readinto(rbuf)


def _write(handle, buf, buf_size):
    ff = pyrana.ff.FF()
    dst = ff.ffi.from_handle(handle)
    wbuf = ff.ffi.buffer(buf, buf_size)
    dst.write(rbuf)


def _seek(handle, offset, whence):
    ff = pyrana.ff.FF()
    src = ff.ffi.from_handle(handle)
    src.seek(offset, whence)


class IOSource:
    def __init__(self, src, seekable=True, bufsize=PKT_SIZE):
        self.avio = None
        self._ff = pyrana.ff.FF()
        self._buf = Buffer(bufsize)
        self._src = src
        self._open(src, seekable)

    def __del__(self):
        self._close()

    def _open(self, src, seekable):
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

    def _close(self):
        self._ff.lavu.av_free(self.avio)                


class Demuxer:
    def __init__(self, src, name=None):
        """
        Demuxer(src, name="")
        Initialize a new demuxer for the file type `name' (use "" (empty)
        for auto probing).
        A Demuxer needs a RawIOBase-compliant as a source of data.
        The RawIOBase-compliant object must be already open.
        """
        self._ff = pyrana.ff.FF()
        avf = self._ff.lavf  # shortcut
        ffi = self._ff.ffi   # shortcut
        fmt = ffi.NULL
        if name is not None:
            fmt = _find_fmt_by_name(name, avf.av_iformat_next)
        self._src = IOSource(src)
        self._ctx = avf.avformat_alloc_context()
        self._ctx.pb = self._src.avio
        err = avf.avformat_open_input(ffi.addressof(self._ctx),
                                      "",
                                      fmt,
                                      ffi.NULL)
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
        return []


class Muxer:
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
        pass
