#!/usr/bin/python

import io
import unittest
import hashlib
import os
import os.path

import pyrana
import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
from pyrana.common import MediaType
from pyrana.formats import STREAM_ANY
from pyrana.video import PixelFormat
from pyrana.audio import SampleFormat, ChannelLayout



class TestMuxer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def setUp(self):
        self.pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUVJ420P
        self.vparams = {
            'bit_rate': 1000,
            'width': 352,
            'height': 288,
            'time_base': (1, 25),
            'pix_fmt': PixelFormat.AV_PIX_FMT_YUVJ420P
        }
        self.aparams = {
            'bit_rate': 64000,
            'sample_rate': 22050,
            'channel_layout': ChannelLayout.AV_CH_LAYOUT_STEREO,
            'sample_fmt': SampleFormat.AV_SAMPLE_FMT_S16
        }

    def test_open_empty_buf_fail(self):
        with self.assertRaises(pyrana.errors.SetupError), \
                io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f)
            assert mux

    def test_open_empty_buf_autodetect(self):
        with io.BytesIO() as f:
            f.name = 'bio_test.avi'  # XXX
            mux = pyrana.formats.Muxer(f)
            assert mux

    def test_open_empty_buf_named(self):
        with io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            assert mux

    def test_open_encoders(self):
        with io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            venc = mux.open_encoder('mjpeg', self.vparams)
            aenc = mux.open_encoder('mp2', self.aparams)

    def test_write_header_no_streams(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
                io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            mux.write_header()

    def test_write_trailer_no_streams(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
                io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            mux.write_header()

    def test_write_header_only_video(self):
        with io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            venc = mux.open_encoder('mjpeg', self.vparams)
            mux.write_header()
            assert f.tell() > 0

    def test_write_trailer_only_video(self):
        with io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            venc = mux.open_encoder('mjpeg', self.vparams)
            mux.write_header()
            mux.write_trailer()
            assert f.tell() > 0

    def test_write_trailer_requires_header(self):
        with io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            venc = mux.open_encoder('mjpeg', self.vparams)
            with self.assertRaises(pyrana.errors.ProcessingError):
                mux.write_trailer()

    def test_write_trailer_only_video_twice_fails(self):
        with io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            venc = mux.open_encoder('mjpeg', self.vparams)
            mux.write_header()
            mux.write_trailer()
            with self.assertRaises(pyrana.errors.ProcessingError):
                mux.write_trailer()

    def test_write_frame_video(self):
        with io.BytesIO() as f:
            f.name = 'bio'  # XXX
            mux = pyrana.formats.Muxer(f, name='avi')
            venc = mux.open_encoder('mjpeg', self.vparams)
            mux.write_header()
            pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P
            vfrm = pyrana.video.Frame(self.vparams['width'],
                                     self.vparams['height'],
                                     pixfmt)
            pyrana.video.fill_yuv420p(vfrm, 0)
            # hack, do no try this at home
            vfrm.cdata.format = self.pixfmt
            pkt = venc.encode(vfrm)
            mux.write_frame(pkt)
            assert f.tell() > 0


if __name__ == "__main__":
    unittest.main()
