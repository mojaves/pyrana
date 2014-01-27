#!/usr/bin/python

import os.path
import unittest

import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
from pyrana.video import PixelFormat
from pyrana.audio import SampleFormat



class TestBaseEncoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_base_encoder_bad_input_codec(self):
        with self.assertRaises(pyrana.errors.SetupError):
            dec = pyrana.codec.BaseEncoder(0)

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
        params = {
            'bit_rate': 1000,
            'width': 352,
            'height': 288,
            'time_base': (25, 1),
            'pix_fmt': PixelFormat.AV_PIX_FMT_YUVJ420P
        }
        enc = pyrana.codec.BaseEncoder("mjpeg", params)
        assert(enc)
        assert(repr(enc))

#    def test_base_encoder_audio(self):
#        enc = pyrana.codec.BaseEncoder("flac", {})
#        assert(enc)
#        assert(repr(enc))

    def test_encoder_video(self):
        params = {
            'bit_rate': 1000,
            'width': 352,
            'height': 288,
            'time_base': (25, 1),
            'pix_fmt': PixelFormat.AV_PIX_FMT_YUVJ420P
        }
        enc = pyrana.video.Decoder("mpeg1video", params)
        assert(enc)
        assert(repr(enc))
#
#    def test_encoder_audio_empty_flush(self):
#        enc = pyrana.audio.Decoder("flac")
#        with self.assertRaises(pyrana.errors.NeedFeedError):
#            frame = dec.flush()
#
#    def test_encoder_video_empty_flush(self):
#        enc = pyrana.video.Decoder("mpeg1video")
#        with self.assertRaises(pyrana.errors.NeedFeedError):
#            frame = dec.flush()


if __name__ == "__main__":
    unittest.main()
