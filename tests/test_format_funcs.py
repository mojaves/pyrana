#!/usr/bin/python

import pyrana.format
from pyrana.common import MediaType
import unittest


class TestFormatFuncs(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    def test_is_streamable_any_input(self):
        self.assertTrue(any(map(pyrana.format.is_streamable,
                                pyrana.format.INPUT_FORMATS)))

    def test_is_streamable_any_output(self):
        self.assertTrue(any(map(pyrana.format.is_streamable,
                                pyrana.format.OUTPUT_FORMATS)))

    def test_find_stream_empty(self):
        pyrana.format.find_stream({}, 0, MediaType.AVMEDIA_TYPE_UNKNOWN)
        assert(True)  # FIXME


if __name__ == "__main__":
    unittest.main()
