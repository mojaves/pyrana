#!/usr/bin/python

import pyrana
import unittest

class VFrameCommonBaseTestCase(object):
    def setUp(self):
        self._img = self._new_img(w=320, h=240)
    def _check_cannotResetField(self, f, fieldName, oldValue, newValue):
        self.assertTrue(getattr(f, fieldName) == oldValue)
        self.assertRaises(AttributeError, setattr, f, fieldName, newValue)
        self.assertTrue(getattr(f, fieldName) == oldValue)
    def _new_frame(self):
        return pyrana.video.Frame(self._img, pyrana.TS_NULL,
                                  True, False, False)
    def test_NewFromImg(self):
        try:
            self._new_frame()
        except pyrana.PyranaError, x:
            self.fail("failed creation from simple data: %s" %str(x))
    def test_InitValues(self):
        f = self._new_frame()
        # TODO image test
        self.assertTrue(f.pts == pyrana.TS_NULL)
        self.assertTrue(f.isKey == True)
        self.assertTrue(f.toFieldFirst == False)
        self.assertTrue(f.isInterlaced == False)
        self.assertTrue(f.picType == pyrana.video.PICT_NO_TYPE)
        self.assertTrue(f.codedNum == -1)
        self.assertTrue(f.displayNum == -1)
    def test_CannotResetPTS(self):
        self._check_cannotResetField(self._new_frame(),
                                     "pts", pyrana.TS_NULL, 23)
    def test_CannotResetIsKey(self):
        self._check_cannotResetField(self._new_frame(),
                                     "isKey", True, False)
    def test_CannotResetTopFieldFirst(self):
        self._check_cannotResetField(self._new_frame(),
                                     "topFieldFirst", False, True)
    def test_CannotResetIsInterlaced(self):
        self._check_cannotResetField(self._new_frame(),
                                     "isInterlaced", False, True)
    def test_CannotResetPicType(self):
        self._check_cannotResetField(self._new_frame(),
                                     "picType", pyrana.video.PICT_NO_TYPE,
                                                pyrana.video.PICT_I_TYPE)
    def test_CannotResetCodedNum(self):
        self._check_cannotResetField(self._new_frame(), "codedNum", -1, 42)
    def test_CannotResetDisplayNum(self):
        self._check_cannotResetField(self._new_frame(), "displayNum", -1, 42)




class VFrameRGB24TestCase(VFrameCommonBaseTestCase, unittest.TestCase):
    def _new_img(self, w, h):
        d = "\0" * 3 * w * h
        return pyrana.video.Image(w, h, "rgb24", d)




if __name__ == "__main__":
    unittest.main()
 
