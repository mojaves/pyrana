"""
I/O glue code between Python and the FFMpeg libraries.
This module is not part of the pyrana public API.
"""

from .packet import PKT_SIZE
from .errors import UnsupportedError
from . import ff


class Buffer(object):
    """
    Wrapper class for a buffer properly aligned for
    optimal usage by ffmpeg libraries.
    """
    def __init__(self, size=PKT_SIZE):
        self._ff = ff.get_handle()
        self._size = size
        self._data = self._ff.lavu.av_malloc(size)

    def __del__(self):
        self._ff.lavu.av_free(self._data)

    def __len__(self):
        return self._size

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        raise UnsupportedError("cannot delete items from Buffers")

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


def _read(handle, buf, buf_size):
    """
    libavformat read callback. Actually: wrapper. Do not use directly.
    """
    ffh = ff.get_handle()
    src = ffh.ffi.from_handle(handle)
    rbuf = ffh.ffi.buffer(buf, buf_size)
    ret = src.readinto(rbuf)
    return ret if ret is not None else -1


def _write(handle, buf, buf_size):
    """
    libavformat write callback. Actually: wrapper. Do not use directly.
    """
    ffh = ff.get_handle()
    dst = ffh.ffi.from_handle(handle)
    wbuf = ffh.ffi.buffer(buf, buf_size)
    ret = dst.write(wbuf)
    return ret


AVSEEK_SIZE = 0x10000
AVSEEK_FORCE = 0x20000


def _seek(handle, offset, whence):
    """
    libavformat seek callback. Actually: wrapper. Do not use directly.
    """
    if whence == AVSEEK_SIZE:
        return -1  # unsupported, yet
    ffh = ff.get_handle()
    src = ffh.ffi.from_handle(handle)
    ret = src.seek(offset, whence)
    return ret


class IOBridge(object):
    """
    wraps the avio handling.
    A separate classe is advisable because
    1. you need to handle a Buffer for I/O and take good care of it.
    2. you need o propelry av_free the avio once done
    which is enough (it is?) to build a class.
    """
    def __init__(self, fh, readwrite=True, seekable=True,
                 bufsize=PKT_SIZE, delay_open=False):
        self._ff = ff.get_handle()
        ffi = self._ff.ffi
        self._rw = readwrite
        self._fh = fh
        self.avio = ffi.NULL
        self._buf = Buffer(bufsize)
        read = ffi.callback("int(void *, uint8_t *, int)", _read)
        write = ffi.callback("int(void *, uint8_t *, int)", _write)
        seek = ffi.NULL
        if seekable:
            seek = ffi.callback("int64_t(void *, int64_t, int)", _seek)
        self._refs = (read, write, seek)  # ensure the callbacks are ref'd
        if not delay_open:
            self.open()

    def __del__(self):
        self.close()

    def __repr__(self):
        return "IOBridge(src=None, seekable=%i)" % (self.seekable)

    def _alloc_buf(self, size):
        """
        allocates a slice of memory suitable for libav* usage.
        Why don't use a Buffer, you may ask.
        avio_alloc_context takes ownership of the given buffer,
        and dutifully free()s it on avio_close.
        So there is little sense to pack the lifetime handling
        in Buffer here.
        """
        self._ff = ff.get_handle()
        return self._ff.lavu.av_malloc(size)

    @property
    def seekable(self):
        """
        is this IOBridge seek-enabled?
        """
        return self._refs[-1] != self._ff.ffi.NULL  # XXX

    def open(self):
        """
        open (really: allocate) the underlying avio
        """
        ffi = self._ff.ffi
        read, write, seek = self._refs
        self.avio = self._ff.lavf.avio_alloc_context(self._alloc_buf(PKT_SIZE),
                                                     PKT_SIZE,
                                                     int(self._rw),
                                                     ffi.new_handle(self._fh),
                                                     read,
                                                     write,
                                                     seek)

    def close(self):
        """
        close (really: deallocate) the underlying avio
        """
        self._ff.lavu.av_free(self.avio)
        self.avio = self._ff.ffi.NULL


def _seekable(streamable):
    """
    is the stream seekable? The opposite of streamable.
    """
    return not streamable


def iosource(source, streaming, bufsize=PKT_SIZE, delay_open=False):
    """
    convenience function.
    builds an IOBridge suitable as source of data.
    """
    return IOBridge(source, readwrite=False, seekable=_seekable(streaming),
                    bufsize=bufsize, delay_open=delay_open)


def iosink(sink, streaming, bufsize=PKT_SIZE, delay_open=False):
    """
    convenience function.
    builds an IOBridge suitable as sink for data.
    """
    return IOBridge(sink, readwrite=True, seekable=_seekable(streaming),
                    bufsize=bufsize, delay_open=delay_open)
