#!/usr/bin/python

import pyrana.formats
import io
import unittest


_B = b'\0' * 1024 * 64


class TestMuxer(unittest.TestCase):
    def test_new_empty(self):
        f = io.BytesIO(_B)
        mux = pyrana.formats.Muxer(f, "avi")
        assert mux

    @unittest.expectedFailure
    def test_add_stream(self):
        f = io.BytesIO(_B)
        mux = pyrana.formats.Muxer(f, "avi")
        mux.add_stream(0, {})

    @unittest.expectedFailure
    def test_get_pts(self):
        f = io.BytesIO(_B)
        mux = pyrana.formats.Muxer(f, "avi")
#        mux.add_stream(0, {})  # FIXME
        assert(mux.get_pts(0) == 0)

    @unittest.expectedFailure
    def test_write_header(self):
        f = io.BytesIO(_B)
        mux = pyrana.formats.Muxer(f, "avi")  # XXX
        mux.write_header()

    @unittest.expectedFailure
    def test_write_trailer(self):
        f = io.BytesIO(_B)
        mux = pyrana.formats.Muxer(f, "avi")  # XXX
        mux.write_trailer()

    @unittest.expectedFailure
    def test_flush(self):
        f = io.BytesIO(_B)
        mux = pyrana.formats.Muxer(f, "avi")  # XXX
        mux.flush()

    @unittest.expectedFailure
    def test_write_frame(self):
        f = io.BytesIO(_B)
        mux = pyrana.formats.Muxer(f, "avi")  # XXX
#        mux.add_stream(0, {})  # FIXME
        pkt = pyrana.formats.Packet(0, b'0' * 128)
        mux.write_frame(pkt)


if __name__ == "__main__":
    unittest.main()
