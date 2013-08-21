#!/usr/bin/python

import pyrana.format
import io
import unittest


_B = b'\0' * 1024 * 64


class TestDemuxer(unittest.TestCase):
    def test_new_empty_just_init(self):
        f = io.BytesIO(_B)
        dmx = pyrana.format.Demuxer(f, delay_open=True)
        assert dmx

    def test_empty_streams_without_open(self):
        f = io.BytesIO(_B)
        dmx = pyrana.format.Demuxer(f, delay_open=True)
        assert not dmx.streams

    @unittest.expectedFailure
    def test_invalid_decoder_without_open(self):
        f = io.BytesIO(_B)
        dmx = pyrana.format.Demuxer(f, delay_open=True)
        dec = dmx.open_decoder(0)  # FIXME

    @unittest.expectedFailure
    def test_invalid_read_without_open(self):
        f = io.BytesIO(_B)
        dmx = pyrana.format.Demuxer(f, delay_open=True)
        frame = dmx.read_frame()
        assert not frame


if __name__ == "__main__":
    unittest.main()
