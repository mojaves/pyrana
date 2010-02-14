#!/usr/bin/python

import pyrana
import unittest

class GlobalsTestCase(unittest.TestCase):
    def test_InputFormats(self):
        assert(len(pyrana.format.input_formats) > 0)
    def test_OutputFormats(self):
        assert(len(pyrana.format.output_formats) > 0)
    def test_InputVideoCodecs(self):
        assert(len(pyrana.video.input_codecs) > 0)
    def test_OutputVideoCodecs(self):
        assert(len(pyrana.video.output_codecs) > 0)
    def test_InputAudioCodecs(self):
        assert(len(pyrana.audio.input_codecs) > 0)
    def test_OutputAudioCodecs(self):
        assert(len(pyrana.audio.output_codecs) > 0)
    def test_ValidInputFormats(self):
        assert(all(len(name) > 0 for name in pyrana.format.input_formats))
    def test_ValidInputFormats(self):
        assert(all(len(name) > 0 for name in pyrana.format.output_formats))
    def test_ValidInputVideoCodecs(self):
        assert(all(len(name) > 0 for name in pyrana.video.input_codecs))
    def test_ValidOutputVideoCodecs(self):
        assert(all(len(name) > 0 for name in pyrana.video.output_codecs))
    def test_ValidInputAudioCodecs(self):
        assert(all(len(name) > 0 for name in pyrana.audio.input_codecs))
    def test_ValidOutputAudioCodecs(self):
        assert(all(len(name) > 0 for name in pyrana.audio.output_codecs))


if __name__ == "__main__":
    unittest.main()  
