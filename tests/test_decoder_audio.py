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

from tests import fakes


BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


# TODO: refactoring
class TestDecoderAudio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

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
