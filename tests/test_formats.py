#!/usr/bin/python

import pyrana
import pyrana.audio
import pyrana.video
import pyrana.formats
import pyrana.common
import pyrana.ff
import unittest


class TestCommonData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def _assert_valid_collection(self, col):
        self.assertTrue(len(col) > 0)

    def test_input_formats(self):
        self._assert_valid_collection(pyrana.formats.INPUT_FORMATS)

    def test_output_formats(self):
        self._assert_valid_collection(pyrana.formats.OUTPUT_FORMATS)

    def test_input_video_codecs(self):
        self._assert_valid_collection(pyrana.video.INPUT_CODECS)

    def test_output_video_codecs(self):
        self._assert_valid_collection(pyrana.video.OUTPUT_CODECS)

    def test_pixel_formats(self):
        self._assert_valid_collection(pyrana.video.PixelFormat)

    def test_input_audio_codecs(self):
        self._assert_valid_collection(pyrana.audio.INPUT_CODECS)

    def test_output_audio_codecs(self):
        self._assert_valid_collection(pyrana.audio.OUTPUT_CODECS)

    def test_sample_formats(self):
        self._assert_valid_collection(pyrana.audio.SampleFormat)

    def test_valid_input_formats(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.formats.INPUT_FORMATS))

    def test_valid_input_formats(self):
        self.assertTrue(all(len(name) > 0 for name in pyrana.formats.OUTPUT_FORMATS))

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

    def test_find_source_format_defaults(self):
        ffh = pyrana.ff.get_handle()
        fmt = pyrana.common.find_source_format()
        assert ffh.ffi.NULL == fmt

    def test_find_source_format_avi(self):
        ffh = pyrana.ff.get_handle()
        fmt = pyrana.common.find_source_format("avi")
        assert fmt
        assert ffh.ffi.NULL != fmt

    def test_find_source_format_inexistent(self):
        ffh = pyrana.ff.get_handle()
        with self.assertRaises(pyrana.errors.UnsupportedError):
            fmt = pyrana.common.find_source_format("Azathoth")

    def test_find_source_format_none(self):
        ffh = pyrana.ff.get_handle()
        fmt = pyrana.common.find_source_format(None)
        assert ffh.ffi.NULL == fmt


if __name__ == "__main__":
    unittest.main()
