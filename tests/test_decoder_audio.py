#!/usr/bin/python

import os.path
import unittest

import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
import pyrana.audio

#from tests.mockslib import MockFF, MockFrame, MockLavu, MockSws


BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


class TestSamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_cannot_create_samples(self):
        with self.assertRaises(pyrana.errors.SetupError):
            img = pyrana.audio.Samples()

    def test_create_synth1(self):
        ffh = pyrana.ff.get_handle()
        ppframe = pyrana.codec._new_av_frame_pp(ffh)
        smp = pyrana.audio.Samples.from_cdata(ppframe)
        assert(smp.is_shared)
        ffh.lavc.avcodec_free_frame(ppframe)

    # FIXME: bulky. Also depends on decoder.
    def test_create_from_live_frame(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frames = dec.decode(dmx.stream(1))
            assert(frames)
            smp = frames[0].samples()
            assert(smp)
            assert(repr(smp))
            assert(len(smp))
            assert(smp.is_shared)


if __name__ == "__main__":
    unittest.main()
