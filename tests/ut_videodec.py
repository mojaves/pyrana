#!/usr/bin/python

import pyrana
import unittest

import helper

samples = helper.get_samples_path()
st_info = helper.get_stream_info(samples)

def assertIsDecoder(dec):
    assert(dec)
    assert(hasattr(dec, "decode"))
    return dec

def makeDec(fmt):
    dec = pyrana.video.Decoder(fmt)
    return assertIsDecoder(dec)

class VideoDecTestCase(unittest.TestCase):
    def assertFrameOfStream(self, vframe, streaminfo):
        self.assertTrue(vframe)
        self.assertTrue(hasattr(vframe, "image"))
        img = vframe.image;
        self.assertTrue(streaminfo["type"] == pyrana.MEDIA_VIDEO);
        self.assertTrue(img.width == streaminfo["width"])
        self.assertTrue(img.height == streaminfo["height"])
        self.assertTrue(img.pixFmt == streaminfo["pixFmt"])
    
    def test_CreateVideoDec(self):
        makeDec("mpeg1video")
    def test_CannotCreateVideoDecInvalid(self):
        self.assertRaises(pyrana.SetupError, makeDec, "Niggurath")
    def test_FromDemuxerAV(self):
        dmx = pyrana.format.Demuxer(open(samples["OGG_AV"], "rb"))
        self.assertTrue(len(dmx.streams) >= 1)
        dec = dmx.openDecoder(0)
        assertIsDecoder(dec)
    def test_FromDemuxerV(self):
        dmx = pyrana.format.Demuxer(open(samples["MPG_V"], "rb"))
        self.assertTrue(len(dmx.streams) == 1)
        dec = dmx.openDecoder(0)
        assertIsDecoder(dec)
    def test_DecodeSingleFrame(self):
        dmx = pyrana.format.Demuxer(open(samples["OGG_AV"], "rb"))
        self.assertTrue(len(dmx.streams) >= 1)
        j = pyrana.format.find_stream(dmx.streams, 0, pyrana.MEDIA_VIDEO);
        info = dmx.streams[j]
        dec = dmx.openDecoder(j)
        assertIsDecoder(dec)
        pkt = dmx.readFrame(j)
        frm = dec.decode(pkt)
        self.assertFrameOfStream(frm, info);


if __name__ == "__main__":
    if len(samples) == 0:
        sys.stderr.write("need at least one sample to go\n")
        sys.stderr.write("did you correctly edited the samples.cfg file?\n")
    unittest.main() 

