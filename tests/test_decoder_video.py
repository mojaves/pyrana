#!/usr/bin/python

import sys
import os.path
import unittest
import pytest
import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
import pyrana.video


BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


def _next_image(dmx, dec, sid=0, pixfmt=None):
    frm = dec.decode(dmx.stream(sid))
    assert(frm)
    img = frm.image(pixfmt)
    assert(img)
    return img, frm


# TODO: refactoring
class TestDecoderVideo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_create_synth1(self):
        ffh = pyrana.ff.get_handle()
        ppframe = pyrana.codec._new_av_frame_pp(ffh)
        img = pyrana.video.Image.from_cdata(ppframe)
        assert(img.is_shared)
        ffh.lavc.avcodec_free_frame(ppframe)

    # FIXME: bulky. Also depends on decoder.
    def test_create_from_live_frame(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            assert(repr(img))
            assert(len(img) >= img.width * img.height)
            assert(img.is_shared)

    # FIXME: bulky. Also depends on decoder.
    @pytest.mark.skipif(sys.version_info < (3,),
                       reason="requires python3")
    def test_repr_str_equals(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            assert(repr(img) == str(img))

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec, pixfmt=pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
            assert(not img.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_bad(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frame = dec.decode(dmx.stream(0))
            with self.assertRaises(pyrana.errors.ProcessingError):
                img = frame.image(pyrana.video.PixelFormat.AV_PIX_FMT_NONE)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_indirect(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            assert(img.is_shared)
            img2 = img.convert(pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
            assert(img2)
            assert(not img2.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_indirect_bad(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            with self.assertRaises(pyrana.errors.ProcessingError):
                img2 = img.convert(pyrana.video.PixelFormat.AV_PIX_FMT_NONE)

    # FIXME: bulky. Also depends on decoder.
    def test_plane_get0(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            pln = img.plane(0)
            assert(pln)
            assert(isinstance(pln, bytes))

    # FIXME: bulky. Also depends on decoder.
    def test_plane_get3(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            plns = [ img.plane(0),
                     img.plane(1),
                     img.plane(2) ]
            for pln in plns:
                assert(pln)
                assert(isinstance(pln, bytes))
                assert(len(pln) <= len(plns[0]))

    # FIXME: bulky. Also depends on decoder.
    @unittest.expectedFailure
    def test_planes_vs_bytes(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            plns = img.plane(0) + img.plane(1) + img.plane(2)
            data = bytes(img)
            assert(len(img) == len(plns))
            assert(len(img) == len(data))
            assert(data == plns)

    # FIXME: bulky. Also depends on decoder.
    def test_plane_bad1(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            with self.assertRaises(pyrana.errors.ProcessingError):
                pln = img.plane(-1)

    # FIXME: bulky. Also depends on decoder.
    def test_plane_bad2(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img, frm = _next_image(dmx, dec)
            with self.assertRaises(pyrana.errors.ProcessingError):
                pln = img.plane(10)

    # FIXME: bulky. Also depends on decoder.
    def test_video_frame_has_not_samples(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frm = dec.decode(dmx.stream(0))
            with self.assertRaises(AttributeError):
                smp = frm.samples()


if __name__ == "__main__":
    unittest.main()
