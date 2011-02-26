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
    def _new_frame(self, i=None):
        if i is None:
            i = self._img
        return pyrana.video.Frame(i, pyrana.TS_NULL, True, False, False)
    def test_NewFromImg(self):
        try:
            self._new_frame()
        except pyrana.PyranaError as x:
            self.fail("failed creation from simple data: %s" %str(x))
    def test_InitValues(self):
        f = self._new_frame()
        # TODO image test
        self.assertTrue(f.pts == pyrana.TS_NULL)
        self.assertTrue(f.is_key == True)
        self.assertTrue(f.top_field_first == False)
        self.assertTrue(f.is_interlaced == False)
        self.assertTrue(f.pic_type == pyrana.video.PICT_NO_TYPE)
        self.assertTrue(f.coded_num == pyrana.FRAMENUM_NULL)
        self.assertTrue(f.display_num == pyrana.FRAMENUM_NULL)
    def test_CannotResetPTS(self):
        self._check_cannotResetField(self._new_frame(),
                                     "pts", pyrana.TS_NULL, 23)
    def test_CannotResetIsKey(self):
        self._check_cannotResetField(self._new_frame(),
                                     "is_key", True, False)
    def test_CannotResetTopFieldFirst(self):
        self._check_cannotResetField(self._new_frame(),
                                     "top_field_first", False, True)
    def test_CannotResetIsInterlaced(self):
        self._check_cannotResetField(self._new_frame(),
                                     "is_interlaced", False, True)
    def test_CannotResetPicType(self):
        self._check_cannotResetField(self._new_frame(),
                                     "pic_type", pyrana.video.PICT_NO_TYPE,
                                                pyrana.video.PICT_I_TYPE)
    def test_CannotResetCoded_num(self):
        self._check_cannotResetField(self._new_frame(), "coded_num",
                                     pyrana.FRAMENUM_NULL, 42)
    def test_CannotResetDisplay_num(self):
        self._check_cannotResetField(self._new_frame(), "display_num",
                                     pyrana.FRAMENUM_NULL, 42)
    def test_GetImage(self):
        i = self._new_img(400, 300)
        f = self._new_frame(i)
        j = f.image
        self.assertTrue(i.width == j.width)
        self.assertTrue(i.height == j.height)
        self.assertTrue(i.pixel_format == j.pixel_format)
    def test_GetImageLifeTime(self):
        i = self._new_img(400, 300)
        f = self._new_frame(i)
        del i
        j = f.image
        self.assertTrue(j.pixel_format == "rgb24")
        del f
        self.assertTrue(j.pixel_format == "rgb24")
        





class VFrameRGB24TestCase(VFrameCommonBaseTestCase, unittest.TestCase):
    def _new_img(self, w, h):
        d = "\0" * 3 * w * h
        return pyrana.video.Image(w, h, "rgb24", d)




if __name__ == "__main__":
    unittest.main()
 
