#!/usr/bin/python

from collections import namedtuple
import unittest
import pyrana.formats
import pyrana.packet
import pyrana.errors
from pyrana.common import MediaType


FakeTimeBase = namedtuple('FakeTimeBase', ['num', 'den'])
FakeInfo = namedtuple('FakeInfo', ['media_type' ])

NullInfo = FakeInfo(media_type=MediaType.AVMEDIA_TYPE_UNKNOWN)
VideoInfo = FakeInfo(media_type=MediaType.AVMEDIA_TYPE_VIDEO)
AudioInfo = FakeInfo(media_type=MediaType.AVMEDIA_TYPE_AUDIO)


class TestFormatFuncs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_find_stream_empty(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            pyrana.formats.find_stream((), 0, MediaType.AVMEDIA_TYPE_UNKNOWN)

    def test_find_stream_empty2(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            pyrana.formats.find_stream((VideoInfo, ), 0,
                                      MediaType.AVMEDIA_TYPE_UNKNOWN)

    def test_find_stream_empty3(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            pyrana.formats.find_stream((VideoInfo, NullInfo, ), 1,
                                       MediaType.AVMEDIA_TYPE_VIDEO)

    def test_find_stream_fake_bad(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            pyrana.formats.find_stream((VideoInfo,), 0,
                                      MediaType.AVMEDIA_TYPE_AUDIO)

    def test_find_stream_fake_bad_idx(self):
        with self.assertRaises(pyrana.errors.NotFoundError):
            pyrana.formats.find_stream((VideoInfo,), 1,
                                      MediaType.AVMEDIA_TYPE_VIDEO)

    def test_find_stream_fake_good(self):
        idx = pyrana.formats.find_stream((VideoInfo,), 0,
                                        MediaType.AVMEDIA_TYPE_VIDEO)
        assert idx == 0

    def test_raw_packet(self):
        with pyrana.packet.raw_packet(128) as cpkt:
            assert(cpkt.size == 128)

    def test_tb_zero_division_error(self):
        tb = FakeTimeBase(0, 0)
        x = pyrana.formats._tb_to_str(tb)


if __name__ == "__main__":
    unittest.main()
