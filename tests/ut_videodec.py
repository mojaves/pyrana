#!/usr/bin/python

import pyrana
import unittest

import helper

samples = helper.get_samples_path()
st_info = helper.get_stream_info(samples)

class VideoDecTestCase(unittest.TestCase):
    def assertIsDecoder(self, dec):
        self.assertTrue(dec)
        self.assertTrue(hasattr(dec, "decode"))
        return dec
    def assertFrameOfStream(self, vframe, streaminfo):
        self.assertTrue(vframe)
        self.assertTrue(hasattr(vframe, "image"))
        img = vframe.image;
        self.assertTrue(streaminfo["type"] == pyrana.MEDIA_VIDEO);
        self.assertTrue(img.width == streaminfo["width"])
        self.assertTrue(img.height == streaminfo["height"])
        self.assertTrue(img.pixFmt == streaminfo["pixFmt"])
        
#    def test00_CreateVideoDec(self):
#        dec = pyrana.video.Decoder("mpeg1video")
#        self.assertIsDecoder(dec)

    def test0N_FromDemuxerAV2V(self):
        dmx = pyrana.format.Demuxer(open(samples["OGG_AV"], "rb"))
        self.assertTrue(len(dmx.streams) >= 1)
        dec = dmx.openDecoder(0)
        self.assertIsDecoder(dec)
    def test0N_FromDemuxerV2V(self):
        dmx = pyrana.format.Demuxer(open(samples["MPG_V"], "rb"))
        self.assertTrue(len(dmx.streams) == 1)
        dec = dmx.openDecoder(0)
        self.assertIsDecoder(dec)

    def test0X_DecodeSingleFrame(self):
        dmx = pyrana.format.Demuxer(open(samples["OGG_AV"], "rb"))
        self.assertTrue(len(dmx.streams) >= 1)
        j = pyrana.format.find_stream(dmx.streams, 0, pyrana.MEDIA_VIDEO);
        info = dmx.streams[j]
        dec = dmx.openDecoder(j)
        self.assertIsDecoder(dec)
        pkt = dmx.readFrame(j)
        frm = dec.decode(pkt)
        self.assertFrameOfStream(frm, info);


if __name__ == "__main__":
    if len(samples) == 0:
        sys.stderr.write("need at least one sample to go\n")
        sys.stderr.write("did you correctly edited the samples.cfg file?\n")
    unittest.main() 

