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

from tests import fakes


def _new_frame(pixfmt):  # FIXME naming
    frm = pyrana.video.Frame(352, 288, pixfmt)
    img = frm.image()
    return frm, img


class TestImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_cannot_create_image(self):
        with self.assertRaises(pyrana.errors.SetupError):
            img = pyrana.video.Image()

    def test_cannot_create_sws_context(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = fakes.Frame(pixfmt)
        ffh = fakes.FF(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, None, frame, pixfmt)

    def test_cannot_alloc_av_image(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = fakes.Frame(pixfmt)
        ffh = fakes.FF(faulty=False)
        # inject only a faulty lavu
        ffh.lavu = fakes.Lavu(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, None, frame, pixfmt)
        assert(ffh.lavu.img_allocs == 1)

    def test_cannot_convert(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P  # 0
        frame = fakes.Frame(pixfmt)
        ffh = fakes.FF(faulty=False)
        ffh.sws = fakes.Sws(False, True, pixfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, None, frame, pixfmt)
        assert(ffh.sws.scale_done == 1)

    def test_new_frame(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P  # 0
        frm, img = _new_frame(pixfmt)
        assert(repr(img))
        assert(len(img) >= img.width * img.height)
        assert(img.is_shared)

    def test_fill_frame(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P  # 0
        frm, img = _new_frame(pixfmt)
        pyrana.video.fill_yuv420p(frm, 0)

    def test_fill_frame_bad_pixmft(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24  # 0
        frm, img = _new_frame(pixfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video.fill_yuv420p(frm, 0)



class TestPlaneCopy(unittest.TestCase):
    def test__plane_copy_bad_src_linesize(self):
        dst = bytearray(16)
        src = b'a' * 16
        with self.assertRaises(pyrana.errors.ProcessingError):
            num = pyrana.video._plane_copy(dst, src, 15, 16, 16, 1)

    def test__plane_copy_bad_src_linesize(self):
        dst = bytearray(16)
        src = b'a' * 16
        with self.assertRaises(pyrana.errors.ProcessingError):
            num = pyrana.video._plane_copy(dst, src, 16, 15, 16, 1)

    def test__plane_copy(self):
        dst = bytearray(16)
        src = b'a' * 16
        num = pyrana.video._plane_copy(dst, src, 16, 16, 16, 1)
        assert(dst == src)


if __name__ == "__main__":
    unittest.main()
