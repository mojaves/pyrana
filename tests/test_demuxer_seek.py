#!/usr/bin/python

import os.path
from pyrana.common import MediaType
from pyrana.formats import STREAM_ANY
import pyrana.errors
import pyrana.formats
import pyrana
import unittest



BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


class TestDemuxerSeek(unittest.TestCase):
    def test_seek_video_frameno_not_ready(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin, delay_open=True)
            with self.assertRaises(pyrana.errors.ProcessingError):
                dmx.seek_frame(0, 3)

    def test_seek_video_ts_not_ready(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin, delay_open=True)
            with self.assertRaises(pyrana.errors.ProcessingError):
                dmx.seek_ts(0, 100)

    def read_pkt_at_ts(self, sid, ts=100):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            dmx.seek_ts(sid, ts)
            pkt = dmx.read_frame(sid)
            assert(pkt)
            assert(len(pkt))
            return dmx

    def read_pkt_at_frameno(self, sid, frameno=3):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            dmx.seek_frame(sid, frameno)
            pkt = dmx.read_frame(sid)
            assert(pkt)
            assert(len(pkt))
            return dmx

    @unittest.expectedFailure
    def test_seek_video_frameno(self):
        self.read_pkt_at_frameno(0)

    @unittest.expectedFailure
    def test_seek_audio_frameno(self):
        self.read_pkt_at_frameno(1)

    @unittest.expectedFailure
    def test_seek_video_ts(self):
        self.read_pkt_at_ts(0)

    @unittest.expectedFailure
    def test_seek_audio_ts(self):
        self.read_pkt_at_ts(1)


if __name__ == "__main__":
    unittest.main()
