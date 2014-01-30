#!/usr/bin/python

import sys
import os.path
import unittest
import pytest
import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
import pyrana.video

from tests.mockslib import MockFF, MockFrame, MockLavu, MockSws


class TestEncoderVideo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()


if __name__ == "__main__":
    unittest.main()
