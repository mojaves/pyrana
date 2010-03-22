#!/usr/bin/python

import pyrana
import unittest

class GlobalsTestCase(unittest.TestCase):
    def test_InputFormats(self):
        self.assertTrue(len(pyrana.format.input_formats) > 0)
    def test_OutputFormats(self):
        self.assertTrue(len(pyrana.format.output_formats) > 0)
    def test_InputVideoCodecs(self):
        self.assertTrue(len(pyrana.video.input_codecs) > 0)
    def test_OutputVideoCodecs(self):
        self.assertTrue(len(pyrana.video.output_codecs) > 0)
    def test_InputAudioCodecs(self):
        self.assertTrue(len(pyrana.audio.input_codecs) > 0)
    def test_OutputAudioCodecs(self):
        self.assertTrue(len(pyrana.audio.output_codecs) > 0)
    def test_ValidInputFormats(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.input_formats))
    def test_ValidInputFormats(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.output_formats))
    def test_ValidInputVideoCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.input_codecs))
    def test_ValidOutputVideoCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.output_codecs))
    def test_ValidInputAudioCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.input_codecs))
    def test_ValidOutputAudioCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.output_codecs))


if __name__ == "__main__":
    unittest.main()  

