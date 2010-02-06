#!/usr/bin/python

import pymedia
import unittest

class GlobalsTestCase(unittest.TestCase):
    def test00_InputFormats(self):
        assert(len(pymedia.input_formats) > 0)
    def test01_OutputFormats(self):
        assert(len(pymedia.output_formats) > 0)
    def test02_InputCodecs(self):
        assert(len(pymedia.input_codecs) > 0)
    def test03_OutputFormats(self):
        assert(len(pymedia.output_codecs) > 0)
    def test04_ValidInputFormats(self):
        assert(all(len(name) > 0 for name in pymedia.input_formats))
    def test05_ValidInputFormats(self):
        assert(all(len(name) > 0 for name in pymedia.output_formats))
    def test06_ValidInputCodecs(self):
        assert(all(len(name) > 0 for name in pymedia.input_codecs))
    def test07_ValidOutputCodecs(self):
        assert(all(len(name) > 0 for name in pymedia.output_codecs))
    def test08_IsStreaming(self):
        fmts = {}
        assert(all(pymedia.is_streaming(name) == streamed \
                   for name, streamed in fmts.items()))
        self.fail("WRITEME!")


if __name__ == "__main__":
    unittest.main()  
