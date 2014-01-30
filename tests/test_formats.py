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
        self._assert_valid_collection(pyrana.formats.InputFormat)

    def test_output_formats(self):
        self._assert_valid_collection(pyrana.formats.OutputFormat)

    def test_valid_input_formats(self):
        self.assertTrue(all(len(name.value) > 0
                            for name in pyrana.formats.InputFormat))

    def test_valid_input_formats(self):
        self.assertTrue(all(len(name.value) > 0
                            for name in pyrana.formats.OutputFormat))

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
