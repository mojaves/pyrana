#!/usr/bin/python

import pyrana.format
import io
import unittest


_BZ = b'\0' * 1024 * 64


class TestFormatIOSource(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    def test_new_empty(self):
        f = io.BytesIO(_BZ)
        src = pyrana.format.IOSource(f)
        assert src

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
        for b in buf.data:
            assert(b == b'\x00')


if __name__ == "__main__":
    unittest.main()
