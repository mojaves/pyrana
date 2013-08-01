#!/usr/bin/python

import pyrana
import unittest

class TestPacket(unittest.TestCase):
    def test_NewFromString(self):
        try:
            f = pyrana.format.Packet(0, "a")
        except pyrana.PyranaError as x:
            self.fail("failed creation from simple string: %s" %str(x))
    def test_NewFromStringHuge(self):
        try:
            f = pyrana.format.Packet(0, "a" * 1024 * 1024 * 32)
        except:
            self.fail("failed creation from huge string")
    def test_NewFromPacket(self):
        try:
            f = pyrana.format.Packet(0, "a")
            g = pyrana.format.Packet(1, f)
        except pyrana.PyranaError as x:
            self.fail("failed creation from another packet")
    def test_DataValuesMatches(self):
        f = pyrana.format.Packet(0, "a")
        self.assertTrue(f.data == b"a")
        self.assertTrue(f.size == 1)
    def test_DefaultValues(self):
        f = pyrana.format.Packet(0, "a")
        self.assertFalse(f.is_key)
        self.assertTrue(f.pts == pyrana.TS_NULL)
        self.assertTrue(f.dts == pyrana.TS_NULL)
        self.assertTrue(f.stream_id  == 0)
    def test_InitValues(self):
        f = pyrana.format.Packet(3, "abracadabra", 200, 300, True)
        self.assertTrue(f.stream_id == 3)
        self.assertTrue(f.is_key)
        self.assertTrue(f.pts == 200)
        self.assertTrue(f.dts == 300)
    def test_CannotResetStreamIndex(self):
        f = pyrana.format.Packet(0, "gammaray")
        self.assertTrue(f.stream_id == 0)
        self.assertRaises(AttributeError, setattr, f, "stream_id", 23)
        self.assertTrue(f.stream_id == 0)
    def test_CannotResetIsKey(self):
        f = pyrana.format.Packet(0, "gammaray")
        self.assertFalse(f.is_key)
        self.assertRaises(AttributeError, setattr, f, "is_key", 1)
        self.assertFalse(f.is_key)
    def test_CannotResetPTS(self):
        f = pyrana.format.Packet(0, "R'Yleh")
        self.assertTrue(f.pts == pyrana.TS_NULL)
        self.assertRaises(AttributeError, setattr, f, "pts", 42)
        self.assertTrue(f.pts == pyrana.TS_NULL)
    def test_CannotResetDTS(self):
        f = pyrana.format.Packet(0, "R'Yleh")
        self.assertTrue(f.dts == pyrana.TS_NULL)
        self.assertRaises(AttributeError, setattr, f, "dts", 42)
        self.assertTrue(f.dts == pyrana.TS_NULL)
    def test_CannotResetData(self):
        d = b"O RLY?!?"
        f = pyrana.format.Packet(0, d)
        self.assertTrue(f.data == d)
        self.assertRaises(AttributeError, setattr, f, "data", b"YA, RLY")
        self.assertTrue(f.data == d)
    def test_CannotResetSize(self):
        d = b"YA, RLY!!!"
        l = len(d)
        f = pyrana.format.Packet(0, d)
        self.assertTrue(f.size == l)
        self.assertRaises(AttributeError, setattr, f, "size", len(b"YA, RLY"))
        self.assertTrue(f.size == l)



if __name__ == "__main__":
    unittest.main()
 
