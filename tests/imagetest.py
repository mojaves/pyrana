#!/usr/bin/python

import pyrana
import unittest

class ImageCommonBaseTestCase(object):
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
    def test_InitValues(self):
        i = self._build_img(self.width, self.height, self.data, self.pixFmt)
        self.assertTrue(i.width == self.width)
        self.assertTrue(i.height == self.height)
        self.assertTrue(i.pixFmt == self.pixFmt)
        # gratuitous
        self.assertTrue(i.pixFmt in pyrana.video.user_pixel_formats)
    def test_CannotResetWidth(self):
        i = self._build_img(self.width, self.height, self.data)
        self.assertTrue(i.width == self.width)
        self.assertRaises(AttributeError, setattr, i, "width", 42)
        self.assertTrue(i.width == self.width)
    def test_CannotResetHeight(self):
        i = self._build_img(self.width, self.height, self.data)
        self.assertTrue(i.width == self.width)
        self.assertRaises(AttributeError, setattr, i, "height", 42)
        self.assertTrue(i.width == self.width)
    def test_CannotResetPixFmt(self):
        i = self._build_img(self.width, self.height, self.data)
        self.assertTrue(i.width == self.width)
        self.assertRaises(AttributeError, setattr, i, "pixFmt", "something")
        self.assertTrue(i.width == self.width)
 

class ImageFromDataTestCase(ImageCommonBaseTestCase, unittest.TestCase):
    def setUp(self):
        self.pixFmt = "rgb24"
        self.width, self.height = 320, 240
        self.data = "\0\0\0" * self.width * self.height
    def _build_img(self, w, h, d, n="rgb24"):
        return pyrana.video.Image(w, h, n, d)

class ImageFromPlanesTestCase(ImageCommonBaseTestCase, unittest.TestCase):
    def setUp(self):
        self.pixFmt = "yuv420p"
        self.width, self.height = 320, 240
        self.data = [ "\0" * self.width * self.height,
                      "\0" * (self.width / 2 * self.height / 2),
                      "\0" * (self.width / 2 * self.height / 2) ]
    def _build_img(self, w, h, d, n="yuv420p"):
        return pyrana.video.Image(w, h, n, d)



if __name__ == "__main__":
    unittest.main()  

