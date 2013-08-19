#!/usr/bin/python

import pyrana
import pyrana.audio
import pyrana.video
import pyrana.format
import pyrana.common
import unittest


class TestCommonData(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    def _assert_valid_collection(self, col):
        self.assertTrue(len(col) > 0)

    def _assert_valid_collection_items(self, col):
        self.assertTrue(all(len(c) > 0 for c in col))

    def test_input_format(self):
        self._assert_valid_collection(pyrana.format.INPUT_FORMATS)

    def test_output_format(self):
        self._assert_valid_collection(pyrana.format.OUTPUT_FORMATS)

    def test_input_video_codecs(self):
        self._assert_valid_collection(pyrana.video.INPUT_CODECS)

    def test_output_video_codecs(self):
        self._assert_valid_collection(pyrana.video.OUTPUT_CODECS)

    def test_pixel_format(self):
        self._assert_valid_collection(pyrana.video.PixelFormat)

    def test_input_audio_codecs(self):
        self._assert_valid_collection(pyrana.audio.INPUT_CODECS)

    def test_output_audio_codecs(self):
        self._assert_valid_collection(pyrana.audio.OUTPUT_CODECS)

    @unittest.expectedFailure
    def test_sample_format(self):
        self._assert_valid_collection(pyrana.audio.SampleFormat)

    def test_valid_input_format(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.INPUT_FORMATS))

    def test_valid_input_format(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.format.OUTPUT_FORMATS))

    def test_valid_input_video_codecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.INPUT_CODECS))

    def test_valid_output_video_codecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.video.OUTPUT_CODECS))

    def test_valid_input_audio_codecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.INPUT_CODECS))

    def test_valid_output_audio_codecs(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.audio.OUTPUT_CODECS))

    def test_all_formats(self):
        x, y = pyrana.common.all_formats()
        self.assertTrue(len(x))
        self.assertTrue(len(y))
