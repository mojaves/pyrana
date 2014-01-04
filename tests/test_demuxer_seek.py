#!/usr/bin/python

import os
import os.path
import warnings
from pyrana.common import MediaType
from pyrana.formats import STREAM_ANY
import pyrana.errors
import pyrana.formats
import pyrana.iobridge
import pyrana
import unittest



BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


class TestDemuxerSeek(unittest.TestCase):
    def test_seek_video_frameno_not_ready(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin, delay_open=True)
            with self.assertRaises(pyrana.errors.ProcessingError):
                with warnings.catch_warnings():
                    dmx.seek_frame(3)

    def test_seek_video_ts_not_ready(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin, delay_open=True)
            with self.assertRaises(pyrana.errors.ProcessingError):
                with warnings.catch_warnings():
                    dmx.seek_ts(100)

    def read_pkt_at_ts(self, sid, ts=100):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            with warnings.catch_warnings():
                dmx.seek_ts(ts, sid)
            pkt = dmx.read_frame(sid)
            assert(pkt)
            assert(len(pkt))
            return dmx

    def read_pkt_at_frameno(self, sid, frameno=3):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            with warnings.catch_warnings():
                dmx.seek_frame(frameno, sid)
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

    def test_seek_video_ts(self):
        self.read_pkt_at_ts(0)

    def test_seek_audio_ts(self):
        self.read_pkt_at_ts(1)

    def test_seek_any_ts(self):
        self.read_pkt_at_ts(STREAM_ANY)

    def test_seek_fails(self):
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin, streaming=True)
            with self.assertRaises(pyrana.errors.ProcessingError):
                with warnings.catch_warnings():
                    dmx.seek_ts(-1e5, STREAM_ANY)


if __name__ == "__main__":
    unittest.main()
