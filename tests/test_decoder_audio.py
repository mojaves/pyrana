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
            frm = dec.decode(dmx.stream(1))
            assert(frm)
            smp = frm.samples()
            assert(smp)
            assert(repr(smp))
            assert(len(smp))
            assert(smp.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_indirect(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            assert(frm)
            smp = frm.samples()
            assert(smp)
            assert(smp.is_shared)
            smp2 = smp.convert(pyrana.audio.SampleFormat.AV_SAMPLE_FMT_S32P)
            # assert(smp2) # FIXME
            assert(not smp2.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_audio_frame_has_not_image(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            with self.assertRaises(AttributeError):
                img = frm.image()


if __name__ == "__main__":
    unittest.main()
