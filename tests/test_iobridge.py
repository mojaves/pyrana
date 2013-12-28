#!/usr/bin/python

import io
import sys
import random
import unittest
import pytest
import pyrana.iobridge


_BLEN = 64 * 1024
_BZ = b'\0' * _BLEN
_B = "a".encode('utf-8')


def _randgen(L, x=None):
    # FIXME: clumsy, rewrite
    cnt, num = 0, L
    rnd = random.Random(x)
    while cnt < L:
        yield (rnd.randint(0, 255),)
        cnt += 1


class TestBuffer(unittest.TestCase):
    def setUp(self):
        self._buf =pyrana.iobridge.Buffer()
        assert self._buf

    def test_new_empty(self):
        assert repr(self._buf)

    def test_empty_len(self):
        assert len(self._buf) == pyrana.iobridge.PKT_SIZE

    def test_custom_size(self):
        size = pyrana.iobridge.PKT_SIZE * 2
        buf = pyrana.iobridge.Buffer(size)
        assert buf.size == size

    def test_valid_data(self):
        assert self._buf.data

    def test_valid_cdata(self):
        assert self._buf.cdata

    def test_item_access(self):
        self._buf[0] = b'\0'
        assert self._buf[0] == b'\0'


class TestIOSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_new_empty(self):
        f = io.BytesIO(_BZ)
        src = pyrana.iobridge.IOSource(f)
        assert src
        assert repr(src)

    def test_new_empty_seekable(self):
        f = io.BytesIO(_BZ)
        src = pyrana.iobridge.IOSource(f)
        assert src.seekable

    def test_new_empty_not_seekable(self):
        f = io.BytesIO(_BZ)
        src = pyrana.iobridge.IOSource(f, seekable=False)
        assert not src.seekable

    def test_new_empty_not_seekable(self):
        f = io.BytesIO(_BZ)
        src = pyrana.iobridge.IOSource(f, seekable=False)
        assert src

    def test_new_empty_custom_size(self):
        f = io.BytesIO(_BZ)
        size = pyrana.iobridge.PKT_SIZE * 4
        src = pyrana.iobridge.IOSource(f, bufsize=size)
        assert src

    @pytest.mark.skipif(sys.version_info < (3,),
                       reason="requires python3")
    def test_read(self):
        ffh = pyrana.ff.get_handle()
        buf = pyrana.iobridge.Buffer()
        f = io.BytesIO(_BZ)
        h = ffh.ffi.new_handle(f)
        pyrana.iobridge._read(h, buf.cdata, buf.size)
        _x = f.getbuffer()
        try:
            _x = _x.cast('c')  # cpython >= 3.3
        except:
            # cpyhon 3.2: already returns bytes as items.
            pass
        for i, b in enumerate(buf.data):
            assert(b == _x[i])  # XXX sigh. I can barely stand this.

# not yet needed
#    def test_write(self):
#        ffh = pyrana.ff.get_handle()
#        buf = pyrana.iobridge.Buffer(_BLEN)
#        for i, b in enumerate(_randgen(_BLEN)):
#            buf.data[i] = bytes(b)  # XXX whoa,
#                                    # that's almost too ugly to be true
#        f = io.BytesIO()
#        h = ffh.ffi.new_handle(f)
#        pyrana.iobridge._write(h, buf.cdata, buf.size)
#        _x = f.getbuffer()
#        for i, b in enumerate(buf.data):
#            assert(b == bytes((_x[i],)))  # XXX you sure?

    def test_seek(self):
        ffh = pyrana.ff.get_handle()
        buf = pyrana.iobridge.Buffer()
        f = io.BytesIO(_BZ)
        h = ffh.ffi.new_handle(f)
        pyrana.iobridge._seek(h, 128, 0)
        self.assertEqual(f.tell(), 128)


if __name__ == "__main__":
    unittest.main()
