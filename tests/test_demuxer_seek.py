#!/usr/bin/python

import os.path
from pyrana.common import MediaType
from pyrana.formats import STREAM_ANY
import pyrana.errors
import pyrana.formats
import pyrana
import unittest



BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


class TestDemuxerSeel(unittest.TestCase):
    @unittest.expectedFailure
    def test_seek_video_frameno(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            dmx.seek_frame(0, 3)
            pkt = dmx.read_frame(0)
            assert(pkt)
            assert(len(pkt))

    @unittest.expectedFailure
    def test_seek_audio_frameno(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            dmx.seek_frame(1, 3)
            pkt = dmx.read_frame(1)
            assert(pkt)
            assert(len(pkt))

    @unittest.expectedFailure
    def test_seek_video_ts(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            dmx.seek_ts(0, 100)
            pkt = dmx.read_frame(0)
            assert(pkt)
            assert(len(pkt))


if __name__ == "__main__":
    unittest.main()
