#!/usr/bin/python

import pyrana.formats
import unittest


_B = "a".encode('utf-8')


class TestFormatBuffer(unittest.TestCase):
    def test_new_empty(self):
        buf = pyrana.formats.Buffer()
        assert buf
        assert repr(buf)

    def test_empty_len(self):
        buf = pyrana.formats.Buffer()
        assert len(buf) == pyrana.formats.PKT_SIZE

    def test_custom_size(self):
        size = pyrana.formats.PKT_SIZE * 2
        buf = pyrana.formats.Buffer(size)
        assert buf.size == size

    def test_valid_data(self):
        buf = pyrana.formats.Buffer()
        assert buf.data

    def test_valid_cdata(self):
        buf = pyrana.formats.Buffer()
        assert buf.cdata


if __name__ == "__main__":
    unittest.main()
