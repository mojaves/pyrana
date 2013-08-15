#!/usr/bin/python

import pyrana
import pyrana.audio
import pyrana.video
import unittest

class TestCommonData(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    def _assertValidCollection(self, col):
        self.assertTrue(len(col) > 0)

    def _assertValidCollectionItems(self, col):
        self.assertTrue(all(len(c) > 0 for c in col))

    def test_InputFormat(self):
        self._assertValidCollection(pyrana.format.INPUT_FORMATS)

    def test_OutputFormat(self):
        self._assertValidCollection(pyrana.format.OUTPUT_FORMATS)

    def test_InputVideoCodecs(self):
        self._assertValidCollection(pyrana.video.INPUT_CODECS)

    def test_OutputVideoCodecs(self):
        self._assertValidCollection(pyrana.video.OUTPUT_CODECS)

    def test_PixelFormat(self):
        self._assertValidCollection(pyrana.video.PixelFormat)

    def test_InputAudioCodecs(self):
        self._assertValidCollection(pyrana.audio.INPUT_CODECS)

    def test_OutputAudioCodecs(self):
        self._assertValidCollection(pyrana.audio.OUTPUT_CODECS)

    def test_SampleFormat(self):
        self._assertValidCollection(pyrana.audio.SampleFormat)

    def test_ValidInputFormat(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.INPUT_FORMATS))

    def test_ValidInputFormat(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.OUTPUT_FORMATS))

    def test_ValidInputVideoCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.INPUT_CODECS))

    def test_ValidOutputVideoCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.OUTPUT_CODECS))

    def test_ValidInputAudioCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.INPUT_CODECS))

    def test_ValidOutputAudioCodecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.OUTPUT_CODECS))
