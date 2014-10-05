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
from pyrana.audio import ChannelLayout, SampleFormat

from tests import fakes


def _new_frame(smpfmt):  # FIXME naming
    frm = pyrana.audio.Frame(44100,
                             ChannelLayout.AV_CH_LAYOUT_STEREO,
                             smpfmt)
    smp = frm.samples()
    return frm, smp


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
        frame = fakes.Frame(smpfmt)
        ffh = fakes.FF(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)

    def test_cannot_init_swr_context(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP
        frame = fakes.Frame(smpfmt)
        ffh = fakes.FF(faulty=False)
        ffh.swr = fakes.Swr(faulty=False, bad_smp_fmt=smpfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)
        assert(ffh.swr.ctx_inited == 1)

    def test_cannot_alloc_samples(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP
        frame = fakes.Frame(smpfmt)
        ffh = fakes.FF(faulty=False)
        ffh.lavu = fakes.Lavu(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)
        assert(ffh.swr.ctx_inited == 1)
        assert(ffh.lavu.smp_allocs == 1)

    def test_cannot_convert_samples(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLTP
        frame = fakes.Frame(smpfmt)
        ffh = fakes.FF(faulty=False)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio._samples_from_frame(ffh, None, frame, smpfmt)
        assert(ffh.swr.ctx_allocs == 1)
        assert(ffh.swr.ctx_inited == 1)
        assert(ffh.lavu.smp_allocs == 1)
        assert(ffh.swr.conversions == 1)

    def test_new_frame(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_S16  # 0
        frm, smp = _new_frame(smpfmt)
        assert(repr(smp))
        assert(len(smp) >= smp.channels * smp.sample_rate)
        assert(smp.is_shared)

    def test_fill_frame(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_S16  # 0
        frm, smp = _new_frame(smpfmt)
        pyrana.audio.fill_s16(frm)

    def test_fill_frame_bad_pixmft(self):
        smpfmt = pyrana.audio.SampleFormat.AV_SAMPLE_FMT_FLT
        frm, smp = _new_frame(smpfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.audio.fill_s16(frm)


if __name__ == "__main__":
    unittest.main()
