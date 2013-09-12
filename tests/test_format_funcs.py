#!/usr/bin/python

import unittest
import pyrana.formats
import pyrana.packet
import pyrana.errors
from pyrana.common import MediaType


class TestFormatFuncs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_is_streamable_any_input(self):
        self.assertTrue(any(map(pyrana.formats.is_streamable,
                                pyrana.formats.INPUT_FORMATS)))

    def test_is_streamable_any_output(self):
        self.assertTrue(any(map(pyrana.formats.is_streamable,
                                pyrana.formats.OUTPUT_FORMATS)))

    def test_find_stream_empty(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            pyrana.formats.find_stream((), 0, MediaType.AVMEDIA_TYPE_UNKNOWN)

    def test_find_stream_empty2(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            pyrana.formats.find_stream(({}, ), 0,
                                      MediaType.AVMEDIA_TYPE_UNKNOWN)

    def test_find_stream_empty3(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            st = { "type": MediaType.AVMEDIA_TYPE_VIDEO }
            pyrana.formats.find_stream((st, {}, ), 1,
                                      MediaType.AVMEDIA_TYPE_VIDEO)

    def test_find_stream_fake_bad(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            st = { "type": MediaType.AVMEDIA_TYPE_VIDEO }
            pyrana.formats.find_stream((st,), 0,
                                      MediaType.AVMEDIA_TYPE_AUDIO)

    def test_find_stream_fake_bad_idx(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            st = { "type": MediaType.AVMEDIA_TYPE_VIDEO }
            pyrana.formats.find_stream((st,), 1,
                                      MediaType.AVMEDIA_TYPE_VIDEO)

    def test_find_stream_fake_good(self):
        st = { "type": MediaType.AVMEDIA_TYPE_VIDEO }
        idx = pyrana.formats.find_stream((st,), 0,
                                        MediaType.AVMEDIA_TYPE_VIDEO)
        assert idx == 0

    def test_raw_packet(self):
        with pyrana.packet.raw_packet(128) as cpkt:
            assert(cpkt.size == 128)


if __name__ == "__main__":
    unittest.main()
