#!/usr/bin/python

import pyrana
import unittest

import helper

samples = helper.get_samples_path()
st_info = helper.get_stream_info(samples)

class AudioDecTestCase(unittest.TestCase):
    def assertFrameValid(self, frm):
        assert(frm.idx == 0)
        assert(frm.size > 0)
        assert(len(frm.data) > 0)
    def assertFrameValidEmpty(self, frm):
        assert(frm.idx == 0)
        assert(frm.size >= 0)
        assert(len(frm.data) >= 0)
    def _decodeHelper(self, dmx, dec, N, emptable=False):
        for i in range(N):
            pkt = dmx.readFrame()
            frm = dec.decode(pkt)
            if emptable:
                self.assertFrameValidEmpty(frm)
            else:
                self.assertFrameValid(frm)

    def test00_CreateAudioDec(self):
        dec = pyrana.audio.Decoder("mp3")
        assert(dec)
    def test01_SpawnAudioDecXData(self):
        dmx = pyrana.format.Demuxer(open(samples["OGG_A"], "rb"))
        assert(len(dmx.streams) == 1)
        dec = dmx.openDecoder(0)
        assert(dec)
        assert(hasattr(dec, "decode"))
    def test02_SpawnAudioDecNOXData(self):
        dmx = pyrana.format.Demuxer(open(samples["MP3_A"], "rb"))
        assert(len(dmx.streams) == 1)
        dec = dmx.openDecoder(0)
        assert(dec)
        assert(hasattr(dec, "decode"))
    def test03_DecodeOneFrameNOXData(self):
        dmx = pyrana.format.Demuxer(open(samples["MP3_A"], "rb"))
        dec = dmx.openDecoder(0)
        self._decodeHelper(dmx, dec, 1)
    def test04_DecodeTwoFramesNOXData(self):
        # testing internal buffering
        dmx = pyrana.format.Demuxer(open(samples["MP3_A"], "rb"))
        dec = dmx.openDecoder(0)
        self._decodeHelper(dmx, dec, 2)
    def test05_DecodeOneFrameAndFlushNOXData(self):
        dmx = pyrana.format.Demuxer(open(samples["MP3_A"], "rb"))
        dec = dmx.openDecoder(0)
        self._decodeHelper(dmx, dec, 1)
        Fr = dec.flush()
        self.assertFrameValidEmpty(Fr)
    def test07_DecodeOneFrameAndFlush(self):
        dmx    = pyrana.format.Demuxer(open(samples["OGG_A"], "rb"))
        params = dmx.streams[0]
        assert(params)
        name   = params.pop('name')
        assert(params["extradata"])
        dec    = pyrana.audio.Decoder(name, params)
        self._decodeHelper(dmx, dec, 1, True)
        Fr     = dec.flush()
        self.assertFrameValidEmpty(Fr)




if __name__ == "__main__":
    if len(samples) == 0:
        sys.stderr.write("need at least one sample to go\n")
        sys.stderr.write("did you correctly edited the samples.cfg file?\n")
    unittest.main() 

