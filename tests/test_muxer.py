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
        self.f = io.BytesIO()
        self.f.name = 'bio'  # XXX

    def tearDown(self):
        self.f.close()

    def test_open_empty_buf_fail(self):
        with self.assertRaises(pyrana.errors.SetupError):
            mux = pyrana.formats.Muxer(self.f)
            assert mux

    def test_open_empty_buf_autodetect(self):
        self.f.name = 'bio_test.avi'  # XXX
        mux = pyrana.formats.Muxer(self.f)
        assert mux

    def test_open_empty_buf_named(self):
        mux = pyrana.formats.Muxer(self.f, name='avi')
        assert mux

    def test_open_encoders(self):
        mux = pyrana.formats.Muxer(self.f, name='avi')
        venc = mux.open_encoder('mjpeg', self.vparams)
        assert venc
        aenc = mux.open_encoder('mp2', self.aparams)
        assert aenc

    def test_write_header_no_streams(self):
        with self.assertRaises(pyrana.errors.ProcessingError):
            mux = pyrana.formats.Muxer(self.f, name='matroska')
            mux.write_header()

    def test_write_trailer_no_streams(self):
        with self.assertRaises(pyrana.errors.ProcessingError):
            mux = pyrana.formats.Muxer(self.f, name='avi')
            mux.write_header()

    def _open(self, fmt_name, encs, header=True):
        mux = pyrana.formats.Muxer(self.f, name=fmt_name)
        xenc = []
        for name, params in encs:
            xenc.append(mux.open_encoder(name, params))
        if header:
            mux.write_header()
        return mux, xenc

    def test_write_header_only_video(self):
        self._open('avi', (('mjpeg', self.vparams),))
        assert self.f.tell() > 0

    def test_write_trailer_only_video(self):
        mux, _ = self._open('avi', (('mjpeg', self.vparams),))
        mux.write_trailer()
        assert self.f.tell() > 0

    def test_write_header_only_audio(self):
        mux, _ = self._open('avi', (('flac', self.aparams),))
        assert self.f.tell() > 0

    def test_write_trailer_only_audio(self):
        mux, _ = self._open('avi', (('flac', self.aparams),))
        mux.write_trailer()
        assert self.f.tell() > 0

    def test_write_header_only_video_reg(self):
        mux = pyrana.formats.Muxer(self.f, name='matroska')
        enc = pyrana.video.Encoder('mjpeg', self.vparams)
        mux.add_stream(enc)
        mux.write_header()
        assert self.f.tell() > 0

    def test_write_header_only_audio_reg(self):
        mux = pyrana.formats.Muxer(self.f, name='matroska')
        enc = pyrana.audio.Encoder('flac', self.aparams)
        mux.add_stream(enc)
        mux.write_header()
        assert self.f.tell() > 0

    def test_write_trailer(self):
        mux, _ = self._open('matroska', (
                            ('mjpeg', self.vparams),
                            ('flac', self.aparams)))
        mux.write_trailer()
        assert self.f.tell() > 0

    def test_write_trailer_requires_header(self):
        mux, _ = self._open('avi', (
                            ('mjpeg', self.vparams),
                            ('flac', self.aparams)),
                            header=False)
        with self.assertRaises(pyrana.errors.ProcessingError):
            mux.write_trailer()

    def test_write_trailer_only_video_twice_fails(self):
        mux, _ = self._open('avi', (('mjpeg', self.vparams),))
        mux.write_trailer()
        with self.assertRaises(pyrana.errors.ProcessingError):
            mux.write_trailer()

    def test_write_frame_video(self):
        mux, xenc = self._open('avi', (('mjpeg', self.vparams),))
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P
        vfrm = pyrana.video.Frame(self.vparams['width'],
                                  self.vparams['height'],
                                  pixfmt)
        pyrana.video.fill_yuv420p(vfrm, 0)
        # hack, do no try this at home
        vfrm.cdata.format = self.pixfmt
        venc = xenc[0]
        pkt = venc.encode(vfrm)
        mux.write_frame(pkt)
        assert self.f.tell() > 0

    def test_write_trailer_only_audio_twice_fails(self):
        mux, xenc = self._open('avi', (('flac', self.aparams),))
        mux.write_trailer()
        with self.assertRaises(pyrana.errors.ProcessingError):
            mux.write_trailer()

    def test_write_frame_audio(self):
        mux, xenc = self._open('avi', (('flac', self.aparams),))
        # TODO FIXME


if __name__ == "__main__":
    unittest.main()
