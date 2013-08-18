#!/usr/bin/python

import pyrana.format
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
