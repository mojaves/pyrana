#!/usr/bin/python

import random
import io
import unittest
import pyrana.format


_BLEN = 64 * 1024
_BZ = b'\0' * _BLEN


def _randgen(L, x=None):
    # FIXME: clumsy, rewrite
    cnt, num = 0, L
    rnd = random.Random(x)
    while cnt < L:
        yield (rnd.randint(0, 255),)
        cnt += 1


class TestFormatIOSource(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    def test_new_empty(self):
        f = io.BytesIO(_BZ)
        src = pyrana.format.IOSource(f)
        assert src
        assert repr(src)

    def test_new_empty_not_seekable(self):
        f = io.BytesIO(_BZ)
        src = pyrana.format.IOSource(f, seekable=False)
        assert src

    def test_new_empty_custom_size(self):
        f = io.BytesIO(_BZ)
        size = pyrana.format.PKT_SIZE * 4
        src = pyrana.format.IOSource(f, bufsize=size)
        assert src

    def test_read(self):
        ffh = pyrana.ff.get_handle()
        buf = pyrana.format.Buffer()
        f = io.BytesIO(_BZ)
        h = ffh.ffi.new_handle(f)
        pyrana.format._read(h, buf.cdata, buf.size)
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
#        buf = pyrana.format.Buffer(_BLEN)
#        for i, b in enumerate(_randgen(_BLEN)):
#            buf.data[i] = bytes(b)  # XXX whoa,
#                                    # that's almost too ugly to be true
#        f = io.BytesIO()
#        h = ffh.ffi.new_handle(f)
#        pyrana.format._write(h, buf.cdata, buf.size)
#        _x = f.getbuffer()
#        for i, b in enumerate(buf.data):
#            assert(b == bytes((_x[i],)))  # XXX you sure?

    def test_seek(self):
        ffh = pyrana.ff.get_handle()
        buf = pyrana.format.Buffer()
        f = io.BytesIO(_BZ)
        h = ffh.ffi.new_handle(f)
        pyrana.format._seek(h, 128, 0)
        self.assertEquals(f.tell(), 128)


if __name__ == "__main__":
    unittest.main()
