#!/usr/bin/python

import os.path
import unittest

import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
import pyrana.video

from tests.mockslib import MockFF, MockFrame, MockLavu, MockSws


BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


def _next_image(dmx, dec, sid=0, pixfmt=None):
    frame = dec.decode(dmx.stream(sid))
    assert(frame)
    img = frame.image(pixfmt)
    assert(img)
    return img


class TestImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_cannot_create_image(self):
        with self.assertRaises(pyrana.errors.SetupError):
            img = pyrana.video.Image()

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
            img = _next_image(dmx, dec)
            assert(repr(img))
            assert(len(img) >= img.width * img.height)
            assert(img.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img = _next_image(dmx, dec, pixfmt=pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
            assert(not img.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_bad(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frame = dec.decode(dmx.stream(0))
            with self.assertRaises(pyrana.errors.ProcessingError):
                img = frame.image(pyrana.video.PixelFormat.AV_PIX_FMT_NB)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_indirect(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img = _next_image(dmx, dec)
            assert(img.is_shared)
            img2 = img.convert(pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
            assert(img2)
            assert(not img2.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_indirect_bad(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            img = _next_image(dmx, dec)
            with self.assertRaises(pyrana.errors.ProcessingError):
                img2 = img.convert(pyrana.video.PixelFormat.AV_PIX_FMT_NB)

    def test_cannot_create_sws_context(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, frame, pixfmt)

    def test_cannot_alloc_av_image(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=False)
        # inject only a faulty lavu
        ffh.lavu = MockLavu(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, frame, pixfmt)
        assert(ffh.lavu.img_allocs == 1)

    def test_cannot_convert(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P  # 0
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=False)
        ffh.sws = MockSws(False, True, pixfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, frame, pixfmt)
        assert(ffh.sws.scale_done == 1)


if __name__ == "__main__":
    unittest.main()
