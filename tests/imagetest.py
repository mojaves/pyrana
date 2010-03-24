#!/usr/bin/python

import pyrana
import unittest

class ImageFromDataTestCase(unittest.TestCase):
    def setUp(self):
        self.width, self.height = 320, 240
        self.data = "\0\0\0" * self.width * self.height
    def _build_img(self, w, h, d, n="rgb24"):
        return pyrana.video.Image(w, h, n, d)
    def test_NewFromValidString(self):
        try:
            self._build_img(self.width, self.height, self.data)
        except pyrana.PyranaError, x:
            self.fail("failed creation from simple string: %s" %str(x))
    def test_NewFromInvalidPixFmt(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, self.height, self.data, "DUMMY")
    def test_NewFromSenselessWidth(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              -1, self.height, self.data)
    def test_NewFromSenselessHeight(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, -1, self.data)
    def test_NewFromInvalidWidth(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width + 1, self.height, self.data)
    def test_NewFromInvalidHeight(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, self.height + 1, self.data)
    def test_NewFromEmptyData(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, self.height, ())




if __name__ == "__main__":
    unittest.main()  

