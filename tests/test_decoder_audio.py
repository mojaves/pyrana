#!/usr/bin/python

import sys
import os.path
import unittest
import pytest
import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
import pyrana.audio

from tests.mockslib import MockFF, MockFrame, MockLavu, MockSwr


BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


# TODO: refactoring
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

    def test_cannot_create_swr_context(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP
        frame = MockFrame(smpfmt)
        ffh = MockFF(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)

    def test_cannot_init_swr_context(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP
        frame = MockFrame(smpfmt)
        ffh = MockFF(faulty=False)
        ffh.swr = MockSwr(faulty=False, bad_smp_fmt=smpfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)
        assert(ffh.swr.ctx_inited == 1)

    def test_cannot_alloc_samples(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP
        frame = MockFrame(smpfmt)
        ffh = MockFF(faulty=False)
        ffh.lavu = MockLavu(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)
        assert(ffh.swr.ctx_inited == 1)
        assert(ffh.lavu.smp_allocs == 1)

    def test_cannot_convert_samples(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP
        frame = MockFrame(smpfmt)
        ffh = MockFF(faulty=False)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)
        assert(ffh.swr.ctx_inited == 1)
        assert(ffh.lavu.smp_allocs == 1)
        assert(ffh.swr.conversions == 1)

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
    @pytest.mark.skipif(sys.version_info < (3,),
                       reason="requires python3")
    def test_repr_str_equals(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            smp = frm.samples()
            assert(repr(smp) == str(smp))

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            assert(frm)
            smp = frm.samples(pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP)
            # assert(smp)  # FIXME
            assert(repr(smp))
            #assert(len(smp))  # FIXME
            assert(not smp.is_shared)

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

    # FIXME: bulky. Also depends on decoder.
    def test_channel_bad1(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            assert(frm)
            smp = frm.samples()
            # assert(smp)  # FIXME
            with self.assertRaises(pyrana.errors.ProcessingError):
                dat = smp.channel(-1)

    # FIXME: bulky. Also depends on decoder.
    def test_channel_bad2(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            assert(frm)
            smp = frm.samples()
            # assert(smp)  # FIXME
            with self.assertRaises(pyrana.errors.ProcessingError):
                dat = smp.channel(10)

    # FIXME: bulky. Also depends on decoder.
    def test_channel_get0(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            smp = frm.samples()
            chn = smp.channel(0)
            assert(chn)
            assert(isinstance(chn, bytes))

    # FIXME: bulky. Also depends on decoder.
    def test_bytes(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            smp = frm.samples()
            dat = bytes(smp)
            assert(dat)
            assert(isinstance(dat, bytes))



if __name__ == "__main__":
    unittest.main()
