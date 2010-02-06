#!/usr/bin/python

import pyrana
import unittest

class FrameTestCase(unittest.TestCase):
    def test00_NewFromString(self):
        try:
            f = pyrana.format.Packet(0, "a")
        except Exception, x:
            self.fail("failed creation from simple string: %s" %str(x))
    def test01_NewFromStringHuge(self):
        try:
            f = pyrana.format.Packet(0, "a" * 1024 * 1024 * 32)
        except:
            self.fail("failed creation from huge string")
    def test02_NewFromFrame(self):
        try:
            f = pyrana.format.Packet(0, "a")
            g = pyrana.format.Packet(1, f)
        except:
            self.fail("failed creation from another frame")
    def test03_DataValues(self):
        f = pyrana.format.Packet(0, "a")
        assert(f.data == "a")
        assert(f.size == 1)
    def test04_DefaultValues(self):
        f = pyrana.format.Packet(0, "a")
        assert(not f.isKey)
        assert(f.pts == pyrana.TS_NULL)
        assert(f.dts == pyrana.TS_NULL)
        assert(f.idx  == 0)
    def test05_InitValues(self):
        f = pyrana.format.Packet(3, "abracadabra", 200, 300, True)
        assert(f.idx == 3)
        assert(f.isKey)
        assert(f.pts == 200)
        assert(f.dts == 300)
    def test06_ResetStreamIndex(self):
        f = pyrana.format.Packet(0, "gammaray")
        assert(f.idx == 0)
        try:
            f.idx = 1
        except:
            self.fail("failed to set stream index")
        assert(f.idx == 1)
    def test07_ResetIsKey(self):
        f = pyrana.format.Packet(0, "gammaray")
        assert(not f.isKey)
        try:
            f.isKey = True
        except:
            self.fail("failed to set isKey")
        assert(f.isKey)
    def test08_ResetPTS(self):
        f = pyrana.format.Packet(0, "R'Yleh")
        assert(f.dts == pyrana.TS_NULL)
        assert(f.pts == pyrana.TS_NULL)
        try:
            f.pts = 4242
        except:
            self.fail("failed to set pts")
        assert(f.pts == 4242)
        assert(f.dts == pyrana.TS_NULL)
    def test09_ResetDTS(self):
        f = pyrana.format.Packet(0, "R'Yleh")
        assert(f.pts == pyrana.TS_NULL)
        assert(f.dts == pyrana.TS_NULL)
        try:
            f.dts = 4242
        except:
            self.fail("failed to set dts")
        assert(f.dts == 4242)
        assert(f.pts == pyrana.TS_NULL)
    def test10_CannotResetData(self):
        f = pyrana.format.Packet(0, "O RLY?!?")
        self.assertRaises(AttributeError, setattr, f, "data", "YA, RLY")
    def test11_CannotResetSize(self):
        f = pyrana.format.Packet(0, "YA, RLY!")
        self.assertRaises(AttributeError, setattr, f, "size", len("YA, RLY"))



if __name__ == "__main__":
    unittest.main()  
