#!/usr/bin/python

import pyrana
import unittest

import helper


_SAMPLES = helper.get_samples_path()
_ST_INFO = helper.get_stream_info(_SAMPLES)


def prepare_source(K="OGG_AV"):
    return open(_SAMPLES[K], "rb")


def open_dmx(fmt):
    try:
        f = prepare_source()
        dmx = pyrana.format.Demuxer(f, fmt)
    finally:
        f.close()
        raise


class TestDemuxer(helper.BaseFormatTestCase):
    def test_CreateDemuxer(self):
        with prepare_source() as f:
            dmx = pyrana.format.Demuxer(f)
            self.assertTrue(dmx)
    def test_HasStreams(self):
        with prepare_source() as f:
            dmx = pyrana.format.Demuxer(f)
            self.assertTrue(len(dmx.streams) == 2)
    def test_StreamsAreCorrect(self):
        with prepare_source() as f:
            dmx = pyrana.format.Demuxer(f)
            self.failUnlessEqualStreams(dmx.streams, _ST_INFO["OGG_AV"])
    def test_IsValidIdx(self):
        with prepare_source() as f:
            dmx = pyrana.format.Demuxer(f)
            self.assertTrue(dmx.streams)
            F = dmx.read_frame()
            self.assertTrue(F.stream_id in range(len(dmx.streams)))
    def test_StreamsObjSurvives(self):
        def get_streams():
            f = prepare_source()
            dmx = pyrana.format.Demuxer(f)
            f.close()
            return dmx.streams
        streams = get_streams()
        self.failUnlessEqualStreams(streams, _ST_INFO["OGG_AV"])
    def test_ForceRightFormat(self):
        fmt = "avi"
        f = prepare_source("%s_AV" %(fmt.upper()))
        dmx = pyrana.format.Demuxer(f, fmt)
        f.close()
    def test_ForceInexistentFormat(self):
        self.assertRaises(pyrana.UnsupportedError, open_dmx, "ZAPZAPZAP")
    def test_ForceWrongFormat(self):
        self.assertRaises(pyrana.SetupError, open_dmx, "yuv4mpegpipe")
    def test_DirectOpen(self):
        with open(_SAMPLES["OGG_AV"], "rb") as f:
            dmx = pyrana.format.Demuxer(f)
            self.failUnlessEqualStreams(dmx.streams, _ST_INFO["OGG_AV"])
    def test_OpenDecoder(self):
        with open(_SAMPLES["MOV_AV"], "rb") as f:
            dmx = pyrana.format.Demuxer(f)
            dec = dmx.open_decoder(0)
            self.assertTrue(dec)
            self.assertTrue(hasattr(dec, "decode"))
       


if __name__ == "__main__":
    if len(_SAMPLES) == 0:
        sys.stderr.write("need at least one sample to go\n")
        sys.stderr.write("did you correctly edit the samples.cfg file?\n")
    unittest.main() 

