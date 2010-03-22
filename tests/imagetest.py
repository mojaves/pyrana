#!/usr/bin/python

import pyrana
import unittest

class ImageTestCase(unittest.TestCase):
    def setUp(self):
        self.width, self.height = 320, 240
        self.plane = "\0\0\0" * self.width * self.height * 3
        self.data = [ self.plane ] 
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
    def test_NewFromInvalidWidth(self):
        self.failUnlessRaises(pyrana.ProcessingError, self._build_img,
                              self.width + 1, self.height, self.data)
    def test_NewFromSenselessHeight(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, -1, self.data)
    def test_NewFromInvalidHeight(self):
        self.failUnlessRaises(pyrana.ProcessingError, self._build_img,
                              self.width, self.height + 1, self.data)
    def test_NewFromEmptyData(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, self.height, ())
    def test_NewFromInvalidData(self):
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, self.height, [[], [], [], []])
    def test_NewFromInconsistentData(self):
        plane = "\0" * self.width * self.height
        data = [ plane, plane, plane , []] 
        self.failUnlessRaises(pyrana.SetupError, self._build_img,
                              self.width, self.height, data)




if __name__ == "__main__":
    unittest.main()  

