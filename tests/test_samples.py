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


if __name__ == "__main__":
    unittest.main()
