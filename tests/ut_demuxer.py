#!/usr/bin/python

import pyrana
import unittest

import helper

samples = helper.get_samples_path()
st_info = helper.get_stream_info(samples)

def prepareSource():
    f = open(samples["OGG_AV"], "rb")
    assert(f)
    return f

def wrapOpen(fmt):
    f = prepareSource()
    dmx = pyrana.format.Demuxer(f, fmt)

class DemuxerTestCase(unittest.TestCase):
    def failUnlessEqualStreams(self, got, expected):
        for st, ex in zip(got, expected):
            self.assertTrue(len(st) == len(ex))
            for k in ex:
                if k == 'extraData':
                    # we can't compare extradata (yet)
                    continue
                self.failUnlessEqual(ex[k], st[k],
                                     "'%s' is different: ref='%s' got='%s'" \
                                     %(k, ex[k], st[k]))
    def test_CreateDemuxer(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.assertTrue(dmx)
    def test_HasStreams(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.assertTrue(len(dmx.streams) == 2)
    def test_StreamsAreCorrect(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.failUnlessEqualStreams(dmx.streams, st_info["OGG_AV"])
    def test_IsValidIdx(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f)
        self.assertTrue(dmx.streams)
        F = dmx.readFrame()
        self.assertTrue(F.idx in range(len(dmx.streams)))
    def test_StreamsObjSurvives(self):
        def getStreams():
            f = prepareSource()
            dmx = pyrana.format.Demuxer(f)
            return dmx.streams
        streams = getStreams()
        self.failUnlessEqualStreams(streams, st_info["OGG_AV"])
    def test_ForceRightFormat(self):
        f = prepareSource()
        dmx = pyrana.format.Demuxer(f, "ogg")
    def test_ForceInexistentFormat(self):
        self.assertRaises(pyrana.UnsupportedError, wrapOpen, "ZAPZAPZAP")
    def test_ForceWrongFormat(self):
        self.assertRaises(pyrana.SetupError, wrapOpen, "yuv4mpegpipe")
    def test_DirectOpen(self):
        dmx = pyrana.format.Demuxer(open(samples["OGG_AV"], "rb"))
        self.failUnlessEqualStreams(dmx.streams, st_info["OGG_AV"])
    def test_OpenDecoder(self):
        dmx = pyrana.format.Demuxer(open(samples["OGG_AV"], "rb"))
        dec = dmx.openDecoder(0)
        self.assertTrue(dec)
        self.assertTrue(hasattr(dec, "decode"))
       


if __name__ == "__main__":
    if len(samples) == 0:
        sys.stderr.write("need at least one sample to go\n")
        sys.stderr.write("did you correctly edited the samples.cfg file?\n")
    unittest.main() 

