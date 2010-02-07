#!/usr/bin/python

import pyrana
import unittest

class FrameTestCase(unittest.TestCase):
    def test_NewFromString(self):
        try:
            f = pyrana.format.Packet(0, "a")
        except Exception, x:
            self.fail("failed creation from simple string: %s" %str(x))
    def test_NewFromStringHuge(self):
        try:
            f = pyrana.format.Packet(0, "a" * 1024 * 1024 * 32)
        except:
            self.fail("failed creation from huge string")
    def test_NewFromFrame(self):
        try:
            f = pyrana.format.Packet(0, "a")
            g = pyrana.format.Packet(1, f)
        except:
            self.fail("failed creation from another packet")
    def test_DataValuesMatches(self):
        f = pyrana.format.Packet(0, "a")
        assert(f.data == "a")
        assert(f.size == 1)
    def test_DefaultValues(self):
        f = pyrana.format.Packet(0, "a")
        assert(not f.isKey)
        assert(f.pts == pyrana.TS_NULL)
        assert(f.dts == pyrana.TS_NULL)
        assert(f.idx  == 0)
    def test_InitValues(self):
        f = pyrana.format.Packet(3, "abracadabra", 200, 300, True)
        assert(f.idx == 3)
        assert(f.isKey)
        assert(f.pts == 200)
        assert(f.dts == 300)
    def test_CannotResetStreamIndex(self):
        f = pyrana.format.Packet(0, "gammaray")
        assert(f.idx == 0)
        self.assertRaises(AttributeError, setattr, f, "idx", 23)
        assert(f.idx == 0)
    def test_CannotResetIsKey(self):
        f = pyrana.format.Packet(0, "gammaray")
        assert(f.isKey == 0)
        self.assertRaises(AttributeError, setattr, f, "isKey", 1)
        assert(f.isKey == 0)
    def test_CannotResetPTS(self):
        f = pyrana.format.Packet(0, "R'Yleh")
        assert(f.pts == pyrana.TS_NULL)
        self.assertRaises(AttributeError, setattr, f, "pts", 42)
        assert(f.pts == pyrana.TS_NULL)
    def test_CannotResetDTS(self):
        f = pyrana.format.Packet(0, "R'Yleh")
        assert(f.dts == pyrana.TS_NULL)
        self.assertRaises(AttributeError, setattr, f, "dts", 42)
        assert(f.dts == pyrana.TS_NULL)
    def test_CannotResetData(self):
        d = "O RLY?!?"
        f = pyrana.format.Packet(0, d)
        assert(f.data == d)
        self.assertRaises(AttributeError, setattr, f, "data", "YA, RLY")
        assert(f.data == d)
    def test_CannotResetSize(self):
        d = "YA, RLY!!!"
        l = len(d)
        f = pyrana.format.Packet(0, d)
        assert(f.size == l)
        self.assertRaises(AttributeError, setattr, f, "size", len("YA, RLY"))
        assert(f.size == l)



if __name__ == "__main__":
    unittest.main()  
