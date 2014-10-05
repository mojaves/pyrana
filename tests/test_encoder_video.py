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


class TestEncoderVideo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def setUp(self):
        self.pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUVJ420P
        self.params = {
            'bit_rate': 1000,
            'width': 352,
            'height': 288,
            'time_base': (1, 25),
            'pix_fmt': self.pixfmt
        }

    def test_encoder_new(self):
        enc = pyrana.video.Encoder("mjpeg", self.params)
        assert(enc)
        assert(repr(enc))

    def test_base_encoder_encode1(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P
        enc = pyrana.codec.BaseEncoder("mjpeg", self.params)
        frm = pyrana.video.Frame(self.params['width'],
                                 self.params['height'],
                                 pixfmt)
        pyrana.video.fill_yuv420p(frm, 0)
        # hack, do no try this at home
        frm.cdata.format = self.pixfmt
        with self.assertRaises(pyrana.errors.ProcessingError):
            pkt = enc.encode(frm)

    def test_encoder_encode1(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P
        enc = pyrana.video.Encoder("mjpeg", self.params)
        frm = pyrana.video.Frame(self.params['width'],
                                 self.params['height'],
                                 pixfmt)
        pyrana.video.fill_yuv420p(frm, 0)
        # hack, do no try this at home
        frm.cdata.format = self.pixfmt
        pkt = enc.encode(frm)
        assert(pkt)
        assert(pkt.size >= 0)

    def test_encoder_encode25(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P
        enc = pyrana.video.Encoder("mjpeg", self.params)
        frm = pyrana.video.Frame(self.params['width'],
                                 self.params['height'],
                                 pixfmt)
        for i in range(25):
            frm.cdata.format = pixfmt
            pyrana.video.fill_yuv420p(frm, i)
            # hack, do no try this at home
            frm.cdata.format = self.pixfmt
            pkt = enc.encode(frm)
            assert(pkt)
            assert(pkt.size >= 0)

    def test_encoder_encode25_flush(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P
        enc = pyrana.video.Encoder("mjpeg", self.params)
        frm = pyrana.video.Frame(self.params['width'],
                                 self.params['height'],
                                 pixfmt)
        for i in range(25):
            frm.cdata.format = pixfmt
            pyrana.video.fill_yuv420p(frm, i)
            # hack, do no try this at home
            frm.cdata.format = self.pixfmt
            pkt = enc.encode(frm)
            assert(pkt)
            assert(pkt.size >= 0)
        with self.assertRaises(pyrana.errors.NeedFeedError):
            pkt = enc.flush()

    def test_encoder_flush_nothing(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P
        enc = pyrana.video.Encoder("mjpeg", self.params)
        with self.assertRaises(pyrana.errors.NeedFeedError):
            pkt = enc.flush()


if __name__ == "__main__":
    unittest.main()
