#!/usr/bin/python

import pyrana
import unittest

class TestCommonData(unittest.TestCase):
    def _assertValidCollection(self, col):
        self.assertTrue(len(col) > 0)
    def _assertValidCollectionItems(self, col):
        self.assertTrue(all(len(c) > 0 for c in col))

    def test_InputFormats(self):
        self._assertValidCollection(pyrana.format.input_formats)
    def test_OutputFormats(self):
        self._assertValidCollection(pyrana.format.output_formats)

    def test_InputVideoCodecs(self):
        self._assertValidCollection(pyrana.video.input_codecs)
    def test_OutputVideoCodecs(self):
        self._assertValidCollection(pyrana.video.output_codecs)
    def test_PixelFormats(self):
        self._assertValidCollection(pyrana.video.pixel_formats)
    def test_UserPixelFormats(self):
        self._assertValidCollection(pyrana.video.user_pixel_formats)

    def test_InputAudioCodecs(self):
        self._assertValidCollection(pyrana.audio.input_codecs)
    def test_OutputAudioCodecs(self):
        self._assertValidCollection(pyrana.audio.output_codecs)
    def test_SampleFormats(self):
        self._assertValidCollection(pyrana.audio.sample_formats)
    def test_UserSampleFormats(self):
        self._assertValidCollection(pyrana.audio.user_sample_formats)

    def test_ValidInputFormats(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.input_formats))
    def test_ValidInputFormats(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.output_formats))

    def test_ValidInputVideoCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.input_codecs))
    def test_ValidOutputVideoCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.output_codecs))
    def test_ValidPixelFormats(self):
        self._assertValidCollectionItems(pyrana.video.pixel_formats)
    def test_ValidUserPixelFormats(self):
        self._assertValidCollectionItems(pyrana.video.user_pixel_formats)

    def test_ValidInputAudioCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.input_codecs))
    def test_ValidOutputAudioCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.output_codecs))
    def test_ValidSampleFormats(self):
        self._assertValidCollectionItems(pyrana.audio.sample_formats)
    def test_ValidUserSampleFormats(self):
        self._assertValidCollectionItems(pyrana.audio.user_sample_formats)




if __name__ == "__main__":
    unittest.main()  

