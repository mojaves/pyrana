#!/usr/bin/python

import os.path
import unittest

import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
from pyrana.video import PixelFormat
from pyrana.audio import SampleFormat, ChannelLayout


class TestBaseEncoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def setUp(self):
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

    def test_base_encoder_bad_input_codec(self):
        with self.assertRaises(pyrana.errors.SetupError):
            dec = pyrana.codec.BaseEncoder(0, {})

    def test_encoder_require_params(self):
        with self.assertRaises(pyrana.errors.SetupError):
            enc = pyrana.codec.BaseEncoder("mjpeg", {})
        with self.assertRaises(pyrana.errors.SetupError):
            enc = pyrana.codec.BaseEncoder("mp3", {})

    def test_encode_invalid_param(self):
        with self.assertRaises(pyrana.errors.WrongParameterError):
            params = { "foobar": 42 }
            enc = pyrana.codec.BaseEncoder("mjpeg", params)

    def test_base_encoder_video(self):
        enc = pyrana.codec.BaseEncoder("mjpeg", self.vparams)
        assert(enc)
        assert(repr(enc))

    def test_base_encoder_audio(self):
        enc = pyrana.codec.BaseEncoder("flac", self.aparams)
        assert(enc)
        assert(repr(enc))

    def test_encoder_video(self):
        self.vparams['pix_fmt'] = PixelFormat.AV_PIX_FMT_YUV420P
        enc = pyrana.video.Encoder("mpeg1video", self.vparams)
        assert(enc)
        assert(repr(enc))

    def test_encoder_audio_empty_flush(self):
        enc = pyrana.audio.Encoder("flac", self.aparams)
        with self.assertRaises(pyrana.errors.NeedFeedError):
            frame = enc.flush()

    def test_encoder_video_empty_flush(self):
        self.vparams['pix_fmt'] = PixelFormat.AV_PIX_FMT_YUV420P
        enc = pyrana.video.Encoder("mpeg1video", self.vparams)
        with self.assertRaises(pyrana.errors.NeedFeedError):
            frame = enc.flush()


if __name__ == "__main__":
    unittest.main()
