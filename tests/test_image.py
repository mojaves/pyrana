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

from tests.mockslib import MockFF, MockFrame, MockLavu, MockSws


class TestImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_cannot_create_image(self):
        with self.assertRaises(pyrana.errors.SetupError):
            img = pyrana.video.Image()

    def test_cannot_create_sws_context(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, None, frame, pixfmt)

    def test_cannot_alloc_av_image(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=False)
        # inject only a faulty lavu
        ffh.lavu = MockLavu(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, None, frame, pixfmt)
        assert(ffh.lavu.img_allocs == 1)

    def test_cannot_convert(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P  # 0
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=False)
        ffh.sws = MockSws(False, True, pixfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, None, frame, pixfmt)
        assert(ffh.sws.scale_done == 1)


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
