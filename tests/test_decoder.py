#!/usr/bin/python

import unittest
import pyrana.ff
import pyrana.errors
import pyrana.codec


class TestBaseCodecs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_base_decoder_bad_input_codec(self):
        with self.assertRaises(pyrana.errors.SetupError):
            dec = pyrana.codec.BaseDecoder(0)

    def test_base_decoder_video(self):
        dec = pyrana.codec.BaseDecoder("mjpeg")
        assert(dec)
        assert(repr(dec))
    
    def test_base_decoder_audio(self):
        dec = pyrana.codec.BaseDecoder("pcm_s16le")
        assert(dec)
        assert(repr(dec))


if __name__ == "__main__":
    unittest.main()
