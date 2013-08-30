#!/usr/bin/python

import pyrana.format
import unittest


_B = "a".encode('utf-8')


class TestFormatBuffer(unittest.TestCase):
    def test_new_empty(self):
        buf = pyrana.format.Buffer()
        assert buf
        assert repr(buf)

    def test_empty_len(self):
        buf = pyrana.format.Buffer()
        assert len(buf) == pyrana.format.PKT_SIZE

    def test_custom_size(self):
        size = pyrana.format.PKT_SIZE * 2
        buf = pyrana.format.Buffer(size)
        assert buf.size == size

    def test_valid_data(self):
        buf = pyrana.format.Buffer()
        assert buf.data

    def test_valid_cdata(self):
        buf = pyrana.format.Buffer()
        assert buf.cdata


if __name__ == "__main__":
    unittest.main()
