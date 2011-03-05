#!/usr/bin/python

import pyrana
import unittest

import helper

samples = helper.get_samples_path()
st_info = helper.get_stream_info(samples)

def prepareSource(K="OGG_AV"):
    f = open(samples[K], "rb")
    assert(f)
    return f

def wrapOpen(fmt):
    try:
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f, fmt)
    finally:
        f.close()
        raise

class DemuxerTestCase(helper.BaseFormatTestCase):
    def test_CreateDemuxer(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.assertTrue(dmx)
        f.close()
    def test_HasStreams(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.assertTrue(len(dmx.streams) == 2)
        f.close()
    def test_StreamsAreCorrect(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.failUnlessEqualStreams(dmx.streams, st_info["OGG_AV"])
        f.close()
    def test_IsValidIdx(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.assertTrue(dmx.streams)
        F = dmx.read_frame()
        self.assertTrue(F.stream_id in range(len(dmx.streams)))
        f.close()
    def test_StreamsObjSurvives(self):
        def getStreams():
            f = prepareSource()
            dmx = pyrana.format.Demuxer(f)
            f.close()
            return dmx.streams
        streams = getStreams()
        self.failUnlessEqualStreams(streams, st_info["OGG_AV"])
    def test_ForceRightFormat(self):
        fmt = "avi"
        f = prepareSource("%s_AV" %(fmt.upper()))
        dmx = pyrana.format.Demuxer(f, fmt)
        f.close()
    def test_ForceInexistentFormat(self):
        self.assertRaises(pyrana.UnsupportedError, wrapOpen, "ZAPZAPZAP")
    def test_ForceWrongFormat(self):
        self.assertRaises(pyrana.SetupError, wrapOpen, "yuv4mpegpipe")
    def test_DirectOpen(self):
        f = open(samples["OGG_AV"], "rb")
        dmx = pyrana.format.Demuxer(f)
        self.failUnlessEqualStreams(dmx.streams, st_info["OGG_AV"])
        f.close()
    def test_OpenDecoder(self):
        f = open(samples["MOV_AV"], "rb")
        dmx = pyrana.format.Demuxer(f)
        dec = dmx.open_decoder(0)
        self.assertTrue(dec)
        self.assertTrue(hasattr(dec, "decode"))
        f.close()
       


if __name__ == "__main__":
    if len(samples) == 0:
        sys.stderr.write("need at least one sample to go\n")
        sys.stderr.write("did you correctly edited the samples.cfg file?\n")
    unittest.main() 

